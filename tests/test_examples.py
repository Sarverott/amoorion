"""Every notebook of examples/ still runs (they post nowhere: dryrun and fakes)."""

from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

EXAMPLES = Path(__file__).parents[1] / "examples"


@pytest.mark.parametrize(
    "path", sorted(EXAMPLES.glob("*.ipynb")), ids=lambda path: path.stem
)
def test_notebook_runs(
    path,
    monkeypatch,
):

    monkeypatch.delenv(
        "AMOORION_VAULT",
        raising=False,
    )

    notebook = nbformat.read(
        path,
        as_version=4,
    )

    NotebookClient(
        notebook,
        timeout=120,
        resources={"metadata": {"path": str(EXAMPLES)}},
    ).execute()


def test_there_are_examples():

    assert len(list(EXAMPLES.glob("*.ipynb"))) >= 4
