.PHONY: sync lint test app demo ci

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

ci: lint test
