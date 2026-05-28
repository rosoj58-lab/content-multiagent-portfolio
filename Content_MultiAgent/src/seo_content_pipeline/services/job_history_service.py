"""Read-only access to recent local job artifacts."""

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ARTIFACT_REGISTRY,
    ArtifactKey,
    ArticleType,
    JobMetadata,
    PipelineState,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import CreateJobResult


class RecentJobSummary(BaseModel):
    """Compact UI-facing summary for a persisted local job."""

    job_id: str
    article_type: ArticleType | None
    status: WorkflowStatus
    current_stage: WorkflowStage
    updated_at: datetime
    artifact_count: int
    decision_artifact: str | None = None
    label: str


class JobHistoryService:
    """List and load existing jobs without creating or modifying workflow state."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def list_recent_jobs(self, *, limit: int = 5) -> list[RecentJobSummary]:
        """Return newest valid local jobs from the configured artifact root."""
        if limit <= 0 or not self.artifact_store.artifact_root.exists():
            return []

        summaries = [
            summary
            for job_dir in self.artifact_store.artifact_root.iterdir()
            if job_dir.is_dir()
            for summary in [self._build_summary(job_dir)]
            if summary is not None
        ]
        return sorted(summaries, key=lambda summary: summary.updated_at, reverse=True)[:limit]

    def load_job(self, job_id: str) -> CreateJobResult:
        """Load an existing job into the same result shape returned by job creation."""
        metadata = JobMetadata.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.METADATA)
        )
        PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))
        return CreateJobResult(
            metadata=metadata,
            artifact_paths=self._existing_artifact_paths(job_id),
        )

    def _build_summary(self, job_dir: Path) -> RecentJobSummary | None:
        try:
            metadata = JobMetadata.model_validate(
                self.artifact_store.read_json(job_dir.name, ArtifactKey.METADATA)
            )
            state = PipelineState.model_validate(
                self.artifact_store.read_json(job_dir.name, ArtifactKey.STATE)
            )
        except Exception:
            return None

        artifact_paths = self._existing_artifact_paths(metadata.job_id)
        decision_artifact = self._read_decision_artifact(metadata.job_id)
        updated_at = self._summary_updated_at(job_dir, metadata)
        article_type = state.article_type or metadata.article_type
        label = self._format_label(
            job_id=metadata.job_id,
            article_type=article_type,
            status=state.status,
            current_stage=state.current_stage,
            artifact_count=len(artifact_paths),
            decision_artifact=decision_artifact,
        )
        return RecentJobSummary(
            job_id=metadata.job_id,
            article_type=article_type,
            status=state.status,
            current_stage=state.current_stage,
            updated_at=updated_at,
            artifact_count=len(artifact_paths),
            decision_artifact=decision_artifact,
            label=label,
        )

    def _existing_artifact_paths(self, job_id: str) -> dict[ArtifactKey, str]:
        return {
            key: str(path)
            for key in ARTIFACT_REGISTRY
            if (path := self.artifact_store.artifact_path(job_id, key)).exists()
        }

    def _read_decision_artifact(self, job_id: str) -> str | None:
        try:
            run_summary = self.artifact_store.read_json(job_id, ArtifactKey.RUN_SUMMARY)
        except Exception:
            return None
        decision_artifact = run_summary.get("decision_artifact")
        return decision_artifact if isinstance(decision_artifact, str) else None

    @staticmethod
    def _summary_updated_at(job_dir: Path, metadata: JobMetadata) -> datetime:
        if metadata.updated_at is not None:
            return metadata.updated_at
        return datetime.fromtimestamp(job_dir.stat().st_mtime, tz=UTC)

    @staticmethod
    def _format_label(
        *,
        job_id: str,
        article_type: ArticleType | None,
        status: WorkflowStatus,
        current_stage: WorkflowStage,
        artifact_count: int,
        decision_artifact: str | None,
    ) -> str:
        article_label = article_type.value if article_type is not None else "unknown"
        label = (
            f"{job_id} | {article_label} | {status.value} | "
            f"{current_stage.value} | {artifact_count} artifacts"
        )
        if decision_artifact is None:
            return label
        return f"{label} | decision {Path(decision_artifact).name}"
