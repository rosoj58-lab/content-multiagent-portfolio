# Story 4.1: Select Manual or Mock Uniqueness Provider

Status: ready-for-dev

## Story

As an operator,
I want to select a manual or mock uniqueness provider,
so that the pipeline can run reliably without external plagiarism checker credentials.

## Acceptance Criteria

1. Given English QA has passed, when I open the uniqueness stage, then the UI/service layer offers manual and mock providers.
2. Copyleaks is shown as optional/unavailable unless configured.
3. Missing Copyleaks config does not fail app startup.
4. Provider selection is recorded in the job state and final report.
5. FR8, NFR6 and NFR7 are covered.

## Scope Clarification

- This story implements provider selection and availability only. It does not implement manual score entry or the 90 percent threshold gate; those belong to Stories 4.2 and 4.3.
- `manual` must be always available.
- `mock` must be available for demo/test use without external credentials.
- `copyleaks` must not import an SDK, make network calls or require credentials during app startup.
- The selected provider should be recorded in persisted workflow state in a way future stories can reuse for `uniqueness.json` and final reporting.

## Tasks / Subtasks

- [ ] Implement uniqueness provider contracts and availability (AC: 1, 2, 3, 5)
  - [ ] Define a Pydantic uniqueness provider option/status model.
  - [ ] Define a provider protocol/interface with provider name and availability.
  - [ ] Implement manual provider as always available.
  - [ ] Implement mock provider as available for demo/test use.
  - [ ] Implement Copyleaks provider as optional/unavailable without credentials.
  - [ ] Avoid required Copyleaks SDK imports, network access or credential reads outside config.

- [ ] Implement provider selection orchestration (AC: 1, 4)
  - [ ] Add a service that lists provider options for the uniqueness stage.
  - [ ] Add selection handling for `manual` and `mock`.
  - [ ] Reject unavailable providers with actionable errors.
  - [ ] Persist selected provider into `state.json`.
  - [ ] Update `metadata.json` status/history for the uniqueness stage.
  - [ ] Set a manual gate flag for the uniqueness stage.

- [ ] Add UI-facing status support (AC: 1, 2, 4)
  - [ ] Ensure stage view/manual gate data can represent the uniqueness provider-selection stop.
  - [ ] Expose provider options without importing implementation providers directly from `app.py`.

- [ ] Add focused tests (AC: 1-5)
  - [ ] Test manual and mock availability.
  - [ ] Test Copyleaks unavailable when credentials are missing.
  - [ ] Test app/settings startup with missing Copyleaks credentials.
  - [ ] Test provider selection persists selected provider in job state.
  - [ ] Test unavailable provider selection is rejected.
  - [ ] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- `config.py` already defines `UniquenessProviderName = Literal["manual", "mock", "copyleaks"]`.
- `AppSettings` already includes `uniqueness_provider`, `copyleaks_email` and `copyleaks_api_key`.
- `ArtifactKey.UNIQUENESS` already maps to `uniqueness.json`.
- `models/uniqueness.py`, `providers/base.py`, `providers/manual_uniqueness.py`, `providers/mock_uniqueness.py`, `providers/copyleaks_uniqueness.py` and `graph/nodes/uniqueness_node.py` are placeholders.
- Story 3.4 now ends at passed SEO QA and keeps the job moving toward uniqueness.

### Architecture Requirements

- FR8: operator can select manual uniqueness input or an enabled external plagiarism checker provider.
- NFR6: provider credentials must be read from environment variables or local ignored config, never committed.
- NFR7: app must run end-to-end without Copyleaks credentials by using manual uniqueness input.
- Provider selection must be explicit: `manual`, `mock` or `copyleaks`.
- Missing Copyleaks configuration must not fail app startup.
- Fallback must be visible; do not silently switch from Copyleaks to manual.

### Implementation Guidance

- Keep provider implementations isolated under `src/seo_content_pipeline/providers/`.
- Keep orchestration in a service; the Streamlit entrypoint must not import provider implementation modules directly.
- Prefer small Pydantic models over ad hoc dicts for provider options and future final-report reuse.
- Persist the selected provider in `PipelineState.qa_flags` or another existing state field without adding a broad migration unless necessary.
- Use `WorkflowStage.UNIQUENESS_CHECK`, `WorkflowStatus.WAITING_FOR_HUMAN`, `manual_gate_required=True` for the provider-selection gate.
- Do not create fake uniqueness scores in this story.

### Testing Requirements

- Add `tests/test_uniqueness_providers.py` for provider option behavior and Copyleaks safety.
- Add service tests for state/metadata persistence.
- Keep `tests/test_architecture_boundaries.py` passing; `app.py` must stay thin.
- Existing tests must keep passing.

## References

- [Epics: Story 4.1 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: Uniqueness providers](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 3.4 completed SEO QA](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/3-4-run-seo-qa-and-route-failures.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 4 and uniqueness-provider architecture.

### Completion Notes List

- Pending implementation.

### File List

- Pending implementation.

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
