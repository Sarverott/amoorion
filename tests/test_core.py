import pytest

from amoorion.core import AmoorionError, Controller, JsonView, Model, Registry


class Note(Model):
    text: str


class Thing(Controller):
    name = "thing"


def test_model_forbids_unknown_fields():

    with pytest.raises(ValueError):
        Note(
            text="a",
            other=1,
        )


def test_json_view_renders_one_and_many():

    view = JsonView()

    assert view.render(Note(text="a")) == {"text": "a"}

    assert view.render([Note(text="a"), Note(text="b")]) == [
        {"text": "a"},
        {"text": "b"},
    ]


def test_controller_answers_through_its_view():

    assert Thing().respond(Note(text="a")) == {"text": "a"}


def test_registry():

    registry = Registry("thing")

    registry.register(Thing)

    registry.register(Thing)  # same class again is fine

    assert registry.get("thing") is Thing

    assert "thing" in registry and registry.names() == ["thing"]

    with pytest.raises(AmoorionError):
        registry.get("other")


def test_registry_refuses_nameless_and_duplicates():

    registry = Registry("thing")

    registry.register(Thing)

    with pytest.raises(AmoorionError):
        registry.register(
            type(
                "Nameless",
                (Controller,),
                {},
            )
        )

    with pytest.raises(AmoorionError):
        registry.register(
            type(
                "Other",
                (Controller,),
                {"name": "thing"},
            )
        )
