"""English Original writer graph node."""

from seo_content_pipeline.prompts.writer import WritingMode
from seo_content_pipeline.services.writer_service import WriterResult, WriterService


def run_writer_node(
    job_id: str,
    writer_service: WriterService,
    *,
    mode: WritingMode = "demo",
) -> WriterResult:
    """Run the writer stage for an approved brief."""
    return writer_service.generate_english_original(job_id, mode=mode)
