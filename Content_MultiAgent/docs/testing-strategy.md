# Testing Strategy

The test suite is designed to prove that the local MVP is runnable, inspectable and safe to demo without external credentials. It combines small unit tests with integration-style checks around the offline pipeline, CLI, documentation and CI configuration.

## Quality Gate

Run the same checks locally and in CI:

```bash
uv sync --frozen
uv run ruff check .
uv run pytest
```

For shorter local commands:

```bash
make ci
```

## Coverage Areas

- Models and artifact registry: stable workflow contracts, artifact keys and serialization.
- Artifact storage and job service: durable local job folders, metadata, input and state.
- Brief, writer, QA and localization services: stage transitions, persisted reports and routing flags.
- Deterministic validators: brief completeness, article structure, word count, SEO signals and uniqueness score validation.
- Uniqueness providers: manual, mock and optional Copyleaks availability without requiring external credentials.
- Final package and final QA: Markdown/JSON package assembly, failed-check routing and approved status.
- Stable scenario outcomes: BP approval, LP editorial revision routing and GP human-review escalation.
- LP correction lifecycle: preserved failed QA evidence, targeted correction and approval of the same job.
- LP version comparison: rejected draft snapshot and approved read-only comparison presentation.
- LP operator correction: accepted replacement evidence and rejected unsafe wording without mutation.
- Optional OpenAI live brief: Responses adapter, provider failures and brief QA/manual-gate orchestration with mocked responses only.
- Demo inputs and offline demo pipeline: BP/LP/GP inputs, Streamlit demo path and `seo-demo` terminal smoke path.
- UI helpers: decision QA scorecard, status timeline, derived duration labels, artifact previews, controlled error messages and download actions.
- Documentation and repository health: README, Docker docs, interview docs, sample outputs, roadmap, root README and scaffold-cleanliness.
- CI configuration: GitHub Actions uses Python 3.12 and `uv sync --frozen`.

## Why This Matters

The project is a portfolio MVP, so the tests prioritize reliability of the demo path and clarity of the architecture boundaries. The highest-risk paths are the stage transitions, artifact persistence, QA gates and final package approval. Those are covered directly.

## What Is Not Covered Yet

- Browser-level regression automation for every Streamlit interaction.
- Real billed OpenAI API requests.
- Real Copyleaks provider calls.
- Hosted deployment behavior.
- Multi-user concurrency.

Those gaps match the current roadmap. They are not hidden production claims.
