# Story 5.2: Generate Italian and French Localizations

Status: review

## Story

As an operator,
I want Italian and French localizations from the approved English Original,
so that the final package includes all required language versions.

## Acceptance Criteria

1. Given English Original has passed QA and uniqueness gate, when Italian and French localization runs, then `localization_it.md` and `localization_fr.md` are created.
2. Both Italian and French localizations preserve meaning, headings and SEO intent.
3. Localization does not run before uniqueness gate passes.
4. FR13 and FR14 are covered.

## Scope Clarification

- This story implements Italian and French localizations only.
- Spanish localization already exists from Story 5.1 and must not regress.
- The MVP default Italian geo is `it-IT`.
- The MVP default French geo is `fr-FR`.
- This story does not add a full geo-selection UI; it records selected/default geos in workflow state.
- This story does not implement final package assembly or localization quality routing; those belong to Stories 5.3 and 5.4.

## Tasks / Subtasks

- [x] Extend localization prompt support (AC: 2)
  - [x] Add Italian and French prompt builders.
  - [x] Require Markdown-only output.
  - [x] Require preservation of heading hierarchy, meaning and SEO intent.
  - [x] Include default geos `it-IT` and `fr-FR` when none are provided.
  - [x] Keep Spanish prompt behavior compatible.

- [x] Implement Italian and French localization orchestration (AC: 1, 3, 4)
  - [x] Add service method for generating both Italian and French localizations from the approved English Original.
  - [x] Require passed English QA and uniqueness gate before localization.
  - [x] Load `english_original.md`, `brief.json`, and `state.json`.
  - [x] Save `localization_it.md` and `localization_fr.md` through `ArtifactStore`.
  - [x] Update `state.json` and `metadata.json`.
  - [x] Record Italian and French geos in typed state.

- [x] Add graph support (AC: 1)
  - [x] Add localization node wrapper for Italian and French localization.
  - [x] Keep Streamlit entrypoint thin.

- [x] Add focused tests (AC: 1-4)
  - [x] Test Italian and French localization artifacts are persisted.
  - [x] Test prompts include language, geo, headings and SEO intent.
  - [x] Test default geos are recorded.
  - [x] Test explicit geo overrides are recorded.
  - [x] Test localization is rejected before uniqueness gate passes.
  - [x] Test existing Spanish localization behavior still passes.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- Story 5.1 added `LocalizationService.generate_spanish_localization()`, `build_spanish_localization_prompt()`, `LocalizationResult`, and `localization_geos` state tracking.
- `ArtifactKey.LOCALIZATION_IT` maps to `localization_it.md`.
- `ArtifactKey.LOCALIZATION_FR` maps to `localization_fr.md`.
- `tests/test_localization_service.py` already has helpers for localizable jobs that passed English QA and uniqueness gate.
- Story 5.1 code review added the important precondition that localization requires generated English Original plus article validation, editorial QA, SEO QA and uniqueness gate.

### Architecture Requirements

- FR13: system generates Italian Localization from the approved English Original only after English Original passes uniqueness gate.
- FR14: system generates French Localization from the approved English Original only after English Original passes uniqueness gate.
- Both outputs must preserve meaning, headings and SEO intent.
- Full article text and translations are stored as artifacts, not inside graph state.
- Status history must record ordered stage/status transitions.

### Implementation Guidance

- Reuse the Spanish localization service pattern rather than creating a parallel architecture.
- Prefer shared prompt helper code where it reduces duplication without hiding language-specific defaults.
- Use `LLMRunner.generate_text()` for Markdown localization.
- Generate both language texts before writing artifacts, so a French generation failure does not leave a partial Italian artifact.
- Keep service IO behind `ArtifactStore`.
- Use `WorkflowStage.LOCALIZATION` and `WorkflowStatus.RUNNING`.
- Preserve existing Spanish behavior and tests.
- Do not implement final package assembly here.

### Testing Requirements

- Extend `tests/test_localization_service.py`.
- Existing tests must keep passing.
- The first focused test run should fail before implementation if tests are added first.

## References

- [Epics: Story 5.2 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [PRD: FR13 and FR14 localization requirements](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md)
- [Architecture: localization files and FR12-FR14 mapping](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 5.1 completed Spanish localization](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/5-1-generate-spanish-localization.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 5, PRD FR13/FR14, architecture localization notes and Story 5.1 implementation learnings.
- Started implementation; status moved to in-progress.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_localization_service.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_localization_service.py` passed: 8 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 112 tests.

### Completion Notes List

- Added shared localization prompt builder plus Italian and French prompt builders.
- Added default Italian geo `it-IT` and default French geo `fr-FR`.
- Added `LocalizationService.generate_italian_and_french_localizations()` using `LLMRunner.generate_text()`.
- Generated both language texts before writing artifacts to avoid partial writes if the second generation fails.
- Added localization state persistence, artifact path tracking and geo recording for Italian and French.
- Added graph node wrapper for Italian and French localization.
- Extended focused localization tests while keeping Spanish tests passing.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/localization_node.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/localization.py
- Content_MultiAgent/src/seo_content_pipeline/services/localization_service.py
- Content_MultiAgent/tests/test_localization_service.py

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
- 2026-05-22: Started implementation; status moved to in-progress.
- 2026-05-22: Implemented Italian and French localization; status moved to review.
