"""Makefile and README command coverage tests."""

from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_makefile_exposes_common_project_commands() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "help:" in makefile
    assert ".DEFAULT_GOAL := help" in makefile
    assert "Available commands:" in makefile
    assert "lint:" in makefile
    assert "uv run ruff check ." in makefile
    assert "test:" in makefile
    assert "uv run pytest" in makefile
    assert "app:" in makefile
    assert "uv run streamlit run app.py" in makefile
    assert "demo:" in makefile
    assert "uv run seo-demo --demo bp --mode demo" in makefile
    assert "demo-list:" in makefile
    assert "uv run seo-demo --list-demos" in makefile
    assert "demo-all:" in makefile
    assert "uv run seo-demo --demo all --mode demo" in makefile
    assert "--summary-file artifacts/demo/demo-summary.json" in makefile
    assert "ci: lint test" in makefile
    assert "interview-check: ci demo-list demo-all" in makefile
    assert "docker-build:" in makefile
    assert "docker compose -f ../compose.yaml build" in makefile
    assert "docker-test:" in makefile
    assert "docker compose -f ../compose.yaml run --rm app uv run pytest" in makefile
    assert "docker-up:" in makefile
    assert "docker compose -f ../compose.yaml up" in makefile
    assert "docker-down:" in makefile
    assert "docker compose -f ../compose.yaml down" in makefile
    assert "docker-logs:" in makefile
    assert "docker compose -f ../compose.yaml logs -f app" in makefile
    assert "docker-shell:" in makefile
    assert "docker compose -f ../compose.yaml run --rm app sh" in makefile


def test_make_help_prints_available_commands() -> None:
    result = subprocess.run(
        ["make", "--no-print-directory", "help"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Available commands:" in result.stdout
    assert "make interview-check" in result.stdout
    assert "make docker-shell" in result.stdout


def test_readme_mentions_make_shortcuts() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "make help" in readme
    assert "make lint" in readme
    assert "make test" in readme
    assert "make app" in readme
    assert "make demo" in readme
    assert "make demo-list" in readme
    assert "make demo-all" in readme
    assert "make interview-check" in readme
    assert "make docker-build" in readme
    assert "make docker-test" in readme
    assert "make docker-up" in readme
    assert "make docker-down" in readme
    assert "make docker-logs" in readme
    assert "make docker-shell" in readme
    assert "artifacts/demo/demo-summary.json" in readme
    assert "`version` and `run_count`" in readme
