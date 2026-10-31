"""Whiteboard state, op validation, rendering, history (spec §4.2, §12.15-12.16)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class WBFunction(BaseModel):
    id: str
    text: str
    author: str


class WBConcept(BaseModel):
    id: str
    function_id: str
    text: str
    author: str
    status: str = "open"  # open | favored | dropped


class WBEvidence(BaseModel):
    id: str
    author: str
    tool: str
    purpose: str
    code_or_query: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    output_summary: str
    output_full: str = ""
    sketch_path: str | None = None
    status: str = "ok"  # ok | error
    cycle: int = 0


class WBObjection(BaseModel):
    id: str
    author: str
    target_id: str
    text: str
    blocking: bool = False
    status: str = "open"  # open | resolved
    resolution: str = ""
    evidence_ids: list[str] = Field(default_factory=list)


class WBClaim(BaseModel):
    claim: str
    evidence_ids: list[str] = Field(default_factory=list)


class WBProposal(BaseModel):
    version: int
    author: str
    text: str
    concept_ids: list[str] = Field(default_factory=list)
    key_claims: list[WBClaim] = Field(default_factory=list)


class WBVote(BaseModel):
    version: int
    ready: bool
    reason: str = ""


class WBClosure(BaseModel):
    closed_by: str = "cap"  # consensus | cap
    cycles_used: int = 0
    open_blocking: list[str] = Field(default_factory=list)


class Whiteboard(BaseModel):
    inspirations: list[dict[str, Any]] = Field(default_factory=list)
    functions: list[WBFunction] = Field(default_factory=list)
    concepts: list[WBConcept] = Field(default_factory=list)
    evidence: list[WBEvidence] = Field(default_factory=list)
    objections: list[WBObjection] = Field(default_factory=list)
    proposal: WBProposal | None = None
    votes: dict[str, WBVote] = Field(default_factory=dict)
    closure: WBClosure = Field(default_factory=WBClosure)

    # -- evidence is written by CODE only -------------------------------------
    def add_evidence(self, author: str, tool: str, purpose: str, code_or_query: str,
                     output_summary: str, output_full: str = "", inputs: dict[str, Any] | None = None,
                     sketch_path: str | None = None, status: str = "ok", cycle: int = 0) -> WBEvidence:
        ev = WBEvidence(id=f"E{len(self.evidence) + 1}", author=author, tool=tool, purpose=purpose,
                        code_or_query=code_or_query, inputs=inputs or {}, output_summary=output_summary,
                        output_full=output_full, sketch_path=sketch_path, status=status, cycle=cycle)
        self.evidence.append(ev)
        return ev

    def pin_evaluator_requests(self, requests: list[str], feedback: str) -> None:
        for req in requests:
            self.objections.append(WBObjection(
                id=f"O{len(self.objections) + 1}", author="Evaluator",
                target_id=self.proposal.concept_ids[0] if self.proposal and self.proposal.concept_ids else "proposal",
                text=req, blocking=True, status="open"))

    # -- member ops (only write path) -------------------------------------------
    def apply_op(self, author: str, op: dict[str, Any]) -> tuple[bool, str]:
        action = op.get("action", "")
        try:
            if action == "add_function":
                if not op.get("text"):
                    return False, "add_function needs text"
                fn = WBFunction(id=f"F{len(self.functions) + 1}", text=str(op["text"]), author=author)
                self.functions.append(fn)
                return True, fn.id
            if action == "add_concept":
                fid = str(op.get("function_id", ""))
                if fid not in {f.id for f in self.functions}:
                    return False, f"unknown function_id {fid}"
                if not op.get("text"):
                    return False, "add_concept needs text"
                c = WBConcept(id=f"C{len(self.concepts) + 1}", function_id=fid,
                              text=str(op["text"]), author=author)
                self.concepts.append(c)
                return True, c.id
            if action == "set_concept_status":
                cid, status = str(op.get("id", "")), str(op.get("status", ""))
                if status not in ("open", "favored", "dropped"):
                    return False, f"bad concept status {status}"
                for c in self.concepts:
                    if c.id == cid:
                        c.status = status
                        return True, cid
                return False, f"unknown concept {cid}"
            if action == "raise_objection":
                target = str(op.get("target_id", ""))
                known = {f.id for f in self.functions} | {c.id for c in self.concepts} | {"proposal"}
                if target not in known:
                    return False, f"unknown target_id {target}"
                if not op.get("text"):
                    return False, "raise_objection needs text"
                o = WBObjection(id=f"O{len(self.objections) + 1}", author=author, target_id=target,
                                text=str(op["text"]), blocking=bool(op.get("blocking", False)))
                self.objections.append(o)
                return True, o.id
            if action == "resolve_objection":
                oid = str(op.get("id", ""))
                eids = list(op.get("evidence_ids", []) or [])
                resolution = str(op.get("resolution", ""))
                if not eids and not resolution:
                    return False, "resolve_objection needs evidence_ids or a resolution reason"
                known_e = {e.id for e in self.evidence}
                for e in eids:
                    if e not in known_e:
                        return False, f"unknown evidence id {e}"
                for o in self.objections:
                    if o.id == oid:
                        o.status = "resolved"
                        o.resolution = resolution
                        o.evidence_ids = eids
                        return True, oid
                return False, f"unknown objection {oid}"
            if action == "update_proposal":
                if not op.get("text"):
                    return False, "update_proposal needs text"
                cids = list(op.get("concept_ids", []) or [])
                known_c = {c.id for c in self.concepts}
                for c in cids:
                    if c not in known_c:
                        return False, f"unknown concept id {c}"
                claims = [WBClaim(claim=str(k.get("claim", "")), evidence_ids=list(k.get("evidence_ids", []) or []))
                          for k in (op.get("key_claims", []) or [])]
                version = (self.proposal.version + 1) if self.proposal else 1
                self.proposal = WBProposal(version=version, author=author, text=str(op["text"]),
                                           concept_ids=cids, key_claims=claims)
                self.votes.clear()  # any update_proposal clears all votes (spec §4.2)
                return True, f"proposal v{version}"
            if action == "vote":
                if self.proposal is None:
                    return False, "no proposal to vote on"
                self.votes[author] = WBVote(version=self.proposal.version,
                                            ready=bool(op.get("ready", False)),
                                            reason=str(op.get("reason", "")))
                return True, f"vote recorded for v{self.proposal.version}"
            if action == "read_evidence":
                eid = str(op.get("id", ""))
                for e in self.evidence:
                    if e.id == eid:
                        return True, e.output_full or e.output_summary
                return False, f"unknown evidence id {eid}"
            return False, f"unknown whiteboard action {action}"
        except Exception as exc:
            return False, f"whiteboard op error: {exc}"

    # -- closing rule --------------------------------------------------------------
    def consensus_reached(self, roster: list[str]) -> bool:
        if self.proposal is None:
            return False
        if any(o.blocking and o.status == "open" for o in self.objections):
            return False
        for member in roster:
            vote = self.votes.get(member)
            if vote is None or vote.version != self.proposal.version or not vote.ready:
                return False
        return True

    # -- rendering -------------------------------------------------------------------
    def render_markdown(self) -> str:
        lines: list[str] = ["# Whiteboard"]
        if self.inspirations:
            lines.append("## Inspirations")
            for ins in self.inspirations:
                lines.append(f"- {ins.get('archive_id')}: {ins.get('feedback_summary', '')}")
        lines.append("## Functions")
        for f in self.functions:
            lines.append(f"- {f.id} [{f.author}] {f.text}")
        lines.append("## Concepts")
        for c in self.concepts:
            if c.status == "dropped":
                lines.append(f"- {c.id} (dropped) {c.text}")
            else:
                lines.append(f"- {c.id} [{c.author}, {c.status}, for {c.function_id}] {c.text}")
        lines.append("## Evidence")
        for e in self.evidence:
            lines.append(f"- {e.id} [{e.tool}, {e.author}] {e.output_summary} ({e.status})")
        lines.append("## Objections")
        for o in self.objections:
            if o.status == "resolved":
                lines.append(f"- {o.id} (resolved) {o.text}")
            else:
                lines.append(f"- {o.id} [{o.author} -> {o.target_id}, blocking={o.blocking}] {o.text}")
        lines.append("## Proposal")
        if self.proposal:
            lines.append(f"- v{self.proposal.version} [{self.proposal.author}] {self.proposal.text} concepts={self.proposal.concept_ids}")
            for claim in self.proposal.key_claims:
                lines.append(f"  - claim: {claim.claim} evidence={claim.evidence_ids}")
        else:
            lines.append("- (none)")
        lines.append("## Votes")
        for member, vote in self.votes.items():
            lines.append(f"- {member}: ready={vote.ready} (v{vote.version}) {vote.reason}")
        return "\n".join(lines) + "\n"

    def render_warns(self) -> bool:
        return len(self.render_markdown()) / 4 > 30000

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.model_dump(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> Whiteboard:
        return cls.model_validate_json(path.read_text(encoding="utf-8"))


class HistoryLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
