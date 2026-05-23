"""Stable demo input tests."""

import json
from pathlib import Path

from seo_content_pipeline.cli.demo import DEMO_INPUTS
from seo_content_pipeline.config import AppSettings
from seo_content_pipeline.models import ArtifactKey, ArticleType
from seo_content_pipeline.services.artifact_store import ArtifactStore
from seo_content_pipeline.services.job_service import JobService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUTS_DIR = PROJECT_ROOT / "examples" / "inputs"
DEMO_SETUP_DOC = PROJECT_ROOT / "docs" / "demo-setup.md"


EXPECTED_DEMOS = {
    "bp": ("bp-demo.txt", ArticleType.BP, "happy_path"),
    "lp": ("lp-demo.txt", ArticleType.LP, "revision_path"),
    "gp": ("gp-demo.txt", ArticleType.GP, "human_review_path"),
}


def test_stable_demo_input_files_exist() -> None:
    for filename, _article_type, _demo_path in EXPECTED_DEMOS.values():
        path = INPUTS_DIR / filename
        assert path.exists()
        assert path.read_text(encoding="utf-8").strip()

    assert (INPUTS_DIR / "sample-keywords.json").exists()


def test_sample_keywords_metadata_matches_demo_inputs() -> None:
    metadata = json.loads((INPUTS_DIR / "sample-keywords.json").read_text(encoding="utf-8"))

    assert set(metadata["demos"]) == set(EXPECTED_DEMOS)
    for key, (filename, article_type, demo_path) in EXPECTED_DEMOS.items():
        demo = metadata["demos"][key]
        assert demo["input_file"] == filename
        assert demo["article_type"] == article_type.value
        assert demo["demo_path"] == demo_path
        assert demo["main_keyword"]
        assert demo["secondary_keywords"]
        assert demo["lsi_keywords"]


def test_cli_demo_catalog_matches_sample_keywords_metadata() -> None:
    metadata = json.loads((INPUTS_DIR / "sample-keywords.json").read_text(encoding="utf-8"))

    assert set(DEMO_INPUTS) == set(metadata["demos"])
    for key, demo_input in DEMO_INPUTS.items():
        demo = metadata["demos"][key]
        assert demo_input.article_type.value == demo["article_type"]
        assert demo_input.input_path.name == demo["input_file"]
        assert demo_input.demo_path == demo["demo_path"]
        assert demo_input.purpose == demo["notes"]


def test_demo_inputs_can_create_job_shells(tmp_path) -> None:
    settings = AppSettings(artifact_root=tmp_path)
    store = ArtifactStore(settings.artifact_root)
    service = JobService(settings=settings, artifact_store=store)

    for filename, article_type, _demo_path in EXPECTED_DEMOS.values():
        dry_input = (INPUTS_DIR / filename).read_text(encoding="utf-8")

        result = service.create_job(dry_input, article_type)

        input_artifact = store.read_json(result.metadata.job_id, ArtifactKey.INPUT)
        assert input_artifact["article_type"] == article_type.value
        assert input_artifact["dry_input"].startswith("Demo:")
        assert len(input_artifact["dry_input"]) > 300


def test_demo_setup_docs_explain_each_demo_path() -> None:
    docs = DEMO_SETUP_DOC.read_text(encoding="utf-8")

    for filename, article_type, demo_path in EXPECTED_DEMOS.values():
        assert filename in docs
        assert article_type.value in docs
        assert demo_path.replace("_", " ") in docs.lower()
