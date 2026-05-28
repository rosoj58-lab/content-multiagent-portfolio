---
title: 'Add Job Debug Snapshot'
type: 'feature'
created: '2026-05-28'
status: 'done'
baseline_commit: '985f3a36351ade7362f883679d3a134d6fa70358'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/artifact-map.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The app is now observable through scorecards, timelines and run summaries, but debugging a specific job still requires opening several artifacts and mentally combining state, metadata, errors, missing files and gates. For a portfolio interview, a single diagnostic snapshot would make the multi-agent workflow easier to explain and inspect.

**Approach:** Add a derived `debug_snapshot.json` artifact for each generated/demo job. It should summarize current state, article type, manual gate, errors, revision attempts, missing registry artifacts, artifact counts and key artifact paths. It is local read-only diagnostic evidence, not a new source of truth or telemetry system.

## Boundaries & Constraints

**Always:** Derive the snapshot from existing `metadata.json`, `state.json` and artifact registry; include enough fields to debug BP/LP/GP/live-brief jobs quickly; write it as a normal registry JSON artifact; expose it through existing artifact previews/downloads; keep old jobs without this artifact loadable; preserve current workflow statuses and final QA decisions.

**Ask First:** Adding hosted logging, external telemetry, database events, real-time tracing, UI dashboards beyond artifact preview, editing/fixing artifacts from the snapshot, or changing workflow routing based on snapshot contents.

**Never:** Do not treat `debug_snapshot.json` as workflow state; do not scan outside the configured job folder; do not include raw provider secrets or environment values; do not silently repair corrupt artifacts; do not make the complete demo depend on network or paid services.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Fresh job snapshot | New job with only metadata/input/state | Snapshot writes successfully, lists core artifacts present and later-stage artifacts missing | N/A |
| Approved BP demo | Full approved artifact set exists | Snapshot shows `approved`, no manual gate, no errors, final package paths, and zero critical missing artifacts | N/A |
| Routed LP/GP demo | Job stops at revision or human review | Snapshot shows routed status, decision context, revision attempts/notes/errors and missing downstream artifacts as expected | N/A |
| Live brief job | Brief QA manual gate exists without article/final package | Snapshot shows `waiting_for_human`, manual gate true and live brief artifacts present | N/A |
| Missing optional artifact | Older job lacks `debug_snapshot.json` or `run_summary.json` | Recent jobs/artifact panel still load the job; snapshot service can generate a new snapshot on demand | Controlled omission, not traceback |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/models/artifacts.py` -- add `DEBUG_SNAPSHOT` registry entry and filename.
- `src/seo_content_pipeline/models/debug_snapshot.py` -- new Pydantic contract for derived diagnostic artifact.
- `src/seo_content_pipeline/services/debug_snapshot_service.py` -- read metadata/state, inspect registry artifacts, and write `debug_snapshot.json`.
- `src/seo_content_pipeline/services/demo_pipeline_service.py` and `src/seo_content_pipeline/services/live_brief_service.py` -- generate snapshot alongside existing run summary for demo/live paths.
- `src/seo_content_pipeline/ui/artifact_panel.py` -- automatically exposes new registry artifact through existing preview/download flow.
- `tests/test_debug_snapshot_service.py`, `tests/test_demo_observability.py`, `tests/test_live_brief_service.py` -- verify snapshot contract and integration.
- `README.md`, `docs/artifact-map.md`, `docs/interview-cheatsheet.md`, `docs/roadmap.md`, `docs/testing-strategy.md` -- document the diagnostic artifact and its non-production boundary.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/models/artifacts.py` and `src/seo_content_pipeline/models/debug_snapshot.py` -- add stable artifact key, registry metadata and snapshot schema.
- [x] `src/seo_content_pipeline/services/debug_snapshot_service.py` -- implement read-only snapshot derivation with artifact presence, missing artifacts, counts, gate/error/revision summaries and key paths.
- [x] `src/seo_content_pipeline/services/demo_pipeline_service.py` and `src/seo_content_pipeline/services/live_brief_service.py` -- write snapshots wherever `run_summary.json` is already written.
- [x] `tests/` -- cover fresh job, approved demo, routed demo, live brief/manual gate and artifact panel preview inclusion.
- [x] `README.md` and `docs/` -- describe `debug_snapshot.json` as local diagnostic evidence, not telemetry or source of truth.

**Acceptance Criteria:**
- Given a fresh job, when the snapshot service runs, then `debug_snapshot.json` is written with core artifacts present and expected downstream artifacts missing.
- Given a BP demo completes, when artifacts are inspected, then `debug_snapshot.json` appears in the registry preview and reports approved status, final package paths and no workflow errors.
- Given LP or GP routes to revision or human review, when the snapshot is opened, then it shows the routed status, errors/notes where present and missing downstream artifacts without failing.
- Given a live brief job stops at a manual gate, when the snapshot is generated, then it records `manual_gate_required=true` and only the brief-stage artifacts as present.
- Given release checks run, when tests and demo manifest generation complete, then existing `run_summary.json`, recent jobs and BP/LP/GP outcomes remain unchanged.

## Spec Change Log

## Design Notes

Keep the artifact intentionally compact. The snapshot should answer “what is this job, where did it stop, what exists, what is missing, and what should I inspect next?” It should not duplicate full QA reports or content bodies.

Suggested top-level fields:

```python
job_id, article_type, status, current_stage, manual_gate_required
artifact_counts, present_artifacts, missing_artifacts
key_paths, revision_attempts, revision_notes, errors
```

## Verification

**Commands:**
- `uv run ruff check .` -- expected: lint passes.
- `uv run pytest tests/test_debug_snapshot_service.py tests/test_demo_observability.py tests/test_live_brief_service.py tests/test_readme_docs.py tests/test_interview_docs.py` -- expected: focused service/integration/docs pass.
- `make --no-print-directory release-check` -- expected: full regression, demo manifest and existing artifacts remain green.

## Suggested Review Order

**Snapshot Contract**

- Adds `debug_snapshot.json` to the artifact registry.
  [`artifacts.py:30`](../../Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py#L30)

- Defines the compact diagnostic snapshot payload.
  [`debug_snapshot.py:12`](../../Content_MultiAgent/src/seo_content_pipeline/models/debug_snapshot.py#L12)

**Snapshot Derivation**

- Builds snapshots from metadata, state and registry presence only.
  [`debug_snapshot_service.py:26`](../../Content_MultiAgent/src/seo_content_pipeline/services/debug_snapshot_service.py#L26)

- Separates expected missing artifacts from broken referenced paths.
  [`debug_snapshot_service.py:90`](../../Content_MultiAgent/src/seo_content_pipeline/services/debug_snapshot_service.py#L90)

**Workflow Integration**

- Writes snapshots beside run summaries for offline demo paths.
  [`demo_pipeline_service.py:332`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L332)

- Writes snapshots beside live brief summaries after manual gate creation.
  [`live_brief_service.py:86`](../../Content_MultiAgent/src/seo_content_pipeline/services/live_brief_service.py#L86)

**Coverage**

- Covers fresh, approved and routed diagnostic states.
  [`test_debug_snapshot_service.py:21`](../../Content_MultiAgent/tests/test_debug_snapshot_service.py#L21)

- Verifies artifact preview exposes the new diagnostic file.
  [`test_demo_observability.py:141`](../../Content_MultiAgent/tests/test_demo_observability.py#L141)
