import pytest

from amoorion.models import Account, Message, Post, Result


def test_post_needs_text():
    with pytest.raises(ValueError):
        Post(text="")


def test_message_with_author_round_trips():
    message = Message(platform="dryrun", text="hi", author=Account(platform="dryrun", handle="me"))
    assert Message.model_validate(message.model_dump()) == message


def test_result_of_failure():
    result = Result(platform="x", ok=False, error="no token")
    assert result.message is None
