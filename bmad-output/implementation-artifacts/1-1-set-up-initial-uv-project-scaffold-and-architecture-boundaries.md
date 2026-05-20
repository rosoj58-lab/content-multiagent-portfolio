# Story 1.1: Set Up Initial uv Project Scaffold and Architecture Boundaries

Status: review

## Story

As a project owner,
I want a runnable Python project scaffold with the approved directory structure,
so that future stories can be implemented in stable, reviewable locations.

## Acceptance Criteria

1. Given the repository root is empty of application code, when the scaffold is created, then `pyproject.toml`, `uv.lock`, `app.py`, `.env.example`, `.gitignore`, `src/seo_content_pipeline/`, `tests/`, `docs/`, `examples/`, and `artifacts/` exist.
2. All Python package directories contain `__init__.py`.
3. `.gitignore` excludes `.env` and generated artifacts under `artifacts/jobs/`.
4. `uv run pytest` can discover the test suite.

## Scope Clarification

- Treat `/Users/irinawork/bmad_projects/Content_MultiAgent` as the application root for this story.
- Treat `/Users/irinawork/bmad_projects` as the Git/Compose root. Do not move the Git repository.
- The application root is not literally empty: BMad files, Docker files and `docs/docker.md` already exist. Preserve them.
- This story creates the scaffold and architecture guardrails only. Do not implement real workflow behavior, models, graph nodes, providers or LLM calls beyond empty modules/placeholders needed for imports and tests.
- Existing Docker/Compose setup must still work after the scaffold exists.

## Tasks / Subtasks

- [x] Initialize uv project metadata in `Content_MultiAgent` (AC: 1, 4)
  - [x] Run or reproduce the architecture-approved scaffold intent: `uv init --app --package --python 3.12 --name seo-content-pipeline --vcs none .`
  - [x] Ensure `pyproject.toml`, `.python-version`, `uv.lock`, `README.md` and package metadata are created in `Content_MultiAgent`.
  - [x] If `uv init` creates `main.py`, replace it with the required `app.py` entrypoint instead of keeping duplicate entrypoints.
  - [x] Add runtime dependencies: `streamlit`, `langgraph`, `langchain`, `langchain-openai`, `pydantic`, `python-dotenv`.
  - [x] Add dev dependencies: `pytest`, `ruff`, `mypy`.

- [x] Create the approved source tree skeleton (AC: 1, 2)
  - [x] Create `src/seo_content_pipeline/` with `__init__.py`.
  - [x] Create subpackages with `__init__.py`: `models/`, `graph/`, `graph/nodes/`, `services/`, `validators/`, `providers/`, `prompts/`, `ui/`.
  - [x] Create placeholder modules from the architecture tree: `config.py`, model modules, graph modules, service modules, validator modules, provider modules, prompt modules and UI modules.
  - [x] Keep placeholder modules minimal: docstring or explicit `TODO` comment only, no fake business logic.

- [x] Create required app, docs, examples and artifact folders (AC: 1, 3)
  - [x] Create `app.py` as a minimal Streamlit entrypoint that can import and render without touching graph nodes, prompts, validators or provider implementations.
  - [x] Create `tests/` with `__init__.py`, `conftest.py`, `test_architecture_boundaries.py` and a scaffold/test-discovery smoke test.
  - [x] Preserve existing `docs/docker.md`; add missing docs placeholders required by architecture: `architecture-summary.md`, `artifact-map.md`, `demo-script.md`, `demo-setup.md`, `project-structure.md`.
  - [x] Create `examples/briefs/`, `examples/inputs/`, `examples/outputs/` with `.gitkeep` or placeholder README files only.
  - [x] Create `artifacts/demo/.gitkeep` and `artifacts/jobs/.gitkeep`.

- [x] Add environment and ignore-file guardrails (AC: 1, 3)
  - [x] Create `Content_MultiAgent/.env.example` with documented empty placeholders for `OPENAI_API_KEY`, `COPYLEAKS_EMAIL`, `COPYLEAKS_API_KEY`, `APP_MODE`, `UNIQUENESS_PROVIDER`, `MAX_REVISION_ATTEMPTS` and artifact root settings.
  - [x] Add or update `Content_MultiAgent/.gitignore` so `.env`, `.env.*`, virtualenvs, Python caches and generated `artifacts/jobs/*` / `artifacts/demo/*` are ignored while `.gitkeep` files remain tracked.
  - [x] Confirm parent `/Users/irinawork/bmad_projects/.gitignore` still protects secrets and generated artifacts.

- [x] Add architecture-boundary tests and test discovery (AC: 2, 4)
  - [x] `test_architecture_boundaries.py` must parse `app.py` and fail if it imports `seo_content_pipeline.graph.nodes`, `seo_content_pipeline.prompts`, `seo_content_pipeline.validators` or provider implementation modules directly.
  - [x] Add a scaffold smoke test that verifies required directories/files exist and package dirs have `__init__.py`.
  - [x] Ensure `uv run pytest` discovers and runs tests successfully.
  - [x] If host `uv` is unavailable, run the same verification through Docker: `docker compose run --rm app uv run pytest`.

- [x] Verify developer commands and Docker compatibility (AC: 4)
  - [x] Run `uv run pytest`.
  - [x] Run `uv run ruff check .`.
  - [x] Run `docker compose build` from `/Users/irinawork/bmad_projects`.
  - [x] Run `docker compose run --rm app uv run pytest` from `/Users/irinawork/bmad_projects`.
  - [x] Do not leave long-running containers active after verification; use `docker compose down` if needed.

## Dev Notes

### Current Repository State

- Git root: `/Users/irinawork/bmad_projects`.
- Application root: `/Users/irinawork/bmad_projects/Content_MultiAgent`.
- BMad planning artifacts live outside the app root under `/Users/irinawork/bmad_projects/bmad-output`.
- Existing project infrastructure to preserve:
  - `/Users/irinawork/bmad_projects/compose.yaml`
  - `/Users/irinawork/bmad_projects/Content_MultiAgent/Dockerfile`
  - `/Users/irinawork/bmad_projects/Content_MultiAgent/.dockerignore`
  - `/Users/irinawork/bmad_projects/Content_MultiAgent/docs/docker.md`
- `compose.yaml` mounts `./Content_MultiAgent` to `/app` and `./bmad-output` to `/bmad-output`. After `pyproject.toml` exists, Compose will run `uv sync` before starting Streamlit.

### Architecture Requirements

- Use Python 3.12 and uv.
- Streamlit is the local UI, but `app.py` must stay thin.
- LangGraph will be the workflow engine in later stories; do not implement graph behavior here.
- Pydantic v2 will be used for cross-node contracts in later stories.
- File-based artifacts will live under `artifacts/jobs/{job_id}/`.
- No FastAPI, external API layer, auth or graph checkpointing in MVP.
- `.env` is local only and must never be committed.
- Copyleaks must remain optional; this story must not add required Copyleaks SDK imports or credentials.

### Required Project Structure

Create this structure inside `Content_MultiAgent` where missing:

```text
app.py
README.md
pyproject.toml
uv.lock
.python-version
.env.example
.gitignore
artifacts/
  demo/
    .gitkeep
  jobs/
    .gitkeep
docs/
  architecture-summary.md
  artifact-map.md
  demo-script.md
  demo-setup.md
  docker.md
  project-structure.md
examples/
  briefs/
  inputs/
  outputs/
src/
  seo_content_pipeline/
    __init__.py
    config.py
    models/
      __init__.py
      artifacts.py
      content.py
      errors.py
      job.py
      qa_result.py
      stage.py
      uniqueness.py
      validation.py
    graph/
      __init__.py
      builder.py
      routing.py
      state.py
      nodes/
        __init__.py
        brief_node.py
        final_qa_node.py
        localization_node.py
        seo_node.py
        uniqueness_node.py
        writer_node.py
    services/
      __init__.py
      artifact_store.py
      exporters.py
      job_service.py
      llm_client.py
      llm_runner.py
      stage_view_builder.py
    validators/
      __init__.py
      artifact_validators.py
      revision_validators.py
      seo_validators.py
    providers/
      __init__.py
      base.py
      manual_uniqueness.py
      mock_uniqueness.py
      copyleaks_uniqueness.py
    prompts/
      __init__.py
      brief.py
      localization.py
      qa_prompt.py
      writer.py
    ui/
      __init__.py
      artifact_panel.py
      components.py
      empty_states.py
      error_presenter.py
      progress_timeline.py
      renderers.py
tests/
  __init__.py
  conftest.py
  test_architecture_boundaries.py
```

### Boundary Rules For This Story

- `app.py` may import `streamlit` and future-safe public package/UI helpers only.
- `app.py` must not import graph nodes, prompts, validators, or provider implementation modules.
- Placeholder modules must not create fake data contracts. Story 1.2 owns real models and artifact registry.
- Placeholder provider modules must not import external SDKs or require credentials.
- Do not store generated job output in Git. Only `.gitkeep` placeholders under artifact directories are tracked.

### Testing Requirements

- `uv run pytest` must pass or, at minimum for AC #4, discover and execute the scaffold tests.
- Recommended tests:
  - required scaffold paths exist;
  - every Python package directory under `src/seo_content_pipeline` has `__init__.py`;
  - artifact `.gitkeep` files exist;
  - `app.py` avoids forbidden direct imports.
- `ruff check .` should pass after scaffold.
- Do not add brittle tests that depend on a real Streamlit server, LLM credentials or network access.

### Latest Technical Notes

- uv projects are managed through `pyproject.toml`; uv creates `uv.lock` after `uv run`, `uv sync` or `uv lock`, and the lockfile should be committed for reproducible installs.
- `uv add` updates dependencies and lockfile; use it instead of manually editing dependency lists unless a targeted edit is clearer.
- Streamlit apps run with `streamlit run <entrypoint>`. Our entrypoint is `app.py`.
- LangGraph currently requires Python 3.10+ and installs separately from provider integrations; provider packages such as `langchain-openai` must be explicit dependencies.
- Pydantic v2 is the architecture target. Use current stable Pydantic v2 resolved by `uv.lock`; do not use Pydantic v1 APIs.

## References

- [Architecture: Selected Starter and dependencies](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Architecture: project structure and boundaries](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md)
- [Epics: Story 1.1 acceptance criteria](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/epics.md)
- [PRD: MVP vision and local Streamlit app](/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md)
- [Docker Compose project setup](/Users/irinawork/bmad_projects/compose.yaml)
- [Dockerfile](/Users/irinawork/bmad_projects/Content_MultiAgent/Dockerfile)
- uv official docs: https://docs.astral.sh/uv/guides/projects/
- Streamlit official CLI docs: https://docs.streamlit.io/develop/api-reference/cli/run
- LangGraph official install docs: https://docs.langchain.com/oss/python/langgraph/install
- Pydantic official install docs: https://pydantic.dev/docs/validation/2.9/get-started/install/

## Story Context Quality Review

- Critical issues found: 0.
- Enhancements applied in this story file: clarified app root vs Git root, preserved existing Docker/BMad files, added Docker verification path, and constrained placeholder modules so later stories own real behavior.
- Optimization applied: task list is path-oriented and acceptance-criteria mapped so the dev agent can implement without guessing.

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Debug Log References

- `docker compose run --rm app uv lock` resolved 87 packages and created `uv.lock`.
- `docker compose run --rm app uv run pytest` passed: 3 tests collected, 3 passed.
- `docker compose run --rm app uv run ruff check .` passed after excluding BMad service folders via `tool.ruff.extend-exclude`.
- `docker compose build` passed using Docker Compose classic builder with a temporary Docker config because Docker Desktop credential helper hung during public image metadata lookup.
- `docker compose run --rm app uv run pytest` passed again after Docker build.

### Completion Notes List

- Created the Python 3.12 uv scaffold in `Content_MultiAgent` with `pyproject.toml`, `.python-version`, `uv.lock`, `README.md`, `.env.example`, `.gitignore` and `app.py`.
- Added the approved package tree under `src/seo_content_pipeline` with minimal placeholder modules and `__init__.py` files for every package directory.
- Added docs, examples and artifact placeholder folders while preserving existing Docker documentation.
- Added scaffold and architecture-boundary tests; `app.py` stays thin and avoids forbidden implementation-layer imports.
- Adjusted Docker development setup by adding `UV_LINK_MODE=copy` in Compose and removing build-time `uv sync` from Dockerfile so the dev image builds reliably while runtime `uv sync` still handles dependencies.

### File List

- Content_MultiAgent/.env.example
- Content_MultiAgent/.gitignore
- Content_MultiAgent/.python-version
- Content_MultiAgent/Dockerfile
- Content_MultiAgent/README.md
- Content_MultiAgent/app.py
- Content_MultiAgent/artifacts/demo/.gitkeep
- Content_MultiAgent/artifacts/jobs/.gitkeep
- Content_MultiAgent/docs/architecture-summary.md
- Content_MultiAgent/docs/artifact-map.md
- Content_MultiAgent/docs/demo-script.md
- Content_MultiAgent/docs/demo-setup.md
- Content_MultiAgent/docs/project-structure.md
- Content_MultiAgent/examples/briefs/.gitkeep
- Content_MultiAgent/examples/inputs/.gitkeep
- Content_MultiAgent/examples/outputs/README.md
- Content_MultiAgent/pyproject.toml
- Content_MultiAgent/src/seo_content_pipeline/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/config.py
- Content_MultiAgent/src/seo_content_pipeline/graph/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/graph/builder.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/brief_node.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/final_qa_node.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/localization_node.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/seo_node.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/uniqueness_node.py
- Content_MultiAgent/src/seo_content_pipeline/graph/nodes/writer_node.py
- Content_MultiAgent/src/seo_content_pipeline/graph/routing.py
- Content_MultiAgent/src/seo_content_pipeline/graph/state.py
- Content_MultiAgent/src/seo_content_pipeline/models/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py
- Content_MultiAgent/src/seo_content_pipeline/models/content.py
- Content_MultiAgent/src/seo_content_pipeline/models/errors.py
- Content_MultiAgent/src/seo_content_pipeline/models/job.py
- Content_MultiAgent/src/seo_content_pipeline/models/qa_result.py
- Content_MultiAgent/src/seo_content_pipeline/models/stage.py
- Content_MultiAgent/src/seo_content_pipeline/models/uniqueness.py
- Content_MultiAgent/src/seo_content_pipeline/models/validation.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/brief.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/localization.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/qa_prompt.py
- Content_MultiAgent/src/seo_content_pipeline/prompts/writer.py
- Content_MultiAgent/src/seo_content_pipeline/providers/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/providers/base.py
- Content_MultiAgent/src/seo_content_pipeline/providers/copyleaks_uniqueness.py
- Content_MultiAgent/src/seo_content_pipeline/providers/manual_uniqueness.py
- Content_MultiAgent/src/seo_content_pipeline/providers/mock_uniqueness.py
- Content_MultiAgent/src/seo_content_pipeline/services/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/services/artifact_store.py
- Content_MultiAgent/src/seo_content_pipeline/services/exporters.py
- Content_MultiAgent/src/seo_content_pipeline/services/job_service.py
- Content_MultiAgent/src/seo_content_pipeline/services/llm_client.py
- Content_MultiAgent/src/seo_content_pipeline/services/llm_runner.py
- Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py
- Content_MultiAgent/src/seo_content_pipeline/ui/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/ui/artifact_panel.py
- Content_MultiAgent/src/seo_content_pipeline/ui/components.py
- Content_MultiAgent/src/seo_content_pipeline/ui/empty_states.py
- Content_MultiAgent/src/seo_content_pipeline/ui/error_presenter.py
- Content_MultiAgent/src/seo_content_pipeline/ui/progress_timeline.py
- Content_MultiAgent/src/seo_content_pipeline/ui/renderers.py
- Content_MultiAgent/src/seo_content_pipeline/validators/__init__.py
- Content_MultiAgent/src/seo_content_pipeline/validators/artifact_validators.py
- Content_MultiAgent/src/seo_content_pipeline/validators/revision_validators.py
- Content_MultiAgent/src/seo_content_pipeline/validators/seo_validators.py
- Content_MultiAgent/tests/__init__.py
- Content_MultiAgent/tests/conftest.py
- Content_MultiAgent/tests/test_architecture_boundaries.py
- Content_MultiAgent/tests/test_scaffold_structure.py
- Content_MultiAgent/uv.lock
- bmad-output/implementation-artifacts/1-1-set-up-initial-uv-project-scaffold-and-architecture-boundaries.md
- bmad-output/implementation-artifacts/sprint-status.yaml
- compose.yaml

### Change Log

- 2026-05-20: Story created by BMad create-story workflow.
- 2026-05-20: Implemented scaffold, tests, Docker compatibility adjustments and moved story to review.
