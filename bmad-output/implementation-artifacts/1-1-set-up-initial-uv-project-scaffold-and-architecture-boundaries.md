# Story 1.1: Set Up Initial uv Project Scaffold and Architecture Boundaries

Status: ready-for-dev

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

- [ ] Initialize uv project metadata in `Content_MultiAgent` (AC: 1, 4)
  - [ ] Run or reproduce the architecture-approved scaffold intent: `uv init --app --package --python 3.12 --name seo-content-pipeline --vcs none .`
  - [ ] Ensure `pyproject.toml`, `.python-version`, `uv.lock`, `README.md` and package metadata are created in `Content_MultiAgent`.
  - [ ] If `uv init` creates `main.py`, replace it with the required `app.py` entrypoint instead of keeping duplicate entrypoints.
  - [ ] Add runtime dependencies: `streamlit`, `langgraph`, `langchain`, `langchain-openai`, `pydantic`, `python-dotenv`.
  - [ ] Add dev dependencies: `pytest`, `ruff`, `mypy`.

- [ ] Create the approved source tree skeleton (AC: 1, 2)
  - [ ] Create `src/seo_content_pipeline/` with `__init__.py`.
  - [ ] Create subpackages with `__init__.py`: `models/`, `graph/`, `graph/nodes/`, `services/`, `validators/`, `providers/`, `prompts/`, `ui/`.
  - [ ] Create placeholder modules from the architecture tree: `config.py`, model modules, graph modules, service modules, validator modules, provider modules, prompt modules and UI modules.
  - [ ] Keep placeholder modules minimal: docstring or explicit `TODO` comment only, no fake business logic.

- [ ] Create required app, docs, examples and artifact folders (AC: 1, 3)
  - [ ] Create `app.py` as a minimal Streamlit entrypoint that can import and render without touching graph nodes, prompts, validators or provider implementations.
  - [ ] Create `tests/` with `__init__.py`, `conftest.py`, `test_architecture_boundaries.py` and a scaffold/test-discovery smoke test.
  - [ ] Preserve existing `docs/docker.md`; add missing docs placeholders required by architecture: `architecture-summary.md`, `artifact-map.md`, `demo-script.md`, `demo-setup.md`, `project-structure.md`.
  - [ ] Create `examples/briefs/`, `examples/inputs/`, `examples/outputs/` with `.gitkeep` or placeholder README files only.
  - [ ] Create `artifacts/demo/.gitkeep` and `artifacts/jobs/.gitkeep`.

- [ ] Add environment and ignore-file guardrails (AC: 1, 3)
  - [ ] Create `Content_MultiAgent/.env.example` with documented empty placeholders for `OPENAI_API_KEY`, `COPYLEAKS_EMAIL`, `COPYLEAKS_API_KEY`, `APP_MODE`, `UNIQUENESS_PROVIDER`, `MAX_REVISION_ATTEMPTS` and artifact root settings.
  - [ ] Add or update `Content_MultiAgent/.gitignore` so `.env`, `.env.*`, virtualenvs, Python caches and generated `artifacts/jobs/*` / `artifacts/demo/*` are ignored while `.gitkeep` files remain tracked.
  - [ ] Confirm parent `/Users/irinawork/bmad_projects/.gitignore` still protects secrets and generated artifacts.

- [ ] Add architecture-boundary tests and test discovery (AC: 2, 4)
  - [ ] `test_architecture_boundaries.py` must parse `app.py` and fail if it imports `seo_content_pipeline.graph.nodes`, `seo_content_pipeline.prompts`, `seo_content_pipeline.validators` or provider implementation modules directly.
  - [ ] Add a scaffold smoke test that verifies required directories/files exist and package dirs have `__init__.py`.
  - [ ] Ensure `uv run pytest` discovers and runs tests successfully.
  - [ ] If host `uv` is unavailable, run the same verification through Docker: `docker compose run --rm app uv run pytest`.

- [ ] Verify developer commands and Docker compatibility (AC: 4)
  - [ ] Run `uv run pytest`.
  - [ ] Run `uv run ruff check .`.
  - [ ] Run `docker compose build` from `/Users/irinawork/bmad_projects`.
  - [ ] Run `docker compose run --rm app uv run pytest` from `/Users/irinawork/bmad_projects`.
  - [ ] Do not leave long-running containers active after verification; use `docker compose down` if needed.

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

TBD by dev-story workflow.

### Debug Log References

### Completion Notes List

### File List

### Change Log

- 2026-05-20: Story created by BMad create-story workflow.
