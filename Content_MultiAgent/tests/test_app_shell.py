"""App shell structure tests."""

import ast
import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArticleType
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.demo_pipeline_service import DemoPipelineService
from seo_content_pipeline.services.job_service import JobService
from seo_content_pipeline.services import live_brief_service


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAFE_LP_CORRECTION = "The landing page presents only supplied evidence."


def _persist_demo_job(tmp_path, article_type: ArticleType) -> str:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    job = JobService(settings=settings, artifact_store=store).create_job(
        "Stable source notes for recent jobs.",
        article_type,
    )
    DemoPipelineService(settings=settings, artifact_store=store).run_demo_scenario(
        job.metadata.job_id,
        mode="demo",
    )
    return job.metadata.job_id


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


def test_app_shows_quiet_recent_jobs_empty_state(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))

    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()

    assert any("No recent jobs yet" in caption.value for caption in app.caption)
    assert any(button.label == "Create job" for button in app.button)


def test_app_can_load_recent_job_without_rerunning_workflow(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    job_id = _persist_demo_job(tmp_path, ArticleType.BP)

    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    recent_select = next(selectbox for selectbox in app.selectbox if selectbox.label == "Recent jobs")
    recent_select.select(next(option for option in recent_select.options if job_id in option))
    next(button for button in app.button if button.label == "Load selected job").click().run()

    assert any(f"Job created: {job_id}" in success.value for success in app.success)
    assert any(subheader.value == "Decision QA Scorecard" for subheader in app.subheader)
    assert any("run_summary.json" in code.value for code in app.code)


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
    assert any(text_area.label == "Replacement statement" for text_area in app.text_area)
    assert any(button.label == "Apply correction" for button in app.button)
    assert not any("Final package:" in caption.value for caption in app.caption)
    assert not any(subheader.value == "Revision Comparison" for subheader in app.subheader)

    correction_input = next(
        text_area for text_area in app.text_area if text_area.label == "Replacement statement"
    )
    correction_input.input(SAFE_LP_CORRECTION)
    revision_button = next(button for button in app.button if button.label == "Apply correction")
    revision_button.click().run()

    assert any("Revision applied: approved" in success.value for success in app.success)
    assert any("Final package:" in caption.value for caption in app.caption)
    assert any("Resolved revision evidence" in markdown.value for markdown in app.markdown)
    assert any(subheader.value == "Revision Comparison" for subheader in app.subheader)
    assert any("Rejected draft" in markdown.value for markdown in app.markdown)
    assert any("Approved version" in markdown.value for markdown in app.markdown)
    assert any("70 percent" in code.value for code in app.code)
    assert any(SAFE_LP_CORRECTION in code.value for code in app.code)
    assert not any(button.label == "Apply correction" for button in app.button)


def test_app_rejects_unsafe_landing_page_correction_without_approval(tmp_path, monkeypatch) -> None:
    app = _run_demo_scenario_in_app(
        tmp_path,
        monkeypatch,
        article_type="LP",
        input_file="lp-demo.txt",
    )
    correction_input = next(
        text_area for text_area in app.text_area if text_area.label == "Replacement statement"
    )
    correction_input.input("Guaranteed 45% lower costs.")
    correction_button = next(button for button in app.button if button.label == "Apply correction")
    correction_button.click().run()

    assert any(error.value == "Action needed" for error in app.error)
    assert any("without numbers" in info.value for info in app.info)
    assert any(button.label == "Apply correction" for button in app.button)
    assert not any("Final package:" in caption.value for caption in app.caption)
    assert not any(subheader.value == "Revision Comparison" for subheader in app.subheader)


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
    assert not any(button.label == "Apply correction" for button in app.button)
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
    assert not any(button.label == "Apply correction" for button in app.button)
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


def test_app_disables_live_brief_action_without_api_key(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.text_area[0].input("Source notes for an SEO brief.")
    app.button[0].click().run()

    live_button = next(button for button in app.button if button.label == "Generate live SEO brief")
    assert live_button.disabled is True
    assert any("Set OPENAI_API_KEY locally" in info.value for info in app.info)
    assert any("Optional live SEO brief only" in caption.value for caption in app.caption)


class FakeOpenAILLMClient:
    def __init__(self, *, api_key: str, model: str) -> None:
        assert api_key == "test-key"
        assert model == "gpt-5.4-mini"

    def generate(self, prompt: str) -> str:
        assert "SEO brief agent" in prompt
        return json.dumps(
            {
                "topic": "Live SEO brief",
                "goal": "Demonstrate explicit live generation.",
                "audience": "Technical interviewers",
                "main_keyword": "live SEO brief",
                "secondary_keywords": ["OpenAI workflow"],
                "lsi_keywords": ["quality gate"],
                "outline": {
                    "h1": "Live SEO Brief",
                    "sections": [{"h2": "Generation", "h3": ["Review"]}],
                },
                "tone_of_voice": "Clear",
                "constraints": ["Do not invent facts"],
            }
        )


def test_app_runs_configured_live_brief_only_to_manual_gate(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(live_brief_service, "OpenAILLMClient", FakeOpenAILLMClient)
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.text_area[0].input("Source notes for a real SEO brief.")
    app.button[0].click().run()

    live_button = next(button for button in app.button if button.label == "Generate live SEO brief")
    live_button.click().run()

    assert any("Live SEO brief complete: waiting_for_human" in success.value for success in app.success)
    assert any("SEO brief generation and deterministic brief QA only" in caption.value for caption in app.caption)
    assert any("live SEO brief" in code.value for code in app.code)

    rerendered_app = app.run()
    assert not any(button.label == "Generate live SEO brief" for button in rerendered_app.button)
    assert not any(button.label == "Run demo scenario" for button in rerendered_app.button)


class FailingOpenAILLMClient:
    def __init__(self, *, api_key: str, model: str) -> None:
        pass

    def generate(self, prompt: str) -> str:
        raise RuntimeError("OpenAI live generation failed.")


def test_app_presents_controlled_error_for_live_provider_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(live_brief_service, "OpenAILLMClient", FailingOpenAILLMClient)
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.text_area[0].input("Source notes for an SEO brief.")
    app.button[0].click().run()
    next(button for button in app.button if button.label == "Generate live SEO brief").click().run()

    assert any(error.value == "Something needs attention" for error in app.error)
    assert any("Check OPENAI_API_KEY and OPENAI_MODEL" in info.value for info in app.info)
    assert not any("brief.json" in code.value for code in app.code)


class UnparseableOpenAILLMClient:
    def __init__(self, *, api_key: str, model: str) -> None:
        pass

    def generate(self, prompt: str) -> str:
        return "not structured JSON"


def test_app_warns_when_live_brief_needs_human_review(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(live_brief_service, "OpenAILLMClient", UnparseableOpenAILLMClient)
    app = AppTest.from_file(PROJECT_ROOT / "app.py").run()
    app.text_area[0].input("Source notes for an SEO brief.")
    app.button[0].click().run()
    next(button for button in app.button if button.label == "Generate live SEO brief").click().run()

    assert any("Live SEO brief stopped: needs_human_review" in warning.value for warning in app.warning)
    assert not any("Live SEO brief complete" in success.value for success in app.success)
    assert not any("brief.json" in code.value for code in app.code)
