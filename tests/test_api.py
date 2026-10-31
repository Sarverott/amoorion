import pytest
from fastapi.testclient import TestClient

from amoorion.api import create_app
from amoorion.methods import METHODS
from amoorion.vault import VaultLink, open_vault


@pytest.fixture
def client(monkeypatch):

    monkeypatch.setenv(
        "AMOORION_SECRET_API_TOKEN",
        "apitok",
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_HOOKS_GENERIC_TOKEN",
        "hooktok",
    )

    return TestClient(create_app(open_vault(VaultLink(kind="env"))))


AUTH = {"Authorization": "Bearer apitok"}


def test_index_lists_methods_and_hooks(client):

    body = client.get("/").json()

    assert "publish" in body["methods"] and "generic" in body["hooks"]


def test_every_method_says_what_it_answers(client):

    paths = client.get("/openapi.json").json()["paths"]

    for name in METHODS.names():
        answer = paths[f"/methods/{name}"]["post"]["responses"]["200"]

        schema = answer["content"]["application/json"]["schema"]

        assert {"$ref", "items", "anyOf"} & schema.keys(), name


def test_method_call(client):

    response = client.post(
        "/methods/publish",
        json={
            "text": "hi",
            "to": ["dryrun"],
        },
        headers=AUTH,
    )

    assert response.status_code == 200 and response.json()[0]["ok"]


def test_method_needs_token(client):

    assert client.post("/methods/plugins", json={}).status_code == 401

    assert (
        client.post(
            "/methods/plugins", json={}, headers={"Authorization": "Bearer x"}
        ).status_code
        == 401
    )


def test_methods_off_without_token_in_vault(monkeypatch):

    monkeypatch.delenv(
        "AMOORION_SECRET_API_TOKEN",
        raising=False,
    )

    client = TestClient(create_app(open_vault(VaultLink(kind="env"))))

    assert (
        client.post("/methods/plugins", json={}, headers=AUTH).status_code
        == 503
    )


def test_invalid_params(client):

    assert (
        client.post(
            "/methods/publish", json={"text": "hi", "to": []}, headers=AUTH
        ).status_code
        == 422
    )

    assert (
        client.post(
            "/methods/read", json={"platform": "nope"}, headers=AUTH
        ).status_code
        == 400
    )


def test_hook(client):

    ok = client.post(
        "/hooks/generic",
        json={"text": "built"},
        headers={"X-Amoorion-Token": "hooktok"},
    )

    assert ok.status_code == 200 and ok.json()["text"] == "built"

    assert client.post("/hooks/generic", json={"text": "x"}).status_code == 403

    assert client.post("/hooks/nope", json={}).status_code == 404
