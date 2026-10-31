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

## UNIXUSAT=1793429156670 · commit aeb2310

The author read the notebooks and wrote back inside them. Their words, word for word, cell by cell;
the plan drawn from them is in VISION.md (phase 5, point 6) and TODO.md.

### `examples/01-getting-started.ipynb`

Cell 2:

````text
# is there a jupyter presentable ploter like matplotlib for mermaid? or just matplotlib if it fits with some plotting
# or just pandas
````

Cell 4:

````text
# ugly
# wanna try prettyprint? 
import pprint
````

### `examples/02-config-and-setup.ipynb`

Cell 9:

````text
# create simple reader/writter of env files... aren't they just oversimplified forms of something between shell variables and ini file formating?
# honestly defining in the air env by os.env[] and inline string with newlines chars looks like impro teather - sory for harsh critical feedback but seriously i know you can better
````

### `examples/04-identity-vaults.ipynb`

Cell 8:

````text
# i want inputing commands with mentioned elsevere choosing with arrows menus
# after that i will provide all you need here
````

### `examples/05-cli-and-terminals.ipynb`

Cell 2:

````text
main(["plugins"]) # note that it can be defined in other way
# HEY! show me data like that with pandas table - leave this part, add below second one dedicated for notebook jupyter with pandas, how it looks like in comparition is good presentation of possibilities
````

Cell 3:

````text
# show me it with something like matplotlib or pandas, this way it is it is it is rough in my cognitive processing
````

Cell 6:

````text
# can we use something like that?:
output = None
Amoorion().cli.CALL()>"read"-"platform">"nowhere"[output] # set output of command as value of output variable 
#OR
Amoorion().cli.CALL()>"read"-"platform">"nowhere"(print) # prints out same as above calling of main
# because
# CALL functions returns special abstract class with operators overloading `CALL() == abstractor_call`
# after each calling of operator with argument like `(abstractor_call > "read") returns wraped abstractor_call`
# at end there we have confirm expression with output where to place abstractor_call[print] or abstractor_call(print) can callback own final output  into 
````

### `examples/06-getting-over-dataset.ipynb`

Cell 8:

````text
# here will be stored data about movement on socialmedia and library of all posts
# even drafts
# also links and graphs of related social personas etc.
# for quick movement we need vectorized database
# besides that this is place where we can place storylines of identities and profiles for LLMs to grow on that data like mashrooms on warm wet soil of old forest
# so knowledge also lands here in dataset
# dataset can use 
# - torrent, 
# - ipfs, 
# - ftp
# - S3 bucketing, 
# - hugging face, 
# - google drive, 
# - sshfs, 
# - ziparchive, 
# - git repository 
# all of them are our targeting
# try to write some example of above below this block 
````

### `examples/07-summoning-daemons.ipynb`

Cell 3:

````text
# i previously wrote somewhere about multiprocess + threades + asyncio etc. - here is more proper place for them i think
````

### `examples/09-how-to-use-packages.ipynb`

Cell 5:

````text
# keep simplicity at all cost - i like your style with that standarised methods there: `delete, post, read, reply`
# keep it simple but adhence the grouping of options: 
# - model -> create / delete / view / update / submodels{responses-reblogs-comments-reactions} / holder(supermodel){author-identity-profile} / flags{viev_by_user_Q-is_hidden-is_private-type_booleans}
# - post is content type that extends model
# - holder extends model as supermodel
# - user OR bot is holder -> name, id, description, avatar, mail, internal_personificational_data, creds
# - comment is submodel of post
# - reaction is submodel of post
# - holder can follow other holders and can be followed by other holders - vector of id from-to in graph of platform
# - supermodel can live on more than one plain of socialmedia - shared context of profiled identity
````

### `examples/10-webapp-interfacing.ipynb`

Cell 2:

````text
# what in your opinion should have this app in webapp frontend interface Cleo?
# i think about something between chrome extension, obsidian editor plugin and maybe mobile webapp on capasitor?
````

### `examples/11-additional-utilities.ipynb`

Cell 8:

````text
# utilities... also known as helper functions
# most of simple pure python codes that handle things like processing of strings, hashing, encoding etc.
# should be functions among utilities
````

### `examples/12-rest-api.ipynb`

Cell 9:

````text
# can we be compatible with scalar by openapi production?
# can we harvert power of cosmos sdk blockchain, grpc and protobuf?
# i think we can
````

### `examples/13-mcp-in-action.ipynb`

Cell 5:

````text
# NOPE
# we will gonna follow official examples of mcp server creation
from mcp.server import MCPServer
mcp = MCPServer("Demo")  # this will be replaced with Amoorion name and version
@mcp.tool() # we need tools
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
@mcp.resource("greeting://{name}")  # we need resources
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"
````

Cell 6:

````text
# also we will create this kind of tooling for our simulated party
import asyncio
from mcp import Client
async def main() -> None:
    async with Client("http://localhost:8000/mcp") as client:
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(result.structured_content)  # {'result': 3}
asyncio.run(main())
````

### `examples/15-calling-procedures-by-methods.ipynb`

Cell 8:

````text
# only method can be subcommand or outside execution of shell - i saw that git command wrapping in dev pack
# try to use gitpython instead
# every subcommand or shell script or task running is method
# every heavy process of complicated stuff like page request, rest get, html2md or pdf parsing is also method
# ffmpeg, yt-download, ai graphics, usage of integrated programs like gimp, adb, chrome, firefox, blender or obs should also be a method 
````

### `examples/17-unified-inbox.ipynb`

Cell 1:

````text
# let's consider for that one webapp interface injection  - i know that ipython and pupeteer for example (or playwright) allows us to do that
````

### `examples/18-automation-workflowing.ipynb`

Cell 3:

````text
# amo.automate(rules=[rule])
"""
 YES for rules
 NO for amo.automate()
 use 
"""
@amo.workflow("workflowname", rules=[rule]) # draft v1
def workflow_name(amo, inputs):
    try:
        pass
    except Exception():
        return False
    return True
````

Cell 4:

````text
@amo.workflow("workflowname", rules=[rule]) # draft v2 variant A
def workflow_name(amo, inputs):
    '''one'''
    @step
    def first():
        '''one'''
        try:
            pass
        except Exception():
            return False
        return True
    @step
    def first():
        '''one'''
        try:
            pass
        except Exception():
            return False
        return True
    @step
    def first():
        '''one'''
        try:
            pass
        except Exception():
            return False
        return True
    return EXECUTE(first, third).serial()
````

Cell 5:

````text
@amo.workflow("workflowname", rules=[rule])  # draft v2 variant B
async def workflow_name(amo, inputs):
    '''one'''
    @step
    async def first():
        '''one'''
        try:
            pass
        except Exception():
            return False
        return True
    @step
    async def second():
        '''one'''
        try:
            pass
        except Exception():
            return False
        return True
    @step
    async def third():
        '''one'''
        try:
            pass
        except Exception():
            return False
        return True
    return await EXECUTE(third, first).paralel()
````

Cell 7:

````text
        {"method": "publish", "params": {"text": "$text", "to": ["nowhere"]}} # this can still be used with workflows i think
} 
````

Cell 9:

````text
# alright, so let's assum it that all rules are yaml files defined and readable
# output of workflow should have logs then
# and result can be artifact of json for example that can be passed to the sender of post on socialmedia
````

### `examples/19-trying-society-emulations.ipynb`

Cell 10:

````text
# i want here to use my set of biblical names for these personality forming
persona_schema = {
    # from bornday we have got zodiak, chinese zodiak, generation at now psychology, general sociology of times, numberological profile info
    # from death we have lifestyle profiling predictions, statistics of deseases, age mentality, aging factor in perspective (patience level), shorter life is more brave decisions
    born: [
        date.fromtimestamp(random.random())
        geocoords: [random.random(),random.random()]
    ],
    death:[
        date.fromtimestamp(random.random()),
         geocoords: [random.random(),random.random()]
    ]
    
    names: []
    sirnames:[]
    soulname:"..."
    ghostname:"..."
    devilname:"..."
    # from place of birth we can randomize first name, second name and third name - these i collect from necrologs an birth acts then statistical weighted average of propability lottery 
    # each name has own story descriptor - adding to full person summary
    # from place of death we can randomize 2 last names and coinflip whitch one is mother's 
    # also lifestory from-to we can now generate based on that
    # gender choice - coinflip with binary restriction
    # psychological trauma related with one's own gender and sexual confusion, stemming from environmental and genetic factors that present a certain probability of occurrence during puberty ==  random(1,10)^(coinflip+coinflip)/random(1,10)*random(1,10)
    # because why not...
    # every of people will also have random choosen from records of all biblical names for soulname, random person from history for ghostname and demonical or devil's title name from records of myths and legends
    # also random tarot lotery draw in every 6 hours to inspire destiny narrator AI agent that writing novel of person's life
    # wonderful dumb and simplistic masquerade of delusions for our society based on this i took here for us from human society
    # emotions can be driven by emotional drivers --- these are in block below
    # we generates person with lingual talker (small deepseek or quem), operational instructor (small instructional tooling llm in openclaw) and coder of logics that can only code their internal code and provide structurized json for both other
    # power of emotional coders is decided by narrator based on responses by grand 3 above and storyline that identity draws
    # since now chackrams AKA emotional drivers AKA 7 deadly sins will From time to time, they will immersively toss the character about and prompt a discourse regarding the decisions made by the "great trio" whenever they encounter the twists of fate conjured up by a narratorial entity.
    # sounds like solid engine for simulation of humanity...
    # we have to do this!
````

Cell 11:

````text
# emotional drivers can be some of below mentioned
```
W przeciwieństwie do generatywnych modeli AI (jak ChatGPT), które „wymyślają” tekst, te prostsze modele są analityczne i klasyfikacyjne – dostają tekst i przypisują mu konkretną kategorię, etykietę lub wartość liczbową.
Oto zestawienie najważniejszych i najpopularniejszych prostych modeli podzielonych na kategorie:
Klasyfikacja i Filtrowanie Tekstu
• Analiza sentymentu (Sentiment Analysis): Ocenia emocjonalny ton wypowiedzi. Najczęściej dzieli tekst na trzy kategorie: pozytywny, negatywny lub neutralny.
• Detekcja toksyczności i oflagowanych treści (Content Moderation / Toxicity Detection): Wykrywa mowę nienawiści, wulgaryzmy, przemoc czy spam. Służy do automatycznego moderowania komentarzy.
• Klasyfikacja intencji (Intent Classification): Rozpoznaje, czego chce użytkownik (np. w chatbotach bankowych decyduje, czy klient chce „sprawdzić saldo”, czy „zablokować kartę”).
Wyciąganie Informacji i Semantyka
• Rozpoznawanie encji nazwanych (NER - Named Entity Recognition): Wyłapuje z tekstu konkretne obiekty i przypisuje im kategorie, np. imiona ludzi, nazwy firm, daty, kwoty czy lokalizacje.
• Analiza semantyczna i podobieństwo tekstów (Semantic Similarity): Mierzy, jak bliskie znaczeniowo są dwa zdania (nawet jeśli używają zupełnie innych słów, np. „Jak naprawić koło?” i „Instrukcja zmiany opony”).
• Wykrywanie języka (Language Detection): Natychmiastowo rozpoznaje, w jakim języku (np. polskim, angielskim, hiszpańskim) został napisany dany tekst.
Tradycyjne Algorytmy (Co stoi pod maską?)
Te prostsze zadania bardzo często realizuje się za pomocą mniejszych, starszych architektur, które nie potrzebują potężnych kart graficznych:
• Modele typu BERT (np. RoBERTa, DistilBERT): Małe modele transformerowe, które świetnie "rozumieją" kontekst i są mistrzami w klasyfikacji oraz NER.
• Algorytmy statystyczne (TF-IDF, Naive Bayes, SVM): Klasyczne metody matematyczne. Nie wymagają sieci neuronowych, są błyskawiczne i idealnie sprawdzają się np. w filtrach antyspamowych.
Czy potrzebujesz tych modeli do konkretnego projektu programistycznego, czy chcesz po prostu porównać ich skuteczność i koszty z nowoczesnymi modelami generatywnymi?
```
````

### `examples/20-all-socialmedia-posting-from-one-script.ipynb` (new)

Cell 0:

````text
# sending to the world the news about newest release

- requires ngrok running
- workflow that react after webhook 
- determining standard template of release info
- checking available platforms with credentials
- listing types of approaches
- for each platform little shaffling of content
- for each platform another graphics
- for each platform another video
- all posts with linking of latest release link, latest package, latest documentation link
- 
````

Cell 1:

````text

### mechanics of hooks should be runned like that

from amoorion import Amoorion

#from amoorion.hooks import HOOKS

# 
amo = Amoorion()

#amo.listen() 
# todo in future: totp or hotp secreting
#amo.hook(HOOKS["github:webhook"].at(options))

amo.workflows() # draft, 

amo.on(HOOKS["category", "category"])

@HOOKS.listen(
    amo, # who listens
    "webhook",  # classed category of hook
    "github",  # registered sender type with format and schema of data that will come
    "secret's label" # identity label of profile
) # DRAFT: it has only hash of secret, when it gets it from call, it hashes and compare them
async def call_webhook(self, payload_by_shema, request_data, callback): # if webhook receives request and routing maches registered sender and condition of maching secret returns true this is executed
    callback(int(), "data")
    # for example another webhook without waiting
    # and another webhook with waiting
    return int() # errorcode

# asyncio + threading + multiprocessing + contextvars + sched ... i don't know actualy what would be better here

async def host():

    await Daemon(
        [*amo.listeners]
    ).run()


# above code is just conceptual, give it own flavor, this is brainstorm
````

Cell 2:

````text
@amo.workflow("hello-world")
def hello_world_posting(amo):
    try:
        for platform in PLUGINS:
            platform.send_post({
                identity_label, # for example sarverott on tumblr by oauth would be "OAUTH::tumblr.com::sarverott"
                post_title,
                post_content_template.fill(post_content_json OR post_content_dict),
                post_options # including type, flag switches, hashtags that if it is active on particular platform will check and replace inside content text of post if hashtagged word is in the text
            }) # returns list of link to post and diagnostical return dict like id, or timestamp
    except Exception():
        return False
    return True

````

### `src/amoorion/cli/view.py`

````text
# can we make it more interactive? like for example instead of input we can try arrow steering of context menu selection with enter as confirmation, shift as going back by stacking of context recurrentions calling, form mechanics and staff like loading screens
````

New files of the author: `resources/rulesets/world.rule.yml`, `resources/scopes/{input1,output1}.sheme.json`,
`resources/scopes/{input2,output2}.sheme.toml` (all empty for now), `resources/templates/hello.template.md`.
