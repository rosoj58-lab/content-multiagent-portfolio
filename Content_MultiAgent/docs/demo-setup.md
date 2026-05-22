# Demo Setup

This project uses stable local inputs so the portfolio demo can be repeated without relying on external research or live APIs.

## Demo Inputs

| Path | Article type | Demo path | Purpose |
| --- | --- | --- | --- |
| `examples/inputs/bp-demo.txt` | `BP` | happy path | Informational blog post demo for the clean end-to-end workflow. |
| `examples/inputs/lp-demo.txt` | `LP` | revision path | Commercial landing page demo for revision routing when unsupported claims or risky conversion copy appear. |
| `examples/inputs/gp-demo.txt` | `GP` | human review path | Guest post demo for link-placement sensitivity and human-review explanation. |
| `examples/inputs/sample-keywords.json` | `BP`, `LP`, `GP` | all paths | Stable keyword metadata for repeatable brief and demo setup notes. |

## How to Use

1. Start the Streamlit app in demo mode.
2. Open one of the files from `examples/inputs/`.
3. Paste the full text into the Dry input field.
4. Select the matching article type: `BP`, `LP`, or `GP`.
5. Keep mode set to `demo` for shorter article generation.
6. Run the pipeline and inspect the generated artifacts under the configured artifact root.

The BP case is the main happy path. The LP case is meant to explain revision routing. The GP case is meant to explain why human review remains valuable for sensitive guest-post link placement.
