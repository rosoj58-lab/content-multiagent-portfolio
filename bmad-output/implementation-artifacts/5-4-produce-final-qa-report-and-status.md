# Story 5.4: Produce Final QA Report and Status

Status: done

## Story

As an operator,
I want a final QA report with approved or revision status,
so that I can understand whether the content package is ready.

## Acceptance Criteria

1. Given final package assembly has run, when final QA runs, then the report lists completed stages, failed checks if any, uniqueness result and localization status.
2. Status is `Approved` only when all mandatory artifacts and gates pass.
3. `Needs Revision` includes routing guidance.
4. FR16 and FR17 are covered.

## Scope Clarification

- This story adds a dedicated `final_qa_report.json` artifact.
- This story sets the persisted job status to `approved` or `needs_revision`.
- This story does not regenerate package content, localizations, uniqueness checks or article QA.
- Final QA is deterministic and reads already-persisted artifacts and state.

## Tasks / Subtasks

- [x] Add final QA report contract and artifact registry support (AC: 1)
  - [x] Add `ArtifactKey.FINAL_QA_REPORT` mapped to `final_qa_report.json`.
  - [x] Add typed final QA report models.
  - [x] Export new models through `models/__init__.py`.

- [x] Implement final QA service (AC: 1, 2, 3, 4)
  - [x] Read state, metadata, final packages, QA reports, uniqueness report and localization artifacts.
  - [x] Determine completed stages from status history and artifact presence.
  - [x] List failed checks with clear messages.
  - [x] Include uniqueness score/source/threshold/pass status.
  - [x] Include Spanish, Italian and French localization status and geos.
  - [x] Set status `approved` only when mandatory artifacts and gates pass.
  - [x] Set status `needs_revision` with routing guidance when any mandatory check fails.
  - [x] Persist `final_qa_report.json`, `state.json` and `metadata.json`.

- [x] Add graph support (AC: 1)
  - [x] Add final QA node wrapper.
  - [x] Keep package assembly node behavior intact.

- [x] Add focused tests (AC: 1-4)
  - [x] Test happy path writes approved final QA report and updates state/metadata.
  - [x] Test missing or failed mandatory artifact/gate results in `needs_revision`.
  - [x] Test report includes uniqueness result and localization statuses.
  - [x] Test routing guidance points to the relevant next stage.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- Story 5.3 adds `FinalPackageExporter`, typed final package models and `assemble_final_package_node()`.
- `final_qa_node.py` now hosts final package graph support and can be extended with final QA node support.
- `ArtifactKey` does not yet include a dedicated final QA report artifact.
- `PipelineState` already tracks `qa_flags`, `artifact_paths`, `uniqueness_score`, `uniqueness_threshold`, `localization_geos` and status history.

### Architecture Requirements

- FR16: system produces a final QA report with status `Approved` or `Needs Revision`.
- Report lists completed stages, failed checks if any, uniqueness result and localization status.
- `Approved` requires all mandatory checks to pass.
- `Needs Revision` includes routing guidance to the next agent/stage.
- FR17: workflow status reflects current pipeline state and revision routing.

### Implementation Guidance

- Implement deterministic final QA in a new service, likely `services/final_qa_service.py`.
- Use `ArtifactStore` for all reads and writes.
- Treat required artifacts and gates separately so the report can explain exactly what is missing or failed.
- Mandatory artifacts should include input, brief, English original, article validation, editorial QA, SEO QA, uniqueness, all three localizations, `final_package.md` and `final_package.json`.
- Mandatory gates should include article validation, editorial QA, SEO QA, uniqueness gate, all three localization generated flags and final package assembled flag.
- For routing guidance, use the earliest relevant failed stage: brief issues to `brief_drafted`, writing/QA issues to `writing` or `seo_qa`, uniqueness issues to `uniqueness_check`, localization issues to `localization`, package issues to `final_qa`.
- Keep `Approved` impossible when any required artifact or gate is missing.

### Testing Requirements

- Add `tests/test_final_qa_service.py`.
- Existing tests must keep passing.
- The first focused test run should fail before implementation if tests are added first.

## References

- [Epics: Story 5.4 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [PRD: FR16 final QA requirements](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md)
- [Architecture: final QA service locations](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 5.3 completed final package assembly](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/5-3-assemble-markdown-and-json-final-package.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 5, PRD FR16/FR17, architecture final QA notes and Story 5.3 implementation learnings.
- Started implementation; status moved to in-progress.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_final_qa_service.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_final_qa_service.py` passed: 4 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 119 tests.
- Code review finding patched: final QA now syncs `final_package.md` and `final_package.json` workflow status to the terminal approved or revision status.
- Post-review verification passed: final QA tests 4/4, `ruff check .`, full `pytest` 119/119.
- Code review clean after package status sync patch; status moved to done.

### Completion Notes List

- Added `final_qa_report.json` artifact registry support.
- Added typed final QA report models.
- Added deterministic `FinalQAService`.
- Final QA writes approved status only when mandatory artifacts, gates, QA reports and uniqueness threshold pass.
- Needs Revision reports include failed checks and routing guidance.
- Final QA syncs final package Markdown and JSON workflow status after terminal status is known.
- Added final QA graph node wrapper.
- Added focused final QA service tests.
- Code review passed after final package status sync patch.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/final_qa_node.py
- Content_MultiAgent/src/seo_content_pipeline/models/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py
- Content_MultiAgent/src/seo_content_pipeline/models/final_qa.py
- Content_MultiAgent/src/seo_content_pipeline/services/final_qa_service.py
- Content_MultiAgent/tests/test_final_qa_service.py

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
- 2026-05-22: Started implementation; status moved to in-progress.
- 2026-05-22: Implemented final QA report and terminal status; status moved to review.
- 2026-05-22: Patched final package status sync after final QA.
- 2026-05-22: Code review passed; status moved to done.
