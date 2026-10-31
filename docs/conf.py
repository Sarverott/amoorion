"""Sphinx configuration of amoorion's docs (Read the Docs, `task docs:build`).

The pages are the Markdown in docs/ (MyST); the API reference is generated
from the code (autosummary); the examples are the notebooks of examples/,
copied in at build time and shown as they were saved, not run again
(docs/_ext/amoorion_pages.py).
"""

import sys
import unicodedata
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent / "_ext"),
)

from amoorion_pages import BRANCH, REPOSITORY, ROOT, setup  # noqa: E402, F401 - Sphinx calls `setup`

from amoorion import __version__  # noqa: E402

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
exclude_patterns = [
    "_build",
    ".agents",
    "Taskfile.yml",
    "README.md",
    "**/.ipynb_checkpoints",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3
myst_fence_as_directive = ["mermaid"]
# The README skips heading levels (## to ####), as GitHub allows.
suppress_warnings = ["myst.header"]
nb_execution_mode = "off"

# The docstrings use `single backticks` for code, as Markdown does.
default_role = "code"
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"
autodoc_typehints = "description"

html_theme = "furo"
html_title = f"amoorion {version}"
# The look of the presentation page and resources/images (docs/_static/amoorion.css).
GRAPHICS = ROOT / "resources" / "images"
html_logo = str(GRAPHICS / "Amoorion rose-gold gothic wordmark.png")
html_favicon = str(
    GRAPHICS / "Amoorion\u2019s Cupid Bot Sends Heart Messages-2-mini.png"
)
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

# The PDF of Read the Docs is made by pdflatex, which knows no box drawing, and
# stops after 100 errors with no PDF at all. Rich's tables in the outputs of the
# notebooks are full of it, so they are drawn with + - | there.
# `task docs:check:latex` tells of any other character it wouldn't know.


def _ascii_box(code: int) -> str:
    """What stands for one box drawing character: a line stays a line, the rest is a joint."""

    name = unicodedata.name(chr(code))

    if "HORIZONTAL" in name and "VERTICAL" not in name and "AND" not in name:
        return "-"

    if "VERTICAL" in name and "HORIZONTAL" not in name and "AND" not in name:
        return "|"

    return "+"


latex_elements = {
    "preamble": "\n".join(
        f"\\DeclareUnicodeCharacter{{{code:04X}}}{{{_ascii_box(code)}}}"
        for code in range(0x2500, 0x2580)
    ),
}
