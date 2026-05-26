"""Read-only comparison view for a resolved article revision."""

from dataclasses import dataclass

import streamlit as st

from seo_content_pipeline.models import (
    ArtifactKey,
    ArticleType,
    PipelineState,
    RevisionHistoryArtifact,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


@dataclass(frozen=True)
class RevisionComparison:
    """Two persisted article versions that demonstrate a resolved revision."""

    rejected_markdown: str
    approved_markdown: str


def build_revision_comparison(
    job_id: str,
    artifact_store: ArtifactStore,
) -> RevisionComparison | None:
    """Build comparison data only for an approved LP correction with both versions."""
    state = PipelineState.model_validate(artifact_store.read_json(job_id, ArtifactKey.STATE))
    if state.article_type is not ArticleType.LP or state.status is not WorkflowStatus.APPROVED:
        return None

    history_path = artifact_store.artifact_path(job_id, ArtifactKey.REVISION_HISTORY)
    if not history_path.exists():
        return None
    history = RevisionHistoryArtifact.model_validate(
        artifact_store.read_json(job_id, ArtifactKey.REVISION_HISTORY)
    )
    if not history.revisions:
        return None

    revision = history.revisions[-1]
    rejected_path = artifact_store.artifact_path(job_id, ArtifactKey.REJECTED_ENGLISH_ORIGINAL)
    approved_path = artifact_store.artifact_path(job_id, ArtifactKey.ENGLISH_ORIGINAL)
    if (
        revision.resolved_status is not WorkflowStatus.APPROVED
        or revision.rejected_article_path != str(rejected_path)
        or revision.approved_article_path != str(approved_path)
        or not rejected_path.exists()
        or not approved_path.exists()
    ):
        return None

    return RevisionComparison(
        rejected_markdown=artifact_store.read_text(job_id, ArtifactKey.REJECTED_ENGLISH_ORIGINAL),
        approved_markdown=artifact_store.read_text(job_id, ArtifactKey.ENGLISH_ORIGINAL),
    )


def render_revision_comparison(comparison: RevisionComparison) -> None:
    """Render rejected and approved Markdown articles together for inspection."""
    st.subheader("Revision Comparison")
    rejected_column, approved_column = st.columns(2)
    with rejected_column:
        st.markdown("**Rejected draft**")
        st.code(comparison.rejected_markdown, language="markdown", wrap_lines=True, height=360)
    with approved_column:
        st.markdown("**Approved version**")
        st.code(comparison.approved_markdown, language="markdown", wrap_lines=True, height=360)
