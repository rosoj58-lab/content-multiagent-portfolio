"""Repository health checks for portfolio polish."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
SEARCH_ROOTS = [
    REPO_ROOT / "compose.yaml",
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "Dockerfile",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "examples",
    PROJECT_ROOT / "src",
]


def _text_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix in {".md", ".py", ".toml", ".json"}
        )
    return files


def test_tracked_portfolio_files_do_not_contain_scaffold_leftovers() -> None:
    forbidden = [
        "Project scaffold is ready",
        "Placeholder for expected output",
        "placeholders.",
    ]
    offenders: list[str] = []
    for path in _text_files():
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            if phrase in text:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {phrase}")

    assert offenders == []


def test_empty_placeholder_modules_were_removed() -> None:
    removed_paths = [
        "src/seo_content_pipeline/graph/state.py",
        "src/seo_content_pipeline/graph/builder.py",
        "src/seo_content_pipeline/validators/revision_validators.py",
    ]

    assert [path for path in removed_paths if (PROJECT_ROOT / path).exists()] == []


def test_dockerignore_excludes_local_state_and_keeps_env_example() -> None:
    dockerignore = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")

    required_patterns = [
        ".env",
        ".env.*",
        "!.env.example",
        ".venv/",
        ".pytest_cache/",
        ".ruff_cache/",
        ".mypy_cache/",
        ".coverage",
        "coverage.xml",
        "htmlcov/",
        ".playwright-mcp/",
        ".streamlit/secrets.toml",
        "artifacts/jobs/*",
        "!artifacts/jobs/.gitkeep",
    ]

    for pattern in required_patterns:
        assert pattern in dockerignore
