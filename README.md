# Content Multi-Agent Portfolio Project

This repository contains a local portfolio application for a multi-agent SEO content workflow.

## Main Project

Open the project here:

- `Content_MultiAgent/README.md` - full project overview, demo flow and development commands.
- `Content_MultiAgent/docs/interview-cheatsheet.md` - short pitch, architecture talking points, tradeoffs and likely interview questions.
- `Content_MultiAgent/examples/outputs/` - stable sample final package and final QA report.

## Quick Start

```bash
cd Content_MultiAgent
uv sync
uv run streamlit run app.py
```

Then open `http://localhost:8501`, create a job from `examples/inputs/bp-demo.txt`, and click `Run full demo pipeline`.

Terminal smoke demo:

```bash
cd Content_MultiAgent
uv run seo-demo --demo bp --mode demo
```

## Quality Gate

```bash
cd Content_MultiAgent
uv run ruff check .
uv run pytest
```

GitHub Actions runs the same checks for changes under `Content_MultiAgent/`.
