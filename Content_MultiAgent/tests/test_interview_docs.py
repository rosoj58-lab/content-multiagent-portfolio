"""Interview documentation tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "demo_setup": PROJECT_ROOT / "docs" / "demo-setup.md",
    "demo_script": PROJECT_ROOT / "docs" / "demo-script.md",
    "artifact_map": PROJECT_ROOT / "docs" / "artifact-map.md",
    "architecture_summary": PROJECT_ROOT / "docs" / "architecture-summary.md",
    "project_structure": PROJECT_ROOT / "docs" / "project-structure.md",
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


def test_artifact_map_identifies_storage_and_qa_decisions() -> None:
    artifact_map = _read_doc("artifact_map").lower()

    assert "artifacts/jobs" in artifact_map
    assert "state.json" in artifact_map
    assert "final_package.md" in artifact_map
    assert "final_package.json" in artifact_map
    assert "final_qa_report.json" in artifact_map
    assert "qa decision" in artifact_map
    assert "revision routing" in artifact_map


def test_architecture_docs_reinforce_status_and_routing_requirements() -> None:
    combined = (_read_doc("architecture_summary") + "\n" + _read_doc("project_structure")).lower()

    assert "fr17" in combined
    assert "fr18" in combined
    assert "workflow status" in combined
    assert "revision routing" in combined
    assert "streamlit" in combined
    assert "artifactstore" in combined
