"""README and Docker documentation coverage tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_interview_demo_flow() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Run full demo pipeline" in readme
    assert "artifacts/jobs/<job_id>/" in readme
    assert "final_package.md" in readme
    assert "final_qa_report.json" in readme
    assert "examples/inputs/bp-demo.txt" in readme
    assert "uv run seo-demo --demo bp --mode demo" in readme
    assert "uv run seo-demo --list-demos" in readme
    assert "uv run seo-demo --demo all --mode demo" in readme
    assert "--summary-file artifacts/demo/demo-summary.json" in readme
    assert "docker compose run --rm app uv run pytest" in readme


def test_docker_docs_match_current_streamlit_app() -> None:
    docker_docs = (PROJECT_ROOT / "docs" / "docker.md").read_text(encoding="utf-8")

    assert "http://localhost:8501" in docker_docs
    assert "Run full demo pipeline" in docker_docs
    assert "Project scaffold is ready" not in docker_docs
    assert "artifacts/jobs/<job_id>/" in docker_docs
