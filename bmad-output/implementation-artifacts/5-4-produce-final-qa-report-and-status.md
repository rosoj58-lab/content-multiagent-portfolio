# Story 5.4: Produce Final QA Report and Status

Status: ready-for-dev

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

- [ ] Add final QA report contract and artifact registry support (AC: 1)
  - [ ] Add `ArtifactKey.FINAL_QA_REPORT` mapped to `final_qa_report.json`.
  - [ ] Add typed final QA report models.
  - [ ] Export new models through `models/__init__.py`.

- [ ] Implement final QA service (AC: 1, 2, 3, 4)
  - [ ] Read state, metadata, final packages, QA reports, uniqueness report and localization artifacts.
  - [ ] Determine completed stages from status history and artifact presence.
  - [ ] List failed checks with clear messages.
  - [ ] Include uniqueness score/source/threshold/pass status.
  - [ ] Include Spanish, Italian and French localization status and geos.
  - [ ] Set status `approved` only when mandatory artifacts and gates pass.
  - [ ] Set status `needs_revision` with routing guidance when any mandatory check fails.
  - [ ] Persist `final_qa_report.json`, `state.json` and `metadata.json`.

- [ ] Add graph support (AC: 1)
  - [ ] Add final QA node wrapper.
  - [ ] Keep package assembly node behavior intact.

- [ ] Add focused tests (AC: 1-4)
  - [ ] Test happy path writes approved final QA report and updates state/metadata.
  - [ ] Test missing or failed mandatory artifact/gate results in `needs_revision`.
  - [ ] Test report includes uniqueness result and localization statuses.
  - [ ] Test routing guidance points to the relevant next stage.
  - [ ] Run full `pytest` and `ruff check .`.

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

### Completion Notes List

- Pending implementation.

### File List

- Pending implementation.

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
