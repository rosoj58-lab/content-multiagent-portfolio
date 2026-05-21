# Story 3.3: Run Editorial QA

Status: review

## Story

As an operator,
I want editorial QA for brief compliance, readability and factual discipline,
so that weak article drafts are caught before SEO QA.

## Acceptance Criteria

1. Given deterministic article checks have run, when editorial QA runs, then `editorial_qa.json` is saved.
2. The report includes pass/fail checks, recommendations and summary.
3. Unsupported factual claims are flagged unless generic and low-risk.
4. Failed editorial QA routes to revision guidance.
5. FR6 and NFR4 are covered.

## Scope Clarification

- This story implements LLM-facing editorial QA and persistence. It does not implement SEO QA, uniqueness, localization or full revision execution.
- Editorial QA consumes the approved brief, English Original and deterministic article validation report.
- The LLM output must parse into the existing `QAReport` Pydantic contract.
- Failed editorial QA should route back to `writing` with recommendations so targeted revision can happen without regenerating the whole workflow.

## Tasks / Subtasks

- [x] Add editorial QA prompt support (AC: 2, 3, 5)
  - [x] Build prompt from `SEOBrief`, English Original and deterministic validation report.
  - [x] Include brief compliance, logical structure, readability, filler and factual discipline checks.
  - [x] Explicitly flag unsupported factual claims unless they are generic and low-risk.
  - [x] Require structured JSON matching `QAReport`.

- [x] Add editorial QA orchestration (AC: 1, 2, 4, 5)
  - [x] Require `article_validation.json` before editorial QA runs.
  - [x] Load `brief.json`, `english_original.md` and `article_validation.json`.
  - [x] Generate structured `QAReport` through `LLMRunner`.
  - [x] Persist `editorial_qa.json`.
  - [x] Normalize failed reports to route back to `writing`.
  - [x] Update state/metadata and artifact paths.

- [x] Add focused tests (AC: 1-5)
  - [x] Test passing editorial QA report persistence.
  - [x] Test failed unsupported factual claims route to writing with recommendations.
  - [x] Test missing deterministic validation report is rejected.
  - [x] Test prompt contains unsupported factual claim instruction.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 3.1 creates `english_original.md`.
- Story 3.2 creates `article_validation.json`.
- `ArtifactKey.EDITORIAL_QA` already maps to `editorial_qa.json`.
- `QAReport` and `ValidationCheck` are the reusable structured QA contracts.
- `prompts/qa_prompt.py` is currently a placeholder.

### Architecture Requirements

- FR6: system checks English Original for brief compliance, logical structure, readability, lack of filler and unsupported factual claims.
- NFR4: MVP should avoid unnecessary repeated full-article generation when only targeted revision is needed.
- LLM QA consumes deterministic validator output but does not replace it.
- All LLM calls go through `services/llm_runner.py`.
- LLM outputs must parse into typed Pydantic contracts.

### Implementation Guidance

- Keep provider usage injectable and fake-client friendly.
- Do not add real OpenAI calls or network requirements.
- If failed report lacks a routing target, normalize it to `WorkflowStage.WRITING`.
- If failed report lacks recommendations, derive recommendations from failed check messages.

### Testing Requirements

- `tests/test_editorial_qa_service.py`: pass persistence, fail routing, missing validation precondition.
- `tests/test_editorial_qa_prompt.py`: prompt instructions for factual discipline and output schema.
- Existing tests must keep passing.

## References

- [Epics: Story 3.3 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: Editorial QA](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 3.2 completed article validators](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/3-2-run-deterministic-article-validators.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_editorial_qa_prompt.py tests/test_editorial_qa_service.py` passed: 4 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 73 tests.

### Completion Notes List

- Added editorial QA prompt builder with factual-discipline instruction and `QAReport` schema requirement.
- Added `EditorialQAService.run_editorial_qa()` to require deterministic article validation, load artifacts, parse LLM output into `QAReport`, persist `editorial_qa.json`, and update state/metadata.
- Normalized failed editorial QA to route to `writing` with recommendations for targeted revision.
- Added tests for prompt content, passing report persistence, failed unsupported factual claim routing, and missing validation precondition.

### File List

- Content_MultiAgent/src/seo_content_pipeline/prompts/qa_prompt.py
- Content_MultiAgent/src/seo_content_pipeline/services/editorial_qa_service.py
- Content_MultiAgent/tests/test_editorial_qa_prompt.py
- Content_MultiAgent/tests/test_editorial_qa_service.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented editorial QA; status moved to review.
