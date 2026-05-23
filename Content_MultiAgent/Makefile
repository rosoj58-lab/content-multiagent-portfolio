.PHONY: sync lint test app demo demo-all ci

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

demo-all:
	uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json

ci: lint test
