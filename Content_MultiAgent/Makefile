.PHONY: sync lint test app demo demo-list demo-all ci interview-check

sync:
	uv sync

lint:
	uv run ruff check .

test:
	uv run pytest

app:
	uv run streamlit run app.py

demo:
	uv run seo-demo --demo bp --mode demo

demo-list:
	uv run seo-demo --list-demos

demo-all:
	uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json

ci: lint test

interview-check: ci demo-list demo-all
