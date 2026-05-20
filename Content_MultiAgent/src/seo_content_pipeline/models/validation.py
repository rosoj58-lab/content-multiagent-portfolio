"""Validation check contracts."""

from typing import Any, Literal

from pydantic import BaseModel, Field


ValidationSeverity = Literal["info", "warning", "error"]


class ValidationCheck(BaseModel):
    """One deterministic validation result."""

    name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
