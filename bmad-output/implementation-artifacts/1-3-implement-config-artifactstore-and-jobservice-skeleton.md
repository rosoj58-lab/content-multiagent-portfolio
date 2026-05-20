# Story 1.3: Implement Config, ArtifactStore, and JobService Skeleton

Status: review

## Story

As an operator,
I want the app to create and inspect a demo job shell,
so that the local demo has a durable source of truth before real agent stages are added.

## Acceptance Criteria

1. Given `.env.example` and `config.py` exist, when the app creates a new job through `JobService.create_job()`, then `artifacts/jobs/{job_id}/metadata.json`, `input.json`, and `state.json` are written through `ArtifactStore`.
2. `config.py` is the only module that reads environment variables.
3. Artifact writes use the artifact registry.
4. `test_config.py`, `test_artifact_store.py`, and `test_job_service.py` cover default config, job creation and artifact persistence.

## Scope Clarification

- Implement a durable job shell only. Do not implement LangGraph execution, LLM calls, Streamlit forms, providers, validators, or real content generation in this story.
- Use the Story 1.2 model contracts instead of creating parallel dict shapes.
- Treat `/Users/irinawork/bmad_projects/Content_MultiAgent` as the application root and `/Users/irinawork/bmad_projects` as the Git/Compose root.
- Keep `app.py` thin and unchanged unless a test proves an import boundary regression.

## Tasks / Subtasks

- [x] Implement typed application settings in `config.py` (AC: 2, 4)
  - [x] Read environment variables only inside `src/seo_content_pipeline/config.py`.
  - [x] Load `.env` through `python-dotenv` if present.
  - [x] Expose an `AppSettings` Pydantic model or equivalent typed object with defaults for `APP_MODE`, `ARTIFACT_ROOT`, `BMAD_OUTPUT_DIR`, `MAX_REVISION_ATTEMPTS`, `UNIQUENESS_PROVIDER`, `OPENAI_API_KEY`, `COPYLEAKS_EMAIL`, and `COPYLEAKS_API_KEY`.
  - [x] Missing OpenAI/Copyleaks credentials must not fail startup.
  - [x] Add `tests/test_config.py` covering defaults and env override behavior.

- [x] Implement `ArtifactStore` persistence (AC: 1, 3, 4)
  - [x] Replace the placeholder in `src/seo_content_pipeline/services/artifact_store.py`.
  - [x] Resolve job artifact paths as `{artifact_root}/{job_id}/{registry filename}` using `ArtifactKey` and `ARTIFACT_REGISTRY`.
  - [x] Write Pydantic models and plain mappings as JSON with `model_dump(mode="json")` where applicable.
  - [x] Use atomic writes where practical: write to a temp file in the target directory, then replace the final path.
  - [x] Add read helpers for JSON artifacts that will be useful for `JobService`.
  - [x] Add `tests/test_artifact_store.py` covering path resolution, registry-based writes, persistence, and atomic replacement behavior.

- [x] Implement `JobService.create_job()` skeleton (AC: 1, 3, 4)
  - [x] Replace the placeholder in `src/seo_content_pipeline/services/job_service.py`.
  - [x] Accept dry input, optional `ArticleType`, and settings/artifact store dependencies.
  - [x] Reject empty or whitespace-only dry input with a clear `ValueError`.
  - [x] Create a unique job ID that is filesystem-safe and stable enough for demo use.
  - [x] Write `metadata.json`, `input.json`, and `state.json` through `ArtifactStore` using `ArtifactKey.METADATA`, `ArtifactKey.INPUT`, and `ArtifactKey.STATE`.
  - [x] Return a small result object or `JobMetadata` plus artifact path references that Story 1.4 can use.
  - [x] Add `tests/test_job_service.py` covering job creation, required artifacts, persisted state, and empty-input rejection.

- [x] Preserve architecture boundaries and run verification (AC: 2, 4)
  - [x] Ensure no modules other than `config.py` call `os.getenv`, `os.environ`, or `dotenv`.
  - [x] Do not read/write artifacts directly outside `ArtifactStore`.
  - [x] Run full `pytest` and `ruff check .`.
  - [x] Update this story's Dev Agent Record and File List when complete.

## Dev Notes

### Current Repository State

- Story 1.1 created placeholders for `config.py`, `services/artifact_store.py`, and `services/job_service.py`.
- Story 1.2 implemented `ArtifactKey.METADATA`, `ArtifactKey.INPUT`, `ArtifactKey.STATE`, `ARTIFACT_REGISTRY`, `JobMetadata`, `PipelineState`, `StatusHistoryEntry`, `ArticleType`, `WorkflowStage`, and `WorkflowStatus`.
- Story 1.2 code review explicitly added `metadata.json` registry support so this story can write all job shell artifacts through the registry.
- `.env.example` already documents `APP_MODE`, `ARTIFACT_ROOT`, `BMAD_OUTPUT_DIR`, `MAX_REVISION_ATTEMPTS`, `OPENAI_API_KEY`, `UNIQUENESS_PROVIDER`, `COPYLEAKS_EMAIL`, and `COPYLEAKS_API_KEY`.
- Local verification can use:
  `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest`

### Architecture Requirements

- Use file-based storage under `artifacts/jobs/{job_id}/`.
- `config.py` is the only module that reads environment variables and settings.
- `JobService` is the facade between Streamlit and workflow execution.
- `ArtifactStore` is the only layer that reads/writes artifacts.
- Artifact writes must use the artifact registry and should be atomic where practical.
- `JobService.create_job()` writes `input.json`, `state.json`, and job metadata before real graph stages exist.
- No FastAPI, external API server, auth, graph checkpointing, LLM calls, or provider network calls in this story.

### Implementation Guidance

- Prefer constructor injection:
  - `settings = get_settings()`
  - `store = ArtifactStore(settings.artifact_root)`
  - `service = JobService(settings=settings, artifact_store=store)`
- Use `Path` internally for filesystem paths, but keep serialized JSON values simple strings/enums.
- Keep input artifact minimal and explicit: `job_id`, `created_at`, `stage`, `dry_input`, `article_type`.
- Initial state should be lightweight and based on `PipelineState`, not full content.
- Initial stage should be `WorkflowStage.INPUT_RECEIVED`; initial status can be `WorkflowStatus.WAITING_FOR_HUMAN` or `WorkflowStatus.RUNNING` if the test/story documents the choice.

### Testing Requirements

- `test_config.py`: default settings, env override, missing credentials do not raise, `config.py` as the only env-reading module.
- `test_artifact_store.py`: registry path resolution, JSON write/read, Pydantic serialization, no direct hardcoded filenames in service code.
- `test_job_service.py`: creates all three required artifacts, uses registry keys, rejects empty input, persists `JobMetadata` and `PipelineState` shape.
- Existing tests must keep passing.

## References

- [Architecture: configuration boundary](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Architecture: data flow and job directory contract](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Epics: Story 1.3 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Story 1.2 completed model contracts](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/1-2-define-core-models-stage-status-and-artifact-registry.md)

## Story Context Quality Review

- Critical issues found: 0.
- Enhancements applied: carried forward the Story 1.2 review fix for `metadata.json`, clarified dependency injection boundaries, added env-reading guardrail and atomic write requirement.
- Optimization applied: tasks map directly to config, artifact store, job service and verification responsibilities.

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_config.py tests/test_artifact_store.py tests/test_job_service.py` passed: 8 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 17 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.

### Completion Notes List

- Implemented typed `AppSettings` and `get_settings()` in `config.py`; missing OpenAI/Copyleaks credentials remain valid defaults.
- Implemented registry-backed `ArtifactStore` with JSON read/write, Pydantic serialization and temp-file replacement.
- Implemented `JobService.create_job()` with whitespace input rejection, filesystem-safe job IDs and persisted `metadata.json`, `input.json`, and `state.json`.
- Added focused tests for config defaults/overrides, env-reading boundary, artifact persistence and job shell creation.

### File List

- Content_MultiAgent/src/seo_content_pipeline/config.py
- Content_MultiAgent/src/seo_content_pipeline/services/artifact_store.py
- Content_MultiAgent/src/seo_content_pipeline/services/job_service.py
- Content_MultiAgent/tests/test_artifact_store.py
- Content_MultiAgent/tests/test_config.py
- Content_MultiAgent/tests/test_job_service.py

## Change Log

- 2026-05-20: Implemented Story 1.3 config, artifact store and job service skeleton; status moved to review.
