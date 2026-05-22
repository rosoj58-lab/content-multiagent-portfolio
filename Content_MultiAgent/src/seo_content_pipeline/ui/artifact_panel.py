"""Artifact preview and download panel."""

import json
from dataclasses import dataclass

import streamlit as st

from seo_content_pipeline.models import ARTIFACT_REGISTRY, ArtifactKey
from seo_content_pipeline.services.artifact_store import ArtifactStore


PREVIEW_LIMIT = 4000


@dataclass(frozen=True)
class ArtifactPreview:
    """UI-ready artifact preview data."""

    key: ArtifactKey
    label: str
    path: str
    content_type: str
    preview: str
    content: str
    download_label: str


def build_artifact_previews(
    job_id: str,
    artifact_store: ArtifactStore,
    *,
    artifact_keys: list[ArtifactKey] | None = None,
) -> list[ArtifactPreview]:
    """Build previews for existing artifacts."""
    keys = artifact_keys or list(ARTIFACT_REGISTRY)
    previews: list[ArtifactPreview] = []
    for artifact_key in keys:
        spec = ARTIFACT_REGISTRY[artifact_key]
        path = artifact_store.artifact_path(job_id, artifact_key)
        if not path.exists():
            continue
        if spec.content_type == "application/json":
            payload = artifact_store.read_json(job_id, artifact_key)
            preview = json.dumps(payload, ensure_ascii=False, indent=2)
        else:
            preview = artifact_store.read_text(job_id, artifact_key)
        previews.append(
            ArtifactPreview(
                key=artifact_key,
                label=spec.ui_label,
                path=str(path),
                content_type=spec.content_type,
                preview=_trim_preview(preview),
                content=preview,
                download_label=f"Download {spec.ui_label}",
            )
        )
    return previews


def render_artifact_panel(job_id: str, artifact_store: ArtifactStore) -> None:
    """Render artifact previews and download actions."""
    st.subheader("Artifacts")
    previews = build_artifact_previews(job_id, artifact_store)
    if not previews:
        st.info("No artifacts are available for this job yet.")
        return

    for preview in previews:
        with st.expander(preview.label, expanded=False):
            st.caption(preview.path)
            language = "json" if preview.content_type == "application/json" else "markdown"
            st.code(preview.preview, language=language)
            st.download_button(
                preview.download_label,
                data=preview.content,
                file_name=preview.path.rsplit("/", maxsplit=1)[-1],
                mime=preview.content_type,
            )


def _trim_preview(text: str) -> str:
    if len(text) <= PREVIEW_LIMIT:
        return text
    return text[:PREVIEW_LIMIT] + "\n...[preview truncated]"
