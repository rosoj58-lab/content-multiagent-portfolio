"""Changelog documentation tests."""

from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_changelog_documents_current_portfolio_release() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## {pyproject['project']['version']} - Portfolio MVP" in changelog
    assert "seo-demo" in changelog
    assert "make interview-check" in changelog
    assert "LP editorial revision" in changelog
    assert "GP human-review escalation" in changelog
    assert "Decision QA Scorecard" in changelog
    assert "Docker development environment" in changelog
    assert "GitHub Actions quality gate" in changelog
    assert "Tracked example outputs" in changelog
    assert "Known Limits" in changelog
    assert "deterministic offline content" in changelog
    assert "File-based persistence" in changelog


def test_readme_links_changelog() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "CHANGELOG.md" in readme
    assert "MVP release notes" in readme
