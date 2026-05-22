"""Final package export services."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ARTIFACT_REGISTRY,
    ArtifactKey,
    JobMetadata,
    PipelineState,
    StatusHistoryEntry,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


REQUIRED_PACKAGE_ARTIFACTS = (
    ArtifactKey.INPUT,
    ArtifactKey.BRIEF,
    ArtifactKey.ENGLISH_ORIGINAL,
    ArtifactKey.EDITORIAL_QA,
    ArtifactKey.SEO_QA,
    ArtifactKey.UNIQUENESS,
    ArtifactKey.LOCALIZATION_ES,
    ArtifactKey.LOCALIZATION_IT,
    ArtifactKey.LOCALIZATION_FR,
)


class FinalPackageResult(BaseModel):
    """Result returned after final package assembly."""

    job_id: str
    status: WorkflowStatus
    markdown_path: str
    json_path: str


class ArtifactReference(BaseModel):
    """Traceability reference for one source artifact."""

    filename: str
    content_type: str
    ui_label: str
    path: str


class FinalPackageContent(BaseModel):
    """Article content included in the final package."""

    english_original: str
    localizations: dict[str, str]


class FinalPackageWorkflowStatus(BaseModel):
    """Workflow status captured when the package is assembled."""

    current_stage: WorkflowStage
    status: WorkflowStatus


class FinalContentPackage(BaseModel):
    """Machine-readable final content package."""

    job_id: str
    generated_at: datetime
    article_type: str | None
    dry_input: str
    workflow_status: FinalPackageWorkflowStatus
    artifact_references: dict[ArtifactKey, ArtifactReference]
    seo_brief: dict[str, Any]
    content: FinalPackageContent
    qa_reports: dict[str, dict[str, Any]]
    uniqueness_report: dict[str, Any]


class FinalPackageExporter:
    """Assemble Markdown and JSON final content packages."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def assemble_final_package(self, job_id: str) -> FinalPackageResult:
        """Read completed workflow artifacts and write final package exports."""
        self._ensure_required_artifacts_exist(job_id)

        input_artifact = self.artifact_store.read_json(job_id, ArtifactKey.INPUT)
        brief_artifact = self.artifact_store.read_json(job_id, ArtifactKey.BRIEF)
        editorial_qa = self.artifact_store.read_json(job_id, ArtifactKey.EDITORIAL_QA)
        seo_qa = self.artifact_store.read_json(job_id, ArtifactKey.SEO_QA)
        uniqueness = self.artifact_store.read_json(job_id, ArtifactKey.UNIQUENESS)
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)

        content = FinalPackageContent(
            english_original=self.artifact_store.read_text(
                job_id,
                ArtifactKey.ENGLISH_ORIGINAL,
            ),
            localizations={
                "es": self.artifact_store.read_text(job_id, ArtifactKey.LOCALIZATION_ES),
                "it": self.artifact_store.read_text(job_id, ArtifactKey.LOCALIZATION_IT),
                "fr": self.artifact_store.read_text(job_id, ArtifactKey.LOCALIZATION_FR),
            },
        )
        generated_at = datetime.now(UTC)
        package = FinalContentPackage(
            job_id=job_id,
            generated_at=generated_at,
            article_type=input_artifact.get("article_type") or self._article_type_value(state),
            dry_input=input_artifact["dry_input"],
            workflow_status=FinalPackageWorkflowStatus(
                current_stage=WorkflowStage.FINAL_QA,
                status=WorkflowStatus.RUNNING,
            ),
            artifact_references=self._artifact_references(job_id),
            seo_brief=brief_artifact,
            content=content,
            qa_reports={
                "editorial_qa": editorial_qa,
                "seo_qa": seo_qa,
            },
            uniqueness_report=uniqueness,
        )
        package_payload = package.model_dump(mode="json")
        markdown = self._render_markdown_package(package_payload)

        markdown_path = self.artifact_store.write_text(
            job_id,
            ArtifactKey.FINAL_PACKAGE_MD,
            markdown,
        )
        json_path = self.artifact_store.write_json(
            job_id,
            ArtifactKey.FINAL_PACKAGE_JSON,
            package_payload,
        )
        self._persist_final_package_state(
            job_id,
            markdown_path=str(markdown_path),
            json_path=str(json_path),
            generated_at=generated_at,
            metadata=metadata,
            state=state,
        )
        return FinalPackageResult(
            job_id=job_id,
            status=WorkflowStatus.RUNNING,
            markdown_path=str(markdown_path),
            json_path=str(json_path),
        )

    def _ensure_required_artifacts_exist(self, job_id: str) -> None:
        missing = [
            artifact_key.value
            for artifact_key in REQUIRED_PACKAGE_ARTIFACTS
            if not self.artifact_store.artifact_path(job_id, artifact_key).exists()
        ]
        if missing:
            raise ValueError(f"Final package requires missing artifacts: {', '.join(missing)}")

    def _artifact_references(self, job_id: str) -> dict[ArtifactKey, ArtifactReference]:
        references: dict[ArtifactKey, ArtifactReference] = {}
        for artifact_key in REQUIRED_PACKAGE_ARTIFACTS:
            spec = ARTIFACT_REGISTRY[artifact_key]
            references[artifact_key] = ArtifactReference(
                filename=spec.filename,
                content_type=spec.content_type,
                ui_label=spec.ui_label,
                path=str(self.artifact_store.artifact_path(job_id, artifact_key)),
            )
        return references

    @staticmethod
    def _article_type_value(state: PipelineState) -> str | None:
        if state.article_type is None:
            return None
        return state.article_type.value

    @staticmethod
    def _render_markdown_package(package: dict) -> str:
        brief = package["seo_brief"]["brief"]
        editorial_qa = package["qa_reports"]["editorial_qa"]
        seo_qa = package["qa_reports"]["seo_qa"]
        uniqueness = package["uniqueness_report"]
        references = package["artifact_references"]
        content = package["content"]

        reference_lines = "\n".join(
            f"- {reference['ui_label']}: `{reference['filename']}`"
            for reference in references.values()
        )
        secondary_keywords = ", ".join(brief["secondary_keywords"])
        lsi_keywords = ", ".join(brief["lsi_keywords"])

        return (
            "# Final Content Package\n\n"
            f"- Job ID: `{package['job_id']}`\n"
            f"- Article Type: `{package['article_type']}`\n"
            f"- Generated At: `{package['generated_at']}`\n\n"
            "## Traceability\n\n"
            f"{reference_lines}\n\n"
            "## Dry Input\n\n"
            f"{package['dry_input']}\n\n"
            "## SEO Brief\n\n"
            f"- Topic: {brief['topic']}\n"
            f"- Goal: {brief['goal']}\n"
            f"- Audience: {brief['audience']}\n"
            f"- Main keyword: {brief['main_keyword']}\n"
            f"- Secondary keywords: {secondary_keywords}\n"
            f"- LSI keywords: {lsi_keywords}\n"
            f"- Tone of voice: {brief['tone_of_voice']}\n\n"
            "## English Original\n\n"
            f"{content['english_original']}\n\n"
            "## Spanish Localization\n\n"
            f"{content['localizations']['es']}\n\n"
            "## Italian Localization\n\n"
            f"{content['localizations']['it']}\n\n"
            "## French Localization\n\n"
            f"{content['localizations']['fr']}\n\n"
            "## Editorial QA Report\n\n"
            f"- Passed: `{editorial_qa['passed']}`\n"
            f"- Summary: {editorial_qa['summary']}\n\n"
            "## SEO QA Report\n\n"
            f"- Passed: `{seo_qa['passed']}`\n"
            f"- Summary: {seo_qa['summary']}\n\n"
            "## Uniqueness Report\n\n"
            f"- Score: `{uniqueness['score']}`\n"
            f"- Source: `{uniqueness['source']}`\n\n"
            "## Workflow Status\n\n"
            f"- Stage: `{package['workflow_status']['current_stage']}`\n"
            f"- Status: `{package['workflow_status']['status']}`"
        )

    def _persist_final_package_state(
        self,
        job_id: str,
        *,
        markdown_path: str,
        json_path: str,
        generated_at: datetime,
        metadata: JobMetadata,
        state: PipelineState,
    ) -> None:
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.FINAL_QA,
            status=WorkflowStatus.RUNNING,
            message="Final Markdown and JSON packages assembled.",
            created_at=generated_at,
        )

        state.current_stage = WorkflowStage.FINAL_QA
        state.status = WorkflowStatus.RUNNING
        state.artifact_paths[ArtifactKey.FINAL_PACKAGE_MD] = markdown_path
        state.artifact_paths[ArtifactKey.FINAL_PACKAGE_JSON] = json_path
        state.qa_flags["final_package_assembled"] = True
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.FINAL_QA
        metadata.status = WorkflowStatus.RUNNING
        metadata.updated_at = generated_at
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
