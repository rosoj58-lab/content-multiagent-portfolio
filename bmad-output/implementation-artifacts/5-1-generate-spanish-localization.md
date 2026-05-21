# Story 5.1: Generate Spanish Localization

Status: review

## Story

As an operator,
I want Spanish localization from the approved English Original,
so that the final package includes a localized Spanish version.

## Acceptance Criteria

1. Given English Original has passed QA and uniqueness gate, when Spanish localization runs, then `localization_es.md` is created.
2. The Spanish localization preserves meaning, headings and SEO intent.
3. The selected or default Spanish geo is recorded.
4. FR12 is covered.

## Scope Clarification

- This story implements Spanish localization only; Italian and French belong to Story 5.2.
- Localization must not run before uniqueness gate passes.
- The MVP default Spanish geo is `es-US` unless another geo is passed explicitly.
- This story does not add a full geo-selection UI; it records the selected/default geo in workflow state.

## Tasks / Subtasks

- [x] Implement Spanish localization prompt support (AC: 2, 3)
  - [x] Build prompt from English Original, SEO brief and Spanish geo.
  - [x] Instruct the model to return Markdown only.
  - [x] Require preservation of heading hierarchy and SEO intent.
  - [x] Include default geo `es-US` when none is provided.

- [x] Implement localization orchestration (AC: 1, 3, 4)
  - [x] Add `LocalizationService.generate_spanish_localization()`.
  - [x] Require passed uniqueness gate before localization.
  - [x] Load `english_original.md`, `brief.json`, and `state.json`.
  - [x] Save `localization_es.md` through `ArtifactStore`.
  - [x] Update `state.json` and `metadata.json`.
  - [x] Record Spanish geo in typed state.

- [x] Add graph support (AC: 1)
  - [x] Add localization node wrapper for Spanish localization.
  - [x] Keep Streamlit entrypoint thin.

- [x] Add focused tests (AC: 1-4)
  - [x] Test Spanish localization artifact is persisted.
  - [x] Test localization prompt includes Spanish, geo, headings and SEO intent.
  - [x] Test default `es-US` geo is recorded.
  - [x] Test explicit geo override is recorded.
  - [x] Test localization is rejected before uniqueness gate passes.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- `ArtifactKey.LOCALIZATION_ES` already maps to `localization_es.md`.
- `prompts/localization.py` and `graph/nodes/localization_node.py` are placeholders.
- `WriterService` is the closest pattern for LLM-backed Markdown artifact generation.
- Story 4.3 routes passing uniqueness scores to `WorkflowStage.LOCALIZATION` and sets `qa_flags["uniqueness_gate_passed"] = True`.

### Architecture Requirements

- FR12: system generates Spanish Localization from the approved English Original and adapts wording to selected geo when provided.
- Localization must happen only after English Original passes uniqueness gate.
- Full article text and translations are stored as artifacts, not inside graph state.
- Status history must record ordered stage/status transitions.

### Implementation Guidance

- Use `LLMRunner.generate_text()` for Markdown localization.
- Keep service IO behind `ArtifactStore`.
- Use `WorkflowStage.LOCALIZATION` and `WorkflowStatus.RUNNING`.
- Add a typed state field for localization geos rather than storing strings in `qa_flags`.
- Do not implement Italian/French here.
- Do not implement final package assembly here.

### Testing Requirements

- Add `tests/test_localization_service.py`.
- Existing tests must keep passing.

## References

- [Epics: Story 5.1 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: localization files and FR12-FR14 mapping](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 4.3 completed uniqueness gate](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/4-3-gate-workflow-by-90-percent-threshold.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 5, architecture localization notes, WriterService pattern and Story 4.3 implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_localization_service.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_localization_service.py` passed: 3 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 107 tests.

### Completion Notes List

- Added Spanish localization prompt builder with default geo `es-US`.
- Added `LocalizationService.generate_spanish_localization()` using `LLMRunner.generate_text()`.
- Added localization state persistence, artifact path tracking and geo recording.
- Added graph node wrapper for Spanish localization.
- Added focused localization tests.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/localization_node.py
- Content_MultiAgent/src/seo_content_pipeline/models/job.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/localization.py
- Content_MultiAgent/src/seo_content_pipeline/services/localization_service.py
- Content_MultiAgent/tests/test_localization_service.py

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
- 2026-05-21: Started implementation; status moved to in-progress.
- 2026-05-21: Implemented Spanish localization; status moved to review.
