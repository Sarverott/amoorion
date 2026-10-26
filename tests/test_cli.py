import json

import pytest

import amoorion
from amoorion.cli import main


def test_version_matches_project(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert capsys.readouterr().out.strip() == f"amoorion {amoorion.__version__}"


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "publish" in capsys.readouterr().out


def test_publish_as_json(capsys):
    assert main(["--json", "publish", "--text", "hello", "--to", "dryrun"]) == 0
    [result] = json.loads(capsys.readouterr().out)
    assert result["ok"] and result["message"]["text"] == "hello"


def test_plugins_as_table(capsys):
    assert main(["plugins"]) == 0
    assert "dryrun" in capsys.readouterr().out


def test_bad_params_fail_cleanly(capsys):
    assert main(["read", "--platform", "dryrun", "--limit", "0"]) == 1
    assert capsys.readouterr().err.startswith("amoorion:")
