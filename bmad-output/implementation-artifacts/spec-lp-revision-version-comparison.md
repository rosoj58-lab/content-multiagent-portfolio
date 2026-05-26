---
title: 'Show LP Revision Version Comparison'
type: 'feature'
created: '2026-05-26'
status: 'done'
baseline_commit: '0ebd126abdb0241c35e7591066630bff006ff3e0'
context:
  - '{project-root}/docs/architecture-summary.md'
  - '{project-root}/docs/demo-script.md'
  - '{project-root}/docs/roadmap.md'
---

<frozen-after-approval reason="human-owned intent - do not modify unless human renegotiates">

## Intent

**Problem:** LP correction now proves that an editorial failure was resolved, but overwriting `english_original.md` removes the exact rejected wording from the visual walkthrough. During an interview the operator cannot inspect the problematic draft against the approved correction in one view.

**Approach:** Preserve the routed LP draft as a dedicated Markdown evidence artifact before replacement, link that snapshot to the existing structured revision record, and render a read-only side-by-side comparison after the corrected job is approved.

## Boundaries & Constraints

**Always:** Keep the first LP stop and explicit correction action unchanged; preserve the rejected draft before any write to the working English Original; continue using the same `job_id` and existing QA gates; show comparison only when persisted before/after evidence is available; keep artifacts downloadable and inspectable.

**Ask First:** Adding operator text editing, supporting repeated revisions or stages beyond the existing LP editorial path, changing final package contents to include rejected text, or introducing dynamic version storage for arbitrary histories.

**Never:** Do not replace QA evidence with a purely visual diff; do not expose a comparison for BP/GP or incomplete revisions; do not represent this read-only comparison as a production editing workspace; do not bypass validation to produce the approved after-state.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| LP before correction | LP at editorial `needs_revision` | Current failed draft remains visible; comparison is absent until approved correction exists | N/A |
| LP correction approved | LP correction action succeeds | Rejected Markdown snapshot remains stored and UI shows rejected vs approved text side by side | N/A |
| Non-comparable outcome | BP, GP, or partial/missing version evidence | Ordinary artifacts and scorecard render without version comparison | Do not render misleading comparison |

</frozen-after-approval>

## Code Map

- `src/seo_content_pipeline/models/artifacts.py`, `src/seo_content_pipeline/models/revision.py` -- registry and revision linkage for a rejected Markdown snapshot.
- `src/seo_content_pipeline/services/demo_pipeline_service.py` -- LP correction boundary where the failed article must be captured before overwrite.
- `src/seo_content_pipeline/ui/`, `app.py` -- build and render a read-only comparison only for resolved evidence.
- `tests/test_demo_pipeline_service.py`, `tests/test_app_shell.py` -- persisted content and operator-visible comparison behavior.
- `docs/demo-script.md`, `docs/artifact-map.md`, `docs/roadmap.md` -- interview claim and honest remaining scope.

## Tasks & Acceptance

**Execution:**
- [x] `src/seo_content_pipeline/models/`, `src/seo_content_pipeline/models/artifacts.py` -- add a registered rejected-original Markdown artifact and reference paths in the existing revision entry.
- [x] `src/seo_content_pipeline/services/demo_pipeline_service.py` -- snapshot the failed LP text before targeted replacement and resolve the revision with the approved article path.
- [x] `src/seo_content_pipeline/ui/`, `app.py` -- add a revision-comparison view that renders the stored rejected and approved versions together after resolution.
- [x] `tests/` -- cover snapshot immutability, absence for unsupported states, and Streamlit comparison visibility after correction.
- [x] `README.md`, `docs/` -- document the version comparison walkthrough and defer free-form editing/repeated version history accurately.

**Acceptance Criteria:**
- Given an LP job routed for revision, when the correction is applied, then the rejected text containing the unsupported claim persists independently from the corrected `english_original.md`.
- Given the corrected LP has reached approval with both version paths recorded, when the operator views the job, then a read-only comparison visibly presents rejected and approved Markdown with the removed claim distinguishable.
- Given any job without completed LP comparison evidence, when the app renders, then it does not display a version comparison or imply that editing occurred.

## Spec Change Log

## Design Notes

A single registered rejected-original snapshot matches the already constrained one-correction LP demo. Generalized version collections are intentionally deferred because they only become justified with free-form editing or repeated revision loops.

## Verification

**Commands:**
- `uv run ruff check .` -- expected: lint passes.
- `uv run pytest tests/test_demo_pipeline_service.py tests/test_app_shell.py tests/test_artifact_registry.py` -- expected: stored comparison and UI behavior pass.
- `make --no-print-directory release-check` -- expected: complete suite passes and initial BP/LP/GP outcomes remain distinct.

## Suggested Review Order

**Snapshot Boundary**

- Preserve rejected wording immediately before targeted LP replacement.
  [`demo_pipeline_service.py:122`](../../Content_MultiAgent/src/seo_content_pipeline/services/demo_pipeline_service.py#L122)

- Register the snapshot as an inspectable Markdown artifact.
  [`artifacts.py:8`](../../Content_MultiAgent/src/seo_content_pipeline/models/artifacts.py#L8)

- Attach before and approved paths to structured revision evidence.
  [`revision.py:11`](../../Content_MultiAgent/src/seo_content_pipeline/models/revision.py#L11)

**Read-Only Presentation**

- Require approved LP evidence before constructing any comparison.
  [`revision_comparison.py:25`](../../Content_MultiAgent/src/seo_content_pipeline/ui/revision_comparison.py#L25)

- Render bounded side-by-side article panes after the decision scorecard.
  [`app.py:104`](../../Content_MultiAgent/app.py#L104)

**Verification And Narrative**

- Prove preserved rejected content across demo and full writing modes.
  [`test_demo_pipeline_service.py:125`](../../Content_MultiAgent/tests/test_demo_pipeline_service.py#L125)

- Prove visibility only after the operator completes LP correction.
  [`test_app_shell.py:44`](../../Content_MultiAgent/tests/test_app_shell.py#L44)

- Demonstrate the evidence trail during an interview walkthrough.
  [`demo-script.md:11`](../../Content_MultiAgent/docs/demo-script.md#L11)
