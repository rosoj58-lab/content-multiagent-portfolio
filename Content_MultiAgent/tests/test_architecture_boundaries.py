"""Architecture boundary tests for the Streamlit entrypoint."""

import ast
from pathlib import Path


FORBIDDEN_IMPORT_PREFIXES = (
    "seo_content_pipeline.config",
    "seo_content_pipeline.services.artifact_store",
    "seo_content_pipeline.graph.nodes",
    "seo_content_pipeline.prompts",
    "seo_content_pipeline.validators",
    "seo_content_pipeline.providers.manual_uniqueness",
    "seo_content_pipeline.providers.mock_uniqueness",
    "seo_content_pipeline.providers.copyleaks_uniqueness",
)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)

    return modules


def test_app_does_not_import_forbidden_implementation_layers() -> None:
    app_path = Path(__file__).resolve().parents[1] / "app.py"

    imports = _imported_modules(app_path)

    forbidden = {
        module
        for module in imports
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in FORBIDDEN_IMPORT_PREFIXES)
    }
    assert forbidden == set()
