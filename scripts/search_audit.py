"""Audit of the council's literature search in one run (dev tool; one Meta call for the relevance judge).

Usage: .venv/bin/python scripts/search_audit.py <run_dir> [--judge]
Per meeting and member: queries, sources cited with the sentence the member took from them, pages opened, results
found but unused, and whether the member's speech engages with sources (their own or others'). With --judge, a
muse-spark judge reads each cited statement and says in words whether it is relevant to the problem and to that
member's discipline; the report lists the ones it doubts. Writes <run_dir>/search_audit.md.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    run = Path(sys.argv[1])
    judge = "--judge" in sys.argv
    problem = json.loads((run / "problem.json").read_text(encoding="utf-8"))
    lines = [f"# Search audit — {problem['title']}", f"Run: {run.name}", ""]
    cited_all: list[dict] = []
    for wbf in sorted(run.glob("stage_a/iter_*/whiteboard.json")):
        board = json.loads(wbf.read_text(encoding="utf-8"))
        turns = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((wbf.parent / "turns").glob("*.json"))]
        ev = [e for e in board["evidence"] if e["tool"] == "web_search"]
        by = collections.defaultdict(list)
        for e in ev:
            by[e["author"]].append(e)
        lines.append(f"## Meeting {int(wbf.parent.name.split('_')[-1]) + 1}: {len(ev)} search evidence items")
        for member, items in by.items():
            refs = [(e, (e.get("references") or [{}])[0]) for e in items]
            cited = [(e, r) for e, r in refs if r.get("cited") and r.get("passage")]
            if not cited:  # runs before note_citations: the speaker's own sentences that name the source
                sents = re.split(r"(?<=[.!?])\s+", " ".join(t.get("message", "") for t in turns if t.get("member") == member))
                cited = [(e, {**r, "passage": next(s for s in sents if re.search(rf"\b{e['id']}\b", s))})
                         for e, r in refs if any(re.search(rf"\b{e['id']}\b", s) for s in sents)]
            read = sum(1 for _, r in refs if r.get("read"))
            queries = sorted({e["code_or_query"] for e in items if e["code_or_query"]})
            speech = " ".join(t.get("message", "") for t in turns if t.get("member") == member)
            own = sum(1 for e, _ in cited if e["id"] in speech)
            others = {i for i in re.findall(r"\bE\d+\b", speech)} & {e["id"] for e in ev if e["author"] != member}
            lines.append(f"- **{member}**: {len(queries)} queries, {len(cited)} sources cited with a statement, "
                         f"{read} pages opened, {len(items) - len(cited)} results not cited; speech names "
                         f"{own} of its own cited sources and {len(others)} sources other members found.")
            for e, r in cited[:6]:
                lines.append(f"  - {e['id']} {r.get('title', '')[:70]} — “{r.get('passage', '')[:160]}”")
                cited_all.append({"id": e["id"], "member": member, "query": e["code_or_query"],
                                  "statement": r.get("passage", ""), "title": r.get("title", "")})
        lines.append("")
    if judge and cited_all:
        from pydantic import BaseModel

        from hs.client import MetaClient

        class Item(BaseModel):
            id: str
            relevant: bool
            why: str

        class Verdicts(BaseModel):
            items: list[Item]

        client = MetaClient(run_dir=run / "search_audit_calls", max_cost=0.3)
        table = "\n".join(f"{c['id']} | {c['member']} | query: {c['query']} | source: {c['title']} | "
                          f"statement: {c['statement']}" for c in cited_all)
        res = client.structured(
            "light_check", Verdicts, "You audit an engineering team's literature use.",
            f"PROBLEM: {problem['statement']}\n\nFor each cited statement, is it relevant to this problem and to the "
            "member's discipline (relevant), and why, in one short sentence.\n\n" + table)
        doubted = [i for i in res.items if not i.relevant]
        lines.append(f"## Relevance judge: {len(res.items) - len(doubted)} of {len(res.items)} cited statements "
                     "judged relevant")
        lines += [f"- doubted {i.id}: {i.why}" for i in doubted]
    (run / "search_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
