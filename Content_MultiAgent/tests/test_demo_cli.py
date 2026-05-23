"""Offline demo CLI tests."""

import json
from pathlib import Path

from seo_content_pipeline.cli.demo import main


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


def test_demo_cli_supports_full_mode(tmp_path, capsys) -> None:
    exit_code = main(["--demo", "lp", "--mode", "full", "--artifact-root", str(tmp_path)])

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
    assert output.count("status=approved") == 3
    assert len(job_ids) == 3
    assert len(set(job_ids)) == 3
    for job_id in job_ids:
        assert (tmp_path / job_id / "final_package.md").exists()
        assert (tmp_path / job_id / "final_qa_report.json").exists()


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
    assert summary["requested_demo"] == "all"
    assert summary["mode"] == "demo"
    assert summary["artifact_root"] == str(artifact_root)
    assert [run["demo"] for run in summary["runs"]] == ["bp", "lp", "gp"]
    assert [run["article_type"] for run in summary["runs"]] == ["BP", "LP", "GP"]
    assert [run["input_file"] for run in summary["runs"]] == [
        "examples/inputs/bp-demo.txt",
        "examples/inputs/lp-demo.txt",
        "examples/inputs/gp-demo.txt",
    ]
    assert {run["status"] for run in summary["runs"]} == {"approved"}
    for run in summary["runs"]:
        assert Path(run["artifact_dir"]).exists()
        assert Path(run["final_package"]).exists()
        assert Path(run["final_qa_report"]).exists()
