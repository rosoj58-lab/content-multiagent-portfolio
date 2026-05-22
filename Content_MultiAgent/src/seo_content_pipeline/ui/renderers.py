"""Small render helpers for QA and status data."""

from dataclasses import dataclass

import streamlit as st

from seo_content_pipeline.models import QAReport


@dataclass(frozen=True)
class QAChecklistItem:
    """UI-ready QA checklist row."""

    name: str
    status_label: str
    severity: str
    message: str


def build_qa_checklist(report: QAReport) -> list[QAChecklistItem]:
    """Build display rows from a QA report."""
    return [
        QAChecklistItem(
            name=check.name,
            status_label="Pass" if check.passed else "Fail",
            severity=check.severity,
            message=check.message,
        )
        for check in report.checks
    ]


def render_qa_summary(report: QAReport) -> None:
    """Render a concise QA report summary."""
    status = "Passed" if report.passed else "Needs revision"
    st.markdown(f"**{report.stage.value} QA:** {status}")
    st.caption(report.summary)
    for item in build_qa_checklist(report):
        icon = "[ok]" if item.status_label == "Pass" else "[fix]"
        st.write(f"{icon} {item.name}: {item.message}")
