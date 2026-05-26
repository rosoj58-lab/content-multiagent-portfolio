"""Artifact keys and registry metadata."""

from enum import Enum

from pydantic import BaseModel


class ArtifactKey(str, Enum):
    """Stable keys for every persisted pipeline artifact."""

    METADATA = "metadata"
    INPUT = "input"
    STATE = "state"
    BRIEF = "brief"
    BRIEF_QA = "brief_qa"
    ENGLISH_ORIGINAL = "english_original"
    REJECTED_ENGLISH_ORIGINAL = "rejected_english_original"
    ARTICLE_VALIDATION = "article_validation"
    EDITORIAL_QA = "editorial_qa"
    REVISION_HISTORY = "revision_history"
    SEO_QA = "seo_qa"
    UNIQUENESS = "uniqueness"
    LOCALIZATION_ES = "localization_es"
    LOCALIZATION_IT = "localization_it"
    LOCALIZATION_FR = "localization_fr"
    FINAL_PACKAGE_MD = "final_package_md"
    FINAL_PACKAGE_JSON = "final_package_json"
    FINAL_QA_REPORT = "final_qa_report"


class ArtifactSpec(BaseModel):
    """Metadata used by storage, UI and exporters for one artifact."""

    key: ArtifactKey
    filename: str
    content_type: str
    ui_label: str
    description: str


ARTIFACT_REGISTRY: dict[ArtifactKey, ArtifactSpec] = {
    ArtifactKey.METADATA: ArtifactSpec(
        key=ArtifactKey.METADATA,
        filename="metadata.json",
        content_type="application/json",
        ui_label="Job Metadata",
        description="Persisted job identity, status and history metadata.",
    ),
    ArtifactKey.INPUT: ArtifactSpec(
        key=ArtifactKey.INPUT,
        filename="input.json",
        content_type="application/json",
        ui_label="Dry Input",
        description="Original operator input and selected article type.",
    ),
    ArtifactKey.STATE: ArtifactSpec(
        key=ArtifactKey.STATE,
        filename="state.json",
        content_type="application/json",
        ui_label="Workflow State",
        description="Lightweight persisted workflow state for a job.",
    ),
    ArtifactKey.BRIEF: ArtifactSpec(
        key=ArtifactKey.BRIEF,
        filename="brief.json",
        content_type="application/json",
        ui_label="SEO Brief",
        description="Structured SEO brief used to generate the article.",
    ),
    ArtifactKey.BRIEF_QA: ArtifactSpec(
        key=ArtifactKey.BRIEF_QA,
        filename="brief_qa.json",
        content_type="application/json",
        ui_label="Brief QA",
        description="Deterministic completeness checks for the SEO brief.",
    ),
    ArtifactKey.ENGLISH_ORIGINAL: ArtifactSpec(
        key=ArtifactKey.ENGLISH_ORIGINAL,
        filename="english_original.md",
        content_type="text/markdown",
        ui_label="English Original",
        description="Approved English US source article.",
    ),
    ArtifactKey.REJECTED_ENGLISH_ORIGINAL: ArtifactSpec(
        key=ArtifactKey.REJECTED_ENGLISH_ORIGINAL,
        filename="english_original_rejected.md",
        content_type="text/markdown",
        ui_label="Rejected English Original",
        description="Preserved English draft that triggered a routed revision.",
    ),
    ArtifactKey.ARTICLE_VALIDATION: ArtifactSpec(
        key=ArtifactKey.ARTICLE_VALIDATION,
        filename="article_validation.json",
        content_type="application/json",
        ui_label="Article Validation",
        description="Deterministic checks for English Original structure and length.",
    ),
    ArtifactKey.EDITORIAL_QA: ArtifactSpec(
        key=ArtifactKey.EDITORIAL_QA,
        filename="editorial_qa.json",
        content_type="application/json",
        ui_label="Editorial QA",
        description="Editorial quality checks and revision recommendations.",
    ),
    ArtifactKey.REVISION_HISTORY: ArtifactSpec(
        key=ArtifactKey.REVISION_HISTORY,
        filename="revision_history.json",
        content_type="application/json",
        ui_label="Revision History",
        description="Preserved routed QA decisions and their resolution outcomes.",
    ),
    ArtifactKey.SEO_QA: ArtifactSpec(
        key=ArtifactKey.SEO_QA,
        filename="seo_qa.json",
        content_type="application/json",
        ui_label="SEO QA",
        description="SEO validation checks and routing decision.",
    ),
    ArtifactKey.UNIQUENESS: ArtifactSpec(
        key=ArtifactKey.UNIQUENESS,
        filename="uniqueness.json",
        content_type="application/json",
        ui_label="Uniqueness Report",
        description="Manual, mock or external plagiarism-check result.",
    ),
    ArtifactKey.LOCALIZATION_ES: ArtifactSpec(
        key=ArtifactKey.LOCALIZATION_ES,
        filename="localization_es.md",
        content_type="text/markdown",
        ui_label="Spanish Localization",
        description="Spanish localized article generated after uniqueness approval.",
    ),
    ArtifactKey.LOCALIZATION_IT: ArtifactSpec(
        key=ArtifactKey.LOCALIZATION_IT,
        filename="localization_it.md",
        content_type="text/markdown",
        ui_label="Italian Localization",
        description="Italian localized article generated after uniqueness approval.",
    ),
    ArtifactKey.LOCALIZATION_FR: ArtifactSpec(
        key=ArtifactKey.LOCALIZATION_FR,
        filename="localization_fr.md",
        content_type="text/markdown",
        ui_label="French Localization",
        description="French localized article generated after uniqueness approval.",
    ),
    ArtifactKey.FINAL_PACKAGE_MD: ArtifactSpec(
        key=ArtifactKey.FINAL_PACKAGE_MD,
        filename="final_package.md",
        content_type="text/markdown",
        ui_label="Final Markdown Package",
        description="Human-readable final content package.",
    ),
    ArtifactKey.FINAL_PACKAGE_JSON: ArtifactSpec(
        key=ArtifactKey.FINAL_PACKAGE_JSON,
        filename="final_package.json",
        content_type="application/json",
        ui_label="Final JSON Package",
        description="Machine-readable final content package.",
    ),
    ArtifactKey.FINAL_QA_REPORT: ArtifactSpec(
        key=ArtifactKey.FINAL_QA_REPORT,
        filename="final_qa_report.json",
        content_type="application/json",
        ui_label="Final QA Report",
        description="Final readiness report and approved or revision status.",
    ),
}


def get_artifact_spec(key: ArtifactKey) -> ArtifactSpec:
    """Return registry metadata for an artifact key."""
    return ARTIFACT_REGISTRY[key]
