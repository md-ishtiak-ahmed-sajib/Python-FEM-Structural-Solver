"""Check local documentation links, home links and the complete root index."""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def links_from(path: Path, errors: list[str]) -> set[Path]:
    targets = set()
    content = path.read_text(encoding="utf-8")
    for match in LINK.finditer(content):
        raw = match.group(1).strip().strip("<>")
        url = urlsplit(raw)
        if url.scheme in ("http", "https", "mailto"):
            continue  # This check does not claim to verify external websites.
        if url.scheme or raw.startswith("/"):
            errors.append(f"{path.relative_to(ROOT)}: use a relative local link: {raw}")
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if not target.is_relative_to(ROOT):
            errors.append(f"{path.relative_to(ROOT)}: link leaves the repository: {raw}")
        elif not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target: {raw}")
        else:
            targets.add(target)
    return targets


def main() -> int:
    documents = sorted({*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md")})
    errors: list[str] = []
    graph = {path: links_from(path, errors) for path in documents}
    home = ROOT / "README.md"
    index = graph[home]
    for path in documents:
        if path == home:
            continue
        name = str(path.relative_to(ROOT))
        if path not in index:
            errors.append(f"{name}: missing from the root README index")
        if home not in graph[path]:
            errors.append(f"{name}: missing a link back to the root README")
        if path.is_relative_to(ROOT / "docs"):
            section = path.parent / "README.md"
            if path != section and section not in graph[path]:
                errors.append(f"{name}: missing a link to its folder guide")
            if path != section and path not in graph.get(section, set()):
                errors.append(f"{name}: missing from its folder guide")
    for error in errors:
        print(error)
    print(
        f"Checked {len(documents)} Markdown documents and their local links: {len(errors)} errors."
    )
    if not errors:
        print("Every document is indexed at the project home and links back to it.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
