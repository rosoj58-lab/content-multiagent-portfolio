"""Optional OpenAI-backed SEO brief generation for an existing new job."""

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import ArtifactKey, PipelineState, WorkflowStage, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.brief_qa_service import BriefQAService
from seo_content_pipeline.services.brief_service import BriefService
from seo_content_pipeline.services.debug_snapshot_service import DebugSnapshotService
from seo_content_pipeline.services.llm_client import LLMClientProtocol, OpenAILLMClient
from seo_content_pipeline.services.llm_runner import LLMRunner
from seo_content_pipeline.services.run_summary_service import RunSummaryService


class LiveBriefResult(BaseModel):
    """Outcome of a single explicitly triggered live brief generation action."""

    job_id: str
    status: WorkflowStatus
    brief_path: str | None = None
    brief_qa_path: str | None = None


class LiveBriefService:
    """Generate only an SEO brief via OpenAI, then apply deterministic brief QA."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
        llm_client: LLMClientProtocol | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)
        self.llm_client = llm_client

    @property
    def is_configured(self) -> bool:
        """Report whether the operator has configured a key for a live request."""
        return bool(self.settings.openai_api_key and self.settings.openai_api_key.strip())

    def generate_live_brief(self, job_id: str) -> LiveBriefResult:
        """Generate and QA one live SEO brief without advancing later stages."""
        state = PipelineState.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.STATE)
        )
        self._ensure_new_job(state)
        if not self.is_configured:
            raise ValueError("Live SEO brief generation requires OPENAI_API_KEY.")

        client = self.llm_client or OpenAILLMClient(
            api_key=self.settings.openai_api_key or "",
            model=self.settings.openai_model,
        )
        brief_result = BriefService(
            settings=self.settings,
            artifact_store=self.artifact_store,
            llm_runner=LLMRunner(client),
        ).generate_brief(job_id)
        if brief_result.status is not WorkflowStatus.RUNNING:
            self._write_run_summary(job_id)
            return LiveBriefResult(job_id=job_id, status=brief_result.status)

        qa_result = BriefQAService(
            settings=self.settings,
            artifact_store=self.artifact_store,
        ).validate_brief(job_id)
        self._write_run_summary(job_id)
        return LiveBriefResult(
            job_id=job_id,
            status=qa_result.status,
            brief_path=str(self.artifact_store.artifact_path(job_id, ArtifactKey.BRIEF)),
            brief_qa_path=str(self.artifact_store.artifact_path(job_id, ArtifactKey.BRIEF_QA)),
        )

    @staticmethod
    def _ensure_new_job(state: PipelineState) -> None:
        if (
            state.current_stage is not WorkflowStage.INPUT_RECEIVED
            or state.status is not WorkflowStatus.RUNNING
        ):
            raise ValueError("Live SEO brief generation requires a newly created job.")

    def _write_run_summary(self, job_id: str) -> None:
        RunSummaryService(settings=self.settings, artifact_store=self.artifact_store).write_summary(job_id)
        DebugSnapshotService(settings=self.settings, artifact_store=self.artifact_store).write_snapshot(job_id)
