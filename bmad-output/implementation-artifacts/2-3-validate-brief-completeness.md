# Story 2.3: Validate Brief Completeness

Status: done

## Story

As an operator,
I want the system to validate SEO Brief completeness,
so that weak briefs do not proceed to writing.

## Acceptance Criteria

1. Given `brief.json` exists, when brief QA runs, then a structured brief QA report is saved.
2. Missing main keyword fails the check with an actionable missing-field message.
3. Unclear audience fails the check with an actionable missing-field message.
4. Missing or incomplete H1/H2/H3 outline fails the check with an actionable missing-field message.
5. Failed brief QA exposes actionable missing fields through UI-ready stage data.
6. Passed brief QA moves the job to a manual approval gate.
7. FR4, NFR1 and NFR2 are covered.

## Scope Clarification

- This story implements deterministic brief completeness QA. It does not implement manual approval actions, revision submission UI, article writing, LLM QA, or LangGraph end-to-end execution.
- Brief QA should save a durable `brief_qa.json` report so the portfolio demo can inspect why a brief passed or failed.
- Passed brief QA should set the job to `waiting_for_human` at `brief_drafted`; Story 2.4 will implement approve/request-revision actions.
- Failed brief QA should set the job to `needs_revision` at `brief_drafted` and keep actionable missing-field details in the QA report and UI-ready `StageView`.

## Tasks / Subtasks

- [x] Add brief QA artifact support (AC: 1)
  - [x] Add `ArtifactKey.BRIEF_QA` and registry metadata for `brief_qa.json`.
  - [x] Ensure artifact registry tests continue to cover all keys.

- [x] Implement deterministic brief validators (AC: 2, 3, 4, 7)
  - [x] Implement `validate_required_brief_fields()`.
  - [x] Detect missing/blank main keyword.
  - [x] Detect unclear/generic audience.
  - [x] Detect missing/incomplete H1/H2/H3 outline.
  - [x] Return `list[ValidationCheck]`, not booleans or strings.

- [x] Implement brief QA orchestration (AC: 1, 5, 6)
  - [x] Load `brief.json` from `ArtifactStore`.
  - [x] Save structured `QAReport` to `brief_qa.json`.
  - [x] Update `state.json` and `metadata.json` to `waiting_for_human` on pass.
  - [x] Update `state.json` and `metadata.json` to `needs_revision` on fail.
  - [x] Store `brief_qa` artifact path in `PipelineState.artifact_paths`.

- [x] Expose UI-ready actionable state (AC: 5, 6)
  - [x] Build `StageView` data for failed brief QA with actionable missing fields.
  - [x] Build `StageView` data for passed brief QA with approve/request-revision actions.

- [x] Add focused tests (AC: 1-7)
  - [x] Test validator failure for missing main keyword.
  - [x] Test validator failure for unclear audience.
  - [x] Test validator failure for missing/incomplete outline.
  - [x] Test service saves `brief_qa.json` and updates manual gate on pass.
  - [x] Test service saves failed report and exposes actionable UI data on fail.

- [x] Run verification and update story record
  - [x] Run full `pytest`.
  - [x] Run `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List.

## Dev Notes

### Current Repository State

- Story 2.2 added `SEOBrief`, `SEOBriefArtifact`, `BriefService`, and `LLMRunner`.
- `brief.json` is persisted through `ArtifactKey.BRIEF`.
- `QAReport` and `ValidationCheck` already exist and should be reused.
- `validators/artifact_validators.py` is still a placeholder.

### Architecture Requirements

- FR4: system validates that the SEO Brief contains enough information for article generation and returns weak briefs with specific missing or weak fields.
- NFR1/NFR2: local deterministic validation must be reliable and transparent for demo/debugging.
- Deterministic validators return `list[ValidationCheck]`.
- Full artifacts live in files; `PipelineState` stays lightweight.
- Streamlit remains a thin UI layer; UI-specific state should be provided as `StageView` data.

### Implementation Guidance

- Keep validators pure and filesystem-free.
- Treat malformed `brief.json` as a failed QA report where possible, not as an uncontrolled crash.
- Store actionable missing/weak field names in check metadata, so UI and future revision routing can reuse them.
- Do not introduce real LLM calls, provider dependencies, or network requirements.

### Testing Requirements

- `tests/test_brief_validators.py`: required field and outline edge cases.
- `tests/test_brief_qa_service.py`: pass/fail persistence and state transitions.
- `tests/test_status_presenter.py`: UI-ready failed/pass brief QA stage data.
- Existing tests must keep passing.

## References

- [Epics: Story 2.3 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: QA and validation](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 2.2 completed brief generation](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/2-2-generate-seo-brief-from-dry-input.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_brief_validators.py tests/test_brief_qa_service.py tests/test_status_presenter.py tests/test_artifact_registry.py` passed: 18 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 44 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- Code review clean: no decision-needed, patch, or deferred findings.

### Completion Notes List

- Added `brief_qa.json` artifact support through `ArtifactKey.BRIEF_QA`.
- Implemented deterministic brief completeness validators for main keyword, audience and H1/H2/H3 outline.
- Added `BriefQAService.validate_brief()` to save `QAReport`, update state/metadata and open the manual gate on pass.
- Added UI-ready `StageView` builder for failed actionable fields and passed approval actions.
- Added focused tests for validators, service persistence/state transitions, registry and stage view behavior.

### File List

- Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py
- Content_MultiAgent/src/seo_content_pipeline/services/brief_qa_service.py
- Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py
- Content_MultiAgent/src/seo_content_pipeline/validators/artifact_validators.py
- Content_MultiAgent/tests/test_artifact_registry.py
- Content_MultiAgent/tests/test_brief_qa_service.py
- Content_MultiAgent/tests/test_brief_validators.py
- Content_MultiAgent/tests/test_status_presenter.py

## Change Log

- 2026-05-21: Created story and moved status to in-progress.
- 2026-05-21: Implemented deterministic brief QA; status moved to review.
- 2026-05-21: Code review clean; status moved to done.
