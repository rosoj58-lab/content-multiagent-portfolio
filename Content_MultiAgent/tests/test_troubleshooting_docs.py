"""Troubleshooting documentation tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_troubleshooting_docs_cover_demo_recovery_paths() -> None:
    text = (PROJECT_ROOT / "docs" / "troubleshooting.md").read_text(encoding="utf-8")

    assert "curl -I http://localhost:8501" in text
    assert "uv run streamlit run app.py --server.port 8502" in text
    assert "uv sync --frozen" in text
    assert "uv run seo-demo --demo bp --mode demo" in text
    assert "artifacts/jobs/<job_id>/" in text
    assert "docker compose up --build" in text
    assert "OPENAI_API_KEY=" in text
    assert "make ci" in text


def test_readme_links_troubleshooting_docs() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/troubleshooting.md" in readme
