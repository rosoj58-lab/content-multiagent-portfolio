# Roadmap

This roadmap explains the current portfolio MVP and the most useful next steps. It is intentionally conservative: the project should be presented as a working local demo, not as a production SaaS platform.

## Current MVP

- Local Streamlit app for creating and inspecting content jobs.
- Offline demo pipeline that runs without OpenAI or Copyleaks credentials.
- Terminal smoke demo through `uv run seo-demo --demo bp --mode demo`.
- Typed Pydantic models for workflow state, artifacts, QA reports, uniqueness and final QA.
- File-based artifact persistence under `artifacts/jobs/<job_id>/`.
- Deterministic QA gates for article structure, SEO signals, uniqueness thresholding and final package readiness.
- Distinct offline outcomes: BP approval, LP revision routing for unsupported claims and GP human review for sensitive link placement.
- Explicit LP correction-to-approval action with persisted revision history evidence.
- Spanish, Italian and French localization artifacts.
- Markdown and JSON final package exports.
- GitHub Actions quality gate with `uv sync --frozen`, `ruff` and `pytest`.

## Next Technical Steps

1. Async stage execution

   Move long-running stages into a queue or background worker so Streamlit can show progress without blocking the request lifecycle.

2. Expanded Revision Workspace

   Extend the controlled LP correction into free-form edits, additional failed stages and side-by-side artifact version comparison.

3. Real LLM provider configuration

   Wire an OpenAI-backed client behind the existing `LLMRunner` boundary while keeping deterministic offline demo mode available.

4. Real uniqueness provider execution

   Extend the Copyleaks provider from availability metadata into a real provider call, with timeout handling, secrets validation and provider-specific errors.

5. Durable storage

   Replace or supplement file-based state with a database when job history, search, multi-user access or hosted deployment becomes necessary.

6. Observability

   Add structured logs, stage durations, retry counters and exportable run summaries for debugging.

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
- Manual uniqueness is reliable for interviews but must be replaced or supplemented for production.
- Localization quality is represented structurally in the MVP; production quality would need stronger language QA.
- The UI is optimized for demonstration, not for high-volume editorial operations.

## Interview Framing

The strongest way to present the project is as a working local product with production-shaped boundaries. The MVP proves orchestration, artifacts, QA gates, routing and reproducibility. The roadmap shows a realistic path toward production without pretending those capabilities already exist.
