"""Empty states for the local portfolio UI."""

import streamlit as st


def render_no_job_empty_state() -> None:
    """Render the initial app state before a job exists."""
    st.info("Create a job to start the local pipeline shell.")
    st.caption("For a repeatable demo, paste one of the files from examples/inputs.")
