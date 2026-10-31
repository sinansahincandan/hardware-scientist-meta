import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
os.environ.setdefault("HS_FAKE", "1")
