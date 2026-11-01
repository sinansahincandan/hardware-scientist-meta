"""Controller loop (spec §7). Every exit path ends with Report.write."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from hs import config
from hs.client import BudgetExceeded
from hs.lessons import load_lessons, update_lessons
from hs.master_prompt import MasterPrompt
from hs.schemas import Problem
from hs.stage_a.archive import CouncilArchive
from hs.stage_a.evaluator import Evaluator
from hs.stage_a.manager import Manager
from hs.stage_a.meeting import Meeting, Secretary
from hs.stage_b import figure as figure_mod
from hs.stage_b import schematic as schematic_mod
from hs.stage_b.annotate import Annotator
from hs.stage_b.designer_eval import DesignerEvalRunner, decide, feedback_text, label_failed
from hs.stage_b.image_archive import ImageArchive
from hs.stage_b.image_model import ImageModel
from hs.stage_b.vlm_prompt import VLMPromptWriter


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


def make_run_dir(problem: Problem, base: Path = Path("runs")) -> Path:
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
            key = ref.get("url") or f"{ref.get('title')}|{ref.get('query')}"
            if key in seen:
                continue
            seen.add(key)
            refs.append(ref)
    lines = ["# References", ""]
    for i, ref in enumerate(refs, 1):
        if ref.get("unresolved"):
            lines.append(f"{i}. unresolved source (search: {ref.get('query', '')})")
        else:
            year = f"({ref['year']}) " if ref.get("year") else ""
            lines.append(f"{i}. {ref.get('authors_or_org', '')} — {ref.get('title', '')} {year}{ref.get('url', '')}")
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

    def run(self, problem: Problem, base: Path = Path("runs")) -> RunResult:
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
        lessons_text = load_lessons()
        master = MasterPrompt.rev0(self.client, problem, lessons_text, run_dir)
        from hs.master_prompt import roster_of

        trace.log(f"master prompt rev 0 written; roster={', '.join(roster_of(master.sections))}")
        manager = Manager(self.client, master)
        archive = CouncilArchive(run_dir)
        img_archive = ImageArchive(run_dir)
        evaluator = Evaluator(self.client)
        secretary = Secretary(self.client)
        returns_to_a = 0
        label_failures_total = 0  # persists across Stage B attempts (AUTOPILOT §7.1 fallback)
        best_pass: tuple[Any, ...] | None = None
        last: tuple[Any, ...] | None = None
        pending_eval_requests: list[str] = []
        pending_eval_feedback = ""
        exit_reason = "iterations exhausted"

        for k in range(self.max_a_iters):
            if hasattr(self.client, "fake_iteration"):
                self.client.fake_iteration = k
            inspirations = manager.inspirations(archive)
            meeting = Meeting(self.client, master, run_dir, k,
                              min_cycles=self.min_cycles, max_cycles=self.max_cycles)
            meeting.pin_inspirations(inspirations)
            if pending_eval_requests:
                meeting.pin_evaluator_requests(pending_eval_requests, pending_eval_feedback)
            room = meeting.run()
            if room.board.render_warns():
                trace.log(f"iter {k}: whiteboard rendering exceeds ~30k tokens (warning)")
            trace.log(f"iter {k}: meeting closed_by={room.closed_by} cycles={room.cycles_used}")
            iter_dir = run_dir / "stage_a" / f"iter_{k:02d}"
            solution = secretary.synthesize(room, problem, iter_dir)
            verdict = evaluator.judge(master, solution, room.board, room.closed_by, iter_dir)
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

            decision = "s2_return"
            ev = None
            s1_diffs = ""
            label_failures = label_failures_total
            attempt_dir = run_dir / "stage_b" / f"attempt_{returns_to_a:02d}"
            carry_render: Path | None = None
            carry_vlm = None
            for r in range(self.max_s1_rounds):
                round_dir = attempt_dir / f"round_{r:02d}"
                round_dir.mkdir(parents=True, exist_ok=True)
                geometry = schematic_mod.render_schematic(spec, round_dir)
                writer = VLMPromptWriter(self.client)
                if carry_render is not None and carry_vlm is not None:
                    vlm = carry_vlm
                    render_path = round_dir / "render.png"
                    render_path.write_bytes(carry_render.read_bytes())
                    carry_render = None
                else:
                    vlm = writer.write(solution, spec, round_dir / "schematic.png",
                                       round_dir / "schematic_labeled.png", img_archive,
                                       s1_differences=s1_diffs, corrections=s1_diffs,
                                       force_code_labels=label_failures >= 2)
                    render_bytes = ImageModel(self.client).edit(vlm, round_dir / "schematic.png")
                    render_path = round_dir / "render.png"
                    render_path.write_bytes(render_bytes)
                (round_dir / "vlm_prompt.json").write_text(vlm.model_dump_json(indent=2), encoding="utf-8")
                annotated_path, loc, missing = Annotator(self.client).run(
                    render_path, spec, geometry, round_dir / "annotated.png",
                    code_labels=(vlm.label_mode == "code"))
                ev = DesignerEvalRunner(self.client).run(
                    annotated_path, round_dir / "schematic_labeled.png", solution, missing)
                decision = decide(ev, r, self.max_s1_rounds)
                (round_dir / "eval.json").write_text(ev.model_dump_json(indent=2), encoding="utf-8")
                (round_dir / "decision.txt").write_text(decision + "\n", encoding="utf-8")
                img_archive.add(attempt=returns_to_a, round_idx=r, vlm_prompt=vlm.prompt,
                                render_path=str(render_path), annotated_path=str(annotated_path),
                                s1_faithful=ev.s1_faithful, s1_differences=ev.s1_differences,
                                s2_flaw=ev.s2_flaw, s2_feedback=ev.s2_feedback, decision=decision)
                last = (solution, spec, annotated_path, loc, render_path)
                if ev.s1_faithful:
                    best_pass = last
                trace.log(f"iter {k} round {r}: S1={ev.s1_faithful} S2={ev.s2_flaw} decision={decision}")
                if label_failed(ev):
                    label_failures += 1
                    label_failures_total = label_failures
                    trace.log(f"iter {k} round {r}: label failure {label_failures}/2 before code-label fallback")
                # Targeted corrections from actual-image review, appended verbatim next round (§7.2).
                s1_diffs = "\n".join(x for x in (ev.s1_differences, ev.label_findings,
                                                 ev.pixel_description) if x)
                if decision == "s1_retry":
                    # Two-step chain for S1 (spec §5.5b): regions are the output
                    # gradient; the VLM prompt gradient diagnoses each region.
                    from hs.stage_b.prompt_gradient import VLMPromptGradientRunner, composite_region

                    grad_runner = VLMPromptGradientRunner(self.client)
                    try:
                        grad = grad_runner.run(render_path, round_dir / "schematic_labeled.png", vlm, ev)
                        (round_dir / "vlm_gradient.json").write_text(grad.model_dump_json(indent=2), encoding="utf-8")
                        render_regions = [x for x in ev.regions if x.source == "render" and len(x.box) == 4]
                        if grad.fix_mode == "local" and render_regions:
                            current = render_path
                            kept_any = False
                            for region in render_regions:
                                fix = next((g.prompt_fix for g in grad.per_region
                                            if g.part_id == region.part_id), region.expected)
                                edited_bytes = self.client.image_edit(
                                    f"Change only this: {fix}. Keep everything else in the image identical.",
                                    current)
                                edited_path = round_dir / f"edited_{region.part_id}.png"
                                edited_path.write_bytes(edited_bytes)
                                comp_path = round_dir / f"local_{region.part_id}.png"
                                assert_info = composite_region(current, edited_path, region.box, comp_path)
                                (round_dir / f"composite_{region.part_id}.json").write_text(
                                    json.dumps(assert_info), encoding="utf-8")
                                if not assert_info["outside_unchanged"]:
                                    trace.log(f"iter {k} round {r}: local edit {region.part_id} reverted (outside-box pixels changed)")
                                    continue
                                ann_local, _loc2, _miss2 = Annotator(self.client).run(
                                    comp_path, spec, geometry, round_dir / f"annotated_local_{region.part_id}.png",
                                    code_labels=(vlm.label_mode == "code"))
                                check = grad_runner.progress_check(ann_local, ev, fix)
                                (round_dir / f"progress_{region.part_id}.json").write_text(
                                    check.model_dump_json(indent=2), encoding="utf-8")
                                if check.fixed_region_pass and check.previous_pass and not check.seam_visible:
                                    current = comp_path
                                    kept_any = True
                                    trace.log(f"iter {k} round {r}: local edit {region.part_id} kept")
                                else:
                                    trace.log(f"iter {k} round {r}: local edit {region.part_id} reverted by progress check")
                            if kept_any:
                                carry_render = current
                                carry_vlm = vlm
                        else:
                            s1_diffs = (grad.summary + "\n" + "\n".join(
                                f"{g.part_id}: {g.diagnosis} -> {g.prompt_fix}" for g in grad.per_region)
                                + "\n" + s1_diffs)
                    except Exception as exc:  # gradient path must never kill the run (budget guards still apply first)
                        if "budget cap" in str(exc) or "hs run cost" in str(exc):
                            raise
                        trace.log(f"iter {k} round {r}: VLM prompt gradient skipped: {exc}")
                if decision != "s1_retry":
                    break
            if decision == "s1_retry":
                decision = "s2_return"
            if decision == "s1_pass" and last is not None:
                sol, sp, annot, loc, _render = last
                figure_path = figure_mod.compose(
                    self.client, sol, sp, annotated_path=annot, localization=loc, run_dir=run_dir,
                    master_history=master.history, s_history=img_archive.entries(),
                    sources=self._sources(run_dir))
                update_lessons(self.client, trace.text(), img_archive.summary_text(), run_dir.name)
                trace.log("run accepted; final figure composed")
                return figure_path
            assert ev is not None
            fb = feedback_text(ev, self.max_s1_rounds - 1, self.max_s1_rounds)
            archive.set_status(aid, "rejected_by_designer", feedback=fb)
            trace.log(f"iter {k}: designer returned to Stage A: {fb[:160]}")
            if returns_to_a >= self.max_b_returns:
                exit_reason = "MAX_B_RETURNS reached (designer)"
                break
            returns_to_a += 1
            manager.edit(room, solution, fb, iter_dir, tools=meeting.tools)
            if manager.no_progress_streak >= 2:
                exit_reason = "two consecutive no_progress iterations"
                break

        warnings.append(f"best effort: {exit_reason}")
        src = best_pass or last
        figure_path = None
        if src is not None:
            sol, sp, annot, loc, _render = src
            figure_path = figure_mod.compose(
                self.client, sol, sp, annotated_path=annot, localization=loc, run_dir=run_dir,
                master_history=master.history, s_history=img_archive.entries(),
                sources=self._sources(run_dir), best_effort=True)
        update_lessons(self.client, trace.text(), img_archive.summary_text(), run_dir.name)
        return figure_path

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
                    sources.append(line[2:])
        return sources
