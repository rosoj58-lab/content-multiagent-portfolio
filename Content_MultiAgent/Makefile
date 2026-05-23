.PHONY: help sync lint test app demo demo-list demo-all ci interview-check

help:
	@printf '%s\n' \
		'Available commands:' \
		'  make sync             Install project dependencies with uv' \
		'  make lint             Run Ruff' \
		'  make test             Run pytest' \
		'  make app              Start Streamlit locally' \
		'  make demo             Run the BP happy-path CLI demo' \
		'  make demo-list        List stable demo scenarios' \
		'  make demo-all         Generate BP, LP and GP demo artifacts' \
		'  make ci               Run lint and tests' \
		'  make interview-check  Run CI checks and prepare demo artifacts'

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
