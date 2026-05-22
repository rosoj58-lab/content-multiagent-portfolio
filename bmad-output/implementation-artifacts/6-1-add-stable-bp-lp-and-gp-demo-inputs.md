# Story 6.1: Add Stable BP, LP and GP Demo Inputs

Status: ready-for-dev

## Story

As a project owner,
I want stable demo inputs for BP, LP and GP article types,
so that the portfolio demo can be repeated consistently.

## Acceptance Criteria

1. Given the examples directory exists, when demo inputs are added, then `examples/inputs/bp-demo.txt`, `lp-demo.txt`, `gp-demo.txt` and `sample-keywords.json` exist.
2. Each input is usable by the Streamlit demo flow.
3. The docs explain which demo path each input supports.
4. UJ-3 and UX-DR6 are covered.

## Scope Clarification

- This story adds stable demo source inputs and supporting keyword metadata only.
- This story does not implement observability UI; that belongs to Story 6.2.
- This story does not create the full interview walkthrough docs; that belongs to Story 6.3.
- Inputs should be realistic enough to generate distinct BP, LP and GP outputs without live web research.

## Tasks / Subtasks

- [ ] Add stable demo input artifacts (AC: 1, 2)
  - [ ] Create `examples/inputs/bp-demo.txt`.
  - [ ] Create `examples/inputs/lp-demo.txt`.
  - [ ] Create `examples/inputs/gp-demo.txt`.
  - [ ] Create `examples/inputs/sample-keywords.json`.
  - [ ] Keep each text input plain enough to paste into the Streamlit dry input form.

- [ ] Document demo paths (AC: 3, 4)
  - [ ] Update demo docs with BP, LP and GP path descriptions.
  - [ ] Explain the intended demo behavior and article type for each file.
  - [ ] Keep deeper interview walkthrough content deferred to Story 6.3.

- [ ] Add focused validation tests (AC: 1, 2, 3)
  - [ ] Test all expected demo files exist.
  - [ ] Test keyword metadata is valid JSON and maps BP/LP/GP to the expected files.
  - [ ] Test each input can create a job shell with its article type through `JobService`.
  - [ ] Test docs mention all demo input files and paths.
  - [ ] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- `examples/outputs/README.md` exists, but `examples/inputs/` does not yet exist.
- `docs/demo-setup.md`, `docs/demo-script.md` and related docs currently contain placeholders.
- `JobService.create_job()` already accepts dry input plus `ArticleType.BP`, `ArticleType.LP` or `ArticleType.GP`.
- Streamlit intake already supports a dry input text area and article type selector.

### Architecture Requirements

- UJ-3: operator prepares portfolio demos for BP, LP and GP and receives comparable packages.
- UX-DR6: UI must support reproducible demo flows: happy path, revision path and human-review path.
- Examples should support local portfolio demo reliability without external services.

### Implementation Guidance

- Prefer `examples/inputs/` for demo source files, matching architecture notes.
- Keep demo inputs deterministic and self-contained: include product/context facts, target audience, constraints and desired angle.
- `sample-keywords.json` should be structured enough for future demo docs and tests.
- Update `docs/demo-setup.md` with concise demo path mapping for this story; Story 6.3 can expand it later.

### Testing Requirements

- Add or extend tests focused on example inputs.
- Existing tests must keep passing.

## References

- [Epics: Story 6.1 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [PRD: UJ-3 demo cases](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md)
- [Architecture: examples and demo docs](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 6, PRD UJ-3/UX-DR6 and current docs/examples state.

### Completion Notes List

- Pending implementation.

### File List

- Pending implementation.

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
