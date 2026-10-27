"""The project's web page, built at every release into the github-pages branch (gh-pages.yml).

index.html: the presentation page, the build of amoorion-website
(`task site:website`), when given; else the project page. project.html:
what amoorion is (the README), how to install it, its platforms, links to
the docs, PyPI and GitHub. releases.html: CHANGELOG.md. examples/: the
marimo pages of the notebooks (`task examples:build`) and their index.
manifest.json lists what the site holds, site.webmanifest is for
browsers. The pages are styled after the presentation page and the
graphics of resources/. Links that leave the page go to the repository.
"""

import html
import json
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt

from amoorion_dev import version as versions
from amoorion_dev.repo import Repo

# After the presentation page (amoorion-website) and resources/: night, rose and gold.
FONTS = (
    "https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Cormorant+Garamond:wght@500;700"
    "&family=Plus+Jakarta+Sans:wght@400;600&display=swap"
)
STYLE = """
:root { --bg: #07090e; --fg: #f2e9e4; --muted: #b9a9a3; --line: rgba(226, 168, 147, 0.22);
  --rose: #e14c62; --gold: #e2a893; --card: #0d101a; }
* { box-sizing: border-box; }
body { margin: 0; background: radial-gradient(ellipse at top, #1a0f18 0%, var(--bg) 55%) fixed; color: var(--fg);
  font: 16px/1.65 "Plus Jakarta Sans", system-ui, -apple-system, sans-serif; }
main, header, footer { max-width: 56rem; margin: 0 auto; padding: 0 1rem; }
header { padding-top: 2.2rem; padding-bottom: 1.4rem; border-bottom: 1px solid var(--line); text-align: center; }
header img { max-width: min(30rem, 90%); height: auto; }
header p { color: var(--muted); margin: 0.3rem 0 1rem; }
h1, h2, h3 { font-family: "Cormorant Garamond", Georgia, serif; color: var(--gold); line-height: 1.2; }
h2 { font-size: 2rem; margin-top: 2.4rem; }
nav a { margin: 0 0.6rem; color: var(--gold); text-decoration: none; font-family: Cinzel, serif;
  font-size: 0.9rem; letter-spacing: 0.08em; }
nav a:hover { color: var(--rose); }
.version { display: inline-block; padding: 0.1rem 0.7rem; border: 1px solid var(--line); border-radius: 999px;
  font-size: 0.85rem; color: var(--gold); }
pre, code { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 0.9em; }
pre { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 0.9rem; overflow-x: auto; }
a { color: var(--rose); }
table { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
th, td { border-bottom: 1px solid var(--line); padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 0.9rem; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1.1rem;
  text-decoration: none; color: inherit; transition: border-color 0.2s, box-shadow 0.2s; }
.card:hover { border-color: rgba(225, 76, 98, 0.6); box-shadow: 0 0 20px rgba(225, 76, 98, 0.2); }
.card h3 { margin: 0 0 0.3rem; font-size: 1.3rem; }
.card p { margin: 0; color: var(--muted); font-size: 0.92rem; }
footer { color: var(--muted); font-size: 0.85rem; padding-top: 2rem; padding-bottom: 3rem;
  border-top: 1px solid var(--line); margin-top: 3rem; text-align: center; }
"""
# The graphics of resources/images, under the names the pages use.
GRAPHICS = {
    "wordmark.png": "Amoorion rose-gold gothic wordmark.png",
    "cupid.png": "Amoorion\u2019s Cupid Bot Sends Heart Messages-2-mini.png",
}

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


def build(repo: Repo, out: Path, examples: Path | None = None, website: Path | None = None) -> list[Path]:
    """The web page in `out`: the presentation page (the built amoorion-website) at its root when given,
    project.html (the README, the platforms), releases.html, examples/, and the manifest files."""
    settings = repo.settings().get("repository", {})
    slug = settings.get("slug", "Sarverott/amoorion")
    docs = settings.get("docs", "https://amoorion.readthedocs.io/")
    version = versions.current(repo)
    blob = f"https://github.com/{slug}/blob/{repo.settings().get('branches', {}).get('release', 'master')}"
    presentation = website is not None and (website / "index.html").is_file()
    home = "project.html" if presentation else "index.html"
    links = {
        "Home": "index.html",
        **({"Project": home} if presentation else {}),
        "Examples": "examples/index.html",
        "Releases": "releases.html",
        "Docs": docs,
        "PyPI": "https://pypi.org/project/amoorion/",
        "GitHub": f"https://github.com/{slug}",
    }
    shutil.rmtree(out, ignore_errors=True)
    if presentation:
        shutil.copytree(website, out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "graphics").mkdir(exist_ok=True)
    for name, source in GRAPHICS.items():
        if (repo.root / "resources" / "images" / source).is_file():
            shutil.copyfile(repo.root / "resources" / "images" / source, out / "graphics" / name)

    readme = repo.read("README.md")
    # The README's own title and badges are the page's header already.
    readme = re.sub(r"\A# amoorion\n.*?\n---\n", "", readme, flags=re.S)
    cards = []
    for package in sorted((repo.root / "packages").glob("*/README.md")):
        text = package.read_text()
        name = package.parent.name
        cards.append(
            f'<a class="card" href="{blob}/packages/{name}/README.md">'
            f"<h3>{html.escape(name)}</h3><p>{html.escape(first_paragraph(text))}</p></a>"
        )
    pages = []
    (out / "examples").mkdir(exist_ok=True)
    if examples and examples.is_dir():
        shutil.copytree(examples, out / "examples", dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.py", "__marimo__"))
        pages = sorted(p for p in (out / "examples").glob("*.html") if p.name != "index.html")
    titles = {p.name: p.stem.split("-", 1)[-1].replace("-", " ") for p in pages}
    example_cards = "".join(
        f'<a class="card" href="{p.name}"><h3>{html.escape(titles[p.name])}</h3><p>a marimo notebook</p></a>' for p in pages
    )
    body = (
        "<h2>Install</h2>\n<pre><code>pip install amoorion amoorion-bluesky   # the core and the platforms you use</code></pre>\n"
        + outward(render(readme), blob, ".")
        + '<h2>Platforms</h2>\n<div class="cards">' + "".join(cards) + "</div>\n"
        + ('<h2>Examples</h2>\n<p><a href="examples/index.html">Notebooks, run with marimo</a></p>\n' if pages else "")
    )
    written = [out / home, out / "releases.html", out / "examples" / "index.html"]
    written[0].write_text(page("amoorion", body, version, links))
    releases = outward(render(repo.read("CHANGELOG.md") or "No release yet."), blob, ".")
    written[1].write_text(page("amoorion releases", "<h2>Releases</h2>\n" + releases, version, links))
    listing = '<div class="cards">' + example_cards + "</div>" if pages else "<p>No examples built.</p>"
    written[2].write_text(page("amoorion examples", "<h2>Examples</h2>\n" + listing, version, links, root="../"))
    written += manifests(repo, out, version, slug, docs, pages)
    written += for_machines(out, version, links, slug, docs, pages)
    (out / ".nojekyll").write_text("")
    return written + pages


def manifests(repo: Repo, out: Path, version: str, slug: str, docs: str, examples: list[Path]) -> list[Path]:
    """manifest.json: what the site and the release hold, for machines; site.webmanifest: for browsers."""
    contents = {
        "name": "amoorion",
        "version": version,
        "repository": f"https://github.com/{slug}",
        "docs": docs,
        "packages": {package.name: package.version(repo) for package in versions.packages(repo)},
        "pages": sorted(str(path.relative_to(out)) for path in out.rglob("*.html")),
        "examples": [f"examples/{path.name}" for path in examples],
    }
    web = {
        "name": "amoorion",
        "short_name": "amoorion",
        "description": "Universal tool for administration of chatting and communication platforms",
        "start_url": "./",
        "display": "browser",
        "background_color": "#07090e",
        "theme_color": "#e14c62",
        "icons": [{"src": "graphics/cupid.png", "sizes": "512x512", "type": "image/png"}],
    }
    files = [out / "manifest.json", out / "site.webmanifest"]
    files[0].write_text(json.dumps(contents, indent=2) + "\n")
    files[1].write_text(json.dumps(web, indent=2) + "\n")
    return files


def for_machines(out: Path, version: str, links: dict[str, str], slug: str, docs: str, examples: list[Path]) -> list[Path]:
    """404.html (GitHub Pages shows it for any missing page), robots.txt and llms.txt."""
    base = f"https://{slug.split('/')[0].lower()}.github.io/{slug.split('/')[1]}/"
    lost = (
        "<h2>Lost between platforms</h2>\n<p>This page isn't here: it may have moved, or never was.</p>\n"
        f'<p><a href="{base}">Back to the start</a>, or read <a href="{docs}">the docs</a>.</p>\n'
    )
    # Absolute links: GitHub Pages serves 404.html at whatever path was asked for.
    absolute = {name: url if ":" in url else base + url for name, url in links.items()}
    files = [out / "404.html", out / "robots.txt", out / "llms.txt"]
    files[0].write_text(page("amoorion: not found", lost, version, absolute, root=base))
    files[1].write_text(f"User-agent: *\nAllow: /\n\n# The docs keep their own: {docs}robots.txt\n")
    entries = "\n".join(f"- [{path.stem.split('-', 1)[-1].replace('-', ' ')}]({base}examples/{path.name})" for path in examples)
    files[2].write_text(
        f"# amoorion\n\n> Universal tool for administration of chatting and communication platforms: publish, "
        f"read and reply on many platforms from one CLI, HTTP API or MCP server. Version {version}.\n\n"
        f"## Docs\n\n- [Documentation, as an index for agents]({docs}llms.txt)\n"
        f"- [Agent skill]({docs}skills/amoorion/SKILL.md)\n\n"
        f"## This site\n\n- [Project]({base}project.html)\n- [Releases]({base}releases.html)\n"
        f"- [What the site holds]({base}manifest.json)\n"
        + (f"\n## Examples (marimo)\n\n{entries}\n" if entries else "")
        + f"\n## Code\n\n- [GitHub](https://github.com/{slug})\n- [PyPI](https://pypi.org/project/amoorion/)\n"
    )
    return files
