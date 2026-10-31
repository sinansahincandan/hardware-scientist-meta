"""Manager: inspirations, written diagnosis, revert-then-rewrite (spec §4.6, §3.2)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hs.master_prompt import MasterPrompt
from hs.schemas import Gradients, Inspirations, MasterPromptRewrite, SolutionPrompt
from hs.stage_a.archive import CouncilArchive
from hs.stage_a.meeting import MeetingResult


class Manager:
    def __init__(self, client: Any, master: MasterPrompt) -> None:
        self.client = client
        self.master = master
        self.last_gradients: Gradients | None = None

    @property
    def no_progress_streak(self) -> int:
        return self.master.no_progress_streak

    def inspirations(self, archive: CouncilArchive) -> list[dict[str, Any]]:
        entries = archive.entries()
        if not entries:
            return []
        payload = json.dumps({"archive_ids": [e["id"] for e in entries],
                              "statuses": {e["id"]: e["status"] for e in entries}})
        picks = self.client.structured("manager_inspirations", Inspirations,
                                       "Pick 1-3 inspirations; at least one rejected if any exist.",
                                       payload)
        by_id = {e["id"]: e for e in entries}
        chosen = [p for p in picks.picks if p.archive_id in by_id][:3]
        # code enforcement: at least one non-accepted when available
        if chosen and all(by_id[p.archive_id]["status"] == "accepted" for p in chosen):
            rejected = [e for e in entries if e["status"] != "accepted"]
            if rejected:
                from hs.schemas import InspirationPick

                chosen[-1] = InspirationPick(archive_id=rejected[-1]["id"], why_useful="Rejected attempt to learn from.")
        return [{"archive_id": p.archive_id, "status": by_id[p.archive_id]["status"],
                 "feedback_summary": by_id[p.archive_id].get("feedback", "")[:200]} for p in chosen]

    def diagnose(self, room: MeetingResult, solution: SolutionPrompt, feedback_text: str,
                 iter_dir: Path) -> Gradients:
        stats = json.dumps(room.stats)
        prompt = (
            "TRANSCRIPT:\n" + "\n".join(f"{t['member']}: {t['message']}" for t in room.transcript)
            + f"\n\nMEMBER STATS: {stats}\n\nSOLUTION:\n{solution.model_dump_json(indent=2)}"
            f"\n\nFEEDBACK:\n{feedback_text}\n\nCURRENT MASTER PROMPT:\n{self.master.text()}"
            "\n\nDiagnose the process (never propose a design). State whether this is the same problem "
            "as the previous failure and which sections to revert if so."
        )
        gradients = self.client.structured("manager_gradients", Gradients,
                                           "You are the Manager. Diagnose how the team worked.",
                                           prompt)
        self.last_gradients = gradients
        (iter_dir / "diagnosis.json").write_text(gradients.model_dump_json(indent=2), encoding="utf-8")
        return gradients

    def edit(self, room: MeetingResult, solution: SolutionPrompt, feedback_text: str,
             iter_dir: Path) -> dict[str, Any]:
        """Diagnosis -> revert (code) -> optimizer rewrite with guards/shrink. Returns ops report."""
        gradients = self.diagnose(room, solution, feedback_text, iter_dir)
        reverted = self.master.apply_reverts(gradients)
        rewrite = self.client.structured(
            "optimizer", MasterPromptRewrite,
            "Rewrite only the sections that need it, as free Markdown section text.",
            f"MASTER PROMPT:\n{self.master.text()}\n\nMANAGER NOTES:\n{gradients.model_dump_json(indent=2)}")
        report = self.master.apply_rewrite(rewrite)
        if report.get("guard_reasked"):
            rewrite2 = self.client.structured(
                "optimizer", MasterPromptRewrite,
                "Your rewrite violated a guard: " + "; ".join(report["violations"]) + ". Fix it.",
                f"MASTER PROMPT:\n{self.master.text()}\n\nMANAGER NOTES:\n{gradients.model_dump_json(indent=2)}")
            report = self.master.apply_rewrite(rewrite2, _guard_retry=True)
        if report.get("shrink_asked"):
            rewrite3 = self.client.structured(
                "optimizer", MasterPromptRewrite,
                "Sections shrank by >50%: " + ", ".join(report["shrink_asked"]) + ". Confirm intended.",
                f"MASTER PROMPT:\n{self.master.text()}\n\nMANAGER NOTES:\n{gradients.model_dump_json(indent=2)}")
            report = self.master.apply_rewrite(rewrite3, _shrink_retry=True)
        report["reverted"] = reverted
        report["gradients"] = gradients.model_dump()
        return report
