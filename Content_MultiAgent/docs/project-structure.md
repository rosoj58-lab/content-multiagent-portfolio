# Project Structure

This structure is optimized for an inspectable local portfolio project. The important design choice is separation: UI renders state, services perform workflow actions, models define data contracts, and artifacts persist the output of each stage.

```text
app.py
src/seo_content_pipeline/
  cli/
  config.py
  models/
  services/
  validators/
  providers/
  prompts/
  graph/
  ui/
tests/
docs/
examples/inputs/
examples/outputs/
artifacts/jobs/
```

## Key Directories

`cli/` contains command-line entrypoints such as `seo-demo`, which runs the offline demo pipeline without opening Streamlit.

`models/` contains the public contracts: `PipelineState`, `JobMetadata`, `ArtifactKey`, `QAReport`, `UniquenessResult`, `FinalQAReport`, `WorkflowStage` and `WorkflowStatus`.

`services/` contains orchestration logic. `JobService` creates job shells, `ArtifactStore` persists files, QA services write reports, localization writes language artifacts, exporters assemble final packages, and `FinalQAService` decides approved vs needs revision.

`ui/` contains Streamlit-facing presentation helpers: progress timeline, artifact panel, controlled error presenter, empty states and QA render helpers. This keeps `app.py` thin and protects architecture boundaries.

`examples/inputs/` contains the reproducible BP, LP and GP demo inputs. These support UX-DR6: happy path, revision path and human-review path.

`artifacts/jobs/` is where demo runs are inspected. During an interview, open BP
to show `state.json`, QA reports, localizations, final package files and
`final_qa_report.json`; open LP and GP to show their routed
`editorial_qa.json` decision artifacts.
For the LP correction walkthrough, open `revision_history.json` beside the
approved final package and `english_original_rejected.md` to show that both the
failed QA evidence and rejected content were preserved for comparison.

## Requirements Trace

FR17 is visible in workflow status models, status history and UI timeline rendering. FR18 is visible in revision routing fields, QA report routing targets and final QA guidance. The project structure keeps those decisions inspectable rather than hidden in a single generated text blob.
