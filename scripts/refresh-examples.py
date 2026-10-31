"""Run notebooks of examples/ and save their outputs into them: `task examples:refresh`.

They post nowhere (dryrun and fakes), so this is safe at any time. The paths and
times in the outputs change with every run: refresh when the examples change.
"""

import sys
from pathlib import Path

import nbformat
from amoorion_dev.shape import run as shape
from nbclient import NotebookClient

EXAMPLES = Path(__file__).parents[1] / "examples"


def refresh(path: Path) -> None:
    """Run one notebook from examples/ and write it back in the code's shape."""

    notebook = nbformat.read(
        path,
        as_version=4,
    )

    NotebookClient(
        notebook,
        timeout=120,
        resources={"metadata": {"path": str(EXAMPLES)}},
    ).execute()

    nbformat.write(
        notebook,
        path,
    )

    shape([path])


if __name__ == "__main__":
    for name in sys.argv[1:] or sorted(EXAMPLES.glob("*.ipynb")):
        print(name)

        refresh(Path(name).resolve())
