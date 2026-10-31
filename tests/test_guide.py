"""The guided CLI, answered from a script instead of a keyboard."""

import io

from rich.console import Console

from amoorion.cli.guide import Guide


def guide(answers: str) -> tuple[Guide, io.StringIO]:

    out = io.StringIO()

    return Guide(
        Console(file=out, width=120, force_terminal=False), io.StringIO(answers)
    ), out


def test_publish_step_by_step_after_confirming():

    g, out = guide("publish\nhello from the guide\n\n\n\ndryrun\ny\nn\n")

    assert g.run() == 0

    text = out.getvalue()

    assert "platforms that can publish:" in text and "dryrun" in text

    assert "yes" in text  # the result's ok, as a cell


def test_declining_runs_nothing(monkeypatch):

    from amoorion.plugins.dryrun import DryRun

    before = len(DryRun._messages)

    g, out = guide("publish\nnot sent\n\n\n\ndryrun\nn\nn\n")

    g.run()

    assert len(DryRun._messages) == before


def test_read_only_methods_need_no_confirmation_and_q_quits():

    g, out = guide("plugins\nn\n")

    assert g.run() == 0 and "dryrun" in out.getvalue()

    g, out = guide("nonsense\nq\n")

    assert g.run() == 0 and "no method 'nonsense'" in out.getvalue()


def test_platforms_are_offered_by_capability():

    g, _ = guide("")

    assert "dryrun" in g.platforms("reply")

    assert "discord-webhook" in g.platforms(
        "publish"
    ) and "discord-webhook" not in g.platforms("read")


def test_the_end_of_the_answers_ends_the_guide():

    g, _ = guide("publish\nunfinished")

    assert g.run() == 0
