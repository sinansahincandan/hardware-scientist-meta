"""CouncilArchive (spec §4.1, §10)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.schemas import SolutionPrompt


class CouncilArchive:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.path = run_dir / "archive.jsonl"
        run_dir.mkdir(parents=True, exist_ok=True)

    def entries(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _write_all(self, entries: list[dict[str, Any]]) -> None:
        self.path.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")

    def add(self, solution: SolutionPrompt, *, iteration: int, revision: int,
            status: str, accept: bool, feedback: str, solution_path: str = "") -> str:
        entries = self.entries()
        aid = f"A{len(entries) + 1}"
        entries.append({"id": aid, "iteration": iteration, "revision": revision, "status": status,
                        "solution_path": solution_path, "accept": accept, "feedback": feedback,
                        "title": solution.title})
        self._write_all(entries)
        return aid

    def set_status(self, aid: str, status: str, feedback: str = "") -> None:
        entries = self.entries()
        for entry in entries:
            if entry["id"] == aid:
                entry["status"] = status
                if feedback:
                    entry["feedback"] = feedback
        self._write_all(entries)

    def best(self) -> dict[str, Any] | None:
        entries = self.entries()
        if not entries:
            return None
        accepted = [e for e in entries if e.get("accept")]
        if accepted:
            return accepted[-1]
        not_designer = [e for e in entries if e.get("status") != "rejected_by_designer"]
        if not_designer:
            return not_designer[-1]
        return entries[-1]
