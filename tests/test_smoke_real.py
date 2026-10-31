"""Real-API smoke tests (spec §11, §14). NOT run in fake mode.

Run manually (see CHECKPOINT.md):
  HS_SMOKE=1 .venv/bin/python -m pytest tests/test_smoke_real.py -q
"""
import os

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("HS_SMOKE") != "1", reason="real API smoke test; set HS_SMOKE=1")


def test_structured_output_shape():
    """Settles §14.1: text.format nesting on /v1/responses."""
    from hs.client import MetaClient
    from hs.schemas import Verdict

    client = MetaClient()
    verdict = client.structured("evaluator", Verdict,
                                "Reply with a verdict.", "Say accept=false with brief feedback.")
    assert isinstance(verdict.accept, bool)


def test_truncation_shape():
    """Settles §14.8: provoke truncation with max_output_tokens=16 and record the shape."""
    from hs.client import MetaClient

    client = MetaClient()
    resp = client.responses(role="member", instructions="Count slowly.",
                            input_items=[{"type": "message", "role": "user",
                                          "content": [{"type": "input_text", "text": "Count to 100."}]}],
                            max_output_tokens=16)
    print(f"status={getattr(resp, 'status', None)} incomplete={getattr(resp, 'incomplete_details', None)}")
