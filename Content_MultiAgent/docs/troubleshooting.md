# Troubleshooting

This runbook covers common local demo issues. It assumes commands are run from `Content_MultiAgent/` unless noted.

## App Does Not Open

Check whether Streamlit is listening on port `8501`:

```bash
curl -I http://localhost:8501
```

If another process owns the port, stop it or start Streamlit on a different port:

```bash
uv run streamlit run app.py --server.port 8502
```

## Dependencies Drift

CI uses the lockfile:

```bash
uv sync --frozen
```

For local development after changing `pyproject.toml`, run:

```bash
uv lock
uv sync
```

## Demo Smoke Test

Use the CLI when you want to verify the pipeline without opening the browser:

```bash
uv run seo-demo --demo bp --mode demo
```

To confirm available scenario names:

```bash
uv run seo-demo --list-demos
```

The BP command should print `status=approved`, `decision_artifact=...`,
`final_package=...` and `final_qa_report=...`.

For all stable demo paths, generate a manifest:

```bash
uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json
```

The all-scenario output should show BP as `approved`, LP as `needs_revision` and
GP as `needs_human_review`. LP and GP intentionally print
`final_package=not_generated`; inspect their `decision_artifact` instead.

## Generated Artifacts

Runtime job folders are written under:

```text
artifacts/jobs/<job_id>/
```

Those folders are ignored by Git. To inspect a run, open the printed `artifact_dir`
and check `state.json` plus the printed `decision_artifact`. Approved BP runs also
include `final_package.md` and `final_qa_report.json`.

## Docker

Run Docker commands from the repository root, one directory above `Content_MultiAgent`:

```bash
docker compose up --build
docker compose run --rm app uv run pytest
```

If dependencies fail inside Docker, rebuild the image:

```bash
docker compose down
docker compose build --no-cache
docker compose up
```

## External Credentials

The repeatable demo does not need OpenAI or Copyleaks credentials. Leave these empty for the offline demo:

```bash
OPENAI_API_KEY=
COPYLEAKS_EMAIL=
COPYLEAKS_API_KEY=
```

## Fast Health Check

Run the local quality gate:

```bash
make ci
```

Expected result: `ruff` passes and the full `pytest` suite passes.
