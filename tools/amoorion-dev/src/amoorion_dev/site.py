"""The project's web page, built at every release into the github-pages branch (gh-pages.yml).

index.html: what amoorion is (the README), how to install it, its
platforms, the examples, links to the docs, PyPI and GitHub.
releases.html: CHANGELOG.md. examples/: the marimo pages of the notebooks,
when `task examples:build` made them. Links that leave the page go to the
repository.
"""

import html
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt

from amoorion_dev import version as versions
from amoorion_dev.repo import Repo

STYLE = """
:root { --bg: #fbfaf7; --fg: #1d1b19; --muted: #6b655e; --line: #e3ded6; --accent: #b3261e; --card: #ffffff; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #151413; --fg: #ece8e2; --muted: #a39c93; --line: #2f2c29; --accent: #ef6b5f; --card: #1d1b19; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }
main, header, footer { max-width: 54rem; margin: 0 auto; padding: 0 1rem; }
header { padding-top: 3rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--line); }
header h1 { font-size: 2.6rem; margin: 0; letter-spacing: -0.02em; }
header p { color: var(--muted); margin: 0.3rem 0 1rem; }
nav a { margin-right: 1.2rem; color: var(--accent); text-decoration: none; font-weight: 600; }
.version { display: inline-block; padding: 0.1rem 0.6rem; border: 1px solid var(--line); border-radius: 999px;
  font-size: 0.85rem; color: var(--muted); }
pre, code { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 0.9em; }
pre { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 0.9rem; overflow-x: auto; }
a { color: var(--accent); }
table { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
th, td { border-bottom: 1px solid var(--line); padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 0.8rem; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 0.9rem 1rem; }
.card h3 { margin: 0 0 0.3rem; font-size: 1.05rem; }
.card p { margin: 0; color: var(--muted); font-size: 0.92rem; }
footer { color: var(--muted); font-size: 0.85rem; padding-top: 2rem; padding-bottom: 3rem;
  border-top: 1px solid var(--line); margin-top: 3rem; }
"""

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


def page(title: str, body: str, version: str, links: dict[str, str]) -> str:
    nav = "".join(f'<a href="{html.escape(url)}">{html.escape(name)}</a>' for name, url in links.items())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<header>
<h1>amoorion</h1>
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


def build(repo: Repo, out: Path, examples: Path | None = None) -> list[Path]:
    settings = repo.settings().get("repository", {})
    slug = settings.get("slug", "Sarverott/amoorion")
    docs = settings.get("docs", "https://amoorion.readthedocs.io/")
    version = versions.current(repo)
    blob = f"https://github.com/{slug}/blob/{repo.settings().get('branches', {}).get('release', 'master')}"
    links = {
        "Home": "index.html",
        "Releases": "releases.html",
        "Docs": docs,
        "PyPI": "https://pypi.org/project/amoorion/",
        "GitHub": f"https://github.com/{slug}",
    }
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)

    readme = repo.read("README.md")
    # The README's own title and banner are the page's header already.
    readme = re.sub(r"\A# amoorion\n.*?\n---\n", "", readme, flags=re.S)
    cards = []
    for package in sorted((repo.root / "packages").glob("*/README.md")):
        text = package.read_text()
        name = package.parent.name
        cards.append(
            f'<a class="card" href="{blob}/packages/{name}/README.md" style="text-decoration:none;color:inherit">'
            f"<h3>{html.escape(name)}</h3><p>{html.escape(first_paragraph(text))}</p></a>"
        )
    pages = []
    if examples and examples.is_dir():
        shutil.copytree(examples, out / "examples", ignore=shutil.ignore_patterns("*.py", "__marimo__"))
        pages = sorted((out / "examples").glob("*.html"))
    example_list = "".join(
        f'<li><a href="examples/{p.name}">{html.escape(p.stem.split("-", 1)[-1].replace("-", " "))}</a></li>'
        for p in pages
    )
    body = (
        "<h2>Install</h2>\n<pre><code>pip install amoorion amoorion-bluesky   # the core and the platforms you use</code></pre>\n"
        + outward(render(readme), blob, ".")
        + "<h2>Platforms</h2>\n<div class=\"cards\">" + "".join(cards) + "</div>\n"
        + ("<h2>Examples</h2>\n<p>Notebooks, run with marimo:</p>\n<ul>" + example_list + "</ul>\n" if pages else "")
    )
    written = [out / "index.html", out / "releases.html"]
    written[0].write_text(page("amoorion", body, version, links))
    releases = outward(render(repo.read("CHANGELOG.md") or "No release yet."), blob, ".")
    written[1].write_text(page("amoorion releases", "<h2>Releases</h2>\n" + releases, version, links))
    (out / ".nojekyll").write_text("")
    return written + pages
