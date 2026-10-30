"""One page of the site: Markdown rendered, its links, the frame around it."""

import html
import re
from pathlib import Path

from markdown_it import MarkdownIt

from amoorion_dev.webpage.style import FONTS, STYLE

LINK = re.compile(r'(href|src)="(?!https?:|mailto:|#)([^"]+)"')


def render(markdown: str) -> str:
    return MarkdownIt("commonmark").enable("table").enable("strikethrough").render(markdown)


def outward(page: str, base: str, here: str) -> str:
    """Relative links of a Markdown file in `here` (relative to the root) go to the repository."""

    def replace(match: re.Match[str]) -> str:
        target = (Path(here) / match.group(2)).as_posix()
        parts: list[str] = []
        for part in target.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        return f'{match.group(1)}="{base}/{"/".join(parts)}"'

    return LINK.sub(replace, page)


def first_paragraph(markdown: str) -> str:
    paragraphs = [part.strip() for part in markdown.split("\n\n") if part.strip() and not part.startswith("#")]
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", paragraphs[0]).replace("\n", " ") if paragraphs else ""


def page(title: str, body: str, version: str, links: dict[str, str], root: str = "") -> str:
    """A page of the site; `root` leads from it to the site's root ("" or "../")."""
    nav = "".join(
        f'<a href="{html.escape(url if ":" in url else root + url)}">{html.escape(name)}</a>' for name, url in links.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="{root}graphics/cupid.png">
<link rel="manifest" href="{root}site.webmanifest">
<link href="{FONTS}" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>
<header>
<a href="{root}index.html"><img src="{root}graphics/wordmark.png" alt="amoorion"></a>
<p>Universal tool for administration of chatting and communication platforms
<span class="version">v{html.escape(version)}</span></p>
<nav>{nav}</nav>
</header>
<main>
{body}
</main>
<footer>MIT License, © 2024–present Sett Sarverott. Built from the repository at v{html.escape(version)}.</footer>
</body>
</html>
"""
