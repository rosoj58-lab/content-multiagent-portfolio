# Story 3.2: Run Deterministic Article Validators

Status: review

## Story

As an operator,
I want deterministic checks for word count and heading structure,
so that basic quality gates do not depend on LLM judgment.

## Acceptance Criteria

1. Given `english_original.md` exists, when deterministic validators run, then word count checks produce `list[ValidationCheck]`.
2. Required heading structure checks produce `list[ValidationCheck]`.
3. Required artifact checks produce `list[ValidationCheck]`.
4. Failures are visible in a QA summary.
5. Validator tests cover pass, warning and error severities.
6. NFR1 and NFR2 are covered.

## Scope Clarification

- This story implements deterministic article validation and a durable `article_validation.json` report. It does not implement editorial LLM QA, SEO keyword QA or revision routing beyond recording the validation result.
- Full-mode word count target is 1500-1600 words. Demo-mode articles may be shorter; validator thresholds are configurable per mode.
- Heading checks validate Markdown structure only: exactly one H1, at least one H2 and at least one H3.
- Required artifact checks verify that `english_original.md` exists through the artifact registry.

## Tasks / Subtasks

- [x] Add article validation artifact support (AC: 4)
  - [x] Add `ArtifactKey.ARTICLE_VALIDATION` and registry metadata for `article_validation.json`.
  - [x] Ensure artifact registry tests cover the new key.

- [x] Implement deterministic article validators (AC: 1, 2, 3, 5)
  - [x] Implement `validate_word_count()`.
  - [x] Implement `validate_heading_structure()`.
  - [x] Implement `validate_required_artifacts()`.
  - [x] Return `list[ValidationCheck]`, not booleans or strings.
  - [x] Cover pass, warning and error severities in tests.

- [x] Add article validation orchestration (AC: 4, 6)
  - [x] Load `english_original.md` through `ArtifactStore`.
  - [x] Run deterministic validators.
  - [x] Save a structured `QAReport` to `article_validation.json`.
  - [x] Update `state.json` and `metadata.json` with validation status.
  - [x] Store the article validation artifact path in `PipelineState.artifact_paths`.

- [x] Add focused tests (AC: 1-6)
  - [x] Test pass severity for valid article.
  - [x] Test warning severity for near-range word count.
  - [x] Test error severity for missing headings.
  - [x] Test required artifact failure.
  - [x] Test service report persistence and QA summary.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 3.1 persists `english_original.md` and records `english_original_generated`.
- `QAReport` and `ValidationCheck` already exist.
- `validators/artifact_validators.py` contains deterministic brief validators and can host article artifact validators.
- `ArtifactStore` supports JSON and Markdown artifacts.

### Architecture Requirements

- Deterministic validators run before LLM QA.
- Validators return `list[ValidationCheck]`.
- Word count, required headings and artifact completeness should not depend on LLM judgment.
- Full artifacts live in files; `PipelineState` stays lightweight.

### Implementation Guidance

- Keep validators pure and filesystem-free except for `validate_required_artifacts()`, which should accept already-computed artifact availability data.
- Let the service perform artifact IO and pass plain text/data into validators.
- Do not route to copywriter/editorial revision yet; Story 3.3 and 3.4 own later QA routing.

### Testing Requirements

- `tests/test_article_validators.py`: pure validator pass/warning/error coverage.
- `tests/test_article_validation_service.py`: report persistence, summary, state transitions and required artifact failure.
- Existing tests must keep passing.

## References

- [Epics: Story 3.2 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: QA and validation](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 3.1 completed writer stage](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/3-1-generate-english-original-from-approved-brief.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_article_validators.py tests/test_article_validation_service.py tests/test_artifact_registry.py` passed: 17 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 69 tests.

### Completion Notes List

- Added `article_validation.json` artifact support through `ArtifactKey.ARTICLE_VALIDATION`.
- Implemented deterministic validators for article word count, Markdown H1/H2/H3 structure and required artifact availability.
- Added `ArticleValidationService.validate_english_original()` to save a structured `QAReport`, update state/metadata and expose failures in summary/recommendations.
- Added focused tests covering pass, warning and error severities plus service persistence.

### File List

- Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py
- Content_MultiAgent/src/seo_content_pipeline/services/article_validation_service.py
- Content_MultiAgent/src/seo_content_pipeline/validators/artifact_validators.py
- Content_MultiAgent/tests/test_article_validation_service.py
- Content_MultiAgent/tests/test_article_validators.py
- Content_MultiAgent/tests/test_artifact_registry.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented deterministic article validators; status moved to review.
