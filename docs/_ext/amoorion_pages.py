"""What the docs' build does around Sphinx: links leaving docs/, copied notebooks, the state page, llms.txt, skills."""

import os
import re
import shutil
from pathlib import Path

DOCS = Path(__file__).parent.parent
ROOT = DOCS.parent
REPOSITORY = "https://github.com/Sarverott/amoorion"
# Links out of docs/ (to the code, the packages, LICENSE…) go to the repository.
BRANCH = os.environ.get(
    "READTHEDOCS_GIT_IDENTIFIER",
    "master",
)
LATEST = "https://amoorion.readthedocs.io/en/latest/"
LINK = re.compile(r"(\]\()(?!https?:|mailto:|#)([^)\s]+)(\))")


def _outward(
    text: str,
    source: Path,
    placed: Path | None = None,
) -> str:
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

            url = os.path.relpath(
                target,
                placed.parent,
            )

        else:
            kind = "tree" if target.is_dir() else "blob"

            url = f"{REPOSITORY}/{kind}/{BRANCH}/{target.relative_to(ROOT).as_posix()}"

        return f"{match.group(1)}{url}{'#' + anchor if anchor else ''}{match.group(3)}"

    return LINK.sub(
        replace,
        text,
    )


def _source_read(
    app,
    docname: str,
    source: list[str],
) -> None:

    placed = Path(app.env.doc2path(docname))

    real = (
        ROOT / placed.relative_to(DOCS)
        if docname.startswith("examples/")
        else placed
    )

    source[0] = _outward(
        source[0],
        real,
        placed,
    )


def _include_read(
    app,
    relative_path: Path,
    parent_docname: str,
    content: list[str],
) -> None:

    content[0] = _outward(
        content[0],
        DOCS / relative_path,
    )


def _examples(app) -> None:
    """examples/*.ipynb into docs/examples/ (ignored by git), for the toctree."""

    target = DOCS / "examples"

    shutil.rmtree(
        target,
        ignore_errors=True,
    )

    target.mkdir()

    for notebook in sorted((ROOT / "examples").glob("*.ipynb")):
        shutil.copy(
            notebook,
            target / notebook.name,
        )


def _state(app) -> None:
    """docs/devlog/STATE.md (ignored by git): the state of development at this build.

    On Read the Docs it also asks GitHub and PyPI; local builds stay offline.
    """

    from amoorion_dev.repo import Repo

    from amoorion_dev.state import read

    from amoorion_dev.state_page import markdown

    online = os.environ.get("READTHEDOCS") == "True"

    (DOCS / "devlog" / "STATE.md").write_text(
        markdown(
            read(
                Repo(ROOT),
                online=online,
            )
        )
    )


def _llms_absolute(
    app,
    exception,
) -> None:
    """The links of llms.txt (and its nested ones) in full, to the latest docs in English.

    sphinx-llm writes them relative to the file, and Read the Docs also serves
    llms.txt at its root, where those paths don't exist.
    """

    if exception is not None or app.builder.format != "html":
        return

    out = Path(app.outdir)

    for file in out.rglob("llms*.txt"):
        folder = file.parent.relative_to(out).as_posix()

        prefix = LATEST if folder == "." else f"{LATEST}{folder}/"

        file.write_text(
            LINK.sub(
                lambda match: f"{match[1]}{prefix}{match[2]}{match[3]}",
                file.read_text(),
            )
        )


def _skills(
    app,
    exception,
) -> None:
    """skills/ of the repository into the built site, as /skills/<name>/SKILL.md."""

    if exception is None and app.builder.format == "html":
        shutil.copytree(
            ROOT / "skills",
            Path(app.outdir) / "skills",
            dirs_exist_ok=True,
        )


def setup(app) -> None:

    app.connect(
        "build-finished",
        _skills,
    )

    # After sphinx-llm has written them.
    app.connect(
        "build-finished",
        _llms_absolute,
        priority=900,
    )

    app.connect(
        "builder-inited",
        _examples,
    )

    app.connect(
        "builder-inited",
        _state,
    )

    app.connect(
        "source-read",
        _source_read,
    )

    app.connect(
        "include-read",
        _include_read,
    )
