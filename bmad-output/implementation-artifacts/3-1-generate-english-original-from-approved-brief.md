# Story 3.1: Generate English Original From Approved Brief

Status: done

## Story

As an operator,
I want the system to generate an English US article from an approved SEO Brief,
so that I receive the primary content artifact for QA.

## Acceptance Criteria

1. Given the brief is approved, when the writing stage runs, then `english_original.md` is created.
2. The writer prompt requires English US.
3. The writer prompt requires H1/H2/H3 structure from the approved brief.
4. Demo mode supports a shorter target length.
5. Full mode targets 1500-1600 words.
6. The stage timeline records writing completion.
7. FR5 is covered.

## Scope Clarification

- This story implements the writer stage service, prompt and Markdown artifact persistence. It does not implement deterministic article validators, editorial QA, SEO QA, uniqueness or localization.
- The writer output is Markdown, so `english_original.md` is persisted as a text artifact through `ArtifactStore`.
- The actual word-count validation is Story 3.2; this story ensures mode-specific target length is included in the writer prompt.
- The writer must require a previously approved brief (`brief_approved`) before generating content.

## Tasks / Subtasks

- [x] Add text artifact persistence (AC: 1)
  - [x] Add `ArtifactStore.write_text()` for text/markdown artifacts.
  - [x] Add `ArtifactStore.read_text()` for text artifacts.
  - [x] Add tests proving JSON/text content-type boundaries are enforced.

- [x] Add writer prompt and LLM runner support (AC: 2, 3, 4, 5)
  - [x] Add `LLMRunner.generate_text()`.
  - [x] Build a writer prompt from `SEOBrief`.
  - [x] Include English US requirement.
  - [x] Include H1/H2/H3 outline instructions.
  - [x] Include demo and full target length instructions.

- [x] Add writer stage orchestration (AC: 1, 6, 7)
  - [x] Validate that the job state is `brief_approved`.
  - [x] Load `brief.json`.
  - [x] Generate Markdown article through `LLMRunner`.
  - [x] Persist `english_original.md`.
  - [x] Update `state.json` and `metadata.json` with writing stage completion.
  - [x] Store the English Original artifact path in `PipelineState.artifact_paths`.

- [x] Add focused tests (AC: 1-7)
  - [x] Test approved brief generates `english_original.md`.
  - [x] Test unapproved brief is rejected.
  - [x] Test demo prompt uses shorter target length.
  - [x] Test full prompt targets 1500-1600 words.
  - [x] Test writing completion is recorded in status history.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Epic 2 is complete.
- Story 2.4 records approved briefs as `current_stage=brief_approved`, `status=approved`, and `qa_flags["brief_approved"] = True`.
- `ArtifactKey.ENGLISH_ORIGINAL` already maps to `english_original.md`.
- `prompts/writer.py`, `graph/nodes/writer_node.py`, and the writer service are placeholders/missing.
- `ArtifactStore` currently supports JSON artifacts only.

### Architecture Requirements

- FR5: system generates an English US article from an approved SEO Brief with H1/H2/H3 structure and target length of 1500-1600 words in full mode.
- LLM calls go through `services/llm_runner.py`.
- Streamlit remains thin; writer orchestration belongs in services or graph nodes.
- Full artifacts live in files; `PipelineState` stores artifact paths and status only.

### Implementation Guidance

- Keep real provider usage injectable and fake-client friendly for tests.
- Do not validate article word count in this story; Story 3.2 owns deterministic article validators.
- Persist raw Markdown exactly as generated after trimming outer whitespace and appending a final newline.
- Do not overwrite unrelated artifacts.

### Testing Requirements

- `tests/test_artifact_store.py`: text artifact persistence and content-type enforcement.
- `tests/test_writer_service.py`: approved-only generation, mode-specific prompt targets, Markdown persistence and status updates.
- Existing tests must keep passing.

## References

- [Epics: Story 3.1 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: writer mapping](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 2.4 completed brief approval gate](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/2-4-approve-or-request-revision-for-seo-brief.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_artifact_store.py tests/test_llm_runner.py tests/test_writer_service.py` passed: 18 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 59 tests.
- Code review clean: no decision-needed, patch, or deferred findings.

### Completion Notes List

- Added text/Markdown artifact persistence to `ArtifactStore`.
- Added `LLMRunner.generate_text()` for non-JSON LLM outputs.
- Added writer prompt builder with English US, outline and demo/full target length requirements.
- Added `WriterService.generate_english_original()` to enforce approved brief, generate Markdown and update state/metadata.
- Added writer graph node wrapper.
- Added focused tests for Markdown persistence, text LLM output and writer stage behavior.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/writer_node.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/writer.py
- Content_MultiAgent/src/seo_content_pipeline/services/artifact_store.py
- Content_MultiAgent/src/seo_content_pipeline/services/llm_runner.py
- Content_MultiAgent/src/seo_content_pipeline/services/writer_service.py
- Content_MultiAgent/tests/test_artifact_store.py
- Content_MultiAgent/tests/test_llm_runner.py
- Content_MultiAgent/tests/test_writer_service.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented English Original writer stage; status moved to review.
- 2026-05-21: Code review clean; status moved to done.
