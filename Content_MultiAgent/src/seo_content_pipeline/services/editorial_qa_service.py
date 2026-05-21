"""Editorial QA orchestration."""

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
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.prompts.qa_prompt import build_editorial_qa_prompt
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.llm_runner import LLMRunner


class EditorialQAResult(BaseModel):
    """Result returned after editorial QA."""

    job_id: str
    report: QAReport
    status: WorkflowStatus


class EditorialQAService:
    """Run editorial QA for the English Original article."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
        llm_runner: LLMRunner | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)
        self.llm_runner = llm_runner or LLMRunner()

    def run_editorial_qa(self, job_id: str) -> EditorialQAResult:
        """Run LLM-backed editorial QA and persist the structured report."""
        brief_artifact = SEOBriefArtifact.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        )
        article = self.artifact_store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL)
        article_validation = QAReport.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.ARTICLE_VALIDATION)
        )
        prompt = build_editorial_qa_prompt(
            brief=brief_artifact.brief,
            english_original=article,
            article_validation_summary=article_validation.summary,
        )
        report = self.llm_runner.generate_structured(
            prompt=prompt,
            model_type=QAReport,
            repair_prompt_builder=_build_editorial_qa_repair_prompt,
        )
        report = self._normalize_report(job_id, report)
        report_path = self.artifact_store.write_json(job_id, ArtifactKey.EDITORIAL_QA, report)
        status = WorkflowStatus.RUNNING if report.passed else WorkflowStatus.NEEDS_REVISION
        self._persist_state(job_id, status, str(report_path))
        return EditorialQAResult(job_id=job_id, report=report, status=status)

    @staticmethod
    def _normalize_report(job_id: str, report: QAReport) -> QAReport:
        report.job_id = job_id
        report.stage = WorkflowStage.EDITORIAL_REVIEW
        if report.passed:
            report.routing_target = None
        else:
            report.routing_target = WorkflowStage.WRITING
            if not report.recommendations:
                report.recommendations = [check.message for check in report.checks if not check.passed]
        return report

    def _persist_state(self, job_id: str, status: WorkflowStatus, report_path: str) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.EDITORIAL_REVIEW,
            status=status,
            message=(
                "Editorial QA passed."
                if status is WorkflowStatus.RUNNING
                else "Editorial QA failed. Targeted writing revision is required."
            ),
        )

        state.current_stage = WorkflowStage.EDITORIAL_REVIEW
        state.status = status
        state.artifact_paths[ArtifactKey.EDITORIAL_QA] = report_path
        state.qa_flags["editorial_qa_passed"] = status is WorkflowStatus.RUNNING
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.EDITORIAL_REVIEW
        metadata.status = status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))


def _build_editorial_qa_repair_prompt(
    original_prompt: str,
    invalid_output: str,
    error_message: str,
) -> str:
    return (
        "The previous editorial QA response did not parse as QAReport JSON.\n"
        "Repair it and return only valid JSON. Do not add markdown or commentary.\n\n"
        f"Parse error:\n{error_message}\n\n"
        f"Invalid output:\n{invalid_output}\n\n"
        f"Original task:\n{original_prompt}"
    )
