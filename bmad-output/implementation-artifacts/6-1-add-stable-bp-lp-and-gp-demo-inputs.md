# Story 6.1: Add Stable BP, LP and GP Demo Inputs

Status: done

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

- [x] Add stable demo input artifacts (AC: 1, 2)
  - [x] Create `examples/inputs/bp-demo.txt`.
  - [x] Create `examples/inputs/lp-demo.txt`.
  - [x] Create `examples/inputs/gp-demo.txt`.
  - [x] Create `examples/inputs/sample-keywords.json`.
  - [x] Keep each text input plain enough to paste into the Streamlit dry input form.

- [x] Document demo paths (AC: 3, 4)
  - [x] Update demo docs with BP, LP and GP path descriptions.
  - [x] Explain the intended demo behavior and article type for each file.
  - [x] Keep deeper interview walkthrough content deferred to Story 6.3.

- [x] Add focused validation tests (AC: 1, 2, 3)
  - [x] Test all expected demo files exist.
  - [x] Test keyword metadata is valid JSON and maps BP/LP/GP to the expected files.
  - [x] Test each input can create a job shell with its article type through `JobService`.
  - [x] Test docs mention all demo input files and paths.
  - [x] Run full `pytest` and `ruff check .`.

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
- Started implementation; status moved to in-progress.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_demo_inputs.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_demo_inputs.py` passed: 4 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 123 tests.
- Code review clean; status moved to done.

### Completion Notes List

- Added BP, LP and GP dry input files under `examples/inputs/`.
- Added `sample-keywords.json` with article type, demo path and keyword metadata for all three demos.
- Updated `docs/demo-setup.md` with demo path mapping and usage steps.
- Added focused demo input tests validating files, metadata, docs and `JobService` compatibility.
- Code review passed without patch findings.

### File List

- Content_MultiAgent/docs/demo-setup.md
- Content_MultiAgent/examples/inputs/bp-demo.txt
- Content_MultiAgent/examples/inputs/gp-demo.txt
- Content_MultiAgent/examples/inputs/lp-demo.txt
- Content_MultiAgent/examples/inputs/sample-keywords.json
- Content_MultiAgent/tests/test_demo_inputs.py

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
- 2026-05-22: Started implementation; status moved to in-progress.
- 2026-05-22: Added stable demo inputs and metadata; status moved to review.
- 2026-05-22: Code review passed; status moved to done.
