"""Derived job debug snapshot generation."""

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ARTIFACT_REGISTRY,
    ArtifactKey,
    DebugSnapshotArtifact,
    JobMetadata,
    PipelineState,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


class DebugSnapshotService:
    """Build and persist a compact diagnostic snapshot from existing job artifacts."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def write_snapshot(self, job_id: str) -> DebugSnapshotArtifact:
        """Persist a derived debug snapshot without changing workflow decisions."""
        state = PipelineState.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.STATE)
        )
        metadata = JobMetadata.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.METADATA)
        )
        snapshot = self._build_snapshot(job_id, state, metadata)
        path = self.artifact_store.write_json(job_id, ArtifactKey.DEBUG_SNAPSHOT, snapshot)

        state.artifact_paths[ArtifactKey.DEBUG_SNAPSHOT] = str(path)
        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        return snapshot

    def _build_snapshot(
        self,
        job_id: str,
        state: PipelineState,
        metadata: JobMetadata,
    ) -> DebugSnapshotArtifact:
        present_artifacts, missing_artifacts, key_paths = self._artifact_availability(job_id)
        critical_missing_artifacts = self._critical_missing_artifacts(state)
        return DebugSnapshotArtifact(
            job_id=job_id,
            article_type=(state.article_type or metadata.article_type).value
            if state.article_type or metadata.article_type
            else None,
            status=state.status,
            current_stage=state.current_stage,
            manual_gate_required=state.manual_gate_required,
            workflow_error_count=len(state.errors),
            errors=state.errors,
            revision_attempts=state.revision_attempts,
            revision_notes=state.revision_notes,
            artifact_counts={
                "present": len(present_artifacts),
                "missing": len(missing_artifacts),
                "critical_missing": len(critical_missing_artifacts),
            },
            present_artifacts=present_artifacts,
            missing_artifacts=missing_artifacts,
            critical_missing_artifacts=critical_missing_artifacts,
            key_paths=key_paths,
        )

    def _artifact_availability(
        self,
        job_id: str,
    ) -> tuple[list[ArtifactKey], list[ArtifactKey], dict[ArtifactKey, str]]:
        present_artifacts: list[ArtifactKey] = []
        missing_artifacts: list[ArtifactKey] = []
        key_paths: dict[ArtifactKey, str] = {}
        for key in ARTIFACT_REGISTRY:
            if key is ArtifactKey.DEBUG_SNAPSHOT:
                continue
            path = self.artifact_store.artifact_path(job_id, key)
            if path.exists():
                present_artifacts.append(key)
                key_paths[key] = str(path)
            else:
                missing_artifacts.append(key)
        return present_artifacts, missing_artifacts, key_paths

    def _critical_missing_artifacts(self, state: PipelineState) -> list[ArtifactKey]:
        critical_missing: list[ArtifactKey] = []
        for key in state.artifact_paths:
            if key is ArtifactKey.DEBUG_SNAPSHOT:
                continue
            if not self.artifact_store.artifact_path(state.job_id, key).exists():
                critical_missing.append(key)
        return critical_missing
