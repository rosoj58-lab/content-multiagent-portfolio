"""UI-facing job orchestration facade."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    ArticleType,
    JobMetadata,
    PipelineState,
    StatusHistoryEntry,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


class JobInputArtifact(BaseModel):
    """Persisted dry input artifact."""

    job_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stage: WorkflowStage = WorkflowStage.INPUT_RECEIVED
    dry_input: str
    article_type: ArticleType | None = None


class CreateJobResult(BaseModel):
    """Result returned to UI after creating a job shell."""

    metadata: JobMetadata
    artifact_paths: dict[ArtifactKey, str]


class JobService:
    """Facade used by UI code to create and inspect jobs."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def create_job(
        self,
        dry_input: str,
        article_type: ArticleType | None = None,
    ) -> CreateJobResult:
        """Create a durable job shell and persist initial artifacts."""
        normalized_input = dry_input.strip()
        if not normalized_input:
            raise ValueError("dry input must not be empty")

        job_id = self._new_job_id()
        history = [
            StatusHistoryEntry(
                stage=WorkflowStage.INPUT_RECEIVED,
                status=WorkflowStatus.RUNNING,
                message="Job shell created.",
            )
        ]
        metadata = JobMetadata(
            job_id=job_id,
            current_stage=WorkflowStage.INPUT_RECEIVED,
            status=WorkflowStatus.RUNNING,
            article_type=article_type,
            status_history=history,
        )
        input_artifact = JobInputArtifact(
            job_id=job_id,
            dry_input=normalized_input,
            article_type=article_type,
        )
        state = PipelineState(
            job_id=job_id,
            current_stage=WorkflowStage.INPUT_RECEIVED,
            status=WorkflowStatus.RUNNING,
            article_type=article_type,
            status_history=history,
        )

        metadata_path = self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
        input_path = self.artifact_store.write_json(job_id, ArtifactKey.INPUT, input_artifact)
        state_path = self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)

        return CreateJobResult(
            metadata=metadata,
            artifact_paths={
                ArtifactKey.METADATA: str(metadata_path),
                ArtifactKey.INPUT: str(input_path),
                ArtifactKey.STATE: str(state_path),
            },
        )

    @staticmethod
    def _new_job_id() -> str:
        return f"job-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
