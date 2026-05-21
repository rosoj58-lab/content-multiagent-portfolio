"""Build UI-ready workflow stage views."""

from seo_content_pipeline.models import (
    ArtifactKey,
    JobMetadata,
    QAReport,
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


def build_brief_qa_stage_view(report: QAReport) -> StageView:
    """Build UI-ready state for brief QA results."""
    if report.passed:
        return StageView(
            stage=WorkflowStage.BRIEF_DRAFTED,
            status=WorkflowStatus.WAITING_FOR_HUMAN,
            label="Brief QA",
            description="Brief QA passed and is waiting for manual approval.",
            artifact_links=[ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA],
            available_actions=["Approve brief", "Request revision"],
        )

    fields = _failed_fields(report)
    field_list = ", ".join(fields) if fields else "brief"
    return StageView(
        stage=WorkflowStage.BRIEF_DRAFTED,
        status=WorkflowStatus.NEEDS_REVISION,
        label="Brief QA",
        description="Brief QA found missing or weak fields.",
        artifact_links=[ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA],
        available_actions=["Regenerate SEO brief"],
        blocking_reason=f"Fix these fields before writing: {field_list}.",
    )


def _failed_fields(report: QAReport) -> list[str]:
    fields: list[str] = []
    for check in report.checks:
        field = check.metadata.get("field")
        if not check.passed and isinstance(field, str) and field not in fields:
            fields.append(field)
    return fields
