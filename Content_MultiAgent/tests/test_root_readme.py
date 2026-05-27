"""Repository root README coverage tests."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_readme_points_to_portfolio_project() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Content_MultiAgent/README.md" in readme
    assert "Content_MultiAgent/CHANGELOG.md" in readme
    assert "Content_MultiAgent/CONTRIBUTING.md" in readme
    assert "MVP release notes" in readme
    assert "Content_MultiAgent/docs/interview-cheatsheet.md" in readme
    assert "Content_MultiAgent/examples/outputs/" in readme
    assert "uv run streamlit run app.py" in readme
    assert "uv run seo-demo --demo bp --mode demo" in readme
    assert "Generate live SEO brief" in readme
    assert "complete demo remains offline" in readme
    assert "uv run pytest" in readme
