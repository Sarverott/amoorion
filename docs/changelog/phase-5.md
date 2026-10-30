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
