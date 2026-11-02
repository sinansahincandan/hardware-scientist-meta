"""Shared tools with auto-posted evidence (spec §4.4). Members never edit evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from hs import sandbox
from hs.stage_a.whiteboard import Whiteboard

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {"type": "function", "name": "whiteboard",
     "description": "Write to the shared whiteboard. action is one of add_function, add_concept, "
                    "set_concept_status, raise_objection, resolve_objection, update_proposal, vote, read_evidence. "
                    "Pass the fields for that action as separate properties (never pack them into the action string).",
     "parameters": {"type": "object", "properties": {
         "action": {"type": "string"}, "id": {"type": "string"}, "function_id": {"type": "string"},
         "text": {"type": "string"}, "status": {"type": "string"}, "target_id": {"type": "string"},
         "blocking": {"type": "boolean"}, "resolution": {"type": "string"},
         "evidence_ids": {"type": "array", "items": {"type": "string"}},
         "concept_ids": {"type": "array", "items": {"type": "string"}},
         "key_claims": {"type": "array", "items": {"type": "object"}},
         "ready": {"type": "boolean"}, "reason": {"type": "string"}}, "required": ["action"]}},
    {"type": "function", "name": "calc", "description": "Evaluate an expression with math/numpy/pint Q_.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}, "purpose": {"type": "string"}},
                    "required": ["expression", "purpose"]}},
    {"type": "function", "name": "simulate", "description": "Run a short numpy/scipy/pint script in the sandbox.",
     "parameters": {"type": "object", "properties": {"script": {"type": "string"}, "purpose": {"type": "string"}},
                    "required": ["script", "purpose"]}},
    {"type": "function", "name": "sketch", "description": "Run a matplotlib script saving sketch.png.",
     "parameters": {"type": "object", "properties": {"script": {"type": "string"}, "caption": {"type": "string"}},
                    "required": ["script", "caption"]}},
    {"type": "function", "name": "vetted_calc",
     "description": "Run a vetted calculator: lever_effort, lead_screw_effort, cantilever_deflection, spring_mass_frequency, first_order_settling, natural_convection_plate, tuned_mass_damper_den_hartog. Args are SI floats; input_sources maps each arg to user|source|assumption.",
     "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "args": {"type": "object"},
                                                     "input_sources": {"type": "object"}, "purpose": {"type": "string"}},
                    "required": ["name", "args", "purpose"]}},
    {"type": "function", "name": "new_tool",
     "description": "Register a new calculation tool for this problem: python_source defines run(args) and "
                    "returns a result; smoke_test_input is passed to run() once in the sandbox before the tool "
                    "is registered. Registered tools become callable by every member from the next request.",
     "parameters": {"type": "object", "properties": {
         "name": {"type": "string"}, "description": {"type": "string"}, "parameters": {"type": "object"},
         "python_source": {"type": "string"}, "smoke_test_input": {"type": "object"}},
         "required": ["name", "description", "parameters", "python_source", "smoke_test_input"]}},
    {"type": "web_search", "search_context_size": "low"},
]

_NAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")


_NUMBER = re.compile(r"(?<![\w.])-?\d+\.\d{4,}(?:[eE][-+]?\d+)?")


def _three_sig(match: re.Match[str]) -> str:
    return f"{float(match.group(0)):.3g}"


def readable_result(out: str, ok: bool) -> str:
    """One readable line for the board (A7/B9): the last result lines with long decimals cut to
    3 significant figures; on failure, the exception line, never a raw traceback."""
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    if not lines:
        return "no output" if ok else "failed without a message"
    if not ok:
        return "failed: " + lines[-1][:300]
    tail = lines[-3:]
    return _NUMBER.sub(_three_sig, "; ".join(tail))[:400]


def parse_calc_inputs(expression: str) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    for i, m in enumerate(re.finditer(r"Q_\(\s*([^,\)]+)\s*(?:,\s*[\"']([^\"']+)[\"'])?\s*\)", expression)):
        inputs[f"arg{i}"] = {"value": m.group(1).strip(), "unit": m.group(2) or ""}
    return inputs


def resolve_citation(cit: dict[str, Any], query: str) -> dict[str, Any]:
    """Readable reference fields at record time (v2 D, B8): organisation (site), title, year when the
    title or URL states one, URL, the query, and the passage the search returned (may be empty)."""
    url = str(cit.get("url", "")).strip()
    title = str(cit.get("title", "")).strip()
    if not url:
        return {"authors_or_org": "unresolved source", "title": title or query,
                "year": "", "url": "", "query": query, "unresolved": True, "passage": ""}
    from urllib.parse import urlparse

    host = urlparse(url).netloc.replace("www.", "")
    year = str(cit.get("year") or cit.get("date") or "")[:4]
    if not year:
        found = re.search(r"(?<!\d)(19[5-9]\d|20[0-3]\d)(?!\d)", f"{title} {url}")
        year = found.group(1) if found else ""
    return {"authors_or_org": str(cit.get("author", "") or cit.get("authors", "") or host),
            "title": title or url, "year": year, "url": url, "query": query, "unresolved": False,
            "passage": str(cit.get("snippet", "") or "")}


def format_reference(ref: dict[str, Any]) -> str:
    if ref.get("unresolved"):
        return f"unresolved source (search: {ref.get('query', '')})"
    bits = [ref.get("authors_or_org", ""), ref.get("title", ""), ref.get("year", ""), ref.get("url", "")]
    return " — ".join(b for b in bits if b)


class ToolRunner:
    def __init__(self, board: Whiteboard, run_dir: Path, evidence_dir: Path) -> None:
        self.board = board
        self.run_dir = run_dir
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.new_tools: dict[str, dict[str, Any]] = {}
        self._load_registry()

    def schemas(self) -> list[dict[str, Any]]:
        """The shared tool list plus every registered tool (A7: registered tools are callable)."""
        extra = [{"type": "function", "name": name,
                  "description": str(rec.get("description", ""))[:1000] or f"custom tool {name}",
                  "parameters": rec.get("parameters") or {"type": "object", "properties": {}}}
                 for name, rec in self.new_tools.items()]
        return TOOL_SCHEMAS + extra

    def _registry_dir(self) -> Path:
        d = self.run_dir / "tools"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _load_registry(self) -> None:
        for path in self._registry_dir().glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.new_tools[data["name"]] = data
            except Exception:  # noqa: S112 — a corrupt registry file is skipped, never fatal
                continue

    # -- evidence helpers -------------------------------------------------------
    def _post(self, author: str, tool: str, purpose: str, code_or_query: str, summary: str,
              full: str = "", inputs: dict[str, Any] | None = None, sketch_path: str | None = None,
              status: str = "ok", cycle: int = 0) -> str:
        ev = self.board.add_evidence(author, tool, purpose, code_or_query, summary,
                                     output_full=full or summary, inputs=inputs or {},
                                     sketch_path=sketch_path, status=status, cycle=cycle)
        (self.evidence_dir / f"{ev.id}.json").write_text(
            json.dumps(ev.model_dump(), indent=2), encoding="utf-8")
        return ev.id

    # -- tools ---------------------------------------------------------------------
    def calc(self, author: str, expression: str, purpose: str, cycle: int = 0) -> tuple[str, str]:
        script = (
            "from pint import UnitRegistry\n"
            "ureg = UnitRegistry()\n"
            "Q_ = ureg.Quantity\n"
            "import math, numpy as np\n"
            f"__r = ({expression})\n"
            "print(__r)\n"
        )
        result = sandbox.run_script(script)
        out = (result.stdout.strip() or result.stderr.strip())
        summary = readable_result(out, result.ok)
        eid = self._post(author, "calc", purpose, expression, summary,
                         full=out, inputs=parse_calc_inputs(expression),
                         status="ok" if result.ok else "error", cycle=cycle)
        return eid, f"{eid}: {summary}"

    def simulate(self, author: str, script: str, purpose: str, cycle: int = 0) -> tuple[str, str]:
        result = sandbox.run_script(script)
        out = (result.stdout.strip() or result.stderr.strip())
        summary = readable_result(out, result.ok)
        eid = self._post(author, "simulate", purpose, script, summary,
                         full=out, status="ok" if result.ok else "error", cycle=cycle)
        return eid, f"{eid}: {summary}"

    def sketch(self, author: str, script: str, caption: str, cycle: int = 0) -> tuple[str, str]:
        result = sandbox.run_script(script)
        png = sandbox.sketch_bytes_of(result)
        sketch_rel: str | None = None
        if png:
            fname = f"sketch_{len(self.board.evidence) + 1}.png"
            (self.evidence_dir / fname).write_bytes(png)
            sketch_rel = f"evidence/{fname}"
        last_err = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "no image produced"
        summary = caption if (result.ok and png) else f"failed: {last_err}"[:300]
        eid = self._post(author, "sketch", caption, script, summary,
                         full=result.stdout, sketch_path=sketch_rel,
                         status="ok" if (result.ok and png) else "error", cycle=cycle)
        return eid, f"{eid}: {summary}"

    def vetted_calc(self, author: str, name: str, args: dict[str, Any],
                    input_sources: dict[str, Any] | None = None, purpose: str = "", cycle: int = 0) -> tuple[str, str]:
        from hs.stage_a.calculators import VETTED, run_vetted

        if name not in VETTED:
            eid = self._post(author, "vetted_calc", purpose or name, name,
                             f"unknown vetted calculator {name}", status="error", cycle=cycle)
            return eid, f"{eid}: error: unknown vetted calculator {name}"
        try:
            result = run_vetted(name, args, input_sources)
            summary = ", ".join(f"{k}={v} {result.get('unit', '')}".strip()
                                for k, v in result.items()
                                if k not in ("inputs", "provenance", "calculator", "unit"))[:200]
            eid = self._post(author, f"vetted_calc:{name}", purpose or name,
                             json.dumps({"args": args, "input_sources": input_sources or {}}),
                             summary, full=json.dumps(result, indent=2),
                             inputs=result.get("provenance", {}), cycle=cycle)
            return eid, f"{eid}: {summary}"
        except Exception as exc:
            eid = self._post(author, f"vetted_calc:{name}", purpose or name,
                             json.dumps({"args": args}), f"vetted_calc error: {exc}"[:200],
                             status="error", cycle=cycle)
            return eid, f"{eid}: error: {exc}"

    def web_search_evidence(self, author: str, sources: list[dict[str, Any]], cycle: int = 0) -> list[str]:
        """One evidence item per search result (B8): who searched, the query, and the source."""
        ids: list[str] = []
        for cit in sources:
            query = str(cit.get("query", "") or "")
            reference = resolve_citation(cit, query)
            passage = reference.get("passage", "")
            eid = self._post(author, "web_search", f"search: {query}" if query else "search", query,
                             format_reference(reference),
                             full=(f"{format_reference(reference)}\nPassage returned by the search: {passage}"
                                   if passage else f"{format_reference(reference)}\n(the search returned no passage text)"),
                             cycle=cycle)
            ev = next(e for e in self.board.evidence if e.id == eid)
            ev.references = [reference]
            (self.evidence_dir / f"{eid}.json").write_text(ev.model_dump_json(indent=2), encoding="utf-8")
            ids.append(eid)
        return ids

    def new_tool(self, author: str, name: str, description: str, parameters: dict[str, Any],
                 python_source: str, smoke_test_input: dict[str, Any]) -> tuple[bool, str]:
        from hs import config as _cfg

        if len(self.new_tools) >= _cfg.MAX_NEW_TOOLS:
            return False, f"new_tool cap {_cfg.MAX_NEW_TOOLS} reached"
        if not _NAME_RE.match(name) or name.count(".") > 1 or name in ("browser.search", "browser.open", "browser.find"):
            return False, f"invalid tool name {name}"
        if name in self.new_tools:
            return False, f"tool {name} already registered"
        smoke = f"{python_source}\nprint(run({smoke_test_input!r}))\n" if "def run" in python_source else python_source
        result = sandbox.run_script(smoke)
        if not result.ok:
            return False, f"smoke test failed: {result.stderr.strip()[:200]}"
        record = {"name": name, "description": description, "parameters": parameters,
                  "python_source": python_source, "author": author}
        (self._registry_dir() / f"{name}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        self.new_tools[name] = record
        self._post(author, "new_tool", f"register tool {name}", python_source,
                   f"tool {name} registered", status="ok")
        return True, f"tool {name} registered"

    def run_new_tool(self, author: str, name: str, args: dict[str, Any], cycle: int = 0) -> tuple[str, str]:
        record = self.new_tools[name]
        script = f"{record['python_source']}\nprint(run({args!r}))\n"
        result = sandbox.run_script(script)
        out = (result.stdout.strip() or result.stderr.strip())
        summary = readable_result(out, result.ok)
        eid = self._post(author, name, f"custom tool {name}", script, summary,
                         full=out, status="ok" if result.ok else "error", cycle=cycle)
        return eid, f"{eid}: {summary}"
