# SEO Content Pipeline

Local portfolio application for a multi-agent SEO content workflow. The app turns dry source notes into an inspectable content package: SEO brief, English article, QA reports, uniqueness gate, Spanish/Italian/French localizations, final Markdown/JSON package and final QA report.

The project is built to be demonstrated in interviews. It does not require hosted infrastructure, OpenAI credentials or Copyleaks credentials for the repeatable demo path.

## What It Shows

- A staged content workflow instead of one opaque prompt.
- Human-in-the-loop approval and revision routing.
- Deterministic QA gates for article structure, SEO coverage and uniqueness thresholding.
- File-based artifacts under `artifacts/jobs/<job_id>/` for inspection.
- Streamlit observability: status timeline, artifact previews, download actions and controlled errors.
- Optional provider boundary for Copyleaks without making it mandatory for the local demo.

## Quick Demo

Run the app:

```bash
uv sync
uv run streamlit run app.py
```

Open `http://localhost:8501`, then:

1. Paste `examples/inputs/bp-demo.txt` into the Dry input field.
2. Select article type `BP`.
3. Keep Mode as `demo`.
4. Click `Create job`.
5. Click `Run full demo pipeline`.
6. Open the generated folder under `artifacts/jobs/<job_id>/`.

The offline demo runner creates the full approved artifact set without external APIs:

- `brief.json`
- `english_original.md`
- `article_validation.json`
- `editorial_qa.json`
- `seo_qa.json`
- `uniqueness.json`
- `localization_es.md`
- `localization_it.md`
- `localization_fr.md`
- `final_package.md`
- `final_package.json`
- `final_qa_report.json`

The same offline path can be smoke-tested from the terminal:

```bash
uv run seo-demo --demo bp --mode demo
```

## Demo Inputs

| Input | Article type | Demo path |
| --- | --- | --- |
| `examples/inputs/bp-demo.txt` | `BP` | Happy path |
| `examples/inputs/lp-demo.txt` | `LP` | Revision path discussion |
| `examples/inputs/gp-demo.txt` | `GP` | Human-review discussion |

## Development

Run from this directory when `uv` is installed locally:

```bash
uv sync
uv run ruff check .
uv run pytest
uv run streamlit run app.py
```

Or use the local shortcuts:

```bash
make lint
make test
make app
make demo
```

Run from the Git/Compose root when using Docker:

```bash
docker compose build
docker compose run --rm app uv run ruff check .
docker compose run --rm app uv run pytest
docker compose up
```

## CI

GitHub Actions runs the same quality gate on changes under `Content_MultiAgent/`:

```bash
uv sync
uv run ruff check .
uv run pytest
```

## Project Map

- `app.py` - Streamlit entrypoint.
- `src/seo_content_pipeline/cli/` - command-line demo entrypoints.
- `src/seo_content_pipeline/models/` - typed workflow, artifact, QA and content contracts.
- `src/seo_content_pipeline/services/` - stage orchestration and artifact persistence.
- `src/seo_content_pipeline/validators/` - deterministic QA checks.
- `src/seo_content_pipeline/providers/` - uniqueness provider boundary.
- `src/seo_content_pipeline/ui/` - Streamlit presentation helpers.
- `docs/` - interview setup, demo script, artifact map and architecture notes.
- `tests/` - unit and integration coverage for the local MVP.

## Useful Docs

- `docs/demo-setup.md` - local setup and demo flow.
- `docs/demo-script.md` - interview walkthrough.
- `docs/interview-cheatsheet.md` - concise pitch, tradeoffs and Q&A.
- `docs/artifact-map.md` - artifact filenames and QA decision map.
- `docs/architecture-summary.md` - architecture and routing summary.
- `docs/project-structure.md` - codebase structure.
- `docs/docker.md` - Docker run commands.
