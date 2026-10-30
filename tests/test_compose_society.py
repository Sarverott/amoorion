"""compose, simulate and wiki, against fakes of what they ask."""

import pytest
import requests

from amoorion import Amoorion
from amoorion.core import AmoorionError
from amoorion.society import Persona, Society


class Answer:
    def __init__(self, body, status=200):
        self.body, self.status_code, self.ok, self.text = body, status, status < 400, str(body)

    def json(self):
        return self.body


@pytest.fixture
def amo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AMOORION_VAULT", "env")
    monkeypatch.setenv("AMOORION_INBOX", str(tmp_path / "inbox.sqlite3"))
    monkeypatch.setenv("AMOORION_DATASET", str(tmp_path / "dataset"))
    monkeypatch.setenv("AMOORION_SECRET_LLM_URL", "http://model.test/v1/")
    monkeypatch.setenv("AMOORION_SECRET_LLM_MODEL", "tiny")
    return Amoorion()


def test_compose_asks_the_chat_completions_api(amo, monkeypatch):
    asked = {}

    def post(url, json, headers, timeout):
        asked.update(url=url, json=json, headers=headers)
        return Answer({"choices": [{"message": {"content": " hello "}}]})

    monkeypatch.setattr(requests, "post", post)
    assert amo.compose(prompt="hi", system="be brief") == {"text": "hello", "model": "tiny"}
    assert asked["url"] == "http://model.test/v1/chat/completions"
    assert asked["json"]["messages"][0] == {"role": "system", "content": "be brief"}
    assert asked["headers"] == {}


def test_compose_sends_a_token_and_never_shows_it(amo, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_LLM_TOKEN", "sk-secret")
    sent = {}

    def fail(url, json, headers, timeout):
        sent.update(headers)
        raise requests.ConnectionError(f"failed with {headers}")

    monkeypatch.setattr(requests, "post", fail)
    with pytest.raises(AmoorionError) as error:
        amo.compose(prompt="hi")
    assert sent["Authorization"] == "Bearer sk-secret"
    assert "sk-secret" not in str(error.value)


@pytest.mark.parametrize("answer", [Answer({}, 500), Answer({"choices": []})])
def test_compose_says_when_the_model_gives_nothing(amo, monkeypatch, answer):
    monkeypatch.setattr(requests, "post", lambda *a, **k: answer)
    with pytest.raises(AmoorionError):
        amo.compose(prompt="hi")


def test_society_answers_each_other_and_stays_silent_when_asked():
    people = [Persona(name="a", stance="supportive"), Persona(name="b", stance="critical"), Persona(name="c", stance="silent")]
    said = Society(people).simulate("the plan", rounds=2)
    assert [m.author.handle for m in said] == ["a", "b", "a", "b"]
    assert said[1].text.startswith("@a ") and said[1].reply_to == said[0].id
    assert len({m.id for m in said}) == 4


def test_simulate_keeps_it_local_and_in_the_inbox(amo, monkeypatch):
    def nothing(*a, **k):
        raise AssertionError("a simulation reached out")

    monkeypatch.setattr(requests, "post", nothing)
    monkeypatch.setattr("amoorion.methods.base.open_plugin", nothing)
    people = [{"name": "a", "stance": "supportive"}, {"name": "b", "stance": "critical"}]
    said = amo.simulate(topic="x", personas=people, rounds=1, run="trial")
    assert len(said) == 2
    assert {m["platform"] for m in amo.inbox()} == {"society:trial"}


def test_simulate_by_a_model(amo, monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **k: Answer({"choices": [{"message": {"content": "thought"}}]}))
    people = [{"name": "a"}, {"name": "b"}]
    assert [m["text"] for m in amo.simulate(topic="x", personas=people, rounds=1, llm=True)] == ["thought", "thought"]


def test_wiki(amo, monkeypatch):
    asked = {}

    def get(url, headers, timeout):
        asked.update(url=url, headers=headers)
        return Answer({"title": "NATS", "extract": "A system.", "content_urls": {"desktop": {"page": "https://w/NATS"}}})

    monkeypatch.setattr(requests, "get", get)
    message = amo.wiki(title="NATS messaging", lang="en")
    assert message["text"] == "NATS: A system." and message["url"] == "https://w/NATS"
    assert asked["url"].endswith("/page/summary/NATS%20messaging") and "amoorion" in asked["headers"]["User-Agent"]
    monkeypatch.setattr(requests, "get", lambda *a, **k: Answer({}, 404))
    with pytest.raises(AmoorionError):
        amo.wiki(title="nothing")
    with pytest.raises(ValueError):
        amo.wiki(title="x", lang="evil.example/")


def test_a_deleted_post_can_be_found_again(amo):
    amo.use("dryrun")
    message = amo.publish(text="soon gone")[0]["message"]
    amo.snapshot()
    assert amo.delete(id=message["id"])["ok"]
    assert amo.dataset.find("dryrun", "default", message["id"]).text == "soon gone"
