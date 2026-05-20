"""App shell structure tests."""

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_app_uses_controlled_error_for_empty_intake_input() -> None:
    tree = ast.parse((PROJECT_ROOT / "app.py").read_text(encoding="utf-8"))

    value_error_handlers = [
        handler
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        for handler in node.handlers
        if isinstance(handler.type, ast.Name) and handler.type.id == "ValueError"
    ]

    assert value_error_handlers
    assert any(
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "st"
        and call.func.attr == "error"
        for handler in value_error_handlers
        for call in ast.walk(handler)
        if isinstance(call, ast.Call)
    )
