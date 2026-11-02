"""Runs inside the sandbox subprocess (spec §4.4). Sets env before imports."""
from __future__ import annotations

import os
import sys
import tempfile

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="hs-mpl-"))
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

try:
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (20 * 1024**2, 20 * 1024**2))
except Exception:
    pass

ALLOWED = {"math", "cmath", "statistics", "random", "json", "numpy", "scipy", "matplotlib", "PIL", "pint"}
_real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__


class _Hook:
    def find_module(self, name, path=None):  # legacy, unused on 3.12
        return None


import importlib.abc


class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        top = fullname.split(".")[0]
        if top in ALLOWED:
            return
        # Restrict only when the immediate importing frame is the user script;
        # library-internal imports (numpy importing datetime, ...) pass.
        frame = sys._getframe(1)
        try:
            while frame is not None:
                fname = frame.f_code.co_filename
                if "importlib" in fname or fname.endswith("launcher.py") or fname.startswith("<"):
                    frame = frame.f_back
                    continue
                if fname.endswith("hs_user_script.py") or "/hs-sandbox-" in fname:
                    raise ImportError(f"import of '{fullname}' is not allowed in the sandbox")
                break
        finally:
            del frame
        return


sys.meta_path.insert(0, _Finder())


def _install_file_guard(script: str) -> None:
    """Round-3 review finding 8: user code may read the Python installation and system files, but
    nothing else under the user's home folder (shell startup files hold the API key), and may write
    only inside its own temp folder. Audit hooks cannot be removed by the user script."""
    import pwd

    home = os.path.realpath(pwd.getpwuid(os.getuid()).pw_dir)
    work = os.path.realpath(os.path.dirname(os.path.abspath(script)))
    allowed_read = {os.path.realpath(p) for p in (sys.prefix, sys.base_prefix, sys.exec_prefix, work,
                                                  tempfile.gettempdir(), os.environ.get("MPLCONFIGDIR", ""))
                    if p}
    allowed_write = {work, os.path.realpath(os.environ.get("MPLCONFIGDIR", work))}

    def inside(path: str, roots: set[str]) -> bool:
        return any(path == r or path.startswith(r + os.sep) for r in roots)

    def guard(event: str, args: tuple) -> None:
        if event != "open" or not args or isinstance(args[0], int):
            return
        path = os.path.realpath(os.fsdecode(args[0]))
        mode, flags = (args[1] if len(args) > 1 else None), (args[2] if len(args) > 2 else 0)
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            mode is None and isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
        if writing and not inside(path, allowed_write):
            raise PermissionError(f"the sandbox may not write {path}")
        if inside(path, {home}) and not inside(path, allowed_read):
            raise PermissionError(f"the sandbox may not read files in the user's home folder: {path}")

    sys.addaudithook(guard)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: launcher.py <script>", file=sys.stderr)
        return 2
    script = sys.argv[1]
    with open(script, encoding="utf-8") as fh:
        code = fh.read()
    _install_file_guard(script)
    globals_dict: dict = {"__name__": "__main__", "__file__": script}
    exec(compile(code, script, "exec"), globals_dict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
