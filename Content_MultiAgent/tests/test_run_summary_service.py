"""Run summary artifact tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType, WorkflowStatus
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.run_summary_service import RunSummaryService


def _new_job(tmp_path, article_type: ArticleType = ArticleType.BP):
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable source notes for a run summary.",
        article_type,
    )
    return settings, store, job.metadata.job_id


def test_run_summary_can_describe_fresh_job_without_decision_artifact(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path)

    summary = RunSummaryService(settings=settings, artifact_store=store).write_summary(job_id)

    payload = store.read_json(job_id, ArtifactKey.RUN_SUMMARY)
    assert summary.status is WorkflowStatus.RUNNING
    assert payload["job_id"] == job_id
    assert payload["article_type"] == "BP"
    assert payload["status"] == "running"
    assert payload["current_stage"] == "input_received"
    assert payload["decision_artifact"] is None
    assert payload["final_package_path"] is None
    assert payload["generated_artifact_count"] == 3
    assert payload["manual_gate_required"] is False
    assert {artifact["key"] for artifact in payload["generated_artifacts"]} >= {
        "metadata",
        "input",
        "state",
    }


def test_run_summary_describes_approved_demo_decision_and_final_package(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path, ArticleType.BP)

    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job_id,
        mode="demo",
    )

    payload = store.read_json(job_id, ArtifactKey.RUN_SUMMARY)
    assert payload["status"] == "approved"
    assert payload["current_stage"] == "final_qa"
    assert payload["decision_artifact"].endswith("final_qa_report.json")
    assert payload["final_package_path"].endswith("final_package.md")
    assert payload["final_qa_report_path"].endswith("final_qa_report.json")
    assert payload["generated_artifact_count"] >= 15
    assert payload["artifact_counts"]["json"] >= 8
    assert payload["artifact_counts"]["markdown"] >= 4


def test_run_summary_describes_routed_demo_without_final_package(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path, ArticleType.GP)

    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job_id,
        mode="demo",
    )

    payload = store.read_json(job_id, ArtifactKey.RUN_SUMMARY)
    assert payload["status"] == "needs_human_review"
    assert payload["current_stage"] == "editorial_review"
    assert payload["decision_artifact"].endswith("editorial_qa.json")
    assert payload["final_package_path"] is None
    assert payload["final_qa_report_path"] is None
    assert payload["revision_notes"]["editorial_review"] == [
        "Confirm that the contextual project link is acceptable to the host publication."
    ]


def test_run_summary_does_not_point_to_missing_decision_artifact(tmp_path) -> None:
    settings, store, job_id = _new_job(tmp_path)
    state = store.read_json(job_id, ArtifactKey.STATE)
    state["current_stage"] = "brief_drafted"
    state["status"] = "needs_human_review"
    store.write_json(job_id, ArtifactKey.STATE, state)

    RunSummaryService(settings=settings, artifact_store=store).write_summary(job_id)

    payload = store.read_json(job_id, ArtifactKey.RUN_SUMMARY)
    assert payload["decision_artifact"] is None
    assert payload["decision_artifact_key"] is None
