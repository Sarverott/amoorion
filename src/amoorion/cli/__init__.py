"""Command line: one subcommand per method, plus the servers."""

from amoorion.cli.base import main
from amoorion.cli.parser import build_parser
from amoorion.cli.view import RichView

__all__ = ["RichView", "build_parser", "main"]
