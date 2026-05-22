"""Demo observability view tests."""

import ast
from pathlib import Path

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import (
    ArtifactKey,
    PipelineState,
    QAReport,
    StatusHistoryEntry,
    ValidationCheck,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.stage_view_builder import build_pipeline_stage_views
from seo_content_pipeline.ui.artifact_panel import build_artifact_previews
from seo_content_pipeline.ui.error_presenter import build_controlled_error
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
