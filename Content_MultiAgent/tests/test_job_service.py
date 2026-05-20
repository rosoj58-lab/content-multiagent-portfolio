"""Job service tests."""

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, WorkflowStage, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService


def test_job_service_create_job_persists_job_shell(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    service = JobService(settings=settings, artifact_store=store)

    result = service.create_job("Create SEO content for a product page.", ArticleType.LP)

    assert result.metadata.job_id
    assert result.metadata.current_stage is WorkflowStage.INPUT_RECEIVED
    assert result.metadata.status is WorkflowStatus.RUNNING
    assert set(result.artifact_paths) == {ArtifactKey.METADATA, ArtifactKey.INPUT, ArtifactKey.STATE}

    metadata = store.read_json(result.metadata.job_id, ArtifactKey.METADATA)
    input_artifact = store.read_json(result.metadata.job_id, ArtifactKey.INPUT)
    state = store.read_json(result.metadata.job_id, ArtifactKey.STATE)

    assert metadata["job_id"] == result.metadata.job_id
    assert input_artifact["dry_input"] == "Create SEO content for a product page."
    assert input_artifact["article_type"] == "LP"
    assert input_artifact["stage"] == "input_received"
    assert state["job_id"] == result.metadata.job_id
    assert state["current_stage"] == "input_received"


def test_job_service_rejects_empty_dry_input(tmp_path) -> None:
    service = JobService(
        settings=AppSettings(artifact_root=tmp_path),
        artifact_store=ArtifactStore(tmp_path),
    )

    with pytest.raises(ValueError, match="dry input"):
        service.create_job("   ")
