"""Controller loop (spec §7). Every exit path ends with Report.write."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from hs import config
from hs.client import BudgetExceeded
from hs.lessons import load_lessons, load_light, update_lessons
from hs.master_prompt import MasterPrompt
from hs.schemas import Problem
from hs.stage_a.archive import CouncilArchive
from hs.stage_a.evaluator import Evaluator
from hs.stage_a.manager import Manager
from hs.stage_a.meeting import Meeting, Secretary
from hs.stage_b import figure as figure_mod
from hs.stage_b import schematic as schematic_mod
from hs.stage_b.image_archive import ImageArchive
from hs.stage_b.loop import RoundResult, council_sketches, run_stage_b


@dataclass
class RunResult:
    run_dir: Path
    figure_path: Path | None
    warnings: list[str] = field(default_factory=list)
    cost_usd: float = 0.0


class Trace:
    def __init__(self, run_dir: Path) -> None:
        self.path = run_dir / "trace.md"
        if not self.path.exists():
            self.path.write_text("# Trace\n", encoding="utf-8")

    def log(self, msg: str) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(f"- {msg}\n")

    def text(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""


def make_run_dir(problem: Problem, base: Path = config.PROJECT_ROOT / "runs") -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", problem.title.lower()).strip("-")[:40] or "problem"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = base / f"{stamp}_{slug}"
    n = 2
    while candidate.exists():
        candidate = base / f"{stamp}_{slug}-{n}"
        n += 1
    candidate.mkdir(parents=True)
    return candidate


def build_references(run_dir: Path) -> Path:
    """Numbered reference list for the run (v2 D), from recorded citations."""
    refs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ev_file in sorted((run_dir / "stage_a").glob("iter_*/evidence/*.json")):
        try:
            ev = json.loads(ev_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: S112 — unreadable evidence file contributes no references
            continue
        for ref in ev.get("references", []) or []:
            from hs.stage_a.tools import clean_title

            ref = {**ref, "title": clean_title(str(ref.get("title", "")), str(ref.get("url", ""))),
                   "authors_or_org": str(ref.get("authors_or_org", "")).split(":")[0]}
            key = ref.get("url") or f"{ref.get('title')}|{ref.get('query')}"
            if key in seen:
                continue
            seen.add(key)
            refs.append(ref)
    # Prior-art sources are searched literature too; their URLs are recorded
    # in novelty.md even when no member search produced an evidence item.
    for novelty in sorted(run_dir.glob("stage_a/iter_*/novelty.md")):
        for line in novelty.read_text(encoding="utf-8").splitlines():
            if line.startswith("- http"):
                url, _, title = line[2:].strip().partition(" — ")
                if url not in seen:
                    seen.add(url)
                    from urllib.parse import urlparse

                    refs.append({"authors_or_org": urlparse(url).netloc.replace("www.", ""),
                                 "title": title or url, "year": "", "url": url,
                                 "query": "prior-art check", "unresolved": False})
    lines = ["# References", ""]
    for i, ref in enumerate(refs, 1):
        if ref.get("unresolved"):
            lines.append(f"{i}. unresolved source (search: {ref.get('query', '')})")
        else:
            year = f"({ref['year']}) " if ref.get("year") else ""
            title = ref.get("title", "")
            url = ref.get("url", "")
            lines.append(f"{i}. {ref.get('authors_or_org', '')} — {title} {year}{'' if title == url else url}")
    out = run_dir / "references.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


class Controller:
    def __init__(self, client: Any, *, max_a_iters: int = config.MAX_A_ITERS,
                 max_s1_rounds: int = config.MAX_S1_ROUNDS, max_b_returns: int = config.MAX_B_RETURNS,
                 min_cycles: int = config.MIN_CYCLES, max_cycles: int = config.MAX_CYCLES) -> None:
        self.client = client
        self.max_a_iters = max_a_iters
        self.max_s1_rounds = max_s1_rounds
        self.max_b_returns = max_b_returns
        self.min_cycles = min_cycles
        self.max_cycles = max_cycles

    def run(self, problem: Problem, base: Path = config.PROJECT_ROOT / "runs") -> RunResult:
        run_dir = make_run_dir(problem, base)
        (run_dir / "problem.json").write_text(problem.model_dump_json(indent=2), encoding="utf-8")
        if hasattr(self.client, "cost"):
            self.client.cost.run_dir = run_dir
            self.client.cost.flush()
        trace = Trace(run_dir)
        warnings: list[str] = []
        figure_path: Path | None = None
        try:
            figure_path = self._loop(problem, run_dir, trace, warnings)
        except BudgetExceeded as exc:
            warnings.append(f"best effort: cost cap hit ({exc})")
            trace.log(f"BudgetExceeded: {exc}")
            figure_path = self._best_effort_figure(run_dir, trace)
        finally:
            try:
                from hs.board import write_board
                from hs.report import write_report

                build_references(run_dir)
                write_report(run_dir)
                write_board(run_dir)
            except Exception as exc:  # report must never mask the run result
                trace.log(f"report/board generation failed: {exc}")
        cost = 0.0
        cost_file = run_dir / "cost.json"
        if cost_file.exists():
            cost = float(json.loads(cost_file.read_text(encoding="utf-8")).get("total_usd", 0.0))
        return RunResult(run_dir=run_dir, figure_path=figure_path, warnings=warnings, cost_usd=cost)

    # -- internals ---------------------------------------------------------------
    def _loop(self, problem: Problem, run_dir: Path, trace: Trace, warnings: list[str]) -> Path | None:
        lessons_text = load_light()  # the light copy; the full record stays in knowledge/lessons_full.md
        # Fake runs read the real lessons but write their synthetic lessons into the run folder.
        self._lessons_out: Path | None = None
        if getattr(self.client, "is_fake", False) and not os.environ.get("HS_LESSONS_PATH"):
            self._lessons_out = run_dir / "lessons_full_fake_run.md"
            self._lessons_out.write_text(load_lessons(), encoding="utf-8")
        _record_knowledge_in(run_dir, lessons_text)
        master = MasterPrompt.rev0(self.client, problem, lessons_text, run_dir)
        from hs.master_prompt import roster_of

        trace.log(f"master prompt rev 0 written; roster={', '.join(roster_of(master.sections))}")
        manager = Manager(self.client, master)
        archive = CouncilArchive(run_dir)
        img_archive = ImageArchive(run_dir)
        evaluator = Evaluator(self.client)
        secretary = Secretary(self.client)
        returns_to_a = 0
        room: Any = None
        solution: Any = None
        best_pass: RoundResult | None = None
        last: RoundResult | None = None
        pending_eval_requests: list[str] = []
        pending_eval_feedback = ""
        exit_reason = "iterations exhausted"

        for k in range(self.max_a_iters):
            if hasattr(self.client, "fake_iteration"):
                self.client.fake_iteration = k
            inspirations = manager.inspirations(archive)
            meeting = Meeting(self.client, master, run_dir, k,
                              min_cycles=self.min_cycles, max_cycles=self.max_cycles)
            if k > 0 and meeting.carry_from(run_dir / "stage_a" / f"iter_{k - 1:02d}"):
                trace.log(f"iter {k}: meeting continues on the board of iter {k - 1}")
            meeting.pin_inspirations(inspirations)
            if pending_eval_requests:
                meeting.pin_evaluator_requests(pending_eval_requests, pending_eval_feedback)
            room = meeting.run()
            if room.board.render_warns():
                trace.log(f"iter {k}: whiteboard rendering exceeds ~30k tokens (warning)")
            trace.log(f"iter {k}: meeting closed_by={room.closed_by} cycles={room.cycles_used}")
            iter_dir = run_dir / "stage_a" / f"iter_{k:02d}"
            solution = secretary.synthesize(room, problem, iter_dir)
            verdict = evaluator.judge(master, solution, room.board, room.closed_by, iter_dir,
                                      previous_requests=pending_eval_requests)
            status = "accepted" if verdict.accept else "rejected"
            aid = archive.add(solution, iteration=k, revision=master.rev, status=status,
                              accept=verdict.accept, feedback=verdict.feedback,
                              solution_path=f"stage_a/iter_{k:02d}/solution.json")
            trace.log(f"iter {k}: evaluator accept={verdict.accept} archive={aid}")
            pending_eval_requests = list(verdict.evidence_requests)
            pending_eval_feedback = verdict.feedback
            if not verdict.accept:
                report = manager.edit(room, solution, verdict.feedback, iter_dir, tools=meeting.tools)
                trace.log(f"iter {k}: manager edit changed={report.get('changed')} reverted={report.get('reverted')}")
                if manager.no_progress_streak >= 2:
                    exit_reason = "two consecutive no_progress iterations"
                    break
                continue

            # Stage B
            if hasattr(self.client, "fake_attempt"):
                self.client.fake_attempt = returns_to_a
            spec, errors = schematic_mod.spec_and_check(self.client, solution)
            if errors or spec is None:
                fb = "the concept cannot be drawn consistently: " + "; ".join(errors)
                archive.set_status(aid, "rejected_by_designer", feedback=fb)
                trace.log(f"iter {k}: schematic check failed: {fb}")
                if returns_to_a >= self.max_b_returns:
                    exit_reason = "MAX_B_RETURNS reached (schematic)"
                    break
                returns_to_a += 1
                manager.edit(room, solution, fb, iter_dir, tools=meeting.tools)
                if manager.no_progress_streak >= 2:
                    exit_reason = "two consecutive no_progress iterations"
                    break
                continue

            attempt_dir = run_dir / "stage_b" / f"attempt_{returns_to_a:02d}"
            sb = run_stage_b(self.client, solution, spec, attempt_dir, img_archive,
                             lambda msg, k=k: trace.log(f"iter {k} {msg}"),
                             attempt=returns_to_a, max_rounds=self.max_s1_rounds,
                             sketches=council_sketches(iter_dir))
            last = sb.last
            best_pass = sb.best_pass or best_pass
            if sb.decision == "s1_pass" and sb.last is not None:
                figure_path = self._compose(sb.last, run_dir, master, img_archive)
                self._update_knowledge(run_dir, trace, img_archive, problem, solution, room)
                trace.log("run accepted; final figure composed")
                return figure_path
            if sb.decision == "s1_exhausted":
                # Fig. 1 (owner decision, SPEC-11): reported as such to the Manager, who decides in writing
                # whether the design is under-specified; it is not presented as a design flaw.
                archive.set_status(aid, "could_not_draw", feedback=sb.feedback)
                (attempt_dir / "s1_exhausted.md").write_text(sb.feedback + "\n", encoding="utf-8")
                trace.log(f"iter {k}: accepted design could not be drawn faithfully after {sb.rounds} rounds; "
                          "reported to the Manager as a drawing failure")
                if returns_to_a >= self.max_b_returns:
                    exit_reason = f"accepted design could not be drawn faithfully after {sb.rounds} rounds"
                    break
                returns_to_a += 1
                manager.edit(room, solution, sb.feedback, iter_dir, tools=meeting.tools)
                if manager.no_progress_streak >= 2:
                    exit_reason = "two consecutive no_progress iterations"
                    break
                continue
            archive.set_status(aid, "rejected_by_designer", feedback=sb.feedback)
            trace.log(f"iter {k}: designer saw a design flaw (S2); back to Stage A")
            if returns_to_a >= self.max_b_returns:
                exit_reason = "MAX_B_RETURNS reached (designer)"
                break
            returns_to_a += 1
            manager.edit(room, solution, sb.feedback, iter_dir, tools=meeting.tools)
            if manager.no_progress_streak >= 2:
                exit_reason = "two consecutive no_progress iterations"
                break

        warnings.append(f"best effort: {exit_reason}")
        figure_path = None
        if best_pass is not None:  # only a render the critic found faithful becomes a figure
            figure_path = self._compose(best_pass, run_dir, master, img_archive, best_effort=True)
        elif last is not None:
            trace.log("no faithful render exists; no final figure composed")
        if room is not None and solution is not None:
            self._update_knowledge(run_dir, trace, img_archive, problem, solution, room)
        else:
            update_lessons(self.client, trace.text(), img_archive.summary_text(), run_dir.name, self._lessons_out)
        return figure_path

    def _update_knowledge(self, run_dir: Path, trace: Trace, img_archive: ImageArchive, problem: Problem,
                          solution: Any, room: Any) -> None:
        """End of problem (Fig. 1 dotted arrow): lessons, insights and smoke-tested tools into knowledge/."""
        from hs.knowledge import carry_tools, write_insights

        update_lessons(self.client, trace.text(), img_archive.summary_text(), run_dir.name, self._lessons_out)
        base = run_dir / "knowledge_fake_run" if getattr(self.client, "is_fake", False) else None
        try:
            path = write_insights(self.client, run_dir, problem.title, solution.model_dump_json(indent=2),
                                  room.board.evidence, base)
            if path is not None:
                trace.log(f"knowledge: insights written to {path.relative_to(path.parents[2])}")
        except BudgetExceeded:
            raise
        except Exception as exc:  # knowledge is an add-on; it must not lose the run
            trace.log(f"knowledge: insights not written ({type(exc).__name__}: {exc})")
        try:
            from hs.skills import update_skills

            for line in update_skills(self.client, run_dir.name, problem.title, solution.model_dump_json(indent=2),
                                      room.board.evidence, base):
                trace.log(f"knowledge: {line}")
        except BudgetExceeded:
            raise
        except Exception as exc:  # knowledge is an add-on; it must not lose the run
            trace.log(f"knowledge: skills not updated ({type(exc).__name__}: {exc})")
        carried = carry_tools(run_dir, base)
        if carried:
            trace.log(f"knowledge: tools carried to later problems: {', '.join(carried)}")

    def _compose(self, rnd: RoundResult, run_dir: Path, master: MasterPrompt, img_archive: ImageArchive,
                 best_effort: bool = False) -> Path:
        return figure_mod.compose(
            self.client, rnd.solution, rnd.spec, annotated_path=rnd.annotated, render_path=rnd.render,
            localization=rnd.localization, run_dir=run_dir, master_history=master.history,
            s_history=img_archive.entries(), sources=self._sources(run_dir), best_effort=best_effort)

    def _best_effort_figure(self, run_dir: Path, trace: Trace) -> Path | None:
        # No accepted render exists on an early budget hit; record and return None.
        trace.log("best-effort exit without an accepted render (budget hit before Stage B pass)")
        return None

    @staticmethod
    def _sources(run_dir: Path) -> list[str]:
        sources: list[str] = []
        for novelty in sorted(run_dir.glob("stage_a/iter_*/novelty.md")):
            for line in novelty.read_text(encoding="utf-8").splitlines():
                if line.startswith("- http"):
                    sources.append(line[2:].partition(" — ")[0])
        return sources


def _record_knowledge_in(run_dir: Path, lessons_text: str) -> None:
    """What this problem inherits from earlier ones (Fig. 1 knowledge/), for the pages: lesson ids given to
    rev 0, insight files members can search, smoke-tested tools loaded into the toolbox."""
    from hs.knowledge import carried_tools, knowledge_dir

    insights = sorted(p.stem for p in (knowledge_dir() / "insights").glob("*.md")) \
        if (knowledge_dir() / "insights").exists() else []
    (run_dir / "knowledge_in.json").write_text(json.dumps({
        "lessons": re.findall(r"^- (L\d+):", lessons_text, flags=re.MULTILINE),
        "insight_runs": insights,
        "tools": {name: rec.get("source_run", "") for name, rec in carried_tools().items()},
        "skills": [s.get("name", "") for s in __import__("hs.skills", fromlist=["list_skills"]).list_skills()],
    }, indent=2), encoding="utf-8")
