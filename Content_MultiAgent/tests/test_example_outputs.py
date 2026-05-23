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
    assert "uv run seo-demo --demo bp --mode demo" in readme
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
