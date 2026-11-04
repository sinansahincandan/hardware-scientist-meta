"""Benchmark page: Hardware Scientist vs one Meta prompt, per problem side by side — figures, blind rubric scores
with the judge's reasons, wall time and cost. Two designs per problem (round 1) or three (round 2: the earlier
Hardware Scientist run as well). Images embedded; opens anywhere.

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
WHO = {"baseline": "Single prompt", "hs_prev": "Hardware Scientist, old council", "hs": "Hardware Scientist"}
ORDER = ["baseline", "hs_prev", "hs"]


def _img(path: Path, width: int = 900) -> str:
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, width))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=84)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _cost(who: str, k: dict, base_rec: dict) -> tuple[float, float, Path]:
    """(seconds, dollars, figure) for one design."""
    if who == "baseline":
        return base_rec["wall_seconds"], base_rec["cost_usd"], Path(base_rec["_dir"]) / "figure.png"
    run = ROOT / "runs" / k["hs_run" if who == "hs" else "hs_prev_run"]
    t = json.loads((run / "timing.json").read_text(encoding="utf-8"))
    return t["wall_seconds"], t["cost_usd"], run / "final" / "panel_A.png"


def main() -> int:
    scores = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    key = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out = Path(sys.argv[3])
    e = html.escape
    whos = [w for w in ORDER if any(w in k.values() for k in key.values())]
    tot = {w: {"score": 0, "s": 0.0, "c": 0.0, "best": 0} for w in whos}
    rows, blocks = [], []
    for pid in sorted(scores):
        sc, k = scores[pid], key[pid]
        label = {v: lab for lab, v in k.items() if lab in ("A", "B", "C")}
        prob_file = next((ROOT / "examples" / "bench").glob(f"{pid}_*.json"))
        prob = json.loads(prob_file.read_text(encoding="utf-8"))
        bdir = ROOT / "runs" / "baseline" / prob_file.stem
        base_rec = json.loads((bdir / "record.json").read_text(encoding="utf-8")) | {"_dir": str(bdir)}
        best = {lab: w for w, lab in label.items()}[sc["better"]]
        cells, cols = [], []
        for w in whos:
            s, c, fig = _cost(w, k, base_rec)
            total = sc[label[w]]["total"]
            tot[w]["score"] += total
            tot[w]["s"] += s
            tot[w]["c"] += c
            tot[w]["best"] += best == w
            took = f"{s / 60:.0f} min" if s >= 120 else f"{s:.0f} s"
            cells.append(f"<td class='n'>{'<b>' if best == w else ''}{total}/25{'</b>' if best == w else ''}"
                         f"<br><span class='t'>{took} · ${c:.2f}</span></td>")
            crit = "".join(f"<tr><td>{CRIT[x]}</td><td class='n'>{sc[label[w]][x]['score']}</td>"
                           f"<td>{e(sc[label[w]][x]['why'])}</td></tr>" for x in CRIT)
            cols.append(f"<div class='col{' best' if best == w else ''}'><h3>{WHO[w]} <span class='tot'>{total}/25"
                        f"</span></h3><p class='t'>design {label[w]} for the judge · {took} · ${c:.2f}</p>"
                        f"<img src='{_img(fig)}'><table class='crit'>{crit}</table></div>")
        rows.append(f"<tr><td>{e(prob['title'])}</td>{''.join(cells)}<td><b>{WHO[best]}</b></td></tr>")
        names = ", ".join(f"{lab} = {WHO[w]}" for w, lab in sorted(label.items(), key=lambda x: x[1]))
        blocks.append(
            f"<section><h2>{e(prob['title'])}</h2><p class='prob'>{e(prob['statement'])}</p><ul class='cons'>"
            + "".join(f"<li>{e(c)}</li>" for c in prob["constraints"]) + "</ul>"
            f"<div class='verdict'><b>Judge: {WHO[best]} is best.</b> {e(sc['why'])} <i>(In the judge's words: "
            f"{names}.)</i></div><div class='cols c{len(whos)}'>" + "".join(cols)
            + f"</div><p class='arith'><b>Arithmetic the judge re-derived:</b> {e(sc.get('arithmetic_checked', ''))}</p>"
            "</section>")
    n = len(scores)
    head = "".join(f"<th>{WHO[w]}</th>" for w in whos)
    total_cells = "".join(f"<td class='n'><b>{tot[w]['score']}/{25 * n}</b><br><span class='t'>"
                          f"{tot[w]['s'] / 60:.0f} min · ${tot[w]['c']:.2f}</span></td>" for w in whos)
    best_line = "; ".join(f"{WHO[w]} {tot[w]['best']}" for w in whos)
    prev_note = ("\"Old council\" is the Hardware Scientist run of 2026-11-02 (members wrote the proposal); "
                 "\"Hardware Scientist\" is the run with the advisor council and chief designer (2026-11-03)."
                 if "hs_prev" in whos else
                 "\"Hardware Scientist\" is the run with the advisor council and chief designer (2026-11-03). The judge "
                 "also scored an earlier Hardware Scientist version, left out here; its letter can appear in the "
                 "judge's words.")
    page = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
<title>Hardware Scientist vs a single prompt</title><style>
body{{margin:0;background:#f4f6f9;color:#16202c;font:16px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
.wrap{{max-width:1320px;margin:0 auto;padding:30px 22px 60px}}h1{{font-size:32px;margin:0 0 4px}}
.sub{{color:#5b6878;margin:0 0 20px}}table{{border-collapse:collapse;width:100%;background:#fff}}
td,th{{border-bottom:1px solid #e1e6ec;padding:8px 10px;text-align:left;vertical-align:top}}
.n{{white-space:nowrap}}.t{{color:#5b6878;font-size:13px}}section{{background:#fff;border:1px solid #e1e6ec;
border-radius:12px;padding:20px;margin:26px 0}}.prob{{color:#33404f;margin:4px 0}}
.cons{{color:#5b6878;margin:4px 0 12px;font-size:14px}}
.verdict{{background:#f1f5fb;border-left:5px solid #1f6fd1;padding:10px 14px;border-radius:6px;margin:10px 0 16px}}
.cols{{display:grid;gap:16px}}.cols.c2{{grid-template-columns:1fr 1fr}}.cols.c3{{grid-template-columns:1fr 1fr 1fr}}
@media(max-width:900px){{.cols.c2,.cols.c3{{grid-template-columns:1fr}}}}
.col{{border:1px solid #e1e6ec;border-radius:10px;padding:10px}}.col.best{{border:2px solid #1f6fd1}}
.col img{{width:100%;border-radius:8px;border:1px solid #e1e6ec}}.col h3{{margin:0 0 2px;font-size:17px}}
.tot{{float:right;color:#1f6fd1}}.crit td{{font-size:12.5px}}.arith{{font-size:13px;color:#5b6878}}
.note{{background:#fff8e6;border:1px solid #f0d9a0;border-radius:8px;padding:12px 16px;font-size:14px;margin:16px 0}}
</style></head><body><div class='wrap'><h1>Hardware Scientist vs a single prompt</h1>
<p class='sub'>Same Meta models, same problem text. Single prompt: one Muse Spark call with web search + one Muse Image
call. Hardware Scientist: council, Evaluator, Manager, picture loop. Scored blind by an independent judge (Claude Opus)
on the rubric written before any result (examples/bench/RUBRIC.md), 5 criteria × 1–5; the judge saw the designs as
A/B/C in mixed order.</p>
<table><tr><th>Problem</th>{head}<th>Judge's best</th></tr>{''.join(rows)}
<tr><td><b>Total</b></td>{total_cells}<td>{best_line}</td></tr></table>
<div class='note'><b>Read with care.</b> Three problems, one judge, one run per system and problem: a small sample.
{prev_note} Every HS design document lists each key number with the calculation behind it, as it stands on HS's
whiteboard, so the judge could tell HS from the single prompt by format.</div>
{''.join(blocks)}</div></body></html>"""
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
