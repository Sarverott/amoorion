"""Workflows, rules and the search of the inbox, on dryrun."""

import pytest

from amoorion import Amoorion
from amoorion.models import Account, Message
from amoorion.workflows import Rule, Step, fill, matches


@pytest.fixture
def amo(
    tmp_path,
    monkeypatch,
):

    monkeypatch.chdir(tmp_path)

    monkeypatch.setenv(
        "AMOORION_VAULT",
        "env",
    )

    monkeypatch.setenv(
        "AMOORION_INBOX",
        str(tmp_path / "inbox.sqlite3"),
    )

    monkeypatch.setenv(
        "AMOORION_DATASET",
        str(tmp_path / "dataset"),
    )

    return Amoorion().use("dryrun")


def test_fill_only_puts_text_in():

    assert fill({"a": ["$x", 1], "b": "$unknown $$"}, {"x": "${y}"}) == {
        "a": ["${y}", 1],
        "b": "$unknown $",
    }


def test_workflow_passes_what_was_said_on(amo):

    results = amo.workflow(
        steps=[
            {
                "method": "publish",
                "params": {
                    "text": "first",
                    "to": ["dryrun"],
                },
            },
            {
                "method": "publish",
                "params": {
                    "text": "again: $last",
                    "to": ["dryrun"],
                },
            },
        ]
    )

    assert [step["ok"] for step in results] == [True, True]

    assert results[1]["result"][0]["message"]["text"] == "again: first"


def test_workflow_stops_at_the_first_failure(amo):

    results = amo.workflow(
        steps=[
            {
                "method": "publish",
                "params": {
                    "text": "x",
                    "to": ["nowhere"],
                },
            },
            {
                "method": "publish",
                "params": {
                    "text": "never",
                    "to": ["dryrun"],
                },
            },
        ]
    )

    assert (
        len(results) == 1
        and results[0]["ok"] is False
        and "nowhere" in results[0]["error"]
    )


@pytest.mark.parametrize("name", ["workflow", "automate"])
def test_steps_cant_start_more_steps(
    amo,
    name,
):

    [result] = amo.workflow(
        steps=[
            {
                "method": name,
                "params": {},
            }
        ]
    )

    assert result["ok"] is False and "can't" in result["error"]


def test_unknown_method_and_bad_params_fail_as_a_step(amo):

    assert amo.workflow(steps=[{"method": "nope"}])[0]["ok"] is False

    assert (
        amo.workflow(
            steps=[{"method": "publish", "params": {"to": ["dryrun"]}}]
        )[0]["ok"]
        is False
    )


def test_rules_match():

    message = Message(
        platform="hook:github",
        text="Release v1",
        author=Account(
            platform="hook:github",
            handle="a",
        ),
    )

    assert matches(
        Rule(name="r", steps=[Step(method="x")], contains="release"), message
    )

    assert not matches(
        Rule(name="r", steps=[Step(method="x")], platform="hook:gitlab"),
        message,
    )


def test_a_rule_acts_once_per_message(amo):

    amo.store.keep(
        [
            Message(
                platform="hook:generic",
                text="deploy done",
                id="1",
            ),
            Message(
                platform="hook:generic",
                text="other",
                id="2",
            ),
        ]
    )

    rule = {
        "name": "announce",
        "platform": "hook:generic",
        "contains": "deploy",
        "steps": [
            {
                "method": "publish",
                "params": {
                    "text": "news: $text from $platform",
                    "to": ["dryrun"],
                },
            }
        ],
    }

    [done] = amo.automate(rules=[rule])

    assert (
        done["rule"] == "announce" and done["message_id"] == "1" and done["ok"]
    )

    assert (
        done["steps"][0]["result"][0]["message"]["text"]
        == "news: deploy done from hook:generic"
    )

    assert amo.automate(rules=[rule]) == []


def test_a_failed_rule_is_tried_again(amo):

    amo.store.keep(
        [
            Message(
                platform="hook:generic",
                text="x",
                id="1",
            )
        ]
    )

    rule = {
        "name": "r",
        "steps": [
            {
                "method": "publish",
                "params": {
                    "text": "$text",
                    "to": ["nowhere"],
                },
            }
        ],
    }

    assert amo.automate(rules=[rule])[0]["ok"] is False

    assert amo.automate(rules=[rule])[0]["ok"] is False


def test_search_finds_text_of_any_case_and_escapes(amo):

    amo.store.keep(
        [
            Message(
                platform="a",
                text="Hello World",
                id="1",
            ),
            Message(
                platform="b",
                text="100% sure",
                id="2",
            ),
            Message(
                platform="b",
                text="1000 sure",
                id="3",
            ),
        ]
    )

    assert [m["id"] for m in amo.search(text="hello")] == ["1"]

    assert [m["id"] for m in amo.search(text="100%")] == ["2"]

    assert amo.search(text="hello", platform="b") == []
