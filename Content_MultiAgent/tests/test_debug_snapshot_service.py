"""Job debug snapshot artifact tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.debug_snapshot_service import DebugSnapshotService
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService


def _new_job(tmp_path, article_type: ArticleType = ArticleType.BP):
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable source notes for debug snapshots.",
        article_type,
    )
    return settings, store, job.metadata.job_id


def test_debug_snapshot_describes_fresh_job_artifacts_and_missing_downstream(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path)

    snapshot = DebugSnapshotService(settings=settings, artifact_store=store).write_snapshot(job_id)
    payload = store.read_json(job_id, ArtifactKey.DEBUG_SNAPSHOT)

    assert snapshot.job_id == job_id
    assert payload["status"] == "running"
    assert payload["current_stage"] == "input_received"
    assert payload["manual_gate_required"] is False
    assert payload["workflow_error_count"] == 0
    assert payload["artifact_counts"]["present"] == 3
    assert payload["artifact_counts"]["missing"] >= 10
    assert "metadata" in payload["present_artifacts"]
    assert "input" in payload["present_artifacts"]
    assert "state" in payload["present_artifacts"]
    assert "final_package_md" in payload["missing_artifacts"]
    assert payload["key_paths"]["metadata"].endswith("metadata.json")


def test_debug_snapshot_describes_approved_demo_without_errors(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path, ArticleType.BP)

    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job_id,
        mode="demo",
    )

    payload = store.read_json(job_id, ArtifactKey.DEBUG_SNAPSHOT)
    assert payload["article_type"] == "BP"
    assert payload["status"] == "approved"
    assert payload["current_stage"] == "final_qa"
    assert payload["manual_gate_required"] is False
    assert payload["workflow_error_count"] == 0
    assert payload["critical_missing_artifacts"] == []
    assert payload["key_paths"]["final_package_md"].endswith("final_package.md")
    assert payload["key_paths"]["run_summary"].endswith("run_summary.json")


def test_debug_snapshot_describes_routed_demo_state_and_missing_downstream(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path, ArticleType.GP)

    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job_id,
        mode="demo",
    )

    payload = store.read_json(job_id, ArtifactKey.DEBUG_SNAPSHOT)
    assert payload["status"] == "needs_human_review"
    assert payload["current_stage"] == "editorial_review"
    assert payload["workflow_error_count"] == 1
    assert payload["errors"][0]["code"] == "editorial_human_review_required"
    assert "final_package_md" in payload["missing_artifacts"]
    assert payload["critical_missing_artifacts"] == []
