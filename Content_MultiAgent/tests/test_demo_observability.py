"""Demo observability view tests."""

import ast
from pathlib import Path

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import (
    ArtifactKey,
    ArticleType,
    PipelineState,
    QAReport,
    StatusHistoryEntry,
    ValidationCheck,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.stage_view_builder import build_pipeline_stage_views
from seo_content_pipeline.ui.artifact_panel import build_artifact_previews
from seo_content_pipeline.ui.error_presenter import build_controlled_error
from seo_content_pipeline.ui.qa_scorecard import build_decision_scorecard
from seo_content_pipeline.ui.renderers import build_qa_checklist


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pipeline_stage_views_include_progress_artifacts_and_revision_counters() -> None:
    state = PipelineState(
        job_id="job-123",
        current_stage=WorkflowStage.SEO_QA,
        status=WorkflowStatus.NEEDS_REVISION,
        artifact_paths={
            ArtifactKey.INPUT: "/tmp/input.json",
            ArtifactKey.BRIEF: "/tmp/brief.json",
            ArtifactKey.SEO_QA: "/tmp/seo_qa.json",
        },
        status_history=[
            StatusHistoryEntry(
                stage=WorkflowStage.INPUT_RECEIVED,
                status=WorkflowStatus.RUNNING,
                message="Job created.",
            ),
            StatusHistoryEntry(
                stage=WorkflowStage.BRIEF_DRAFTED,
                status=WorkflowStatus.RUNNING,
                message="Brief generated.",
            ),
        ],
        revision_attempts={WorkflowStage.SEO_QA: 1},
        revision_notes={WorkflowStage.SEO_QA: ["Keyword coverage is weak."]},
    )

    views = build_pipeline_stage_views(state, max_revision_attempts=2)
    seo_view = next(view for view in views if view.stage is WorkflowStage.SEO_QA)
    final_view = next(view for view in views if view.stage is WorkflowStage.FINAL_QA)

    assert [view.stage for view in views][0] is WorkflowStage.INPUT_RECEIVED
    assert seo_view.status is WorkflowStatus.NEEDS_REVISION
    assert seo_view.revision_attempt == 1
    assert seo_view.max_revision_attempts == 2
    assert seo_view.blocking_reason == "Keyword coverage is weak."
    assert ArtifactKey.SEO_QA in seo_view.artifact_links
    assert final_view.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert final_view.available_actions == []


def test_artifact_previews_handle_json_and_markdown(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job("Demo input")
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, "# Demo Article\n\nBody.")

    previews = build_artifact_previews(
        job.metadata.job_id,
        store,
        artifact_keys=[ArtifactKey.INPUT, ArtifactKey.ENGLISH_ORIGINAL],
    )

    assert [preview.key for preview in previews] == [ArtifactKey.INPUT, ArtifactKey.ENGLISH_ORIGINAL]
    assert previews[0].content_type == "application/json"
    assert '"dry_input": "Demo input"' in previews[0].preview
    assert previews[1].content_type == "text/markdown"
    assert previews[1].preview.startswith("# Demo Article")
    assert previews[1].content.strip() == "# Demo Article\n\nBody."
    assert all(preview.download_label.startswith("Download") for preview in previews)


def test_artifact_panel_render_exposes_download_action() -> None:
    tree = ast.parse((PROJECT_ROOT / "src/seo_content_pipeline/ui/artifact_panel.py").read_text(encoding="utf-8"))

    assert any(
        isinstance(call.func, ast.Attribute) and call.func.attr == "download_button"
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
    )


def test_qa_checklist_maps_passed_and_failed_checks() -> None:
    report = QAReport(
        job_id="job-123",
        stage=WorkflowStage.SEO_QA,
        passed=False,
        summary="SEO QA failed.",
        checks=[
            ValidationCheck(
                name="keyword_in_h1",
                passed=True,
                severity="info",
                message="Main keyword appears in H1.",
            ),
            ValidationCheck(
                name="keyword_coverage",
                passed=False,
                severity="error",
                message="Secondary keyword coverage is weak.",
            ),
        ],
    )

    checklist = build_qa_checklist(report)

    assert [item.name for item in checklist] == ["keyword_in_h1", "keyword_coverage"]
    assert checklist[0].status_label == "Pass"
    assert checklist[1].status_label == "Fail"
    assert checklist[1].severity == "error"


def test_controlled_error_includes_action_without_traceback() -> None:
    error = build_controlled_error(
        ValueError("dry input must not be empty"),
        action="Paste a demo input and try again.",
    )

    assert error.title == "Action needed"
    assert "dry input" in error.detail
    assert error.action == "Paste a demo input and try again."
    assert "Traceback" not in error.detail


def _run_scorecard_demo(tmp_path, article_type: ArticleType):
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable source notes for the scorecard demo.",
        article_type,
    )
    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job.metadata.job_id,
        mode="demo",
    )
    return build_decision_scorecard(job.metadata.job_id, store)


def test_decision_scorecard_is_hidden_before_a_terminal_decision(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job("Source notes.")

    assert build_decision_scorecard(job.metadata.job_id, store) is None


def test_decision_scorecard_explains_approved_final_quality_evidence(tmp_path) -> None:
    scorecard = _run_scorecard_demo(tmp_path, ArticleType.BP)

    assert scorecard is not None
    assert scorecard.status is WorkflowStatus.APPROVED
    assert scorecard.decision_stage is WorkflowStage.FINAL_QA
    assert scorecard.decision_artifact is ArtifactKey.FINAL_QA_REPORT
    assert scorecard.next_action is None
    assert any(signal.label == "Uniqueness threshold" and signal.status_label == "Pass" for signal in scorecard.signals)
    assert sum(signal.status_label == "Ready" for signal in scorecard.signals) == 3


def test_decision_scorecard_explains_landing_page_revision_route(tmp_path) -> None:
    scorecard = _run_scorecard_demo(tmp_path, ArticleType.LP)

    assert scorecard is not None
    assert scorecard.status is WorkflowStatus.NEEDS_REVISION
    assert scorecard.decision_artifact is ArtifactKey.EDITORIAL_QA
    assert scorecard.routing_target is WorkflowStage.WRITING
    assert any(signal.label == "unsupported_factual_claims" and signal.status_label == "Fail" for signal in scorecard.signals)
    assert "70 percent claim" in scorecard.next_action


def test_decision_scorecard_explains_guest_post_human_review_action(tmp_path) -> None:
    scorecard = _run_scorecard_demo(tmp_path, ArticleType.GP)

    assert scorecard is not None
    assert scorecard.status is WorkflowStatus.NEEDS_HUMAN_REVIEW
    assert scorecard.decision_artifact is ArtifactKey.EDITORIAL_QA
    assert scorecard.routing_target is None
    assert any(signal.label == "native_link_placement_review" and signal.status_label == "Fail" for signal in scorecard.signals)
    assert "host publication" in scorecard.next_action
