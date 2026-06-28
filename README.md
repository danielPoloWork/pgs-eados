# Enterprise Agentic Delivery Operating System (EADOS)

[![CI](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v2.2.0-blue.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](.eados-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> **🌐 Translations:** [简体中文](.eados-core/docs/i18n/zh-Hans/README.md) · [日本語](.eados-core/docs/i18n/ja/README.md) — derived from this English source. Policy & freshness: [`.eados-core/docs/i18n/`](.eados-core/docs/i18n/README.md).

> A language-agnostic **delivery operating system** for enterprise software, games, and mobile
> apps: an opt-in phase pipeline — `init → design → plan → scaffold → audit → refactor` — that
> governs a project from its first RFC to release. Its `scaffold` phase stamps out an **enterprise
> agent system** for *any* language, from a single manifest and parameterized templates.

EADOS is not a product you ship; it is the **operating system for how the work flows** — a
declarative, gate-enforced, human-in-the-loop governance layer (not a runtime kernel). Its
**`scaffold` phase is the factory** that stamps out repositories sharing the same enterprise
structure, GitHub workflow, quality gates, and AI-agent contract — regardless of language,
framework, or tooling. The other phases (`design`, `plan`, `audit`, `refactor`) extend that
governance across the whole delivery lifecycle.

> **The pipeline.** Each phase is an opt-in `/eados <phase>` command over a persistent,
> gate-checked manifest; the design is [RFC-0001](.eados-core/docs/rfc/0001-eados-delivery-os.md),
> the phases live in [`orchestrator/commands/`](.eados-core/orchestrator/commands/README.md).
> Generation alone (the classic factory) is still just `/eados scaffold` — nothing about it changed.

It exists to answer one question:

> *"How do I get the **same** enterprise rigor — agents, ADRs, CI matrix, consistency lint,
> SemVer governance — on every project, whatever the language: Rust / Python / TypeScript /
> Go / Java / …?"*

The answer: point the **Enterprise Project Architect** agent at EADOS, run the
**intake interview**, and let it generate the new repository.

> **New here?** Read [`.eados-core/docs/USAGE.md`](.eados-core/docs/USAGE.md) — the full map of
> what EADOS can do, how it works, and what is fixed vs. what you can customize. Want to *see* the
> pipeline run? Follow the [phase-by-phase walkthrough](.eados-core/docs/walkthrough.md).

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

Every one of these is a **parameterized artifact** held to an enterprise bar. The genericity lives
in three places:

1. **Language profiles** (`orchestrator/profiles/*.yaml`) encode the per-language
   toolchain knowledge (build tool, test framework, formatter, linter, sanitizers,
   CI matrix, source-file extension, namespace style, version-constant location).
2. **The project manifest** (`orchestrator/project.yaml`) captures the maintainer's
   answers — one source of truth for every placeholder.
3. **The templates** (`templates/**`) are the enterprise artifacts with the
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
[`orchestrator/generate.md`](.eados-core/orchestrator/generate.md).

---

## Repository layout

```text
pgs-eados/
├── README.md                          # this file
├── AGENTS.md                          # agent contract for EADOS itself (+ the meta-architect persona)
├── CLAUDE.md / GEMINI.md              # tool adapters → defer to AGENTS.md
├── LICENSE
├── .github/workflows/ci.yml           # EADOS's own CI (self-lint + render smoke)
└── .eados-core/                        # ALL the factory machinery — one ignorable folder
    ├── agent/                         # enterprise-architect + composable roles + registry
    │   ├── README.md                  # the agent registry/index
    │   ├── enterprise-architect.md    # the orchestrating "senior project architect"
    │   └── reviewer.md  security-auditor.md  release-manager.md  profile-author.md
    ├── orchestrator/                  # the engine
    │   ├── README.md  interview.md  generate.md  recovery.md  placeholders.md
    │   ├── questionnaire.yaml         # machine-readable question bank
    │   ├── project.yaml.template      # the project manifest skeleton (copied to project.yaml per run)
    │   ├── examples/reference.yaml    # a worked manifest + render-smoke fixture
    │   └── profiles/                  # per-language toolchain knowledge (+ _schema.md)
    ├── templates/                     # the parameterized enterprise scaffolding (the output)
    │   ├── AGENTS.md.tmpl  CLAUDE.md.tmpl  GEMINI.md.tmpl  README.md.tmpl  …
    │   ├── docs/**                    # adr/, patterns/, specs/, bugs/, journal/, workflow/, i18n/
    │   ├── .github/**                 # PR + issue templates, CODEOWNERS, dependabot, ci.yml + release.yml
    │   └── tools/consistency_lint.py  # generic, profile-driven congruence checker
    ├── tools/                         # the factory's own tooling
    │   ├── eados_lint.py               # self-lint: placeholder/profile/playbook integrity
    │   ├── render.py                  # deterministic Mustache-subset renderer
    │   ├── autotune.py                # proposes default changes from accumulated run records
    │   └── self_review.py             # structural quality review of a generated repo
    ├── config/                        # customization overlays (defaults.yaml, house-rules.md)
    ├── learning/                      # lessons ledger + run records (memory / auto-tuning input)
    ├── eval/rubric.md                 # the self-evaluation rubric
    ├── maintenance/stay-current.md    # the profile-refresh routine (+ cron recipe)
    └── docs/adr/                      # ADRs governing EADOS's own design decisions
```

---

## Getting started

### Requirements

EADOS is a markdown/YAML factory — nothing to compile, almost nothing to install. What you need
depends on how you drive it:

- **To use it conversationally (recommended)** — an **AI coding agent** that reads `AGENTS.md`:
  Claude Code, Gemini Antigravity, or ChatGPT Codex.
- **To use it deterministically (no agent)** — **Python 3.12+** only, for the bundled tooling
  (`render.py`, `eados_lint.py`, and the generated `consistency_lint.py`); standard-library only,
  no `pip install`.
- **To contribute to EADOS** — **git**, to clone and open pull requests. You do **not** need git
  just to download and use the factory.

### Prerequisites — getting an AI coding agent

The recommended (conversational) path needs an **`AGENTS.md`-aware AI coding agent**. Install one:

- **Claude Code** — [install & setup](https://docs.anthropic.com/en/docs/claude-code)
- **Gemini Antigravity** — [antigravity.google](https://antigravity.google/)
- **ChatGPT Codex** — [Codex CLI](https://developers.openai.com/codex/cli)

"**Open the folder with your agent**" then means: start the agent in your project's repo root — it
auto-loads `AGENTS.md` and adopts the Enterprise Project Architect persona, ready for the interview.

**Which model?** EADOS leans on the agent's reasoning, so the strongest models do best. Today it
performs best with **Claude Opus 4.8 (high)** — with **Fable 5** not yet available — followed by
**OpenAI Codex 5.5** and **Gemini 3.5 Flash**; **Mistral AI** and **Sakana AI** are not yet tested.

> **⚠ AI agents can hallucinate.** They draft confidently and are sometimes wrong — **review every
> diff, RFC, and command** before acting on it. EADOS lowers the barrier for newcomers, but it is a
> **power tool**: most effective in experienced hands, where you bring the engineering judgment and
> the agent brings the speed. The human owns every irreversible step (open / merge / publish).

**No agent? You're not blocked** — take the **deterministic path**: fill `project.yaml` and run
`render.py` (Python 3.12+, standard-library only). See [Quickstart](#quickstart) and
[`USAGE.md`](.eados-core/docs/USAGE.md) §3.

### Get it

**Guided installer (one step) — recommended.** Grab the installer for your OS from the latest
release and run it: it prompts for where to install (new vs existing repo, path), **verifies the
bundle's SHA256** (fail-closed), and extracts it **additively** (never overwriting an existing file).
Full options (macOS double-click, scripting flags, air-gapped verify) are in
[`USAGE.md`](.eados-core/docs/USAGE.md) §6.

```bash
# Linux / macOS — download then run (it prompts)
curl -fsSL https://github.com/danielPoloWork/pgs-eados/releases/latest/download/setup.sh -o setup.sh && sh setup.sh
```

```powershell
# Windows (PowerShell) — or double-click setup.bat from the release
Invoke-WebRequest https://github.com/danielPoloWork/pgs-eados/releases/latest/download/setup.ps1 -OutFile setup.ps1; powershell -ExecutionPolicy Bypass -File setup.ps1
```

**Or download the bundle manually** — no clone, and you see exactly what runs. The bundle is a
self-contained, **prefix-less** copy of the factory (no CI, changelog, or git history). Extract it
**at the root of your project's repo** so its contents — `.eados-core/` plus the agent contract and
`LICENSE` — land directly there, **not** inside a subfolder:

```bash
cd my-project        # your project's repo root (new or existing)
curl -L -o /tmp/pgs-eados-bundle.tar.gz \
  https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz
tar xzf /tmp/pgs-eados-bundle.tar.gz   # extracts .eados-core/, AGENTS.md, … into the current folder
```

On **Windows (PowerShell)** — `tar` ships with Windows 10+:

```powershell
cd my-project
Invoke-WebRequest -Uri https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz -OutFile $env:TEMP/pgs-eados-bundle.tar.gz
tar -xzf $env:TEMP/pgs-eados-bundle.tar.gz   # extracts .eados-core/, AGENTS.md, … into the current folder
```

You should now have `my-project/.eados-core/` (next to `AGENTS.md`). Prefer a ZIP or your browser?
Download either asset from the [latest release](https://github.com/danielPoloWork/pgs-eados/releases/latest)
and unzip it **at the repo root** (its contents at the top level — no wrapping folder). Then
confirm and generate as in [Quickstart](#quickstart):

```bash
ls .eados-core                           # orchestrator/ templates/ tools/ …
python .eados-core/tools/eados_lint.py    # optional: confirm the factory is internally congruent
```

**Clone the repository — to contribute to EADOS** (the full repo: CI, changelog, history):

```bash
git clone https://github.com/danielPoloWork/pgs-eados.git && cd pgs-eados
```

## Quickstart

You drive EADOS conversationally through the Enterprise Project Architect agent.

1. **Open the project folder with your AI coding agent** (Claude Code, Gemini, Codex). It reads
   `AGENTS.md` and adopts the meta-architect persona.
2. **Say what you want to build.** e.g. *"New project: a Rust token-bucket rate limiter,
   library, GitHub owner `acme`, default branch `main`."*
3. **Answer the interview.** The architect walks
   [`orchestrator/interview.md`](.eados-core/orchestrator/interview.md) — language(s), frameworks,
   tools, governance, and the functional spec — asking only the questions whose answers
   it cannot safely default.
4. **Review the manifest.** The architect writes `orchestrator/project.yaml` and shows it
   to you for confirmation before generating anything.
5. **Generate.** The architect follows [`orchestrator/generate.md`](.eados-core/orchestrator/generate.md)
   to render the new repository, runs the consistency lint, and drafts the bootstrap PR.

You never have to remember the enterprise rules — they are encoded in the templates and
enforced by the lint. You only make the project-specific decisions.

### Or render it yourself (deterministic, no agent)

The interview's only output is a filled manifest, so you can also fill it by hand and render
without an agent:

```bash
cp .eados-core/orchestrator/project.yaml.template .eados-core/orchestrator/project.yaml
# edit .eados-core/orchestrator/project.yaml — see .eados-core/orchestrator/examples/reference.yaml for a worked one
python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place
python tools/consistency_lint.py     # the generated repo's own gate (now at the repo root)
```

`render.py` performs exactly the substitutions in
[`orchestrator/placeholders.md`](.eados-core/orchestrator/placeholders.md), honors the `capabilities.*`
gates, leaves GitHub Actions `${{ … }}` untouched, and **aborts on any unresolved
placeholder**. The render-smoke job in EADOS's own CI runs this against
[`orchestrator/examples/reference.yaml`](.eados-core/orchestrator/examples/reference.yaml) on every push.

### The tools

| Tool | What it does |
|---|---|
| [`tools/render.py`](.eados-core/tools/render.py) | Renders a manifest into a repository (deterministic). |
| [`tools/eados_lint.py`](.eados-core/tools/eados_lint.py) | Self-lint: placeholder integrity, profile completeness, playbook references. |
| `templates/tools/consistency_lint.py` | Shipped *into* each generated repo; enforces its cross-artifact congruence. |

---

## Design principles (why it is shaped this way)

- **One source of truth per fact.** A project fact (name, language, owner, namespace)
  is captured once in `project.yaml` and flows to every artifact via placeholders.
  This is the same anti-drift discipline the generated `consistency_lint.py` enforces.
- **Open to any language.** EADOS is not limited to a fixed list — the nineteen shipped profiles
  (C, C++, C#, VB.NET, Java, Kotlin, Scala, Python, Ruby, PHP, JavaScript, TypeScript, Go, Rust,
  Swift, Dart, Lua, COBOL, Pascal) are **seeds**. Supporting a new language means
  copying [`profiles/_template.yaml`](.eados-core/orchestrator/profiles/_template.yaml) to one
  `profiles/<lang>.yaml` — never editing templates, which only know about *roles* (build tool,
  test runner, formatter), never specific tools. There is no "unsupported language", only
  "not yet profiled".
- **The generated repo governs itself.** EADOS's job ends at generation. The new repo
  ships with its own `AGENTS.md`, CI, and lint, so it is self-sufficient and is *not*
  coupled back to EADOS.
- **English on disk, any language in chat.** Every generated artifact is English; the interview
  itself may be conducted in the maintainer's language.
- **Human owns the irreversible steps.** The agent drafts branches, commits, and PRs;
  the human opens, reviews, and merges. EADOS reproduces that boundary verbatim.

---

## Contributing & governance

EADOS is **owner-governed**: contributors *suggest* via pull requests, the owner
(`@danielPoloWork`) *decides* and **squash-merges**. Nobody pushes to `main` directly.

- Start with [`CONTRIBUTING.md`](CONTRIBUTING.md): fork → feature branch → Conventional
  Commits → run the gates (`eados_lint`, render-smoke, `tools/tests/`) → open a PR.
- `main` accepts the **squash** merge method only; the full branch-protection ruleset
  (require-PR, restrict who can push) is active once the repo is public.
- Security issues never go in a public issue — see [`SECURITY.md`](SECURITY.md). Questions and
  ideas go to GitHub Discussions. Releases follow SemVer and are recorded in
  [`CHANGELOG.md`](CHANGELOG.md). The full contract is [`AGENTS.md`](AGENTS.md).

---

## Provenance

Every rule, template, and gate in EADOS is deliberate: the design is ratified in
[RFC-0001](.eados-core/docs/rfc/0001-eados-delivery-os.md), and each non-trivial decision is recorded
in [`docs/adr/`](.eados-core/docs/adr/).

## License & ownership

EADOS is released under the **[MIT License](LICENSE)** — © 2026 **Daniel Polo**. It is maintained and
**owner-governed** by **Daniel Polo** (`@danielPoloWork`): contributors *suggest* via pull requests,
the owner *decides* and squash-merges (see [Contributing & governance](#contributing--governance)).
The bundled `LICENSE` ships with the factory on purpose — `render.py` reads it as the source for every
generated project's license, so each repo EADOS produces is MIT-licensed to its own owner.
