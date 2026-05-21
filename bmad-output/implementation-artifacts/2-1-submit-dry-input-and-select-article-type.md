# Story 2.1: Submit Dry Input and Select Article Type

Status: done

## Story

As an operator,
I want to submit Dry Input and select BP, LP or GP,
so that the pipeline can start with the correct article type and source material.

## Acceptance Criteria

1. Given the Streamlit shell is running, when I submit non-empty Dry Input and select an Article Type, then the job stores Dry Input and selected Article Type in `input.json`.
2. Empty input is rejected with a controlled UI error state.
3. The stage timeline records `input_received`.
4. FR1 and FR2 are covered.

## Scope Clarification

- This story formalizes the content intake behavior that started in Story 1.4. Do not implement SEO brief generation, article type inference, LangGraph execution, LLM calls or content generation here.
- Article Type selection is explicit for this story: `BP`, `LP`, or `GP`. Inference remains out of scope unless a later story adds it.
- Artifact files remain the source of truth. Streamlit Session State may store UI state and the latest `CreateJobResult` only.
- Keep `app.py` thin: it may call `JobService` and UI helpers, but must not import config, artifact store, graph nodes, prompts, validators or provider implementations directly.

## Tasks / Subtasks

- [x] Strengthen intake persistence tests (AC: 1, 3, 4)
  - [x] Verify `JobService.create_job()` trims Dry Input before persistence.
  - [x] Verify all selected `ArticleType` values (`BP`, `LP`, `GP`) persist correctly in `input.json`, `metadata.json`, and `state.json`.
  - [x] Verify `state.json` includes `current_stage=input_received` and status history records `input_received`.

- [x] Strengthen UI-controlled error and form behavior (AC: 1, 2)
  - [x] Ensure empty or whitespace-only input displays a controlled Streamlit error through `app.py`.
  - [x] Ensure the UI form exposes Dry Input, Article Type selector, demo/full mode selector and job creation action without adding generation behavior.
  - [x] Add focused tests for pure form/submission helpers where feasible; avoid brittle Streamlit server tests unless they add real value.

- [x] Preserve status timeline behavior (AC: 3)
  - [x] Ensure `build_initial_stage_views()` uses the job metadata current stage/status and exposes `WorkflowStage.INPUT_RECEIVED`.
  - [x] Ensure `test_status_presenter.py` checks `input_received` stage and artifact links.

- [x] Run verification and update story record (AC: 1-4)
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Start Streamlit locally and smoke-check intake submission if code changed in UI/app paths.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 1.4 implemented the first Streamlit shell with Dry Input, Article Type selector, demo/full mode selector and job creation button.
- Story 1.4 code review moved `stage_view_builder` behind a UI helper so `app.py` stays within the UI/service boundary.
- `JobService.create_job()` already persists `metadata.json`, `input.json`, and `state.json` through `ArtifactStore`.
- Existing tests cover one article type (`LP`) and empty input rejection at the service layer; Story 2.1 should broaden this to full BP/LP/GP intake coverage and timeline evidence.

### Architecture Requirements

- FR1: operator can submit Dry Input for a new content job; system accepts plain text input, rejects empty input, and stores original Dry Input as part of the job record.
- FR2: operator can select `BP`, `LP`, or `GP`; optional inference is not required for this story.
- Streamlit is a thin UI layer. Business logic belongs in services or pure helpers.
- `JobService` is the facade between Streamlit and workflow execution.
- `ArtifactStore` is the only layer that reads/writes artifacts.
- `input.json`, `metadata.json`, and `state.json` are structured JSON artifacts and should serialize enum values as strings.

### Implementation Guidance

- Prefer improving tests first. If the current implementation already satisfies an AC, keep the code unchanged and document that the test now guards it.
- Do not add new dependencies.
- Do not make Copyleaks, OpenAI, LangGraph, or provider code part of this story.
- Keep Streamlit text concise and operational; this is a local portfolio tool, not a landing page.

### Testing Requirements

- `test_job_service.py`: full BP/LP/GP persistence, trimmed dry input, empty input rejection, status history includes `input_received`.
- `test_status_presenter.py`: initial `StageView` list includes `WorkflowStage.INPUT_RECEIVED` and links to metadata/input/state artifacts.
- `test_architecture_boundaries.py`: existing app import restrictions remain green.
- Existing tests must keep passing.

## References

- [Epics: Story 2.1 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: Streamlit UI and data flow](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 1.4 completed Streamlit shell](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/1-4-build-minimal-streamlit-shell-and-status-timeline.md)
- [Story 1.3 completed JobService skeleton](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/1-3-implement-config-artifactstore-and-jobservice-skeleton.md)

## Story Context Quality Review

- Critical issues found: 0.
- Enhancements applied: scoped out article type inference and brief generation, broadened test guidance for all article types and status history.
- Optimization applied: story focuses on locking down already-visible intake behavior before moving to brief generation.

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_job_service.py tests/test_app_shell.py tests/test_status_presenter.py` passed: 8 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 28 tests.
- Streamlit smoke-check was not rerun because Story 2.1 changed tests only; UI/app implementation remained unchanged from the Story 1.4 verified shell.
- Code review verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 28 tests.
- Code review verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.

### Completion Notes List

- Added BP/LP/GP intake persistence coverage for `input.json`, `metadata.json`, and `state.json`.
- Added test coverage for trimmed Dry Input persistence.
- Added test coverage that `state.json` status history records `input_received`.
- Added static app-shell test proving empty input is handled through controlled `st.error` rendering.

### File List

- Content_MultiAgent/tests/test_app_shell.py
- Content_MultiAgent/tests/test_job_service.py

## Change Log

- 2026-05-20: Locked down Story 2.1 intake behavior with tests; status moved to review.
- 2026-05-21: Code review clean; status moved to done.
