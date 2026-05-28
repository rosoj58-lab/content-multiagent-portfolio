# Changelog

## 0.1.0 - Portfolio MVP

Initial local portfolio release of the multi-agent SEO content pipeline.

### Added

- Streamlit workflow for turning dry source notes into an inspectable SEO content package.
- Deterministic offline demo path for BP, LP and GP scenarios without OpenAI or Copyleaks credentials.
- Stage artifacts for brief, writing, article validation, editorial QA, SEO QA, uniqueness, localization, final package and final QA.
- `seo-demo` CLI with scenario listing, all-scenario runs, version output and a versioned demo summary manifest.
- `make interview-check` for a local readiness pass before interviews.
- Distinct deterministic demo outcomes: BP approval, LP editorial revision for an unsupported claim and GP human-review escalation for contextual link placement.
- Decision QA Scorecard in Streamlit for approval evidence, revision guidance and human-review actions.
- LP correction-to-approval action with persisted `revision_history.json` evidence.
- Read-only LP version comparison with a persisted `english_original_rejected.md` snapshot.
- Targeted operator-authored LP correction with pre-mutation claim-pattern validation.
- Optional OpenAI Responses API action for generating one live SEO brief before deterministic QA and manual approval.
- Docker development environment with app, test and diagnostic shortcuts.
- GitHub Actions quality gate using `uv sync --frozen`, Ruff and pytest.
- Tracked example outputs for GitHub review, including a sample final package, final QA report and demo summary manifest.

### Known Limits

- The repeatable full demo uses deterministic offline content; the optional live OpenAI path currently stops after SEO brief QA.
- Manual uniqueness keeps the demo reliable; real Copyleaks submission remains an optional integration boundary.
- File-based persistence is optimized for local inspection, not concurrent hosted production usage.
- Auth, database storage, queue workers, CMS publishing and hosted deployment are intentionally deferred.
