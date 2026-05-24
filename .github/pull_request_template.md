## Summary

- Briefly describe the change and why it matters.

## Quality Gate

- [ ] `uv run ruff check .`
- [ ] `uv run pytest`
- [ ] `make interview-check` when demo behavior, artifacts or documentation changed

## Demo Proof

- [ ] Streamlit demo path checked when UI behavior changed
- [ ] `uv run seo-demo --demo bp --mode demo` checked when pipeline behavior changed
- [ ] Generated artifacts reviewed under `artifacts/jobs/<job_id>/`

## Docker

- [ ] `docker compose build` when dependencies, Dockerfile or Compose config changed
- [ ] `docker compose run --rm app uv run pytest` when Docker behavior changed

## Security And Privacy

- [ ] No `.env`, API keys, provider tokens or generated private content committed
- [ ] `SECURITY.md` reviewed when provider, artifact or credential handling changed

## Notes

- Add screenshots, artifact paths or follow-up context when useful.
