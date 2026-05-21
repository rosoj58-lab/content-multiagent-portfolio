"""SEO QA graph node."""

from seo_content_pipeline.services.seo_qa_service import SEOQAResult, SEOQAService


def run_seo_node(job_id: str, seo_qa_service: SEOQAService) -> SEOQAResult:
    """Run SEO QA for a job."""
    return seo_qa_service.run_seo_qa(job_id)
