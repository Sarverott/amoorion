# Phase 4: documentation, examples, releases

Append-only.

## UNIXUSAT=1793054132742 · commit 340b67d

The author's first inquiry (docs/devlog/INQUIRIES.md), word for word:

````markdown
### inquiry

> for clearify whole we have done here for users we need to improove our docs. i initialized project in readthedocs and placed some stuff there.
> we want to make it be genetared from markdown we will gona place in "docs/" with partial autonomous generation of docs based on code for code
> referencing. besides that we need to present some examples of usage in "examples/" written in jupyter notebooks files. we need also to write
> script with marimo generated builds of examples that will be .gitignored by "examples/.gitignore". add also workflow for publishing git package
> and pypi package at release been created. releases should be generated at pull request megre or push to master. begin draft of plan first based on
> this message for phase 4 (current 4->5 and 5->6 now) then realize the steps
````

It opens a new phase 4; linking becomes phase 5 and deployment phase 6.
Where earlier entries say "phase 4" (rules on the inbox, Q11) or "phase 5"
(deployment), they mean phases 5 and 6 now. The plan drawn from it is in
VISION.md (phase 4) and TODO.md.

## UNIXUSAT=1793054962845 · commit d947a88

The inquiry carried out. The author's Read the Docs start works: the docs
are a Sphinx site from the Markdown in `docs/` (MyST), with the README,
the platforms' READMEs, the guides, the plan and this changelog as pages and
an API reference generated from the code; `task docs:build` builds it with
warnings as errors inside `task check`. Four Jupyter notebooks in
`examples/` (first steps, vault and accounts, API with hooks and inbox, an
own plugin) run in the tests and show in the docs; `task examples:build`
makes marimo builds of them into the ignored `examples/build/`. A push to
`master` releases: commitizen bumps every package to one version, tags it
and makes a GitHub release, whose packages are attached to it and published
to PyPI. Not run for real yet: the workflows and Read the Docs. Q15 opened.
INQUIRIES.md joins the devlog.
