"""Offline demo CLI tests."""

import json
from pathlib import Path
import tomllib

import pytest

from seo_content_pipeline.cli.demo import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_demo_cli_creates_approved_job(tmp_path, capsys) -> None:
    exit_code = main(["--demo", "bp", "--mode", "demo", "--artifact-root", str(tmp_path)])

    output = capsys.readouterr().out
    job_id = next(line.removeprefix("job_id=") for line in output.splitlines() if line.startswith("job_id="))
    job_dir = tmp_path / job_id

    assert exit_code == 0
    assert "status=approved" in output
    assert f"artifact_dir={job_dir}" in output
    assert (job_dir / "final_package.md").exists()
    assert (job_dir / "final_qa_report.json").exists()
    assert (job_dir / "run_summary.json").exists()
    assert f"run_summary={job_dir / 'run_summary.json'}" in output


def test_demo_cli_supports_full_mode(tmp_path, capsys) -> None:
    exit_code = main(["--demo", "bp", "--mode", "full", "--artifact-root", str(tmp_path)])

    output = capsys.readouterr().out
    package_line = next(line for line in output.splitlines() if line.startswith("final_package="))
    package_path = Path(package_line.removeprefix("final_package="))

    assert exit_code == 0
    assert "status=approved" in output
    assert package_path.exists()


def test_demo_cli_can_run_all_stable_inputs(tmp_path, capsys) -> None:
    exit_code = main(["--demo", "all", "--mode", "demo", "--artifact-root", str(tmp_path)])

    output = capsys.readouterr().out
    job_ids = [
        line.removeprefix("job_id=")
        for line in output.splitlines()
        if line.startswith("job_id=")
    ]

    assert exit_code == 0
    assert "demo=bp" in output
    assert "demo=gp" in output
    assert "demo=lp" in output
    assert output.count("status=approved") == 1
    assert "status=needs_revision" in output
    assert "status=needs_human_review" in output
    assert len(job_ids) == 3
    assert len(set(job_ids)) == 3
    assert (tmp_path / job_ids[0] / "final_package.md").exists()
    assert (tmp_path / job_ids[0] / "final_qa_report.json").exists()
    for job_id in job_ids[1:]:
        assert (tmp_path / job_id / "editorial_qa.json").exists()
        assert not (tmp_path / job_id / "final_package.md").exists()


def test_demo_cli_can_write_summary_manifest(tmp_path, capsys) -> None:
    summary_file = tmp_path / "demo-summary.json"
    artifact_root = tmp_path / "jobs"

    exit_code = main(
        [
            "--demo",
            "all",
            "--mode",
            "demo",
            "--artifact-root",
            str(artifact_root),
            "--summary-file",
            str(summary_file),
        ]
    )

    output = capsys.readouterr().out
    summary = json.loads(summary_file.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert f"summary_file={summary_file}" in output
    assert summary["version"] == 2
    assert summary["requested_demo"] == "all"
    assert summary["mode"] == "demo"
    assert summary["artifact_root"] == str(artifact_root)
    assert summary["run_count"] == 3
    assert [run["demo"] for run in summary["runs"]] == ["bp", "lp", "gp"]
    assert [run["article_type"] for run in summary["runs"]] == ["BP", "LP", "GP"]
    assert [run["input_file"] for run in summary["runs"]] == [
        "examples/inputs/bp-demo.txt",
        "examples/inputs/lp-demo.txt",
        "examples/inputs/gp-demo.txt",
    ]
    assert [run["demo_path"] for run in summary["runs"]] == [
        "happy_path",
        "revision_path",
        "human_review_path",
    ]
    assert "clean end-to-end path" in summary["runs"][0]["purpose"]
    assert "revision routing" in summary["runs"][1]["purpose"]
    assert "human-review handling" in summary["runs"][2]["purpose"]
    assert [run["status"] for run in summary["runs"]] == [
        "approved",
        "needs_revision",
        "needs_human_review",
    ]
    for run in summary["runs"]:
        assert Path(run["artifact_dir"]).exists()
        assert Path(run["decision_artifact"]).exists()
        assert Path(run["run_summary"]).exists()
    assert Path(summary["runs"][0]["final_package"]).exists()
    assert Path(summary["runs"][0]["final_qa_report"]).exists()
    assert summary["runs"][0]["run_summary"].endswith("run_summary.json")
    for run in summary["runs"][1:]:
        assert run["final_package"] is None
        assert run["final_qa_report"] is None
        assert run["run_summary"].endswith("run_summary.json")


def test_demo_cli_can_list_stable_demo_catalog(tmp_path, capsys) -> None:
    exit_code = main(["--list-demos", "--artifact-root", str(tmp_path)])

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "demo=bp" in output
    assert "article_type=BP" in output
    assert "input_file=examples/inputs/bp-demo.txt" in output
    assert "demo_path=happy_path" in output
    assert "demo=lp" in output
    assert "demo_path=revision_path" in output
    assert "demo=gp" in output
    assert "demo_path=human_review_path" in output
    assert list(tmp_path.iterdir()) == []


def test_demo_cli_help_documents_public_options(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    output = capsys.readouterr().out

    assert exc_info.value.code == 0
    assert "Run the offline SEO content pipeline demo." in output
    assert "--version" in output
    assert "--demo {bp,lp,gp,all}" in output
    assert "--mode {demo,full}" in output
    assert "--artifact-root" in output
    assert "--summary-file" in output
    assert "--list-demos" in output


def test_demo_cli_version_matches_project_metadata(capsys) -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    output = capsys.readouterr().out

    assert exc_info.value.code == 0
    assert output.strip() == f"seo-demo {pyproject['project']['version']}"


def test_demo_cli_rejects_unknown_demo_without_artifacts(tmp_path, capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--demo", "unknown", "--artifact-root", str(tmp_path)])

    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "invalid choice: 'unknown'" in captured.err
    assert "choose from bp, lp, gp, all" in captured.err
    assert list(tmp_path.iterdir()) == []
