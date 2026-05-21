"""Uniqueness threshold gate orchestration."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.graph.routing import UNIQUENESS_THRESHOLD, route_after_uniqueness_gate
from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    StatusHistoryEntry,
    UniquenessResult,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


class UniquenessGateResult(BaseModel):
    """Result returned after applying the uniqueness threshold."""

    job_id: str
    uniqueness: UniquenessResult
    threshold: float
    passed: bool
    routing_target: WorkflowStage
    routing_reason: str
    status: WorkflowStatus


class UniquenessGateService:
    """Apply the deterministic uniqueness threshold gate."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
        threshold: float = UNIQUENESS_THRESHOLD,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)
        self.threshold = threshold

    def apply_threshold_gate(self, job_id: str) -> UniquenessGateResult:
        """Route a job based on the persisted uniqueness score."""
        uniqueness = self._load_uniqueness(job_id)
        routing_target = route_after_uniqueness_gate(uniqueness, threshold=self.threshold)
        passed = routing_target is WorkflowStage.LOCALIZATION
        status = WorkflowStatus.RUNNING if passed else WorkflowStatus.NEEDS_REVISION
        routing_reason = self._routing_reason(uniqueness, passed)
        result = UniquenessGateResult(
            job_id=job_id,
            uniqueness=uniqueness,
            threshold=self.threshold,
            passed=passed,
            routing_target=routing_target,
            routing_reason=routing_reason,
            status=status,
        )
        self._persist_state(job_id, result)
        return result

    def _load_uniqueness(self, job_id: str) -> UniquenessResult:
        try:
            payload = self.artifact_store.read_json(job_id, ArtifactKey.UNIQUENESS)
        except FileNotFoundError as error:
            raise ValueError("A uniqueness artifact is required before threshold gating") from error
        return UniquenessResult.model_validate(payload)

    def _routing_reason(self, uniqueness: UniquenessResult, passed: bool) -> str:
        if passed:
            return (
                f"Uniqueness score {uniqueness.score:g} meets the "
                f"{self.threshold:g} percent threshold."
            )
        return (
            f"Uniqueness score {uniqueness.score:g} is below {self.threshold:g}; "
            "revise the English Original."
        )

    def _persist_state(self, job_id: str, result: UniquenessGateResult) -> None:
        state = PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))
        metadata = JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
        next_stage = WorkflowStage.LOCALIZATION if result.passed else WorkflowStage.UNIQUENESS_CHECK
        history_entry = StatusHistoryEntry(
            stage=next_stage,
            status=result.status,
            message=result.routing_reason,
        )

        state.current_stage = next_stage
        state.status = result.status
        state.qa_flags["uniqueness_gate_passed"] = result.passed
        state.uniqueness_score = result.uniqueness.score
        state.uniqueness_threshold = result.threshold
        state.uniqueness_source = result.uniqueness.source
        state.uniqueness_routing_reason = result.routing_reason
        state.revision_notes[WorkflowStage.UNIQUENESS_CHECK] = [] if result.passed else [
            result.routing_reason
        ]
        state.status_history.append(history_entry)

        metadata.current_stage = next_stage
        metadata.status = result.status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
