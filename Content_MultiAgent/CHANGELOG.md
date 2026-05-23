# Changelog

## 0.1.0 - Portfolio MVP

Initial local portfolio release of the multi-agent SEO content pipeline.

### Added

- Streamlit workflow for turning dry source notes into an inspectable SEO content package.
- Deterministic offline demo path for BP, LP and GP scenarios without OpenAI or Copyleaks credentials.
- Stage artifacts for brief, writing, article validation, editorial QA, SEO QA, uniqueness, localization, final package and final QA.
- `seo-demo` CLI with scenario listing, all-scenario runs, version output and a versioned demo summary manifest.
- `make interview-check` for a local readiness pass before interviews.
- Docker development environment with app, test and diagnostic shortcuts.
- GitHub Actions quality gate using `uv sync --frozen`, Ruff and pytest.
- Tracked example outputs for GitHub review, including a sample final package, final QA report and demo summary manifest.

### Known Limits

- The repeatable demo uses deterministic offline content rather than live model calls.
- Manual uniqueness keeps the demo reliable; real Copyleaks submission remains an optional integration boundary.
- File-based persistence is optimized for local inspection, not concurrent hosted production usage.
- Auth, database storage, queue workers, CMS publishing and hosted deployment are intentionally deferred.
