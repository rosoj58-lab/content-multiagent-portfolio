"""Manual approval and revision handling for SEO briefs."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    QAReport,
    StatusHistoryEntry,
    WorkflowError,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


class BriefGateActionResult(BaseModel):
    """Result returned after a manual brief gate action."""

    job_id: str
    status: WorkflowStatus
    current_stage: WorkflowStage
    revision_attempt: int | None = None


class BriefApprovalService:
    """Handle manual approval and revision requests for generated briefs."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def approve_brief(self, job_id: str) -> BriefGateActionResult:
        """Approve a QA-passed brief and enable the writing stage."""
        self._ensure_brief_exists(job_id)
        self._ensure_qa_passed(job_id)
        state = self._load_state(job_id)
        if not state.manual_gate_required or state.status is not WorkflowStatus.WAITING_FOR_HUMAN:
            raise ValueError("brief approval requires an active manual gate")

        metadata = self._load_metadata(job_id)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.BRIEF_APPROVED,
            status=WorkflowStatus.APPROVED,
            message="SEO brief approved. Writing stage enabled.",
        )

        state.current_stage = WorkflowStage.BRIEF_APPROVED
        state.status = WorkflowStatus.APPROVED
        state.manual_gate_required = False
        state.qa_flags["brief_approved"] = True
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.BRIEF_APPROVED
        metadata.status = WorkflowStatus.APPROVED
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
        return BriefGateActionResult(
            job_id=job_id,
            status=WorkflowStatus.APPROVED,
            current_stage=WorkflowStage.BRIEF_APPROVED,
        )

    def request_revision(self, job_id: str, notes: str) -> BriefGateActionResult:
        """Route the job back to brief generation with operator notes."""
        self._ensure_brief_exists(job_id)
        self._ensure_qa_exists(job_id)
        revision_notes = notes.strip()
        if not revision_notes:
            raise ValueError("revision notes must not be empty")

        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        previous_attempts = state.revision_attempts.get(WorkflowStage.BRIEF_DRAFTED, 0)
        if previous_attempts >= self.settings.max_revision_attempts:
            self._persist_revision_limit_state(job_id, state, metadata, revision_notes)
            return BriefGateActionResult(
                job_id=job_id,
                status=WorkflowStatus.NEEDS_HUMAN_REVIEW,
                current_stage=WorkflowStage.BRIEF_DRAFTED,
                revision_attempt=previous_attempts,
            )

        next_attempt = previous_attempts + 1
        notes_for_stage = state.revision_notes.setdefault(WorkflowStage.BRIEF_DRAFTED, [])
        notes_for_stage.append(revision_notes)
        state.revision_attempts[WorkflowStage.BRIEF_DRAFTED] = next_attempt
        state.current_stage = WorkflowStage.BRIEF_DRAFTED
        state.status = WorkflowStatus.NEEDS_REVISION
        state.manual_gate_required = False
        state.qa_flags["brief_revision_requested"] = True
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=WorkflowStatus.NEEDS_REVISION,
            message="Brief revision requested. Route back to SEO brief generation.",
        )
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.BRIEF_DRAFTED
        metadata.status = WorkflowStatus.NEEDS_REVISION
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
        return BriefGateActionResult(
            job_id=job_id,
            status=WorkflowStatus.NEEDS_REVISION,
            current_stage=WorkflowStage.BRIEF_DRAFTED,
            revision_attempt=next_attempt,
        )

    def _persist_revision_limit_state(
        self,
        job_id: str,
        state: PipelineState,
        metadata: JobMetadata,
        revision_notes: str,
    ) -> None:
        workflow_error = WorkflowError(
            code="brief_revision_limit_reached",
            message="Brief revision limit reached. Human review is required.",
            node="brief_approval_service",
            stage=WorkflowStage.BRIEF_DRAFTED,
            recoverable=True,
            details={
                "max_revision_attempts": self.settings.max_revision_attempts,
                "latest_notes": revision_notes,
            },
        )
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=WorkflowStatus.NEEDS_HUMAN_REVIEW,
            message="Brief revision limit reached. Human review is required.",
        )
        state.current_stage = WorkflowStage.BRIEF_DRAFTED
        state.status = WorkflowStatus.NEEDS_HUMAN_REVIEW
        state.manual_gate_required = False
        state.errors.append(workflow_error)
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.BRIEF_DRAFTED
        metadata.status = WorkflowStatus.NEEDS_HUMAN_REVIEW
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _ensure_brief_exists(self, job_id: str) -> None:
        self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)

    def _ensure_qa_exists(self, job_id: str) -> QAReport:
        return QAReport.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.BRIEF_QA))

    def _ensure_qa_passed(self, job_id: str) -> None:
        report = self._ensure_qa_exists(job_id)
        if not report.passed:
            raise ValueError("brief approval requires a passed brief QA report")

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
