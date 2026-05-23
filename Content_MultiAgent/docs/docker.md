# Docker Development Environment

This project uses Docker Desktop to keep the Python runtime isolated from other local portfolio projects.

## Run The App

Run from the Git/Compose root, one directory above `Content_MultiAgent`:

```bash
docker compose up --build
```

The Streamlit app will be available at:

```text
http://localhost:8501
```

The compose file mounts `Content_MultiAgent` into `/app`, so source edits are visible inside the container. Generated job artifacts are written to `Content_MultiAgent/artifacts/jobs/`.

## Test In Docker

```bash
docker compose run --rm app uv run ruff check .
docker compose run --rm app uv run pytest
```

## Environment Variables

Create `Content_MultiAgent/.env` locally when API keys are needed. This file is ignored by Git. The repeatable offline demo does not require these values.

```bash
APP_MODE=demo
ARTIFACT_ROOT=artifacts/jobs
BMAD_OUTPUT_DIR=/bmad-output
MAX_REVISION_ATTEMPTS=2
UNIQUENESS_PROVIDER=manual
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

From `Content_MultiAgent/`, the same common Docker actions are available as
shortcuts:

```bash
make docker-build
make docker-test
make docker-up
make docker-down
make docker-logs
make docker-shell
```

## Demo Flow

1. Open `http://localhost:8501`.
2. Paste one of the stable inputs from `examples/inputs/`.
3. Create a job.
4. Click `Run full demo pipeline`.
5. Inspect the final package and QA report under `artifacts/jobs/<job_id>/`.
