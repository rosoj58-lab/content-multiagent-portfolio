"""Artifact keys and registry metadata."""

from enum import Enum

from pydantic import BaseModel


class ArtifactKey(str, Enum):
    """Stable keys for every persisted pipeline artifact."""

    INPUT = "input"
    STATE = "state"
    BRIEF = "brief"
    ENGLISH_ORIGINAL = "english_original"
    EDITORIAL_QA = "editorial_qa"
    SEO_QA = "seo_qa"
    UNIQUENESS = "uniqueness"
    LOCALIZATION_ES = "localization_es"
    LOCALIZATION_IT = "localization_it"
    LOCALIZATION_FR = "localization_fr"
    FINAL_PACKAGE_MD = "final_package_md"
    FINAL_PACKAGE_JSON = "final_package_json"


class ArtifactSpec(BaseModel):
    """Metadata used by storage, UI and exporters for one artifact."""

    key: ArtifactKey
    filename: str
    content_type: str
    ui_label: str
    description: str


ARTIFACT_REGISTRY: dict[ArtifactKey, ArtifactSpec] = {
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
    ArtifactKey.ENGLISH_ORIGINAL: ArtifactSpec(
        key=ArtifactKey.ENGLISH_ORIGINAL,
        filename="english_original.md",
        content_type="text/markdown",
        ui_label="English Original",
        description="Approved English US source article.",
    ),
    ArtifactKey.EDITORIAL_QA: ArtifactSpec(
        key=ArtifactKey.EDITORIAL_QA,
        filename="editorial_qa.json",
        content_type="application/json",
        ui_label="Editorial QA",
        description="Editorial quality checks and revision recommendations.",
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
}


def get_artifact_spec(key: ArtifactKey) -> ArtifactSpec:
    """Return registry metadata for an artifact key."""
    return ARTIFACT_REGISTRY[key]
