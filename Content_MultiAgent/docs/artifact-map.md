# Artifact Map

Artifacts are stored under `artifacts/jobs/<job_id>/` by default. The `ArtifactStore` writes files through the registry in `models/artifacts.py`, so filenames are not scattered through the codebase.

## Demo Index

`make demo-all` writes `artifacts/demo/demo-summary.json` as a versioned index of
the BP, LP and GP demo runs. This file is outside individual job folders and is
intended for interview navigation.

| Field | Purpose |
| --- | --- |
| `version` | Manifest contract version. Current value: `2`. |
| `requested_demo` | Requested CLI scenario, usually `all`. |
| `mode` | Article generation mode used for the run. |
| `artifact_root` | Root folder where job folders were written. |
| `run_count` | Number of entries in `runs`. |
| `runs[].demo` | Scenario key: `bp`, `lp`, or `gp`. |
| `runs[].article_type` | Article type used by the job: `BP`, `LP`, or `GP`. |
| `runs[].input_file` | Stable source input used for the job. |
| `runs[].demo_path` | Scenario purpose category, such as `happy_path`. |
| `runs[].purpose` | Human-readable explanation of why this scenario exists. |
| `runs[].artifact_dir` | Generated job folder to open during a demo. |
| `runs[].status` | Observed outcome: `approved`, `needs_revision`, or `needs_human_review`. |
| `runs[].decision_artifact` | Path to the report that proves the scenario outcome. |
| `runs[].final_package` | Path to the human-readable final package for approved runs; otherwise `null`. |
| `runs[].final_qa_report` | Path to final QA for approved runs; otherwise `null`. |

## Core State

| File | Purpose |
| --- | --- |
| `metadata.json` | Job identity, current stage, terminal status and status history for UI display. |
| `input.json` | Original dry input and selected article type. |
| `state.json` | Lightweight workflow state: artifact paths, QA flags, revision attempts, routing notes, uniqueness details and localization geos. |

## Content And QA

| File | Stage | QA decision role |
| --- | --- | --- |
| `brief.json` | SEO brief | Defines topic, goal, audience, keywords and outline. |
| `brief_qa.json` | Brief QA | Records completeness checks before writing. |
| `english_original.md` | Writing | Source article used by QA, uniqueness and localization. |
| `english_original_rejected.md` | Routed revision | Preserved LP draft before its targeted correction. |
| `article_validation.json` | Writing validation | Deterministic article checks such as structure and word count. |
| `editorial_qa.json` | Editorial review | Checks factual discipline, structure and editorial risk. |
| `revision_history.json` | Routed revision | Preserves failed QA evidence and records its correction outcome. |
| `seo_qa.json` | SEO QA | Checks keyword and heading intent; failed checks can trigger revision routing. |
| `uniqueness.json` | Uniqueness check | Records manual, mock or provider score and supports the uniqueness gate. |

## Localization And Package

| File | Purpose |
| --- | --- |
| `localization_es.md` | Spanish localization after English QA and uniqueness pass. |
| `localization_it.md` | Italian localization after English QA and uniqueness pass. |
| `localization_fr.md` | French localization after English QA and uniqueness pass. |
| `final_package.md` | Human-readable final content package. |
| `final_package.json` | Machine-readable final package for inspection or integration. |
| `final_qa_report.json` | Final readiness report with completed stages, failed checks, uniqueness result, localization status and final routing guidance. |

## QA Decisions

QA decisions are made from persisted reports and state flags. A job is approved only when mandatory artifacts exist, QA reports pass, the uniqueness gate passes, all localizations exist and the final package is assembled. If a required check fails, final QA writes `needs_revision`, adds revision routing guidance, and records the target stage in `final_qa_report.json`.

The stable demo scenarios intentionally stop at different decision points: BP
continues through final QA, LP stops after editorial QA with writing revision
guidance, and GP stops after editorial QA for human link-placement review. In the
Streamlit LP walkthrough, an explicit correction action continues that same job to
approval while preserving its original decision in `revision_history.json` and its
rejected wording in `english_original_rejected.md` for read-only version comparison.
