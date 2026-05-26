# Demo Script

## Opening Pitch

This is a local SEO Content Multi-Agent Pipeline. It turns dry source notes into an inspectable content package: SEO brief, English original, QA reports, uniqueness result, Spanish/Italian/French localizations, final Markdown/JSON package and final QA report. The point is not to hide work behind one prompt. The point is to show controlled stages, persisted artifacts and revision routing.

## Happy Path: BP

Use `examples/inputs/bp-demo.txt` with article type `BP`. Click `Run demo scenario` and explain that this path demonstrates the clean flow: dry input -> brief -> English original -> editorial QA -> SEO QA -> uniqueness gate -> localization -> final package -> final QA. In the UI, start with the Decision QA Scorecard: it exposes final approval, uniqueness threshold evidence and localization readiness. Then point to the progress timeline, artifact previews and download actions. In the filesystem, open `artifacts/jobs/<job_id>/` and show `state.json`, `brief.json`, `english_original.md`, QA JSON files, localizations and final package files.

## Revision Path: LP

Use `examples/inputs/lp-demo.txt` with article type `LP`. This scenario writes a draft
containing an unsupported 70 percent performance claim, then produces a failed
`editorial_qa.json` report with `status=needs_revision` and routing target `writing`.
The scorecard surfaces the failed claim and its correction action before you open
the draft and report side by side. The talking point is FR18: failed checks do not
become vague errors; they become revision guidance with a target stage.
Then click `Apply recommended revision`. The same job persists the failed report in
`revision_history.json`, replaces the unsupported wording, runs the existing quality
gates and finishes with an approved final package. Use the resolved revision evidence
in the scorecard to show a controlled loop rather than a hidden retry.

## Human-Review Path: GP

Use `examples/inputs/gp-demo.txt` with article type `GP`. The draft includes one
contextual portfolio link and produces `editorial_qa.json` with
`status=needs_human_review` and `requires_human_review=true`. Explain that guest
posts can require editorial judgment even when a link is contextually relevant.
Use the scorecard's next action to show why the decision belongs with an editor.
Human review is a feature, not a failure: the workflow preserves control where publication fit matters.

## Closing Points

Mention FR17 workflow status tracking, FR18 revision routing, and UX-DR6 reproducible demo flows. The project is portfolio-ready because the same inputs can be run repeatedly and every important decision is visible in artifacts rather than only in console logs.
