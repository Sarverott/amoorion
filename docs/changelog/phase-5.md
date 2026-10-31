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

## UNIXUSAT=1793412625813 · commit 7bf1882

The author, in their own words: "okidoki, let's play with form of code formating. look at
current state of code, you may notice unpresent state of tabs and idents. it is not wrong but
propably many people will find it \"unclean\" - for me it looks open and reading is faster this
way. if it is possible then set up that code autoformatter or linter (i'm not sure what ruff is)
to format not into standard shaping but our style... or at least as similar as possible. besides
that add more commentary a lot in the examples, some of inside source codes (this splitting into
multiline style was commenting-friendly strategy) and descriptional multiline stringings at heads
of classes and functions so it is more defined and selfexplanatory there. besides that i added
comment in lefthook about more stuff to be placed there. also we can consider to upgrade that
`.vscode` dir there so for example jupyter notebooks will be refreshed on their own by task or
louncher (i never used that before). also skills dir was updated long time ago i think. if it is
not a sin then maybe we can define amoorion additionally as agentic skill itself as additional
extra feacher?"

Ruff alone can't write that shape: it adds no blank lines, and splits only by width. So
`amoorion-dev shape` adds trailing commas and blank lines first (libcst) and ruff keeps them;
`task format` runs it, `task check` and a `pre-commit` hook hold it. Differences from the
author's hand: no blank line under `for`, `if` and the like, as ruff removes it; conditions stay
on one line; a trailing comma after the last item. Docstrings on all 420 classes and functions
that lacked one, kept by a test; the notebooks and scripts of `examples/` commented. lefthook also
lints YAML before a commit, runs the gate before a push of development and syncs after a pull.
`.vscode` has settings, tasks and launchers; `task examples:refresh` reruns notebooks, on demand and
not by itself, as their outputs change every run. `SKILL.md` brought up to date and installed with
the package, the `skill` method hands it out, `.claude-plugin/` makes the repository a plugin.

## UNIXUSAT=1793416209800 · commit ff73da2

The author's inquiry, word for word:

### to be added also in 7th phase
- docker releases on dockerhub with workflow
- docker and pip publishing on github as packages of container and python pack
- totp, hotp, oauth, webauthn, elliptic curves and segwit stuff - delegated access permissions (propably requires setternet as carrier of trust but that and other integrations will be in phase 9)
    - https://github.com/pyauth/pywarp
    - paramiko
    - pyotp
    - qr codes
- pure python adb package in use as user simulations with scrcpy, remote adb, gsm gateway for sms and phonecalls - also propably ressurectiong of qpython to change phone into fine suite for agents
- dependabot and rest of security/vurnability/dependency problems on github
- automation of publications announcements across all socialmedia platforms supported by amoorion with it's plugins


### to be added also in 8th phase
- colab google codes and google stuff integration like google calendar, sheets, docs, slides, forms, drive, youtube, translate, ads, google keep, analitics, contacts, maps, aistudio, gemini and bigquery
- mirror repository of project on gitlab, bitbucket, gitea and sr.ht - including automations like pipelines and else
- workflow for handling issues by dev scripts with you in charge - hooks, listeners, self-sufficiency, independency

### to be added also in 9th phase
- writting in docs in agents own area (docs/.agents) directory of "Almanah" with problems, obstacles, and accidental events—whether encountered in the past or anticipated in advance—along with their solutions, as well as key information on how to devise such solutions, the specific, atypical, or governed logic underlying these occurrences, and the probability of their potential manifestation at some point in the future, whether at a defined or an unspecified time.

## problems with documentation on Readthedocs

it throws this error right now

```
latexmk -r latexmkrc -pdf -f -dvi- -ps- -jobname=amoorion -interaction=nonstopmode
Use of uninitialized value in concatenation (.) or string at (eval 10) line 1.
Use of uninitialized value in concatenation (.) or string at (eval 10) line 2.
Use of uninitialized value in concatenation (.) or string at (eval 10) line 3.
Use of uninitialized value in concatenation (.) or string at (eval 10) line 4.
Latexmk: A user -r option asked me to process an rc file an extra time.
   Name of file = 'latexmkrc'
   Abs. path = '/home/docs/checkouts/amoorion/checkouts/latest/_readthedocs/pdf/latexmkrc'
  I'll not process it
Rc files read:
  /etc/LatexMk
  latexmkrc
Latexmk: This is Latexmk, John Collins, 31 Jan. 2024. Version 4.83.
No existing .aux file, so I'll make a simple one, and require run of *latex.
Latexmk: applying rule 'pdflatex'...
Rule 'pdflatex':  Reasons for rerun
Category 'other':
  Rerun of 'pdflatex' forced or previously required:
    Reason or flag: 'Initial setup'
------------
Run number 1 of rule 'pdflatex'
```

previous one releases of docs was stopped also by this issue

Phases 7 to 9 are planned in VISION.md. Read the Docs had failed on every build since v0.4.21.
Its PDF stopped there: that release was the first with outputs in the notebooks, whose rich tables
hold box drawing, and pdflatex gives up at its 100th unknown character, leaving no PDF. `docs/conf.py`
now draws them with `+ - |`; the README's SVG badges, which LaTeX can't embed either, stay out of the
PDF. `scripts/check-latex.py`, part of `task docs:build`, refuses both before they reach Read the Docs.
The PDF was compiled here by `latexmk` in `sphinxdoc/sphinx-latexpdf`: exit code 0, 258 pages. Doing so
found `python -m amoorion` starting the CLI on import, as the API reference imports every module; it
now runs only when run.
