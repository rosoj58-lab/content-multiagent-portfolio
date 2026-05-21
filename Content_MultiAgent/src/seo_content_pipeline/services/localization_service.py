"""Localization stage orchestration."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    SEOBriefArtifact,
    StatusHistoryEntry,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.prompts.localization import (
    DEFAULT_SPANISH_GEO,
    build_spanish_localization_prompt,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.llm_runner import LLMRunner


class LocalizationResult(BaseModel):
    """Result returned after localization generation."""

    job_id: str
    language: str
    geo: str
    status: WorkflowStatus
    localization_path: str


class LocalizationService:
    """Generate localized Markdown artifacts after uniqueness approval."""

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

    def generate_spanish_localization(
        self,
        job_id: str,
        *,
        geo: str = DEFAULT_SPANISH_GEO,
    ) -> LocalizationResult:
        """Generate and persist the Spanish localization."""
        state = self._load_state(job_id)
        self._ensure_uniqueness_gate_passed(state)
        brief_artifact = SEOBriefArtifact.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        )
        english_original = self.artifact_store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL)
        prompt = build_spanish_localization_prompt(
            brief=brief_artifact.brief,
            english_original=english_original,
            geo=geo,
        )
        localization = self.llm_runner.generate_text(prompt=prompt)
        localization_path = self.artifact_store.write_text(
            job_id,
            ArtifactKey.LOCALIZATION_ES,
            localization,
        )
        self._persist_localization_state(job_id, str(localization_path), geo)
        return LocalizationResult(
            job_id=job_id,
            language="es",
            geo=geo,
            status=WorkflowStatus.RUNNING,
            localization_path=str(localization_path),
        )

    @staticmethod
    def _ensure_uniqueness_gate_passed(state: PipelineState) -> None:
        if (
            state.current_stage is not WorkflowStage.LOCALIZATION
            or state.status is not WorkflowStatus.RUNNING
            or not state.qa_flags.get("uniqueness_gate_passed", False)
        ):
            raise ValueError("Spanish localization requires a passed uniqueness gate")

    def _persist_localization_state(self, job_id: str, localization_path: str, geo: str) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.LOCALIZATION,
            status=WorkflowStatus.RUNNING,
            message=f"Spanish localization generated for {geo}.",
        )

        state.current_stage = WorkflowStage.LOCALIZATION
        state.status = WorkflowStatus.RUNNING
        state.artifact_paths[ArtifactKey.LOCALIZATION_ES] = localization_path
        state.localization_geos["es"] = geo
        state.qa_flags["localization_es_generated"] = True
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.LOCALIZATION
        metadata.status = WorkflowStatus.RUNNING
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
