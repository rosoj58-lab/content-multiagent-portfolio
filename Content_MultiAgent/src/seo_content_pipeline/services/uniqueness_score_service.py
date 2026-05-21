"""Manual uniqueness score orchestration."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
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
from seo_content_pipeline.validators.artifact_validators import validate_uniqueness_score


class ManualUniquenessScoreResult(BaseModel):
    """Result returned after recording a manual uniqueness score."""

    job_id: str
    uniqueness: UniquenessResult
    status: WorkflowStatus


class UniquenessScoreService:
    """Record operator-supplied uniqueness scores."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def record_manual_score(self, job_id: str, score: object) -> ManualUniquenessScoreResult:
        """Validate and persist a manually entered uniqueness score."""
        normalized_score = self._normalize_score(score)
        self._ensure_manual_provider_selected(job_id)
        uniqueness = UniquenessResult(
            job_id=job_id,
            score=normalized_score,
            source="manual",
            provider_metadata={
                "provider": "manual",
                "entered_by": "operator",
                "score_origin": "external_checker",
            },
        )
        report_path = self.artifact_store.write_json(job_id, ArtifactKey.UNIQUENESS, uniqueness)
        status = WorkflowStatus.RUNNING
        self._persist_state(job_id, str(report_path), status)
        return ManualUniquenessScoreResult(job_id=job_id, uniqueness=uniqueness, status=status)

    @staticmethod
    def _normalize_score(score: object) -> float:
        check = validate_uniqueness_score(score)[0]
        if not check.passed:
            raise ValueError(check.message)
        return float(score)

    def _ensure_manual_provider_selected(self, job_id: str) -> None:
        state = PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))
        if state.selected_uniqueness_provider != "manual":
            raise ValueError("Manual uniqueness score requires selected manual provider")

    def _persist_state(self, job_id: str, report_path: str, status: WorkflowStatus) -> None:
        state = PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))
        metadata = JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.UNIQUENESS_CHECK,
            status=status,
            message="Manual uniqueness score recorded.",
        )

        state.current_stage = WorkflowStage.UNIQUENESS_CHECK
        state.status = status
        state.artifact_paths[ArtifactKey.UNIQUENESS] = report_path
        state.manual_gate_required = False
        state.qa_flags["uniqueness_score_recorded"] = True
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.UNIQUENESS_CHECK
        metadata.status = status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
