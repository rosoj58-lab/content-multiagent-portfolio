"""Uniqueness provider selection orchestration."""

from datetime import UTC, datetime

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, UniquenessProviderName, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    PipelineState,
    StatusHistoryEntry,
    UniquenessProviderOption,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.providers.base import UniquenessProvider
from seo_content_pipeline.providers.copyleaks_uniqueness import CopyleaksUniquenessProvider
from seo_content_pipeline.providers.manual_uniqueness import ManualUniquenessProvider
from seo_content_pipeline.providers.mock_uniqueness import MockUniquenessProvider
from seo_content_pipeline.services.artifact_store import ArtifactStore


class UniquenessProviderSelectionResult(BaseModel):
    """Result returned after selecting a uniqueness provider."""

    job_id: str
    selected_provider: UniquenessProviderName
    provider_options: list[UniquenessProviderOption]
    status: WorkflowStatus


class UniquenessProviderService:
    """List and persist explicit uniqueness provider selections."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
        providers: tuple[UniquenessProvider, ...] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)
        self.providers = providers or (
            ManualUniquenessProvider(),
            MockUniquenessProvider(),
            CopyleaksUniquenessProvider(),
        )

    def list_provider_options(self) -> list[UniquenessProviderOption]:
        """Return provider availability without triggering external checks."""
        return [provider.get_option(self.settings) for provider in self.providers]

    def select_provider(
        self,
        job_id: str,
        provider_name: UniquenessProviderName,
    ) -> UniquenessProviderSelectionResult:
        """Persist an explicit provider selection for the uniqueness stage."""
        provider_options = self.list_provider_options()
        selected_option = self._find_option(provider_options, provider_name)
        if selected_option is None:
            raise ValueError(f"Unknown uniqueness provider: {provider_name}")
        if not selected_option.available:
            reason = selected_option.reason or "provider is not configured"
            raise ValueError(f"Uniqueness provider {provider_name!r} is not available: {reason}")

        status = WorkflowStatus.WAITING_FOR_HUMAN
        self._persist_selection(job_id, provider_name, status)
        return UniquenessProviderSelectionResult(
            job_id=job_id,
            selected_provider=provider_name,
            provider_options=provider_options,
            status=status,
        )

    @staticmethod
    def _find_option(
        provider_options: list[UniquenessProviderOption],
        provider_name: UniquenessProviderName,
    ) -> UniquenessProviderOption | None:
        return next((option for option in provider_options if option.name == provider_name), None)

    def _persist_selection(
        self,
        job_id: str,
        provider_name: UniquenessProviderName,
        status: WorkflowStatus,
    ) -> None:
        state = PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))
        metadata = JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.UNIQUENESS_CHECK,
            status=status,
            message=f"Uniqueness provider selected: {provider_name}.",
        )

        state.current_stage = WorkflowStage.UNIQUENESS_CHECK
        state.status = status
        state.manual_gate_required = True
        state.selected_uniqueness_provider = provider_name
        state.qa_flags["uniqueness_provider_selected"] = True
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.UNIQUENESS_CHECK
        metadata.status = status
        metadata.updated_at = datetime.now(UTC)
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)
