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

Inspect at least one generated `artifacts/jobs/<job_id>/` folder and confirm:

- `state.json` explains the final workflow status.
- `final_package.md` and `final_package.json` exist.
- `final_qa_report.json` records an approved or intentionally routed result.
- `artifacts/demo/demo-summary.json` lists BP, LP and GP runs when all scenarios
  were generated.

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
