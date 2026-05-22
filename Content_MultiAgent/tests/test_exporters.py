"""Final package exporter tests."""

import pytest

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
from seo_content_pipeline.services.job_service import JobService


ENGLISH_ORIGINAL = """# Multi-Agent SEO Content Pipeline

## Brief Generation

### Quality Gates

The system preserves SEO intent for technical hiring managers.
"""

SPANISH_LOCALIZATION = "# Pipeline de Contenido SEO Multiagente\n\nContenido localizado."
ITALIAN_LOCALIZATION = "# Pipeline di Contenuti SEO Multi-Agente\n\nContenuto localizzato."
FRENCH_LOCALIZATION = "# Pipeline de Contenu SEO Multi-Agent\n\nContenu localisé."


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


def _qa_report(job_id: str, stage: WorkflowStage, summary: str) -> QAReport:
    return QAReport(
        job_id=job_id,
        stage=stage,
        passed=True,
        checks=[],
        summary=summary,
        score=1.0,
    )


def _prepare_packageable_job(tmp_path) -> tuple[str, FinalPackageExporter, ArtifactStore]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Dry source notes for a landing page.",
        ArticleType.LP,
    )
    job_id = job.metadata.job_id

    store.write_json(job_id, ArtifactKey.BRIEF, _brief_artifact(job_id))
    store.write_text(job_id, ArtifactKey.ENGLISH_ORIGINAL, ENGLISH_ORIGINAL)
    store.write_json(
        job_id,
        ArtifactKey.EDITORIAL_QA,
        _qa_report(job_id, WorkflowStage.EDITORIAL_REVIEW, "Editorial QA passed."),
    )
    store.write_json(
        job_id,
        ArtifactKey.SEO_QA,
        _qa_report(job_id, WorkflowStage.SEO_QA, "SEO QA passed."),
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
    store.write_text(job_id, ArtifactKey.LOCALIZATION_ES, SPANISH_LOCALIZATION)
    store.write_text(job_id, ArtifactKey.LOCALIZATION_IT, ITALIAN_LOCALIZATION)
    store.write_text(job_id, ArtifactKey.LOCALIZATION_FR, FRENCH_LOCALIZATION)

    state = PipelineState.model_validate(store.read_json(job_id, ArtifactKey.STATE))
    state.current_stage = WorkflowStage.LOCALIZATION
    state.status = WorkflowStatus.RUNNING
    state.qa_flags["seo_qa_passed"] = True
    state.qa_flags["uniqueness_gate_passed"] = True
    state.qa_flags["localization_es_generated"] = True
    state.qa_flags["localization_it_generated"] = True
    state.qa_flags["localization_fr_generated"] = True
    store.write_json(job_id, ArtifactKey.STATE, state)

    return job_id, FinalPackageExporter(settings=settings, artifact_store=store), store


def test_final_package_exporter_persists_markdown_and_json(tmp_path) -> None:
    job_id, exporter, store = _prepare_packageable_job(tmp_path)

    result = exporter.assemble_final_package(job_id)

    markdown = store.read_text(job_id, ArtifactKey.FINAL_PACKAGE_MD)
    package = store.read_json(job_id, ArtifactKey.FINAL_PACKAGE_JSON)
    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.markdown_path.endswith("final_package.md")
    assert result.json_path.endswith("final_package.json")
    assert markdown.startswith("# Final Content Package")
    assert "## English Original" in markdown
    assert "## Spanish Localization" in markdown
    assert "## Italian Localization" in markdown
    assert "## French Localization" in markdown
    assert "Editorial QA passed." in markdown
    assert "SEO QA passed." in markdown
    assert package["job_id"] == job_id
    assert package["article_type"] == "LP"
    assert package["dry_input"] == "Dry source notes for a landing page."
    assert package["content"]["english_original"].startswith("# Multi-Agent SEO Content Pipeline")
    assert package["content"]["localizations"]["es"].startswith("# Pipeline de Contenido SEO")
    assert package["qa_reports"]["seo_qa"]["summary"] == "SEO QA passed."
    assert package["uniqueness_report"]["score"] == 94.0
    assert state["artifact_paths"]["final_package_md"].endswith("final_package.md")
    assert state["artifact_paths"]["final_package_json"].endswith("final_package.json")
    assert state["qa_flags"]["final_package_assembled"] is True
    assert state["current_stage"] == WorkflowStage.FINAL_QA.value
    assert state["status"] == WorkflowStatus.RUNNING.value
    assert metadata["current_stage"] == WorkflowStage.FINAL_QA.value
    assert metadata["status"] == WorkflowStatus.RUNNING.value
    assert package["workflow_status"]["current_stage"] == WorkflowStage.FINAL_QA.value
    assert package["workflow_status"]["status"] == WorkflowStatus.RUNNING.value


def test_final_package_json_includes_traceability_references(tmp_path) -> None:
    job_id, exporter, store = _prepare_packageable_job(tmp_path)

    exporter.assemble_final_package(job_id)

    package = store.read_json(job_id, ArtifactKey.FINAL_PACKAGE_JSON)
    references = package["artifact_references"]

    assert references["input"]["filename"] == "input.json"
    assert references["brief"]["filename"] == "brief.json"
    assert references["editorial_qa"]["filename"] == "editorial_qa.json"
    assert references["seo_qa"]["filename"] == "seo_qa.json"
    assert references["uniqueness"]["filename"] == "uniqueness.json"
    assert references["localization_es"]["filename"] == "localization_es.md"
    assert references["localization_it"]["filename"] == "localization_it.md"
    assert references["localization_fr"]["filename"] == "localization_fr.md"
    assert references["input"]["ui_label"] == "Dry Input"
    assert package["seo_brief"]["brief"]["main_keyword"] == "multi-agent SEO content pipeline"


def test_final_package_exporter_rejects_missing_required_artifact(tmp_path) -> None:
    job_id, exporter, store = _prepare_packageable_job(tmp_path)
    store.artifact_path(job_id, ArtifactKey.LOCALIZATION_FR).unlink()

    with pytest.raises(ValueError, match="localization_fr"):
        exporter.assemble_final_package(job_id)

    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert not store.artifact_path(job_id, ArtifactKey.FINAL_PACKAGE_MD).exists()
    assert not store.artifact_path(job_id, ArtifactKey.FINAL_PACKAGE_JSON).exists()
    assert ArtifactKey.FINAL_PACKAGE_MD.value not in state["artifact_paths"]
    assert ArtifactKey.FINAL_PACKAGE_JSON.value not in state["artifact_paths"]
    assert metadata["status"] != WorkflowStatus.APPROVED.value
