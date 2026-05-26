"""English Original writer stage orchestration."""

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
from seo_content_pipeline.prompts.writer import WritingMode, build_writer_prompt
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.llm_runner import LLMRunner


class WriterResult(BaseModel):
    """Result returned after English Original generation."""

    job_id: str
    status: WorkflowStatus
    article_path: str


class WriterService:
    """Generate the English Original from an approved SEO brief."""

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

    def generate_english_original(
        self,
        job_id: str,
        *,
        mode: WritingMode = "demo",
    ) -> WriterResult:
        """Generate and persist the English Original Markdown article."""
        state = self._load_state(job_id)
        self._ensure_brief_approved(state)
        brief_artifact = SEOBriefArtifact.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        )
        prompt = build_writer_prompt(brief=brief_artifact.brief, mode=mode)
        article = self.llm_runner.generate_text(prompt=prompt)
        article_path = self.artifact_store.write_text(
            job_id,
            ArtifactKey.ENGLISH_ORIGINAL,
            article,
        )
        self._persist_writing_state(job_id, str(article_path))
        return WriterResult(
            job_id=job_id,
            status=WorkflowStatus.RUNNING,
            article_path=str(article_path),
        )

    def revise_english_original(
        self,
        job_id: str,
        *,
        mode: WritingMode = "demo",
    ) -> WriterResult:
        """Generate a targeted article revision after routed editorial QA."""
        state = self._load_state(job_id)
        self._ensure_editorial_revision_routed(state, job_id)
        brief_artifact = SEOBriefArtifact.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        )
        prompt = (
            build_writer_prompt(brief=brief_artifact.brief, mode=mode)
            + "\nRevise the English Original using the routed editorial recommendation."
        )
        article = self.llm_runner.generate_text(prompt=prompt)
        article_path = self.artifact_store.write_text(
            job_id,
            ArtifactKey.ENGLISH_ORIGINAL,
            article,
        )
        self._persist_writing_state(job_id, str(article_path), revised=True)
        return WriterResult(
            job_id=job_id,
            status=WorkflowStatus.RUNNING,
            article_path=str(article_path),
        )

    @staticmethod
    def _ensure_brief_approved(state: PipelineState) -> None:
        if (
            state.current_stage is not WorkflowStage.BRIEF_APPROVED
            or state.status is not WorkflowStatus.APPROVED
            or not state.qa_flags.get("brief_approved", False)
        ):
            raise ValueError("writing requires an approved brief")

    def _ensure_editorial_revision_routed(self, state: PipelineState, job_id: str) -> None:
        report = QAReport.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.EDITORIAL_QA)
        )
        if (
            state.current_stage is not WorkflowStage.EDITORIAL_REVIEW
            or state.status is not WorkflowStatus.NEEDS_REVISION
            or report.passed
            or report.routing_target is not WorkflowStage.WRITING
        ):
            raise ValueError("targeted writing revision requires routed editorial QA")

    def _persist_writing_state(
        self,
        job_id: str,
        article_path: str,
        *,
        revised: bool = False,
    ) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.WRITING,
            status=WorkflowStatus.RUNNING,
            message=(
                "English Original revised after editorial QA."
                if revised
                else "English Original generated."
            ),
        )

        state.current_stage = WorkflowStage.WRITING
        state.status = WorkflowStatus.RUNNING
        state.artifact_paths[ArtifactKey.ENGLISH_ORIGINAL] = article_path
        state.qa_flags["english_original_generated"] = True
        if revised:
            attempts = state.revision_attempts.get(WorkflowStage.EDITORIAL_REVIEW, 0)
            state.revision_attempts[WorkflowStage.EDITORIAL_REVIEW] = attempts + 1
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.WRITING
        metadata.status = WorkflowStatus.RUNNING
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
