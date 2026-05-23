"""CI workflow and README coverage tests."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_github_actions_ci_runs_project_quality_gate() -> None:
    workflow = REPO_ROOT / ".github" / "workflows" / "content-multiagent-ci.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "working-directory: Content_MultiAgent" in text
    assert "workflow_dispatch:" in text
    assert "contents: read" in text
    assert "python-version: \"3.12\"" in text
    assert "uv sync" in text
    assert "uv run ruff check ." in text
    assert "uv run pytest" in text


def test_readme_mentions_ci_quality_gate() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "GitHub Actions" in readme
    assert "uv run ruff check ." in readme
    assert "uv run pytest" in readme
