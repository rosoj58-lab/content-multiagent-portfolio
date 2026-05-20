"""Configuration tests."""

import ast
from pathlib import Path

from seo_content_pipeline.config import AppSettings, get_settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "src" / "seo_content_pipeline"


def test_default_settings_do_not_require_external_credentials(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("COPYLEAKS_EMAIL", raising=False)
    monkeypatch.delenv("COPYLEAKS_API_KEY", raising=False)

    settings = get_settings(load_env_file=False)

    assert settings.app_mode == "demo"
    assert settings.artifact_root == Path("artifacts/jobs")
    assert settings.max_revision_attempts == 2
    assert settings.uniqueness_provider == "manual"
    assert settings.openai_api_key is None
    assert settings.copyleaks_email is None
    assert settings.copyleaks_api_key is None


def test_settings_read_environment_overrides(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("APP_MODE", "local")
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path / "jobs"))
    monkeypatch.setenv("BMAD_OUTPUT_DIR", str(tmp_path / "bmad-output"))
    monkeypatch.setenv("MAX_REVISION_ATTEMPTS", "5")
    monkeypatch.setenv("UNIQUENESS_PROVIDER", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")

    settings = get_settings(load_env_file=False)

    assert settings == AppSettings(
        app_mode="local",
        artifact_root=tmp_path / "jobs",
        bmad_output_dir=tmp_path / "bmad-output",
        max_revision_attempts=5,
        uniqueness_provider="mock",
        openai_api_key="test-openai",
    )


def test_config_module_is_only_source_file_that_reads_environment() -> None:
    offenders: list[str] = []

    for path in PACKAGE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if (
                    isinstance(node.value, ast.Name)
                    and node.value.id == "os"
                    and node.attr in {"getenv", "environ"}
                ):
                    offenders.append(path.relative_to(PROJECT_ROOT).as_posix())
            elif isinstance(node, ast.ImportFrom) and node.module == "dotenv":
                offenders.append(path.relative_to(PROJECT_ROOT).as_posix())
            elif isinstance(node, ast.Import):
                if any(alias.name == "dotenv" for alias in node.names):
                    offenders.append(path.relative_to(PROJECT_ROOT).as_posix())

    assert sorted(set(offenders)) == ["src/seo_content_pipeline/config.py"]
