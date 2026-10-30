"""Asking a language model, through the API most of them speak: OpenAI's chat completions.

Ollama, llama.cpp's server, a LiteLLM proxy, vLLM, OpenAI, Claude and Hugging Face's
router all answer `POST <url>/chat/completions`, so one call covers them, without a
package for each. From the vault, entry `llm`:

    llm/url     e.g. http://localhost:11434/v1 for Ollama, https://api.openai.com/v1
    llm/model   e.g. llama3.2
    llm/token   optional: local servers need none
"""

import requests

from amoorion.core import AmoorionError, Model
from amoorion.vault import Vault

TIMEOUT = 300


class Composition(Model):
    text: str
    model: str


def _optional(vault: Vault, name: str) -> str | None:
    try:
        return vault.get(name)
    except AmoorionError:
        return None


def complete(prompt: str, vault: Vault, system: str | None = None, model: str | None = None) -> Composition:
    url = vault.get("llm/url").rstrip("/")
    model = model or vault.get("llm/model")
    token = _optional(vault, "llm/token")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    try:
        response = requests.post(
            f"{url}/chat/completions",
            json={"model": model, "messages": messages},
            headers={"Authorization": f"Bearer {token}"} if token else {},
            timeout=TIMEOUT,
        )
    except requests.RequestException as error:
        raise AmoorionError(f"the model at {url} can't be reached: {type(error).__name__}") from None
    if not response.ok:
        raise AmoorionError(f"the model at {url} answered {response.status_code}: {response.text[:200]}")
    try:
        return Composition(text=response.json()["choices"][0]["message"]["content"].strip(), model=model)
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise AmoorionError(f"the model at {url} gave no answer") from None
