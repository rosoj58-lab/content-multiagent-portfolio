"""Deterministic English Original validation orchestration."""

from datetime import UTC, datetime
from typing import Literal

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
from seo_content_pipeline.validators.artifact_validators import (
    validate_heading_structure,
    validate_required_artifacts,
    validate_word_count,
)


ArticleValidationMode = Literal["demo", "full"]


class ArticleValidationResult(BaseModel):
    """Result returned after deterministic article validation."""

    job_id: str
    report: QAReport
    status: WorkflowStatus


class ArticleValidationService:
    """Run deterministic validators for the English Original."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def validate_english_original(
        self,
        job_id: str,
        *,
        mode: ArticleValidationMode = "demo",
    ) -> ArticleValidationResult:
        """Validate the English Original and persist a QA report."""
        article_exists = self.artifact_store.artifact_path(
            job_id,
            ArtifactKey.ENGLISH_ORIGINAL,
        ).exists()
        checks = validate_required_artifacts({"english_original": article_exists})
        if article_exists:
            article = self.artifact_store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL)
            min_words, max_words = self._word_count_range(mode)
            checks.extend(validate_word_count(article, min_words=min_words, max_words=max_words))
            checks.extend(validate_heading_structure(article))

        report = self._build_report(job_id, checks)
        report_path = self.artifact_store.write_json(
            job_id,
            ArtifactKey.ARTICLE_VALIDATION,
            report,
        )
        status = WorkflowStatus.RUNNING if report.passed else WorkflowStatus.NEEDS_REVISION
        self._persist_state(job_id, status, str(report_path))
        return ArticleValidationResult(job_id=job_id, report=report, status=status)

    @staticmethod
    def _word_count_range(mode: ArticleValidationMode) -> tuple[int, int]:
        if mode == "full":
            return 1500, 1600
        return 500, 700

    @staticmethod
    def _build_report(job_id: str, checks: list[ValidationCheck]) -> QAReport:
        passed = all(check.passed for check in checks)
        failed_or_warning = [
            check for check in checks if not check.passed or check.severity == "warning"
        ]
        summary = (
            "Deterministic article validation passed."
            if passed
            else "Deterministic article validation failed: "
            + "; ".join(check.message for check in failed_or_warning)
        )
        recommendations = [check.message for check in failed_or_warning]
        return QAReport(
            job_id=job_id,
            stage=WorkflowStage.WRITING,
            passed=passed,
            checks=checks,
            summary=summary,
            score=sum(check.passed for check in checks) / len(checks) if checks else 0.0,
            recommendations=recommendations,
            routing_target=None if passed else WorkflowStage.WRITING,
        )

    def _persist_state(self, job_id: str, status: WorkflowStatus, report_path: str) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.WRITING,
            status=status,
            message=(
                "Deterministic article validation passed."
                if status is WorkflowStatus.RUNNING
                else "Deterministic article validation failed."
            ),
        )

        state.current_stage = WorkflowStage.WRITING
        state.status = status
        state.artifact_paths[ArtifactKey.ARTICLE_VALIDATION] = report_path
        state.qa_flags["article_validation_passed"] = status is WorkflowStatus.RUNNING
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.WRITING
        metadata.status = status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
