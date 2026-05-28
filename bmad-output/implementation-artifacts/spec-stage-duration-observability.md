---
title: 'Add Stage Duration Observability'
type: 'feature'
created: '2026-05-28'
status: 'done'
baseline_commit: '6ebe310a1ae223d3fe848dd82be9d7661e2a1513'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/artifact-map.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The portfolio demo already shows stage status and artifacts, but it does not explain how long each stage took or where the workflow spent time. For interviews, this weakens the “inspectable multi-agent pipeline” story because observability stops at status transitions.

**Approach:** Add a derived stage duration summary from existing `status_history` timestamps and surface it in `run_summary.json` plus the Streamlit timeline. Keep it read-only and deterministic: no background worker, no telemetry service, no database, and no changes to stage execution behavior.

## Boundaries & Constraints

**Always:** Use persisted `metadata.json` / `state.json` history as the source; treat duration data as derived observability, not workflow state; keep existing jobs readable when they lack duration fields; show compact human-readable durations in Streamlit; include machine-readable seconds in `run_summary.json`; preserve current BP/LP/GP outcomes.

**Ask First:** Adding real-time timers, async execution, external logging/metrics, tracing vendors, database-backed events, performance dashboards, retry analytics beyond existing counters, or changing how services create status history entries.

**Never:** Do not mutate historical status entries just to compute durations; do not infer durations from filesystem timestamps when status history is enough; do not add network calls; do not make tests depend on wall-clock sleeps; do not claim these are production performance metrics.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Fresh job | Only initial `input_received` history exists | `run_summary.json` includes zero completed duration entries and total duration of `0` | N/A |
| Approved BP demo | Multiple ordered status history entries ending at final QA approval | Summary lists per-stage elapsed seconds between consecutive transitions; timeline displays durations for completed stages | N/A |
| Routed LP or GP demo | Workflow stops at `needs_revision` or `needs_human_review` | Durations are calculated up to the routed decision stage without requiring final package artifacts | N/A |
| Duplicate stage transitions | Same stage appears more than once due revision/correction | Summary aggregates elapsed seconds per stage and records transition count | N/A |
| Missing or malformed history timing | Empty history or non-monotonic timestamps | Duration summary remains empty or ignores negative intervals; UI does not crash | Controlled omission, not traceback |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/models/job.py` -- `StatusHistoryEntry` timestamp source for deriving durations.
- `src/seo_content_pipeline/models/run_summary.py` -- add typed duration entries and total duration fields.
- `src/seo_content_pipeline/services/stage_duration_service.py` -- shared deterministic duration aggregation and display formatting.
- `src/seo_content_pipeline/services/run_summary_service.py` -- derive per-stage duration data while writing `run_summary.json`.
- `src/seo_content_pipeline/services/stage_view_builder.py` -- attach derived duration labels to `StageView` objects without changing routing.
- `src/seo_content_pipeline/models/stage.py` -- expose optional duration label on timeline view model.
- `src/seo_content_pipeline/ui/progress_timeline.py` -- render duration labels compactly in Streamlit.
- `tests/test_run_summary_service.py`, `tests/test_status_presenter.py`, `tests/test_app_shell.py` -- cover summary contract, timeline view data and UI rendering.
- `README.md`, `docs/artifact-map.md`, `docs/interview-cheatsheet.md`, `docs/roadmap.md`, `docs/testing-strategy.md` -- document duration observability as local derived evidence.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/models/run_summary.py` -- add a backward-compatible duration entry contract and total duration seconds.
- [x] `src/seo_content_pipeline/services/run_summary_service.py` -- compute deterministic per-stage durations from ordered status history with duplicate-stage aggregation.
- [x] `src/seo_content_pipeline/models/stage.py`, `src/seo_content_pipeline/services/stage_view_builder.py`, `src/seo_content_pipeline/ui/progress_timeline.py` -- expose and render compact stage duration labels in the existing timeline.
- [x] `tests/` -- add focused coverage for fresh jobs, approved jobs, routed jobs, duplicate transitions and UI timeline text.
- [x] `README.md` and `docs/` -- describe duration observability as derived local demo evidence, not production telemetry.

**Acceptance Criteria:**
- Given a fresh job, when a run summary is generated, then the summary contains no completed stage duration rows and total duration is `0`.
- Given a completed BP demo, when `run_summary.json` is opened, then it contains per-stage duration rows with stage names, elapsed seconds and transition counts.
- Given LP or GP stops before final QA, when the summary is generated, then durations still describe transitions that happened before the routed decision.
- Given a job with repeated stage transitions, when durations are calculated, then repeated stage time is aggregated instead of overwriting prior time.
- Given Streamlit renders a loaded or current job, when the timeline appears, then completed stages show compact duration text and missing duration data does not break the page.

## Spec Change Log

## Design Notes

Duration should be computed from consecutive `StatusHistoryEntry.created_at` values sorted by timestamp. Attribute each interval to the stage of the earlier entry because that stage was active until the next transition. Ignore negative intervals after sorting/validation rather than failing the demo.

Keep the shape simple:

```python
class StageDurationSummary(BaseModel):
    stage: WorkflowStage
    elapsed_seconds: float
    transition_count: int
```

## Verification

**Commands:**
- `uv run ruff check .` -- expected: lint passes.
- `uv run pytest tests/test_run_summary_service.py tests/test_status_presenter.py tests/test_app_shell.py tests/test_readme_docs.py tests/test_interview_docs.py` -- expected: focused contract/UI/docs pass.
- `make --no-print-directory release-check` -- expected: full regression and demo manifest generation remain green.

## Suggested Review Order

**Duration Derivation**

- Centralizes deterministic duration aggregation from existing status history.
  [`stage_duration_service.py:8`](../../Content_MultiAgent/src/seo_content_pipeline/services/stage_duration_service.py#L8)

- Defines the backward-compatible run summary duration contract.
  [`run_summary.py:21`](../../Content_MultiAgent/src/seo_content_pipeline/models/run_summary.py#L21)

**Run Summary**

- Adds derived duration rows without changing workflow decisions.
  [`run_summary_service.py:57`](../../Content_MultiAgent/src/seo_content_pipeline/services/run_summary_service.py#L57)

**Timeline UI**

- Attaches formatted duration labels to existing StageView objects.
  [`stage_view_builder.py:118`](../../Content_MultiAgent/src/seo_content_pipeline/services/stage_view_builder.py#L118)

- Renders compact duration text in the current timeline cards.
  [`progress_timeline.py:30`](../../Content_MultiAgent/src/seo_content_pipeline/ui/progress_timeline.py#L30)

**Coverage**

- Proves duplicate stage transitions aggregate instead of overwriting.
  [`test_run_summary_service.py:114`](../../Content_MultiAgent/tests/test_run_summary_service.py#L114)

- Proves Streamlit-facing stage views expose compact labels.
  [`test_status_presenter.py:182`](../../Content_MultiAgent/tests/test_status_presenter.py#L182)
