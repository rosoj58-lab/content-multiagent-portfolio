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


def build_pipeline_stage_views(
    state,
    *,
    max_revision_attempts: int = 2,
) -> list[StageView]:
    """Build a full pipeline timeline from persisted state."""
    stage_specs = [
        (
            WorkflowStage.INPUT_RECEIVED,
            "Input received",
            "Dry input and selected article type are persisted.",
            [ArtifactKey.METADATA, ArtifactKey.INPUT, ArtifactKey.STATE],
            ["Create SEO brief"],
        ),
        (
            WorkflowStage.BRIEF_DRAFTED,
            "SEO brief",
            "SEO brief is generated, validated and approved before writing.",
            [ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA],
            ["Review brief", "Approve brief"],
        ),
        (
            WorkflowStage.WRITING,
            "English original",
            "English source article is generated and checked deterministically.",
            [ArtifactKey.ENGLISH_ORIGINAL, ArtifactKey.ARTICLE_VALIDATION],
            ["Run editorial QA"],
        ),
        (
            WorkflowStage.EDITORIAL_REVIEW,
            "Editorial QA",
            "Editorial review checks structure, claims and revision guidance.",
            [ArtifactKey.EDITORIAL_QA],
            ["Run SEO QA"],
        ),
        (
            WorkflowStage.SEO_QA,
            "SEO QA",
            "SEO QA checks keyword coverage, heading intent and routing.",
            [ArtifactKey.SEO_QA],
            ["Revise English Original", "Continue to uniqueness"],
        ),
        (
            WorkflowStage.UNIQUENESS_CHECK,
            "Uniqueness",
            "Uniqueness score gates localization.",
            [ArtifactKey.UNIQUENESS],
            ["Enter score", "Continue to localization"],
        ),
        (
            WorkflowStage.LOCALIZATION,
            "Localization",
            "Spanish, Italian and French localizations are generated.",
            [
                ArtifactKey.LOCALIZATION_ES,
                ArtifactKey.LOCALIZATION_IT,
                ArtifactKey.LOCALIZATION_FR,
            ],
            ["Assemble final package"],
        ),
        (
            WorkflowStage.FINAL_QA,
            "Final package and QA",
            "Final Markdown/JSON package and readiness report are produced.",
            [
                ArtifactKey.FINAL_PACKAGE_MD,
                ArtifactKey.FINAL_PACKAGE_JSON,
                ArtifactKey.FINAL_QA_REPORT,
            ],
            ["Download final package"],
        ),
    ]
    stage_order = {stage: index for index, stage in enumerate(WorkflowStage)}
    current_index = stage_order[state.current_stage]
    views: list[StageView] = []

    for stage, label, description, artifact_keys, actions in stage_specs:
        stage_index = stage_order[stage]
        if stage is state.current_stage:
            status = state.status
        elif stage_index < current_index:
            status = WorkflowStatus.APPROVED
        else:
            status = WorkflowStatus.WAITING_FOR_HUMAN

        artifact_links = [
            artifact_key for artifact_key in artifact_keys if artifact_key in state.artifact_paths
        ]
        revision_attempt = state.revision_attempts.get(stage, 0)
        revision_notes = state.revision_notes.get(stage, [])
        blocking_reason = (
            revision_notes[-1]
            if revision_notes
            and stage is state.current_stage
            and status in {WorkflowStatus.NEEDS_REVISION, WorkflowStatus.NEEDS_HUMAN_REVIEW}
            else None
        )

        available_actions = actions if stage is state.current_stage and status is not WorkflowStatus.APPROVED else []

        views.append(
            StageView(
                stage=stage,
                status=status,
                label=label,
                description=description,
                artifact_links=artifact_links,
                available_actions=available_actions,
                blocking_reason=blocking_reason,
                revision_attempt=revision_attempt,
                max_revision_attempts=max_revision_attempts,
            )
        )

    return views


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


def build_brief_manual_gate_stage_view(
    *,
    revision_attempt: int,
    max_revision_attempts: int,
) -> StageView:
    """Build UI-ready state for the brief approval manual gate."""
    return StageView(
        stage=WorkflowStage.BRIEF_DRAFTED,
        status=WorkflowStatus.WAITING_FOR_HUMAN,
        label="Brief approval",
        description="Next action: approve the brief to enable writing, or request a targeted revision.",
        artifact_links=[ArtifactKey.BRIEF, ArtifactKey.BRIEF_QA],
        available_actions=["Approve brief", "Request revision"],
        blocking_reason="Brief QA passed. Human approval is required before writing.",
        revision_attempt=revision_attempt,
        max_revision_attempts=max_revision_attempts,
    )


def build_uniqueness_provider_stage_view(
    *,
    available_provider_names: list[str],
    has_copyleaks_config: bool,
) -> StageView:
    """Build UI-ready state for uniqueness provider selection."""
    actions = [
        f"Select {provider_name} provider"
        for provider_name in available_provider_names
        if provider_name in {"manual", "mock", "copyleaks"}
    ]
    description = "Choose how the English Original uniqueness score will be supplied."
    if not has_copyleaks_config:
        description += " Copyleaks is optional and currently unavailable."

    return StageView(
        stage=WorkflowStage.UNIQUENESS_CHECK,
        status=WorkflowStatus.WAITING_FOR_HUMAN,
        label="Uniqueness provider",
        description=description,
        artifact_links=[ArtifactKey.ENGLISH_ORIGINAL, ArtifactKey.SEO_QA, ArtifactKey.STATE],
        available_actions=actions,
        blocking_reason="Select a uniqueness provider before entering a score.",
    )


def build_uniqueness_gate_stage_view(
    *,
    score: float,
    source: str,
    threshold: float,
    passed: bool,
    routing_reason: str,
) -> StageView:
    """Build UI-ready state for the uniqueness threshold gate."""
    status = WorkflowStatus.RUNNING if passed else WorkflowStatus.NEEDS_REVISION
    return StageView(
        stage=WorkflowStage.UNIQUENESS_CHECK,
        status=status,
        label="Uniqueness gate",
        description=(
            f"Score: {score:g}. Source: {source}. Threshold: {threshold:g}. "
            f"{routing_reason}"
        ),
        artifact_links=[ArtifactKey.UNIQUENESS, ArtifactKey.ENGLISH_ORIGINAL],
        available_actions=["Continue to localization"] if passed else ["Revise English Original"],
        blocking_reason=None if passed else routing_reason,
    )


def _failed_fields(report: QAReport) -> list[str]:
    fields: list[str] = []
    for check in report.checks:
        field = check.metadata.get("field")
        if not check.passed and isinstance(field, str) and field not in fields:
            fields.append(field)
    return fields
