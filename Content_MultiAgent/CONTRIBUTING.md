# Contributing

This is a portfolio project, so every change should keep the demo easy to run,
inspect and explain in an interview.

## Local Setup

Run commands from `Content_MultiAgent/` unless noted otherwise:

```bash
uv sync
uv run ruff check .
uv run pytest
uv run streamlit run app.py
```

Open `http://localhost:8501` and use `examples/inputs/bp-demo.txt` for the
fastest local smoke test.

## Demo Checks

Before treating a change as interview-ready, run:

```bash
make interview-check
```

This runs the local quality gate, lists the stable demo inputs and regenerates
`artifacts/demo/demo-summary.json`.

For a narrower terminal smoke test:

```bash
uv run seo-demo --demo bp --mode demo
```

## Docker Checks

From the Git/Compose root:

```bash
docker compose build
docker compose run --rm app uv run pytest
docker compose up
```

Use Docker when you want an isolated project environment or want to validate the
same setup on another machine.

## Change Rules

- Keep generated runtime files out of commits: `artifacts/jobs/*` and
  `artifacts/demo/*` are local demo outputs.
- Follow `SECURITY.md` for `.env`, API keys, provider credentials and generated
  content before sharing artifacts.
- Update tests when changing commands, filenames, artifacts or README promises.
- Keep the offline demo path working without OpenAI or Copyleaks credentials.
- Prefer small commits that can be explained as one portfolio improvement.

## Release Notes

When a visible capability or limitation changes, update `CHANGELOG.md` before
calling the project interview-ready.
