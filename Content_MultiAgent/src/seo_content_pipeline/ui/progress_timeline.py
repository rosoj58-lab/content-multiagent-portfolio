"""Streamlit rendering for workflow progress."""

import streamlit as st

from seo_content_pipeline.models import StageView, WorkflowStatus


STATUS_ICONS = {
    WorkflowStatus.RUNNING: "[run]",
    WorkflowStatus.WAITING_FOR_HUMAN: "[wait]",
    WorkflowStatus.APPROVED: "[ok]",
    WorkflowStatus.NEEDS_REVISION: "[revise]",
    WorkflowStatus.NEEDS_HUMAN_REVIEW: "[review]",
    WorkflowStatus.FAILED: "[fail]",
}


def render_progress_timeline(stage_views: list[StageView]) -> None:
    """Render a compact status timeline."""
    st.subheader("Pipeline status")
    for view in stage_views:
        icon = STATUS_ICONS[view.status]
        with st.container(border=True):
            st.markdown(f"**{icon} {view.label}**")
            st.caption(view.status.value.replace("_", " "))
            st.write(view.description)
            if view.blocking_reason:
                st.warning(view.blocking_reason)
            if view.artifact_links:
                st.caption(
                    "Artifacts: "
                    + ", ".join(artifact_key.value for artifact_key in view.artifact_links)
                )
            if view.available_actions:
                st.caption("Next: " + ", ".join(view.available_actions))
