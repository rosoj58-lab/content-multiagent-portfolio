"""Decision QA scorecard builders and Streamlit rendering."""

from dataclasses import dataclass

import streamlit as st

from seo_content_pipeline.models import (
    ArtifactKey,
    FinalQAReport,
    PipelineState,
    QAReport,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


TERMINAL_DECISIONS = {
    WorkflowStatus.APPROVED,
    WorkflowStatus.NEEDS_REVISION,
    WorkflowStatus.NEEDS_HUMAN_REVIEW,
}
LOCALIZATION_LABELS = {
    "es": "Spanish localization",
    "it": "Italian localization",
    "fr": "French localization",
}


@dataclass(frozen=True)
class ScorecardSignal:
    """One human-readable quality signal behind a decision."""

    label: str
    status_label: str
    detail: str


@dataclass(frozen=True)
class DecisionScorecard:
    """UI-ready explanation of a terminal workflow decision."""

    status: WorkflowStatus
    decision_stage: WorkflowStage
    summary: str
    signals: list[ScorecardSignal]
    decision_artifact: ArtifactKey
    routing_target: WorkflowStage | None = None
    next_action: str | None = None


def build_decision_scorecard(
    job_id: str,
    artifact_store: ArtifactStore,
) -> DecisionScorecard | None:
    """Build a scorecard once a persisted job has reached a decision."""
    state = PipelineState.model_validate(artifact_store.read_json(job_id, ArtifactKey.STATE))
    if state.status not in TERMINAL_DECISIONS:
        return None

    final_qa_path = artifact_store.artifact_path(job_id, ArtifactKey.FINAL_QA_REPORT)
    if final_qa_path.exists():
        report = FinalQAReport.model_validate(
            artifact_store.read_json(job_id, ArtifactKey.FINAL_QA_REPORT)
        )
        return _build_final_qa_scorecard(report)

    editorial_path = artifact_store.artifact_path(job_id, ArtifactKey.EDITORIAL_QA)
    if editorial_path.exists() and state.current_stage is WorkflowStage.EDITORIAL_REVIEW:
        report = QAReport.model_validate(artifact_store.read_json(job_id, ArtifactKey.EDITORIAL_QA))
        return _build_editorial_scorecard(report, state.status)

    return None


def _build_final_qa_scorecard(report: FinalQAReport) -> DecisionScorecard:
    score = report.uniqueness_result.score
    score_label = "not recorded" if score is None else f"{score:g}%"
    signals = [
        ScorecardSignal(
            label="Final quality gate",
            status_label="Pass" if not report.failed_checks else "Fail",
            detail=(
                "All mandatory artifacts and checks passed."
                if not report.failed_checks
                else f"{len(report.failed_checks)} blocking checks remain."
            ),
        ),
        ScorecardSignal(
            label="Uniqueness threshold",
            status_label="Pass" if report.uniqueness_result.passed else "Fail",
            detail=(
                f"Score {score_label}; required {report.uniqueness_result.threshold:g}%"
                f" ({report.uniqueness_result.source or 'unknown source'})."
            ),
        ),
    ]
    for language, localization in report.localization_status.items():
        signals.append(
            ScorecardSignal(
                label=LOCALIZATION_LABELS.get(language, f"{language} localization"),
                status_label="Ready" if localization.present else "Missing",
                detail=localization.geo or "Artifact availability checked.",
            )
        )
    for failed_check in report.failed_checks:
        signals.append(
            ScorecardSignal(
                label=failed_check.name,
                status_label="Fail",
                detail=failed_check.message,
            )
        )
    return DecisionScorecard(
        status=report.status,
        decision_stage=WorkflowStage.FINAL_QA,
        summary=(
            "Final package is approved and ready for review."
            if report.status is WorkflowStatus.APPROVED
            else "Final QA identified blocking work before approval."
        ),
        signals=signals,
        decision_artifact=ArtifactKey.FINAL_QA_REPORT,
        routing_target=report.routing_target,
        next_action=report.routing_guidance,
    )


def _build_editorial_scorecard(
    report: QAReport,
    status: WorkflowStatus,
) -> DecisionScorecard:
    signals = [
        ScorecardSignal(
            label=check.name,
            status_label="Pass" if check.passed else "Fail",
            detail=check.message,
        )
        for check in report.checks
    ]
    return DecisionScorecard(
        status=status,
        decision_stage=report.stage,
        summary=report.summary,
        signals=signals,
        decision_artifact=ArtifactKey.EDITORIAL_QA,
        routing_target=report.routing_target,
        next_action=report.recommendations[0] if report.recommendations else None,
    )


def render_decision_scorecard(scorecard: DecisionScorecard) -> None:
    """Render a concise explanation of the persisted terminal decision."""
    st.subheader("Decision QA Scorecard")
    outcome = scorecard.status.value.replace("_", " ")
    if scorecard.status is WorkflowStatus.APPROVED:
        st.success(f"Outcome: {outcome}")
    else:
        st.warning(f"Outcome: {outcome}")
    st.caption(f"Decision stage: {scorecard.decision_stage.value}")
    st.write(scorecard.summary)
    for signal in scorecard.signals:
        marker = "[ok]" if signal.status_label in {"Pass", "Ready"} else "[action]"
        st.write(f"{marker} {signal.label}: {signal.status_label} - {signal.detail}")
    if scorecard.routing_target:
        st.caption(f"Route: {scorecard.routing_target.value}")
    if scorecard.next_action:
        st.info(f"Next action: {scorecard.next_action}")
