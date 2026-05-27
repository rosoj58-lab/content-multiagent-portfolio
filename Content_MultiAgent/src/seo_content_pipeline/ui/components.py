"""Streamlit UI components for the app shell."""

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from seo_content_pipeline.models import ArticleType


DemoMode = Literal["demo", "full"]


@dataclass(frozen=True)
class JobFormSubmission:
    """Validated user input from the job creation form."""

    dry_input: str
    article_type: ArticleType
    demo_mode: DemoMode


def render_job_creation_form() -> JobFormSubmission | None:
    """Render the dry input form and return a submission when requested."""
    with st.form("create-job-form"):
        dry_input = st.text_area(
            "Dry input",
            height=180,
            placeholder="Paste the source notes, offer, audience and keyword ideas here.",
        )
        article_type_value = st.selectbox(
            "Article type",
            options=[article_type.value for article_type in ArticleType],
            index=1,
        )
        demo_mode = st.segmented_control(
            "Mode",
            options=["demo", "full"],
            default="demo",
        )
        submitted = st.form_submit_button("Create job", type="primary")

    if not submitted:
        return None

    selected_mode: DemoMode = "full" if demo_mode == "full" else "demo"
    return JobFormSubmission(
        dry_input=dry_input,
        article_type=ArticleType(article_type_value),
        demo_mode=selected_mode,
    )


def render_job_summary(job_id: str, artifact_paths: dict[str, str], demo_mode: str) -> None:
    """Render created job metadata and artifact paths."""
    st.success(f"Job created: {job_id}")
    st.caption(f"Mode: {demo_mode}")
    with st.expander("Artifacts", expanded=True):
        for label, path in artifact_paths.items():
            st.code(f"{label}: {path}", language="text")


def render_lp_correction_form(default_statement: str) -> str | None:
    """Render the focused LP correction input and return submitted wording."""
    with st.form("lp-correction-form"):
        statement = st.text_area(
            "Replacement statement",
            value=default_statement,
            height=100,
        )
        submitted = st.form_submit_button("Apply correction", type="primary")

    return statement if submitted else None
