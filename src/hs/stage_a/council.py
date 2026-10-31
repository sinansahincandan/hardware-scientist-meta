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
from hs.master_prompt import MasterPrompt, member_instructions
from hs.stage_a.tools import TOOL_SCHEMAS, ToolRunner
from hs.stage_a.whiteboard import Whiteboard

COUNTED_TOOLS = {"calc", "simulate", "sketch", "web_search", "new_tool", "vetted_calc"}


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


def run_member_turn(client: Any, master: MasterPrompt, member: str, board: Whiteboard,
                    tools: ToolRunner, transcript: list[dict[str, Any]], cycle: int,
                    history: list[dict[str, Any]] | None = None) -> str:
    roster_instructions = member_instructions(master.sections, member)
    since = [t for t in transcript if t["member"] != member]
    own_prev = next((t["message"] for t in reversed(transcript) if t["member"] == member), "")
    user_text = (
        f"WHITEBOARD:\n{board.render_markdown()}\n\n"
        f"TRANSCRIPT SINCE YOUR LAST TURN:\n" + "\n".join(f"{t['member']}: {t['message']}" for t in since[-8:])
        + f"\n\nYOUR PREVIOUS MESSAGE:\n{own_prev}\n\nSpeak now (<= 250 words). "
        "Use the whiteboard tool to write to the board; use calc/vetted_calc/simulate/sketch/web_search for evidence. "
        "Search the literature the way your persona implies: your own domain's directly relevant papers, standards "
        "and datasheets first, and neighbouring or distant fields where a transferable principle may exist. "
        "When you borrow a principle from another field, state on the whiteboard why it should transfer. "
        "For sketch scripts, draw in a hand-sketched whiteboard style (e.g. matplotlib plt.xkcd()) "
        "showing the actual mechanism, the workpiece/load, and fixed vs moving parts."
    )
    prev_id: str | None = None
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
            resp = client.responses(role="member", instructions=roster_instructions,
                                    input_items=input_items, tools=TOOL_SCHEMAS,
                                    previous_response_id=prev_id, parallel_tool_calls=parallel)
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
                                     f"board state and finish with your spoken message (<= 250 words).")}]}]
            continue
        prev_id = getattr(resp, "id", prev_id)
        input_items = []
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
                if wb_calls > config.MAX_WHITEBOARD_CALLS_PER_TURN:
                    output = "whiteboard budget exhausted — write your message now"
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
        # web_search evidence: post one entry per citation in this response
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", None) == "message":
                for block in getattr(item, "content", []) or []:
                    cites = [{"url": getattr(a, "url", ""), "title": getattr(a, "title", "")}
                             for a in (getattr(block, "annotations", []) or [])
                             if getattr(a, "type", None) == "url_citation"]
                    if cites:
                        for eid in tools.web_search_evidence(member, "member search", cites, cycle=cycle):
                            if history is not None:
                                history.append({"cycle": cycle, "member": member, "kind": "evidence",
                                                "evidence_id": eid, "tool": "web_search"})
    return last_text or "(no message)"
