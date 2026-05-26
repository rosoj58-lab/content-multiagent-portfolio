"""Core model and artifact registry tests."""

from seo_content_pipeline.models import (
    ARTIFACT_REGISTRY,
    ArtifactKey,
    JobMetadata,
    PipelineState,
    QAReport,
    RevisionHistoryArtifact,
    RevisionHistoryEntry,
    StageView,
    ValidationCheck,
    WorkflowError,
    WorkflowStage,
    WorkflowStatus,
)


def test_workflow_stage_and_status_are_separate_contracts() -> None:
    assert WorkflowStage.WRITING.value == "writing"
    assert WorkflowStatus.RUNNING.value == "running"
    assert WorkflowStage.WRITING.value != WorkflowStatus.RUNNING.value


def test_artifact_registry_covers_every_artifact_key() -> None:
    assert set(ARTIFACT_REGISTRY) == set(ArtifactKey)


def test_artifact_registry_includes_job_shell_artifacts_for_job_service() -> None:
    assert ARTIFACT_REGISTRY[ArtifactKey.METADATA].filename == "metadata.json"
    assert ARTIFACT_REGISTRY[ArtifactKey.INPUT].filename == "input.json"
    assert ARTIFACT_REGISTRY[ArtifactKey.STATE].filename == "state.json"


def test_artifact_registry_includes_brief_qa_report() -> None:
    assert ARTIFACT_REGISTRY[ArtifactKey.BRIEF_QA].filename == "brief_qa.json"
    assert ARTIFACT_REGISTRY[ArtifactKey.BRIEF_QA].content_type == "application/json"


def test_artifact_registry_includes_article_validation_report() -> None:
    assert ARTIFACT_REGISTRY[ArtifactKey.ARTICLE_VALIDATION].filename == "article_validation.json"
    assert ARTIFACT_REGISTRY[ArtifactKey.ARTICLE_VALIDATION].content_type == "application/json"


def test_artifact_registry_includes_revision_history_report() -> None:
    assert ARTIFACT_REGISTRY[ArtifactKey.REVISION_HISTORY].filename == "revision_history.json"
    assert ARTIFACT_REGISTRY[ArtifactKey.REVISION_HISTORY].content_type == "application/json"


def test_artifact_registry_has_unique_filenames_and_required_metadata() -> None:
    filenames = [spec.filename for spec in ARTIFACT_REGISTRY.values()]

    assert len(filenames) == len(set(filenames))
    for key, spec in ARTIFACT_REGISTRY.items():
        assert spec.key is key
        assert spec.filename
        assert spec.content_type in {"application/json", "text/markdown"}
        assert spec.ui_label
        assert spec.description


def test_artifact_registry_filename_extensions_match_content_type() -> None:
    for spec in ARTIFACT_REGISTRY.values():
        if spec.content_type == "application/json":
            assert spec.filename.endswith(".json")
        elif spec.content_type == "text/markdown":
            assert spec.filename.endswith(".md")


def test_model_mutable_defaults_are_not_shared() -> None:
    first_check = ValidationCheck(name="word_count", passed=True, severity="info", message="ok")
    second_check = ValidationCheck(name="keyword", passed=True, severity="info", message="ok")
    first_check.metadata["count"] = 1

    first_report = QAReport(
        job_id="job-1",
        stage=WorkflowStage.SEO_QA,
        passed=True,
        checks=[first_check],
        summary="ok",
    )
    second_report = QAReport(
        job_id="job-2",
        stage=WorkflowStage.SEO_QA,
        passed=True,
        checks=[second_check],
        summary="ok",
    )
    first_report.recommendations.append("keep keyword density natural")

    first_history = RevisionHistoryArtifact(
        job_id="job-1",
        revisions=[
            RevisionHistoryEntry(
                attempt=1,
                source_stage=WorkflowStage.EDITORIAL_REVIEW,
                initial_status=WorkflowStatus.NEEDS_REVISION,
                failed_report=first_report,
                action="Remove unsupported claim.",
            )
        ],
    )
    second_history = RevisionHistoryArtifact(job_id="job-2")
    first_history.revisions[0].action = "Provide supporting evidence."

    first_view = StageView(
        stage=WorkflowStage.SEO_QA,
        status=WorkflowStatus.APPROVED,
        label="SEO QA",
        description="Checks SEO quality.",
    )
    second_view = StageView(
        stage=WorkflowStage.SEO_QA,
        status=WorkflowStatus.APPROVED,
        label="SEO QA",
        description="Checks SEO quality.",
    )
    first_view.available_actions.append("continue")

    first_job = JobMetadata(job_id="job-1", current_stage=WorkflowStage.INPUT_RECEIVED)
    second_job = JobMetadata(job_id="job-2", current_stage=WorkflowStage.INPUT_RECEIVED)
    first_job.status_history.append(
        {
            "stage": WorkflowStage.INPUT_RECEIVED,
            "status": WorkflowStatus.RUNNING,
            "message": "started",
        }
    )

    first_state = PipelineState(
        job_id="job-1",
        current_stage=WorkflowStage.BRIEF_DRAFTED,
        status=WorkflowStatus.NEEDS_REVISION,
    )
    second_state = PipelineState(
        job_id="job-2",
        current_stage=WorkflowStage.BRIEF_DRAFTED,
        status=WorkflowStatus.NEEDS_REVISION,
    )
    first_state.revision_notes[WorkflowStage.BRIEF_DRAFTED] = ["make audience specific"]

    error = WorkflowError(
        code="parse_failed",
        message="Could not parse LLM output.",
        node="brief_node",
        stage=WorkflowStage.BRIEF_DRAFTED,
        recoverable=True,
    )
    error.details["attempt"] = 1
    second_error = WorkflowError(
        code="parse_failed",
        message="Could not parse LLM output.",
        node="brief_node",
        stage=WorkflowStage.BRIEF_DRAFTED,
        recoverable=True,
    )

    assert second_check.metadata == {}
    assert second_report.recommendations == []
    assert second_history.revisions == []
    assert second_view.available_actions == []
    assert second_job.status_history == []
    assert second_state.revision_notes == {}
    assert second_error.details == {}
