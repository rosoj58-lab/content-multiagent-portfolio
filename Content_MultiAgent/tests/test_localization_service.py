"""Localization service tests."""

import pytest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import (
    ArtifactKey,
    ArticleType,
    PipelineState,
    SEOBrief,
    SEOBriefArtifact,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.llm_runner import LLMRunner
from seo_content_pipeline.services.localization_service import LocalizationService


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


ENGLISH_ORIGINAL = """# Multi-Agent SEO Content Pipeline

## Brief Generation

### Quality Gates

The system preserves SEO intent for technical hiring managers.
"""

SPANISH_LOCALIZATION = """# Pipeline de Contenido SEO Multiagente

## Generación del Brief

### Controles de Calidad

El sistema conserva la intención SEO para responsables técnicos de contratación.
"""


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


def _prepare_localizable_job(
    tmp_path,
    *,
    responses: list[str],
) -> tuple[str, LocalizationService, ArtifactStore, FakeLLMClient]:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    client = FakeLLMClient(responses)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Create SEO content that will be localized.",
        ArticleType.LP,
    )
    store.write_json(job.metadata.job_id, ArtifactKey.BRIEF, _brief_artifact(job.metadata.job_id))
    store.write_text(job.metadata.job_id, ArtifactKey.ENGLISH_ORIGINAL, ENGLISH_ORIGINAL)
    state = PipelineState.model_validate(store.read_json(job.metadata.job_id, ArtifactKey.STATE))
    state.current_stage = WorkflowStage.LOCALIZATION
    state.status = WorkflowStatus.RUNNING
    state.qa_flags["english_original_generated"] = True
    state.qa_flags["uniqueness_gate_passed"] = True
    store.write_json(job.metadata.job_id, ArtifactKey.STATE, state)
    return (
        job.metadata.job_id,
        LocalizationService(settings=settings, artifact_store=store, llm_runner=LLMRunner(client)),
        store,
        client,
    )


def test_localization_service_generates_spanish_localization_with_default_geo(tmp_path) -> None:
    job_id, service, store, client = _prepare_localizable_job(
        tmp_path,
        responses=[SPANISH_LOCALIZATION],
    )

    result = service.generate_spanish_localization(job_id)

    localization = store.read_text(job_id, ArtifactKey.LOCALIZATION_ES)
    state = store.read_json(job_id, ArtifactKey.STATE)
    metadata = store.read_json(job_id, ArtifactKey.METADATA)

    assert result.localization_path.endswith("localization_es.md")
    assert result.geo == "es-US"
    assert localization.startswith("# Pipeline de Contenido SEO Multiagente")
    assert state["artifact_paths"]["localization_es"].endswith("localization_es.md")
    assert state["localization_geos"]["es"] == "es-US"
    assert state["qa_flags"]["localization_es_generated"] is True
    assert metadata["current_stage"] == WorkflowStage.LOCALIZATION.value
    assert "Spanish" in client.prompts[0]
    assert "es-US" in client.prompts[0]
    assert "# Multi-Agent SEO Content Pipeline" in client.prompts[0]
    assert "multi-agent SEO content pipeline" in client.prompts[0]


def test_localization_service_records_explicit_spanish_geo(tmp_path) -> None:
    job_id, service, store, _client = _prepare_localizable_job(
        tmp_path,
        responses=[SPANISH_LOCALIZATION],
    )

    result = service.generate_spanish_localization(job_id, geo="es-MX")

    state = store.read_json(job_id, ArtifactKey.STATE)

    assert result.geo == "es-MX"
    assert state["localization_geos"]["es"] == "es-MX"


def test_localization_service_rejects_before_uniqueness_gate_passes(tmp_path) -> None:
    job_id, service, store, _client = _prepare_localizable_job(
        tmp_path,
        responses=[SPANISH_LOCALIZATION],
    )
    state = PipelineState.model_validate(store.read_json(job_id, ArtifactKey.STATE))
    state.current_stage = WorkflowStage.UNIQUENESS_CHECK
    state.qa_flags["uniqueness_gate_passed"] = False
    store.write_json(job_id, ArtifactKey.STATE, state)

    with pytest.raises(ValueError, match="uniqueness gate"):
        service.generate_spanish_localization(job_id)
