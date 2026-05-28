"""Application settings.

This is the only source module allowed to read environment variables.
"""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field


AppMode = Literal["demo", "local", "production"]
UniquenessProviderName = Literal["manual", "mock", "copyleaks"]


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return value


class AppSettings(BaseModel):
    """Typed application settings used by services and UI."""

    app_mode: AppMode = "demo"
    artifact_root: Path = Path("artifacts/jobs")
    bmad_output_dir: Path = Path("/bmad-output")
    max_revision_attempts: int = Field(default=2, ge=0)
    uniqueness_provider: UniquenessProviderName = "manual"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-mini"
    copyleaks_email: str | None = None
    copyleaks_api_key: str | None = None


def get_settings(*, load_env_file: bool = True) -> AppSettings:
    """Load settings from environment variables and optional local .env."""
    if load_env_file:
        load_dotenv()

    return AppSettings(
        app_mode=os.getenv("APP_MODE", "demo"),
        artifact_root=Path(os.getenv("ARTIFACT_ROOT", "artifacts/jobs")),
        bmad_output_dir=Path(os.getenv("BMAD_OUTPUT_DIR", "/bmad-output")),
        max_revision_attempts=os.getenv("MAX_REVISION_ATTEMPTS", "2"),
        uniqueness_provider=os.getenv("UNIQUENESS_PROVIDER", "manual"),
        openai_api_key=_optional_env("OPENAI_API_KEY"),
        openai_model=_optional_env("OPENAI_MODEL") or "gpt-5.4-mini",
        copyleaks_email=_optional_env("COPYLEAKS_EMAIL"),
        copyleaks_api_key=_optional_env("COPYLEAKS_API_KEY"),
    )
