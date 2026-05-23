"""Offline demo pipeline CLI."""

from __future__ import annotations

import argparse
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run a deterministic offline demo job and print the artifact locations."""
    parser = argparse.ArgumentParser(description="Run the offline SEO content pipeline demo.")
    parser.add_argument(
        "--demo",
        choices=sorted(DEMO_INPUTS),
        default="bp",
        help="Stable demo input to run.",
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
    args = parser.parse_args(argv)

    article_type, input_path = DEMO_INPUTS[args.demo]
    dry_input = input_path.read_text(encoding="utf-8")
    settings = AppSettings(artifact_root=args.artifact_root)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(dry_input, article_type)
    result = DemoPipelineService(settings=settings, artifact_store=store).run_full_demo(
        job.metadata.job_id,
        mode=args.mode,
    )

    print(f"job_id={result.job_id}")
    print(f"status={result.status.value}")
    print(f"artifact_dir={store.job_dir(result.job_id)}")
    print(f"final_package={result.final_package_path}")
    print(f"final_qa_report={result.final_qa_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
