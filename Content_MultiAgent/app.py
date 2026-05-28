"""Streamlit entrypoint for the SEO Content Pipeline."""

import streamlit as st

from seo_content_pipeline.models import ArtifactKey, PipelineState, WorkflowStage, WorkflowStatus
from seo_content_pipeline.services.demo_pipeline_service import (
    DEFAULT_LP_CORRECTION_STATEMENT,
    DemoPipelineService,
)
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services.job_history_service import JobHistoryService
from seo_content_pipeline.services.live_brief_service import LiveBriefService
from seo_content_pipeline.ui.artifact_panel import render_artifact_panel
from seo_content_pipeline.ui.components import (
    render_job_creation_form,
    render_job_summary,
    render_live_brief_action,
    render_lp_correction_form,
)
from seo_content_pipeline.ui.empty_states import render_no_job_empty_state
from seo_content_pipeline.ui.error_presenter import build_controlled_error, render_controlled_error
from seo_content_pipeline.ui.job_history import render_recent_job_picker
from seo_content_pipeline.ui.progress_timeline import render_pipeline_progress_timeline
from seo_content_pipeline.ui.qa_scorecard import (
    build_decision_scorecard,
    can_apply_lp_revision,
    render_decision_scorecard,
)
from seo_content_pipeline.ui.revision_comparison import (
    build_revision_comparison,
    render_revision_comparison,
)


def main() -> None:
    """Render the local portfolio app shell."""
    st.set_page_config(page_title="SEO Content Pipeline", layout="wide")
    st.title("SEO Content Pipeline")

    service = JobService()
    history_service = JobHistoryService(
        settings=service.settings,
        artifact_store=service.artifact_store,
    )
    try:
        selected_job_id = render_recent_job_picker(history_service.list_recent_jobs())
        if selected_job_id is not None:
            st.session_state["current_job_result"] = history_service.load_job(selected_job_id)
            st.session_state["demo_mode"] = "loaded"
    except Exception as error:
        render_controlled_error(
            build_controlled_error(error, action="Refresh recent jobs or create a new job.")
        )

    submission = render_job_creation_form()

    if submission is not None:
        try:
            result = service.create_job(submission.dry_input, submission.article_type)
        except ValueError as error:
            render_controlled_error(
                build_controlled_error(error, action="Paste a demo input and try again.")
            )
        else:
            st.session_state["current_job_result"] = result
            st.session_state["demo_mode"] = submission.demo_mode

    result = st.session_state.get("current_job_result")
    if result is None:
        render_no_job_empty_state()
        return

    artifact_paths = {key.value: path for key, path in result.artifact_paths.items()}
    render_job_summary(result.metadata.job_id, artifact_paths, st.session_state.get("demo_mode", "demo"))
    revision_confirmation = st.session_state.pop("revision_confirmation", None)
    if revision_confirmation:
        st.success(f"Revision applied: {revision_confirmation['status']}")
        st.caption(f"Final package: {revision_confirmation['final_package_path']}")
    try:
        action_state = PipelineState.model_validate(
            service.artifact_store.read_json(result.metadata.job_id, ArtifactKey.STATE)
        )
        can_start_generation = (
            action_state.current_stage is WorkflowStage.INPUT_RECEIVED
            and action_state.status is WorkflowStatus.RUNNING
        )
        if can_start_generation and st.button("Run demo scenario", type="secondary"):
            try:
                demo_result = DemoPipelineService(
                    settings=service.settings,
                    artifact_store=service.artifact_store,
                ).run_demo_scenario(
                    result.metadata.job_id,
                    mode=st.session_state.get("demo_mode", "demo"),
                )
            except Exception as error:
                render_controlled_error(
                    build_controlled_error(
                        error,
                        action="Recreate the job from a stable demo input and run the demo again.",
                    )
                )
            else:
                if demo_result.status.value == "approved":
                    st.success(f"Demo scenario complete: {demo_result.status.value}")
                else:
                    st.warning(f"Demo scenario complete: {demo_result.status.value}")
                st.caption(f"Decision artifact: {demo_result.decision_artifact_path}")
                if demo_result.final_package_path:
                    st.caption(f"Final package: {demo_result.final_package_path}")
                can_start_generation = False
        live_service = LiveBriefService(
            settings=service.settings,
            artifact_store=service.artifact_store,
        )
        if can_start_generation and render_live_brief_action(
            configured=live_service.is_configured,
            model=service.settings.openai_model,
        ):
            try:
                live_result = live_service.generate_live_brief(result.metadata.job_id)
            except Exception as error:
                render_controlled_error(
                    build_controlled_error(
                        error,
                        action="Check OPENAI_API_KEY and OPENAI_MODEL locally, then try again.",
                    )
                )
            else:
                if live_result.status is WorkflowStatus.WAITING_FOR_HUMAN:
                    st.success(f"Live SEO brief complete: {live_result.status.value}")
                else:
                    st.warning(f"Live SEO brief stopped: {live_result.status.value}")
                st.caption("Live action scope: SEO brief generation and deterministic brief QA only.")
    except Exception as error:
        render_controlled_error(
            build_controlled_error(
                error,
                action="Refresh the job or recreate it from a stable demo input.",
            )
        )
    try:
        state = PipelineState.model_validate(
            service.artifact_store.read_json(result.metadata.job_id, ArtifactKey.STATE)
        )
        if can_apply_lp_revision(state):
            correction_statement = render_lp_correction_form(DEFAULT_LP_CORRECTION_STATEMENT)
            if correction_statement is not None:
                try:
                    revision_result = DemoPipelineService(
                        settings=service.settings,
                        artifact_store=service.artifact_store,
                    ).apply_lp_editorial_revision(
                        result.metadata.job_id,
                        correction_statement,
                        mode=st.session_state.get("demo_mode", "demo"),
                    )
                except ValueError as error:
                    render_controlled_error(
                        build_controlled_error(
                            error,
                            action="Use wording without numbers or promotional result promises, then submit again.",
                        )
                    )
                else:
                    st.session_state["revision_confirmation"] = {
                        "status": revision_result.status.value,
                        "final_package_path": revision_result.final_package_path,
                    }
                    st.rerun()
        scorecard = build_decision_scorecard(result.metadata.job_id, service.artifact_store)
        if scorecard is not None:
            render_decision_scorecard(scorecard)
        comparison = build_revision_comparison(result.metadata.job_id, service.artifact_store)
        if comparison is not None:
            render_revision_comparison(comparison)
        render_pipeline_progress_timeline(state)
        render_artifact_panel(result.metadata.job_id, service.artifact_store)
    except Exception as error:
        render_controlled_error(
            build_controlled_error(
                error,
                action="Refresh the job or recreate it from a stable demo input.",
            )
        )


if __name__ == "__main__":
    main()
