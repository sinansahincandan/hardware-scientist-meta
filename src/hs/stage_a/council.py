"""Council members: real Responses tool loop for one turn (spec §4.3).

Fake mode never enters here (Meeting uses FakeClient.scripted_turn); this is
the production path: fresh chain per turn, previous_response_id inside the
turn only, instructions resent, tool caps enforced by code.
"""
from __future__ import annotations

import json
import time
from typing import Any

from hs import config
from hs.client import _output_text, search_sources
from hs.master_prompt import MasterPrompt, member_instructions
from hs.stage_a.tools import TOOL_SCHEMAS, ToolRunner
from hs.stage_a.whiteboard import Whiteboard

COUNTED_TOOLS = {"calc", "simulate", "sketch", "web_search", "new_tool", "vetted_calc", "search_knowledge", "use_skill"}


def _unwrap_args(args: dict[str, Any]) -> dict[str, Any]:
    """Models sometimes pack all fields into the action string as JSON; unwrap."""
    action = args.get("action")
    if isinstance(action, str) and action.strip().startswith("{"):
        try:
            inner = json.loads(action)
            if isinstance(inner, dict):
                merged = dict(inner)
                for k, v in args.items():
                    if k != "action":
                        merged[k] = v
                if "action" not in merged and "type" in merged:
                    merged["action"] = merged.pop("type")
                return merged
        except Exception:
            pass
    return args


SPEAKING_RULE = (
    "Speak in full sentences. Say each point in plain words first, then give only the numbers that decide "
    "it, with units and at most three significant figures. One point per short paragraph, at most three "
    "points. When you rely on a calculation, simulation, sketch or source, name it in words with its id, for "
    "example 'the 760 mm door width (E10)'; an id never stands alone. Cite literature only when it is on the "
    "whiteboard as search evidence and you have read it, by its evidence id and title; never cite from "
    "memory. Before you rely on a key result, check it against everyday scales and known regimes "
    "(accelerations in g, sizes against a person or a door, loads against body weights, energies against "
    "daily household use) and say so when a number falls outside what such things show. End with your "
    "position: ready or not ready, and why. Address the other people in the room only by their names. Define "
    "every abbreviation the first time you use it. Talk only about the device, never about figures, images "
    "or any pipeline. This is concept design: aim for a concept that works and can be built."
)


def _compact_transcript(since: list[dict[str, Any]], budget: int = 24000) -> str:
    """Compaction (v2 E): full text for recent turns; earlier turns are covered by the chief designer's records on
    the board, so they are listed here by first sentence only."""
    lines = [f"{t['member']}: {t['message']}" for t in since]
    text = "\n".join(lines)
    if len(text) <= budget:
        return text
    kept: list[str] = []
    total = 0
    for line in reversed(lines):
        if total + len(line) > budget and kept:
            break
        kept.append(line)
        total += len(line)
    kept.reverse()
    older = lines[: len(lines) - len(kept)]
    summary = "\n".join(f"{l.split(':')[0]}: {l.split(':', 1)[-1].strip().split('.')[0]}."
                        for l in older if ":" in l)
    return (f"EARLIER TURNS (first sentences; the chief designer's records on the board hold the state):\n{summary}"
            f"\n\nRECENT TURNS:\n" + "\n".join(kept))


def run_member_turn(client: Any, master: MasterPrompt, member: str, board: Whiteboard,
                    tools: ToolRunner, transcript: list[dict[str, Any]], cycle: int,
                    history: list[dict[str, Any]] | None = None,
                    instructions_override: str | None = None,
                    extra_instruction: str = "", role: str = "member",
                    allowed_actions: set[str] | None = None,
                    tool_schemas: list[dict[str, Any]] | None = None) -> str:
    """One speaker's turn. `role` is the billing role; `allowed_actions` limits whiteboard
    actions (vote-only round, Manager); `tool_schemas` replaces the default tool list."""
    roster_instructions = instructions_override or member_instructions(master.sections, member)
    since = [t for t in transcript if t["member"] != member]
    own_prev = next((t["message"] for t in reversed(transcript) if t["member"] == member), "")
    from hs.master_prompt import roster_of

    people = ", ".join(roster_of(master.sections) + ["the Manager"])
    user_text = (
        f"PEOPLE IN THIS ROOM (address them only by these names): {people}\n\n"
        f"WHITEBOARD:\n{board.render_markdown()}\n\n"
        f"TRANSCRIPT SINCE YOUR LAST TURN:\n" + _compact_transcript(since[-12:])
        + f"\n\nYOUR PREVIOUS MESSAGE:\n{own_prev}\n\nSpeak now. Write compactly: your point, the numbers that decide it with units, the evidence ids; no padding, no repetition of the board. {SPEAKING_RULE}\n"
        "Use the whiteboard tool to write to the board; use calc/vetted_calc/simulate/sketch/web_search for evidence. "
        "Read the evidence already on the board before computing: reuse an existing evidence item by its id "
        "unless you state in your message why you recompute it. Post a labeled sketch (sketch tool, hand-drawn "
        "xkcd style, with the mechanism, the workpiece or load, and fixed versus moving parts) when you propose "
        "or change a concept whose geometry, mechanism or flow path matters; purely numerical turns need no sketch. "
        "Search the literature the way your persona implies (web_search): your own domain's directly relevant "
        "papers, standards and datasheets first, and neighbouring or distant fields where a transferable principle "
        "may exist. Open and read the pages that matter (the search tool can open a page and find text in it) "
        "instead of relying on titles. In your message, state in your own sentence the value, rule or finding you "
        "take from each source, with its citation: that sentence is posted on the whiteboard with the source, so "
        "the others and the Evaluator can check it. Then say what it means from your discipline's point of view "
        "for this design, and answer what other members took from their sources when it bears on yours. When you "
        "borrow a principle from another field, say why it should transfer. Open the page behind any number you "
        "rely on rather than trusting a title. If the proposal on the board still states a value or claim the board "
        "has since corrected, say so in your opinion with the corrected value and its evidence id; the Manager "
        "(chief designer) updates the proposal. "
        + (("From this round on, take up at least one source another member put on the board that bears on your "
            "area, name it by its id, and say what it means from your discipline: confirm it, qualify it, or "
            "contradict it with a source of your own. "
            + _others_sources(tools, member)) if cycle >= 2 else "")
        + extra_instruction
        + "\n" + _skill_index()
    )
    prev_id: str | None = None
    new_search_ids: list[str] = []
    counted = 0
    wb_calls = 0
    chain_restarts = 0
    same_chain_retries = 0
    last_text = ""
    input_items: list[dict[str, Any]] = [{"type": "message", "role": "user",
                                          "content": [{"type": "input_text", "text": user_text}]}]
    for _ in range(16):
        parallel = False if counted >= 4 else None  # from 5th counted call: one at a time
        try:
            offered = tool_schemas or tools.schemas()
            resp = client.responses(role=role, instructions=roster_instructions,
                                    input_items=input_items, tools=offered,
                                    previous_response_id=prev_id, parallel_tool_calls=parallel,
                                    include=(["web_search_call.results"]
                                             if any(t.get("type") == "web_search" for t in offered) else None))
        except Exception as exc:
            # Provider-side chain state can expire while tools run (400
            # "referenced response not found or expired", observed on real
            # runs, sometimes repeatedly in one long turn). First retry the
            # same chained request (transient node-local miss), then restart
            # this turn as a fresh chain from the current board (board and
            # evidence state is code-side and persists).
            if prev_id is None or "not found or expired" not in str(exc):
                raise
            if same_chain_retries < 2:
                same_chain_retries += 1
                time.sleep(3)
                continue
            if chain_restarts >= 4:
                raise
            same_chain_retries = 0
            chain_restarts += 1
            prev_id = None
            input_items = [{"type": "message", "role": "user", "content": [{"type": "input_text",
                            "text": (f"WHITEBOARD (your previous chain in this turn expired; "
                                     f"board state below already includes your earlier actions):\n"
                                     f"{board.render_markdown()}\n\nContinue your turn from this "
                                     f"board state and finish with your spoken message, written compactly.")}]}]
            continue
        prev_id = getattr(resp, "id", prev_id)
        input_items = []
        # B8: every source a search returned becomes evidence at once — also from the final response.
        sources = search_sources(resp)
        if sources:
            for eid in tools.web_search_evidence(member, sources, cycle=cycle):
                new_search_ids.append(eid)
                if history is not None:
                    history.append({"cycle": cycle, "member": member, "kind": "evidence",
                                    "evidence_id": eid, "tool": "web_search"})
        calls = [i for i in (getattr(resp, "output", []) or []) if getattr(i, "type", None) == "function_call"]
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", None) == "message":
                for block in getattr(item, "content", []) or []:
                    if getattr(block, "type", None) == "output_text":
                        last_text = getattr(block, "text", "") or last_text
        if not calls:
            break
        for call in calls:
            name = getattr(call, "name", "")
            try:
                args = json.loads(getattr(call, "arguments", "{}") or "{}")
            except Exception:
                args = {}
            if name == "whiteboard":
                wb_calls += 1
                op_action = str(_unwrap_args(args).get("action", ""))
                if wb_calls > (config.MAX_CHIEF_WHITEBOARD_CALLS_PER_TURN if member == "Manager"
                               else config.MAX_WHITEBOARD_CALLS_PER_TURN):
                    output = "whiteboard budget exhausted — write your message now"
                elif allowed_actions is not None and op_action not in allowed_actions:
                    output = (f"error: action {op_action} is not available in this turn; "
                              f"available: {', '.join(sorted(allowed_actions))}")
                else:
                    op_args = _unwrap_args(args)
                    ok, msg = board.apply_op(member, op_args)
                    output = msg if ok else f"error: {msg}"
                    if history is not None:
                        history.append({"cycle": cycle, "member": member, "kind": "op",
                                        "op": op_args, "ok": ok, "msg": msg})
            elif name in COUNTED_TOOLS:
                counted += 1
                if counted > config.MAX_TOOL_CALLS_PER_TURN:
                    output = "tool budget exhausted — write your message now"
                elif name == "calc":
                    eid, output = tools.calc(member, str(args.get("expression", "")), str(args.get("purpose", "")), cycle=cycle)
                    if history is not None:
                        history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid, "tool": "calc"})
                elif name == "simulate":
                    eid, output = tools.simulate(member, str(args.get("script", "")), str(args.get("purpose", "")), cycle=cycle)
                    if history is not None:
                        history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid, "tool": "simulate"})
                elif name == "sketch":
                    eid, output = tools.sketch(member, str(args.get("script", "")), str(args.get("caption", "")), cycle=cycle)
                    if history is not None:
                        history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid, "tool": "sketch"})
                elif name == "vetted_calc":
                    eid, output = tools.vetted_calc(member, str(args.get("name", "")),
                                                  dict(args.get("args", {}) or {}),
                                                  dict(args.get("input_sources", {}) or {}),
                                                  str(args.get("purpose", "")), cycle=cycle)
                    if history is not None:
                        history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid, "tool": "vetted_calc"})
                elif name == "new_tool":
                    ok, output = tools.new_tool(member, str(args.get("name", "")), str(args.get("description", "")),
                                                dict(args.get("parameters", {}) or {}),
                                                str(args.get("python_source", "")),
                                                dict(args.get("smoke_test_input", {}) or {}))
                    output = output if ok else f"error: {output}"
                elif name == "use_skill":
                    eid, output = tools.use_skill(member, str(args.get("name", "")), cycle=cycle)
                    if history is not None and eid:
                        history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid,
                                        "tool": "use_skill"})
                elif name == "search_knowledge":
                    eid, output = tools.search_knowledge(member, str(args.get("query", "")), cycle=cycle)
                    if history is not None:
                        history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid,
                                        "tool": "search_knowledge"})
                else:  # web_search is built-in; evidence posted by caller from citations
                    output = "web_search handled by the built-in tool"
            elif name in tools.new_tools:
                counted += 1
                eid, output = tools.run_new_tool(member, name, args, cycle=cycle)
                if history is not None:
                    history.append({"cycle": cycle, "member": member, "kind": "evidence", "evidence_id": eid, "tool": name})
            else:
                output = f"error: unknown tool {name}"
            input_items.append({"type": "function_call_output",
                                "call_id": getattr(call, "call_id", ""), "output": str(output)[:2000]})
    if new_search_ids and prev_id is not None:
        # Spec §4.4 / B8: one extra chained request so the member can cite the new search evidence by id.
        listing = "\n".join(f"- {e.id}: {e.output_summary}" for e in board.evidence if e.id in new_search_ids)
        try:
            resp = client.responses(
                role=role, instructions=roster_instructions, previous_response_id=prev_id,
                tools=[t for t in TOOL_SCHEMAS if t.get("name") == "whiteboard"],
                input_items=[{"type": "message", "role": "user", "content": [{"type": "input_text", "text": (
                    "Your searches are now on the whiteboard as evidence:\n" + listing + "\n\nRewrite your spoken "
                    "message so that every source you rely on is cited by its evidence id and title, and cite "
                    "nothing that is not on the board. Reply with the message only.")}]}])
            text = _output_text(resp)
            last_text = text or last_text
        except Exception as exc:
            if "not found or expired" not in str(exc):
                raise
    # Raw search tokens never appear in speech (v2 D): strip token spans.
    import re as _re

    cleaned = _re.sub(r"\[\d+†[^\]]*\]", "", last_text or "")
    tools.note_citations(member, cleaned)  # what the speaker took from each search source they named
    return cleaned.strip() or "(no message)"


def _others_sources(tools: ToolRunner, member: str, limit: int = 8) -> str:
    """A short list of the search sources other members cited (id, who, what they took from it)."""
    rows = []
    for ev in tools.board.evidence:
        ref = ev.references[0] if ev.references else {}
        if ev.tool == "web_search" and ev.author != member and ref.get("passage"):
            rows.append(f"{ev.id} ({ev.author.split()[0]}): {ref.get('title', '')[:70]} — {ref['passage'][:160]}")
    return ("Sources other members took something from:\n" + "\n".join(rows[-limit:]) + "\n") if rows else ""


def _skill_index() -> str:
    from hs.skills import index_text

    return index_text()
