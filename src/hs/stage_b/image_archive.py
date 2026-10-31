"""ImageArchive (spec §5.5)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ImageArchive:
    def __init__(self, run_dir: Path) -> None:
        self.path = run_dir / "image_archive.jsonl"
        run_dir.mkdir(parents=True, exist_ok=True)

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def add(self, *, attempt: int, round_idx: int, vlm_prompt: str, render_path: str,
            annotated_path: str, s1_faithful: bool, s1_differences: str,
            s2_flaw: bool, s2_feedback: str, decision: str) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "attempt": attempt, "round": round_idx, "vlm_prompt": vlm_prompt,
                "render": render_path, "annotated": annotated_path,
                "s1_faithful": s1_faithful, "s1_differences": s1_differences,
                "s2_flaw": s2_flaw, "s2_feedback": s2_feedback, "decision": decision,
            }) + "\n")

    def summary_text(self) -> str:
        entries = self.entries()
        if not entries:
            return "(no previous rounds)"
        return "\n".join(
            f"attempt {e['attempt']} round {e['round']}: S1 faithful={e['s1_faithful']} "
            f"differences={e['s1_differences'][:120]} prompt={e['vlm_prompt'][:120]}"
            for e in entries)
