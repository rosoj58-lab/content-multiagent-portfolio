# ADR 0001: Offline-First Demo And Provider Boundaries

## Status

Accepted.

## Context

The project is a portfolio application for interviews, not a hosted SaaS
product. The core demo must be repeatable on a local machine without waiting for
external services, paying for API calls or exposing credentials during a screen
share.

At the same time, the product concept includes real-world integration points:
LLM generation, uniqueness checking and optional Copyleaks-style verification.
Those concerns should be visible in the architecture without making the local
demo fragile.

## Decision

Keep the interview path offline-first and deterministic. External capabilities
must sit behind provider boundaries and be optional for the default demo.

Concretely:

- The stable BP, LP and GP demo paths run without OpenAI or Copyleaks
  credentials.
- One optional `Generate live SEO brief` action may call OpenAI only after an
  operator configures a local key and explicitly selects that action.
- `providers/` owns uniqueness integrations, including manual, mock and optional
  Copyleaks-compatible implementations.
- Services depend on provider contracts instead of directly calling vendor APIs.
- Artifacts remain file-based under `artifacts/jobs/<job_id>/` so every stage can
  be inspected after a run.
- README, demo scripts and tests treat offline execution as the supported
  baseline.

## Consequences

Positive consequences:

- The demo is reliable in interviews and CI-like local checks.
- The architecture still shows how real integrations would be added.
- A reviewer can inspect one real model-backed brief and its deterministic QA
  state without making the full demo depend on paid calls.
- Tests can assert behavior without network flakiness or secret management.
- The project is easier to clone, run and review from GitHub.

Tradeoffs:

- The complete demo content is deterministic; the optional live path proves only
  SEO brief generation, not a complete model-backed pipeline.
- The optional Copyleaks path is a boundary demonstration, not a full production
  integration.
- Hosted execution, async workers, queues and persistent databases are deferred.

## Validation

The decision is validated by:

- `uv run seo-demo --demo all --mode demo`
- `make interview-check`
- `uv run pytest`
- Documentation links from `README.md`, `docs/architecture-summary.md` and
  `docs/interview-cheatsheet.md`

If a future change makes credentials mandatory for the default demo path, this
ADR must be revisited.
