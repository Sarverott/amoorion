"""amoorion: administration of chatting and communication platforms."""

from importlib.metadata import version

# From the installed package, so the docs, the API and `--version` never lag behind pyproject.toml.
__version__ = version("amoorion")


def main() -> int:
    """The `amoorion` command; imported here so that starting up stays light."""

    from amoorion.cli import main

    return main()


def __getattr__(name: str) -> object:
    """`Amoorion`, `Plug` and `Plugins` load only when asked for, not with every `import amoorion`."""

    # Not imported above: plugin packages import amoorion.plugins while amoorion itself loads.
    if name in ("Amoorion", "Plug", "Plugins"):
        from amoorion import app

        return getattr(
            app,
            name,
        )

    raise AttributeError(name)
