"""Pure workflow routing helpers."""

from seo_content_pipeline.models import UniquenessResult, WorkflowStage


UNIQUENESS_THRESHOLD = 90.0


def route_after_uniqueness_gate(
    uniqueness: UniquenessResult,
    *,
    threshold: float = UNIQUENESS_THRESHOLD,
) -> WorkflowStage:
    """Return the next stage for a uniqueness score."""
    if uniqueness.score >= threshold:
        return WorkflowStage.LOCALIZATION
    return WorkflowStage.WRITING
