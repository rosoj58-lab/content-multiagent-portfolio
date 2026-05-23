"""Makefile and README command coverage tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_makefile_exposes_common_project_commands() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "lint:" in makefile
    assert "uv run ruff check ." in makefile
    assert "test:" in makefile
    assert "uv run pytest" in makefile
    assert "app:" in makefile
    assert "uv run streamlit run app.py" in makefile
    assert "demo:" in makefile
    assert "uv run seo-demo --demo bp --mode demo" in makefile
    assert "demo-all:" in makefile
    assert "uv run seo-demo --demo all --mode demo" in makefile
    assert "ci: lint test" in makefile


def test_readme_mentions_make_shortcuts() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "make lint" in readme
    assert "make test" in readme
    assert "make app" in readme
    assert "make demo" in readme
    assert "make demo-all" in readme
