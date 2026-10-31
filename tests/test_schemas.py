import pytest
from pydantic import BaseModel

from hs.schemas import DesignerEval, SolutionPrompt, Verdict, make_strict_schema


def _walk(node, root=True):
    if isinstance(node, dict):
        assert "allOf" not in node and "oneOf" not in node
        if node.get("type") == "object" or "properties" in node:
            assert node.get("additionalProperties") is False
            assert sorted(node.get("required", [])) == sorted(node.get("properties", {}).keys())
        for v in node.values():
            _walk(v, root=False)
    elif isinstance(node, list):
        for v in node:
            _walk(v, root=False)


def test_strict_schema_rules():
    for model in (Verdict, SolutionPrompt, DesignerEval):
        schema = make_strict_schema(model)
        assert schema["type"] == "object"
        for banned in ("anyOf", "oneOf", "allOf", "enum", "not"):
            assert banned not in schema
        _walk(schema)


def test_strict_schema_recursive_ref_rejected():
    class Node(BaseModel):
        name: str
        child: "Node | None" = None

    Node.model_rebuild()
    with pytest.raises(ValueError):
        make_strict_schema(Node)
