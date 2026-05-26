"""App shell structure tests."""

import ast
from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_app_uses_controlled_error_for_empty_intake_input() -> None:
    tree = ast.parse((PROJECT_ROOT / "app.py").read_text(encoding="utf-8"))

    value_error_handlers = [
        handler
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        for handler in node.handlers
        if isinstance(handler.type, ast.Name) and handler.type.id == "ValueError"
    ]

    assert value_error_handlers
    assert any(
        isinstance(call.func, ast.Name) and call.func.id == "render_controlled_error"
        for handler in value_error_handlers
        for call in ast.walk(handler)
        if isinstance(call, ast.Call)
    )


def _run_demo_scenario_in_app(tmp_path, monkeypatch, *, article_type: str, input_file: str) -> AppTest:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    dry_input = (PROJECT_ROOT / "examples" / "inputs" / input_file).read_text(encoding="utf-8")
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.text_area[0].input(dry_input)
    app.selectbox[0].select(article_type)
    app.button[0].click().run()
    scenario_button = next(button for button in app.button if button.label == "Run demo scenario")
    scenario_button.click().run()
    return app


def test_app_displays_landing_page_revision_decision(tmp_path, monkeypatch) -> None:
    app = _run_demo_scenario_in_app(
        tmp_path,
        monkeypatch,
        article_type="LP",
        input_file="lp-demo.txt",
    )

    assert any("needs_revision" in warning.value for warning in app.warning)
    assert any("editorial_qa.json" in caption.value for caption in app.caption)
    assert any(subheader.value == "Decision QA Scorecard" for subheader in app.subheader)
    assert any("Remove the 70 percent claim" in info.value for info in app.info)
    assert any(button.label == "Apply recommended revision" for button in app.button)
    assert not any("Final package:" in caption.value for caption in app.caption)
    assert not any(subheader.value == "Revision Comparison" for subheader in app.subheader)

    revision_button = next(
        button for button in app.button if button.label == "Apply recommended revision"
    )
    revision_button.click().run()

    assert any("Revision applied: approved" in success.value for success in app.success)
    assert any("Final package:" in caption.value for caption in app.caption)
    assert any("Resolved revision evidence" in markdown.value for markdown in app.markdown)
    assert any(subheader.value == "Revision Comparison" for subheader in app.subheader)
    assert any("Rejected draft" in markdown.value for markdown in app.markdown)
    assert any("Approved version" in markdown.value for markdown in app.markdown)
    assert any("70 percent" in code.value for code in app.code)
    assert not any(button.label == "Apply recommended revision" for button in app.button)


def test_app_displays_guest_post_human_review_decision(tmp_path, monkeypatch) -> None:
    app = _run_demo_scenario_in_app(
        tmp_path,
        monkeypatch,
        article_type="GP",
        input_file="gp-demo.txt",
    )

    assert any("needs_human_review" in warning.value for warning in app.warning)
    assert any("editorial_qa.json" in caption.value for caption in app.caption)
    assert any(subheader.value == "Decision QA Scorecard" for subheader in app.subheader)
    assert any("host publication" in info.value for info in app.info)
    assert not any(button.label == "Apply recommended revision" for button in app.button)
    assert not any("Final package:" in caption.value for caption in app.caption)
    assert not any(subheader.value == "Revision Comparison" for subheader in app.subheader)


def test_app_displays_approved_scorecard_for_blog_post(tmp_path, monkeypatch) -> None:
    app = _run_demo_scenario_in_app(
        tmp_path,
        monkeypatch,
        article_type="BP",
        input_file="bp-demo.txt",
    )

    assert any("approved" in success.value for success in app.success)
    assert any(subheader.value == "Decision QA Scorecard" for subheader in app.subheader)
    assert any("Final package:" in caption.value for caption in app.caption)
    assert not any("Next action:" in info.value for info in app.info)
    assert not any(subheader.value == "Revision Comparison" for subheader in app.subheader)

    rerendered_app = app.run()

    assert any(
        subheader.value == "Decision QA Scorecard" for subheader in rerendered_app.subheader
    )


def test_app_hides_scorecard_before_scenario_execution(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.text_area[0].input("Source notes.")
    app.button[0].click().run()

    assert not any(subheader.value == "Decision QA Scorecard" for subheader in app.subheader)
