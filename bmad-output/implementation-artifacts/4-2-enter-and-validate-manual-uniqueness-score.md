# Story 4.2: Enter and Validate Manual Uniqueness Score

Status: ready-for-dev

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

- [ ] Implement uniqueness score model and validator (AC: 1, 2, 3, 5)
  - [ ] Add a persisted `UniquenessResult` Pydantic model.
  - [ ] Include `job_id`, stage, score, source, provider metadata and timestamp.
  - [ ] Add deterministic score validation for numeric values from 0 to 100.
  - [ ] Reject non-numeric, boolean and out-of-range values.

- [ ] Implement manual score orchestration (AC: 1, 2, 3, 4)
  - [ ] Add a service method to record manual uniqueness score.
  - [ ] Require `selected_uniqueness_provider == "manual"` before accepting manual score.
  - [ ] Save `uniqueness.json` through `ArtifactStore`.
  - [ ] Update `state.json` with artifact path and score-recorded flag.
  - [ ] Update `metadata.json` status/history for the uniqueness stage.
  - [ ] Clear the manual gate after a valid score is recorded.

- [ ] Add graph/UI-facing support (AC: 1, 3)
  - [ ] Add uniqueness node wrapper for manual score recording.
  - [ ] Keep Streamlit entrypoint thin; no direct provider/service implementation imports from `app.py`.
  - [ ] Ensure controlled service errors can be rendered by UI later.

- [ ] Add focused tests (AC: 1-5)
  - [ ] Test valid scores at 0, 90 and 100 are accepted.
  - [ ] Test invalid scores below 0, above 100, booleans and strings are rejected.
  - [ ] Test `uniqueness.json` contains score, source `manual`, provider metadata and timestamp.
  - [ ] Test manual score cannot be recorded unless manual provider is selected.
  - [ ] Run full `pytest` and `ruff check .`.

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

### Completion Notes List

- Pending implementation.

### File List

- Pending implementation.

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
