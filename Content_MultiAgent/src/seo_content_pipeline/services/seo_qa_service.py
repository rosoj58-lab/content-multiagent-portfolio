"""SEO QA orchestration."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    QAReport,
    SEOBriefArtifact,
    StatusHistoryEntry,
    WorkflowError,
    WorkflowStage,
    WorkflowStatus,
    ValidationCheck,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.validators.seo_validators import validate_seo_article


class SEOQAResult(BaseModel):
    """Result returned after SEO QA."""

    job_id: str
    report: QAReport
    status: WorkflowStatus


class SEOQAService:
    """Run SEO QA and route failures to targeted writing revision."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def run_seo_qa(self, job_id: str) -> SEOQAResult:
        """Run deterministic SEO QA for a job with passed editorial QA."""
        self._ensure_editorial_qa_passed(job_id)
        brief_artifact = SEOBriefArtifact.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        )
        article = self.artifact_store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL)
        article_validation = QAReport.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.ARTICLE_VALIDATION)
        )
        checks = validate_seo_article(
            article=article,
            brief_artifact=brief_artifact,
            article_validation_report=article_validation,
        )
        report = self._build_report(job_id, checks)
        status = self._status_for_report(job_id, report)
        self._apply_routing(report, status)
        report_path = self.artifact_store.write_json(job_id, ArtifactKey.SEO_QA, report)
        self._persist_state(job_id, status, str(report_path), report)
        return SEOQAResult(job_id=job_id, report=report, status=status)

    def _ensure_editorial_qa_passed(self, job_id: str) -> None:
        report = QAReport.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.EDITORIAL_QA))
        if not report.passed:
            raise ValueError("SEO QA requires a passed editorial QA report")

    @staticmethod
    def _build_report(job_id: str, checks: list[ValidationCheck]) -> QAReport:
        passed = all(check.passed for check in checks)
        issues = [check for check in checks if not check.passed or check.severity == "warning"]
        summary = (
            "SEO QA passed."
            if passed
            else "SEO QA failed: " + "; ".join(check.message for check in issues)
        )
        return QAReport(
            job_id=job_id,
            stage=WorkflowStage.SEO_QA,
            passed=passed,
            checks=checks,
            summary=summary,
            score=sum(check.passed for check in checks) / len(checks) if checks else 0.0,
            recommendations=[check.message for check in issues],
            routing_target=None if passed else WorkflowStage.WRITING,
        )

    @staticmethod
    def _apply_routing(report: QAReport, status: WorkflowStatus) -> None:
        if status is WorkflowStatus.NEEDS_HUMAN_REVIEW:
            report.routing_target = None

    def _status_for_report(self, job_id: str, report: QAReport) -> WorkflowStatus:
        if report.passed:
            return WorkflowStatus.RUNNING

        state = self._load_state(job_id)
        attempts = state.revision_attempts.get(WorkflowStage.SEO_QA, 0)
        if attempts >= self.settings.max_revision_attempts:
            return WorkflowStatus.NEEDS_HUMAN_REVIEW
        return WorkflowStatus.NEEDS_REVISION

    def _persist_state(
        self,
        job_id: str,
        status: WorkflowStatus,
        report_path: str,
        report: QAReport,
    ) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        state.current_stage = WorkflowStage.SEO_QA
        state.status = status
        state.artifact_paths[ArtifactKey.SEO_QA] = report_path
        state.qa_flags["seo_qa_passed"] = report.passed and status is WorkflowStatus.RUNNING

        if not report.passed and status is WorkflowStatus.NEEDS_REVISION:
            next_attempt = state.revision_attempts.get(WorkflowStage.SEO_QA, 0) + 1
            state.revision_attempts[WorkflowStage.SEO_QA] = next_attempt
            notes = state.revision_notes.setdefault(WorkflowStage.SEO_QA, [])
            notes.extend(report.recommendations)

        if not report.passed and status is WorkflowStatus.NEEDS_HUMAN_REVIEW:
            state.errors.append(
                WorkflowError(
                    code="seo_revision_limit_reached",
                    message="SEO QA revision limit reached. Human review is required.",
                    node="seo_qa_service",
                    stage=WorkflowStage.SEO_QA,
                    recoverable=True,
                    details={"max_revision_attempts": self.settings.max_revision_attempts},
                )
            )

        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.SEO_QA,
            status=status,
            message=self._history_message(status),
        )
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.SEO_QA
        metadata.status = status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    @staticmethod
    def _history_message(status: WorkflowStatus) -> str:
        if status is WorkflowStatus.RUNNING:
            return "SEO QA passed."
        if status is WorkflowStatus.NEEDS_HUMAN_REVIEW:
            return "SEO QA revision limit reached. Human review is required."
        return "SEO QA failed. Targeted writing revision is required."

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
