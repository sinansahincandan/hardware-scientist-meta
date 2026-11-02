import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
os.environ.setdefault("HS_FAKE", "1")
if os.environ.get("HS_SMOKE") != "1":
    # Tests never touch the real budget ledger; real smoke tests (HS_SMOKE=1) do.
    import tempfile

    os.environ["HS_BUDGET_LEDGER"] = str(Path(tempfile.mkdtemp(prefix="hs-test-budget-")) / "ledger.jsonl")
