"""amoorion: administration of chatting and communication platforms."""

from importlib.metadata import version

# From the installed package, so the docs, the API and `--version` never lag behind pyproject.toml.
__version__ = version("amoorion")


def main() -> int:
    from amoorion.cli import main

    return main()
