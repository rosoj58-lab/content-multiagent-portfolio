"""Offline demo pipeline CLI."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArticleType
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService


@dataclass(frozen=True)
class DemoInput:
    """Stable input metadata for one offline demo scenario."""

    article_type: ArticleType
    input_path: Path
    demo_path: str
    purpose: str


DEMO_INPUTS = {
    "bp": DemoInput(
        article_type=ArticleType.BP,
        input_path=Path("examples/inputs/bp-demo.txt"),
        demo_path="happy_path",
        purpose="Use this case to show the clean end-to-end path from dry input to final package.",
    ),
    "lp": DemoInput(
        article_type=ArticleType.LP,
        input_path=Path("examples/inputs/lp-demo.txt"),
        demo_path="revision_path",
        purpose="Use this case to demonstrate revision routing for unsupported claims or commercial copy risk.",
    ),
    "gp": DemoInput(
        article_type=ArticleType.GP,
        input_path=Path("examples/inputs/gp-demo.txt"),
        demo_path="human_review_path",
        purpose="Use this case to explain human-review handling for sensitive link-placement workflows.",
    ),
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
    parser.add_argument(
        "--list-demos",
        action="store_true",
        help="Print the stable demo catalog and exit without generating artifacts.",
    )
    args = parser.parse_args(argv)

    if args.list_demos:
        _print_demo_catalog()
        return 0

    demo_names = list(DEMO_INPUTS) if args.demo == "all" else [args.demo]
    runs: list[dict[str, str]] = []
    for index, demo_name in enumerate(demo_names):
        if index > 0:
            print()
        runs.append(_run_demo(demo_name, mode=args.mode, artifact_root=args.artifact_root))

    if args.summary_file is not None:
        summary = {
            "version": 1,
            "requested_demo": args.demo,
            "mode": args.mode,
            "artifact_root": str(args.artifact_root),
            "run_count": len(runs),
            "runs": runs,
        }
        args.summary_file.parent.mkdir(parents=True, exist_ok=True)
        args.summary_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"summary_file={args.summary_file}")

    return 0


def _run_demo(demo_name: str, *, mode: str, artifact_root: Path) -> dict[str, str]:
    demo_input = DEMO_INPUTS[demo_name]
    article_type = demo_input.article_type
    input_path = demo_input.input_path
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
        "article_type": article_type.value,
        "input_file": input_path.as_posix(),
        "demo_path": demo_input.demo_path,
        "purpose": demo_input.purpose,
        "job_id": result.job_id,
        "status": result.status.value,
        "artifact_dir": str(store.job_dir(result.job_id)),
        "final_package": result.final_package_path,
        "final_qa_report": result.final_qa_report_path,
    }


def _print_demo_catalog() -> None:
    for demo_name, demo_input in DEMO_INPUTS.items():
        print(f"demo={demo_name}")
        print(f"article_type={demo_input.article_type.value}")
        print(f"input_file={demo_input.input_path.as_posix()}")
        print(f"demo_path={demo_input.demo_path}")
        print(f"purpose={demo_input.purpose}")
        print()


if __name__ == "__main__":
    raise SystemExit(main())
