"""Shared tools with auto-posted evidence (spec §4.4). Members never edit evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from hs import sandbox
from hs.stage_a.whiteboard import Whiteboard

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {"type": "function", "name": "whiteboard", "description": "Write to the shared whiteboard.",
     "parameters": {"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]}},
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
    {"type": "web_search", "search_context_size": "low"},
]

_NAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")


def parse_calc_inputs(expression: str) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    for i, m in enumerate(re.finditer(r"Q_\(\s*([^,\)]+)\s*(?:,\s*[\"']([^\"']+)[\"'])?\s*\)", expression)):
        inputs[f"arg{i}"] = {"value": m.group(1).strip(), "unit": m.group(2) or ""}
    return inputs


class ToolRunner:
    def __init__(self, board: Whiteboard, run_dir: Path, evidence_dir: Path) -> None:
        self.board = board
        self.run_dir = run_dir
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.new_tools: dict[str, dict[str, Any]] = {}
        self._load_registry()

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
        summary = out.splitlines()[-1] if out else "calc error"
        eid = self._post(author, "calc", purpose, expression, summary[:200],
                         full=out, inputs=parse_calc_inputs(expression),
                         status="ok" if result.ok else "error", cycle=cycle)
        return eid, f"{eid}: {summary}"

    def simulate(self, author: str, script: str, purpose: str, cycle: int = 0) -> tuple[str, str]:
        result = sandbox.run_script(script)
        out = (result.stdout.strip() or result.stderr.strip())
        summary = (out.splitlines()[-1] if out else "simulate done")[:200]
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
        summary = caption if result.ok else f"sketch error: {result.stderr.strip()[:120]}"
        eid = self._post(author, "sketch", caption, script, summary[:200],
                         full=result.stdout, sketch_path=sketch_rel,
                         status="ok" if result.ok else "error", cycle=cycle)
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

    def web_search_evidence(self, author: str, query: str, citations: list[dict[str, Any]], cycle: int = 0) -> list[str]:
        ids: list[str] = []
        for cit in citations:
            url = str(cit.get("url", ""))
            eid = self._post(author, "web_search", query, query,
                             f"source: {cit.get('title', '')} {url}"[:200], full=url, cycle=cycle)
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
        summary = (out.splitlines()[-1] if out else "tool done")[:200]
        eid = self._post(author, name, f"custom tool {name}", script, summary,
                         full=out, status="ok" if result.ok else "error", cycle=cycle)
        return eid, f"{eid}: {summary}"
