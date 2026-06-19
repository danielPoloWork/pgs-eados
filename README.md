# Enterprise Agentic Architecture Orchestrator (EAAO)

[![CI](https://github.com/danielPoloWork/pgs-eaao/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eaao/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](.eaao-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> **🌐 Translations:** [简体中文](docs/i18n/zh-Hans/README.md) · [日本語](docs/i18n/ja/README.md) — derived from this English source. Policy & freshness: [`docs/i18n/`](docs/i18n/README.md).

> A language-agnostic meta-project that reproduces the **enterprise agent system** of
> `pbr-cpp-memory-pool` for *any* new project, in *any* language, with *any* toolchain —
> by interviewing the maintainer, recording the answers in a single manifest, and
> rendering a complete, governed repository from parameterized templates.

EAAO is not the product. EAAO is the **factory** that stamps out products that all
share the same technical-enterprise structure, the same GitHub workflow, the same
quality gates, and the same AI-agent contract — regardless of programming language,
framework, or tooling.

It exists to answer one question:

> *"We built `pbr-cpp-memory-pool` to an enterprise bar — agents, ADRs, CI matrix,
> consistency lint, SemVer governance. How do we get the **same** rigor on the next
> project, which is in Rust / Python / TypeScript / Go / Java / …?"*

The answer: point the **Enterprise Project Architect** agent at EAAO, run the
**intake interview**, and let it generate the new repository.

> **New here?** Read [`.eaao-core/docs/USAGE.md`](.eaao-core/docs/USAGE.md) — the full map of
> what EAAO can do, how it works, and what is fixed vs. what you can customize.

---

## What you get out of it

Running the orchestrator against a fresh project idea produces a new repository that
already contains, on day zero:

| Concern | Reproduced artifact |
|---|---|
| **Agent contract** | `AGENTS.md` (source of truth) + `CLAUDE.md` / `GEMINI.md` adapters, with the senior-architect persona bound to *the new project's* language and stack |
| **Source layout** | Maven-style cross-language tree `src/{main,test,bench}/<lang>/<group-path>/<project>/` — identical shape, language-appropriate segment |
| **Git governance** | Conventional Commits, branch-naming, one-item-per-PR / one-PR-at-a-time, the agent-vs-human boundary, the PR template + PR-metadata policy |
| **GitHub automation** | CI **and** release workflows, Dependabot, CODEOWNERS, issue forms (+ Discussions/Security routing), a label set, and a one-time `gh` setup script for branch protection / rulesets / Pages / Discussions |
| **Documentation system** | ADRs (+ template + index), design-patterns catalogue (+ the 8-category taxonomy), spec template, session journal, bug ledger, changelog split, releases, and opt-in **i18n** (translated docs + freshness gate) |
| **Quality gates** | A GitHub Actions CI workflow wired to the chosen toolchain's build / test / format / lint / sanitize commands, plus the agent-runnable `consistency_lint.py` |
| **Versioning & comms** | SemVer policy, milestone-driven release flow, post-release maintenance / hotfix / deprecation / security protocol, and an opt-in **announcements** workflow (X / Discord / LinkedIn / Reddit …) |

Every one of these is a **parameterized copy** of what already works in
`pbr-cpp-memory-pool`. The genericity lives in three places:

1. **Language profiles** (`orchestrator/profiles/*.yaml`) encode the per-language
   toolchain knowledge (build tool, test framework, formatter, linter, sanitizers,
   CI matrix, source-file extension, namespace style, version-constant location).
2. **The project manifest** (`orchestrator/project.yaml`) captures the maintainer's
   answers — one source of truth for every placeholder.
3. **The templates** (`templates/**`) are the `pbr` artifacts with the
   project-specific facts replaced by `{{PLACEHOLDERS}}`.

---

## How it works (the pipeline)

```text
                 ┌─────────────────────────────────────────────────────────┐
                 │  Enterprise Project Architect agent (agent/...)         │
                 │  persona: senior architect, 20+ yrs, enterprise bar     │
                 └─────────────────────────────────────────────────────────┘
                                          │
   1. INTERVIEW            ───────────────┼───────────────  orchestrator/interview.md
      Ask the maintainer about language(s), frameworks, tools,                 +
      governance, and the project spec (with follow-up questions).   orchestrator/questionnaire.yaml
                                          │
   2. RESOLVE PROFILE      ───────────────┼───────────────  orchestrator/profiles/<lang>.yaml
      Load the toolchain profile(s) for the chosen language(s);
      the profile fills the toolchain-shaped placeholders.
                                          │
   3. WRITE MANIFEST       ───────────────┼───────────────  orchestrator/project.yaml
      Merge answers + profile into one parameter manifest.
                                          │
   4. RENDER              ────────────────┼───────────────  templates/**  →  <new-repo>/**
      Substitute {{PLACEHOLDERS}}, lay down the source tree,
      seed ADR-0001/0002, the roadmap's Milestone 1, the spec.
                                          │
   5. VERIFY              ────────────────┼───────────────  templates/tools/consistency_lint.py
      Run the consistency lint; initialize git; draft the first PR.
                                          ▼
                            A new, governed, enterprise-grade repository
```

The full, ordered procedure is the **generation playbook**:
[`orchestrator/generate.md`](.eaao-core/orchestrator/generate.md).

---

## Repository layout

```text
pgs-eaao/
├── README.md                          # this file
├── AGENTS.md                          # agent contract for EAAO itself (+ the meta-architect persona)
├── CLAUDE.md / GEMINI.md              # tool adapters → defer to AGENTS.md
├── LICENSE
├── .github/workflows/ci.yml           # EAAO's own CI (self-lint + render smoke)
└── .eaao-core/                        # ALL the factory machinery — one ignorable folder
    ├── agent/                         # enterprise-architect + composable roles + registry
    │   ├── README.md                  # the agent registry/index
    │   ├── enterprise-architect.md    # the orchestrating "senior project architect"
    │   └── reviewer.md  security-auditor.md  release-manager.md  profile-author.md
    ├── orchestrator/                  # the engine
    │   ├── README.md  interview.md  generate.md  recovery.md  placeholders.md
    │   ├── questionnaire.yaml         # machine-readable question bank
    │   ├── project.yaml.template      # the project manifest skeleton (copied to project.yaml per run)
    │   ├── examples/reference.yaml    # a worked manifest (pbr-cpp-memory-pool) + render-smoke fixture
    │   └── profiles/                  # per-language toolchain knowledge (+ _schema.md)
    ├── templates/                     # the parameterized enterprise scaffolding (the output)
    │   ├── AGENTS.md.tmpl  CLAUDE.md.tmpl  GEMINI.md.tmpl  README.md.tmpl  …
    │   ├── docs/**                    # adr/, patterns/, specs/, bugs/, journal/, workflow/, i18n/
    │   ├── .github/**                 # PR + issue templates, CODEOWNERS, dependabot, ci.yml + release.yml
    │   └── tools/consistency_lint.py  # generic, profile-driven congruence checker
    ├── tools/                         # the factory's own tooling
    │   ├── eaao_lint.py               # self-lint: placeholder/profile/playbook integrity
    │   ├── render.py                  # deterministic Mustache-subset renderer
    │   ├── autotune.py                # proposes default changes from accumulated run records
    │   └── self_review.py             # structural quality review of a generated repo
    ├── config/                        # customization overlays (defaults.yaml, house-rules.md)
    ├── learning/                      # lessons ledger + run records (memory / auto-tuning input)
    ├── eval/rubric.md                 # the self-evaluation rubric
    ├── maintenance/stay-current.md    # the profile-refresh routine (+ cron recipe)
    └── docs/adr/                      # ADRs governing EAAO's own design decisions
```

---

## Getting started

### Requirements

EAAO is a markdown/YAML factory — there is nothing to compile and almost nothing to install:

- **git** and an **AI coding agent** that reads `AGENTS.md` — Claude Code, Gemini Antigravity,
  or ChatGPT Codex (this is how you normally drive it);
- **Python 3.12+** — only for the bundled tooling (`tools/render.py`, `tools/eaao_lint.py`, and
  the generated `consistency_lint.py`). All three are standard-library only; no `pip install`.

### Get it

```bash
git clone https://github.com/danielPoloWork/pgs-eaao.git
cd pgs-eaao
python tools/eaao_lint.py        # optional: confirm the factory is internally congruent
```

## Quickstart

You drive EAAO conversationally through the Enterprise Project Architect agent.

1. **Open this repo with your AI coding agent** (Claude Code, Gemini, Codex). It reads
   `AGENTS.md` and adopts the meta-architect persona.
2. **Say what you want to build.** e.g. *"New project: a Rust token-bucket rate limiter,
   library, GitHub owner `acme`, default branch `main`."*
3. **Answer the interview.** The architect walks
   [`orchestrator/interview.md`](.eaao-core/orchestrator/interview.md) — language(s), frameworks,
   tools, governance, and the functional spec — asking only the questions whose answers
   it cannot safely default.
4. **Review the manifest.** The architect writes `orchestrator/project.yaml` and shows it
   to you for confirmation before generating anything.
5. **Generate.** The architect follows [`orchestrator/generate.md`](.eaao-core/orchestrator/generate.md)
   to render the new repository, runs the consistency lint, and drafts the bootstrap PR.

You never have to remember the enterprise rules — they are encoded in the templates and
enforced by the lint. You only make the project-specific decisions.

### Or render it yourself (deterministic, no agent)

The interview's only output is a filled manifest, so you can also fill it by hand and render
without an agent:

```bash
cp orchestrator/project.yaml.template orchestrator/project.yaml
# edit orchestrator/project.yaml — see orchestrator/examples/reference.yaml for a worked one
python tools/render.py orchestrator/project.yaml --out ../my-new-repo
cd ../my-new-repo && python tools/consistency_lint.py     # the generated repo's own gate
```

`render.py` performs exactly the substitutions in
[`orchestrator/placeholders.md`](.eaao-core/orchestrator/placeholders.md), honors the `capabilities.*`
gates, leaves GitHub Actions `${{ … }}` untouched, and **aborts on any unresolved
placeholder**. The render-smoke job in EAAO's own CI runs this against
[`orchestrator/examples/reference.yaml`](.eaao-core/orchestrator/examples/reference.yaml) on every push.

### The tools

| Tool | What it does |
|---|---|
| [`tools/render.py`](.eaao-core/tools/render.py) | Renders a manifest into a repository (deterministic). |
| [`tools/eaao_lint.py`](.eaao-core/tools/eaao_lint.py) | Self-lint: placeholder integrity, profile completeness, playbook references. |
| `templates/tools/consistency_lint.py` | Shipped *into* each generated repo; enforces its cross-artifact congruence. |

---

## Design principles (why it is shaped this way)

- **One source of truth per fact.** A project fact (name, language, owner, namespace)
  is captured once in `project.yaml` and flows to every artifact via placeholders.
  This is the same anti-drift discipline the generated `consistency_lint.py` enforces.
- **Open to any language.** EAAO is not limited to a fixed list — the nineteen shipped profiles
  (C, C++, C#, VB.NET, Java, Kotlin, Scala, Python, Ruby, PHP, JavaScript, TypeScript, Go, Rust,
  Swift, Dart, Lua, COBOL, Pascal) are **seeds**. Supporting a new language means
  copying [`profiles/_template.yaml`](.eaao-core/orchestrator/profiles/_template.yaml) to one
  `profiles/<lang>.yaml` — never editing templates, which only know about *roles* (build tool,
  test runner, formatter), never specific tools. There is no "unsupported language", only
  "not yet profiled".
- **The generated repo governs itself.** EAAO's job ends at generation. The new repo
  ships with its own `AGENTS.md`, CI, and lint, so it is self-sufficient and is *not*
  coupled back to EAAO.
- **English on disk, any language in chat.** Like the reference project, every
  generated artifact is English; the interview itself may be conducted in the
  maintainer's language.
- **Human owns the irreversible steps.** The agent drafts branches, commits, and PRs;
  the human opens, reviews, and merges. EAAO reproduces that boundary verbatim.

---

## Provenance

EAAO is reverse-engineered from `pbr-cpp-memory-pool` — every rule, template, and gate
here has a concrete origin in that project's `AGENTS.md`, `docs/`, `.github/`, and
`tools/consistency_lint.py`. See [`docs/adr/`](.eaao-core/docs/adr/) for the decisions that shaped
the generalization.
