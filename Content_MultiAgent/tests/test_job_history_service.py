"""Recent job history service tests."""

from datetime import UTC, datetime, timedelta

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_history_service import JobHistoryService
from seo_content_pipeline.services.job_service import JobService


def _create_demo_job(tmp_path, article_type: ArticleType, updated_at: datetime):
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        f"Stable notes for {article_type.value}.",
        article_type,
    )
    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job.metadata.job_id,
        mode="demo",
    )
    metadata = store.read_json(job.metadata.job_id, ArtifactKey.METADATA)
    metadata["updated_at"] = updated_at.isoformat().replace("+00:00", "Z")
    store.write_json(job.metadata.job_id, ArtifactKey.METADATA, metadata)
    return settings, store, job.metadata.job_id


def test_recent_job_history_returns_empty_list_when_artifact_root_is_missing(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path / "missing")

    assert JobHistoryService(settings=settings).list_recent_jobs() == []


def test_recent_job_history_orders_jobs_and_skips_corrupt_folders(tmp_path) -> None:
    now = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
    settings, store, older_job_id = _create_demo_job(tmp_path, ArticleType.LP, now)
    _, _, newer_job_id = _create_demo_job(tmp_path, ArticleType.BP, now + timedelta(minutes=5))
    (tmp_path / "job-corrupt").mkdir()
    (tmp_path / "not-a-job.txt").write_text("ignore me", encoding="utf-8")

    jobs = JobHistoryService(settings=settings, artifact_store=store).list_recent_jobs()

    assert [job.job_id for job in jobs] == [newer_job_id, older_job_id]
    assert jobs[0].article_type is ArticleType.BP
    assert jobs[0].status.value == "approved"
    assert jobs[0].current_stage.value == "final_qa"
    assert jobs[0].artifact_count >= 15
    assert jobs[0].label.startswith(f"{newer_job_id} | BP | approved")
    assert "decision final_qa_report.json" in jobs[0].label


def test_recent_job_history_respects_display_limit(tmp_path) -> None:
    now = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
    settings, store, first_job_id = _create_demo_job(tmp_path, ArticleType.BP, now)
    _create_demo_job(tmp_path, ArticleType.LP, now + timedelta(minutes=1))

    jobs = JobHistoryService(settings=settings, artifact_store=store).list_recent_jobs(limit=1)

    assert len(jobs) == 1
    assert jobs[0].job_id != first_job_id


def test_recent_job_history_loads_existing_job_as_create_job_result(tmp_path) -> None:
    settings, store, job_id = _create_demo_job(
        tmp_path,
        ArticleType.GP,
        datetime(2026, 5, 28, 12, 0, tzinfo=UTC),
    )

    loaded = JobHistoryService(settings=settings, artifact_store=store).load_job(job_id)

    assert loaded.metadata.job_id == job_id
    assert loaded.metadata.article_type is ArticleType.GP
    assert ArtifactKey.METADATA in loaded.artifact_paths
    assert ArtifactKey.STATE in loaded.artifact_paths
    assert ArtifactKey.RUN_SUMMARY in loaded.artifact_paths
