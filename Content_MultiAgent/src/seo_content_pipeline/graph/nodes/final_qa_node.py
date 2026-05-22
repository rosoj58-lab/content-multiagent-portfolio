"""Final package and final QA graph nodes."""

from seo_content_pipeline.services.exporters import FinalPackageExporter, FinalPackageResult


def assemble_final_package_node(
    job_id: str,
    final_package_exporter: FinalPackageExporter,
) -> FinalPackageResult:
    """Assemble final Markdown and JSON package artifacts for a job."""
    return final_package_exporter.assemble_final_package(job_id)
