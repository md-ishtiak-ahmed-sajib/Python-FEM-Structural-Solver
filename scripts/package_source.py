"""Create a reviewable source archive with no environments, credentials or private data."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    files = [
        root / name
        for name in [
            "README.md",
            "AGENTS.md",
            "LICENSE",
            "CITATION.cff",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "THIRD_PARTY.md",
            "SECURITY.md",
            "MANIFEST.in",
            "pyproject.toml",
            "requirements.lock",
            "reference-requirements.lock",
            "run-local.cmd",
            "app.py",
            ".gitignore",
            ".gitattributes",
            "src/fem_solver/py.typed",
        ]
    ]
    for folder, pattern in [
        ("src/fem_solver", "*.py"),
        ("tests", "*.py"),
        ("scripts", "*.py"),
        ("docs", "*.md"),
        ("examples", "*.json"),
        ("examples", "*.csv"),
        ("data/bench", "*-template.*"),
        ("reports", "*.json"),
        ("reports", "*.csv"),
        ("reports", "*.png"),
        ("reports", "*.svg"),
        (".streamlit", "*.toml"),
        (".github", "*.yml"),
    ]:
        files.extend((root / folder).rglob(pattern))
    destination = root / "dist/Python-FEM-Structural-Solver-source.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            archive.write(path, "Python-FEM-Structural-Solver/" + path.relative_to(root).as_posix())
    print(
        f"Prepared {destination.name}: {len(set(files))} files, {destination.stat().st_size:,} bytes"
    )


if __name__ == "__main__":
    main()
