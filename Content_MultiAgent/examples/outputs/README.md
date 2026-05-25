# Example Outputs

This folder contains stable, human-readable examples of the final artifacts produced by the offline BP happy path.

These files are intentionally not copied from a timestamped job folder. Runtime artifacts are generated under `artifacts/jobs/<job_id>/` and ignored by Git. The examples here show the expected output shape for GitHub review and interview discussion.

## Files

- `sample-final-package.md` - abbreviated final Markdown package with traceability, article content, localization summaries and QA sections.
- `sample-final-qa-report.json` - final QA readiness report showing approved status, completed stages, uniqueness result and localization status.
- `sample-demo-summary.json` - versioned demo index showing BP approval, LP revision and GP human-review outcome paths.

## Reproduce Locally

```bash
uv run seo-demo --demo bp --mode demo
```

Then open the printed `artifact_dir` and compare its `final_package.md` and `final_qa_report.json` to the examples in this folder.

To reproduce the demo summary shape:

```bash
uv run seo-demo --demo all --mode demo --summary-file artifacts/demo/demo-summary.json
```

In that manifest BP points to its final QA report; LP and GP point to their
editorial decision artifacts because those scenarios intentionally stop before
final package assembly.
