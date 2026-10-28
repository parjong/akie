"""Dependencies flow downward only: service -> storage -> core."""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).parents[2] / "src" / "akie" / "_internal"

# layer -> layers it must not import from
FORBIDDEN = {
    "core": {"storage", "service", "cli"},
    "storage": {"service", "cli"},
    "service": {"cli"},
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_does_not_import_upward(layer: str) -> None:
    for path in sorted((SRC / layer).rglob("*.py")):
        for module in imported_modules(path):
            for upper in FORBIDDEN[layer]:
                assert not module.startswith(f"akie._internal.{upper}"), (
                    f"{path.relative_to(SRC)} imports {module}"
                )
            assert module != "akie", f"{path.relative_to(SRC)} imports the public API"
