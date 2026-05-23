# Security And Privacy

This project is a local portfolio demo. It is designed to be safe to run and
screen-share without requiring production credentials or hosted infrastructure.

## Supported Demo Boundary

The supported interview path is offline-first:

- `uv run seo-demo --demo bp --mode demo`
- `uv run seo-demo --demo all --mode demo`
- `make interview-check`

These commands must work without OpenAI, Copyleaks or other paid external
credentials.

## Secrets

- Do not commit `.env`, `.env.*`, API keys, provider tokens or Streamlit secrets.
- Keep `.env.example` committed with empty placeholder values only.
- Use `OPENAI_API_KEY`, `COPYLEAKS_EMAIL` and `COPYLEAKS_API_KEY` only in a local
  `.env` file when testing external integrations.
- Rotate any credential immediately if it is accidentally pasted into a prompt,
  terminal transcript, issue, commit or generated artifact.

## Local Artifacts

Generated outputs live under `artifacts/jobs/*` and `artifacts/demo/*`. Treat
them as local runtime data, not source files.

Before sharing a generated artifact publicly, check that the dry input and final
package do not contain private customer data, unpublished business details or
live credentials.

## External Providers

External providers are optional integration points behind provider boundaries.
The default demo path should not make direct network calls to LLM or plagiarism
services. If a provider is enabled manually, validate it with disposable test
content first.

## Dependency And Environment Hygiene

- Use Python 3.12 as pinned in `.python-version`.
- Prefer `uv sync --frozen` in CI-style checks.
- Use Docker when you need an isolated environment for this project.
- Keep generated caches and virtual environments out of commits.

## Reporting

This is a personal portfolio repository. For security issues, open a private
conversation with the repository owner instead of publishing secrets or exploit
details in a public issue.
