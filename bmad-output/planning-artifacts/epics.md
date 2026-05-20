---
stepsCompleted: [1, 2, 3, 4]
extractionStatus: "complete"
status: "complete"
completedAt: "2026-05-20"
inputDocuments:
  - "/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/prds/prd-Content-Multi-Agent-2026-05-19/prd.md"
  - "/Users/irinawork/bmad_projects/bmad-output/planning-artifacts/architecture.md"
---

# Content Multi-Agent - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Content Multi-Agent, decomposing the requirements from the PRD and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Operator can submit Dry Input for a new content job; the system accepts plain text input, rejects empty input, and stores the original Dry Input as part of the job record.

FR2: Operator can select `BP`, `LP`, or `GP`; if no type is selected, the system can infer a proposed Article Type and expose it for confirmation.

FR3: System generates an SEO Brief containing topic, goal, audience, main keyword, secondary keywords, LSI keywords, H1/H2/H3 outline, tone of voice and constraints.

FR4: System validates that the SEO Brief contains enough information for article generation and returns weak briefs to the SEO Brief Agent with specific missing or weak fields.

FR5: System generates an English US article from an approved SEO Brief with H1/H2/H3 structure and target length of 1500-1600 words in full mode.

FR6: System checks the English Original for brief compliance, logical structure, readability, lack of filler and unsupported factual claims.

FR7: System checks main keyword usage, secondary keyword usage, LSI coverage, headings, word count, intent match, Article Type fit and keyword stuffing risk.

FR8: Operator can select manual uniqueness input or an enabled external plagiarism checker provider.

FR9: Operator can enter a Uniqueness Score for the English Original; system accepts numeric scores from 0 to 100 and records source as `manual`.

FR10: System can submit the English Original to Copyleaks for plagiarism checking when Copyleaks provider is enabled.

FR11: System allows localization only when Uniqueness Score is at least 90%; scores below 90 route the job to revision.

FR12: System generates Spanish Localization from the approved English Original and adapts wording to selected geo when provided.

FR13: System generates Italian Localization from the approved English Original only after English Original passes uniqueness gate.

FR14: System generates French Localization from the approved English Original only after English Original passes uniqueness gate.

FR15: System assembles SEO Brief, English Original, Spanish Localization, Italian Localization, French Localization, SEO QA report, uniqueness report and final status into Markdown and JSON final packages.

FR16: System produces a final QA report with status `Approved` or `Needs Revision`, completed stages, failed checks, uniqueness result and localization status.

FR17: System tracks job status using the defined status set and records status changes in order.

FR18: System routes failed checks according to revision loop rules: brief issues to SEO Brief Agent, text issues to Copywriter Agent, style/structure issues to Rewriter, SEO issues to SEO QA + Rewriter, uniqueness below 90 to Rewriter, localization issues to the relevant Localizer.

### NonFunctional Requirements

NFR1: Every QA stage must produce a short machine-readable or structured report.

NFR2: Word count, score threshold, required artifact presence and status validation should be deterministic wherever possible.

NFR3: Final package should reference the Dry Input, Article Type, SEO Brief and QA reports used to create it.

NFR4: MVP should avoid unnecessary repeated full-article generation when only a targeted revision is needed.

NFR5: Operator can review and correct key intermediate artifacts before continuing; brief approval remains a manual gate.

NFR6: API keys and provider credentials must be read from environment variables or local ignored config, never committed.

NFR7: The app must run end-to-end without Copyleaks credentials by using manual uniqueness input.

### Additional Requirements

- Use `uv` Python application scaffold with Python 3.12.
- Use Streamlit as local portfolio UI.
- Use LangGraph `StateGraph` as workflow orchestration layer.
- Use Pydantic v2 models as cross-node contracts.
- Use file-based artifact storage under `artifacts/jobs/{job_id}/`.
- Keep Streamlit Session State for UI interaction state only, not as source of truth.
- Keep LangGraph state lightweight: job ID, stage, artifact paths, summaries, counters, routing flags and errors.
- Store full generated content and reports as artifacts, not inside graph state.
- Export final packages as Markdown and JSON.
- Support demo mode for shorter articles and full mode for 1500-1600 words.
- No authentication in local MVP.
- No FastAPI or external API layer in v1.
- Read secrets from `.env` or local ignored config; commit `.env.example`.
- Keep Copyleaks provider optional/stubbed until manual/mock uniqueness flow works.
- Separate `WorkflowStage` and `WorkflowStatus` enums.
- Define `ArtifactKey` registry mapping keys to filenames, content types, UI labels and descriptions.
- Add `StageView` model and `stage_view_builder.py` to expose UI-ready status objects.
- Every workflow stage must leave UI-visible and file-visible evidence.
- Every manual gate must display stopping reason, available actions, relevant artifact links, previous attempts and next action.
- All LLM calls must go through `services/llm_runner.py`.
- LLM output parsing failures get exactly one repair attempt before routing to human review.
- Deterministic validators must return `list[ValidationCheck]`.
- Revision guards must use configurable `MAX_REVISION_ATTEMPTS`.
- Provider selection must be explicit: `manual`, `mock`, or `copyleaks`; fallback must be visible in UI and final report.
- `config.py` is the only module that reads environment variables and settings.
- `JobService` is the facade between Streamlit and workflow execution.
- `ArtifactStore` is the only layer that reads/writes artifacts.
- `services/exporters.py` formats already-valid artifacts and must not bypass the artifact registry.
- No graph checkpointing in MVP; state persistence is handled through job artifacts.
- Create docs for demo setup, demo script, artifact map, architecture summary and project structure.
- Create examples for BP, LP and GP demo inputs plus sample keywords and demo output notes.
- First implementation story must scaffold the full structure, install dependencies, add `.env.example`, configure `.gitignore`, create empty modules/tests and add architecture-boundary tests.
- Tests must cover validators, routing, artifact store, artifact registry, uniqueness providers, architecture boundaries, job service, status presenter, config and exporters.

### UX Design Requirements

No standalone UX Design document exists. UX-related implementation requirements are captured in Architecture as Streamlit UI patterns:

UX-DR1: UI must show stage-by-stage workflow progress through a timeline or equivalent progress component.

UX-DR2: UI must show QA summaries and validation checklist results in a human-readable format.

UX-DR3: UI must show manual gates for brief approval and uniqueness input with reason, available actions, relevant artifacts and next-step explanation.

UX-DR4: UI must show controlled failure states without exposing raw tracebacks as the primary user-facing experience.

UX-DR5: UI must provide artifact previews and Markdown/JSON download actions for final outputs.

UX-DR6: UI must support reproducible demo flows: happy path, revision path and human-review path.

### FR Coverage Map

FR1: Epic 2 - Dry Input submission.

FR2: Epic 2 - Article Type selection/inference.

FR3: Epic 2 - SEO Brief generation.

FR4: Epic 2 - Brief QA and approval gate.

FR5: Epic 3 - English US article generation.

FR6: Epic 3 - Editorial QA.

FR7: Epic 3 - SEO QA.

FR8: Epic 4 - Uniqueness provider selection.

FR9: Epic 4 - Manual uniqueness score input.

FR10: Epic 4 - Optional Copyleaks provider stub/integration path.

FR11: Epic 4 - Uniqueness threshold gate.

FR12: Epic 5 - Spanish localization.

FR13: Epic 5 - Italian localization.

FR14: Epic 5 - French localization.

FR15: Epic 5 - Markdown/JSON final package.

FR16: Epic 5 - Final QA report.

FR17: Epics 1, 2, 3, 5, 6 - workflow status tracking across stages.

FR18: Epics 4 and 6 - revision routing and demoable failure paths.

## Epic List

### Epic 1: Runnable Portfolio Demo Foundation

User can launch the local Streamlit application, create a demo job shell, see basic pipeline status and trust that the project has a stable architecture foundation for future workflow stages.

**FRs covered:** FR17 partially

**Key architecture coverage:** uv scaffold, project structure, config, `.env.example`, artifact registry, artifact store skeleton, `JobService`, `StageView`, architecture-boundary tests, demo docs/examples.

### Epic 2: Content Intake and SEO Brief Approval

User can enter Dry Input, select or confirm Article Type, generate an SEO Brief, see brief QA results and manually approve or revise the brief before article generation.

**FRs covered:** FR1, FR2, FR3, FR4, FR17 partially

### Epic 3: English Article Generation and QA Gates

User can generate an English Original from an approved brief, receive editorial QA and SEO QA reports, see deterministic validation results and receive actionable revision guidance.

**FRs covered:** FR5, FR6, FR7, FR17 partially

### Epic 4: Uniqueness Gate and Revision Routing

User can select a uniqueness provider, enter manual uniqueness score or use mock provider, see pass/fail gate results and verify revision routing when score is below 90.

**FRs covered:** FR8, FR9, FR11, FR18

**Deferred/optional:** FR10 Copyleaks integration remains stubbed/optional until manual/mock flow is stable.

### Epic 5: Localization and Final Content Package

User can generate Spanish, Italian and French localizations after English approval, then receive final Markdown/JSON package and Final QA report.

**FRs covered:** FR12, FR13, FR14, FR15, FR16, FR17 partially

### Epic 6: Interview-Ready Demo Cases and Observability

User can run reproducible BP, LP and GP demo flows, show happy path, revision path and human-review path, open artifact map/demo docs and explain the pipeline in an interview.

**FRs covered:** FR17, FR18 reinforcement

**Key UX/portfolio coverage:** progress timeline, artifact panel, controlled error states, demo setup, demo script, examples, final walkthrough quality.

## Epic 1: Runnable Portfolio Demo Foundation

User can launch the local Streamlit application, create a demo job shell, see basic pipeline status and trust that the project has a stable architecture foundation for future workflow stages.

### Story 1.1: Set Up Initial uv Project Scaffold and Architecture Boundaries

As a project owner,
I want a runnable Python project scaffold with the approved directory structure,
So that future stories can be implemented in stable, reviewable locations.

**Acceptance Criteria:**

**Given** the repository root is empty of application code
**When** the scaffold is created
**Then** `pyproject.toml`, `uv.lock`, `app.py`, `.env.example`, `.gitignore`, `src/seo_content_pipeline/`, `tests/`, `docs/`, `examples/`, and `artifacts/` exist
**And** all package directories contain `__init__.py`
**And** `.gitignore` excludes `.env` and generated artifacts under `artifacts/jobs/`
**And** `uv run pytest` can discover the test suite.

### Story 1.2: Define Core Models, Stage/Status, and Artifact Registry

As a developer,
I want typed contracts for workflow stages, statuses, artifacts, validation checks, errors, QA reports and job metadata,
So that graph nodes, services and UI share the same vocabulary.

**Acceptance Criteria:**

**Given** the scaffold exists
**When** core models are implemented
**Then** `WorkflowStage`, `WorkflowStatus`, `ArtifactKey`, `ValidationCheck`, `WorkflowError`, `QAReport`, `StageView`, and job metadata models exist
**And** `WorkflowStage` is separate from `WorkflowStatus`
**And** artifact registry maps keys to filename, content type, UI label and description
**And** `test_artifact_registry.py` verifies registry completeness and filename conventions.

### Story 1.3: Implement Config, ArtifactStore, and JobService Skeleton

As an operator,
I want the app to create and inspect a demo job shell,
So that the local demo has a durable source of truth before real agent stages are added.

**Acceptance Criteria:**

**Given** `.env.example` and `config.py` exist
**When** the app creates a new job through `JobService.create_job()`
**Then** `artifacts/jobs/{job_id}/metadata.json`, `input.json`, and `state.json` are written through `ArtifactStore`
**And** `config.py` is the only module that reads environment variables
**And** artifact writes use the artifact registry
**And** `test_config.py`, `test_artifact_store.py`, and `test_job_service.py` cover default config, job creation and artifact persistence.

### Story 1.4: Build Minimal Streamlit Shell and Status Timeline

As an operator,
I want to launch a local Streamlit app and see a basic job status timeline,
So that the project is demonstrably runnable before content generation exists.

**Acceptance Criteria:**

**Given** the scaffold and `JobService` skeleton exist
**When** I run `uv run streamlit run app.py`
**Then** the app opens with a dry input form, article type selector, demo/full mode selector and job creation action
**And** after job creation the UI renders a `StageView`-based timeline
**And** `app.py` imports only UI helpers, public models and `JobService`
**And** `test_architecture_boundaries.py` verifies UI import boundaries
**And** `test_status_presenter.py` verifies `StageView` rendering data.

## Epic 2: Content Intake and SEO Brief Approval

User can enter Dry Input, select or confirm Article Type, generate an SEO Brief, see brief QA results and manually approve or revise the brief before article generation.

### Story 2.1: Submit Dry Input and Select Article Type

As an operator,
I want to submit Dry Input and select BP, LP or GP,
So that the pipeline can start with the correct article type and source material.

**Acceptance Criteria:**

**Given** the Streamlit shell is running
**When** I submit non-empty Dry Input and select an Article Type
**Then** the job stores Dry Input and selected Article Type in `input.json`
**And** empty input is rejected with a controlled UI error state
**And** the stage timeline records `input_received`
**And** FR1 and FR2 are covered.

### Story 2.2: Generate SEO Brief From Dry Input

As an operator,
I want the system to generate a structured SEO Brief,
So that I can review the planned article before text generation.

**Acceptance Criteria:**

**Given** a job has Dry Input and Article Type
**When** the brief generation stage runs
**Then** `brief.json` is created with topic, goal, audience, main keyword, secondary keywords, LSI keywords, H1/H2/H3 outline, tone of voice and constraints
**And** the brief is parsed into a Pydantic model
**And** LLM parse failure triggers exactly one repair attempt before controlled human-review status
**And** FR3 is covered.

### Story 2.3: Validate Brief Completeness

As an operator,
I want the system to validate SEO Brief completeness,
So that weak briefs do not proceed to writing.

**Acceptance Criteria:**

**Given** `brief.json` exists
**When** brief QA runs
**Then** a structured brief QA report is saved
**And** missing main keyword, unclear audience, or missing outline fails the check
**And** failed brief QA shows actionable missing fields in UI
**And** passed brief QA moves the job to a manual approval gate
**And** FR4, NFR1 and NFR2 are covered.

### Story 2.4: Approve or Request Revision for SEO Brief

As an operator,
I want to approve or request revision on the generated brief,
So that article writing starts only after human review.

**Acceptance Criteria:**

**Given** a generated brief and QA report exist
**When** I approve the brief
**Then** the workflow records `brief_approved` and enables the writing stage
**And** when I request revision the job routes back to brief generation with notes
**And** the manual gate shows reason, available actions, relevant artifact links, previous attempts and next action
**And** FR17, FR18 and NFR5 are covered.

## Epic 3: English Article Generation and QA Gates

User can generate an English Original from an approved brief, receive editorial QA and SEO QA reports, see deterministic validation results and receive actionable revision guidance.

### Story 3.1: Generate English Original From Approved Brief

As an operator,
I want the system to generate an English US article from an approved SEO Brief,
So that I receive the primary content artifact for QA.

**Acceptance Criteria:**

**Given** the brief is approved
**When** the writing stage runs
**Then** `english_original.md` is created
**And** the output uses English US and H1/H2/H3 structure
**And** demo mode supports shorter target length while full mode targets 1500-1600 words
**And** the stage timeline records writing completion
**And** FR5 is covered.

### Story 3.2: Run Deterministic Article Validators

As an operator,
I want deterministic checks for word count and heading structure,
So that basic quality gates do not depend on LLM judgment.

**Acceptance Criteria:**

**Given** `english_original.md` exists
**When** deterministic validators run
**Then** word count, required heading structure and required artifact checks produce `list[ValidationCheck]`
**And** failures are visible in the QA summary
**And** validator tests cover pass, warning and error severities
**And** NFR1 and NFR2 are covered.

### Story 3.3: Run Editorial QA

As an operator,
I want editorial QA for brief compliance, readability and factual discipline,
So that weak article drafts are caught before SEO QA.

**Acceptance Criteria:**

**Given** deterministic article checks have run
**When** editorial QA runs
**Then** an editorial QA report is saved with pass/fail checks, recommendations and summary
**And** unsupported factual claims are flagged unless generic and low-risk
**And** failed editorial QA routes to revision guidance
**And** FR6 and NFR4 are covered.

### Story 3.4: Run SEO QA and Route Failures

As an operator,
I want SEO QA to check keywords, headings, intent and stuffing risk,
So that the English Original is SEO-structured before uniqueness and localization.

**Acceptance Criteria:**

**Given** editorial QA has passed
**When** SEO QA runs
**Then** a structured SEO QA report is saved with keyword, LSI, heading, word count, intent, article type and over-optimization checks
**And** SEO failures route to SEO QA + Rewriter path with actionable notes
**And** revision attempts are bounded by `MAX_REVISION_ATTEMPTS`
**And** FR7, FR17 and FR18 are covered.

## Epic 4: Uniqueness Gate and Revision Routing

User can select a uniqueness provider, enter manual uniqueness score or use mock provider, see pass/fail gate results and verify revision routing when score is below 90.

### Story 4.1: Select Manual or Mock Uniqueness Provider

As an operator,
I want to select a manual or mock uniqueness provider,
So that the pipeline can run reliably without external plagiarism checker credentials.

**Acceptance Criteria:**

**Given** English QA has passed
**When** I open the uniqueness stage
**Then** the UI offers manual and mock providers
**And** Copyleaks is shown as optional/unavailable unless configured
**And** missing Copyleaks config does not fail app startup
**And** provider selection is recorded in the job state and final report
**And** FR8, NFR6 and NFR7 are covered.

### Story 4.2: Enter and Validate Manual Uniqueness Score

As an operator,
I want to enter a manual uniqueness score from an external checker,
So that the system can gate localization honestly.

**Acceptance Criteria:**

**Given** manual uniqueness provider is selected
**When** I enter a score from 0 to 100
**Then** `uniqueness.json` records score, source `manual`, provider metadata and timestamp
**And** invalid values are rejected with a controlled UI error
**And** the system does not invent or simulate manual scores
**And** FR9 is covered.

### Story 4.3: Gate Workflow by 90 Percent Threshold

As an operator,
I want the workflow to continue only when uniqueness is at least 90,
So that localization uses an approved English Original.

**Acceptance Criteria:**

**Given** a uniqueness score exists
**When** the score is `>= 90`
**Then** the workflow routes to localization
**And** when the score is `< 90` the workflow routes to revision with `needs_revision` status
**And** the UI shows the score, source, threshold and routing reason
**And** FR11 and FR18 are covered.

### Story 4.4: Stub Optional Copyleaks Provider Safely

As a project owner,
I want a safe optional Copyleaks integration seam,
So that the portfolio can show extensibility without making the MVP depend on external services.

**Acceptance Criteria:**

**Given** Copyleaks credentials are absent
**When** the app imports providers and starts
**Then** no Copyleaks SDK, network access or credentials are required
**And** Copyleaks provider reports disabled/unconfigured status
**And** tests verify optional import safety
**And** FR10 is represented as deferred/optional without blocking manual/mock flow.

## Epic 5: Localization and Final Content Package

User can generate Spanish, Italian and French localizations after English approval, then receive final Markdown/JSON package and Final QA report.

### Story 5.1: Generate Spanish Localization

As an operator,
I want Spanish localization from the approved English Original,
So that the final package includes a localized Spanish version.

**Acceptance Criteria:**

**Given** English Original has passed QA and uniqueness gate
**When** Spanish localization runs
**Then** `localization_es.md` is created
**And** it preserves meaning, headings and SEO intent
**And** selected or default Spanish geo is recorded
**And** FR12 is covered.

### Story 5.2: Generate Italian and French Localizations

As an operator,
I want Italian and French localizations from the approved English Original,
So that the final package includes all required language versions.

**Acceptance Criteria:**

**Given** English Original has passed QA and uniqueness gate
**When** Italian and French localization runs
**Then** `localization_it.md` and `localization_fr.md` are created
**And** both preserve meaning, headings and SEO intent
**And** localization does not run before uniqueness gate passes
**And** FR13 and FR14 are covered.

### Story 5.3: Assemble Markdown and JSON Final Package

As an operator,
I want the system to assemble final Markdown and JSON packages,
So that I can inspect and download the complete content package.

**Acceptance Criteria:**

**Given** brief, English Original, localizations, SEO QA and uniqueness artifacts exist
**When** final packaging runs
**Then** `final_package.md` and `final_package.json` are created
**And** missing required artifacts prevent approved final status
**And** exports reference Dry Input, Article Type, SEO Brief and QA reports
**And** FR15 and NFR3 are covered.

### Story 5.4: Produce Final QA Report and Status

As an operator,
I want a final QA report with approved or revision status,
So that I can understand whether the content package is ready.

**Acceptance Criteria:**

**Given** final package assembly has run
**When** final QA runs
**Then** the report lists completed stages, failed checks if any, uniqueness result and localization status
**And** status is `Approved` only when all mandatory artifacts and gates pass
**And** `Needs Revision` includes routing guidance
**And** FR16 and FR17 are covered.

## Epic 6: Interview-Ready Demo Cases and Observability

User can run reproducible BP, LP and GP demo flows, show happy path, revision path and human-review path, open artifact map/demo docs and explain the pipeline in an interview.

### Story 6.1: Add Stable BP, LP and GP Demo Inputs

As a project owner,
I want stable demo inputs for BP, LP and GP article types,
So that the portfolio demo can be repeated consistently.

**Acceptance Criteria:**

**Given** the examples directory exists
**When** demo inputs are added
**Then** `examples/inputs/bp-demo.txt`, `lp-demo.txt`, `gp-demo.txt` and `sample-keywords.json` exist
**And** each input is usable by the Streamlit demo flow
**And** the docs explain which demo path each input supports
**And** UJ-3 and UX-DR6 are covered.

### Story 6.2: Implement Demo Observability Views

As an operator,
I want to see progress timeline, artifact panel, QA checklist and controlled error states,
So that I can explain the pipeline clearly in an interview.

**Acceptance Criteria:**

**Given** one or more demo jobs exist
**When** I open the Streamlit app
**Then** I can see stage progress, artifact previews, QA summaries, revision attempt counters and download actions
**And** controlled failure states explain what failed and what action is available
**And** raw tracebacks are not the primary user-facing error experience
**And** UX-DR1 through UX-DR5 are covered.

### Story 6.3: Document Interview Walkthrough and Artifact Map

As a project owner,
I want demo setup, demo script, artifact map and architecture summary docs,
So that I can present the project confidently in interviews.

**Acceptance Criteria:**

**Given** the app and demo flows exist
**When** documentation is created
**Then** `docs/demo-setup.md`, `docs/demo-script.md`, `docs/artifact-map.md`, `docs/architecture-summary.md` and `docs/project-structure.md` exist
**And** docs explain happy path, revision path and human-review path
**And** docs identify where artifacts are stored and how QA decisions are made
**And** FR17, FR18 and UX-DR6 are reinforced.
