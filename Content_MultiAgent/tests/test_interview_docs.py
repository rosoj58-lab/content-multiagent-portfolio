"""Interview documentation tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "demo_setup": PROJECT_ROOT / "docs" / "demo-setup.md",
    "demo_script": PROJECT_ROOT / "docs" / "demo-script.md",
    "interview_cheatsheet": PROJECT_ROOT / "docs" / "interview-cheatsheet.md",
    "artifact_map": PROJECT_ROOT / "docs" / "artifact-map.md",
    "architecture_summary": PROJECT_ROOT / "docs" / "architecture-summary.md",
    "project_structure": PROJECT_ROOT / "docs" / "project-structure.md",
    "roadmap": PROJECT_ROOT / "docs" / "roadmap.md",
    "offline_first_adr": PROJECT_ROOT
    / "docs"
    / "decisions"
    / "0001-offline-first-demo-and-provider-boundaries.md",
}


def _read_doc(name: str) -> str:
    return DOCS[name].read_text(encoding="utf-8")


def test_required_interview_docs_exist_and_are_not_placeholders() -> None:
    for path in DOCS.values():
        text = path.read_text(encoding="utf-8")
        assert path.exists()
        assert "Placeholder" not in text
        assert len(text.split()) > 80


def test_docs_explain_three_demo_paths() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS.values())

    assert "happy path" in combined
    assert "revision path" in combined
    assert "human-review path" in combined or "human review path" in combined
    assert "bp-demo.txt" in combined
    assert "lp-demo.txt" in combined
    assert "gp-demo.txt" in combined


def test_interview_cheatsheet_covers_pitch_tradeoffs_and_questions() -> None:
    cheatsheet = _read_doc("interview_cheatsheet").lower()

    assert "60-second pitch" in cheatsheet
    assert "uv run seo-demo --demo bp --mode demo" in cheatsheet
    assert "uv run seo-demo --list-demos" in cheatsheet
    assert "uv run seo-demo --demo all --mode demo" in cheatsheet
    assert "make interview-check" in cheatsheet
    assert "make release-check" in cheatsheet
    assert "artifacts/demo/demo-summary.json" in cheatsheet
    assert "needs_revision" in cheatsheet
    assert "needs_human_review" in cheatsheet
    assert "decision qa scorecard" in cheatsheet
    assert "honest tradeoffs" in cheatsheet
    assert "likely questions" in cheatsheet
    assert "not a hosted production system" in cheatsheet
    assert "production-ready" in cheatsheet


def test_roadmap_documents_mvp_next_steps_and_deferred_scope() -> None:
    roadmap = _read_doc("roadmap").lower()

    assert "current mvp" in roadmap
    assert "next technical steps" in roadmap
    assert "deferred on purpose" in roadmap
    assert "known risks" in roadmap
    assert "async stage execution" in roadmap
    assert "real llm provider" in roadmap
    assert "hosted deployment" in roadmap
    assert "not as a production saas platform" in roadmap


def test_artifact_map_identifies_storage_and_qa_decisions() -> None:
    artifact_map = _read_doc("artifact_map").lower()

    assert "artifacts/jobs" in artifact_map
    assert "artifacts/demo/demo-summary.json" in artifact_map
    assert "state.json" in artifact_map
    assert "final_package.md" in artifact_map
    assert "final_package.json" in artifact_map
    assert "final_qa_report.json" in artifact_map
    assert "qa decision" in artifact_map
    assert "revision routing" in artifact_map


def test_artifact_map_documents_demo_summary_manifest_contract() -> None:
    artifact_map = _read_doc("artifact_map")

    required_fields = [
        "`version`",
        "`requested_demo`",
        "`mode`",
        "`artifact_root`",
        "`run_count`",
        "`runs[].demo`",
        "`runs[].article_type`",
        "`runs[].input_file`",
        "`runs[].demo_path`",
        "`runs[].purpose`",
        "`runs[].artifact_dir`",
        "`runs[].status`",
        "`runs[].decision_artifact`",
        "`runs[].final_package`",
        "`runs[].final_qa_report`",
    ]

    assert "Manifest contract version" in artifact_map
    assert "Current value: `2`" in artifact_map
    for field in required_fields:
        assert field in artifact_map


def test_architecture_docs_reinforce_status_and_routing_requirements() -> None:
    combined = (_read_doc("architecture_summary") + "\n" + _read_doc("project_structure")).lower()

    assert "fr17" in combined
    assert "fr18" in combined
    assert "workflow status" in combined
    assert "revision routing" in combined
    assert "streamlit" in combined
    assert "artifactstore" in combined


def test_architecture_summary_includes_pipeline_diagram() -> None:
    architecture = _read_doc("architecture_summary").lower()

    assert "```mermaid" in architecture
    assert "flowchart td" in architecture
    assert "dry input" in architecture
    assert "seo brief" in architecture
    assert "uniqueness gate" in architecture
    assert "final qa report" in architecture
    assert "artifactstore artifacts/jobs" in architecture


def test_offline_first_provider_boundary_adr_is_linked_from_interview_docs() -> None:
    adr = _read_doc("offline_first_adr").lower()
    architecture = _read_doc("architecture_summary")
    cheatsheet = _read_doc("interview_cheatsheet")

    adr_path = "docs/decisions/0001-offline-first-demo-and-provider-boundaries.md"

    assert "offline-first demo" in adr
    assert "provider boundaries" in adr
    assert "openai" in adr
    assert "copyleaks" in adr
    assert "credentials" in adr
    assert "artifacts/jobs/<job_id>/" in adr
    assert "uv run seo-demo --demo all --mode demo" in adr
    assert "make interview-check" in adr
    assert adr_path in architecture
    assert adr_path in cheatsheet
