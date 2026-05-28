---
title: 'Add Recent Job History Picker'
type: 'feature'
created: '2026-05-28'
status: 'done'
baseline_commit: '8d67a5b2bfa893bac8520fefb994898d0bb63036'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/artifact-map.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** После нескольких demo/live прогонов Streamlit показывает только job из текущей session state. Для портфолио это неудобно: чтобы вернуться к BP/LP/GP или live brief результату, приходится искать папку `artifacts/jobs/<job_id>/` вручную и заново запускать сценарий.

**Approach:** Добавить компактный recent jobs picker в Streamlit, который читает последние локальные job folders из существующего `ARTIFACT_ROOT`, показывает статус/тип/decision summary и позволяет загрузить выбранный job в текущий экран. Это улучшает демонстрацию без базы данных, без hosted state и без изменения workflow execution.

## Boundaries & Constraints

**Always:** Источник истории — только существующие локальные artifacts under `artifact_root`; UI должен загружать job через существующие `metadata.json`, `state.json` и artifact registry contracts; список должен быть read-only и не менять job state; выбор job должен переиспользовать текущие panels: summary, actions where valid, scorecard, timeline and artifact panel; corrupt/incomplete folders should not crash the app.

**Ask First:** Добавление database-backed job history, multi-user history, deletion/cleanup actions, search/filtering beyond a small recent list, analytics dashboard, cross-machine sync, editable job metadata, or changing job id generation.

**Never:** Не сканировать filesystem outside configured `artifact_root`; не создавать или запускать jobs автоматически при просмотре history; не исправлять поврежденные artifacts silently; не показывать secrets/raw provider responses; не превращать recent list в новый source of truth.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| No jobs yet | Empty or missing `artifact_root` | UI shows a quiet empty state and create-job form remains usable | Missing directory is treated as zero jobs |
| Recent demo jobs exist | BP/LP/GP folders with metadata/state/run_summary | UI lists newest jobs with article type, status, stage and generated artifact count | N/A |
| Select existing job | Operator chooses a job and clicks load | Current UI switches to that job and renders normal scorecard/timeline/artifacts | Invalid selection gets controlled error and does not clear current job |
| Corrupt folder | Folder missing `metadata.json` or `state.json` | Folder is skipped from the list | If selected job becomes unreadable, show controlled recovery guidance |
| Many job folders | Artifact root contains more than display limit | UI shows newest N by metadata/update or filesystem time | Older jobs remain on disk and are not deleted |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/services/artifact_store.py` -- root path and safe job directory helpers; add or reuse listing behavior without broad filesystem access.
- `src/seo_content_pipeline/services/job_history_service.py` -- new read-only service for recent job summaries and loading selected job metadata/artifact paths.
- `src/seo_content_pipeline/services/job_service.py` -- existing `CreateJobResult` contract used by the UI; add a read/load method only if that keeps app code simple.
- `src/seo_content_pipeline/ui/components.py` or new `ui/job_history.py` -- Streamlit component for recent job picker with empty/corrupt-safe behavior.
- `app.py` -- render recent jobs before/near create form and set `st.session_state["current_job_result"]` when a job is loaded.
- `tests/test_app_shell.py`, `tests/test_demo_observability.py`, new focused tests -- verify service ordering, corrupt folder skip, load behavior and UI selection.
- `README.md`, `docs/demo-script.md`, `docs/interview-cheatsheet.md`, `docs/roadmap.md` -- document that recent jobs are local artifact navigation, not production history.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/services/job_history_service.py` -- implement read-only recent job listing and selected job loading from persisted artifacts.
- [x] `src/seo_content_pipeline/ui/` and `app.py` -- add a compact recent-job picker that loads a selected job into existing UI panels without duplicating observability views.
- [x] `tests/` -- cover no jobs, ordered recent jobs, corrupt folder skip, selected job load and UI behavior.
- [x] `README.md` and `docs/` -- document the local recent job workflow and its intentional non-production boundary.

**Acceptance Criteria:**
- Given no persisted jobs, when Streamlit opens, then the recent jobs area does not fail and the create-job flow is unchanged.
- Given multiple persisted demo jobs, when Streamlit opens, then the newest jobs are listed with status/stage/type evidence from artifacts.
- Given a listed job is selected, when the operator clicks load, then the existing scorecard/timeline/artifact panel renders that job without rerunning the workflow.
- Given a malformed job folder exists, when recent jobs are listed, then the malformed folder is skipped or reported as controlled recovery, not a traceback.
- Given the release gate runs, when tests execute, then existing BP/LP/GP outcomes and `run_summary.json` behavior remain unchanged.

## Spec Change Log

## Design Notes

Keep this as local artifact navigation. A simple service-level shape is enough:

```python
class RecentJobSummary(BaseModel):
    job_id: str
    article_type: ArticleType | None
    status: WorkflowStatus
    current_stage: WorkflowStage
    updated_at: datetime
    artifact_count: int
```

Ordering should prefer `metadata.updated_at` if present, then folder modified time as fallback. Loading a job should return the same `CreateJobResult` shape the app already uses, so downstream UI stays unchanged.

## Verification

**Commands:**
- `uv run ruff check .` -- expected: new service/UI/tests pass lint.
- `uv run pytest tests/test_app_shell.py tests/test_demo_observability.py tests/test_job_service.py tests/test_readme_docs.py tests/test_interview_docs.py` -- expected: focused UI/service/docs pass.
- `make --no-print-directory release-check` -- expected: full offline demo outcomes and run summary generation remain unchanged.

## Suggested Review Order

**Entry Point**

- Wires read-only history before creation while keeping create flow intact.
  [`app.py:40`](../../Content_MultiAgent/app.py#L40)

**History Service**

- Lists only configured artifact-root folders and skips corrupt jobs safely.
  [`job_history_service.py:47`](../../Content_MultiAgent/src/seo_content_pipeline/services/job_history_service.py#L47)

- Loads selected jobs into the existing CreateJobResult UI contract.
  [`job_history_service.py:61`](../../Content_MultiAgent/src/seo_content_pipeline/services/job_history_service.py#L61)

- Builds labels with type, status, stage, artifact count and decision file.
  [`job_history_service.py:128`](../../Content_MultiAgent/src/seo_content_pipeline/services/job_history_service.py#L128)

**Streamlit UI**

- Presents empty state or load form without running workflow side effects.
  [`job_history.py:8`](../../Content_MultiAgent/src/seo_content_pipeline/ui/job_history.py#L8)

**Coverage**

- Covers missing root, ordering, corrupt folders, limits and load shape.
  [`test_job_history_service.py:30`](../../Content_MultiAgent/tests/test_job_history_service.py#L30)

- Verifies the app can load a recent job without rerunning the workflow.
  [`test_app_shell.py:64`](../../Content_MultiAgent/tests/test_app_shell.py#L64)
