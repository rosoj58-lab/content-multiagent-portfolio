# Artifact Map

Artifacts are stored under `artifacts/jobs/<job_id>/` by default. The `ArtifactStore` writes files through the registry in `models/artifacts.py`, so filenames are not scattered through the codebase.

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
| `article_validation.json` | Writing validation | Deterministic article checks such as structure and word count. |
| `editorial_qa.json` | Editorial review | Checks factual discipline, structure and editorial risk. |
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
