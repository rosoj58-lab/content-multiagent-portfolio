"""Uniqueness threshold gate service tests."""

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, PipelineState, UniquenessResult, WorkflowStage, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.uniqueness_gate_service import UniquenessGateService


def _prepare_job_with_uniqueness_score(tmp_path, score: float) -> tuple[str, UniquenessGateService, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Create SEO content that has a recorded uniqueness score."
    )
    state = PipelineState.model_validate(store.read_json(job.metadata.job_id, ArtifactKey.STATE))
    state.current_stage = WorkflowStage.UNIQUENESS_CHECK
    state.status = WorkflowStatus.RUNNING
    state.selected_uniqueness_provider = "manual"
    state.qa_flags["uniqueness_score_recorded"] = True
    store.write_json(job.metadata.job_id, ArtifactKey.STATE, state)
    store.write_json(
        job.metadata.job_id,
        ArtifactKey.UNIQUENESS,
        UniquenessResult(
            job_id=job.metadata.job_id,
            score=score,
            source="manual",
            provider_metadata={"provider": "manual"},
        ),
    )
    return job.metadata.job_id, UniquenessGateService(settings=settings, artifact_store=store), store


@pytest.mark.parametrize("score", [90, 100])
def test_uniqueness_gate_routes_passing_scores_to_localization(tmp_path, score) -> None:
    job_id, service, store = _prepare_job_with_uniqueness_score(tmp_path, score)

    result = service.apply_threshold_gate(job_id)

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.passed is True
    assert result.routing_target is WorkflowStage.LOCALIZATION
    assert result.status is WorkflowStatus.RUNNING
    assert state["current_stage"] == WorkflowStage.LOCALIZATION.value
    assert state["status"] == WorkflowStatus.RUNNING.value
    assert state["qa_flags"]["uniqueness_gate_passed"] is True
    assert state["uniqueness_threshold"] == 90.0
    assert state["uniqueness_score"] == float(score)
    assert state["uniqueness_source"] == "manual"
    assert "meets" in state["uniqueness_routing_reason"]
    assert metadata["current_stage"] == WorkflowStage.LOCALIZATION.value


def test_uniqueness_gate_routes_low_score_to_revision(tmp_path) -> None:
    job_id, service, store = _prepare_job_with_uniqueness_score(tmp_path, 89.9)

    result = service.apply_threshold_gate(job_id)

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.passed is False
    assert result.routing_target is WorkflowStage.WRITING
    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert state["current_stage"] == WorkflowStage.UNIQUENESS_CHECK.value
    assert state["status"] == WorkflowStatus.NEEDS_REVISION.value
    assert state["qa_flags"]["uniqueness_gate_passed"] is False
    assert state["uniqueness_score"] == 89.9
    assert state["uniqueness_threshold"] == 90.0
    assert state["revision_notes"]["uniqueness_check"]
    assert "below 90" in state["revision_notes"]["uniqueness_check"][0]
    assert metadata["status"] == WorkflowStatus.NEEDS_REVISION.value


def test_uniqueness_gate_requires_uniqueness_artifact(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Create SEO content without uniqueness yet."
    )
    service = UniquenessGateService(settings=settings, artifact_store=store)

    with pytest.raises(ValueError, match="uniqueness"):
        service.apply_threshold_gate(job.metadata.job_id)
