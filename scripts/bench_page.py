"""Benchmark page: Hardware Scientist vs one Meta prompt, per problem side by side — figures, blind rubric scores
with the judge's reasons, wall time and cost. Images embedded; opens anywhere.

Usage: .venv/bin/python scripts/bench_page.py <scores.json> <key.json> <out.html>
"""
from __future__ import annotations

import base64
import html
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CRIT = {"C1": "Meets the constraints", "C2": "Physically works", "C3": "Numbers right and supported",
        "C4": "Picture shows the design", "C5": "Buildable and honest"}


def _img(path: Path, width: int = 900) -> str:
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, width))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=84)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> int:
    scores = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    key = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out = Path(sys.argv[3])
    e = html.escape
    rows, blocks = [], []
    tot = {"hs": 0, "baseline": 0, "hs_wins": 0, "hs_s": 0.0, "b_s": 0.0, "hs_c": 0.0, "b_c": 0.0}
    for pid in sorted(scores):
        sc, k = scores[pid], key[pid]
        label = {v: lab for lab, v in k.items() if lab in ("A", "B")}
        hs_run = ROOT / "runs" / k["hs_run"]
        prob_file = next((ROOT / "examples" / "bench").glob(f"{pid}_*.json"))
        prob = json.loads(prob_file.read_text(encoding="utf-8"))
        base_rec = json.loads((ROOT / "runs" / "baseline" / prob_file.stem / "record.json").read_text(encoding="utf-8"))
        timing = json.loads((hs_run / "timing.json").read_text(encoding="utf-8"))
        hs_tot, b_tot = sc[label["hs"]]["total"], sc[label["baseline"]]["total"]
        winner = "Hardware Scientist" if sc["better"] == label["hs"] else "Single prompt"
        tot["hs"] += hs_tot
        tot["baseline"] += b_tot
        tot["hs_wins"] += winner == "Hardware Scientist"
        tot["hs_s"] += timing["wall_seconds"]
        tot["b_s"] += base_rec["wall_seconds"]
        tot["hs_c"] += timing["cost_usd"]
        tot["b_c"] += base_rec["cost_usd"]
        rows.append(f"<tr><td>{e(prob['title'])}</td><td class='n'>{hs_tot}/25</td><td class='n'>{b_tot}/25</td>"
                    f"<td><b>{winner}</b></td><td class='n'>{timing['wall_seconds'] / 60:.0f} min · ${timing['cost_usd']:.2f}"
                    f"</td><td class='n'>{base_rec['wall_seconds']:.0f} s · ${base_rec['cost_usd']:.2f}</td></tr>")

        def col(who: str, title: str, fig: Path, sc: dict = sc, label: dict = label) -> str:
            s = sc[label[who]]
            crit = "".join(f"<tr><td>{CRIT[c]}</td><td class='n'>{s[c]['score']}</td><td>{e(s[c]['why'])}</td></tr>"
                           for c in CRIT)
            return (f"<div class='col'><h3>{title} <span class='tot'>{s['total']}/25</span></h3>"
                    f"<img src='{_img(fig)}'><table class='crit'>{crit}</table></div>")
        blocks.append(
            f"<section><h2>{e(prob['title'])}</h2><p class='prob'>{e(prob['statement'])}</p><ul class='cons'>"
            + "".join(f"<li>{e(c)}</li>" for c in prob["constraints"]) + "</ul>"
            f"<div class='verdict'><b>Judge: {winner} is better.</b> {e(sc['why'])} <i>(In the judge's words, "
            f"{label['hs']} = Hardware Scientist, {label['baseline']} = single prompt.)</i></div><div class='cols'>"
            + col("hs", "Hardware Scientist", hs_run / "final" / "panel_A.png")
            + col("baseline", "Single prompt", ROOT / "runs" / "baseline" / prob_file.stem / "figure.png")
            + f"</div><p class='arith'><b>Arithmetic the judge re-derived:</b> {e(sc.get('arithmetic_checked', ''))}</p>"
            "</section>")
    n = len(scores)
    page = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
<title>Hardware Scientist vs a single prompt</title><style>
body{{margin:0;background:#f4f6f9;color:#16202c;font:16px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
.wrap{{max-width:1240px;margin:0 auto;padding:30px 22px 60px}}h1{{font-size:32px;margin:0 0 4px}}
.sub{{color:#5b6878;margin:0 0 20px}}table{{border-collapse:collapse;width:100%;background:#fff}}
td,th{{border-bottom:1px solid #e1e6ec;padding:8px 10px;text-align:left;vertical-align:top}}
.n{{white-space:nowrap}}section{{background:#fff;border:1px solid #e1e6ec;border-radius:12px;padding:20px;margin:26px 0}}
.prob{{color:#33404f;margin:4px 0}}.cons{{color:#5b6878;margin:4px 0 12px;font-size:14px}}
.verdict{{background:#f1f5fb;border-left:5px solid #1f6fd1;padding:10px 14px;border-radius:6px;margin:10px 0 16px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.col img{{width:100%;border-radius:8px;border:1px solid #e1e6ec}}
.col h3{{margin:0 0 8px}}.tot{{float:right;color:#1f6fd1}}.crit td{{font-size:13px}}.arith{{font-size:13px;color:#5b6878}}
.note{{background:#fff8e6;border:1px solid #f0d9a0;border-radius:8px;padding:12px 16px;font-size:14px;margin:16px 0}}
</style></head><body><div class='wrap'><h1>Hardware Scientist vs a single prompt</h1>
<p class='sub'>Same Meta models, same problem text. Single prompt: one Muse Spark call with web search + one Muse Image
call. Hardware Scientist: council, Evaluator, Manager, picture loop. Scored blind by an independent judge (Claude Opus)
on the rubric written before any result (examples/bench/RUBRIC.md), 5 criteria × 1–5.</p>
<table><tr><th>Problem</th><th>HS score</th><th>Single prompt</th><th>Judge prefers</th><th>HS time · cost</th>
<th>Single prompt time · cost</th></tr>{''.join(rows)}
<tr><td><b>Total</b></td><td class='n'><b>{tot['hs']}/{25 * n}</b></td><td class='n'><b>{tot['baseline']}/{25 * n}</b></td>
<td><b>HS {tot['hs_wins']} of {n}</b></td><td class='n'>{tot['hs_s'] / 60:.0f} min · ${tot['hs_c']:.2f}</td>
<td class='n'>{tot['b_s']:.0f} s · ${tot['b_c']:.2f}</td></tr></table>
<div class='note'><b>Read with care.</b> (1) These HS runs used the council <i>before</i> the chief-designer change.
(2) By the fixed labelling, HS was design "B" in all three problems. (3) The packet listed HS's key numbers with
"(calc)" and an evidence id but not the calculation itself, which sits on HS's whiteboard; the judge marked several HS
numbers as uncheckable for that reason. The packet builder now includes each number's calculation for the next runs.
(4) Every one of the six pictures contradicts its own text somewhere (judge).</div>
{''.join(blocks)}</div></body></html>"""
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
