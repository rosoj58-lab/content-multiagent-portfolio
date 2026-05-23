.PHONY: help version sync lint test app demo demo-list demo-all ci interview-check docker-build docker-test docker-up docker-down docker-logs docker-shell
.DEFAULT_GOAL := help

help:
	@printf '%s\n' \
		'Available commands:' \
		'  make version          Print the seo-demo CLI version' \
		'  make sync             Install project dependencies with uv' \
		'  make lint             Run Ruff' \
		'  make test             Run pytest' \
		'  make app              Start Streamlit locally' \
		'  make demo             Run the BP happy-path CLI demo' \
		'  make demo-list        List stable demo scenarios' \
		'  make demo-all         Generate BP, LP and GP demo artifacts' \
		'  make ci               Run lint and tests' \
		'  make interview-check  Run CI checks and prepare demo artifacts' \
		'  make docker-build     Build the Docker image from compose root' \
		'  make docker-test      Run lint and tests in Docker' \
		'  make docker-up        Start the Dockerized Streamlit app' \
		'  make docker-down      Stop Docker services' \
		'  make docker-logs      Follow Docker app logs' \
		'  make docker-shell     Open a shell in the Docker app service'

sync:
	uv sync

version:
	uv run seo-demo --version

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

docker-build:
	docker compose -f ../compose.yaml build

docker-test:
	docker compose -f ../compose.yaml run --rm app uv run ruff check .
	docker compose -f ../compose.yaml run --rm app uv run pytest

docker-up:
	docker compose -f ../compose.yaml up

docker-down:
	docker compose -f ../compose.yaml down

docker-logs:
	docker compose -f ../compose.yaml logs -f app

docker-shell:
	docker compose -f ../compose.yaml run --rm app sh
