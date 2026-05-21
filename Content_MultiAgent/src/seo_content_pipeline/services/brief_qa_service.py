"""SEO brief QA orchestration."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    QAReport,
    StatusHistoryEntry,
    ValidationCheck,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.validators.artifact_validators import validate_required_brief_fields


class BriefQAResult(BaseModel):
    """Result returned after deterministic brief QA."""

    job_id: str
    report: QAReport
    status: WorkflowStatus


class BriefQAService:
    """Validate persisted SEO briefs and update job state."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def validate_brief(self, job_id: str) -> BriefQAResult:
        """Run deterministic brief QA for an existing job."""
        brief_artifact = self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        brief_payload = self._extract_brief_payload(brief_artifact)
        checks = validate_required_brief_fields(brief_payload)
        report = self._build_report(job_id, checks)
        report_path = self.artifact_store.write_json(job_id, ArtifactKey.BRIEF_QA, report)
        status = WorkflowStatus.WAITING_FOR_HUMAN if report.passed else WorkflowStatus.NEEDS_REVISION
        self._persist_state(job_id, status, str(report_path))
        return BriefQAResult(job_id=job_id, report=report, status=status)

    @staticmethod
    def _extract_brief_payload(brief_artifact: dict[str, Any]) -> dict[str, Any]:
        brief_payload = brief_artifact.get("brief", brief_artifact)
        if isinstance(brief_payload, dict):
            return brief_payload
        return {}

    @staticmethod
    def _build_report(job_id: str, checks: list[ValidationCheck]) -> QAReport:
        passed = all(check.passed for check in checks)
        missing_fields = [
            str(check.metadata["field"])
            for check in checks
            if not check.passed and "field" in check.metadata
        ]
        score = sum(check.passed for check in checks) / len(checks) if checks else 0.0
        if passed:
            summary = "Brief QA passed. Brief is ready for manual approval."
            recommendations = ["Review and approve the brief, or request a targeted revision."]
            routing_target = None
        else:
            field_list = ", ".join(missing_fields)
            summary = f"Brief QA failed. Fix these fields before writing: {field_list}."
            recommendations = [check.message for check in checks if not check.passed]
            routing_target = WorkflowStage.BRIEF_DRAFTED

        return QAReport(
            job_id=job_id,
            stage=WorkflowStage.BRIEF_DRAFTED,
            passed=passed,
            checks=checks,
            summary=summary,
            score=score,
            recommendations=recommendations,
            routing_target=routing_target,
        )

    def _persist_state(self, job_id: str, status: WorkflowStatus, report_path: str) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        manual_gate_required = status is WorkflowStatus.WAITING_FOR_HUMAN
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=status,
            message=(
                "Brief QA passed. Waiting for manual approval."
                if manual_gate_required
                else "Brief QA failed. Revision is required."
            ),
        )

        state.current_stage = WorkflowStage.BRIEF_DRAFTED
        state.status = status
        state.manual_gate_required = manual_gate_required
        state.artifact_paths[ArtifactKey.BRIEF_QA] = report_path
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.BRIEF_DRAFTED
        metadata.status = status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
