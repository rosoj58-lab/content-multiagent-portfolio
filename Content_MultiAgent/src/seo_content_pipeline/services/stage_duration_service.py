"""Derived stage duration observability helpers."""

from itertools import pairwise

from seo_content_pipeline.models import StageDurationSummary, StatusHistoryEntry, WorkflowStage


def build_stage_duration_summary(
    status_history: list[StatusHistoryEntry],
) -> list[StageDurationSummary]:
    """Aggregate elapsed time per stage from consecutive status history timestamps."""
    if len(status_history) < 2:
        return []

    ordered_history = sorted(status_history, key=lambda entry: entry.created_at)
    totals: dict[WorkflowStage, float] = {}
    counts: dict[WorkflowStage, int] = {}

    for previous, current in pairwise(ordered_history):
        elapsed_seconds = (current.created_at - previous.created_at).total_seconds()
        if elapsed_seconds < 0:
            continue
        totals[previous.stage] = totals.get(previous.stage, 0) + elapsed_seconds
        counts[previous.stage] = counts.get(previous.stage, 0) + 1

    return [
        StageDurationSummary(
            stage=stage,
            elapsed_seconds=round(totals[stage], 3),
            transition_count=counts[stage],
        )
        for stage in WorkflowStage
        if stage in totals
    ]


def total_duration_seconds(stage_durations: list[StageDurationSummary]) -> float:
    """Return total elapsed seconds across derived stage duration rows."""
    return round(sum(duration.elapsed_seconds for duration in stage_durations), 3)


def format_duration_label(elapsed_seconds: float) -> str:
    """Format elapsed seconds for compact Streamlit timeline display."""
    if elapsed_seconds <= 0:
        return "0s"
    if elapsed_seconds < 1:
        return "<1s"

    total_seconds = int(round(elapsed_seconds))
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"
