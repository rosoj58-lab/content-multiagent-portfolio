# Story 4.4: Stub Optional Copyleaks Provider Safely

Status: done

## Story

As a project owner,
I want a safe optional Copyleaks integration seam,
so that the portfolio can show extensibility without making the MVP depend on external services.

## Acceptance Criteria

1. Given Copyleaks credentials are absent, when the app imports providers and starts, then no Copyleaks SDK, network access or credentials are required.
2. Copyleaks provider reports disabled/unconfigured status when credentials are absent.
3. Tests verify optional import safety.
4. FR10 is represented as deferred/optional without blocking manual/mock flow.

## Scope Clarification

- This story does not implement Copyleaks API submission.
- This story must not add a Copyleaks SDK dependency.
- This story must not make network calls.
- Manual and mock uniqueness provider flows must remain unaffected.
- If credentials are present, the provider may report configured, but production submission remains deferred until a later integration story.

## Tasks / Subtasks

- [x] Strengthen Copyleaks provider stub metadata (AC: 2, 4)
  - [x] Add explicit provider implementation/deferred status metadata.
  - [x] Report missing credentials as unconfigured/disabled.
  - [x] Report FR10 production submission as deferred/optional.
  - [x] Preserve existing manual/mock provider behavior.

- [x] Verify import and startup safety (AC: 1, 3)
  - [x] Ensure provider module imports without Copyleaks SDK installed.
  - [x] Ensure provider module does not read environment variables directly.
  - [x] Ensure provider option lookup does not perform network calls.
  - [x] Keep credentials access centralized in `config.py`.

- [x] Add focused tests (AC: 1-4)
  - [x] Test Copyleaks provider import safety without SDK.
  - [x] Test absent credentials produce disabled/unconfigured status.
  - [x] Test configured credentials still mark production submission as deferred/optional.
  - [x] Test manual/mock options remain available when Copyleaks is unconfigured.
  - [x] Run full `pytest` and `ruff check .`.

## Dev Notes

### Current Repository State

- `providers/copyleaks_uniqueness.py` already avoids SDK imports and network calls.
- `AppSettings` already contains `copyleaks_email` and `copyleaks_api_key`.
- `get_settings()` is the only allowed environment reader.
- `UniquenessProviderOption` currently includes name, label, availability, configured state, reason and manual-score flag.
- Existing tests already cover basic unavailable/available Copyleaks metadata and config startup without credentials.

### Architecture Requirements

- FR10: system can submit English Original to Copyleaks when provider is enabled, but MVP keeps this optional/deferred.
- NFR6: credentials must be read from environment or ignored local config, never committed.
- NFR7: app must run end-to-end without Copyleaks credentials by using manual uniqueness input.
- Architecture explicitly warns against making Copyleaks required for app startup.

### Implementation Guidance

- Prefer extending `UniquenessProviderOption` with explicit status fields rather than adding a new report schema.
- Do not import or add a Copyleaks SDK dependency.
- Do not implement `check()` network behavior in this story.
- Keep provider implementations isolated under `src/seo_content_pipeline/providers/`.
- Keep `app.py` thin and free of direct provider implementation imports.

### Testing Requirements

- Extend `tests/test_uniqueness_providers.py`.
- Existing tests must keep passing.
- Keep `tests/test_config.py::test_config_module_is_only_source_file_that_reads_environment` passing.
- Keep `tests/test_architecture_boundaries.py` passing.

## References

- [Epics: Story 4.4 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Architecture: Copyleaks optional provider constraints](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Story 4.1 provider selection](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/4-1-select-manual-or-mock-uniqueness-provider.md)
- [Story 4.3 uniqueness gate](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/4-3-gate-workflow-by-90-percent-threshold.md)

## Dev Agent Record

### Agent Model Used

GPT-5.5

### Debug Log References

- Story context created from Epic 4, architecture constraints, and existing Copyleaks provider stub.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_uniqueness_providers.py` red phase failed as expected before implementation.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_uniqueness_providers.py` passed: 17 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 104 tests.
- Code review clean: no patch or decision-needed findings; status moved to done.

### Completion Notes List

- Extended `UniquenessProviderOption` with provider implementation status, automated-check support and deferred reason metadata.
- Marked Copyleaks missing-credentials status as `unconfigured`.
- Marked configured Copyleaks production submission as `deferred` for MVP instead of pretending FR10 is fully implemented.
- Added import-safety test that fails if the Copyleaks SDK is imported by the stub provider.
- Confirmed manual/mock provider tests remain green.
- Code review passed without follow-up changes.

### File List

- Content_MultiAgent/src/seo_content_pipeline/models/uniqueness.py
- Content_MultiAgent/src/seo_content_pipeline/providers/copyleaks_uniqueness.py
- Content_MultiAgent/tests/test_uniqueness_providers.py

## Change Log

- 2026-05-21: Created story and moved status to ready-for-dev.
- 2026-05-21: Started implementation; status moved to in-progress.
- 2026-05-21: Implemented safe Copyleaks stub metadata; status moved to review.
- 2026-05-21: Code review passed; status moved to done.
