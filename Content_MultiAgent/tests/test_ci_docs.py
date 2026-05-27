"""CI workflow and README coverage tests."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_github_actions_ci_runs_project_quality_gate() -> None:
    workflow = REPO_ROOT / ".github" / "workflows" / "content-multiagent-ci.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "working-directory: Content_MultiAgent" in text
    assert "workflow_dispatch:" in text
    assert "contents: read" in text
    assert "actions/checkout@v6" in text
    assert "actions/setup-python@v6" in text
    assert "python-version: \"3.12\"" in text
    assert "uv sync --frozen" in text
    assert "uv run ruff check ." in text
    assert "uv run pytest" in text


def test_pull_request_template_covers_quality_demo_docker_and_security() -> None:
    template = REPO_ROOT / ".github" / "pull_request_template.md"
    text = template.read_text(encoding="utf-8")

    assert "## Summary" in text
    assert "## Quality Gate" in text
    assert "uv run ruff check ." in text
    assert "uv run pytest" in text
    assert "make interview-check" in text
    assert "## Demo Proof" in text
    assert "uv run seo-demo --demo bp --mode demo" in text
    assert "artifacts/jobs/<job_id>/" in text
    assert "## Docker" in text
    assert "docker compose build" in text
    assert "docker compose run --rm app uv run pytest" in text
    assert "## Security And Privacy" in text
    assert "SECURITY.md" in text
    assert ".env" in text
    assert "API keys" in text


def test_issue_templates_cover_bug_feature_demo_and_security_context() -> None:
    issue_dir = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
    bug = (issue_dir / "bug_report.yml").read_text(encoding="utf-8")
    feature = (issue_dir / "feature_request.yml").read_text(encoding="utf-8")
    config = (issue_dir / "config.yml").read_text(encoding="utf-8")

    assert "name: Bug report" in bug
    assert "uv run seo-demo --demo bp --mode demo" in bug
    assert "artifacts/jobs/<job_id>/" in bug
    assert "uv run ruff check ." in bug
    assert "uv run pytest" in bug
    assert "make interview-check" in bug
    assert "SECURITY.md" in bug
    assert ".env" in bug

    assert "name: Feature request" in feature
    assert "offline-first" in feature
    assert "Multi-agent workflow" in feature
    assert "Uniqueness provider" in feature
    assert "uv run seo-demo --demo bp --mode demo" in feature
    assert "make interview-check" in feature
    assert "without OpenAI or Copyleaks credentials" in feature
    assert "SECURITY.md" in feature

    assert "blank_issues_enabled: true" in config
    assert "Security and privacy guidance" in config
    assert "docs.github.com" in config
    assert "SECURITY.md" in config


def test_dependabot_covers_project_dependencies_and_platform_files() -> None:
    dependabot = (REPO_ROOT / ".github" / "dependabot.yml").read_text(
        encoding="utf-8"
    )

    assert "version: 2" in dependabot
    assert 'package-ecosystem: "pip"' in dependabot
    assert 'directory: "/Content_MultiAgent"' in dependabot
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert 'package-ecosystem: "docker"' in dependabot
    assert 'package-ecosystem: "docker-compose"' in dependabot
    assert 'interval: "weekly"' in dependabot
    assert "open-pull-requests-limit: 5" in dependabot
    assert '"dependencies"' in dependabot
    assert '"python"' in dependabot
    assert '"github-actions"' in dependabot
    assert '"docker"' in dependabot
    assert 'dependency-name: "python"' in dependabot
    assert '"version-update:semver-major"' in dependabot
    assert '"version-update:semver-minor"' in dependabot


def test_readme_mentions_ci_quality_gate() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "GitHub Actions" in readme
    assert "uv sync --frozen" in readme
    assert "uv run ruff check ." in readme
    assert "uv run pytest" in readme
