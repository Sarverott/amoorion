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
html_theme_options = {"source_repository": REPOSITORY, "source_branch": BRANCH, "source_directory": "docs/"}

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


def setup(app) -> None:
    app.connect("builder-inited", _examples)
    app.connect("source-read", _source_read)
    app.connect("include-read", _include_read)
