# Interview Cheatsheet

## 60-Second Pitch

This is a local multi-agent SEO content pipeline built as a portfolio project. It turns dry source notes into a traceable content package: SEO brief, English article, deterministic QA reports, uniqueness gate, Spanish/Italian/French localizations, final Markdown/JSON package and final QA report. The point is not that one prompt writes content. The point is that each stage has typed contracts, persisted artifacts, quality gates and revision routing.

## Fast Demo Path

Use the BP happy path first:

```bash
uv run streamlit run app.py
```

Then open `http://localhost:8501`, paste `examples/inputs/bp-demo.txt`, select `BP`, keep Mode as `demo`, create a job and click `Run demo scenario`.

For a terminal smoke demo:

```bash
uv run seo-demo --demo bp --mode demo
```

To list the available scenarios before choosing one:

```bash
uv run seo-demo --list-demos
```

To generate BP, LP and GP artifacts in one terminal run:

```bash
uv run seo-demo --demo all --mode demo
```

For a quick manifest of all generated input files, article types and job folders:

```bash
uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json
```

Before an interview, prepare demo artifacts and run the local quality gate:

```bash
make interview-check
```

Before tagging or presenting a portfolio release, the equivalent release command is:

```bash
make release-check
```

The generated manifest proves three distinct outcomes: BP is `approved`, LP is
`needs_revision`, and GP is `needs_human_review`. Open BP to show `final_package.md`
and `final_qa_report.json`; open LP and GP to show their `english_original.md`,
`editorial_qa.json` and routed status in `state.json`. Each generated job also has
`run_summary.json`, a compact card with status, decision artifact and generated
artifact list. In Streamlit, begin each scenario with the Decision QA Scorecard:
it makes the evidence and next action visible before opening the raw artifacts.

For the strongest workflow demonstration, run LP in Streamlit, show its
`needs_revision` scorecard, replace the routed claim using `Replacement statement`,
then click `Apply correction`. The same job ends `approved`, while
`revision_history.json` preserves the failed decision and submitted correction and
`english_original_rejected.md` preserves the rejected wording. Open
`Revision Comparison` to show the operator's decision side by side with the original.

## What To Emphasize

- It is staged orchestration, not a single prompt.
- Artifacts make the workflow inspectable and debuggable.
- `run_summary.json` gives each job an exportable interview card.
- Human approval remains explicit at sensitive gates.
- Failed checks route to a target stage instead of becoming vague errors.
- Manual/offline uniqueness keeps the demo reliable without paid credentials.
- Optional Copyleaks support is isolated behind a provider boundary.
- Optional `Generate live SEO brief` proves one real OpenAI-backed stage without making the complete demo dependent on a paid service.
- CI runs `ruff` and `pytest`, so quality is not only manual.

## Architecture Talking Points

- `models/` defines contracts for state, artifacts, content, QA, uniqueness and final QA.
- `services/` owns workflow actions: job creation, brief generation, QA, uniqueness, localization, export and final QA.
- `validators/` handles deterministic checks that do not need an LLM.
- `providers/` isolates uniqueness implementations.
- `ui/` renders Streamlit decision scorecards, status, artifact previews and controlled errors.
- `cli/` exposes the same offline demo path through `seo-demo`.

## Honest Tradeoffs

- This is a local MVP, not a hosted production system.
- The repeatable complete demo uses deterministic offline content; the optional live OpenAI action stops after brief QA.
- Manual uniqueness is included so the project is demoable without external plagiarism credentials.
- ADR `docs/decisions/0001-offline-first-demo-and-provider-boundaries.md` explains why external services are optional provider implementations instead of requirements for the demo.
- CMS publishing, live SERP research and production auth are intentionally out of scope.
- File-based persistence is simple and inspectable; a production version would likely use a database and queue.

## Likely Questions

**Why multi-agent instead of one prompt?**

Because the project models the production workflow: brief, writing, editorial QA, SEO QA, uniqueness, localization and final QA have different responsibilities. Splitting them makes failures easier to inspect and route.

**Where is quality controlled?**

Quality is controlled through deterministic validators, structured QA reports, manual approval gates, uniqueness thresholding and final QA. The final package is approved only when mandatory artifacts and gates pass.

**How would this become production-ready?**

Add auth, durable database storage, queue-based execution, live model-backed writing and QA after manual approval, real plagiarism provider calls, observability logs/metrics and deployment infrastructure. The current boundaries are designed so those can be added without rewriting the whole app.

**What are you most proud of technically?**

The project is testable and inspectable. The same workflow can be run from Streamlit or `seo-demo`, artifacts show each decision, and CI checks the code path with `ruff` and `pytest`.

**What would you improve next?**

The next useful improvement would extend the explicit live path from brief QA into approval-controlled writing with spend and failure handling, while retaining the repeatable offline demo.
