# Docker Development Environment

This project uses Docker Desktop to keep the local Python runtime isolated from other portfolio projects.

## Installed Tooling

- Docker Desktop for Mac is installed in `~/Applications/Docker.app`.
- Docker CLI symlinks are available through `~/.local/bin`.
- Compose is available as `docker compose`.

## Run The Project

From the repository root:

```bash
docker compose up --build
```

The Streamlit app will be available at:

```text
http://localhost:8501
```

The current image is intentionally ready before the app scaffold exists. Until `app.py` or `src/seo_content_pipeline/app.py` is added, the container starts and waits with a setup message.

## Environment Variables

Create `Content_MultiAgent/.env` locally when API keys are needed. This file is ignored by Git.

Example future values:

```bash
OPENAI_API_KEY=
COPYLEAKS_EMAIL=
COPYLEAKS_API_KEY=
```

## Useful Commands

```bash
docker compose up --build
docker compose down
docker compose logs -f app
docker compose run --rm app sh
```

## Notes

- Generated job artifacts stay outside the image and are mounted through `./bmad-output`.
- Python dependencies should be pinned through `pyproject.toml` and `uv.lock` once the application scaffold is created.
