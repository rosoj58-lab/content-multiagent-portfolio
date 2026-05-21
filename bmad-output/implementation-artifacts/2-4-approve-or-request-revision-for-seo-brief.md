# Story 2.4: Approve or Request Revision for SEO Brief

Status: review

## Story

As an operator,
I want to approve or request revision on the generated brief,
so that article writing starts only after human review.

## Acceptance Criteria

1. Given a generated brief and QA report exist, when I approve the brief, then the workflow records `brief_approved`.
2. Approving the brief disables the manual gate and enables the writing stage.
3. Given a generated brief and QA report exist, when I request revision with notes, then the job routes back to brief generation with notes.
4. Revision request increments the previous-attempt counter for the brief revision loop.
5. Manual gate stage data shows reason, available actions, relevant artifact links, previous attempts and next action.
6. Empty revision notes are rejected with a controlled validation error.
7. FR17, FR18 and NFR5 are covered.

## Scope Clarification

- This story implements backend/manual-gate action handling and UI-ready stage data. It does not implement full Streamlit button/form wiring or the article writer.
- “Enables writing stage” means the state records `brief_approved`, manual gate is closed, and the next action points to writing.
- Revision notes are persisted in lightweight workflow state because they are routing/control data, not full content artifacts.
- Revision attempts are bounded by `AppSettings.max_revision_attempts`; exceeding the limit routes to `needs_human_review`.

## Tasks / Subtasks

- [x] Add revision state support (AC: 3, 4, 7)
  - [x] Add persisted revision notes to `PipelineState`.
  - [x] Keep revision attempts keyed by `WorkflowStage.BRIEF_DRAFTED`.

- [x] Implement brief approval/revision service (AC: 1, 2, 3, 4, 6, 7)
  - [x] Validate that `brief.json` and `brief_qa.json` exist.
  - [x] Validate that approval requires a passed QA report and active manual gate.
  - [x] Record `brief_approved` on approval.
  - [x] Disable manual gate on approval.
  - [x] Reject empty revision notes.
  - [x] Persist revision notes and increment attempts on revision request.
  - [x] Route revision limit overflow to controlled `needs_human_review`.

- [x] Expose manual gate `StageView` data (AC: 2, 5)
  - [x] Show stopping reason.
  - [x] Show approve/request-revision actions.
  - [x] Show `brief` and `brief_qa` artifact links.
  - [x] Show previous attempts and max attempts.
  - [x] Show next action after approval.

- [x] Add focused tests (AC: 1-7)
  - [x] Test approve records `brief_approved` and closes manual gate.
  - [x] Test request revision persists notes and increments attempts.
  - [x] Test empty revision notes are rejected.
  - [x] Test revision limit overflow routes to `needs_human_review`.
  - [x] Test manual gate stage view exposes reason/actions/artifacts/attempts/next action.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 2.2 generates `brief.json`.
- Story 2.3 generates `brief_qa.json` and sets passed QA jobs to `waiting_for_human` with `manual_gate_required=True`.
- `PipelineState` already includes `revision_attempts`, `manual_gate_required`, status history and artifact paths.
- `StageView` already supports `available_actions`, `blocking_reason`, `revision_attempt` and `max_revision_attempts`.

### Architecture Requirements

- FR17: status changes must be tracked in order.
- FR18: failed checks and revision requests route back to the appropriate stage.
- NFR5: operator can review and correct key intermediate artifacts before continuing; brief approval remains a manual gate.
- Manual gates must display reason, available actions, relevant artifact links, previous attempts and next action.
- Streamlit remains a thin UI layer; action logic belongs in services.

### Implementation Guidance

- Keep the service deterministic and filesystem-backed through `ArtifactStore`.
- Do not add LangGraph wiring yet; expose small service methods that future graph/UI code can call.
- Store revision notes as state control data under the brief stage.
- Approval should not delete `brief.json` or `brief_qa.json`.

### Testing Requirements

- `tests/test_brief_approval_service.py`: approval, revision, empty notes, revision limit.
- `tests/test_status_presenter.py`: manual gate `StageView` details.
- Existing tests must keep passing.

## References

- [Epics: Story 2.4 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: manual gate pattern](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 2.3 completed brief QA](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/2-3-validate-brief-completeness.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_brief_approval_service.py tests/test_status_presenter.py tests/test_artifact_registry.py` passed: 17 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 50 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.

### Completion Notes List

- Added persisted `PipelineState.revision_notes` for operator revision instructions.
- Added `BriefApprovalService.approve_brief()` to record `brief_approved`, close the manual gate and enable writing.
- Added `BriefApprovalService.request_revision()` to persist notes, increment attempts and route back to brief generation.
- Added revision-limit overflow route to `needs_human_review`.
- Added manual gate `StageView` builder with reason, actions, artifact links, previous attempts and next action.
- Added focused tests for approval, revision, empty notes, revision limit and manual gate view data.

### File List

- Content_MultiAgent/src/seo_content_pipeline/models/job.py
- Content_MultiAgent/src/seo_content_pipeline/services/brief_approval_service.py
- Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py
- Content_MultiAgent/tests/test_artifact_registry.py
- Content_MultiAgent/tests/test_brief_approval_service.py
- Content_MultiAgent/tests/test_status_presenter.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented brief approval and revision gate; status moved to review.
