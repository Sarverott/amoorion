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
import re
import shutil
from pathlib import Path

from amoorion_dev import version as versions
from amoorion_dev.repo import Repo
from amoorion_dev.webpage.machines import for_machines, manifests
from amoorion_dev.webpage.page import first_paragraph, outward, page, render

# The graphics of resources/images, under the names the pages use.
GRAPHICS = {
    "wordmark.png": "Amoorion rose-gold gothic wordmark.png",
    "cupid.png": "Amoorion\u2019s Cupid Bot Sends Heart Messages-2-mini.png",
}


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
