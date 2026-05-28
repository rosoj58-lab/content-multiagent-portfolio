# Roadmap

This roadmap explains the current portfolio MVP and the most useful next steps. It is intentionally conservative: the project should be presented as a working local demo, not as a production SaaS platform.

## Current MVP

- Local Streamlit app for creating and inspecting content jobs.
- Offline demo pipeline that runs without OpenAI or Copyleaks credentials.
- Terminal smoke demo through `uv run seo-demo --demo bp --mode demo`.
- Typed Pydantic models for workflow state, artifacts, QA reports, uniqueness and final QA.
- File-based artifact persistence under `artifacts/jobs/<job_id>/`.
- Read-only recent jobs picker over local artifact folders.
- Deterministic QA gates for article structure, SEO signals, uniqueness thresholding and final package readiness.
- Distinct offline outcomes: BP approval, LP revision routing for unsupported claims and GP human review for sensitive link placement.
- Explicit LP correction-to-approval action with persisted revision history evidence.
- Read-only LP comparison of the preserved rejected draft and approved correction.
- Targeted operator-authored LP claim correction with a deterministic safety guard.
- Optional OpenAI-backed live SEO brief generation followed by deterministic QA and a manual gate.
- Spanish, Italian and French localization artifacts.
- Markdown and JSON final package exports.
- Exportable per-job `run_summary.json` artifacts for interview navigation.
- Derived stage duration observability in `run_summary.json` and the Streamlit timeline.
- Derived per-job `debug_snapshot.json` artifacts for local diagnostic inspection.
- GitHub Actions quality gate with `uv sync --frozen`, `ruff` and `pytest`.

## Next Technical Steps

1. Live LLM workflow extension

   Extend the explicit live action beyond brief QA only after designing human approval, spend control and failure routing for writing and later stages.

2. Async stage execution

   Move long-running stages into a queue or background worker so Streamlit can show progress without blocking the request lifecycle.

3. Editable Revision Workspace

   Extend the focused LP claim correction into whole-article edits, additional failed stages, source-grounded validation and repeated version history.

4. Real uniqueness provider execution

   Extend the Copyleaks provider from availability metadata into a real provider call, with timeout handling, secrets validation and provider-specific errors.

5. Durable storage

   Replace or supplement file-based state with a database when job history, search, multi-user access or hosted deployment becomes necessary.

6. Observability

   Add structured logs, retry counters and richer debugging views. Current stage durations and debug snapshots are local derived evidence, not production telemetry.

## Deferred On Purpose

- Hosted deployment.
- Authentication and roles.
- CMS publishing.
- Live SERP research.
- Payment, billing or quota logic.
- Production-grade plagiarism provider dependency.
- Automated claims/fact verification against external sources.

## Known Risks

- File-based persistence is excellent for a local demo but not enough for concurrent hosted usage.
- Offline deterministic content proves orchestration, not live model quality.
- The optional live OpenAI action proves only SEO brief generation and can incur API cost.
- Manual uniqueness is reliable for interviews but must be replaced or supplemented for production.
- Localization quality is represented structurally in the MVP; production quality would need stronger language QA.
- The UI is optimized for demonstration, not for high-volume editorial operations.

## Interview Framing

The strongest way to present the project is as a working local product with production-shaped boundaries. The MVP proves orchestration, artifacts, QA gates, routing and reproducibility. The roadmap shows a realistic path toward production without pretending those capabilities already exist.
