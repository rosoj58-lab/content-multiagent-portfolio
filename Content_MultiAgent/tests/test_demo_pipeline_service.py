"""Deterministic demo pipeline tests."""

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService


SAFE_LP_CORRECTION = "The landing page presents only supplied evidence."


def test_demo_pipeline_service_builds_approved_final_package(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable portfolio demo notes for SEO automation.",
        ArticleType.BP,
    )

    result = DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job.metadata.job_id,
        mode="demo",
    )

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    final_report = store.read_json(job.metadata.job_id, ArtifactKey.FINAL_QA_REPORT)
    final_package = store.read_json(job.metadata.job_id, ArtifactKey.FINAL_PACKAGE_JSON)
    article = store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL)

    assert result.status is WorkflowStatus.APPROVED
    assert result.decision_artifact_path.endswith("final_qa_report.json")
    assert result.final_package_path.endswith("final_package.md")
    assert result.final_qa_report_path.endswith("final_qa_report.json")
    assert store.artifact_path(job.metadata.job_id, ArtifactKey.RUN_SUMMARY).exists()
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
        ArticleType.BP,
    )

    result = DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
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


def test_landing_page_demo_stops_on_editorial_revision_for_unsupported_claim(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Landing page source notes with controlled proof requirements.",
        ArticleType.LP,
    )

    result = DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job.metadata.job_id,
        mode="demo",
    )

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    editorial = store.read_json(job.metadata.job_id, ArtifactKey.EDITORIAL_QA)
    article = store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL)

    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert result.decision_artifact_path.endswith("editorial_qa.json")
    assert result.final_package_path is None
    assert store.artifact_path(job.metadata.job_id, ArtifactKey.RUN_SUMMARY).exists()
    assert "70 percent" in article
    assert editorial["passed"] is False
    assert editorial["routing_target"] == "writing"
    assert state["status"] == "needs_revision"
    assert state["revision_notes"]["editorial_review"] == [
        "Remove the 70 percent claim or provide evidence."
    ]


def test_guest_post_demo_stops_for_human_link_placement_review(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Guest post source notes with sensitive contextual link placement.",
        ArticleType.GP,
    )

    result = DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job.metadata.job_id,
        mode="demo",
    )

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    editorial = store.read_json(job.metadata.job_id, ArtifactKey.EDITORIAL_QA)
    article = store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL)

    assert result.status is WorkflowStatus.NEEDS_HUMAN_REVIEW
    assert result.decision_artifact_path.endswith("editorial_qa.json")
    assert result.final_package_path is None
    assert store.artifact_path(job.metadata.job_id, ArtifactKey.RUN_SUMMARY).exists()
    assert "https://example.com/seo-content-pipeline" in article
    assert editorial["requires_human_review"] is True
    assert editorial["routing_target"] is None
    assert state["errors"][0]["code"] == "editorial_human_review_required"
    assert state["revision_notes"]["editorial_review"] == [
        "Confirm that the contextual project link is acceptable to the host publication."
    ]


@pytest.mark.parametrize("mode", ["demo", "full"])
def test_landing_page_revision_preserves_failed_decision_and_reaches_approval(
    tmp_path,
    mode,
) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Landing page source notes with controlled proof requirements.",
        ArticleType.LP,
    )
    service = DemoPipelineService(settings=settings, artifact_store=store)
    service.run_demo_scenario(job.metadata.job_id, mode=mode)

    result = service.apply_lp_editorial_revision(
        job.metadata.job_id,
        SAFE_LP_CORRECTION,
        mode=mode,
    )

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    history = store.read_json(job.metadata.job_id, ArtifactKey.REVISION_HISTORY)
    editorial = store.read_json(job.metadata.job_id, ArtifactKey.EDITORIAL_QA)
    article = store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL)
    rejected_article = store.read_text(job.metadata.job_id, ArtifactKey.REJECTED_ENGLISH_ORIGINAL)

    assert result.job_id == job.metadata.job_id
    assert result.status is WorkflowStatus.APPROVED
    assert result.final_package_path.endswith("final_package.md")
    assert store.artifact_path(job.metadata.job_id, ArtifactKey.RUN_SUMMARY).exists()
    assert "70 percent" not in article
    assert SAFE_LP_CORRECTION in article
    assert "70 percent" in rejected_article
    assert editorial["passed"] is True
    assert history["revisions"][0]["failed_report"]["checks"][0]["name"] == "unsupported_factual_claims"
    assert history["revisions"][0]["correction_statement"] == SAFE_LP_CORRECTION
    assert history["revisions"][0]["rejected_article_path"].endswith("english_original_rejected.md")
    assert history["revisions"][0]["approved_article_path"].endswith("english_original.md")
    assert history["revisions"][0]["resolved_status"] == "approved"
    assert history["revisions"][0]["resolved_at"]
    assert state["artifact_paths"]["revision_history"].endswith("revision_history.json")
    assert state["artifact_paths"]["rejected_english_original"].endswith(
        "english_original_rejected.md"
    )
    assert state["revision_attempts"]["editorial_review"] == 1


@pytest.mark.parametrize("article_type", [ArticleType.BP, ArticleType.GP])
def test_lp_revision_rejects_non_landing_page_outcomes(tmp_path, article_type) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable source notes for invalid correction.",
        article_type,
    )
    service = DemoPipelineService(settings=settings, artifact_store=store)
    service.run_demo_scenario(job.metadata.job_id, mode="demo")

    with pytest.raises(ValueError, match="LP correction requires"):
        service.apply_lp_editorial_revision(job.metadata.job_id, SAFE_LP_CORRECTION, mode="demo")

    assert not store.artifact_path(job.metadata.job_id, ArtifactKey.REVISION_HISTORY).exists()
    assert not store.artifact_path(
        job.metadata.job_id, ArtifactKey.REJECTED_ENGLISH_ORIGINAL
    ).exists()


def test_lp_revision_rejects_inconsistent_editorial_report_without_writing_history(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Landing page source notes with controlled proof requirements.",
        ArticleType.LP,
    )
    service = DemoPipelineService(settings=settings, artifact_store=store)
    service.run_demo_scenario(job.metadata.job_id, mode="demo")
    editorial = store.read_json(job.metadata.job_id, ArtifactKey.EDITORIAL_QA)
    editorial["passed"] = True
    editorial["routing_target"] = None
    store.write_json(job.metadata.job_id, ArtifactKey.EDITORIAL_QA, editorial)

    with pytest.raises(ValueError, match="routed failed editorial report"):
        service.apply_lp_editorial_revision(job.metadata.job_id, SAFE_LP_CORRECTION, mode="demo")

    assert not store.artifact_path(job.metadata.job_id, ArtifactKey.REVISION_HISTORY).exists()
    assert not store.artifact_path(
        job.metadata.job_id, ArtifactKey.REJECTED_ENGLISH_ORIGINAL
    ).exists()


@pytest.mark.parametrize(
    ("statement", "expected_message"),
    [
        (" ", "must not be empty"),
        ("Guaranteed 45% lower costs.", "common promotional result wording"),
        ("We promise lower costs for every team.", "common promotional result wording"),
        ("Lower costs for every team.", "common promotional result wording"),
        ("Higher conversions for growing teams.", "common promotional result wording"),
        ("Higher profits and improved margins.", "common promotional result wording"),
        ("Sales growth for every team.", "common promotional result wording"),
        ("Evidence " * 21, "20 words or fewer"),
    ],
)
def test_lp_operator_correction_rejects_unsafe_input_without_mutating_artifacts(
    tmp_path,
    statement,
    expected_message,
) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Landing page source notes with controlled proof requirements.",
        ArticleType.LP,
    )
    service = DemoPipelineService(settings=settings, artifact_store=store)
    service.run_demo_scenario(job.metadata.job_id, mode="demo")
    original_article = store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL)

    with pytest.raises(ValueError, match=expected_message):
        service.apply_lp_editorial_revision(job.metadata.job_id, statement, mode="demo")

    state = store.read_json(job.metadata.job_id, ArtifactKey.STATE)
    assert state["status"] == WorkflowStatus.NEEDS_REVISION.value
    assert store.read_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL) == original_article
    assert not store.artifact_path(job.metadata.job_id, ArtifactKey.REVISION_HISTORY).exists()
    assert not store.artifact_path(
        job.metadata.job_id, ArtifactKey.REJECTED_ENGLISH_ORIGINAL
    ).exists()


def test_lp_revision_cannot_be_reapplied_after_approval(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Landing page source notes with controlled proof requirements.",
        ArticleType.LP,
    )
    service = DemoPipelineService(settings=settings, artifact_store=store)
    service.run_demo_scenario(job.metadata.job_id, mode="demo")
    service.apply_lp_editorial_revision(job.metadata.job_id, SAFE_LP_CORRECTION, mode="demo")

    with pytest.raises(ValueError, match="LP correction requires"):
        service.apply_lp_editorial_revision(job.metadata.job_id, SAFE_LP_CORRECTION, mode="demo")

    history = store.read_json(job.metadata.job_id, ArtifactKey.REVISION_HISTORY)
    assert len(history["revisions"]) == 1
