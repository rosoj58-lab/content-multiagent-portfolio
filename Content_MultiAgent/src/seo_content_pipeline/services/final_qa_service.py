"""Final QA report and status orchestration."""

from datetime import UTC, datetime

from seo_content_pipeline.config import AppSettings, get_settings
from seo_content_pipeline.models import (
    ArtifactKey,
    FinalQAFailedCheck,
    FinalQALocalizationStatus,
    FinalQAReport,
    FinalQAUniquenessResult,
    JobMetadata,
    PipelineState,
    StatusHistoryEntry,
    WorkflowStage,
    WorkflowStatus,
)
from seo_content_pipeline.services.artifact_store import ArtifactStore


MANDATORY_ARTIFACTS: tuple[tuple[ArtifactKey, WorkflowStage], ...] = (
    (ArtifactKey.INPUT, WorkflowStage.INPUT_RECEIVED),
    (ArtifactKey.BRIEF, WorkflowStage.BRIEF_DRAFTED),
    (ArtifactKey.ENGLISH_ORIGINAL, WorkflowStage.WRITING),
    (ArtifactKey.ARTICLE_VALIDATION, WorkflowStage.WRITING),
    (ArtifactKey.EDITORIAL_QA, WorkflowStage.EDITORIAL_REVIEW),
    (ArtifactKey.SEO_QA, WorkflowStage.SEO_QA),
    (ArtifactKey.UNIQUENESS, WorkflowStage.UNIQUENESS_CHECK),
    (ArtifactKey.LOCALIZATION_ES, WorkflowStage.LOCALIZATION),
    (ArtifactKey.LOCALIZATION_IT, WorkflowStage.LOCALIZATION),
    (ArtifactKey.LOCALIZATION_FR, WorkflowStage.LOCALIZATION),
    (ArtifactKey.FINAL_PACKAGE_MD, WorkflowStage.FINAL_QA),
    (ArtifactKey.FINAL_PACKAGE_JSON, WorkflowStage.FINAL_QA),
)

MANDATORY_GATES: tuple[tuple[str, WorkflowStage, str], ...] = (
    ("article_validation_passed", WorkflowStage.WRITING, "Article validation must pass."),
    ("editorial_qa_passed", WorkflowStage.EDITORIAL_REVIEW, "Editorial QA must pass."),
    ("seo_qa_passed", WorkflowStage.SEO_QA, "SEO QA must pass."),
    ("uniqueness_gate_passed", WorkflowStage.UNIQUENESS_CHECK, "Uniqueness gate must pass."),
    ("localization_es_generated", WorkflowStage.LOCALIZATION, "Spanish localization must exist."),
    ("localization_it_generated", WorkflowStage.LOCALIZATION, "Italian localization must exist."),
    ("localization_fr_generated", WorkflowStage.LOCALIZATION, "French localization must exist."),
    ("final_package_assembled", WorkflowStage.FINAL_QA, "Final package must be assembled."),
)

LOCALIZATION_ARTIFACTS = {
    "es": ArtifactKey.LOCALIZATION_ES,
    "it": ArtifactKey.LOCALIZATION_IT,
    "fr": ArtifactKey.LOCALIZATION_FR,
}


class FinalQAResult(FinalQAReport):
    """Return type for final QA execution."""


class FinalQAService:
    """Produce deterministic final QA report and terminal workflow status."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.artifact_store = artifact_store or ArtifactStore(self.settings.artifact_root)

    def run_final_qa(self, job_id: str) -> FinalQAResult:
        """Persist final QA report and approved or revision status."""
        state = self._load_state(job_id)
        metadata = self._load_metadata(job_id)
        failed_checks = (
            self._artifact_failures(job_id)
            + self._gate_failures(state)
            + self._qa_report_failures(job_id)
        )
        uniqueness_result = self._uniqueness_result(job_id, state)
        if not uniqueness_result.passed and not any(
            check.name == "gate_uniqueness_gate_passed" for check in failed_checks
        ):
            failed_checks.append(
                FinalQAFailedCheck(
                    name="uniqueness_threshold_passed",
                    message="Uniqueness score must meet the configured threshold.",
                    routing_target=WorkflowStage.UNIQUENESS_CHECK,
                )
            )

        status = WorkflowStatus.APPROVED if not failed_checks else WorkflowStatus.NEEDS_REVISION
        routing_target = failed_checks[0].routing_target if failed_checks else None
        routing_guidance = self._routing_guidance(routing_target) if routing_target else None
        report = FinalQAReport(
            job_id=job_id,
            status=status,
            completed_stages=self._completed_stages(job_id, state),
            failed_checks=failed_checks,
            uniqueness_result=uniqueness_result,
            localization_status=self._localization_status(job_id, state),
            routing_target=routing_target,
            routing_guidance=routing_guidance,
        )
        report_path = self.artifact_store.write_json(job_id, ArtifactKey.FINAL_QA_REPORT, report)
        self._sync_final_package_status(job_id, report.status)
        self._persist_final_status(
            job_id,
            report=report,
            report_path=str(report_path),
            state=state,
            metadata=metadata,
        )
        return FinalQAResult.model_validate(report.model_dump())

    def _artifact_failures(self, job_id: str) -> list[FinalQAFailedCheck]:
        failures = []
        for artifact_key, routing_target in MANDATORY_ARTIFACTS:
            if not self.artifact_store.artifact_path(job_id, artifact_key).exists():
                failures.append(
                    FinalQAFailedCheck(
                        name=f"artifact_{artifact_key.value}_present",
                        message=f"Required artifact {artifact_key.value} is missing.",
                        routing_target=routing_target,
                    )
                )
        return failures

    @staticmethod
    def _gate_failures(state: PipelineState) -> list[FinalQAFailedCheck]:
        return [
            FinalQAFailedCheck(name=f"gate_{flag}", message=message, routing_target=routing_target)
            for flag, routing_target, message in MANDATORY_GATES
            if not state.qa_flags.get(flag, False)
        ]

    def _qa_report_failures(self, job_id: str) -> list[FinalQAFailedCheck]:
        report_checks = (
            (ArtifactKey.ARTICLE_VALIDATION, WorkflowStage.WRITING, "Article validation report failed."),
            (ArtifactKey.EDITORIAL_QA, WorkflowStage.EDITORIAL_REVIEW, "Editorial QA report failed."),
            (ArtifactKey.SEO_QA, WorkflowStage.SEO_QA, "SEO QA report failed."),
        )
        failures = []
        for artifact_key, routing_target, message in report_checks:
            if not self.artifact_store.artifact_path(job_id, artifact_key).exists():
                continue
            report = self.artifact_store.read_json(job_id, artifact_key)
            if report.get("passed") is not True:
                failures.append(
                    FinalQAFailedCheck(
                        name=f"report_{artifact_key.value}_passed",
                        message=message,
                        routing_target=routing_target,
                    )
                )
        return failures

    def _uniqueness_result(self, job_id: str, state: PipelineState) -> FinalQAUniquenessResult:
        threshold = state.uniqueness_threshold or 90.0
        score = state.uniqueness_score
        source = state.uniqueness_source.value if state.uniqueness_source else None
        if self.artifact_store.artifact_path(job_id, ArtifactKey.UNIQUENESS).exists():
            uniqueness = self.artifact_store.read_json(job_id, ArtifactKey.UNIQUENESS)
            score = uniqueness.get("score", score)
            source = uniqueness.get("source", source)
        return FinalQAUniquenessResult(
            score=score,
            source=source,
            threshold=threshold,
            passed=score is not None
            and score >= threshold
            and state.qa_flags.get("uniqueness_gate_passed", False),
        )

    def _localization_status(
        self,
        job_id: str,
        state: PipelineState,
    ) -> dict[str, FinalQALocalizationStatus]:
        return {
            language: FinalQALocalizationStatus(
                language=language,
                artifact_key=artifact_key,
                present=self.artifact_store.artifact_path(job_id, artifact_key).exists(),
                geo=state.localization_geos.get(language),
            )
            for language, artifact_key in LOCALIZATION_ARTIFACTS.items()
        }

    def _completed_stages(self, job_id: str, state: PipelineState) -> list[WorkflowStage]:
        stages = {entry.stage for entry in state.status_history}
        artifact_stage_map = {
            ArtifactKey.INPUT: WorkflowStage.INPUT_RECEIVED,
            ArtifactKey.BRIEF: WorkflowStage.BRIEF_DRAFTED,
            ArtifactKey.ENGLISH_ORIGINAL: WorkflowStage.WRITING,
            ArtifactKey.EDITORIAL_QA: WorkflowStage.EDITORIAL_REVIEW,
            ArtifactKey.SEO_QA: WorkflowStage.SEO_QA,
            ArtifactKey.UNIQUENESS: WorkflowStage.UNIQUENESS_CHECK,
            ArtifactKey.LOCALIZATION_ES: WorkflowStage.LOCALIZATION,
            ArtifactKey.LOCALIZATION_IT: WorkflowStage.LOCALIZATION,
            ArtifactKey.LOCALIZATION_FR: WorkflowStage.LOCALIZATION,
            ArtifactKey.FINAL_PACKAGE_JSON: WorkflowStage.FINAL_QA,
        }
        for artifact_key, stage in artifact_stage_map.items():
            if self.artifact_store.artifact_path(job_id, artifact_key).exists():
                stages.add(stage)
        stage_order = {stage: index for index, stage in enumerate(WorkflowStage)}
        return sorted(stages, key=lambda stage: stage_order[stage])

    @staticmethod
    def _routing_guidance(routing_target: WorkflowStage) -> str:
        return f"Route the job to {routing_target.value} for revision before approval."

    def _sync_final_package_status(self, job_id: str, status: WorkflowStatus) -> None:
        package_json_path = self.artifact_store.artifact_path(job_id, ArtifactKey.FINAL_PACKAGE_JSON)
        if package_json_path.exists():
            package = self.artifact_store.read_json(job_id, ArtifactKey.FINAL_PACKAGE_JSON)
            package["workflow_status"] = {
                "current_stage": WorkflowStage.FINAL_QA.value,
                "status": status.value,
            }
            self.artifact_store.write_json(job_id, ArtifactKey.FINAL_PACKAGE_JSON, package)

        package_markdown_path = self.artifact_store.artifact_path(job_id, ArtifactKey.FINAL_PACKAGE_MD)
        if package_markdown_path.exists():
            markdown = self.artifact_store.read_text(job_id, ArtifactKey.FINAL_PACKAGE_MD)
            heading = "## Workflow Status\n\n"
            if heading in markdown:
                prefix = markdown.split(heading, maxsplit=1)[0]
                markdown = (
                    f"{prefix}{heading}"
                    f"- Stage: `{WorkflowStage.FINAL_QA.value}`\n"
                    f"- Status: `{status.value}`"
                )
                self.artifact_store.write_text(job_id, ArtifactKey.FINAL_PACKAGE_MD, markdown)

    def _persist_final_status(
        self,
        job_id: str,
        *,
        report: FinalQAReport,
        report_path: str,
        state: PipelineState,
        metadata: JobMetadata,
    ) -> None:
        now = datetime.now(UTC)
        history_entry = StatusHistoryEntry(
            stage=WorkflowStage.FINAL_QA,
            status=report.status,
            message=f"Final QA completed with status {report.status.value}.",
            created_at=now,
        )
        state.current_stage = WorkflowStage.FINAL_QA
        state.status = report.status
        state.artifact_paths[ArtifactKey.FINAL_QA_REPORT] = report_path
        state.qa_flags["final_qa_passed"] = report.status is WorkflowStatus.APPROVED
        if report.routing_guidance:
            state.revision_notes.setdefault(WorkflowStage.FINAL_QA, []).append(report.routing_guidance)
        state.status_history.append(history_entry)

        metadata.current_stage = WorkflowStage.FINAL_QA
        metadata.status = report.status
        metadata.updated_at = now
        metadata.status_history.append(history_entry)

        self.artifact_store.write_json(job_id, ArtifactKey.STATE, state)
        self.artifact_store.write_json(job_id, ArtifactKey.METADATA, metadata)

    def _load_state(self, job_id: str) -> PipelineState:
        return PipelineState.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.STATE))

    def _load_metadata(self, job_id: str) -> JobMetadata:
        return JobMetadata.model_validate(self.artifact_store.read_json(job_id, ArtifactKey.METADATA))
