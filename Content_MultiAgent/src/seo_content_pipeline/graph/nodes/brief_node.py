"""Brief generation graph node."""

from seo_content_pipeline.services.brief_service import BriefGenerationResult, BriefService


def run_brief_node(job_id: str, brief_service: BriefService) -> BriefGenerationResult:
    """Run the brief generation stage for a job."""
    return brief_service.generate_brief(job_id)
