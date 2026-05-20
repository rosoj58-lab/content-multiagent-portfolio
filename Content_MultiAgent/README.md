# SEO Content Pipeline

Local portfolio application for a multi-agent SEO content workflow.

## Development

Run from this directory when `uv` is installed locally:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run streamlit run app.py
```

Run from the Git/Compose root when using Docker:

```bash
docker compose build
docker compose run --rm app uv run pytest
docker compose up
```
