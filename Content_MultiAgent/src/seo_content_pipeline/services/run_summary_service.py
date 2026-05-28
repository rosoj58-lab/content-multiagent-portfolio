"""Derived job-level run summary generation."""

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ARTIFACT_REGISTRY,
    ArtifactKey,
    JobMetadata,
    PipelineState,
    RunSummaryArtifact,
    RunSummaryArtifactEntry,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


class RunSummaryService:
    """Build and persist an exportable summary from existing job artifacts."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def write_summary(self, job_id: str) -> RunSummaryArtifact:
        """Persist a derived run summary without changing workflow decisions."""
        state = PipelineState.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.STATE)
        )
        metadata = JobMetadata.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.METADATA)
        )
        summary = self._build_summary(job_id, state, metadata)
        path = self.artifact_store.write_json(job_id, ArtifactKey.RUN_SUMMARY, summary)

        state.artifact_paths[ArtifactKey.RUN_SUMMARY] = str(path)
        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        return summary

    def _build_summary(
        self,
        job_id: str,
        state: PipelineState,
        metadata: JobMetadata,
    ) -> RunSummaryArtifact:
        generated_artifacts = self._generated_artifacts(job_id)
        artifact_counts = self._artifact_counts(generated_artifacts)
        decision_key = self._decision_artifact_key(job_id, state)

        return RunSummaryArtifact(
            job_id=job_id,
            article_type=(state.article_type or metadata.article_type).value
            if state.article_type or metadata.article_type
            else None,
            status=state.status,
            current_stage=state.current_stage,
            decision_artifact=(
                str(self.artifact_store.artifact_path(job_id, decision_key))
                if decision_key is not None
                else None
            ),
            decision_artifact_key=decision_key,
            generated_artifacts=generated_artifacts,
            generated_artifact_count=len(generated_artifacts),
            artifact_counts=artifact_counts,
            final_package_path=self._existing_path(job_id, ArtifactKey.FINAL_PACKAGE_MD),
            final_qa_report_path=self._existing_path(job_id, ArtifactKey.FINAL_QA_REPORT),
            manual_gate_required=state.manual_gate_required,
            revision_attempts=state.revision_attempts,
            revision_notes=state.revision_notes,
            qa_flags=state.qa_flags,
            uniqueness_score=state.uniqueness_score,
            uniqueness_threshold=state.uniqueness_threshold,
            uniqueness_source=state.uniqueness_source,
        )

    def _generated_artifacts(self, job_id: str) -> list[RunSummaryArtifactEntry]:
        artifacts: list[RunSummaryArtifactEntry] = []
        for key, spec in ARTIFACT_REGISTRY.items():
            if key is ArtifactKey.RUN_SUMMARY:
                continue
            path = self.artifact_store.artifact_path(job_id, key)
            if not path.exists():
                continue
            artifacts.append(
                RunSummaryArtifactEntry(
                    key=key,
                    label=spec.ui_label,
                    path=str(path),
                    content_type=spec.content_type,
                    exists=True,
                )
            )
        return artifacts

    @staticmethod
    def _artifact_counts(artifacts: list[RunSummaryArtifactEntry]) -> dict[str, int]:
        counts = {"json": 0, "markdown": 0}
        for artifact in artifacts:
            if artifact.content_type == "application/json":
                counts["json"] += 1
            elif artifact.content_type == "text/markdown":
                counts["markdown"] += 1
        return counts

    def _decision_artifact_key(self, job_id: str, state: PipelineState) -> ArtifactKey | None:
        candidates = {
            WorkflowStage.FINAL_QA: ArtifactKey.FINAL_QA_REPORT,
            WorkflowStage.EDITORIAL_REVIEW: ArtifactKey.EDITORIAL_QA,
            WorkflowStage.SEO_QA: ArtifactKey.SEO_QA,
            WorkflowStage.BRIEF_DRAFTED: ArtifactKey.BRIEF_QA,
            WorkflowStage.WRITING: ArtifactKey.ARTICLE_VALIDATION,
        }
        if state.status is WorkflowStatus.RUNNING:
            return None

        candidate = candidates.get(state.current_stage)
        if candidate is not None and self.artifact_store.artifact_path(job_id, candidate).exists():
            return candidate
        return None

    def _existing_path(self, job_id: str, key: ArtifactKey) -> str | None:
        path = self.artifact_store.artifact_path(job_id, key)
        return str(path) if path.exists() else None
