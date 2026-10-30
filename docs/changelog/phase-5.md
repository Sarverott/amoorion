# Phase 5: linking

## The list of the phase, and the old notebooks

UNIXUSAT=1793372376697 · commit 9abd654

The author's words:

> that check there returns this: "This workflow run required approval but was not approved before it expired." - this can be first think to be repaired in phase 5, do all of our current step list for this phase then at next step after them change every name of jupyter notebook examples file from "<NAME>.ipynb" into "old.<NAME>.ipynb". we will gonna need list of examples to be presented - based on pseudocode written and descriptions try to implement functionalities i am gonna present this way. let's go!

**Check.** `check` runs on pull requests to development only: the flow's own
to master waited for an approval nobody gives, and the flow checks before merging.

**A 502 on the way.** GitHub answered 502 when the flow started the release
of v0.4.5, after the merge, leaving master untagged. The author noticed my
watcher waiting on it and halted it. The flow now tries five times; the next
push released v0.4.5 by itself.

**Hooks.** `github`, `gitlab` and `discord`, one module each.

**ntfy.** A plugin, and a target: the method `notify` sends to the platforms
of `AMOORION_NOTIFY`, and everything the hooks receive goes there too. That
variable is my reading of "notification target"; the rules of Q11 can replace it.

**NATS.** Off unless `AMOORION_NATS` names a server. Tested against a fake
client only; no server has been tried.

**E-mail.** `amoorion-email`: SMTP, IMAP, reply; Blogger shares its sending.

**Notebooks.** Renamed `old.<NAME>.ipynb`; they still run and build. The phase
stays open for the author's list of new examples.

## UNIXUSAT=1793386940114 · commit 3a8bd2b

The author's drafts: nineteen numbered notebooks in `examples/`, five empty
directories in `examples/advanced-usecases/`, pseudocode of a new way to use
amoorion (`Amoorion`, `Plugins`, `use`, `load`, `save`), and this inquiry. Asked
in the chat: "proposals are soft calls with only reference to figure it out, not
strict ordering - consider each of them". The empty notebooks were not valid
files and the pseudocode can't run yet, so the first commit gives the empty ones
a title and marks the drafted cells `skip-execution`, word for word.

## proposing examples related to projects refered by links below or used with company of mentioned packages

#### why not to try at least
- https://ngrok.com/download/python
- https://github.com/astral-sh/ruff
- https://github.com/camel-ai/oasis
- https://github.com/Swind/pure-python-adb
- https://docs.trychroma.com/docs/overview/getting-started
- https://github.com/goldsmith/Wikipedia
- https://podman.io/get-started
- https://docs.litellm.ai/docs/proxy/quick_start#quick-start---litellm-proxy--configyaml
- https://developers.openai.com/api/reference/python
- https://huggingface.co/docs/huggingface_hub/index
- https://www.paramiko.org/
- https://adk.dev/
- https://github.com/nikmcfly/MiroFish-Offline
- https://github.com/justinfinnn/miroclaw
- https://github.com/ollama/ollama-python
- https://github.com/abetlen/llama-cpp-python
- https://github.com/crewaiinc/crewai
- https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
- https://github.com/tensorflow/tensorflow
- https://github.com/huggingface/transformers
- https://github.com/langgenius/dify
- https://github.com/langchain-ai/langchain
- https://github.com/pytorch/pytorch
- https://github.com/openbq-org/OpenBB
- https://github.com/calesthio/OpenMontage
- https://github.com/ansible/ansible
- https://github.com/scrapy/scrapy
- https://github.com/keras-team/keras
- https://github.com/makeplane/plane
- https://github.com/MemPalace/mempalace
- https://github.com/getsentry/sentry
- https://github.com/HKUDS/nanobot

#### examples on huggingface as spaces
- https://github.com/streamlit/streamlit
- https://github.com/gradio-app/gradio

#### looks like usefull mechanics
- https://github.com/sherlock-project/sherlock
- https://github.com/Comfy-Org/comfy-python-sdk
- https://github.com/Comfy-Org/comfy-api-proxy
- https://github.com/Comfy-Org/comfy-cli
- https://docs.blender.org/api/current/info_quickstart.html
- https://developer.gimp.org/resource/writing-a-plug-in/tutorial-python/
- https://github.com/obsproject/obs-studio/wiki/Getting-Started-With-OBS-Scripting
- https://github.com/Comfy-Org/ComfyUI
- https://github.com/ultralytics/ultralytics

## UNIXUSAT=1793389417618 · commit bb6de5e

**The author's examples.** `Amoorion` and `Plugins` follow the pseudocode, with two
departures it needed: a `Plug` is a `str`, because `list(Plugins)` was to give names
while `for platform in Plugins` gives objects; and `dict(Plugins)` gives a named tuple,
as a set can't hold a dict. `amo.inbox()` is the method, so the store is `amo.store`.

New methods: `search`, `workflow`, `automate`, `compose`, `simulate`, `wiki`. New hooks:
`sentry`, `plane`. Nineteen notebooks and six use cases run in the tests; the
verdict on every link of the inquiry is `docs/inspirations.md`. Writing notebook 06 found
that `Dataset.find` crashed on a deleted post; fixed.

The last item of the phase stays open for the author to look at the examples, so the `Y`
release waits for them.

## UNIXUSAT=1793395763196 · commit f73e6c9

The author cut `methods/base.py` into one file per method and asked to finish it and to
bring the same shortness to the other `.py` files. The method files got their imports,
`all_params.py` (left empty by the author) lists the params of every method. Then the rest
was cut the same way, moving code and not changing what it does: `app` (plugs, states,
front-ends), `workflows` (rules), `dataset` (entry), `nats` (publish, service), `cli` (parser,
view), `plugins` (loading), `hooks` (generic), `amoorion-dev` (bump, remote, show, state_page,
webpage), the docs' hooks (`docs/_ext`), and what shapes a post's text in seven plugin packages
(`text.py`; the Discord webhook got its own file). Only the inbox's list and search, which
repeated each other, and the servers' table of the CLI were simplified. Tests and notebook 08
follow the new places; no test was removed.
