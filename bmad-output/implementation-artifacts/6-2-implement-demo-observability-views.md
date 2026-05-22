# Story 6.2: Implement Demo Observability Views

Status: review

## Story

As an operator,
I want to see progress timeline, artifact panel, QA checklist and controlled error states,
so that I can explain the pipeline clearly in an interview.

## Acceptance Criteria

1. Given one or more demo jobs exist, when I open the Streamlit app, then I can see stage progress.
2. I can see artifact previews and download actions.
3. I can see QA summaries and revision attempt counters.
4. Controlled failure states explain what failed and what action is available.
5. Raw tracebacks are not the primary user-facing error experience.
6. UX-DR1 through UX-DR5 are covered.

## Scope Clarification

- This story adds demo observability surfaces for the current job in the local Streamlit app.
- This story does not implement a full historical job browser.
- This story does not add new pipeline generation steps.
- UI polish should be practical and stable; deeper interview docs belong to Story 6.3.

## Tasks / Subtasks

- [x] Implement stage observability model (AC: 1, 3)
  - [x] Build stage views from persisted `PipelineState`.
  - [x] Include progress labels, stage statuses and artifact links.
  - [x] Include revision attempt counters where present.
  - [x] Keep existing initial timeline behavior compatible.

- [x] Implement artifact panel and downloads (AC: 2)
  - [x] Build artifact previews from `ArtifactStore`.
  - [x] Support JSON and Markdown previews.
  - [x] Expose download actions for existing artifacts.

- [x] Implement QA summary helpers (AC: 3)
  - [x] Build checklist items from `QAReport`.
  - [x] Render pass/fail summaries without raw model dumps.

- [x] Implement controlled error states (AC: 4, 5)
  - [x] Add reusable controlled error presenter.
  - [x] Update `app.py` to show controlled recovery guidance for observability errors.
  - [x] Avoid exposing raw tracebacks as the primary UI state.

- [x] Add focused tests (AC: 1-6)
  - [x] Test pipeline stage views include stage progress and revision counters.
  - [x] Test artifact preview builder handles JSON and Markdown.
  - [x] Test artifact panel render code exposes download actions.
  - [x] Test QA checklist helper maps passed and failed checks.
  - [x] Test controlled error helper exposes user action.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- `progress_timeline.py` renders `StageView` objects and currently supports initial job timeline.
- `stage_view_builder.py` has initial, brief QA, manual gate and uniqueness stage view helpers.
- `artifact_panel.py`, `renderers.py`, `error_presenter.py` and `empty_states.py` are placeholders.
- `app.py` creates a job shell and renders only job summary plus initial progress timeline.

### Architecture Requirements

- UX-DR1: progress timeline.
- UX-DR2: QA summaries.
- UX-DR3: manual gates and revision actions.
- UX-DR4: controlled failure states.
- UX-DR5: artifact previews and download actions.
- Story 6.2 should be screenshot-reviewable later, but unit tests should cover the core view contracts now.

### Implementation Guidance

- Keep business logic out of Streamlit render functions where possible.
- Prefer pure builders for tests, then thin Streamlit render wrappers.
- Use existing `StageView`, `ArtifactStore`, `QAReport`, `PipelineState`, `ArtifactKey` contracts.
- Do not introduce a frontend framework beyond Streamlit.
- Keep cards restrained; operational UI should be dense and inspectable.

### Testing Requirements

- Add focused tests for pure observability builders.
- Use AST tests only where Streamlit UI calls are otherwise hard to assert.
- Existing tests must keep passing.

## References

- [Epics: Story 6.2 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: UI observability requirements](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 6.1 demo inputs](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/6-1-add-stable-bp-lp-and-gp-demo-inputs.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 6, current Streamlit UI modules and StageView builder state.
- Started implementation; status moved to in-progress.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_demo_observability.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_demo_observability.py` passed: 5 tests.
- Architecture and app shell regressions were caught and patched by routing stage view builder access through the UI layer and updating the app shell controlled-error assertion.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 128 tests.

### Completion Notes List

- Added full pipeline stage view builder from persisted `PipelineState`.
- Added artifact preview and download panel for JSON and Markdown artifacts.
- Added QA checklist and summary render helpers.
- Added controlled error presenter and no-job empty state.
- Updated `app.py` to render persisted progress, artifacts and controlled observability errors.
- Added focused demo observability tests.

### File List

- Content_MultiAgent/app.py
- Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py
- Content_MultiAgent/src/seo_content_pipeline/ui/artifact_panel.py
- Content_MultiAgent/src/seo_content_pipeline/ui/empty_states.py
- Content_MultiAgent/src/seo_content_pipeline/ui/error_presenter.py
- Content_MultiAgent/src/seo_content_pipeline/ui/progress_timeline.py
- Content_MultiAgent/src/seo_content_pipeline/ui/renderers.py
- Content_MultiAgent/tests/test_app_shell.py
- Content_MultiAgent/tests/test_demo_observability.py

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
- 2026-05-22: Started implementation; status moved to in-progress.
- 2026-05-22: Implemented demo observability views; status moved to review.
