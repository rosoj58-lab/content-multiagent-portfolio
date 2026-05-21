# Story 4.3: Gate Workflow by 90 Percent Threshold

Status: review

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

- [x] Implement uniqueness threshold validation and routing (AC: 1, 2, 4)
  - [x] Add deterministic threshold validation for `UniquenessResult`.
  - [x] Treat score `90` as passing.
  - [x] Route passing scores to `WorkflowStage.LOCALIZATION`.
  - [x] Route failing scores to `WorkflowStatus.NEEDS_REVISION` with writing/revision target.
  - [x] Keep routing pure where possible.

- [x] Implement threshold gate orchestration (AC: 1, 2, 4)
  - [x] Add service method to read `uniqueness.json` and apply the 90 percent gate.
  - [x] Update `state.json` and `metadata.json`.
  - [x] Preserve `ArtifactKey.UNIQUENESS` path.
  - [x] For pass: set current stage to localization and status running.
  - [x] For fail: set current stage to uniqueness check and status needs_revision.
  - [x] Store routing reason and QA flag for later final report/demo.

- [x] Add UI/status support (AC: 3)
  - [x] Add stage view helper that shows score, source, threshold and routing reason.
  - [x] Include relevant artifact links.
  - [x] Expose revision action for below-threshold scores.

- [x] Add focused tests (AC: 1-4)
  - [x] Test score `90` passes and routes to localization.
  - [x] Test score `100` passes and routes to localization.
  - [x] Test score below `90` routes to needs_revision.
  - [x] Test stage view includes score, source, threshold and routing reason.
  - [x] Test missing uniqueness artifact is rejected with controlled error.
  - [x] Run full `pytest` and `ruff check .`.

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
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_uniqueness_gate_service.py tests/test_status_presenter.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_uniqueness_gate_service.py tests/test_status_presenter.py` passed: 12 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 103 tests.
- Code review finding patched: threshold gate now preserves the `uniqueness.json` artifact path in `state.json`.
- Post-review verification passed: targeted uniqueness/status tests 12/12, `ruff check .`, full `pytest` 103/103.

### Completion Notes List

- Added pure `route_after_uniqueness_gate()` with `UNIQUENESS_THRESHOLD = 90.0`.
- Added `UniquenessGateService.apply_threshold_gate()` to consume `uniqueness.json` and route pass/fail states.
- Added typed uniqueness gate state fields for score, threshold, source and routing reason.
- Added UI-ready uniqueness gate stage view with score/source/threshold/reason.
- Added tests for pass boundary, below-threshold revision routing and missing artifact error.
- Added review fix to preserve `ArtifactKey.UNIQUENESS` in state during threshold gating.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/routing.py
- Content_MultiAgent/src/seo_content_pipeline/models/job.py
- Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py
- Content_MultiAgent/src/seo_content_pipeline/services/uniqueness_gate_service.py
- Content_MultiAgent/tests/test_status_presenter.py
- Content_MultiAgent/tests/test_uniqueness_gate_service.py

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
- 2026-05-21: Started implementation; status moved to in-progress.
- 2026-05-21: Implemented uniqueness threshold gate; status moved to review.
- 2026-05-21: Patched code review finding for uniqueness artifact path preservation.
