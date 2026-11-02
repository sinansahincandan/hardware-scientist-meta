"""Subprocess sandbox for LLM-written code (spec §4.4). Never exec in-process."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

MAX_CAPTURE = 4096


@dataclass
class SandboxResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool = False


def run_script(script: str, timeout: float = 10.0, extra_files: dict[str, bytes] | None = None) -> SandboxResult:
    launcher = Path(__file__).with_name("launcher.py")
    with tempfile.TemporaryDirectory(prefix="hs-sandbox-") as tmp:
        tmpdir = Path(tmp)
        script_path = tmpdir / "hs_user_script.py"
        script_path.write_text(script, encoding="utf-8")
        if extra_files:
            for name, data in extra_files.items():
                (tmpdir / name).write_bytes(data)
        env = {
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": tmp,
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": tmp,
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(launcher), str(script_path)],
                capture_output=True, text=True, timeout=timeout, cwd=tmp, env=env, check=False,
            )
            sketch = tmpdir / "sketch.png"
            sketch_bytes = sketch.read_bytes() if sketch.exists() else None
            result = SandboxResult(
                ok=proc.returncode == 0,
                stdout=(proc.stdout or "")[-MAX_CAPTURE:],  # the result and the error are at the end
                stderr=(proc.stderr or "")[-MAX_CAPTURE:],
                returncode=proc.returncode,
            )
            object.__setattr__(result, "_sketch_bytes", sketch_bytes)
            return result
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(
                ok=False,
                stdout=((exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""))[:MAX_CAPTURE],
                stderr="sandbox timeout",
                returncode=None,
                timed_out=True,
            )


def sketch_bytes_of(result: SandboxResult) -> bytes | None:
    return getattr(result, "_sketch_bytes", None)
