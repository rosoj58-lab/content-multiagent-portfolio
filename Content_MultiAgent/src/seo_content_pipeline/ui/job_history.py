"""Streamlit controls for loading recent local jobs."""

import streamlit as st

from seo_content_pipeline.services.job_history_service import RecentJobSummary


def render_recent_job_picker(recent_jobs: list[RecentJobSummary]) -> str | None:
    """Render a compact recent jobs picker and return the selected job id on submit."""
    st.subheader("Recent jobs")
    if not recent_jobs:
        st.caption("No recent jobs yet.")
        return None

    labels_by_job_id = {job.label: job.job_id for job in recent_jobs}
    with st.form("recent-job-form"):
        selected_label = st.selectbox("Recent jobs", options=list(labels_by_job_id))
        submitted = st.form_submit_button("Load selected job", type="secondary")

    if not submitted:
        return None
    return labels_by_job_id[selected_label]
