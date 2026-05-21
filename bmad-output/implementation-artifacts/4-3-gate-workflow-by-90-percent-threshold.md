# Story 4.3: Gate Workflow by 90 Percent Threshold

Status: ready-for-dev

## Story

As an operator,
I want the workflow to continue only when uniqueness is at least 90,
so that localization uses an approved English Original.

## Acceptance Criteria

1. Given a uniqueness score exists, when the score is `>= 90`, then the workflow routes to localization.
2. When the score is `< 90`, the workflow routes to revision with `needs_revision` status.
3. The UI/status layer shows the score, source, threshold and routing reason.
4. FR11 and FR18 are covered.

## Scope Clarification

- This story implements the threshold gate after `uniqueness.json` exists.
- This story does not generate localization content; Epic 5 owns localization generation.
- For scores below 90, route to targeted writing revision using `WorkflowStage.WRITING`, because there is still no separate rewriter stage enum.
- Threshold must be deterministic and fixed at 90 for this MVP story.

## Tasks / Subtasks

- [ ] Implement uniqueness threshold validation and routing (AC: 1, 2, 4)
  - [ ] Add deterministic threshold validation for `UniquenessResult`.
  - [ ] Treat score `90` as passing.
  - [ ] Route passing scores to `WorkflowStage.LOCALIZATION`.
  - [ ] Route failing scores to `WorkflowStatus.NEEDS_REVISION` with writing/revision target.
  - [ ] Keep routing pure where possible.

- [ ] Implement threshold gate orchestration (AC: 1, 2, 4)
  - [ ] Add service method to read `uniqueness.json` and apply the 90 percent gate.
  - [ ] Update `state.json` and `metadata.json`.
  - [ ] Preserve `ArtifactKey.UNIQUENESS` path.
  - [ ] For pass: set current stage to localization and status running.
  - [ ] For fail: set current stage to uniqueness check and status needs_revision.
  - [ ] Store routing reason and QA flag for later final report/demo.

- [ ] Add UI/status support (AC: 3)
  - [ ] Add stage view helper that shows score, source, threshold and routing reason.
  - [ ] Include relevant artifact links.
  - [ ] Expose revision action for below-threshold scores.

- [ ] Add focused tests (AC: 1-4)
  - [ ] Test score `90` passes and routes to localization.
  - [ ] Test score `100` passes and routes to localization.
  - [ ] Test score below `90` routes to needs_revision.
  - [ ] Test stage view includes score, source, threshold and routing reason.
  - [ ] Test missing uniqueness artifact is rejected with controlled error.
  - [ ] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- Story 4.2 writes `uniqueness.json` as `UniquenessResult`.
- `UniquenessResult.score` is a float from 0 to 100 and `source` is currently `manual`.
- Story 4.2 leaves the job at `WorkflowStage.UNIQUENESS_CHECK` with `WorkflowStatus.RUNNING`.
- `graph/routing.py` is currently a placeholder and can host pure routing helpers.
- `stage_view_builder.py` already has provider-selection stage view support.

### Architecture Requirements

- FR11: localization is allowed only when uniqueness score is at least 90.
- FR18: uniqueness below 90 routes to revision.
- Deterministic validators and routing should handle thresholds, not LLMs.
- Status history must record ordered stage/status transitions.

### Implementation Guidance

- Keep threshold as a named constant, e.g. `UNIQUENESS_THRESHOLD = 90.0`.
- Do not overwrite `uniqueness.json`; Story 4.3 should consume it.
- Use `WorkflowStage.LOCALIZATION` for the pass route.
- Use `WorkflowStage.WRITING` as the routing target/revision destination for below-threshold scores.
- Store enough state for the UI/final report to explain the gate: score, source, threshold and routing reason.
- Avoid adding a new artifact unless necessary; state flags/notes are enough for MVP routing evidence.

### Testing Requirements

- Extend `tests/test_uniqueness_providers.py` or add a focused test module for the gate service.
- Extend `tests/test_status_presenter.py` for the uniqueness gate view.
- Existing tests must keep passing.

## References

- [Epics: Story 4.3 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: routing and uniqueness threshold](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 4.2 completed manual score recording](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/4-2-enter-and-validate-manual-uniqueness-score.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 4, architecture routing notes, and Story 4.2 implementation.

### Completion Notes List

- Pending implementation.

### File List

- Pending implementation.

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
