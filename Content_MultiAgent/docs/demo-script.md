# Demo Script

## Opening Pitch

This is a local SEO Content Multi-Agent Pipeline. It turns dry source notes into an inspectable content package: SEO brief, English original, QA reports, uniqueness result, Spanish/Italian/French localizations, final Markdown/JSON package and final QA report. The point is not to hide work behind one prompt. The point is to show controlled stages, persisted artifacts and revision routing.

## Happy Path: BP

Use `examples/inputs/bp-demo.txt` with article type `BP`. Click `Run full demo pipeline` and explain that this path demonstrates the clean flow: dry input -> brief -> English original -> editorial QA -> SEO QA -> uniqueness gate -> localization -> final package -> final QA. In the UI, point to the progress timeline, artifact previews and download actions. In the filesystem, open `artifacts/jobs/<job_id>/` and show `state.json`, `brief.json`, `english_original.md`, QA JSON files, localizations and final package files.

## Revision Path: LP

Use `examples/inputs/lp-demo.txt` with article type `LP`. This case is written to discuss commercial-copy risk. If unsupported claims or weak SEO coverage appear, the system should explain the failed check and route the job to the relevant stage. The talking point is FR18: failed checks do not become vague errors; they become revision guidance with a target stage.

## Human-Review Path: GP

Use `examples/inputs/gp-demo.txt` with article type `GP`. This case is for link-placement sensitivity. Explain that guest posts can require human review because a native link may become too promotional. Human review is a feature, not a failure: the workflow preserves control where editorial judgment matters.

## Closing Points

Mention FR17 workflow status tracking, FR18 revision routing, and UX-DR6 reproducible demo flows. The project is portfolio-ready because the same inputs can be run repeatedly and every important decision is visible in artifacts rather than only in console logs.
