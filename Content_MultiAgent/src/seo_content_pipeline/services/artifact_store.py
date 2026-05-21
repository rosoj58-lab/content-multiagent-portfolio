"""File-based artifact persistence."""

import json
import os
import tempfile
from pathlib import Path, PurePath
from typing import Any

from pydantic import BaseModel

from seo_content_pipeline.models import ARTIFACT_REGISTRY, ArtifactKey


class ArtifactStore:
    """Registry-backed storage for job artifacts."""

    def __init__(self, artifact_root: str | Path) -> None:
        self.artifact_root = Path(artifact_root)

    def job_dir(self, job_id: str) -> Path:
        """Return the directory for a job's artifacts."""
        self._validate_job_id(job_id)
        return self.artifact_root / job_id

    def artifact_path(self, job_id: str, key: ArtifactKey) -> Path:
        """Return the registry-derived path for an artifact."""
        return self.job_dir(job_id) / ARTIFACT_REGISTRY[key].filename

    def write_json(self, job_id: str, key: ArtifactKey, payload: BaseModel | dict[str, Any]) -> Path:
        """Write a JSON artifact atomically and return its path."""
        spec = ARTIFACT_REGISTRY[key]
        if spec.content_type != "application/json":
            raise ValueError(f"Artifact {key.value!r} is not a JSON artifact.")

        target = self.artifact_path(job_id, key)
        target.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_jsonable(payload)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                json.dump(data, tmp_file, ensure_ascii=False, indent=2)
                tmp_file.write("\n")
            Path(tmp_name).replace(target)
        except Exception:
            Path(tmp_name).unlink(missing_ok=True)
            raise

        return target

    def read_json(self, job_id: str, key: ArtifactKey) -> dict[str, Any]:
        """Read a JSON artifact as a mapping."""
        spec = ARTIFACT_REGISTRY[key]
        if spec.content_type != "application/json":
            raise ValueError(f"Artifact {key.value!r} is not a JSON artifact.")

        with self.artifact_path(job_id, key).open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError(f"Artifact {key.value!r} did not contain a JSON object.")
        return data

    def write_text(self, job_id: str, key: ArtifactKey, payload: str) -> Path:
        """Write a text artifact atomically and return its path."""
        spec = ARTIFACT_REGISTRY[key]
        if spec.content_type != "text/markdown":
            raise ValueError(f"Artifact {key.value!r} is not a text artifact.")

        target = self.artifact_path(job_id, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = payload.strip()
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(text)
                tmp_file.write("\n")
            Path(tmp_name).replace(target)
        except Exception:
            Path(tmp_name).unlink(missing_ok=True)
            raise

        return target

    def read_text(self, job_id: str, key: ArtifactKey) -> str:
        """Read a text artifact."""
        spec = ARTIFACT_REGISTRY[key]
        if spec.content_type != "text/markdown":
            raise ValueError(f"Artifact {key.value!r} is not a text artifact.")

        return self.artifact_path(job_id, key).read_text(encoding="utf-8")

    @staticmethod
    def _to_jsonable(payload: BaseModel | dict[str, Any]) -> dict[str, Any]:
        if isinstance(payload, BaseModel):
            return payload.model_dump(mode="json")
        return payload

    @staticmethod
    def _validate_job_id(job_id: str) -> None:
        path = PurePath(job_id)
        if not job_id or path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
            raise ValueError("job_id must be a single safe path segment")
