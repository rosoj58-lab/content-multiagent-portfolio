"""Testing strategy documentation tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_testing_strategy_documents_quality_gate_and_coverage() -> None:
    strategy = (PROJECT_ROOT / "docs" / "testing-strategy.md").read_text(encoding="utf-8")

    assert "uv sync --frozen" in strategy
    assert "uv run ruff check ." in strategy
    assert "uv run pytest" in strategy
    assert "offline demo pipeline" in strategy
    assert "Final package and final QA" in strategy
    assert "LP editorial revision routing" in strategy
    assert "GP human-review escalation" in strategy
    assert "decision QA scorecard" in strategy
    assert "LP correction lifecycle" in strategy
    assert "LP version comparison" in strategy
    assert "Documentation and repository health" in strategy
    assert "What Is Not Covered Yet" in strategy


def test_readme_links_testing_strategy() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/testing-strategy.md" in readme
