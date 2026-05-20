"""Artifact store tests."""

from pathlib import Path

import pytest

from seo_content_pipeline.models import (
    ARTIFACT_REGISTRY,
    ArtifactKey,
    JobMetadata,
    WorkflowStage,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


def test_artifact_store_resolves_paths_from_registry(tmp_path) -> None:
    store = ArtifactStore(artifact_root=tmp_path)

    path = store.artifact_path("job-123", ArtifactKey.METADATA)

    assert path == tmp_path / "job-123" / ARTIFACT_REGISTRY[ArtifactKey.METADATA].filename


def test_artifact_store_writes_and_reads_json_artifacts(tmp_path) -> None:
    store = ArtifactStore(artifact_root=tmp_path)
    metadata = JobMetadata(job_id="job-123", current_stage=WorkflowStage.INPUT_RECEIVED)

    path = store.write_json("job-123", ArtifactKey.METADATA, metadata)
    loaded = store.read_json("job-123", ArtifactKey.METADATA)

    assert path == tmp_path / "job-123" / "metadata.json"
    assert loaded["job_id"] == "job-123"
    assert loaded["current_stage"] == "input_received"
    assert loaded["status"] == "running"


def test_artifact_store_replaces_existing_json_atomically(tmp_path) -> None:
    store = ArtifactStore(artifact_root=tmp_path)

    store.write_json("job-123", ArtifactKey.INPUT, {"value": "first"})
    store.write_json("job-123", ArtifactKey.INPUT, {"value": "second"})

    assert store.read_json("job-123", ArtifactKey.INPUT) == {"value": "second"}
    assert not list(Path(tmp_path / "job-123").glob("*.tmp"))


@pytest.mark.parametrize("unsafe_job_id", ["", "../outside", "nested/job", "/tmp/job"])
def test_artifact_store_rejects_unsafe_job_ids(tmp_path, unsafe_job_id) -> None:
    store = ArtifactStore(artifact_root=tmp_path)

    with pytest.raises(ValueError, match="job_id"):
        store.artifact_path(unsafe_job_id, ArtifactKey.INPUT)
