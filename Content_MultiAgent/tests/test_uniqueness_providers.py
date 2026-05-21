"""Uniqueness provider selection tests."""

import importlib

import pytest

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import ArtifactKey, PipelineState, WorkflowStage, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.uniqueness_provider_service import UniquenessProviderService
from seo_content_pipeline.services.uniqueness_score_service import UniquenessScoreService


def _service_setup(
    tmp_path,
    *,
    settings: AppSettings | None = None,
) -> tuple[str, UniquenessProviderService, UniquenessScoreService, ArtifactStore]:
    settings = settings or AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Create SEO content that will later need a uniqueness check."
    )
    return (
        job.metadata.job_id,
        UniquenessProviderService(settings=settings, artifact_store=store),
        UniquenessScoreService(settings=settings, artifact_store=store),
        store,
    )


def _mark_seo_qa_passed(job_id: str, store: ArtifactStore) -> None:
    state = PipelineState.model_validate(store.read_json(job_id, ArtifactKey.STATE))
    state.current_stage = WorkflowStage.SEO_QA
    state.status = WorkflowStatus.RUNNING
    state.qa_flags["seo_qa_passed"] = True
    store.write_json(job_id, ArtifactKey.STATE, state)


def test_manual_and_mock_providers_are_available_without_external_credentials(tmp_path) -> None:
    _job_id, service, _score_service, _store = _service_setup(tmp_path)

    options = {option.name: option for option in service.list_provider_options()}

    assert options["manual"].available is True
    assert options["manual"].configured is True
    assert options["mock"].available is True
    assert options["mock"].configured is True


def test_copyleaks_provider_is_unavailable_without_credentials(tmp_path) -> None:
    _job_id, service, _score_service, _store = _service_setup(tmp_path)

    options = {option.name: option for option in service.list_provider_options()}

    assert options["copyleaks"].available is False
    assert options["copyleaks"].configured is False
    assert options["copyleaks"].implementation_status == "unconfigured"
    assert options["copyleaks"].supports_automated_check is False
    assert options["copyleaks"].deferred_reason == "FR10 Copyleaks API submission is optional/deferred for the MVP."
    assert "credentials" in str(options["copyleaks"].reason)


def test_copyleaks_provider_is_available_when_credentials_are_configured(tmp_path) -> None:
    settings = AppSettings(
        artifact_root=tmp_path,
        copyleaks_email="demo@example.com",
        copyleaks_api_key="secret",
    )
    _job_id, service, _score_service, _store = _service_setup(tmp_path, settings=settings)

    options = {option.name: option for option in service.list_provider_options()}

    assert options["copyleaks"].available is True
    assert options["copyleaks"].configured is True
    assert options["copyleaks"].implementation_status == "deferred"
    assert options["copyleaks"].supports_automated_check is False
    assert options["copyleaks"].deferred_reason == "FR10 Copyleaks API submission is optional/deferred for the MVP."


def test_copyleaks_provider_imports_without_optional_sdk(monkeypatch) -> None:
    original_import = __import__

    def guarded_import(name, *args, **kwargs):
        if name.startswith("copyleaks"):
            raise AssertionError("Copyleaks SDK should not be imported by the stub provider")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)

    module = importlib.import_module("seo_content_pipeline.providers.copyleaks_uniqueness")
    module = importlib.reload(module)

    assert hasattr(module, "CopyleaksUniquenessProvider")


def test_missing_copyleaks_config_does_not_fail_settings_startup(monkeypatch) -> None:
    monkeypatch.delenv("COPYLEAKS_EMAIL", raising=False)
    monkeypatch.delenv("COPYLEAKS_API_KEY", raising=False)

    settings = get_settings(load_env_file=False)

    assert settings.copyleaks_email is None
    assert settings.copyleaks_api_key is None


def test_provider_selection_persists_selected_provider_in_job_state(tmp_path) -> None:
    job_id, service, _score_service, store = _service_setup(tmp_path)
    _mark_seo_qa_passed(job_id, store)

    result = service.select_provider(job_id, "mock")

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.selected_provider == "mock"
    assert result.status is WorkflowStatus.WAITING_FOR_HUMAN
    assert state["current_stage"] == WorkflowStage.UNIQUENESS_CHECK.value
    assert state["status"] == WorkflowStatus.WAITING_FOR_HUMAN.value
    assert state["selected_uniqueness_provider"] == "mock"
    assert state["manual_gate_required"] is True
    assert state["qa_flags"]["uniqueness_provider_selected"] is True
    assert metadata["current_stage"] == WorkflowStage.UNIQUENESS_CHECK.value
    assert metadata["status"] == WorkflowStatus.WAITING_FOR_HUMAN.value


def test_unavailable_provider_selection_is_rejected_without_state_mutation(tmp_path) -> None:
    job_id, service, _score_service, store = _service_setup(tmp_path)
    _mark_seo_qa_passed(job_id, store)

    with pytest.raises(ValueError, match="not available"):
        service.select_provider(job_id, "copyleaks")

    state = store.read_json(job_id, ArtifactKey.STATE)

    assert state["current_stage"] == WorkflowStage.SEO_QA.value
    assert state.get("selected_uniqueness_provider") is None


def test_provider_selection_requires_passed_seo_qa(tmp_path) -> None:
    job_id, service, _score_service, store = _service_setup(tmp_path)

    with pytest.raises(ValueError, match="SEO QA"):
        service.select_provider(job_id, "manual")

    state = store.read_json(job_id, ArtifactKey.STATE)

    assert state["current_stage"] == WorkflowStage.INPUT_RECEIVED.value
    assert state.get("selected_uniqueness_provider") is None


def test_manual_uniqueness_score_records_uniqueness_artifact(tmp_path) -> None:
    job_id, provider_service, score_service, store = _service_setup(tmp_path)
    _mark_seo_qa_passed(job_id, store)
    provider_service.select_provider(job_id, "manual")

    result = score_service.record_manual_score(job_id, 92.5)

    artifact = store.read_json(job_id, ArtifactKey.UNIQUENESS)
    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.uniqueness.score == 92.5
    assert artifact["score"] == 92.5
    assert artifact["source"] == "manual"
    assert artifact["provider_metadata"]["provider"] == "manual"
    assert artifact["provider_metadata"]["entered_by"] == "operator"
    assert artifact["created_at"]
    assert state["artifact_paths"]["uniqueness"].endswith("uniqueness.json")
    assert state["qa_flags"]["uniqueness_score_recorded"] is True
    assert state["manual_gate_required"] is False
    assert state["status"] == WorkflowStatus.RUNNING.value
    assert metadata["status"] == WorkflowStatus.RUNNING.value


@pytest.mark.parametrize("score", [0, 90, 100])
def test_manual_uniqueness_score_accepts_boundary_values(tmp_path, score) -> None:
    job_id, provider_service, score_service, store = _service_setup(tmp_path)
    _mark_seo_qa_passed(job_id, store)
    provider_service.select_provider(job_id, "manual")

    result = score_service.record_manual_score(job_id, score)

    assert result.uniqueness.score == float(score)


@pytest.mark.parametrize("score", [-0.1, 100.1, True, "95"])
def test_manual_uniqueness_score_rejects_invalid_values(tmp_path, score) -> None:
    job_id, provider_service, score_service, store = _service_setup(tmp_path)
    _mark_seo_qa_passed(job_id, store)
    provider_service.select_provider(job_id, "manual")

    with pytest.raises(ValueError, match="0 to 100"):
        score_service.record_manual_score(job_id, score)

    state = store.read_json(job_id, ArtifactKey.STATE)

    assert "uniqueness" not in state["artifact_paths"]
    assert state["manual_gate_required"] is True


def test_manual_uniqueness_score_requires_manual_provider_selection(tmp_path) -> None:
    job_id, provider_service, score_service, store = _service_setup(tmp_path)
    _mark_seo_qa_passed(job_id, store)
    provider_service.select_provider(job_id, "mock")

    with pytest.raises(ValueError, match="manual provider"):
        score_service.record_manual_score(job_id, 95)

    state = store.read_json(job_id, ArtifactKey.STATE)

    assert "uniqueness" not in state["artifact_paths"]
