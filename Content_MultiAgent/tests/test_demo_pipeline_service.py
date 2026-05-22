"""Deterministic demo pipeline tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService


def test_demo_pipeline_service_builds_approved_final_package(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable portfolio demo notes for SEO automation.",
        ArticleType.BP,
    )

    result = DemoPipelineService(settings=settings, artifact_store=store).run_full_demo(
        job.metadata.job_id,
        mode="demo",
    )

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    final_report = store.read_json(job.metadata.job_id, ArtifactKey.FINAL_QA_REPORT)
    final_package = store.read_json(job.metadata.job_id, ArtifactKey.FINAL_PACKAGE_JSON)
    article = store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL)

    assert result.status is WorkflowStatus.APPROVED
    assert result.final_package_path.endswith("final_package.md")
    assert result.final_qa_report_path.endswith("final_qa_report.json")
    assert state["status"] == WorkflowStatus.APPROVED.value
    assert state["qa_flags"]["final_qa_passed"] is True
    assert state["uniqueness_score"] == 94.0
    assert final_report["status"] == WorkflowStatus.APPROVED.value
    assert final_report["failed_checks"] == []
    assert final_package["workflow_status"]["status"] == WorkflowStatus.APPROVED.value
    assert "multi-agent seo content pipeline" in article.lower()


def test_demo_pipeline_service_supports_full_mode_word_count(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable portfolio demo notes for a landing page.",
        ArticleType.LP,
    )

    result = DemoPipelineService(settings=settings, artifact_store=store).run_full_demo(
        job.metadata.job_id,
        mode="full",
    )

    article_validation = store.read_json(job.metadata.job_id, ArtifactKey.ARTICLE_VALIDATION)
    word_count_check = next(
        check for check in article_validation["checks"] if check["name"] == "article_word_count"
    )

    assert result.status is WorkflowStatus.APPROVED
    assert word_count_check["passed"] is True
    assert word_count_check["severity"] == "info"
    assert 1500 <= word_count_check["metadata"]["word_count"] <= 1600
