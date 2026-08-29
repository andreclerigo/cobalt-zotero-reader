"""Validate local links in the static documentation site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class LinkParser(HTMLParser):
    def __init__(self, source: Path) -> None:
        super().__init__()
        self.source = source
        self.targets: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.targets.append(value)


def main() -> None:
    docs = Path(__file__).resolve().parents[1] / "docs"
    pages = sorted(docs.glob("*.html"))
    failures: list[str] = []
    for page in pages:
        parser = LinkParser(page)
        parser.feed(page.read_text(encoding="utf-8"))
        for target in parser.targets:
            if target.startswith(("#", "http:", "https:", "mailto:", "data:")):
                continue
            path = urlsplit(target).path
            if path and not (page.parent / path).resolve().exists():
                failures.append(f"{page.relative_to(docs)}: missing {target}")
    if not pages:
        failures.append("no HTML pages found")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"validated {len(pages)} HTML pages and their local links")


if __name__ == "__main__":
    main()
