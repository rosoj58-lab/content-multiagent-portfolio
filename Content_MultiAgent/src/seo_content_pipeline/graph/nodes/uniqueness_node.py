"""Uniqueness graph node."""

from seo_content_pipeline.config import UniquenessProviderName
from seo_content_pipeline.services.uniqueness_provider_service import (
    UniquenessProviderSelectionResult,
    UniquenessProviderService,
)
from seo_content_pipeline.services.uniqueness_score_service import (
    ManualUniquenessScoreResult,
    UniquenessScoreService,
)


def select_uniqueness_provider_node(
    job_id: str,
    provider_name: UniquenessProviderName,
    uniqueness_provider_service: UniquenessProviderService,
) -> UniquenessProviderSelectionResult:
    """Persist a uniqueness provider selection for a job."""
    return uniqueness_provider_service.select_provider(job_id, provider_name)


def record_manual_uniqueness_score_node(
    job_id: str,
    score: object,
    uniqueness_score_service: UniquenessScoreService,
) -> ManualUniquenessScoreResult:
    """Record a manual uniqueness score for a job."""
    return uniqueness_score_service.record_manual_score(job_id, score)
