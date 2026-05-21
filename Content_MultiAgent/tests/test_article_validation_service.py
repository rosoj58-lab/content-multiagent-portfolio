"""Article validation service tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, WorkflowStage, WorkflowStatus
from seo_content_pipeline.services.article_validation_service import ArticleValidationService
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService


def _article(word_count: int = 600) -> str:
    words = " ".join(f"word{i}" for i in range(word_count))
    return f"# H1\n\n## H2\n\n### H3\n\n{words}"


def _service_setup(tmp_path) -> tuple[JobService, ArticleValidationService, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    return (
        JobService(settings=settings, artifact_store=store),
        ArticleValidationService(settings=settings, artifact_store=store),
        store,
    )


def test_article_validation_service_persists_passing_report(tmp_path) -> None:
    job_service, validation_service, store = _service_setup(tmp_path)
    job = job_service.create_job("Create content about SEO automation.")
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, _article(600))

    result = validation_service.validate_english_original(job.metadata.job_id, mode="demo")

    report = store.read_json(job.metadata.job_id, ArtifactKey.ARTICLE_VALIDATION)
    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    metadata = store.read_json(job.metadata.job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.RUNNING
    assert result.report.passed is True
    assert report["passed"] is True
    assert report["summary"] == "Deterministic article validation passed."
    assert state["current_stage"] == "writing"
    assert state["artifact_paths"]["article_validation"].endswith("article_validation.json")
    assert state["qa_flags"]["article_validation_passed"] is True
    assert metadata["status_history"][-1]["stage"] == "writing"


def test_article_validation_service_persists_failed_summary(tmp_path) -> None:
    job_service, validation_service, store = _service_setup(tmp_path)
    job = job_service.create_job("Create content about SEO automation.")
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, "# H1\n\nToo short.")

    result = validation_service.validate_english_original(job.metadata.job_id, mode="demo")

    report = store.read_json(job.metadata.job_id, ArtifactKey.ARTICLE_VALIDATION)
    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    failed_checks = [check for check in report["checks"] if check["passed"] is False]

    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert report["passed"] is False
    assert "Deterministic article validation failed" in report["summary"]
    assert {check["name"] for check in failed_checks} == {
        "article_word_count",
        "article_heading_structure",
    }
    assert report["routing_target"] == WorkflowStage.WRITING.value
    assert state["status"] == "needs_revision"
    assert state["qa_flags"]["article_validation_passed"] is False


def test_article_validation_service_reports_missing_required_artifact(tmp_path) -> None:
    job_service, validation_service, store = _service_setup(tmp_path)
    job = job_service.create_job("Create content about SEO automation.")

    result = validation_service.validate_english_original(job.metadata.job_id, mode="demo")

    report = store.read_json(job.metadata.job_id, ArtifactKey.ARTICLE_VALIDATION)
    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)

    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert report["checks"][0]["name"] == "required_artifact_english_original"
    assert report["checks"][0]["severity"] == "error"
    assert "Required artifact is missing" in report["summary"]
    assert state["artifact_paths"]["article_validation"].endswith("article_validation.json")
