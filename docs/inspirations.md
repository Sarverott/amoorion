# Inspirations

The projects the author proposed as references, each considered. Adding a package is
the last resort: first what amoorion already speaks (HTTP, MCP, hooks). "Tried" says
what really ran; everything else is untried against the real thing.

## Adopted

| Project | What it became | Tried |
| ------- | -------------- | ----- |
| [Ollama](https://github.com/ollama/ollama-python), [llama.cpp](https://github.com/abetlen/llama-cpp-python), [LiteLLM proxy](https://docs.litellm.ai/docs/proxy/quick_start), [OpenAI](https://developers.openai.com/api/reference/python), [Claude](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) | `compose`: one call to the chat completions API they all answer, no package for each | a fake server only; Ollama is installed here but has no model |
| [OASIS](https://github.com/camel-ai/oasis), [MiroFish-Offline](https://github.com/nikmcfly/MiroFish-Offline), [miroclaw](https://github.com/justinfinnn/miroclaw) | `simulate`: the idea, very small, written anew; no code taken (the last two are AGPL) | scripted and with a fake model |
| [Sentry](https://github.com/getsentry/sentry), [Plane](https://github.com/makeplane/plane) | the hooks `sentry` and `plane`, from their webhook docs | signed test calls, not the real services |
| [Wikipedia](https://github.com/goldsmith/Wikipedia) | `wiki`: Wikipedia's own REST API, needing no package | a fake answer |
| [ngrok](https://ngrok.com/download/python) | `open_tunnel`, for hooks to be reachable; `pip install ngrok` when wanted | a fake only; it needs an account |
| [Gradio](https://github.com/gradio-app/gradio), [Streamlit](https://github.com/streamlit/streamlit), [Hugging Face](https://huggingface.co/docs/huggingface_hub/index) | `examples/spaces/`: both apps, ready to be Spaces, on `dryrun` only | both ran locally; nothing uploaded |
| [Blender](https://docs.blender.org/api/current/info_quickstart.html), [GIMP](https://developer.gimp.org/resource/writing-a-plug-in/tutorial-python/), [OBS](https://github.com/obsproject/obs-studio/wiki/Getting-Started-With-OBS-Scripting), [ComfyUI](https://github.com/Comfy-Org/ComfyUI), [comfy-python-sdk](https://github.com/Comfy-Org/comfy-python-sdk), [comfy-api-proxy](https://github.com/Comfy-Org/comfy-api-proxy), [comfy-cli](https://github.com/Comfy-Org/comfy-cli) | `advanced-usecases/from-creative-tools/`: one file, standard library only, to post from their scripts through the API | against a real local server, not inside those programs |

## Reached through what exists

| Project | How | Tried |
| ------- | --- | ----- |
| [CrewAI](https://github.com/crewaiinc/crewai), [ADK](https://adk.dev/), [LangChain](https://github.com/langchain-ai/langchain), [nanobot](https://github.com/HKUDS/nanobot), [Dify](https://github.com/langgenius/dify) | agents and workflows can call amoorion's MCP server or its API (notebooks 12, 13) | the server, not from those frameworks |
| [Ansible](https://github.com/ansible/ansible) | a play can call `amoorion workflow`; deploying amoorion by it belongs to phase 6 | no |
| [TensorFlow](https://github.com/tensorflow/tensorflow), [PyTorch](https://github.com/pytorch/pytorch), [Keras](https://github.com/keras-team/keras), [Transformers](https://github.com/huggingface/transformers), [Ultralytics](https://github.com/ultralytics/ultralytics) | far too heavy as dependencies of a posting tool; a model of your own fits as `think` of `Society`, or behind `compose` | no |

## For later

| Project | Why later |
| ------- | --------- |
| [Podman](https://podman.io/get-started) | phase 6: the image and compose file are to work with it too |
| [Paramiko](https://www.paramiko.org/) | phase 6, or a step running something on another machine; a method that runs remote commands needs its own decision |
| [Chroma](https://docs.trychroma.com/docs/overview/getting-started), [MemPalace](https://github.com/MemPalace/mempalace) | searching the inbox by meaning, once `search` by text proves too little |
| [pure-python-adb](https://github.com/Swind/pure-python-adb) | a phone as a platform (SMS, notifications) would be a plugin of its own; it was last changed in 2024 |
| [Scrapy](https://github.com/scrapy/scrapy) | a source of posts for sites without an API; the first such site should decide it |
| [OpenBB](https://github.com/openbq-org/OpenBB), [OpenMontage](https://github.com/calesthio/OpenMontage) | sources of what to post (market data, video); they feed amoorion from outside and need nothing of it but the API |

## Not taken

| Project | Why |
| ------- | --- |
| [Sherlock](https://github.com/sherlock-project/sherlock) | it finds a person's accounts across sites by username: in a tool that also posts and reads, too easy to point at other people. Checking a handle of one's own is a small thing to add if wanted |
| [Ruff](https://github.com/astral-sh/ruff) | tried on `src` and `packages`: 30 findings, 22 of them class attributes that are constants here; not made part of `task check` for now |
