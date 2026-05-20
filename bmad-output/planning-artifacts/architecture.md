---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - "/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md"
  - "/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/briefs/brief-Content-Multi-Agent-2026-05-19/brief.md"
workflowType: "architecture"
lastStep: 8
status: "complete"
completedAt: "2026-05-19"
project_name: "Content Multi-Agent"
user_name: "Ira"
date: "2026-05-19"
---

# Architecture Decision Document

_This document builds through BMad architecture discovery. Sections are appended as architectural decisions are made._

## Initialization

Architecture workspace initialized from:

- PRD: `/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md`
- Product Brief: `/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/briefs/brief-Content-Multi-Agent-2026-05-19/brief.md`

No UX design, research document, project docs, or project-context file were found yet.

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

PRD contains 18 functional requirements grouped around eight capability areas:

- Content Intake: dry input submission and article type selection or inference.
- SEO Briefing: brief generation and brief QA.
- English Article Pipeline: article generation and editorial QA.
- SEO QA: keyword checks, headings, word count, intent and over-optimization checks.
- Uniqueness Handling: provider selection, manual score input, optional Copyleaks integration and threshold gate.
- Localization: Spanish, Italian and French after English approval.
- Final Packaging: Markdown/JSON package and final QA report.
- Workflow Orchestration: statuses and revision routing.

Architecturally this requires a graph/state-machine workflow, not a single linear script. The system must preserve stage boundaries, support manual gates and route failures back to the correct node.

**Non-Functional Requirements:**

The architecture is shaped by these NFRs:

- deterministic validators for word count, required fields, score threshold, artifact completeness and provider availability;
- traceability between Dry Input, SEO Brief, English Original, QA reports, Uniqueness Result and Final Content Package;
- secret handling through environment variables or local ignored config;
- reliable operation without Copyleaks credentials;
- structured QA reports for each QA stage;
- cost control through targeted revision rather than full workflow regeneration.

**Scale & Complexity:**

- Primary domain: local AI workflow app / agent orchestration tool.
- Complexity level: medium.
- Estimated architectural components: 8-10 core components.

The project is medium complexity because UI needs are moderate, but workflow state, structured LLM outputs, QA gates and revision loops need careful design.

### Technical Constraints & Dependencies

Confirmed direction:

- Product surface: local Streamlit app for portfolio demo.
- Workflow engine: LangGraph graph workflow.
- Data contracts: Pydantic models for workflow state, brief, article, QA reports, uniqueness result and final package.
- First export formats: Markdown and JSON.
- Required uniqueness path: manual score input.
- Required test/demo uniqueness path: mock uniqueness provider.
- Optional uniqueness path: Copyleaks API provider with sandbox/demo support.

Open architecture decisions:

- LLM provider and model routing;
- default Spanish geo;
- exact prompts and model parameters per stage.

### Cross-Cutting Concerns Identified

- Workflow state consistency.
- Structured LLM outputs.
- QA gates and revision loops.
- Provider abstraction for uniqueness.
- Deterministic validation vs LLM judgment.
- Secrets/config management.
- Demo reliability without paid/external services.
- Export and traceability.

### Architecture Hardening Notes

- All LLM-facing nodes must use typed Pydantic input/output contracts.
- LLM output parsing failures must trigger controlled repair or fail with an actionable error.
- LangGraph state should stay lightweight: job ID, status, artifact paths, summaries and counters. Full generated artifacts live outside graph state.
- Deterministic validators must run before LLM QA wherever possible.
- Revision loops must have max attempt limits and route to `Needs Human Review` after exhaustion.
- Manual and mock uniqueness providers are required for reliable portfolio demo. Copyleaks remains optional.
- Streamlit UI must expose stage-by-stage progress, QA reports and manual gates rather than hiding the workflow behind one button.
- Demo mode should support shorter articles for fast validation; full mode supports 1500-1600 words.
- The product should describe output as `SEO-structured content package` unless live SERP/keyword research is added later.

## Starter Template Evaluation

### Primary Technology Domain

Local Python AI workflow application with a Streamlit UI and LangGraph orchestration.

### Starter Options Considered

**Option 1: Streamlit-only script**

- Fastest to start.
- Weak structure for tests, providers, graph nodes and artifacts.
- Not strong enough for a portfolio project that needs architecture quality.

**Option 2: FastAPI backend + frontend**

- More production-like.
- Too much overhead for v1 portfolio demo.
- Delays the actual multi-agent workflow.

**Option 3: Custom Python app scaffold with uv**

- Best fit for this portfolio MVP.
- Keeps the app local and easy to run.
- Supports package structure, tests, lockfile, env management and modular architecture.
- Lets Streamlit remain the UI while core logic stays testable outside UI.

### Selected Starter: uv Python Application Scaffold

**Rationale for Selection:**

Use `uv` to initialize a structured Python application. Streamlit is only the UI layer. LangGraph workflow, Pydantic models, validators, providers and exporters live in importable modules under `src/`.

This avoids the common Streamlit anti-pattern where all business logic lives inside one `app.py`.

**Initialization Command:**

```bash
uv init --app --package --python 3.12 --name seo-content-pipeline --vcs none .
```

**Dependencies:**

```bash
uv add streamlit langgraph langchain langchain-openai pydantic python-dotenv
uv add --dev pytest ruff mypy
```

### Architectural Decisions Provided by Starter

**Language & Runtime:**

- Python 3.12.
- `pyproject.toml` for project metadata and dependencies.
- `uv.lock` for reproducible dependency installs.

**UI Layer:**

- Streamlit local app.
- UI shows stage-by-stage workflow status, manual gates, QA reports and final artifacts.

**Workflow Layer:**

- LangGraph graph workflow.
- Nodes map to agents/stages: brief generation, brief QA, writing, editorial QA, SEO QA, uniqueness gate, localization and final QA.

**Data Contracts:**

- Pydantic models for `WorkflowState`, `SEOBrief`, `ArticleDraft`, `QAReport`, `UniquenessResult` and `FinalContentPackage`.

**Storage:**

- First pass: file-based artifacts under `artifacts/jobs/{job_id}/`.
- Graph state stores lightweight references, not full generated text.

**Testing Framework:**

- `pytest` for deterministic validators and provider behavior.
- Tests focus first on word count, required fields, uniqueness threshold, artifact completeness and routing.

**Code Quality:**

- `ruff` for linting and formatting.
- `mypy` for type-checking credibility where practical.

**Development Experience:**

```bash
uv run streamlit run app.py
uv run pytest
```

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- Python 3.12 + uv project scaffold.
- Streamlit as local portfolio UI.
- LangGraph as workflow orchestration layer.
- Pydantic v2 models as all cross-node contracts.
- File-based artifact storage for v1.
- Manual + mock uniqueness providers required; Copyleaks optional.
- Deterministic validators before LLM-based QA.
- Max revision attempts for every revision loop.

**Important Decisions (Shape Architecture):**

- Streamlit Session State is used only for UI interaction state, not as the source of truth for job artifacts.
- LangGraph state remains lightweight and stores job ID, stage, artifact paths, summaries, counters and routing flags.
- Full generated text and reports are persisted under `artifacts/jobs/{job_id}/`.
- Exports are Markdown and JSON.
- Demo mode supports shorter articles; full mode supports 1500-1600 words.
- No auth for local MVP.

**Deferred Decisions (Post-MVP):**

- Copyleaks production webhook hardening.
- SQLite or database-backed job history.
- FastAPI backend.
- Hosted deployment.
- Live SERP/keyword research.
- CMS export.
- User accounts and auth.

### Data Architecture

**Decision:** Use file-based artifact storage for MVP.

**Rationale:**

The app is a local portfolio demo. File-based storage is inspectable, easy to test and easier to explain on interview than a premature database layer.

**Structure:**

```text
artifacts/
  jobs/
    {job_id}/
      input.json
      state.json
      brief.json
      english_original.md
      editorial_qa.json
      seo_qa.json
      uniqueness.json
      localization_es.md
      localization_it.md
      localization_fr.md
      final_package.md
      final_package.json
```

**Data validation:**

All persisted structured artifacts are produced from Pydantic models using `model_dump()` / JSON serialization.

### Workflow Architecture

**Decision:** Use LangGraph `StateGraph`.

**Rationale:**

The workflow has explicit stages, conditional routing and revision loops. LangGraph's state model fits this better than a plain function chain.

**State design:**

LangGraph state stores:

- `job_id`
- `article_type`
- `current_stage`
- `status_history`
- `artifact_paths`
- `qa_flags`
- `revision_counts`
- `errors`
- `manual_gate_required`

Full article text and translations are stored as artifacts, not inside graph state.

### LLM Boundary

**Decision:** All LLM nodes must use typed Pydantic input/output models.

**Rationale:**

The highest risk is malformed or decorative LLM output. Typed contracts make failures explicit.

**Pattern:**

- Prompt receives a typed context object.
- LLM response is parsed into a Pydantic model.
- If parsing fails, run one repair attempt.
- If repair fails, mark stage failed with actionable error.

### QA and Validation

**Decision:** Deterministic validators run before LLM QA.

**Rationale:**

Word count, required headings, required fields, uniqueness threshold and artifact completeness should not depend on LLM judgment.

**Validators:**

- `validate_word_count`
- `validate_required_brief_fields`
- `validate_heading_structure`
- `validate_uniqueness_score`
- `validate_required_artifacts`
- `validate_revision_limit`

LLM QA is reserved for semantic checks: readability, factual discipline, intent fit and structure quality.

### Uniqueness Providers

**Decision:** Implement provider interface.

```python
class UniquenessProvider(Protocol):
    def check(self, text: str, job_id: str) -> UniquenessResult:
        ...
```

**Required providers:**

- `ManualUniquenessProvider`
- `MockUniquenessProvider`

**Optional provider:**

- `CopyleaksUniquenessProvider`

**Rationale:**

Manual and mock providers make the app demoable without external services. Copyleaks can be shown as advanced integration without blocking the base product.

### Frontend Architecture

**Decision:** Streamlit is a thin orchestration UI.

**Rationale:**

Business logic must remain testable outside Streamlit.

**UI responsibilities:**

- collect Dry Input;
- select Article Type;
- select demo/full mode;
- show stage progress;
- show QA reports;
- handle manual brief approval;
- handle manual uniqueness input;
- render final package;
- provide Markdown/JSON downloads.

**Non-responsibilities:**

- LLM prompting logic;
- validators;
- graph routing;
- file storage internals;
- provider implementations.

### Security and Config

**Decision:** No auth in MVP. Secrets through env/local ignored config only.

**Rationale:**

The app is local and portfolio-focused. Auth would add noise. Secret hygiene still matters.

**Config:**

- `.env` for local keys;
- `.env.example` committed;
- `.gitignore` must exclude `.env` and `artifacts/`;
- no API keys in code or docs.

### API and Communication

**Decision:** No external API layer in v1.

**Rationale:**

Streamlit calls core Python modules directly. FastAPI is deferred until there is a reason to host or integrate.

### Infrastructure and Deployment

**Decision:** Local-only MVP.

**Run commands:**

```bash
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format .
```

**Rationale:**

Local execution keeps the project reliable for interviews and avoids deployment complexity before the workflow proves itself.

### Decision Impact Analysis

**Implementation Sequence:**

1. Scaffold uv Python project.
2. Create Pydantic models.
3. Implement file artifact store.
4. Implement deterministic validators.
5. Implement uniqueness providers: mock + manual.
6. Implement LangGraph state and stage-specific nodes with stubbed LLM calls.
7. Add real LLM adapter.
8. Build Streamlit UI around graph stages.
9. Add exports.
10. Add tests.
11. Add optional Copyleaks provider.

**Cross-Component Dependencies:**

- Streamlit depends on workflow service, not graph internals.
- Graph nodes depend on models, validators, providers and artifact store.
- Exporters depend on final package model and artifact store.
- Copyleaks provider depends on config/secrets and must not affect manual provider.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**

- Naming of files, models, stages, statuses and artifact keys.
- Where business logic lives vs Streamlit UI code.
- How graph nodes read/write state.
- How artifacts are persisted.
- How LLM parsing errors are handled.
- How deterministic validators and LLM QA interact.
- How revision loops stop.
- How provider fallback works.
- How workflow state becomes visible in the UI.

### Naming Patterns

**Code Naming Conventions:**

- Python modules/files: `snake_case.py`
  - good: `artifact_store.py`, `seo_validators.py`
  - avoid: `ArtifactStore.py`, `seoValidators.py`
- Classes and Pydantic models: `PascalCase`
  - good: `SEOBrief`, `QAReport`, `WorkflowState`
- Functions and variables: `snake_case`
  - good: `validate_word_count`, `current_stage`
- Constants: `UPPER_SNAKE_CASE`
  - good: `MAX_REVISION_ATTEMPTS`

**Workflow Stage and Status Naming:**

Use enum/string constants, not ad hoc literals. Stages are pipeline locations. Statuses are outcomes or control states.

```python
class WorkflowStage(str, Enum):
    INPUT_RECEIVED = "input_received"
    BRIEF_DRAFTED = "brief_drafted"
    BRIEF_APPROVED = "brief_approved"
    WRITING = "writing"
    EDITORIAL_REVIEW = "editorial_review"
    SEO_QA = "seo_qa"
    UNIQUENESS_CHECK = "uniqueness_check"
    LOCALIZATION = "localization"
    FINAL_QA = "final_qa"

class WorkflowStatus(str, Enum):
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    FAILED = "failed"
```

**Artifact Naming:**

Artifact keys and filenames must be defined through one registry, not scattered strings.

```python
class ArtifactKey(str, Enum):
    INPUT = "input"
    STATE = "state"
    BRIEF = "brief"
    ENGLISH_ORIGINAL = "english_original"
    EDITORIAL_QA = "editorial_qa"
    SEO_QA = "seo_qa"
    UNIQUENESS = "uniqueness"
    LOCALIZATION_ES = "localization_es"
    LOCALIZATION_IT = "localization_it"
    LOCALIZATION_FR = "localization_fr"
    FINAL_PACKAGE_MD = "final_package_md"
    FINAL_PACKAGE_JSON = "final_package_json"
```

The registry maps each `ArtifactKey` to filename, content type, UI label and description.

### Structure Patterns

**Project Organization:**

```text
app.py
src/
  seo_content_pipeline/
    config.py
    models/
      artifacts.py
      content.py
      errors.py
      qa_result.py
      stage.py
      uniqueness.py
      validation.py
      job.py
    graph/
      builder.py
      nodes/
      routing.py
      state.py
    services/
      artifact_store.py
      exporters.py
      job_service.py
      llm_client.py
      llm_runner.py
    validators/
      artifact_validators.py
      revision_validators.py
      seo_validators.py
    providers/
      base.py
      manual_uniqueness.py
      mock_uniqueness.py
      copyleaks_uniqueness.py
    prompts/
      brief.py
      localization.py
      qa_prompt.py
      writer.py
    ui/
      components.py
      renderers.py
      status_presenter.py
tests/
  test_architecture_boundaries.py
  test_artifact_registry.py
  test_artifact_store.py
  test_routing.py
  test_uniqueness_providers.py
  test_validators.py
artifacts/
  jobs/
```

**Rules:**

- `app.py` imports UI helpers and `services/job_service.py`.
- `app.py` must not import `graph.nodes`, `prompts`, `validators` or provider implementations.
- Graph nodes use `ArtifactStore`; they do not call `open()` directly.
- Routing functions live in `graph/routing.py` and are pure unit-testable functions.
- `JobService` is the facade between Streamlit and the workflow.

### Format Patterns

**Structured Artifacts:**

- JSON artifacts use `snake_case` fields.
- Markdown artifacts are for human-readable long-form content.
- Every JSON artifact includes:
  - `job_id`
  - `created_at`
  - `stage`
  - stage-specific payload

**Minimum Model Contracts:**

```python
class ValidationCheck(BaseModel):
    name: str
    passed: bool
    severity: Literal["info", "warning", "error"]
    message: str
    metadata: dict[str, Any] = {}

class QAReport(BaseModel):
    job_id: str
    stage: WorkflowStage
    passed: bool
    score: float | None = None
    checks: list[ValidationCheck]
    recommendations: list[str] = []
    routing_target: WorkflowStage | None = None
    summary: str

class WorkflowError(BaseModel):
    code: str
    message: str
    node: str
    stage: WorkflowStage
    recoverable: bool
    details: dict[str, Any] = {}
    created_at: datetime
```

**UI-Ready Status Object:**

Every workflow stage must expose a UI-ready status object.

```python
class StageView(BaseModel):
    stage: WorkflowStage
    status: WorkflowStatus
    label: str
    description: str
    artifact_links: list[ArtifactKey]
    available_actions: list[str]
    blocking_reason: str | None = None
    recoverable: bool = True
    revision_attempt: int | None = None
    max_revision_attempts: int | None = None
```

This object is what Streamlit renders for the pipeline timeline, manual gates and failure states.

### Communication Patterns

**Graph Node Pattern:**

Every graph node follows this shape:

```python
def node_name(state: PipelineState) -> dict:
    context = load_required_artifacts(state)
    result = do_stage_work(context)
    artifact_path = artifact_store.save(...)
    return {
        "current_stage": next_stage,
        "status": next_status,
        "artifact_paths": updated_paths,
        "status_history": updated_history,
    }
```

Nodes return partial state updates. Nodes do not mutate global state directly.

**Pipeline State Pattern:**

`PipelineState` is lightweight and contains only:

- `job_id`
- `article_type`
- `current_stage`
- `status`
- `artifact_paths`
- `status_history`
- `revision_attempts`
- `qa_flags`
- `errors`
- `manual_gate_required`

Full briefs, articles, translations and reports live in artifacts, not state.

**Routing Pattern:**

Routing functions are pure functions:

```python
def route_after_seo_qa(state: PipelineState) -> WorkflowStage:
    ...
```

They inspect state and reports, then return the next stage or route key. Routing tests must run without filesystem, Streamlit, LLM or providers.

### Process Patterns

**LLM Output Pattern:**

All LLM calls go through `services/llm_runner.py`.

1. Build prompt from typed context.
2. Call LLM adapter.
3. Parse into target Pydantic model.
4. If parsing fails, run exactly one repair attempt.
5. If repair fails, write `WorkflowError` and route to `WorkflowStatus.NEEDS_HUMAN_REVIEW`.

**Validator Pattern:**

Deterministic validators return `list[ValidationCheck]`, not booleans or strings.

**Revision Loop Pattern:**

Revision guards live in one place: `validators/revision_validators.py` or `graph/routing.py`.

```python
if revision_attempts[stage] >= MAX_REVISION_ATTEMPTS:
    return WorkflowStatus.NEEDS_HUMAN_REVIEW
```

`MAX_REVISION_ATTEMPTS` is configurable with a default.

**Provider Fallback Pattern:**

- Provider selection is explicit through config/UI: `manual`, `mock`, or `copyleaks`.
- Manual provider is always available.
- Mock provider is available in tests/demo.
- Copyleaks provider is available only when configured.
- Missing Copyleaks config must not fail app startup.
- Fallback must be visible in UI and final report; the system must not silently hide a provider failure.

### Streamlit UI Patterns

**Session State:**

Allowed:

- currently selected job;
- form values;
- current UI step;
- temporary manual uniqueness input.

Not allowed:

- source of truth for artifacts;
- final package data;
- graph state persistence.

**Rendering Pattern:**

UI reads from `JobService`, artifact store and `StageView`, then renders:

- status timeline;
- current gate;
- QA report summaries;
- validation checklist;
- revision attempt counter;
- artifact previews;
- available user actions;
- download buttons.

**Manual Gate Pattern:**

Every manual gate must display:

- reason for stopping;
- available actions;
- relevant artifact links;
- previous attempts;
- what happens next after each action.

### Demo Observability Patterns

Every workflow stage must leave both UI-visible and file-visible evidence:

- UI-visible: `StageView`, status timeline entry, QA summary or manual gate.
- File-visible: structured artifact or markdown artifact under `artifacts/jobs/{job_id}/`.

Portfolio demo must include reproducible local paths:

- happy path;
- revision path;
- human-review path.

Mock/manual uniqueness providers must support these paths without external credentials.

### Enforcement Guidelines

**All AI Agents MUST:**

- Keep business logic out of `app.py`.
- Use Pydantic models for cross-module data.
- Store full artifacts in `artifacts/jobs/{job_id}/`.
- Keep LangGraph state lightweight.
- Run deterministic validators before LLM QA.
- Use provider interfaces for uniqueness.
- Add tests for validators, routing, artifact registry, import boundaries and providers.
- Never commit `.env` or generated artifacts.

**New Workflow Stage Checklist:**

Any new workflow stage must define:

- enum value;
- display metadata for `StageView`;
- node or route handling;
- artifact key or explicit `None`;
- validator/QA behavior;
- routing rule;
- UI-visible output;
- tests.

**Pattern Enforcement:**

- `ruff check .`
- `ruff format .`
- `pytest`
- `test_artifact_registry.py` verifies stage/artifact mapping.
- `test_architecture_boundaries.py` verifies import boundaries.
- Architecture review before adding new modules.

### Anti-Patterns

- Putting prompts, validators or provider logic in `app.py`.
- Passing full 1500-word articles through every state update.
- Treating LLM QA as a replacement for deterministic checks.
- Hardcoding API keys.
- Making Copyleaks required for the app to start.
- Silently falling back from Copyleaks to manual without recording it.
- Allowing unlimited revision loops.
- Returning raw dicts from LLM nodes without Pydantic parsing.

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
seo-content-pipeline/
├── README.md
├── pyproject.toml
├── uv.lock
├── app.py
├── .env.example
├── .gitignore
├── artifacts/
│   ├── demo/
│   │   └── .gitkeep
│   └── jobs/
│       └── .gitkeep
├── docs/
│   ├── architecture-summary.md
│   ├── artifact-map.md
│   ├── demo-script.md
│   ├── demo-setup.md
│   └── project-structure.md
├── examples/
│   ├── briefs/
│   │   └── demo-brief.md
│   ├── inputs/
│   │   ├── bp-demo.txt
│   │   ├── gp-demo.txt
│   │   ├── lp-demo.txt
│   │   └── sample-keywords.json
│   └── outputs/
│       └── README.md
├── src/
│   └── seo_content_pipeline/
│       ├── __init__.py
│       ├── config.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── artifacts.py
│       │   ├── content.py
│       │   ├── errors.py
│       │   ├── job.py
│       │   ├── qa_result.py
│       │   ├── stage.py
│       │   ├── uniqueness.py
│       │   └── validation.py
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── builder.py
│       │   ├── routing.py
│       │   ├── state.py
│       │   └── nodes/
│       │       ├── __init__.py
│       │       ├── brief_node.py
│       │       ├── final_qa_node.py
│       │       ├── localization_node.py
│       │       ├── seo_node.py
│       │       ├── uniqueness_node.py
│       │       └── writer_node.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── artifact_store.py
│       │   ├── exporters.py
│       │   ├── job_service.py
│       │   ├── llm_client.py
│       │   ├── llm_runner.py
│       │   └── stage_view_builder.py
│       ├── validators/
│       │   ├── __init__.py
│       │   ├── artifact_validators.py
│       │   ├── revision_validators.py
│       │   └── seo_validators.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── manual_uniqueness.py
│       │   ├── mock_uniqueness.py
│       │   └── copyleaks_uniqueness.py
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── brief.py
│       │   ├── localization.py
│       │   ├── qa_prompt.py
│       │   └── writer.py
│       └── ui/
│           ├── __init__.py
│           ├── artifact_panel.py
│           ├── components.py
│           ├── empty_states.py
│           ├── error_presenter.py
│           ├── progress_timeline.py
│           └── renderers.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_architecture_boundaries.py
    ├── test_artifact_registry.py
    ├── test_artifact_store.py
    ├── test_config.py
    ├── test_exporters.py
    ├── test_job_service.py
    ├── test_routing.py
    ├── test_status_presenter.py
    ├── test_uniqueness_providers.py
    └── test_validators.py
```

### Architectural Boundaries

**UI Boundary**

- `app.py` is the Streamlit entry point.
- `app.py` calls `JobService` and UI helpers only.
- `app.py` does not import graph nodes, prompts, validators or provider implementations.
- UI renders `StageView`, QA summaries, artifact previews, progress timeline, empty states, error states and manual gates.

**Workflow Boundary**

- `graph/builder.py` builds the LangGraph graph.
- `graph/nodes/*_node.py` contains stage-specific node functions.
- `graph/routing.py` contains pure routing functions.
- `graph/state.py` defines lightweight `PipelineState`.
- No graph checkpointing in MVP; state persistence is handled through job artifacts.

**Service Boundary**

- `services/job_service.py` is the facade used by UI.
- `services/artifact_store.py` is the only layer that reads/writes artifacts.
- `services/stage_view_builder.py` converts workflow state into UI-ready `StageView` objects.
- `services/llm_client.py` is the low-level LLM API adapter.
- `services/llm_runner.py` owns prompt execution, schema validation and repair attempts.
- `services/exporters.py` formats already-valid artifacts into Markdown and JSON exports; it does not bypass the artifact registry.

**Provider Boundary**

- `providers/base.py` defines provider interfaces.
- Manual and mock uniqueness providers are required.
- Copyleaks provider is optional/stubbed for MVP and must not require SDK imports, credentials or network access at app startup.

**Validation Boundary**

- `validators/*` contains deterministic validators.
- Validators return `list[ValidationCheck]`.
- LLM QA consumes validator output but does not replace deterministic checks.

**Configuration Boundary**

- `config.py` is the only module that reads environment variables and settings.
- Graph nodes, validators, providers and UI receive settings through config objects or service constructors.

### Requirements to Structure Mapping

**FR-1, FR-2: Content Intake and Article Type**

- `app.py`
- `ui/components.py`
- `services/job_service.py`
- `models/content.py`
- `models/job.py`

**FR-3, FR-4: SEO Brief Generation and QA**

- `prompts/brief.py`
- `graph/nodes/brief_node.py`
- `validators/artifact_validators.py`
- `models/content.py`
- `models/qa_result.py`

**FR-5, FR-6: English Article and Editorial QA**

- `prompts/writer.py`
- `prompts/qa_prompt.py`
- `graph/nodes/writer_node.py`
- `services/llm_runner.py`
- `models/content.py`
- `models/qa_result.py`

**FR-7: SEO QA**

- `validators/seo_validators.py`
- `graph/nodes/seo_node.py`
- `prompts/qa_prompt.py`
- `models/qa_result.py`
- `graph/routing.py`

**FR-8 to FR-11: Uniqueness Handling**

- `providers/base.py`
- `providers/manual_uniqueness.py`
- `providers/mock_uniqueness.py`
- `providers/copyleaks_uniqueness.py`
- `models/uniqueness.py`
- `graph/nodes/uniqueness_node.py`
- `graph/routing.py`

**FR-12 to FR-14: Localization**

- `prompts/localization.py`
- `graph/nodes/localization_node.py`
- `models/content.py`
- `services/artifact_store.py`

**FR-15, FR-16: Final Package and QA Report**

- `services/exporters.py`
- `graph/nodes/final_qa_node.py`
- `models/job.py`
- `models/qa_result.py`
- `services/artifact_store.py`

**FR-17, FR-18: Workflow Status and Revision Routing**

- `models/stage.py`
- `graph/state.py`
- `graph/routing.py`
- `validators/revision_validators.py`
- `services/stage_view_builder.py`
- `ui/progress_timeline.py`

### Integration Points

**Internal Communication**

- UI -> `JobService`
- `JobService` -> LangGraph compiled graph
- Graph nodes -> `ArtifactStore`, validators, providers and `LLMRunner`
- UI -> `StageView` and artifact previews through `JobService` / `stage_view_builder`

**External Integrations**

- OpenAI or compatible LLM provider through `services/llm_client.py`.
- Optional Copyleaks through `providers/copyleaks_uniqueness.py`.
- No external API server in v1.

**Data Flow**

1. User submits Dry Input in Streamlit.
2. `JobService.create_job()` writes `input.json`, `state.json` and job metadata.
3. `JobService.run_next_step()` advances graph.
4. Graph node loads needed artifacts through `ArtifactStore`.
5. Node runs deterministic validators and/or LLM runner.
6. Node writes stage artifact.
7. Routing decides next stage/status.
8. `stage_view_builder.py` creates UI-ready status objects.
9. UI renders timeline, QA report, manual gate or final downloads.
10. Final exporter writes `final_package.md` and `final_package.json`.

### File Organization Patterns

**Configuration Files**

- `.env.example` documents expected environment variables.
- `.env` is local only and ignored.
- `config.py` reads env and exposes typed settings.
- `APP_MODE=demo|local|production` controls demo defaults.

**Job Directory Contract**

- Each job lives under `artifacts/jobs/{job_id}/`.
- Each job contains `metadata.json`, `input.json`, `state.json` and stage artifacts.
- Writes should be atomic where practical: write temp file, then replace target file.
- Overwrite policy is explicit: stage artifacts may be overwritten only by the same stage during retry/revision.
- Generated artifacts are ignored by git.

**Source Organization**

- Models are pure Pydantic contracts grouped around artifacts and public stage contracts.
- Services contain orchestration-adjacent business logic.
- Graph contains workflow execution and routing.
- Providers isolate external/manual uniqueness mechanisms.
- UI contains rendering only.

**Test Organization**

- `conftest.py`: temp artifact root, fake artifact store, deterministic mock LLM runner, sample artifacts, fake uniqueness provider responses.
- `test_validators.py`: deterministic validators.
- `test_routing.py`: pure routing.
- `test_artifact_store.py`: file persistence and atomic write behavior.
- `test_artifact_registry.py`: artifact key/filename/UI metadata mapping.
- `test_uniqueness_providers.py`: manual/mock provider behavior and optional Copyleaks import safety.
- `test_architecture_boundaries.py`: import boundary checks.
- `test_job_service.py`: UI-facing orchestration facade.
- `test_status_presenter.py`: `StageView` builder and UI-ready state contract.
- `test_config.py`: defaults, provider selection and no failure without external credentials.
- `test_exporters.py`: Markdown/JSON export contract and missing artifact behavior.

**Demo and Documentation Organization**

- `docs/demo-script.md`: interview walkthrough script.
- `docs/demo-setup.md`: local setup and demo-mode instructions.
- `docs/artifact-map.md`: human explanation of pipeline artifacts.
- `docs/project-structure.md`: structure as architecture contract.
- `examples/inputs/`: stable BP, LP and GP demo inputs.
- `examples/briefs/`: stable demo brief examples.
- `examples/outputs/`: notes or snapshots for expected output shape.

### Development Workflow Integration

**Development Commands**

```bash
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format .
```

**First Implementation Story**

The first implementation story should scaffold this structure, install dependencies, add `.env.example`, configure `.gitignore`, create empty modules/tests and add architecture-boundary tests so future stories have stable paths.

**Deployment Structure**

No hosted deployment in v1. The project is optimized for local portfolio demo and interview walkthrough.

## Architecture Validation Results

### Coherence Validation

**Decision Compatibility:**

Technology choices are compatible: Python 3.12, uv, Streamlit, LangGraph, Pydantic, file artifacts and pytest/ruff support a local portfolio MVP without unnecessary backend infrastructure.

**Pattern Consistency:**

Patterns now align with decisions:

- Streamlit stays thin.
- `JobService` is the UI facade.
- LangGraph state stays lightweight.
- Full artifacts live in file storage.
- Deterministic validators precede LLM QA.
- Manual/mock uniqueness providers keep demo reliable.
- Copyleaks remains optional/stubbed.

**Structure Alignment:**

The project structure supports the architectural boundaries:

- UI, graph, services, validators, providers, prompts and models are separated.
- Stage-specific graph nodes reduce merge conflicts.
- `StageView` and `stage_view_builder.py` support UI observability.
- Tests cover boundaries, config, exporters, routing, providers and artifact registry.

### Requirements Coverage Validation

**Functional Requirements Coverage:**

All FR-1 through FR-18 are mapped to project structure and components.

**Non-Functional Requirements Coverage:**

NFRs are covered:

- deterministic validation;
- traceability;
- secret handling;
- no required Copyleaks credentials;
- structured QA reports;
- cost-control via bounded revision attempts;
- portfolio demo observability.

### Implementation Readiness Validation

**Decision Completeness:**

All critical implementation-blocking decisions are documented.

**Structure Completeness:**

The directory tree is specific enough for implementation stories. It includes root config, source modules, tests, docs, examples and generated artifact boundaries.

**Pattern Completeness:**

Patterns cover naming, state, artifact registry, node shape, routing, validators, LLM repair, provider fallback, UI state and anti-patterns.

### Gap Analysis Results

**Critical Gaps:** None.

**Important Gaps:**

- LLM provider/model routing must be selected before real LLM integration story.
- Default Spanish geo must be chosen before final localization polish.
- Prompt formats and model parameters need definition during prompt implementation stories.

**Nice-to-Have Gaps:**

- Copyleaks production webhook flow can be added after manual/mock uniqueness is working.
- SQLite job history can be added after local artifact workflow is proven.
- FastAPI/hosted deployment can be deferred.

### Architecture Completeness Checklist

**Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**

- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**

- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**

- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY WITH MINOR GAPS

**Confidence Level:** high

**Key Strengths:**

- Strong separation of UI, workflow, services and providers.
- Typed contracts reduce LLM-output fragility.
- Demo reliability is protected by manual/mock uniqueness providers.
- File artifacts make the pipeline inspectable for interviews.
- Tests are defined around architecture risks, not only functions.

**Areas for Future Enhancement:**

- Copyleaks production provider.
- SQLite job index/history.
- Hosted API/UI.
- Live SERP/keyword research.
- CMS export.

### Implementation Handoff

**AI Agent Guidelines:**

- Follow architecture boundaries exactly.
- Do not put business logic in `app.py`.
- Do not store full generated content in graph state.
- Add tests with every new validator, provider, route or stage.
- Keep Copyleaks optional until manual/mock flow works.

**First Implementation Priority:**

Scaffold the uv Python project and create the full directory/test skeleton.
