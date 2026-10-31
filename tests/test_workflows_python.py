"""Workflows written in Python, and rules read from files, on dryrun."""

import asyncio
import json

import pytest

from amoorion import Amoorion
from amoorion.core import AmoorionError
from amoorion.models import Message
from amoorion.utilities import post_from_markdown
from amoorion.workflows import EXECUTE, load_rules, log, step


@pytest.fixture
def amo():

    return Amoorion().use("dryrun")


def _message(
    number,
    text="deploy",
):

    return Message(
        platform="hook:generic",
        text=text,
        id=str(number),
    )


RULE = {
    "name": "deploys",
    "platform": "hook:generic",
    "contains": "deploy",
}


def test_serial_steps_log_and_leave_an_artifact(amo):

    @amo.workflow("news")
    def news(
        amo,
        inputs,
    ):

        @step
        def write():

            log("writing")

            return {"text": inputs["text"]}

        @step
        def send():

            return amo.publish(text="sent")[0]["ok"]

        return EXECUTE(
            write,
            send,
        ).serial()

    run = amo.perform(
        "news",
        {"text": "hello"},
    )

    assert run.ok and run.artifact == {"write": {"text": "hello"}}

    assert "writing" in run.logs and "send: done" in run.logs

    assert amo.workflows() == ["news"]


def test_serial_stops_at_the_first_failure(amo):

    called = []

    @amo.workflow("broken")
    def broken(
        amo,
        inputs,
    ):

        @step
        def first():

            raise ValueError("no way")

        @step
        def second():

            called.append(1)

        return EXECUTE(
            first,
            second,
        ).serial()

    run = amo.perform("broken")

    assert not run.ok and not called

    assert "first: failed: no way" in run.logs


@pytest.mark.parametrize("how", ["serial", "paralel"])
def test_async_steps(
    amo,
    how,
):

    @amo.workflow("both")
    async def both(
        amo,
        inputs,
    ):

        @step
        async def one():

            await asyncio.sleep(0)

            return 1

        @step
        def two():

            return 2

        return await getattr(EXECUTE(one, two), how)()

    run = amo.perform("both")

    assert run.ok and run.artifact == {"one": 1, "two": 2}


def test_perform_works_inside_a_running_loop(amo):

    @amo.workflow("inner")
    async def inner(
        amo,
        inputs,
    ):

        return {"done": True}

    async def outer():

        return amo.perform("inner")

    assert asyncio.run(outer()).artifact == {"done": True}


def test_a_workflow_raising_is_told_in_the_run(amo):

    @amo.workflow("raises")
    def raises(
        amo,
        inputs,
    ):

        raise RuntimeError("boom")

    run = amo.perform("raises")

    assert not run.ok and run.error == "boom"


def test_unknown_workflow(amo):

    with pytest.raises(AmoorionError):
        amo.perform("nope")


def test_run_saves_as_json(
    amo,
    tmp_path,
):

    @amo.workflow("saved")
    def saved(
        amo,
        inputs,
    ):

        return {"link": "x"}

    path = amo.perform("saved").save(tmp_path / "run.json")

    assert json.loads(path.read_text())["artifact"] == {"link": "x"}


def test_react_runs_once_per_message_and_retries_failures(amo):

    results = [
        False,
        True,
    ]

    seen = []

    @amo.workflow(
        "deploys",
        rules=[RULE],
    )
    def deploys(
        amo,
        inputs,
    ):

        seen.append(inputs["text"])

        return results.pop(0)

    amo.store.keep(
        [
            _message(1),
            _message(
                2,
                "other",
            ),
        ]
    )

    assert [run.ok for run in amo.react()] == [False]

    assert [run.ok for run in amo.react()] == [True]

    assert amo.react() == []

    assert seen == ["deploy", "deploy"]


def test_steps_of_a_rule_run_before_the_workflow(amo):

    steps = {
        "method": "publish",
        "params": {
            "text": "$text",
            "to": ["nowhere"],
        },
    }

    called = []

    @amo.workflow(
        "guarded",
        rules=[RULE | {"steps": [steps]}],
    )
    def guarded(
        amo,
        inputs,
    ):

        called.append(1)

    amo.store.keep([_message(1)])

    [run] = amo.react()

    assert not run.ok and not called and "publish" in run.error


def test_rules_from_a_file_and_a_directory(
    amo,
    tmp_path,
):

    (tmp_path / "a.rule.yml").write_text(
        "rules:\n  - {name: a, contains: deploy}\n"
    )

    (tmp_path / "b.rule.yml").write_text("- {name: b}\n")

    (tmp_path / "empty.rule.yml").write_text("")

    assert [rule.name for rule in load_rules(tmp_path)] == ["a", "b"]

    with pytest.raises(AmoorionError):
        load_rules(tmp_path / "none.yml")

    @amo.workflow(
        "filed",
        rules=tmp_path / "a.rule.yml",
    )
    def filed(
        amo,
        inputs,
    ):

        return {"from": inputs["id"]}

    amo.store.keep([_message(1)])

    assert amo.react()[0].artifact == {"from": "1"}


def test_method_needs_steps_or_rules_with_steps(amo):

    with pytest.raises(ValueError):
        amo.workflow()

    with pytest.raises(ValueError):
        amo.workflow(rules=[RULE])


def test_template_values_cant_reach_the_front_matter():

    post, to = post_from_markdown(
        "---\ntitle: $name\nto: [dryrun]\n---\nHello $name",
        {"name": "x\nto: [elsewhere]"},
    )

    assert to == ["dryrun"]

    assert post.title == "x\nto: [elsewhere]"

    assert post.text.endswith("[elsewhere]")
