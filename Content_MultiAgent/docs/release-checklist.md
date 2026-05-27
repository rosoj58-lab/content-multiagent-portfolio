# Release Checklist

Use this before calling a change interview-ready or before tagging a portfolio
release.

## 1. Local Quality Gate

Run from `Content_MultiAgent/`:

```bash
uv sync
uv run ruff check .
uv run pytest
```

The test suite should pass without requiring OpenAI, Copyleaks or other external
credentials.

## 2. Demo Readiness

Regenerate the stable demo manifest:

```bash
make release-check
```

`make release-check` delegates to `make interview-check`, which runs the local
quality gate, lists demo scenarios and regenerates the demo summary manifest.

For a focused smoke check:

```bash
uv run seo-demo --demo bp --mode demo
```

For full scenario coverage:

```bash
uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json
```

Inspect generated `artifacts/jobs/<job_id>/` folders and confirm:

- BP contains `final_package.md`, `final_package.json` and an approved
  `final_qa_report.json`.
- LP contains `editorial_qa.json` with a writing revision route for an unsupported
  performance claim.
- GP contains `editorial_qa.json` with a human-review escalation for contextual
  link placement.
- `artifacts/demo/demo-summary.json` lists BP as `approved`, LP as
  `needs_revision` and GP as `needs_human_review`.

In Streamlit, run LP, edit `Replacement statement` and click `Apply correction`;
confirm the same job contains `revision_history.json`, an approved
`final_qa_report.json` and a final package, while the scorecard shows resolved
revision evidence. Submit wording matching a promotional-result pattern once and
confirm it is rejected
without a final package. Confirm
`english_original_rejected.md` preserves the unsupported claim and
`Revision Comparison` shows it beside the approved version.

When presenting the optional OpenAI integration and a disposable local key is
available, create a separate new job and click `Generate live SEO brief`. Confirm
only `brief.json` and `brief_qa.json` are added before the state stops at
`waiting_for_human`; this paid action is not required for release readiness.

## 3. Docker Check

Run from the Git/Compose root when dependencies, Dockerfile or Compose config
changed:

```bash
docker compose build
docker compose run --rm app uv run pytest
```

Use `docker compose up` for a manual containerized Streamlit check when app
startup behavior changed.

## 4. Documentation Review

Update these files when their promises changed:

- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/interview-cheatsheet.md`
- `docs/roadmap.md`
- `docs/troubleshooting.md`

If an architecture decision changed, add or update an ADR under
`docs/decisions/`.

## 5. Security And Privacy Review

Before sharing a release publicly:

- Confirm no `.env`, `.env.*`, API keys, provider tokens or private generated
  content are committed.
- Review generated artifacts for customer data, unpublished business details and
  secrets.
- Keep the default demo path offline-first unless the ADR has been revisited.

## 6. Git Review

Before publishing or demoing:

```bash
git status --short
git log --oneline -6
```

The working tree should be clean, and the latest commits should describe
coherent portfolio improvements.
