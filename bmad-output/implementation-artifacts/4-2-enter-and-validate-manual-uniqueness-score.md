# Story 4.2: Enter and Validate Manual Uniqueness Score

Status: review

## Story

As an operator,
I want to enter a manual uniqueness score from an external checker,
so that the system can gate localization honestly.

## Acceptance Criteria

1. Given manual uniqueness provider is selected, when I enter a score from 0 to 100, then `uniqueness.json` records the score.
2. `uniqueness.json` records source `manual`, provider metadata and timestamp.
3. Invalid values are rejected with a controlled UI/service error.
4. The system does not invent or simulate manual scores.
5. FR9 is covered.

## Scope Clarification

- This story implements manual score recording only.
- This story must not implement the 90 percent pass/fail gate; Story 4.3 owns threshold routing.
- This story must not call external plagiarism APIs and must not create a fake manual score.
- Manual score entry is valid only after Story 4.1 has selected `manual` as the uniqueness provider.

## Tasks / Subtasks

- [x] Implement uniqueness score model and validator (AC: 1, 2, 3, 5)
  - [x] Add a persisted `UniquenessResult` Pydantic model.
  - [x] Include `job_id`, stage, score, source, provider metadata and timestamp.
  - [x] Add deterministic score validation for numeric values from 0 to 100.
  - [x] Reject non-numeric, boolean and out-of-range values.

- [x] Implement manual score orchestration (AC: 1, 2, 3, 4)
  - [x] Add a service method to record manual uniqueness score.
  - [x] Require `selected_uniqueness_provider == "manual"` before accepting manual score.
  - [x] Save `uniqueness.json` through `ArtifactStore`.
  - [x] Update `state.json` with artifact path and score-recorded flag.
  - [x] Update `metadata.json` status/history for the uniqueness stage.
  - [x] Clear the manual gate after a valid score is recorded.

- [x] Add graph/UI-facing support (AC: 1, 3)
  - [x] Add uniqueness node wrapper for manual score recording.
  - [x] Keep Streamlit entrypoint thin; no direct provider/service implementation imports from `app.py`.
  - [x] Ensure controlled service errors can be rendered by UI later.

- [x] Add focused tests (AC: 1-5)
  - [x] Test valid scores at 0, 90 and 100 are accepted.
  - [x] Test invalid scores below 0, above 100, booleans and strings are rejected.
  - [x] Test `uniqueness.json` contains score, source `manual`, provider metadata and timestamp.
  - [x] Test manual score cannot be recorded unless manual provider is selected.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- Story 4.1 added `selected_uniqueness_provider` to `PipelineState`.
- Story 4.1 added `UniquenessProviderService.select_provider()` and persists `manual_gate_required=True` during provider selection.
- `ArtifactKey.UNIQUENESS` already maps to `uniqueness.json`.
- `models/uniqueness.py` currently contains `UniquenessProviderOption`.
- `validators/artifact_validators.py` contains deterministic validators and is the right place for `validate_uniqueness_score`.
- `graph/nodes/uniqueness_node.py` currently wraps provider selection only.

### Architecture Requirements

- FR9: operator can enter a uniqueness score for the English Original; system accepts numeric scores from 0 to 100 and records source as `manual`.
- NFR2: score validation must be deterministic wherever possible.
- Manual uniqueness input must be honest: no invented, simulated or default manual score.
- Workflow evidence must be file-visible in `artifacts/jobs/{job_id}/uniqueness.json`.

### Implementation Guidance

- Use Pydantic models for persisted uniqueness result data.
- Keep service IO behind `ArtifactStore`.
- Prefer `WorkflowStage.UNIQUENESS_CHECK`.
- After a valid score is recorded, keep the job ready for Story 4.3 threshold gating; do not localize yet.
- Use `WorkflowStatus.RUNNING` after score recording and set `manual_gate_required=False`.
- Store provider metadata in the result, for example selected provider and score source.
- Do not add Copyleaks behavior in this story.

### Testing Requirements

- Add or extend `tests/test_uniqueness_providers.py` for manual score service behavior.
- Add pure validator tests where useful.
- Existing tests must keep passing.

## References

- [Epics: Story 4.2 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: validate_uniqueness_score and uniqueness result](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 4.1 completed provider selection](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/4-1-select-manual-or-mock-uniqueness-provider.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 4, architecture, and Story 4.1 implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_uniqueness_providers.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_uniqueness_providers.py` passed: 16 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 97 tests.

### Completion Notes List

- Added `UniquenessResult` with score, source, provider metadata and timestamp.
- Added deterministic `validate_uniqueness_score()` for numeric 0-100 values.
- Added `UniquenessScoreService.record_manual_score()` to require manual provider selection, save `uniqueness.json`, update state/metadata and clear the manual gate.
- Added graph node wrapper for manual score recording.
- Added tests for valid boundaries, invalid values, artifact persistence and provider precondition.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/uniqueness_node.py
- Content_MultiAgent/src/seo_content_pipeline/models/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/models/uniqueness.py
- Content_MultiAgent/src/seo_content_pipeline/services/uniqueness_score_service.py
- Content_MultiAgent/src/seo_content_pipeline/validators/artifact_validators.py
- Content_MultiAgent/tests/test_uniqueness_providers.py

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
- 2026-05-21: Started implementation; status moved to in-progress.
- 2026-05-21: Implemented manual uniqueness score recording; status moved to review.
