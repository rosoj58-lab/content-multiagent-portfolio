# Story 5.3: Assemble Markdown and JSON Final Package

Status: review

## Story

As an operator,
I want the system to assemble final Markdown and JSON packages,
so that I can inspect and download the complete content package.

## Acceptance Criteria

1. Given brief, English Original, Spanish localization, Italian localization, French localization, SEO QA and uniqueness artifacts exist, when final packaging runs, then `final_package.md` and `final_package.json` are created.
2. Missing required artifacts prevent approved final status.
3. Exports reference Dry Input, Article Type, SEO Brief and QA reports.
4. FR15 and NFR3 are covered.

## Scope Clarification

- This story implements package assembly only.
- Story 5.4 will produce the final QA report and set final `Approved` or `Needs Revision` status.
- In this story, missing required artifacts must stop package creation and leave the workflow out of an approved final state.
- The final package should include references and content snapshots, not rerun LLM generation or QA checks.
- Markdown and JSON outputs must be deterministic and artifact-store backed.

## Tasks / Subtasks

- [x] Define final package data contract (AC: 1, 3)
  - [x] Add typed package models for artifact references and package content.
  - [x] Include Dry Input, Article Type, SEO Brief, English Original, all localizations, SEO QA and uniqueness report.
  - [x] Include traceability metadata such as job id and generated timestamp.

- [x] Implement final package exporter service (AC: 1, 2, 3, 4)
  - [x] Add a service method to assemble final package artifacts.
  - [x] Require all mandatory source artifacts before writing final outputs.
  - [x] Write `final_package.md` through `ArtifactStore`.
  - [x] Write `final_package.json` through `ArtifactStore`.
  - [x] Update `state.json` and `metadata.json` with final package artifact paths and status history.
  - [x] Do not set workflow status to `Approved` in this story.

- [x] Add graph support (AC: 1)
  - [x] Add final package node wrapper.
  - [x] Keep Streamlit entrypoint thin.

- [x] Add focused tests (AC: 1-4)
  - [x] Test final Markdown and JSON packages are persisted.
  - [x] Test JSON package references Dry Input, Article Type, SEO Brief, SEO QA and uniqueness report.
  - [x] Test Markdown package includes all language sections.
  - [x] Test missing required artifact raises and does not create final package artifacts.
  - [x] Test package assembly does not mark the job approved.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- `ArtifactKey.FINAL_PACKAGE_MD` maps to `final_package.md`.
- `ArtifactKey.FINAL_PACKAGE_JSON` maps to `final_package.json`.
- `services/exporters.py` is currently a placeholder.
- `graph/nodes/final_qa_node.py` is currently a placeholder and can host a thin final package node until Story 5.4 adds final QA behavior.
- Story 5.2 records Spanish, Italian and French localization artifacts and geos in state.

### Architecture Requirements

- FR15: system assembles SEO Brief, English Original, Spanish Localization, Italian Localization, French Localization, SEO QA report, uniqueness report and final status into Markdown and JSON final packages.
- NFR3: final package should reference the Dry Input, Article Type, SEO Brief and QA reports used to create it.
- Final package data should be stored as artifacts, not inside graph state.
- Artifact keys and filenames must come from the artifact registry.

### Implementation Guidance

- Implement deterministic package assembly in `services/exporters.py`.
- Use `ArtifactStore` for all reads and writes.
- Read `input.json`, `brief.json`, `english_original.md`, `editorial_qa.json`, `seo_qa.json`, `uniqueness.json`, `localization_es.md`, `localization_it.md`, `localization_fr.md`, `state.json` and `metadata.json`.
- Treat missing required artifacts as a `ValueError` before writing either final package artifact.
- Use `WorkflowStage.FINAL_QA` to indicate the workflow is ready for final QA, but keep `WorkflowStatus.RUNNING` until Story 5.4 decides approved vs revision.
- Keep JSON package structured enough for demos and tests; do not store it as stringified Markdown.

### Testing Requirements

- Add `tests/test_exporters.py`.
- Existing tests must keep passing.
- The first focused test run should fail before implementation if tests are added first.

## References

- [Epics: Story 5.3 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [PRD: FR15 and NFR3 package requirements](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md)
- [Architecture: final package files and exporter location](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 5.2 completed Italian and French localization](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/5-2-generate-italian-and-french-localizations.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 5, PRD FR15/NFR3, architecture exporter notes and Story 5.2 implementation learnings.
- Started implementation; status moved to in-progress.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_exporters.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_exporters.py` passed: 3 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 115 tests.

### Completion Notes List

- Added `FinalPackageExporter` and `FinalPackageResult`.
- Added deterministic Markdown and JSON package assembly.
- Added traceability references for source artifacts using the artifact registry.
- Added required-artifact preflight before writing final package outputs.
- Updated workflow state and metadata to `FINAL_QA` / `RUNNING` without marking the job approved.
- Added graph node wrapper for package assembly.
- Added focused exporter tests.

### File List

- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/final_qa_node.py
- Content_MultiAgent/src/seo_content_pipeline/services/exporters.py
- Content_MultiAgent/tests/test_exporters.py

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
- 2026-05-22: Started implementation; status moved to in-progress.
- 2026-05-22: Implemented final Markdown and JSON package assembly; status moved to review.
