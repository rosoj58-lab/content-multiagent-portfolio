"""Scaffold structure tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "src" / "seo_content_pipeline"


REQUIRED_PATHS = [
    "pyproject.toml",
    "uv.lock",
    "app.py",
    ".env.example",
    ".gitignore",
    "README.md",
    "src/seo_content_pipeline",
    "tests",
    "docs",
    "examples",
    "artifacts",
    "artifacts/demo/.gitkeep",
    "artifacts/jobs/.gitkeep",
]


def test_required_scaffold_paths_exist() -> None:
    missing = [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]

    assert missing == []


def test_python_package_directories_have_init_files() -> None:
    package_dirs = [
        path
        for path in PACKAGE_ROOT.rglob("*")
        if path.is_dir() and "__pycache__" not in path.parts
    ]
    package_dirs.append(PACKAGE_ROOT)

    missing = [path.relative_to(PROJECT_ROOT).as_posix() for path in package_dirs if not (path / "__init__.py").exists()]

    assert missing == []
