---
title: 'Add Exportable Job Run Summary'
type: 'feature'
created: '2026-05-28'
status: 'done'
baseline_commit: '41c3a8b4be5a05ebbe32cd5059da4d3f34a7610f'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/artifact-map.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Текущая Streamlit observability хорошо показывает статус, scorecard и artifacts внутри UI, но после demo run нет одного компактного job-level summary artifact, который можно открыть, скачать или показать на собеседовании как “карточку прогона”. CLI `demo-summary.json` индексирует несколько demo jobs, но не заменяет экспортируемую сводку по конкретному job.

**Approach:** Добавить persisted `run_summary.json` для каждого завершенного или остановленного job action: summary собирается из существующих `state.json`, `metadata.json`, registry artifacts и decision artifacts, показывается в artifact panel и может быть сгенерирован без внешних API. Это усиливает observability без изменения workflow decisions.

## Boundaries & Constraints

**Always:** Summary строится только из уже сохраненных contracts/artifacts; добавляется как registry-backed artifact; не пересчитывает QA verdicts; не меняет `PipelineState.status`, routing или существующие demo outcomes; работает для BP approved, LP needs_revision, GP needs_human_review и optional live brief manual gate; UI должен просто показывать/скачивать artifact через существующий artifact panel.

**Ask First:** Добавление stage durations, retry counters beyond existing state fields, structured logging framework, dashboard history across many jobs, database-backed query layer, hosted observability, analytics charts, или изменение CLI multi-run manifest contract.

**Never:** Не создавать отдельную параллельную “истину” о статусе job; не читать secrets или raw provider responses; не делать сетевые вызовы; не подменять `final_qa_report`, `editorial_qa`, `brief_qa` или `demo-summary.json`; не добавлять новый UI dashboard в этой задаче.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Approved BP demo | Job завершен `approved` с final package и final QA | `run_summary.json` содержит job id, article type, final status/stage, decision artifact, generated artifacts list, final package path and counts | N/A |
| Routed LP/GP demo | Job остановлен на `needs_revision` или `needs_human_review` после editorial QA | Summary сохраняет terminal status, routing target/decision artifact and absent final package explicitly | Missing optional final artifacts are reported as absent, not errors |
| Live brief manual gate | Job остановлен на `waiting_for_human` после live brief + brief QA | Summary shows brief-only scope, current manual gate and generated brief/brief QA artifacts | No OpenAI key or provider call is needed to build summary |
| Fresh/new job | Only metadata/input/state exist | Summary can be built on demand and marks decision artifact/final package as absent | Missing required metadata/state raises a controlled error to the caller |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/models/artifacts.py` -- artifact registry source; add stable `RUN_SUMMARY` key and metadata.
- `src/seo_content_pipeline/models/` -- add typed run summary contract or colocate a small Pydantic model with service if registry-only is simpler.
- `src/seo_content_pipeline/services/run_summary_service.py` -- new pure service that reads metadata/state/artifact registry and persists `run_summary.json`.
- `src/seo_content_pipeline/services/demo_pipeline_service.py`, `services/live_brief_service.py` -- call summary generation after demo results, LP correction results and live brief results.
- `src/seo_content_pipeline/ui/artifact_panel.py` -- should pick up registry-backed summary automatically; adjust only if ordering/preview needs explicit handling.
- `src/seo_content_pipeline/cli/demo.py` -- include `run_summary` path in each run entry without changing the existing multi-run manifest purpose.
- `tests/` -- cover service shape, demo/live integration, artifact registry, UI preview and CLI manifest compatibility.
- `README.md`, `docs/artifact-map.md`, `docs/demo-script.md`, `docs/interview-cheatsheet.md`, `docs/roadmap.md` -- document the interview use case and that this is job-level, not production observability.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/models/artifacts.py` and model exports -- add `run_summary.json` as a first-class JSON artifact.
- [x] `src/seo_content_pipeline/services/run_summary_service.py` -- build a deterministic summary from existing persisted job contracts, including terminal/current status, generated artifacts, decision artifact, final package presence, manual gate and revision counters.
- [x] `src/seo_content_pipeline/services/demo_pipeline_service.py`, `src/seo_content_pipeline/services/live_brief_service.py` -- persist summary after every demo/live action that leaves the job in a meaningful visible state.
- [x] `src/seo_content_pipeline/cli/demo.py` -- print and include the per-job `run_summary` path in each demo run entry while preserving existing summary manifest fields.
- [x] `tests/` -- verify approved, revision, human-review, live manual-gate and fresh-job summary behavior with no external network.
- [x] `README.md` and `docs/` -- update walkthrough docs to point interviewers to `run_summary.json`.

**Acceptance Criteria:**
- Given a BP offline demo job, when the demo completes, then `run_summary.json` exists and the artifact panel/download list includes it.
- Given LP and GP offline demo jobs, when the demo stops before final package, then `run_summary.json` records the routed decision artifact and explicit absence of final package.
- Given a live brief job that reaches manual approval, when summary generation runs, then the summary documents the brief-only scope without continuing the workflow.
- Given the existing release gate runs without credentials, when tests execute, then BP/LP/GP outcomes and all existing manifest fields remain backward compatible.

## Spec Change Log

## Design Notes

Keep the summary as a derived artifact, not new workflow state. The durable source of truth remains `state.json`, `metadata.json` and QA artifacts; `run_summary.json` is an interview/debugging view over those contracts. Suggested top-level shape:

```json
{
  "job_id": "job-...",
  "article_type": "BP",
  "status": "approved",
  "current_stage": "final_qa",
  "decision_artifact": "artifacts/jobs/.../final_qa_report.json",
  "generated_artifacts": [{"key": "brief", "path": "...", "exists": true}],
  "final_package_path": "artifacts/jobs/.../final_package.md",
  "manual_gate_required": false
}
```

## Verification

**Commands:**
- `uv run ruff check .` -- expected: new service, model exports and tests pass lint.
- `uv run pytest tests/test_artifact_registry.py tests/test_demo_cli.py tests/test_demo_observability.py tests/test_live_brief_service.py tests/test_app_shell.py tests/test_readme_docs.py tests/test_interview_docs.py` -- expected: focused behavior and docs pass.
- `make --no-print-directory release-check` -- expected: full offline demo outcomes remain unchanged and `run_summary` is generated for demo jobs.

## Suggested Review Order

**Derived Summary Boundary**

- Entry point builds summary from persisted contracts without changing decisions.
  [`run_summary_service.py:17`](../../Content_MultiAgent/src/seo_content_pipeline/services/run_summary_service.py#L17)

- Decision artifacts are linked only when the backing file exists.
  [`run_summary_service.py:110`](../../Content_MultiAgent/src/seo_content_pipeline/services/run_summary_service.py#L110)

**Artifact Contract**

- Adds run summary as a first-class registry-backed artifact.
  [`artifacts.py:8`](../../Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py#L8)

- Defines the exported per-job JSON shape.
  [`run_summary.py:21`](../../Content_MultiAgent/src/seo_content_pipeline/models/run_summary.py#L21)

**Workflow Integration**

- Demo runs persist summaries for approved and routed outcomes.
  [`demo_pipeline_service.py:128`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L128)

- Live brief runs persist summaries at the manual-gate boundary.
  [`live_brief_service.py:61`](../../Content_MultiAgent/src/seo_content_pipeline/services/live_brief_service.py#L61)

- CLI prints and manifests the per-job summary path.
  [`demo.py:130`](../../Content_MultiAgent/src/seo_content_pipeline/cli/demo.py#L130)

**Verification And Docs**

- Covers fresh, approved, routed and missing-decision-artifact behavior.
  [`test_run_summary_service.py:21`](../../Content_MultiAgent/tests/test_run_summary_service.py#L21)

- Documents run summary as an interview artifact.
  [`README.md:52`](../../Content_MultiAgent/README.md#L52)

- Documents the manifest field and job-level artifact purpose.
  [`artifact-map.md:26`](../../Content_MultiAgent/docs/artifact-map.md#L26)
