"""Tracked example output tests."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "examples" / "outputs"


def test_example_outputs_are_not_placeholders() -> None:
    readme = (OUTPUTS_DIR / "README.md").read_text(encoding="utf-8")
    package = (OUTPUTS_DIR / "sample-final-package.md").read_text(encoding="utf-8")

    assert "Placeholder" not in readme
    assert "sample-final-package.md" in readme
    assert "sample-demo-summary.json" in readme
    assert "uv run seo-demo --demo bp --mode demo" in readme
    assert "uv run seo-demo --demo all --mode demo --summary-file" in readme
    assert "Final Content Package" in package
    assert "multi-agent SEO content pipeline" in package
    assert "Status: `approved`" in package


def test_sample_final_qa_report_matches_approved_shape() -> None:
    report = json.loads((OUTPUTS_DIR / "sample-final-qa-report.json").read_text(encoding="utf-8"))

    assert report["status"] == "approved"
    assert report["failed_checks"] == []
    assert report["uniqueness_result"]["score"] == 94.0
    assert report["uniqueness_result"]["passed"] is True
    assert report["localization_status"]["es"]["present"] is True
    assert report["localization_status"]["it"]["geo"] == "it-IT"
    assert "final_qa" in report["completed_stages"]


def test_sample_demo_summary_matches_versioned_manifest_shape() -> None:
    summary = json.loads((OUTPUTS_DIR / "sample-demo-summary.json").read_text(encoding="utf-8"))

    assert summary["version"] == 1
    assert summary["requested_demo"] == "all"
    assert summary["mode"] == "demo"
    assert summary["run_count"] == 3
    assert [run["demo"] for run in summary["runs"]] == ["bp", "lp", "gp"]
    assert [run["article_type"] for run in summary["runs"]] == ["BP", "LP", "GP"]
    assert [run["demo_path"] for run in summary["runs"]] == [
        "happy_path",
        "revision_path",
        "human_review_path",
    ]
    for run in summary["runs"]:
        assert run["status"] == "approved"
        assert run["input_file"].startswith("examples/inputs/")
        assert run["artifact_dir"].startswith("artifacts/jobs/")
        assert run["final_package"].endswith("final_package.md")
        assert run["final_qa_report"].endswith("final_qa_report.json")
