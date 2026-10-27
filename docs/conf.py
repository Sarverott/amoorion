"""Sphinx configuration of amoorion's docs (Read the Docs, `task docs:build`).

The pages are the Markdown in docs/ (MyST); the API reference is generated
from the code (autosummary); the examples are the notebooks of examples/,
copied in at build time and shown as they were saved, not run again.
"""

import os
import re
import shutil
from pathlib import Path

from amoorion import __version__

DOCS = Path(__file__).parent
ROOT = DOCS.parent
REPOSITORY = "https://github.com/Sarverott/amoorion"
# Links out of docs/ (to the code, the packages, LICENSE…) go to the repository.
BRANCH = os.environ.get("READTHEDOCS_GIT_IDENTIFIER", "master")

project = "amoorion"
author = "Sett Sarverott"
copyright = "2024–present, Sett Sarverott"
release = version = __version__

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.mermaid",
    "sphinx_llm.txt",
    "notfound.extension",
]
exclude_patterns = ["_build", ".agents", "Taskfile.yml", "README.md", "**/.ipynb_checkpoints"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3
myst_fence_as_directive = ["mermaid"]
# The README skips heading levels (## to ####), as GitHub allows.
suppress_warnings = ["myst.header"]
nb_execution_mode = "off"

# The docstrings use `single backticks` for code, as Markdown does.
default_role = "code"
autosummary_generate = True
autodoc_default_options = {"members": True, "show-inheritance": True}
autodoc_member_order = "bysource"
autodoc_typehints = "description"

html_theme = "furo"
html_title = f"amoorion {version}"
# The look of the presentation page and resources/images (docs/_static/amoorion.css).
GRAPHICS = ROOT / "resources" / "images"
html_logo = str(GRAPHICS / "Amoorion rose-gold gothic wordmark.png")
html_favicon = str(GRAPHICS / "Amoorion\u2019s Cupid Bot Sends Heart Messages-2-mini.png")
html_static_path = ["_static"]
# robots.txt at the root (Read the Docs serves it from the default version).
html_extra_path = ["_extra"]

# For machines: llms.txt (the index of pages) and the Markdown of every page
# (<page>.md) by sphinx-llm; Read the Docs also answers `Accept:
# text/markdown` by itself. The agent skill of skills/ goes to /skills/.
llms_txt_description = (
    "amoorion: one tool to publish, read and reply on chatting and communication platforms "
    "(Bluesky, Mastodon, X, Tumblr, Blogger, Facebook, Discord, Telegram, Matrix), with a CLI, "
    "an HTTP API and an MCP server; secrets from a vault. Agent skill: /skills/amoorion/SKILL.md"
)
llms_txt_full_build = True
llms_txt_suppress_unknown_node_warnings = True

# The 404 page, in the theme (sphinx-notfound-page).
notfound_context = {
    "title": "Not found",
    "body": (
        "<h1>Lost between platforms</h1>"
        "<p>This page isn't here: it may have moved, or never was. "
        "Start again from <a href='/'>the docs' front page</a>, or search them.</p>"
    ),
}
html_css_files = ["amoorion.css"]
_FONT = '"Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", sans-serif'
html_theme_options = {
    "source_repository": REPOSITORY,
    "source_branch": BRANCH,
    "source_directory": "docs/",
    "sidebar_hide_name": True,  # the logo is the name
    "light_css_variables": {
        "color-brand-primary": "#b3263c",
        "color-brand-content": "#b3263c",
        "color-brand-visited": "#8e3a4c",
        "color-admonition-background": "#fbf1ee",
        "font-stack": _FONT,
    },
    "dark_css_variables": {
        "color-brand-primary": "#e2a893",
        "color-brand-content": "#e14c62",
        "color-brand-visited": "#c98a7a",
        "color-background-primary": "#07090e",
        "color-background-secondary": "#0d101a",
        "color-background-hover": "#1a1220",
        "color-background-border": "#2a1c26",
        "color-sidebar-background": "#0a0c13",
        "color-foreground-primary": "#f2e9e4",
        "color-foreground-secondary": "#c9bbb5",
        "color-code-background": "#0d101a",
        "font-stack": _FONT,
    },
}

LINK = re.compile(r"(\]\()(?!https?:|mailto:|#)([^)\s]+)(\))")


def _outward(text: str, source: Path, placed: Path | None = None) -> str:
    """Relative Markdown links leaving docs/ become links to the repository.

    `source` is where the text really is, `placed` where Sphinx reads it
    (a copied notebook); links to pages are made relative to `placed`.
    """
    placed = placed or source

    def replace(match: re.Match[str]) -> str:
        path, _, anchor = match.group(2).partition("#")
        target = (source.parent / path).resolve()
        # Pages of docs/ stay links between pages; directories have no page.
        if not path or (target.is_relative_to(DOCS) and not target.is_dir()):
            if not path or placed == source:
                return match.group(0)
            url = os.path.relpath(target, placed.parent)
        else:
            kind = "tree" if target.is_dir() else "blob"
            url = f"{REPOSITORY}/{kind}/{BRANCH}/{target.relative_to(ROOT).as_posix()}"
        return f"{match.group(1)}{url}{'#' + anchor if anchor else ''}{match.group(3)}"

    return LINK.sub(replace, text)


def _source_read(app, docname: str, source: list[str]) -> None:
    placed = Path(app.env.doc2path(docname))
    real = ROOT / placed.relative_to(DOCS) if docname.startswith("examples/") else placed
    source[0] = _outward(source[0], real, placed)


def _include_read(app, relative_path: Path, parent_docname: str, content: list[str]) -> None:
    content[0] = _outward(content[0], DOCS / relative_path)


def _examples(app) -> None:
    """examples/*.ipynb into docs/examples/ (ignored by git), for the toctree."""
    target = DOCS / "examples"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir()
    for notebook in sorted((ROOT / "examples").glob("*.ipynb")):
        shutil.copy(notebook, target / notebook.name)


def _state(app) -> None:
    """docs/devlog/STATE.md (ignored by git): the state of development at this build.

    On Read the Docs it also asks GitHub and PyPI; local builds stay offline.
    """
    from amoorion_dev.repo import Repo
    from amoorion_dev.state import markdown, read

    online = os.environ.get("READTHEDOCS") == "True"
    (DOCS / "devlog" / "STATE.md").write_text(markdown(read(Repo(ROOT), online=online)))


def _skills(app, exception) -> None:
    """skills/ of the repository into the built site, as /skills/<name>/SKILL.md."""
    if exception is None and app.builder.format == "html":
        shutil.copytree(ROOT / "skills", Path(app.outdir) / "skills", dirs_exist_ok=True)


def setup(app) -> None:
    app.connect("build-finished", _skills)
    app.connect("builder-inited", _examples)
    app.connect("builder-inited", _state)
    app.connect("source-read", _source_read)
    app.connect("include-read", _include_read)
