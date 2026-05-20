"""Build UI-ready workflow stage views."""

from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    StageView,
    WorkflowStage,
    WorkflowStatus,
)


def build_initial_stage_views(metadata: JobMetadata) -> list[StageView]:
    """Build the initial timeline for a newly created job shell."""
    return [
        StageView(
            stage=WorkflowStage.INPUT_RECEIVED,
            status=metadata.status,
            label="Input received",
            description="Dry input is saved and ready for SEO brief generation.",
            artifact_links=[
                ArtifactKey.METADATA,
                ArtifactKey.INPUT,
                ArtifactKey.STATE,
            ],
            available_actions=["Create SEO brief"],
        ),
        StageView(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=WorkflowStatus.WAITING_FOR_HUMAN,
            label="SEO brief",
            description="This step will generate and validate the SEO brief in the next epic.",
            artifact_links=[],
            available_actions=[],
            blocking_reason="Brief generation is not implemented yet.",
        ),
    ]
