# Story 6.3: Document Interview Walkthrough and Artifact Map

Status: ready-for-dev

## Story

As a project owner,
I want demo setup, demo script, artifact map and architecture summary docs,
so that I can present the project confidently in interviews.

## Acceptance Criteria

1. Given the app and demo flows exist, when documentation is created, then `docs/demo-setup.md`, `docs/demo-script.md`, `docs/artifact-map.md`, `docs/architecture-summary.md` and `docs/project-structure.md` exist.
2. Docs explain happy path, revision path and human-review path.
3. Docs identify where artifacts are stored and how QA decisions are made.
4. FR17, FR18 and UX-DR6 are reinforced.

## Scope Clarification

- This story documents how to present and inspect the project; it does not add new runtime pipeline behavior.
- Docs should be concise enough to use during an interview.
- Docs should reference existing demo inputs and artifacts, not invent a different workflow.

## Tasks / Subtasks

- [ ] Expand demo setup documentation (AC: 1, 2)
  - [ ] Include local setup command.
  - [ ] Include BP happy path, LP revision path and GP human-review path.
  - [ ] Reference stable demo input files.

- [ ] Create interview demo script (AC: 2, 4)
  - [ ] Explain the opening pitch.
  - [ ] Walk through the three demo paths.
  - [ ] Include talking points for QA gates and human-in-the-loop decisions.

- [ ] Create artifact map (AC: 3)
  - [ ] Identify artifact storage location.
  - [ ] Map artifact filenames to pipeline stages and purpose.
  - [ ] Explain final package and final QA report.

- [ ] Create architecture and project structure summaries (AC: 3, 4)
  - [ ] Summarize local Streamlit app, services, models, validators, providers and artifacts.
  - [ ] Explain how FR17/FR18 routing and status are represented.
  - [ ] Keep project structure practical and inspectable.

- [ ] Add documentation tests (AC: 1-4)
  - [ ] Test required docs exist and are not placeholders.
  - [ ] Test docs mention happy path, revision path and human-review path.
  - [ ] Test artifact map mentions artifact root, state, final package and final QA report.
  - [ ] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- Story 6.1 added stable demo inputs and updated `docs/demo-setup.md`.
- Story 6.2 added observability UI surfaces and controlled error presentation.
- `docs/demo-script.md`, `docs/artifact-map.md`, `docs/architecture-summary.md` and `docs/project-structure.md` are still placeholders.

### Architecture Requirements

- FR17: workflow status reflects current pipeline state and revision routing.
- FR18: failed checks route to the relevant agent or stage.
- UX-DR6: reproducible demo flows for happy path, revision path and human-review path.

### Implementation Guidance

- Keep docs accurate to the current local MVP.
- Do not claim hosted deployment, live SERP research, CMS publishing or production Copyleaks dependency.
- Use exact artifact filenames from `ArtifactKey` registry.
- Keep docs ASCII-only.

### Testing Requirements

- Add `tests/test_interview_docs.py`.
- Existing tests must keep passing.

## References

- [Epics: Story 6.3 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Story 6.1 stable demo inputs](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/6-1-add-stable-bp-lp-and-gp-demo-inputs.md)
- [Story 6.2 observability views](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/6-2-implement-demo-observability-views.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 6 and current docs/demo state.

### Completion Notes List

- Pending implementation.

### File List

- Pending implementation.

## Change Log

- 2026-05-22: Created story and moved status to ready-for-dev.
