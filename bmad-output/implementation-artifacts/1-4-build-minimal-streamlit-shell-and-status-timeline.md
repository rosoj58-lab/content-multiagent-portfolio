# Story 1.4: Build Minimal Streamlit Shell and Status Timeline

Status: done

## Story

As an operator,
I want to launch a local Streamlit app and see a basic job status timeline,
so that the project is demonstrably runnable before content generation exists.

## Acceptance Criteria

1. Given the scaffold and `JobService` skeleton exist, when I run `uv run streamlit run app.py`, then the app opens with a dry input form, article type selector, demo/full mode selector and job creation action.
2. After job creation the UI renders a `StageView`-based timeline.
3. `app.py` imports only UI helpers, public models and `JobService`.
4. `test_architecture_boundaries.py` verifies UI import boundaries.
5. `test_status_presenter.py` verifies `StageView` rendering data.

## Scope Clarification

- Implement a minimal runnable shell only. Do not implement SEO brief generation, graph execution, LLM calls, provider selection, uniqueness checks or content stages.
- Streamlit Session State may store only UI interaction state such as the current job result. Artifact files remain the source of truth.
- Keep business logic out of `app.py`; app code should call `JobService` and UI helpers only.
- Treat `/Users/irinawork/bmad_projects/Content_MultiAgent` as the application root and `/Users/irinawork/bmad_projects` as the Git/Compose root.

## Tasks / Subtasks

- [x] Build UI-ready status presenter data (AC: 2, 5)
  - [x] Replace `services/stage_view_builder.py` placeholder with a pure function that converts `JobMetadata` or initial job state into `list[StageView]`.
  - [x] Include at least the initial `WorkflowStage.INPUT_RECEIVED` view with status, label, description, artifact links and available actions.
  - [x] Add `tests/test_status_presenter.py` covering the initial timeline data and ensuring it uses `StageView`.

- [x] Build minimal Streamlit UI helpers (AC: 1, 2)
  - [x] Replace placeholders in `ui/components.py` and `ui/progress_timeline.py` as needed.
  - [x] Render dry input text area, article type selector, demo/full mode selector and job creation button.
  - [x] Render a readable timeline from `list[StageView]`.
  - [x] Keep UI helper functions thin; they may import Streamlit and public models but not graph nodes, prompts, validators or provider implementations.

- [x] Update `app.py` shell (AC: 1, 2, 3)
  - [x] `app.py` should set page config and call UI/service helpers.
  - [x] `app.py` may import `JobService`, public models, and UI helpers only.
  - [x] On create action, call `JobService.create_job()` and store only UI state/result references in Streamlit session state.
  - [x] Show created job ID and artifact paths after job creation.
  - [x] Display a controlled validation error for empty dry input; do not expose raw tracebacks as the primary UI.

- [x] Strengthen boundary and regression tests (AC: 3, 4, 5)
  - [x] Update `test_architecture_boundaries.py` so `app.py` cannot import `config`, `ArtifactStore`, graph nodes, prompts, validators or provider implementations directly.
  - [x] Add tests for `stage_view_builder.py` and any pure UI data helpers.
  - [x] Run full `pytest` and `ruff check .`.

- [x] Run the app locally for manual verification (AC: 1, 2)
  - [x] Start Streamlit with local `uv` after implementation.
  - [x] Confirm the server starts and provide the local URL.
  - [x] Stop the server before finalizing unless the user explicitly wants it left running.

### Review Findings

- [x] [Review][Patch] Keep `stage_view_builder` behind a UI helper instead of importing it in `app.py` [Content_MultiAgent/app.py:6] — resolved by moving the builder call behind `render_initial_progress_timeline()` in `ui.progress_timeline` and forbidding direct `app.py` imports from `services.stage_view_builder`.

## Dev Notes

### Current Repository State

- Story 1.3 completed `JobService.create_job()`, `ArtifactStore`, and `AppSettings`.
- `JobService.create_job()` currently returns `CreateJobResult` with `metadata` and paths for `metadata`, `input`, and `state`.
- `services/stage_view_builder.py`, `ui/components.py`, and `ui/progress_timeline.py` are placeholders.
- `app.py` currently renders only a scaffold title and message.

### Architecture Requirements

- Streamlit is a thin UI layer; business logic remains in services and pure helpers.
- `app.py` calls `JobService` and UI helpers only.
- `app.py` must not import graph nodes, prompts, validators, provider implementations, `config.py`, or `ArtifactStore`.
- `StageView` is what Streamlit renders for timeline entries, manual gates and failure states.
- UI reads from `JobService`, artifact store and `StageView`, then renders status timeline, QA summaries, artifact previews and manual gates over time. This story implements only the initial status timeline.
- Session State is for UI interaction state only, not the source of truth for artifacts.

### Implementation Guidance

- Use existing public models from `seo_content_pipeline.models`: `ArticleType`, `ArtifactKey`, `JobMetadata`, `StageView`, `WorkflowStage`, `WorkflowStatus`.
- `stage_view_builder.py` should be testable without Streamlit.
- A minimal first timeline can show:
  - `Input received`
  - status `running`
  - artifact links: metadata, input, state
  - next action: `Continue to SEO brief generation` or equivalent placeholder action for future Story 2.2.
- The demo/full selector can be persisted in session state for now; no backend behavior is required in this story.
- Do not add custom CSS-heavy design. Keep Streamlit controls predictable and work-focused.

### Testing Requirements

- `test_status_presenter.py`: builds `StageView` list from a created job and checks stage, status, labels, artifact links and available actions.
- `test_architecture_boundaries.py`: app import restrictions include no direct config/artifact store imports.
- Existing tests must keep passing.

## References

- [Architecture: Streamlit UI and StageView patterns](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Architecture: app.py and UI boundaries](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Epics: Story 1.4 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Story 1.3 completed JobService skeleton](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/1-3-implement-config-artifactstore-and-jobservice-skeleton.md)

## Story Context Quality Review

- Critical issues found: 0.
- Enhancements applied: clarified session state boundary, direct import restrictions and manual Streamlit verification requirement.
- Optimization applied: isolated pure status presenter work from Streamlit rendering so tests remain fast.

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_status_presenter.py tests/test_architecture_boundaries.py` passed: 3 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 24 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- Streamlit smoke-check started at `http://127.0.0.1:8501`; browser verification created a job and displayed artifact paths plus `StageView` timeline.
- Post-review patch verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_architecture_boundaries.py tests/test_status_presenter.py` passed: 3 tests.
- Post-review patch verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 24 tests.
- Post-review patch verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.

### Completion Notes List

- Implemented `build_initial_stage_views()` as a pure `StageView` builder for the initial job shell timeline.
- Implemented Streamlit UI helpers for dry input, article type, demo/full mode, job summary and progress timeline.
- Updated `app.py` to create a job through `JobService`, store UI result state and render a basic timeline without importing lower-level implementation layers.
- Strengthened architecture boundary tests and added status presenter tests.
- Resolved code review finding by keeping `stage_view_builder` behind a UI rendering helper.

### File List

- Content_MultiAgent/app.py
- Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py
- Content_MultiAgent/src/seo_content_pipeline/ui/components.py
- Content_MultiAgent/src/seo_content_pipeline/ui/progress_timeline.py
- Content_MultiAgent/tests/test_architecture_boundaries.py
- Content_MultiAgent/tests/test_status_presenter.py

## Change Log

- 2026-05-20: Implemented Story 1.4 minimal Streamlit shell and status timeline; status moved to review.
- 2026-05-20: Resolved Story 1.4 code review finding; status moved to done.
