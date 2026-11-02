"""Plain wording for requests the provider's content filter blocked (round 3, owner decision 2026-11-02):
a blocked request is retried once without numbers, units, ratings and product codes."""
from __future__ import annotations

import copy
import re
from typing import Any

_CODE = re.compile(r"[A-Z]{2,}[A-Za-z]*s?[,.;:)]*")


def plain_words(text: str) -> str:
    """Text without tokens that carry digits (sizes, ratings, model numbers) or all-capital codes."""
    kept = [w for w in text.split() if not re.search(r"\d", w) and not _CODE.fullmatch(w)]
    return re.sub(r"\s+([,.;:])", r"\1", " ".join(kept)).strip(" ,;")


def plain_text_keep_lines(text: str) -> str:
    return "\n".join(plain_words(line) for line in text.splitlines())


def plain_request(kwargs: dict[str, Any]) -> dict[str, Any]:
    """A copy of a Responses request with every text part in plain wording (images and tools unchanged)."""
    out = copy.deepcopy(kwargs)
    if isinstance(out.get("instructions"), str):
        out["instructions"] = plain_text_keep_lines(out["instructions"])
    for item in out.get("input", []) or []:
        if item.get("type") == "function_call_output" and isinstance(item.get("output"), str):
            item["output"] = plain_text_keep_lines(item["output"])
        for block in item.get("content", []) if isinstance(item.get("content"), list) else []:
            if block.get("type") == "input_text":
                block["text"] = plain_text_keep_lines(block.get("text", ""))
    return out
