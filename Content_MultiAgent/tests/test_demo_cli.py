"""Offline demo CLI tests."""

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
