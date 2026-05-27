---
title: 'Add Operator-Authored LP Claim Correction'
type: 'feature'
created: '2026-05-26'
status: 'done'
baseline_commit: '9df53d2b37896d62111f8ce3992b07ffbfca8277'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/demo-script.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent - do not modify unless human renegotiates">

## Intent

**Problem:** LP walkthrough now proves a resolved revision and version comparison, but correction content is still automatically selected. For a portfolio demonstration this leaves the operator observing an automated retry rather than making a controlled editorial decision.

**Approach:** On the existing LP `needs_revision` path, let the operator edit the replacement wording for the routed unsupported claim, deterministically validate that narrow correction, persist it in revision evidence, and continue the same established QA-to-approval flow.

## Boundaries & Constraints

**Always:** Keep the initial LP failed draft/report unchanged until explicit submit; edit only the one routed commercial-claim statement inside the controlled demo article; validate operator wording before writing snapshot/history/current article artifacts; retain the same `job_id`, rejected snapshot, comparison view and normal downstream gates; disclose that validation covers the routed claim pattern rather than general fact checking.

**Ask First:** Whole-document text editing, additional failed stages, multiple revision attempts, source-grounded claim extraction, live LLM/fact-check services, or changing GP human review.

**Never:** Do not approve blank correction wording, performance numbers, percentages or guarantee-style claims entered as replacement text; do not persist a revision attempt when correction validation rejects input; do not imply this targeted form verifies arbitrary facts or is a production content editor.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Safe operator correction | LP at editorial `needs_revision`; concise non-promissory replacement statement | Same job snapshots rejected article, writes operator statement into corrected draft/history, runs normal gates and reaches `approved` | N/A |
| Unsafe operator correction | Replacement is blank or includes numeric/percentage/guarantee performance claim | Job remains `needs_revision`; original article/report remain current; no snapshot/history is created | Controlled validation guidance beside the form |
| Unsupported job state | BP, GP or LP already completed | Correction editor is absent and service cannot apply the action | Existing controlled rejection remains available at service boundary |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/services/demo_pipeline_service.py` -- existing LP continuation and deterministic article fixture; inject validated operator wording before preservation/continuation.
- `src/seo_content_pipeline/models/revision.py` -- structured audit entry for the submitted correction statement and its resolution.
- `src/seo_content_pipeline/ui/`, `app.py` -- LP correction form, safe default wording and controlled validation presentation.
- `tests/test_demo_pipeline_service.py`, `tests/test_app_shell.py`, `tests/test_demo_observability.py` -- safe correction, rejected unsafe submission and persisted evidence/UI proof.
- `README.md`, `docs/demo-script.md`, `docs/interview-cheatsheet.md`, `docs/roadmap.md` -- describe human-in-the-loop demo truthfully and defer full editing.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/models/revision.py`, `src/seo_content_pipeline/services/demo_pipeline_service.py` -- accept one operator correction statement, validate it before mutations, embed it in corrected LP content and persist it in revision history.
- [x] `src/seo_content_pipeline/ui/`, `app.py` -- replace one-click LP correction with a focused edit-and-submit control and retain approved comparison rendering.
- [x] `tests/` -- verify valid statement persistence/content, blocked unsafe statements without mutation, and Streamlit operator workflow visibility.
- [x] `README.md`, `docs/`, `CHANGELOG.md` -- document targeted operator correction and honest remaining constraints.

**Acceptance Criteria:**
- Given an LP job routed for unsupported claim correction, when the operator submits safe replacement wording, then the same job is approved through existing gates and the approved article/comparison/history show that wording.
- Given an LP job routed for correction, when the operator submits blank or unsafe promotional wording, then a controlled message is shown and no correction artifacts or approved state are created.
- Given BP, GP or an already-approved LP, when the app is rendered, then no operator correction form is presented.

## Spec Change Log

## Design Notes

This feature edits the known failing statement, not arbitrary Markdown. A deterministic guard can defensibly reject the risk demonstrated by the portfolio scenario before the offline editorial pass; arbitrary user-authored factual validation would require a separate source-grounding design.

## Verification

**Commands:**
- `uv run ruff check .` -- expected: lint passes.
- `uv run pytest tests/test_demo_pipeline_service.py tests/test_demo_observability.py tests/test_app_shell.py` -- expected: correction form, validation and evidence lifecycle pass.
- `make --no-print-directory release-check` -- expected: full regression suite passes; initial BP/LP/GP outcomes remain distinct.

## Suggested Review Order

**Validated Correction Path**

- Start here: same-job continuation validates input before preserving revision evidence.
  [`demo_pipeline_service.py:137`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L137)

- Narrow deterministic guard blocks known commercial-result patterns before artifact mutation.
  [`demo_pipeline_service.py:218`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L218)

**Operator Experience And Evidence**

- Streamlit exposes the focused submission only on an eligible LP revision.
  [`app.py:89`](../../Content_MultiAgent/app.py#L89)

- Form limits the operator interaction to one replacement statement.
  [`components.py:63`](../../Content_MultiAgent/src/seo_content_pipeline/ui/components.py#L63)

- Revision history records the submitted wording alongside resolution evidence.
  [`revision.py:11`](../../Content_MultiAgent/src/seo_content_pipeline/models/revision.py#L11)

**Verification And Demo Truth**

- Service tests prove persistence, approval, and rejection without evidence mutation.
  [`test_demo_pipeline_service.py:129`](../../Content_MultiAgent/tests/test_demo_pipeline_service.py#L129)

- UI tests prove eligible visibility and controlled rejection behavior.
  [`test_app_shell.py:45`](../../Content_MultiAgent/tests/test_app_shell.py#L45)

- Interview flow documents the focused guard without claiming general fact checking.
  [`demo-script.md:15`](../../Content_MultiAgent/docs/demo-script.md#L15)
