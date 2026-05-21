"""SEO brief generation orchestration."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    ArticleType,
    JobMetadata,
    PipelineState,
    SEOBrief,
    SEOBriefArtifact,
    StatusHistoryEntry,
    WorkflowError,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.prompts.brief import build_brief_prompt, build_brief_repair_prompt
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.llm_runner import LLMOutputParsingError, LLMRunner


class BriefGenerationResult(BaseModel):
    """Result of a brief generation stage run."""

    job_id: str
    status: WorkflowStatus
    brief: SEOBriefArtifact | None = None
    error: WorkflowError | None = None


class BriefService:
    """Generate SEO brief artifacts from stored dry input."""

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

    def generate_brief(self, job_id: str) -> BriefGenerationResult:
        """Run brief generation for an existing job."""
        input_artifact = self.artifact_store.read_json(job_id, ArtifactKey.INPUT)
        article_type = self._article_type_from_input(input_artifact)
        dry_input = self._dry_input_from_input(input_artifact)

        prompt = build_brief_prompt(dry_input=dry_input, article_type=article_type)
        try:
            brief = self.llm_runner.generate_structured(
                prompt=prompt,
                model_type=SEOBrief,
                repair_prompt_builder=build_brief_repair_prompt,
            )
        except LLMOutputParsingError as error:
            workflow_error = self._persist_human_review_state(job_id, error)
            return BriefGenerationResult(
                job_id=job_id,
                status=WorkflowStatus.NEEDS_HUMAN_REVIEW,
                error=workflow_error,
            )

        brief_artifact = SEOBriefArtifact(job_id=job_id, article_type=article_type, brief=brief)
        brief_path = self.artifact_store.write_json(job_id, ArtifactKey.BRIEF, brief_artifact)
        self._persist_success_state(job_id, str(brief_path))

        return BriefGenerationResult(
            job_id=job_id,
            status=WorkflowStatus.RUNNING,
            brief=brief_artifact,
        )

    @staticmethod
    def _article_type_from_input(input_artifact: dict[str, object]) -> ArticleType:
        raw_article_type = input_artifact.get("article_type")
        if raw_article_type is None:
            raise ValueError("input artifact must include article_type")
        return ArticleType(str(raw_article_type))

    @staticmethod
    def _dry_input_from_input(input_artifact: dict[str, object]) -> str:
        raw_dry_input = input_artifact.get("dry_input")
        if not isinstance(raw_dry_input, str) or not raw_dry_input.strip():
            raise ValueError("input artifact must include non-empty dry_input")
        return raw_dry_input.strip()

    def _persist_success_state(self, job_id: str, brief_path: str) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=WorkflowStatus.RUNNING,
            message="SEO brief generated.",
        )

        state.current_stage = WorkflowStage.BRIEF_DRAFTED
        state.status = WorkflowStatus.RUNNING
        state.artifact_paths[ArtifactKey.BRIEF] = brief_path
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.BRIEF_DRAFTED
        metadata.status = WorkflowStatus.RUNNING
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _persist_human_review_state(
        self,
        job_id: str,
        parsing_error: LLMOutputParsingError,
    ) -> WorkflowError:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        workflow_error = WorkflowError(
            code="brief_parse_failed",
            message="SEO brief output could not be parsed after one repair attempt.",
            node="brief_node",
            stage=WorkflowStage.BRIEF_DRAFTED,
            recoverable=True,
            details={
                "attempts": parsing_error.attempts,
                "last_error": parsing_error.last_error,
            },
        )
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=WorkflowStatus.NEEDS_HUMAN_REVIEW,
            message="SEO brief generation needs human review.",
        )

        state.current_stage = WorkflowStage.BRIEF_DRAFTED
        state.status = WorkflowStatus.NEEDS_HUMAN_REVIEW
        state.errors.append(workflow_error)
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.BRIEF_DRAFTED
        metadata.status = WorkflowStatus.NEEDS_HUMAN_REVIEW
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
        return workflow_error

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
