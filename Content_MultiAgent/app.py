"""Streamlit entrypoint for the SEO Content Pipeline."""

import streamlit as st

from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.ui.components import render_job_creation_form, render_job_summary
from seo_content_pipeline.ui.progress_timeline import render_initial_progress_timeline


def main() -> None:
    """Render the local portfolio app shell."""
    st.set_page_config(page_title="SEO Content Pipeline", layout="wide")
    st.title("SEO Content Pipeline")

    service = JobService()
    submission = render_job_creation_form()

    if submission is not None:
        try:
            result = service.create_job(submission.dry_input, submission.article_type)
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state["current_job_result"] = result
            st.session_state["demo_mode"] = submission.demo_mode

    result = st.session_state.get("current_job_result")
    if result is None:
        st.info("Create a job to start the local pipeline shell.")
        return

    artifact_paths = {key.value: path for key, path in result.artifact_paths.items()}
    render_job_summary(result.metadata.job_id, artifact_paths, st.session_state.get("demo_mode", "demo"))
    render_initial_progress_timeline(result.metadata)


if __name__ == "__main__":
    main()
