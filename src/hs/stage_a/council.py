"""Council members: real Responses tool loop for one turn (spec §4.3).

Fake mode never enters here (Meeting uses FakeClient.scripted_turn); this is
the production path: fresh chain per turn, previous_response_id inside the
turn only, instructions resent, tool caps enforced by code.
"""
from __future__ import annotations

import json
from typing import Any

from hs import config
from hs.master_prompt import MasterPrompt, member_instructions
from hs.stage_a.tools import TOOL_SCHEMAS, ToolRunner
from hs.stage_a.whiteboard import Whiteboard

COUNTED_TOOLS = {"calc", "simulate", "sketch", "web_search", "new_tool", "vetted_calc"}


def run_member_turn(client: Any, master: MasterPrompt, member: str, board: Whiteboard,
                    tools: ToolRunner, transcript: list[dict[str, Any]], cycle: int) -> str:
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
        "When you borrow a principle from another field, state on the whiteboard why it should transfer."
    )
    prev_id: str | None = None
    counted = 0
    wb_calls = 0
    last_text = ""
    input_items: list[dict[str, Any]] = [{"type": "message", "role": "user",
                                          "content": [{"type": "input_text", "text": user_text}]}]
    for _ in range(12):
        parallel = False if counted >= 4 else None  # from 5th counted call: one at a time
        resp = client.responses(role="member", instructions=roster_instructions,
                                input_items=input_items, tools=TOOL_SCHEMAS,
                                previous_response_id=prev_id, parallel_tool_calls=parallel)
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
                    ok, msg = board.apply_op(member, args)
                    output = msg if ok else f"error: {msg}"
            elif name in COUNTED_TOOLS:
                counted += 1
                if counted > config.MAX_TOOL_CALLS_PER_TURN:
                    output = "tool budget exhausted — write your message now"
                elif name == "calc":
                    _, output = tools.calc(member, str(args.get("expression", "")), str(args.get("purpose", "")), cycle=cycle)
                elif name == "simulate":
                    _, output = tools.simulate(member, str(args.get("script", "")), str(args.get("purpose", "")), cycle=cycle)
                elif name == "sketch":
                    _, output = tools.sketch(member, str(args.get("script", "")), str(args.get("caption", "")), cycle=cycle)
                elif name == "vetted_calc":
                    _, output = tools.vetted_calc(member, str(args.get("name", "")),
                                                  dict(args.get("args", {}) or {}),
                                                  dict(args.get("input_sources", {}) or {}),
                                                  str(args.get("purpose", "")), cycle=cycle)
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
                _, output = tools.run_new_tool(member, name, args, cycle=cycle)
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
                        tools.web_search_evidence(member, "member search", cites, cycle=cycle)
    return last_text or "(no message)"
