"""Pre-commit check: no secret and no file over 50 MB in tracked or staged files.

Prints file names only, never the matched text. Exit code 1 on any hit.
Usage: .venv/bin/python scripts/secret_scan.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 50 * 1024 * 1024
# An assignment of a long literal to a key-like name (placeholders such as <your key> do not match).
ASSIGNMENT = re.compile(rb"(API_KEY|SECRET|TOKEN)\w*\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{24,}")


def _files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z", "--cached"], cwd=ROOT, capture_output=True, check=True)
    return [ROOT / p for p in out.stdout.decode().split("\0") if p]


def _known_secrets() -> list[bytes]:
    values = [os.environ.get("MODEL_API_KEY", "")]
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                values.append(line.split("=", 1)[1].strip().strip("'\""))
    return [v.encode() for v in values if len(v) >= 16]


def main() -> int:
    secrets = _known_secrets()
    problems: list[str] = []
    for path in _files():
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_BYTES:
            problems.append(f"over 50 MB: {path.relative_to(ROOT)}")
            continue
        data = path.read_bytes()
        if any(s in data for s in secrets):
            problems.append(f"contains the API key: {path.relative_to(ROOT)}")
        elif ASSIGNMENT.search(data):
            problems.append(f"looks like a hard-coded secret: {path.relative_to(ROOT)}")
    for p in problems:
        print(p)
    print("secret scan: " + ("FAILED" if problems else f"clean ({len(secrets)} known secret(s) checked)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
