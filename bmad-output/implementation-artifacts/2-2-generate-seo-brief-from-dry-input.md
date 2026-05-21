# Story 2.2: Generate SEO Brief From Dry Input

Status: review

## Story

As an operator,
I want the system to generate a structured SEO Brief,
so that I can review the planned article before text generation.

## Acceptance Criteria

1. Given a job has Dry Input and Article Type, when the brief generation stage runs, then `brief.json` is created.
2. `brief.json` contains topic, goal, audience, main keyword, secondary keywords, LSI keywords, H1/H2/H3 outline, tone of voice and constraints.
3. The brief is parsed into a Pydantic model before it is persisted.
4. LLM parse failure triggers exactly one repair attempt.
5. If the repair attempt fails, the job moves to controlled `needs_human_review` status with a persisted workflow error.
6. FR3 is covered.

## Scope Clarification

- This story implements the typed SEO brief generation stage and LLM parsing pattern. It does not implement brief QA, manual approval UI, article writing, real provider selection, or LangGraph end-to-end execution.
- The production LLM adapter may remain unconfigured; tests must use injected fake clients and must not require network or API keys.
- `ArtifactStore` remains the only layer that writes `brief.json`, `state.json`, and `metadata.json`.
- On successful brief generation, the job remains `running` at `brief_drafted`; Story 2.3 will decide whether the brief is complete and ready for a manual approval gate.

## Tasks / Subtasks

- [x] Add typed SEO brief contracts (AC: 2, 3, 6)
  - [x] Define Pydantic models for SEO brief content and H1/H2/H3 outline.
  - [x] Enforce non-empty keyword, audience, tone and constraints lists where useful.
  - [x] Export the public brief model through `seo_content_pipeline.models`.

- [x] Add prompt and LLM parsing infrastructure (AC: 3, 4, 5)
  - [x] Implement a brief prompt builder from Dry Input and Article Type.
  - [x] Implement a repair prompt builder that includes the parse error and invalid output.
  - [x] Implement `LLMRunner.generate_structured()` with exactly one repair attempt.
  - [x] Provide an injectable LLM client protocol so tests do not call external services.

- [x] Add brief generation orchestration (AC: 1, 5, 6)
  - [x] Load `input.json` from the artifact store.
  - [x] Generate and parse the SEO brief.
  - [x] Persist `brief.json`.
  - [x] Update `state.json` and `metadata.json` with `brief_drafted` status history.
  - [x] Persist controlled `WorkflowError` and `needs_human_review` on double parse failure.

- [x] Add focused tests (AC: 1-6)
  - [x] Verify valid generated JSON creates `brief.json` with required fields.
  - [x] Verify invalid first output triggers one repair call and then succeeds.
  - [x] Verify two invalid outputs produce `needs_human_review` with a persisted error.
  - [x] Verify direct LLM runner parsing behavior.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 2.1 persists `input.json`, `metadata.json`, and `state.json` with Dry Input and explicit `ArticleType`.
- `ArtifactKey.BRIEF` already maps to `brief.json`.
- `src/seo_content_pipeline/models/content.py`, `services/llm_runner.py`, `services/llm_client.py`, `prompts/brief.py`, and `graph/nodes/brief_node.py` are placeholders.
- No real LLM provider should be required to run tests or start the local app.

### Architecture Requirements

- FR3: system generates an SEO Brief containing topic, goal, audience, main keyword, secondary keywords, LSI keywords, H1/H2/H3 outline, tone of voice and constraints.
- All LLM-facing nodes must use typed Pydantic input/output contracts.
- All LLM calls go through `services/llm_runner.py`.
- If parsing fails, run exactly one repair attempt.
- If repair fails, write `WorkflowError` and route to `WorkflowStatus.NEEDS_HUMAN_REVIEW`.
- Streamlit remains a thin UI layer and must not import prompts, graph nodes, artifact store, validators or provider implementations directly.

### Implementation Guidance

- Keep brief generation callable from a service or node without requiring Streamlit.
- Prefer a small service facade for artifact reads/writes and state updates; keep graph integration minimal until later workflow stories.
- Store full brief content in `brief.json`; keep `PipelineState` lightweight with artifact paths, status, history and errors only.
- Use enum values through Pydantic JSON serialization rather than string literals.

### Testing Requirements

- `tests/test_llm_runner.py`: parse success, repair success, and repair failure behavior.
- `tests/test_brief_service.py`: artifact persistence, state/metadata updates, and controlled human-review route.
- Existing tests must keep passing.

## References

- [Epics: Story 2.2 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: LLM output pattern](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 2.1 completed intake](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/2-1-submit-dry-input-and-select-article-type.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_llm_runner.py tests/test_brief_service.py` passed: 6 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 34 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.

### Completion Notes List

- Added typed `SEOBrief` contracts with H1/H2/H3 outline support.
- Added prompt builders for initial brief generation and single repair attempt.
- Added injectable LLM client protocol and `LLMRunner.generate_structured()` with exactly one repair attempt.
- Added `BriefService.generate_brief()` to read `input.json`, persist `brief.json`, update state/metadata, and route double parse failures to `needs_human_review`.
- Added focused tests for success, repair success, repair failure and direct runner behavior.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/brief_node.py
- Content_MultiAgent/src/seo_content_pipeline/models/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/models/content.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/brief.py
- Content_MultiAgent/src/seo_content_pipeline/services/brief_service.py
- Content_MultiAgent/src/seo_content_pipeline/services/llm_client.py
- Content_MultiAgent/src/seo_content_pipeline/services/llm_runner.py
- Content_MultiAgent/tests/test_brief_service.py
- Content_MultiAgent/tests/test_llm_runner.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented SEO brief generation; status moved to review.
