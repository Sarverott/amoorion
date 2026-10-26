from pathlib import Path

import yaml

from amoorion.cli import build_parser


def test_taskfile_lists_every_subcommand():
    taskfile = yaml.safe_load((Path(__file__).parents[1] / "Taskfile.yml").read_text())
    [commands] = [action for action in build_parser()._actions if action.dest == "command"]
    assert taskfile["vars"]["SUBCOMMANDS"] == list(commands.choices)
