"""Final QA service tests."""

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import (
    ArtifactKey,
    ArticleType,
    PipelineState,
    QAReport,
    SEOBrief,
    SEOBriefArtifact,
    UniquenessResult,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.exporters import FinalPackageExporter
from seo_content_pipeline.services.final_qa_service import FinalQAService
from seo_content_pipeline.services.job_service import JobService


def _brief_artifact(job_id: str) -> SEOBriefArtifact:
    return SEOBriefArtifact(
        job_id=job_id,
        article_type=ArticleType.LP,
        brief=SEOBrief(
            topic="AI workflow for SEO content",
            goal="Show how the portfolio project works.",
            audience="Technical hiring managers",
            main_keyword="multi-agent SEO content pipeline",
            secondary_keywords=["SEO automation"],
            lsi_keywords=["quality gates"],
            outline={
                "h1": "Multi-Agent SEO Content Pipeline",
                "sections": [{"h2": "Brief Generation", "h3": ["Quality Gates"]}],
            },
            tone_of_voice="Clear and technical",
            constraints=["Do not invent facts"],
        ),
    )


def _qa_report(job_id: str, stage: WorkflowStage, *, passed: bool, summary: str) -> QAReport:
    return QAReport(
        job_id=job_id,
        stage=stage,
        passed=passed,
        checks=[],
        summary=summary,
        score=1.0 if passed else 0.0,
    )


def _prepare_final_qa_job(tmp_path) -> tuple[str, FinalQAService, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Dry source notes for a landing page.",
        ArticleType.LP,
    )
    job_id = job.metadata.job_id

    store.write_json(job_id, ArtifactKey.BRIEF, _brief_artifact(job_id))
    store.write_text(job_id, ArtifactKey.ENGLISH_ORIGINAL, "# English Original\n\nBody.")
    store.write_json(
        job_id,
        ArtifactKey.ARTICLE_VALIDATION,
        _qa_report(job_id, WorkflowStage.WRITING, passed=True, summary="Article validation passed."),
    )
    store.write_json(
        job_id,
        ArtifactKey.EDITORIAL_QA,
        _qa_report(
            job_id,
            WorkflowStage.EDITORIAL_REVIEW,
            passed=True,
            summary="Editorial QA passed.",
        ),
    )
    store.write_json(
        job_id,
        ArtifactKey.SEO_QA,
        _qa_report(job_id, WorkflowStage.SEO_QA, passed=True, summary="SEO QA passed."),
    )
    store.write_json(
        job_id,
        ArtifactKey.UNIQUENESS,
        UniquenessResult(
            job_id=job_id,
            score=94.0,
            source="manual",
            provider_metadata={"provider": "manual"},
        ),
    )
    store.write_text(job_id, ArtifactKey.LOCALIZATION_ES, "# Spanish\n\nContenido.")
    store.write_text(job_id, ArtifactKey.LOCALIZATION_IT, "# Italian\n\nContenuto.")
    store.write_text(job_id, ArtifactKey.LOCALIZATION_FR, "# French\n\nContenu.")

    state = PipelineState.model_validate(store.read_json(job_id, ArtifactKey.STATE))
    state.current_stage = WorkflowStage.LOCALIZATION
    state.status = WorkflowStatus.RUNNING
    state.qa_flags["article_validation_passed"] = True
    state.qa_flags["editorial_qa_passed"] = True
    state.qa_flags["seo_qa_passed"] = True
    state.qa_flags["uniqueness_gate_passed"] = True
    state.qa_flags["localization_es_generated"] = True
    state.qa_flags["localization_it_generated"] = True
    state.qa_flags["localization_fr_generated"] = True
    state.uniqueness_score = 94.0
    state.uniqueness_threshold = 90.0
    state.localization_geos = {"es": "es-US", "it": "it-IT", "fr": "fr-FR"}
    store.write_json(job_id, ArtifactKey.STATE, state)

    FinalPackageExporter(settings=settings, artifact_store=store).assemble_final_package(job_id)
    return job_id, FinalQAService(settings=settings, artifact_store=store), store


def test_final_qa_service_approves_when_all_mandatory_checks_pass(tmp_path) -> None:
    job_id, service, store = _prepare_final_qa_job(tmp_path)

    result = service.run_final_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.FINAL_QA_REPORT)
    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.status is WorkflowStatus.APPROVED
    assert report["status"] == WorkflowStatus.APPROVED.value
    assert report["failed_checks"] == []
    assert report["uniqueness_result"]["score"] == 94.0
    assert report["uniqueness_result"]["passed"] is True
    assert report["localization_status"]["es"]["present"] is True
    assert report["localization_status"]["it"]["geo"] == "it-IT"
    assert WorkflowStage.FINAL_QA.value in report["completed_stages"]
    assert state["status"] == WorkflowStatus.APPROVED.value
    assert state["qa_flags"]["final_qa_passed"] is True
    assert state["artifact_paths"]["final_qa_report"].endswith("final_qa_report.json")
    assert metadata["status"] == WorkflowStatus.APPROVED.value


def test_final_qa_service_routes_missing_localization_to_revision(tmp_path) -> None:
    job_id, service, store = _prepare_final_qa_job(tmp_path)
    store.artifact_path(job_id, ArtifactKey.LOCALIZATION_FR).unlink()
    state = PipelineState.model_validate(store.read_json(job_id, ArtifactKey.STATE))
    state.qa_flags["localization_fr_generated"] = False
    store.write_json(job_id, ArtifactKey.STATE, state)

    result = service.run_final_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.FINAL_QA_REPORT)
    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.status is WorkflowStatus.NEEDS_REVISION
    assert report["status"] == WorkflowStatus.NEEDS_REVISION.value
    assert any(check["name"] == "artifact_localization_fr_present" for check in report["failed_checks"])
    assert report["localization_status"]["fr"]["present"] is False
    assert report["routing_target"] == WorkflowStage.LOCALIZATION.value
    assert "localization" in report["routing_guidance"]
    assert state["status"] == WorkflowStatus.NEEDS_REVISION.value
    assert state["qa_flags"]["final_qa_passed"] is False
    assert state["revision_notes"]["final_qa"]


def test_final_qa_service_blocks_approval_when_uniqueness_gate_failed(tmp_path) -> None:
    job_id, service, store = _prepare_final_qa_job(tmp_path)
    store.write_json(
        job_id,
        ArtifactKey.UNIQUENESS,
        UniquenessResult(
            job_id=job_id,
            score=82.0,
            source="manual",
            provider_metadata={"provider": "manual"},
        ),
    )
    state = PipelineState.model_validate(store.read_json(job_id, ArtifactKey.STATE))
    state.qa_flags["uniqueness_gate_passed"] = False
    state.uniqueness_score = 82.0
    store.write_json(job_id, ArtifactKey.STATE, state)

    service.run_final_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.FINAL_QA_REPORT)

    assert report["status"] == WorkflowStatus.NEEDS_REVISION.value
    assert report["uniqueness_result"]["score"] == 82.0
    assert report["uniqueness_result"]["passed"] is False
    assert report["routing_target"] == WorkflowStage.UNIQUENESS_CHECK.value
    assert any(check["name"] == "gate_uniqueness_gate_passed" for check in report["failed_checks"])


def test_final_qa_service_blocks_approval_when_qa_report_failed(tmp_path) -> None:
    job_id, service, store = _prepare_final_qa_job(tmp_path)
    store.write_json(
        job_id,
        ArtifactKey.SEO_QA,
        _qa_report(job_id, WorkflowStage.SEO_QA, passed=False, summary="SEO QA failed."),
    )

    service.run_final_qa(job_id)

    report = store.read_json(job_id, ArtifactKey.FINAL_QA_REPORT)

    assert report["status"] == WorkflowStatus.NEEDS_REVISION.value
    assert report["routing_target"] == WorkflowStage.SEO_QA.value
    assert any(check["name"] == "report_seo_qa_passed" for check in report["failed_checks"])
