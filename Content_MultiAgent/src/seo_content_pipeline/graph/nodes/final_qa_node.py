"""Final package and final QA graph nodes."""

from seo_content_pipeline.services.exporters import FinalPackageExporter, FinalPackageResult
from seo_content_pipeline.services.final_qa_service import FinalQAResult, FinalQAService


def assemble_final_package_node(
    job_id: str,
    final_package_exporter: FinalPackageExporter,
) -> FinalPackageResult:
    """Assemble final Markdown and JSON package artifacts for a job."""
    return final_package_exporter.assemble_final_package(job_id)


def run_final_qa_node(
    job_id: str,
    final_qa_service: FinalQAService,
) -> FinalQAResult:
    """Run final QA and persist approved or revision status."""
    return final_qa_service.run_final_qa(job_id)
