"""README and Docker documentation coverage tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_interview_demo_flow() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "CONTRIBUTING.md" in readme
    assert "SECURITY.md" in readme
    assert "docs/decisions/0001-offline-first-demo-and-provider-boundaries.md" in readme
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
    assert "make docker-build" in docker_docs
    assert "make docker-test" in docker_docs
    assert "make docker-up" in docker_docs
    assert "make docker-down" in docker_docs
    assert "make docker-logs" in docker_docs
    assert "make docker-shell" in docker_docs


def test_contributing_docs_cover_local_and_docker_quality_gates() -> None:
    contributing = (PROJECT_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "uv sync" in contributing
    assert "uv run ruff check ." in contributing
    assert "uv run pytest" in contributing
    assert "uv run streamlit run app.py" in contributing
    assert "make interview-check" in contributing
    assert "uv run seo-demo --demo bp --mode demo" in contributing
    assert "docker compose build" in contributing
    assert "docker compose run --rm app uv run pytest" in contributing
    assert "artifacts/jobs/*" in contributing
    assert "artifacts/demo/*" in contributing
    assert "SECURITY.md" in contributing


def test_security_docs_cover_secrets_artifacts_and_provider_boundaries() -> None:
    security = (PROJECT_ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert "uv run seo-demo --demo bp --mode demo" in security
    assert "uv run seo-demo --demo all --mode demo" in security
    assert "make interview-check" in security
    assert ".env.example" in security
    assert "OPENAI_API_KEY" in security
    assert "COPYLEAKS_EMAIL" in security
    assert "COPYLEAKS_API_KEY" in security
    assert "artifacts/jobs/*" in security
    assert "artifacts/demo/*" in security
    assert "provider boundaries" in security
    assert "Python 3.12" in security
