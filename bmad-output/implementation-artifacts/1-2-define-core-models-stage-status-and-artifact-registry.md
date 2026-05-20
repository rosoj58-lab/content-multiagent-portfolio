# Story 1.2: Define Core Models, Stage/Status, and Artifact Registry

Status: done

## Story

As a developer,
I want typed contracts for workflow stages, statuses, artifacts, validation checks, errors, QA reports and job metadata,
so that graph nodes, services and UI share the same vocabulary.

## Acceptance Criteria

1. Given the scaffold exists, when core models are implemented, then `WorkflowStage`, `WorkflowStatus`, `ArtifactKey`, `ValidationCheck`, `WorkflowError`, `QAReport`, `StageView`, and job metadata models exist.
2. `WorkflowStage` is separate from `WorkflowStatus`; stages represent pipeline locations, statuses represent execution/control outcomes.
3. Artifact registry maps each artifact key to filename, content type, UI label and description.
4. `test_artifact_registry.py` verifies registry completeness and filename conventions.

## Scope Clarification

- Implement typed contracts only. Do not implement `ArtifactStore`, `JobService`, graph execution, UI rendering, providers, validators or LLM calls in this story.
- Keep models pure and import-light: model modules may depend on standard library and Pydantic only.
- Treat `/Users/irinawork/bmad_projects/Content_MultiAgent` as the application root and `/Users/irinawork/bmad_projects` as the Git/Compose root.
- Preserve the thin `app.py` boundary from Story 1.1.

## Tasks / Subtasks

- [x] Implement workflow stage and status contracts (AC: 1, 2)
  - [x] Replace the placeholder in `src/seo_content_pipeline/models/stage.py` with `WorkflowStage`, `WorkflowStatus`, and `StageView`.
  - [x] Use enum/string constants, not ad hoc literals.
  - [x] Include stage/status values from architecture: input/brief/writing/review/SEO/uniqueness/localization/final QA and running/waiting/approved/revision/human-review/failed statuses.

- [x] Implement artifact key enum and registry (AC: 1, 3, 4)
  - [x] Replace the placeholder in `src/seo_content_pipeline/models/artifacts.py` with `ArtifactKey`, an `ArtifactSpec` Pydantic model, and one registry constant/dict.
  - [x] Registry entries must include filename, content type, UI label and description.
  - [x] Include required keys: `input`, `state`, `brief`, `english_original`, `editorial_qa`, `seo_qa`, `uniqueness`, `localization_es`, `localization_it`, `localization_fr`, `final_package_md`, `final_package_json`.
  - [x] Keep filename conventions explicit and stable; JSON artifacts should end in `.json`, Markdown artifacts should end in `.md`.

- [x] Implement validation, QA, error and job metadata models (AC: 1)
  - [x] Replace placeholders in `models/validation.py`, `models/qa_result.py`, `models/errors.py`, and `models/job.py`.
  - [x] `ValidationCheck` should include `name`, `passed`, `severity`, `message`, and metadata with a safe default factory.
  - [x] `QAReport` should include `job_id`, `stage`, `passed`, optional score, checks, recommendations, optional routing target, and summary.
  - [x] `WorkflowError` should include code, message, node, stage, recoverability, details, and created timestamp.
  - [x] Add job metadata models for persisted job identity/status/history that Story 1.3 can reuse for `metadata.json` and `state.json`.

- [x] Expose public model API carefully (AC: 1)
  - [x] Update `src/seo_content_pipeline/models/__init__.py` to export only stable public contracts from this story.
  - [x] Avoid circular imports between model modules.
  - [x] Do not modify placeholder provider, graph node, prompt or UI behavior.

- [x] Add focused tests (AC: 2, 3, 4)
  - [x] Add `tests/test_artifact_registry.py`.
  - [x] Add or extend tests to verify stage/status separation, registry completeness, unique filenames and content-type/extension consistency.
  - [x] Verify model defaults do not share mutable state between instances.
  - [x] Ensure `uv run pytest` and `uv run ruff check .` pass, using Docker if host `uv` is unavailable.

### Review Findings

- [x] [Review][Patch] Add metadata artifact key to registry before Story 1.3 [Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py:8] — resolved by adding `ArtifactKey.METADATA`, a `metadata.json` registry entry and a focused test for job shell artifacts.

## Dev Notes

### Current Repository State

- Story 1.1 created the full scaffold and left model files as placeholders with docstrings only.
- `app.py` currently imports only Streamlit and must remain thin.
- Existing architecture-boundary tests check that `app.py` does not directly import graph nodes, prompts, validators or provider implementations.
- Docker build verification previously required a temporary Docker config because Docker Desktop credential helper returned an API error during public image metadata lookup; this is an environment issue, not a repository requirement.

### Architecture Requirements

- Use Python 3.12 and Pydantic v2.
- Pydantic models are the cross-node contracts.
- Full generated content will live in artifacts; graph state should stay lightweight.
- JSON artifacts use `snake_case` fields and should be serializable through Pydantic `model_dump()` / JSON serialization.
- `ArtifactKey` and filenames must be centralized in one registry, not scattered strings.
- Deterministic validators will later return `list[ValidationCheck]`; this story defines the contract only.
- `StageView` is the UI-ready object that Streamlit will later render for timeline entries, manual gates and failure states.

### Required Model Locations

```text
src/seo_content_pipeline/models/
  __init__.py
  artifacts.py
  errors.py
  job.py
  qa_result.py
  stage.py
  validation.py
tests/
  test_artifact_registry.py
```

### Suggested Contract Shapes

Use these as the implementation baseline unless a cleaner equivalent preserves the same fields:

```python
class ValidationCheck(BaseModel):
    name: str
    passed: bool
    severity: Literal["info", "warning", "error"]
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
```

```python
class QAReport(BaseModel):
    job_id: str
    stage: WorkflowStage
    passed: bool
    score: float | None = None
    checks: list[ValidationCheck]
    recommendations: list[str] = Field(default_factory=list)
    routing_target: WorkflowStage | None = None
    summary: str
```

```python
class StageView(BaseModel):
    stage: WorkflowStage
    status: WorkflowStatus
    label: str
    description: str
    artifact_links: list[ArtifactKey] = Field(default_factory=list)
    available_actions: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    recoverable: bool = True
    revision_attempt: int | None = None
    max_revision_attempts: int | None = None
```

### Previous Story Intelligence

- Story 1.1 established the project root split: app code under `Content_MultiAgent`, Git and Compose one level above.
- Use existing placeholder modules; replace placeholders only where this story owns the real contracts.
- Keep code small and deterministic. Do not introduce fake workflow behavior just to make tests pass.
- Existing verification path is `docker compose run --rm app uv run pytest` from `/Users/irinawork/bmad_projects` when host tools are unavailable.

### Latest Technical Notes

- Python 3.12 supports string-compatible enum usage through `StrEnum`, but the architecture examples use `class X(str, Enum)`. Either is acceptable if values serialize as strings and tests confirm string values.
- Pydantic v2 no longer treats all optional-looking annotations as implicit defaults; explicitly assign defaults for optional fields and use `Field(default_factory=...)` for mutable defaults.

## References

- [Architecture: workflow stages, statuses and artifact registry](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Architecture: model, validation and StageView contracts](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Architecture: source and test organization](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Epics: Story 1.2 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [Story 1.1 implementation notes](/Users/irinawork/bmad_projects/bmad-output/implementation-artifacts/1-1-set-up-initial-uv-project-scaffold-and-architecture-boundaries.md)
- Python enum docs: https://docs.python.org/3.12/library/enum.html
- Pydantic v2 model docs: https://docs.pydantic.dev/latest/concepts/models/

## Story Context Quality Review

- Critical issues found: 0.
- Enhancements applied: clarified that Story 1.2 owns model contracts only, added exact file locations, public API expectations, mutable-default guardrails and registry filename rules.
- Optimization applied: task list maps directly to acceptance criteria and the architecture-defined contracts.

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Debug Log References

- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest tests/test_artifact_registry.py` passed: 5 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 8 tests.
- `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.
- Docker Compose still returned a Docker Desktop API 500 for the networks route; verification was completed with local `uv` and Python 3.12 instead.
- Post-review patch verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run pytest` passed: 9 tests.
- Post-review patch verification: `UV_PROJECT_ENVIRONMENT="$HOME/.cache/uv/seo-content-pipeline-macos" "$HOME/.local/bin/uv" run ruff check .` passed.

### Completion Notes List

- Implemented centralized `ArtifactKey` and `ARTIFACT_REGISTRY` with stable filenames, content types, UI labels and descriptions.
- Added `ArtifactKey.METADATA` and `metadata.json` registry support during code review so Story 1.3 can write all job shell artifacts through the registry.
- Implemented `WorkflowStage`, `WorkflowStatus`, `StageView`, `ValidationCheck`, `QAReport`, `WorkflowError`, `JobMetadata`, `StatusHistoryEntry`, `PipelineState` and `ArticleType`.
- Exported stable model contracts from `seo_content_pipeline.models`.
- Added registry/model tests covering stage/status separation, registry completeness, filename conventions and mutable default isolation.

### File List

- Content_MultiAgent/src/seo_content_pipeline/models/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py
- Content_MultiAgent/src/seo_content_pipeline/models/errors.py
- Content_MultiAgent/src/seo_content_pipeline/models/job.py
- Content_MultiAgent/src/seo_content_pipeline/models/qa_result.py
- Content_MultiAgent/src/seo_content_pipeline/models/stage.py
- Content_MultiAgent/src/seo_content_pipeline/models/validation.py
- Content_MultiAgent/tests/test_artifact_registry.py

## Change Log

- 2026-05-20: Implemented Story 1.2 core model contracts and artifact registry; status moved to review.
- 2026-05-20: Resolved code review finding for `metadata.json` artifact registry coverage; status moved to done.
