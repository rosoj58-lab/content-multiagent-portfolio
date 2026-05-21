# Story 3.4: Run SEO QA and Route Failures

Status: done

## Story

As an operator,
I want SEO QA to check keywords, headings, intent and stuffing risk,
so that the English Original is SEO-structured before uniqueness and localization.

## Acceptance Criteria

1. Given editorial QA has passed, when SEO QA runs, then `seo_qa.json` is saved.
2. The structured SEO QA report includes keyword, LSI, heading, word count, intent, article type and over-optimization checks.
3. SEO failures route to SEO QA + Rewriter path with actionable notes.
4. Revision attempts are bounded by `MAX_REVISION_ATTEMPTS`.
5. FR7, FR17 and FR18 are covered.

## Scope Clarification

- This story implements local deterministic SEO QA for the MVP. It does not add live SERP or keyword research.
- SEO failures are routed to targeted writing revision because the current workflow has no separate rewriter stage enum.
- Revision attempts are counted under `WorkflowStage.SEO_QA`; exceeding the configured limit routes to `needs_human_review`.
- Passing SEO QA keeps the job moving toward uniqueness; Story 4 owns the uniqueness gate.

## Tasks / Subtasks

- [x] Implement SEO validators (AC: 2)
  - [x] Check main keyword usage.
  - [x] Check secondary keyword usage.
  - [x] Check LSI keyword coverage.
  - [x] Check heading keyword/topic alignment.
  - [x] Include word-count check signal.
  - [x] Include intent and article type fit checks.
  - [x] Include over-optimization/stuffing risk check.

- [x] Implement SEO QA orchestration (AC: 1, 3, 4, 5)
  - [x] Require passed `editorial_qa.json`.
  - [x] Load `brief.json`, `english_original.md`, `article_validation.json`, and `editorial_qa.json`.
  - [x] Save `seo_qa.json` as `QAReport`.
  - [x] Route failures to `needs_revision` with `routing_target=writing`.
  - [x] Increment SEO QA revision attempts on failure.
  - [x] Route revision limit overflow to `needs_human_review`.
  - [x] Update `state.json` and `metadata.json`.

- [x] Add focused tests (AC: 1-5)
  - [x] Test passing SEO QA report persistence.
  - [x] Test keyword/LSI/heading/stuffing failures with actionable recommendations.
  - [x] Test SEO failures increment revision attempts and route to writing.
  - [x] Test revision limit overflow routes to human review.
  - [x] Test missing or failed editorial QA is rejected.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 3.1 creates `english_original.md`.
- Story 3.2 creates `article_validation.json`.
- Story 3.3 creates `editorial_qa.json`.
- `ArtifactKey.SEO_QA` already maps to `seo_qa.json`.
- `validators/seo_validators.py` and `graph/nodes/seo_node.py` are placeholders.

### Architecture Requirements

- FR7: check main keyword usage, secondary keyword usage, LSI coverage, headings, word count, intent match, Article Type fit and keyword stuffing risk.
- FR17: status changes must be tracked in order.
- FR18: SEO issues route to SEO QA + Rewriter path.
- Revision attempts are bounded by configurable `MAX_REVISION_ATTEMPTS`.

### Implementation Guidance

- Keep validators deterministic and filesystem-free.
- Keep service IO behind `ArtifactStore`.
- Use `QAReport` and `ValidationCheck`; do not introduce a separate report schema.
- Treat Rewriter as a targeted writing revision path until a dedicated rewriter stage exists.

### Testing Requirements

- `tests/test_seo_validators.py`: pure SEO validator pass/fail coverage.
- `tests/test_seo_qa_service.py`: persistence, routing and revision-limit behavior.
- Existing tests must keep passing.

## References

- [Epics: Story 3.4 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: SEO QA mapping](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 3.3 completed editorial QA](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/3-3-run-editorial-qa.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_seo_validators.py tests/test_seo_qa_service.py` passed: 7 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 80 tests.
- Code review finding patched: SEO QA reports no longer keep `routing_target=writing` after the revision limit routes the job to human review.
- Post-review verification passed: targeted SEO tests 7/7, `ruff check .`, full `pytest` 80/80.

### Completion Notes List

- Implemented deterministic SEO checks for main keyword, secondary keywords, LSI keywords, heading alignment, word count signal, intent match, article type fit and keyword stuffing risk.
- Added `SEOQAService.run_seo_qa()` to require passed editorial QA, save `seo_qa.json`, update state/metadata and route failures.
- Added SEO revision attempt tracking under `WorkflowStage.SEO_QA`.
- Added human-review route when SEO revision attempts exceed `MAX_REVISION_ATTEMPTS`.
- Added SEO graph node wrapper and focused tests.
- Code review passed after fixing human-review routing consistency.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/seo_node.py
- Content_MultiAgent/src/seo_content_pipeline/services/seo_qa_service.py
- Content_MultiAgent/src/seo_content_pipeline/validators/seo_validators.py
- Content_MultiAgent/tests/test_seo_qa_service.py
- Content_MultiAgent/tests/test_seo_validators.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented SEO QA and failure routing; status moved to review.
- 2026-05-21: Patched code review finding and moved status to done.
