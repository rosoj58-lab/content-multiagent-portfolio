"""SEO QA service tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, QAReport, SEOBrief, SEOBriefArtifact
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.seo_qa_service import SEOQAService
from seo_content_pipeline.validators.artifact_validators import validate_word_count


def _brief_artifact(job_id: str) -> SEOBriefArtifact:
    return SEOBriefArtifact(
        job_id=job_id,
        article_type=ArticleType.LP,
        brief=SEOBrief(
            topic="AI workflow for SEO content",
            goal="Show how a portfolio project automates content workflow.",
            audience="Technical hiring managers",
            main_keyword="multi-agent SEO content pipeline",
            secondary_keywords=["SEO automation"],
            lsi_keywords=["quality gates"],
            outline={
                "h1": "Multi-Agent SEO Content Pipeline",
                "sections": [{"h2": "SEO Automation Workflow", "h3": ["Quality Gates"]}],
            },
            tone_of_voice="Clear and technical",
            constraints=["Do not invent facts"],
        ),
    )


def _passing_article() -> str:
    return (
        "# Multi-Agent SEO Content Pipeline\n\n"
        "## SEO Automation Workflow\n\n"
        "### Quality Gates\n\n"
        "A multi-agent SEO content pipeline helps technical hiring managers inspect "
        "SEO automation, quality gates, and content workflow decisions."
    )


def _service_setup(tmp_path, *, max_revision_attempts: int = 2) -> tuple[JobService, SEOQAService, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path, max_revision_attempts=max_revision_attempts)
    store = ArtifactStore(settings.artifact_root)
    return (
        JobService(settings=settings, artifact_store=store),
        SEOQAService(settings=settings, artifact_store=store),
        store,
    )


def _prepare_job(
    tmp_path,
    *,
    article: str,
    editorial_passed: bool = True,
    max_revision_attempts: int = 2,
) -> tuple[str, SEOQAService, ArtifactStore]:
    job_service, service, store = _service_setup(
        tmp_path,
        max_revision_attempts=max_revision_attempts,
    )
    job = job_service.create_job("Create content about SEO automation.")
    store.write_json(job.metadata.job_id, ArtifactKey.BRIEF, _brief_artifact(job.metadata.job_id))
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, article)
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.ARTICLE_VALIDATION,
        QAReport(
            job_id=job.metadata.job_id,
            stage="writing",
            passed=True,
            checks=validate_word_count(article, min_words=1, max_words=200),
            summary="Deterministic article validation passed.",
        ),
    )
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.EDITORIAL_QA,
        QAReport(
            job_id=job.metadata.job_id,
            stage="editorial_review",
            passed=editorial_passed,
            checks=[],
            summary="Editorial QA passed." if editorial_passed else "Editorial QA failed.",
        ),
    )
    return job.metadata.job_id, service, store


def test_seo_qa_service_persists_passing_report(tmp_path) -> None:
    job_id, service, store = _prepare_job(tmp_path, article=_passing_article())

    result = service.run_seo_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.SEO_QA)
    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.report.passed is True
    assert report["stage"] == "seo_qa"
    assert report["passed"] is True
    assert state["current_stage"] == "seo_qa"
    assert state["status"] == "running"
    assert state["artifact_paths"]["seo_qa"].endswith("seo_qa.json")
    assert state["qa_flags"]["seo_qa_passed"] is True


def test_seo_qa_service_routes_failures_to_writing_revision(tmp_path) -> None:
    job_id, service, store = _prepare_job(
        tmp_path,
        article="# Unrelated Title\n\n## Overview\n\n### Details\n\nNothing relevant here.",
    )

    result = service.run_seo_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.SEO_QA)
    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.status.value == "needs_revision"
    assert report["passed"] is False
    assert report["routing_target"] == "writing"
    assert report["recommendations"]
    assert state["revision_attempts"]["seo_qa"] == 1
    assert state["revision_notes"]["seo_qa"]
    assert state["qa_flags"]["seo_qa_passed"] is False


def test_seo_qa_service_routes_to_human_review_when_revision_limit_is_reached(tmp_path) -> None:
    job_id, service, store = _prepare_job(
        tmp_path,
        article="# Unrelated Title\n\n## Overview\n\n### Details\n\nNothing relevant here.",
        max_revision_attempts=1,
    )
    service.run_seo_qa(job_id)

    result = service.run_seo_qa(job_id)

    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.status.value == "needs_human_review"
    assert state["status"] == "needs_human_review"
    assert state["errors"][0]["code"] == "seo_revision_limit_reached"


def test_seo_qa_service_requires_passed_editorial_qa(tmp_path) -> None:
    job_id, service, _store = _prepare_job(
        tmp_path,
        article=_passing_article(),
        editorial_passed=False,
    )

    try:
        service.run_seo_qa(job_id)
    except ValueError as error:
        assert "passed editorial QA" in str(error)
    else:
        raise AssertionError("expected ValueError")
