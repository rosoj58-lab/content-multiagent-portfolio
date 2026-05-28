"""README and Docker documentation coverage tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_interview_demo_flow() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "CONTRIBUTING.md" in readme
    assert "SECURITY.md" in readme
    assert "docs/decisions/0001-offline-first-demo-and-provider-boundaries.md" in readme
    assert "Run demo scenario" in readme
    assert "Decision QA Scorecard" in readme
    assert "Replacement statement" in readme
    assert "Apply correction" in readme
    assert "revision_history.json" in readme
    assert "english_original_rejected.md" in readme
    assert "artifacts/jobs/<job_id>/" in readme
    assert "final_package.md" in readme
    assert "final_qa_report.json" in readme
    assert "run_summary.json" in readme
    assert "Recent jobs" in readme
    assert "examples/inputs/bp-demo.txt" in readme
    assert "uv run seo-demo --demo bp --mode demo" in readme
    assert "uv run seo-demo --list-demos" in readme
    assert "uv run seo-demo --demo all --mode demo" in readme
    assert "--summary-file artifacts/demo/demo-summary.json" in readme
    assert "Generate live SEO brief" in readme
    assert "OPENAI_MODEL=gpt-5.4-mini" in readme
    assert "explicit paid action" in readme
    assert "docker compose run --rm app uv run pytest" in readme


def test_docker_docs_match_current_streamlit_app() -> None:
    docker_docs = (PROJECT_ROOT / "docs" / "docker.md").read_text(encoding="utf-8")

    assert "http://localhost:8501" in docker_docs
    assert "Run demo scenario" in docker_docs
    assert "OPENAI_MODEL=gpt-5.4-mini" in docker_docs
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
    assert "OPENAI_MODEL" in security
    assert "Generate live SEO brief" in security
    assert "COPYLEAKS_EMAIL" in security
    assert "COPYLEAKS_API_KEY" in security
    assert "artifacts/jobs/*" in security
    assert "artifacts/demo/*" in security
    assert "provider boundaries" in security
    assert "Python 3.12" in security


def test_release_checklist_covers_quality_demo_docker_docs_and_security() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    checklist = (PROJECT_ROOT / "docs" / "release-checklist.md").read_text(
        encoding="utf-8"
    )

    assert "docs/release-checklist.md" in readme
    assert "uv sync" in checklist
    assert "uv run ruff check ." in checklist
    assert "uv run pytest" in checklist
    assert "make interview-check" in checklist
    assert "make release-check" in checklist
    assert "uv run seo-demo --demo bp --mode demo" in checklist
    assert "--summary-file artifacts/demo/demo-summary.json" in checklist
    assert "artifacts/jobs/<job_id>/" in checklist
    assert "final_package.md" in checklist
    assert "final_qa_report.json" in checklist
    assert "needs_revision" in checklist
    assert "needs_human_review" in checklist
    assert "Replacement statement" in checklist
    assert "Apply correction" in checklist
    assert "revision_history.json" in checklist
    assert "english_original_rejected.md" in checklist
    assert "Revision Comparison" in checklist
    assert "Generate live SEO brief" in checklist
    assert "waiting_for_human" in checklist
    assert "docker compose build" in checklist
    assert "docker compose run --rm app uv run pytest" in checklist
    assert "CHANGELOG.md" in checklist
    assert "SECURITY.md" in checklist
    assert "docs/decisions/" in checklist
    assert "git status --short" in checklist
