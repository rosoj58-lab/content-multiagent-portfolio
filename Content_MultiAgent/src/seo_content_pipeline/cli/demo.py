"""Offline demo pipeline CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArticleType
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService


DEMO_INPUTS = {
    "bp": (ArticleType.BP, Path("examples/inputs/bp-demo.txt")),
    "lp": (ArticleType.LP, Path("examples/inputs/lp-demo.txt")),
    "gp": (ArticleType.GP, Path("examples/inputs/gp-demo.txt")),
}
DEMO_CHOICES = [*DEMO_INPUTS, "all"]


def main(argv: Sequence[str] | None = None) -> int:
    """Run a deterministic offline demo job and print the artifact locations."""
    parser = argparse.ArgumentParser(description="Run the offline SEO content pipeline demo.")
    parser.add_argument(
        "--demo",
        choices=DEMO_CHOICES,
        default="bp",
        help="Stable demo input to run, or all to run every demo input.",
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "full"],
        default="demo",
        help="Article generation length mode.",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("artifacts/jobs"),
        help="Directory where job artifacts should be written.",
    )
    parser.add_argument(
        "--summary-file",
        type=Path,
        help="Optional JSON file where a manifest of generated demo runs should be written.",
    )
    args = parser.parse_args(argv)

    demo_names = list(DEMO_INPUTS) if args.demo == "all" else [args.demo]
    runs: list[dict[str, str]] = []
    for index, demo_name in enumerate(demo_names):
        if index > 0:
            print()
        runs.append(_run_demo(demo_name, mode=args.mode, artifact_root=args.artifact_root))

    if args.summary_file is not None:
        summary = {
            "requested_demo": args.demo,
            "mode": args.mode,
            "artifact_root": str(args.artifact_root),
            "runs": runs,
        }
        args.summary_file.parent.mkdir(parents=True, exist_ok=True)
        args.summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"summary_file={args.summary_file}")

    return 0


def _run_demo(demo_name: str, *, mode: str, artifact_root: Path) -> dict[str, str]:
    article_type, input_path = DEMO_INPUTS[demo_name]
    dry_input = input_path.read_text(encoding="utf-8")
    settings = AppSettings(artifact_root=artifact_root)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(dry_input, article_type)
    result = DemoPipelineService(settings=settings, artifact_store=store).run_full_demo(
        job.metadata.job_id,
        mode=mode,
    )

    print(f"demo={demo_name}")
    print(f"job_id={result.job_id}")
    print(f"status={result.status.value}")
    print(f"artifact_dir={store.job_dir(result.job_id)}")
    print(f"final_package={result.final_package_path}")
    print(f"final_qa_report={result.final_qa_report_path}")
    return {
        "demo": demo_name,
        "job_id": result.job_id,
        "status": result.status.value,
        "artifact_dir": str(store.job_dir(result.job_id)),
        "final_package": result.final_package_path,
        "final_qa_report": result.final_qa_report_path,
    }


if __name__ == "__main__":
    raise SystemExit(main())
