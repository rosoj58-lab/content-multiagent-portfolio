# Demo Setup

This project uses stable local inputs so the portfolio demo can be repeated without live research, hosted infrastructure or external plagiarism credentials.

## Local Run

Use the project Python environment and start Streamlit:

```bash
uv run streamlit run app.py
```

The app opens a local form with Dry input, Article type and Mode. Keep Mode set to `demo` for shorter generated articles. The same pipeline can be inspected through artifacts under `artifacts/jobs/<job_id>/`.

For a terminal-only smoke demo, run:

```bash
uv run seo-demo --demo bp --mode demo
```

To list the stable scenarios and their purpose:

```bash
uv run seo-demo --list-demos
```

To prepare all stable demo paths before an interview, run:

```bash
uv run seo-demo --demo all --mode demo
```

To create one JSON manifest with all generated job folders, run:

```bash
uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json
```

To run the quality gate and prepare all terminal demo artifacts together:

```bash
make interview-check
```

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
5. Click `Run demo scenario` to execute the selected outcome.
6. For LP, click `Apply recommended revision` to demonstrate correction and approval.
7. Open `artifacts/jobs/<job_id>/` to show the persisted source of truth.

The BP case is the main happy path and generates the approved final package. The LP case
produces an English draft with an unsupported performance claim, then stops at
`editorial_qa.json` with `needs_revision` guidance. After explicit correction,
the same LP job writes `revision_history.json`, replaces the working draft and
reaches an approved final package. The GP case includes a contextual project link,
then stops at `editorial_qa.json` with `needs_human_review` because publication fit
needs editorial judgment.
