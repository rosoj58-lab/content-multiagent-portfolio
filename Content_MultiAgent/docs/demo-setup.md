# Demo Setup

This project uses stable local inputs so the portfolio demo can be repeated without live research, hosted infrastructure or external plagiarism credentials.

## Local Run

Use the project Python environment and start Streamlit:

```bash
uv run streamlit run app.py
```

The app opens a local form with Dry input, Article type and Mode. Keep Mode set to `demo` for shorter generated articles. The same pipeline can be inspected through artifacts under `artifacts/jobs/<job_id>/`.

## Demo Inputs

| Path | Article type | Demo path | Purpose |
| --- | --- | --- | --- |
| `examples/inputs/bp-demo.txt` | `BP` | happy path | Informational blog post demo for the clean end-to-end workflow. |
| `examples/inputs/lp-demo.txt` | `LP` | revision path | Commercial landing page demo for revision routing when unsupported claims or risky conversion copy appear. |
| `examples/inputs/gp-demo.txt` | `GP` | human review path | Guest post demo for link-placement sensitivity and human-review explanation. |
| `examples/inputs/sample-keywords.json` | `BP`, `LP`, `GP` | all paths | Stable keyword metadata for repeatable brief and demo setup notes. |

## How to Use

1. Open one of the files from `examples/inputs/`.
2. Paste the full text into the Dry input field.
3. Select the matching article type: `BP`, `LP`, or `GP`.
4. Create the job and inspect the progress timeline and artifact panel.
5. Click `Run full demo pipeline` to generate the offline brief, article, QA reports, uniqueness result, localizations, final package and final QA report.
6. Open `artifacts/jobs/<job_id>/` to show the persisted source of truth.

The BP case is the main happy path. The LP case is meant to explain revision path behavior. The GP case is the human review path and is meant to explain why human review remains valuable for sensitive guest-post link placement.
