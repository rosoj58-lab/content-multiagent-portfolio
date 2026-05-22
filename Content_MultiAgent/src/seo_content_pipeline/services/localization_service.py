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
    DEFAULT_FRENCH_GEO,
    DEFAULT_ITALIAN_GEO,
    DEFAULT_SPANISH_GEO,
    build_french_localization_prompt,
    build_italian_localization_prompt,
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


class MultilingualLocalizationResult(BaseModel):
    """Result returned after generating multiple localizations."""

    job_id: str
    status: WorkflowStatus
    localizations: list[LocalizationResult]


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

    def generate_italian_and_french_localizations(
        self,
        job_id: str,
        *,
        italian_geo: str = DEFAULT_ITALIAN_GEO,
        french_geo: str = DEFAULT_FRENCH_GEO,
    ) -> MultilingualLocalizationResult:
        """Generate and persist Italian and French localizations."""
        state = self._load_state(job_id)
        self._ensure_uniqueness_gate_passed(state)
        brief_artifact = SEOBriefArtifact.model_validate(
            self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        )
        english_original = self.artifact_store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL)
        italian_prompt = build_italian_localization_prompt(
            brief=brief_artifact.brief,
            english_original=english_original,
            geo=italian_geo,
        )
        french_prompt = build_french_localization_prompt(
            brief=brief_artifact.brief,
            english_original=english_original,
            geo=french_geo,
        )

        italian_localization = self.llm_runner.generate_text(prompt=italian_prompt)
        french_localization = self.llm_runner.generate_text(prompt=french_prompt)

        italian_path = self.artifact_store.write_text(
            job_id,
            ArtifactKey.LOCALIZATION_IT,
            italian_localization,
        )
        french_path = self.artifact_store.write_text(
            job_id,
            ArtifactKey.LOCALIZATION_FR,
            french_localization,
        )
        self._persist_multiple_localizations_state(
            job_id,
            localizations={
                "it": (ArtifactKey.LOCALIZATION_IT, str(italian_path), italian_geo),
                "fr": (ArtifactKey.LOCALIZATION_FR, str(french_path), french_geo),
            },
        )
        return MultilingualLocalizationResult(
            job_id=job_id,
            status=WorkflowStatus.RUNNING,
            localizations=[
                LocalizationResult(
                    job_id=job_id,
                    language="it",
                    geo=italian_geo,
                    status=WorkflowStatus.RUNNING,
                    localization_path=str(italian_path),
                ),
                LocalizationResult(
                    job_id=job_id,
                    language="fr",
                    geo=french_geo,
                    status=WorkflowStatus.RUNNING,
                    localization_path=str(french_path),
                ),
            ],
        )

    @staticmethod
    def _ensure_uniqueness_gate_passed(state: PipelineState) -> None:
        if (
            state.current_stage is not WorkflowStage.LOCALIZATION
            or state.status is not WorkflowStatus.RUNNING
            or not state.qa_flags.get("english_original_generated", False)
            or not state.qa_flags.get("article_validation_passed", False)
            or not state.qa_flags.get("editorial_qa_passed", False)
            or not state.qa_flags.get("seo_qa_passed", False)
            or not state.qa_flags.get("uniqueness_gate_passed", False)
        ):
            raise ValueError("Localization requires passed English QA and uniqueness gate")

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

    def _persist_multiple_localizations_state(
        self,
        job_id: str,
        *,
        localizations: dict[str, tuple[ArtifactKey, str, str]],
    ) -> None:
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        language_summary = ", ".join(
            f"{language} ({geo})" for language, (_artifact_key, _path, geo) in localizations.items()
        )
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.LOCALIZATION,
            status=WorkflowStatus.RUNNING,
            message=f"Localizations generated for {language_summary}.",
        )

        state.current_stage = WorkflowStage.LOCALIZATION
        state.status = WorkflowStatus.RUNNING
        for language, (artifact_key, path, geo) in localizations.items():
            state.artifact_paths[artifact_key] = path
            state.localization_geos[language] = geo
            state.qa_flags[f"localization_{language}_generated"] = True
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
