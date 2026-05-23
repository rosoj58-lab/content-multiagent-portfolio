"""Python version contract checks for local, package and CI tooling."""

from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PYTHON = "3.12"


def test_python_version_is_consistent_across_tooling() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    workflow = (REPO_ROOT / ".github" / "workflows" / "content-multiagent-ci.yml").read_text(
        encoding="utf-8"
    )
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert (PROJECT_ROOT / ".python-version").read_text(encoding="utf-8").strip() == EXPECTED_PYTHON
    assert pyproject["project"]["requires-python"] == f">={EXPECTED_PYTHON}"
    assert pyproject["tool"]["ruff"]["target-version"] == "py312"
    assert f'python-version: "{EXPECTED_PYTHON}"' in workflow
    assert f"Python {EXPECTED_PYTHON}" in readme
