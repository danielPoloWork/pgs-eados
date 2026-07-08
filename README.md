# EADOS — Enterprise Agentic Delivery OS

[![CI](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v2.8.0-blue.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![Downloads](https://img.shields.io/github/downloads/danielPoloWork/pgs-eados/total.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](.eados-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> **🌐 Translations:** [简体中文](.eados-core/docs/i18n/zh-Hans/README.md) · [日本語](.eados-core/docs/i18n/ja/README.md) — derived from this English source. Policy & freshness: [`.eados-core/docs/i18n/`](.eados-core/docs/i18n/README.md).

> A language-agnostic **delivery operating system** for enterprise software, web, games, and mobile
> apps: an opt-in phase pipeline — `init → design → plan → scaffold → audit → refactor` — that
> governs a project from its first RFC to release. Its `scaffold` phase stamps out an **enterprise
> agent system** for *any* language, from a single manifest and parameterized templates.

EADOS is not a product you ship; it is the **operating system for how the work flows** — a
declarative, gate-enforced, human-in-the-loop governance layer (not a runtime kernel). Its
**`scaffold` phase is the factory** that stamps out repositories sharing the same enterprise
structure, GitHub workflow, quality gates, and AI-agent contract — regardless of language, framework,
or tooling; the other phases (`design`, `plan`, `audit`, `refactor`) extend that governance across the
whole delivery lifecycle. Each phase is an opt-in `/eados <phase>` command over a persistent,
gate-checked manifest (design: [RFC-0001](.eados-core/docs/rfc/0001-eados-delivery-os.md)).

> **New here?** [`USAGE.md`](.eados-core/docs/USAGE.md) is the full map of what EADOS can do; the
> [phase-by-phase walkthrough](.eados-core/docs/walkthrough.md) shows it running. Just want to install
> it? Jump to [Getting started](#getting-started).

## Contents

- [Why EADOS](#why-eados) · [Capabilities at a glance](#capabilities-at-a-glance)
- [What you get out of it](#what-you-get-out-of-it) · [The phase pipeline](#the-phase-pipeline) · [How generation works](#how-generation-works)
- [Repository layout](#repository-layout) · [The tools](#the-tools) · [How EADOS learns](#how-eados-learns) · [Getting started](#getting-started) · [Quickstart](#quickstart)
- [Design principles](#design-principles-why-it-is-shaped-this-way) · [Security posture](#security-posture) · [FAQ](#faq)
- [Contributing & governance](#contributing--governance) · [Provenance](#provenance) · [License & ownership](#license--ownership)

## Why EADOS

It answers one question:

> *"How do I get the **same** enterprise rigor — agents, ADRs, CI matrix, consistency lint, SemVer
> governance — on **every** project, whatever the language: Rust / Python / TypeScript / Go / Java / …?"*

Point the **Enterprise Project Architect** agent at EADOS, run the intake interview, and it generates
the new repository — or fill the manifest and render deterministically, no agent required.

**Why not a cookiecutter / copier / Yeoman?** Those scaffold a repo *once* and walk away. EADOS is a
**delivery operating system**, not a one-shot template:

1. **Language-agnostic *by data*** — toolchain knowledge lives in profiles, never hardcoded in
   templates, so one factory serves 19+ languages (and a new one is added as data, not code).
2. **The generated repo governs itself** — it ships its own agent contract, CI, quality gate, and
   SemVer flow, and is self-sufficient (no runtime coupling back to EADOS).
3. **Generation is just one phase** — `design → plan → audit → refactor` extend governance across the
   whole lifecycle, over a persistent, gate-checked manifest with role authority and a traceability
   graph.

It is **deterministic and human-gated**: the agent drafts, the human reviews and merges; an unresolved
placeholder is a hard error, never a guess.

## Capabilities at a glance

- **Generate** an enterprise-grade repo in **any language** — 19 profiles shipped; add one as data.
- **Govern the whole lifecycle** — six opt-in phases (`init · design · plan · scaffold · audit ·
  refactor`) over a persistent manifest, with phase-transition gates.
- **Composable agent roles** with a **persona ≠ authority** split — architect, reviewer,
  security-auditor, release-manager, product-manager, tech-lead, producer, contribution-reviewer.
- **Quality & safety gates** — placeholder / profile / spec completeness, a generated
  `consistency_lint`, risk scoring, and a traceability graph (RFC → milestone → PR → commit → release).
- **Inbound contribution review** (`/eados review`) — triage a non-owner PR by trust tier, policy, and
  risk; recommend a disposition (it never auto-merges).
- **Guided installer** — a cross-platform `setup.{sh,command,ps1,bat}` with **fail-closed SHA256**
  verification and additive, no-clobber extraction.
- **Self-improvement, versioned & human-gated** — a lessons ledger, an auto-tuner, and self-review.
- **Opt-in** i18n (translated docs + a freshness gate), social announcements, and benchmarks.
- **No-agent / offline path** — standard-library Python; render deterministically from a manifest.

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

## The phase pipeline

Beyond one-shot generation, EADOS governs a project across six **opt-in** phases — each an
`/eados <phase>` command over the persistent manifest, with deterministic gates on every transition
(the human confirms the human-gated moves). Adopt only the phases you want: a user who just wants
generation runs `/eados scaffold` and ignores the rest.

| Phase | What it does | Key artifact / gate |
|---|---|---|
| **`init`** | Frame the project and write the initial manifest (`delivery_state`). | manifest skeleton |
| **`design`** | Author / import RFCs under a review protocol. | `rfc-approved` |
| **`plan`** | Co-create the roadmap from the RFCs; build the traceability graph. | `roadmap-covers-rfcs` |
| **`scaffold`** | **Generate** the governed repository — the classic factory. | render + `consistency_lint` |
| **`audit`** | Continuous risk scoring + the enforced traceability lint. | `traceability-lint`, risk threshold |
| **`refactor`** | Bring an existing repo up to standard via gated, sandboxed, **additive** PRs. | write-contained sandbox |

Full detail is in [`USAGE.md`](.eados-core/docs/USAGE.md) and the
[command playbooks](.eados-core/orchestrator/commands/README.md). Two cross-cutting commands work in
any phase: [`/eados status`](.eados-core/orchestrator/commands/status.md) (a read-only doctor) and
[`/eados review`](.eados-core/orchestrator/commands/review.md) (inbound-PR triage).

---

## How generation works

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
    │   ├── profiles/                  # per-language toolchain knowledge (+ _schema.md)
    │   ├── os/                        # machine-readable delivery-OS specs (git, workflow, rfc, contribution, …)
    │   ├── domains/                   # domain overlays (game / web / mobile) + schema
    │   └── commands/                  # the /eados <phase> command playbooks
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

## The tools

Everything under `.eados-core/tools/` is standard-library Python (3.12+) — no `pip install`. On
the conversational path you never invoke these by hand (the agent does), but they are the
deterministic spine, grouped by what they do:

**Generate — turn a manifest into a governed repo**

| Tool | What it does |
|------|--------------|
| `render.py` | Deterministic Mustache-subset renderer (manifest → the full scaffold) |
| `render_artifact.py` | Render one template and place it (single-artifact sandbox) |
| `eados.py` | Thin phase orchestrator — the executable `/eados <phase>` |
| `phase_runner.py` | State-driven checker behind each phase (gates + domain overlays) |
| `preflight.py` | Verify the toolchain the pipeline assumes is present & authenticated |
| `seed_milestones.py` | Read `ROADMAP.md` and seed every milestone on GitHub |
| `brownfield.py` · `migration_planner.py` · `sandbox.py` | Read an existing repo, plan a migration, contain refactor writes |

**Govern — authority, traceability, PRs, releases**

| Tool | What it does |
|------|--------------|
| `authority_check.py` | The path→role gate (who may touch what) |
| `doctor.py` | `/eados status` — an at-a-glance health readout |
| `traceability.py` · `derive_links.py` | The lineage graph + its `roadmap-covers-rfcs` / `traceability-lint` gates, derived from merged PRs |
| `risk_score.py` | The audit phase's deterministic risk model |
| `pr_review.py` · `pr_metadata_check.py` | Inbound-PR evaluation + PR-metadata presence |
| `rfc_check.py` | Verify an RFC against the review protocol |
| `sync_action_pins.py` | Keep rendered workflow pins in lockstep with the factory CI |
| `cleanup_installer.py` | Remove guided-installer leftovers after `init` |

**Verify — the gates that keep it honest**

| Tool | What it does |
|------|--------------|
| `eados_lint.py` | The factory self-lint (18 congruence + coverage checks) |
| `self_review.py` | Structural completeness of a generated repo |
| `profile_ci_lint.py` | Every shipped CI fragment parses as valid YAML |
| `consistency_lint.py` *(shipped into the repo)* | Generic, profile-driven congruence checker |
| `yamlmini.py` | The dependency-free YAML loader shared by all of the above |

**Learn — the versioned, human-gated memory loop**

| Tool | What it does |
|------|--------------|
| `record_run.py` | Mechanized run records (Step 9) — provenance-derived overrides + failure/rubric channels |
| `autotune.py` | Propose default changes from the accumulated run records |
| `lesson_audit.py` | Regressions vs. lessons, dead lessons, low rubric trends (report-only) |
| `lesson_sweep.py` | Harvest review-time `Lesson:` fields into draft ledger entries |

See [How EADOS learns](#how-eados-learns) for how the *learn* group closes the loop.

---

## How EADOS learns

EADOS improves without a vector database or opaque fine-tuning: its memory is **versioned,
human-gated, and mechanical**. Four artifacts, each with a clear writer / approver / enforcer:

| Memory | What it holds | Who writes | Who approves | Who enforces |
|--------|---------------|------------|--------------|--------------|
| `learning/lessons.yaml` | Durable, generalizable rules | agent drafts (at review time via the PR `Lesson:` field, or `lesson_sweep.py`) | the owner — a merged PR body is approval by construction | `eados_lint` `lessons` |
| `learning/runs/*.yaml` | One record per generation run (overrides, failures, rubric) | `record_run.py`, mechanically from manifest provenance | — (facts, never edited) | `eados_lint` `run-records` schema gate |
| `autotune.py` · `lesson_audit.py` | Proposals mined from the records | the tools (report-only) | the owner | — (advisory) |
| `docs/adr/**` | Load-bearing design decisions | agent drafts | the owner | ADR index + review |

The spine is an **escalation path** — knowledge hardens one rung at a time:

> **incident → lesson (advisory) → gate (mechanical) → meta-gate (coverage)**

A mistake becomes a recorded *lesson*; a lesson that keeps recurring (surfaced by
`lesson_audit.py`) is promoted to a *gate* in `eados_lint.py` so it cannot recur silently; and the
**gate-coverage meta-gate** guarantees every externally-modifiable file class sits inside that
perimeter. L-0001 ("a multi-line placeholder must carry its indentation") already made the full
trip — it is renderer logic and a lint check today, not a sticky note.

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

**Which model?** EADOS leans on the agent's reasoning, so the strongest models do best. **As of
2026-07**, it performs best with **Claude Opus 4.8 (high)**, followed by **OpenAI Codex 5.5** and
**Gemini 3.5 Flash**; the rest of the Claude 5 family (including **Fable 5**) and **Mistral AI** /
**Sakana AI** are not yet benchmarked for EADOS. *(Model rankings rotate fast — treat this as a
dated snapshot, not a standing claim.)*

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

## Security posture

EADOS treats the supply chain and the agent boundary as first-class:

- **Fail-closed installer integrity.** The guided installer verifies the bundle's **SHA256** against
  the release `SHA256SUMS` before extracting; it refuses an unverified bundle (no blind `curl | sh`)
  and extracts **additively** — never overwriting an existing file.
- **Write-contained generation.** The renderer and the `refactor` sandbox refuse any write that
  escapes the target — traversal / absolute / symlink / `.git` / clobber (the
  [ADR-0007](.eados-core/docs/adr/0007-renderer-write-guards-and-validation-independence.md) principle).
- **Untrusted inbound code.** `/eados review` classifies a non-owner PR by trust tier and flags the
  poisoned-pipeline surface (workflow edits, new deps, secret reach); a non-owner's commits are
  **never merged** — a good idea is re-implemented in-house with credit.
- **Pinned, auditable CI.** GitHub Actions are SHA-pinned (Dependabot + an auto-sync gate keep the
  pins honest); the self-lint gates run **offline** (no network in the gate path).
- **Human owns every irreversible step** — the agent drafts; the human opens, merges, and publishes.
- **Auditable lineage.** A traceability graph ties every release back through PR → commit → milestone
  → RFC; a dangling edge fails the lint.

## FAQ

**Is this a cookiecutter / project template?** No — see [Why EADOS](#why-eados). Generation is one
phase of a governed delivery OS, and the output carries its own governance.

**Do I need an AI agent?** No. The conversational path is recommended, but the **deterministic path**
(fill `project.yaml`, run `render.py`) needs only standard-library Python 3.12+.

**Which languages are supported?** Any. 19 profiles ship today; a new language is a data file
(`profiles/<lang>.yaml`), never a template edit.

**Does a generated repo depend on EADOS at runtime?** No — it is self-sufficient; its own `AGENTS.md`,
CI, and lint travel with it. EADOS's job ends at generation.

**Can I use it offline / air-gapped?** Yes. The installer supports `--from` + `--sums-file` (verify a
hand-downloaded bundle), and the deterministic render + gates need no network.

**Which model works best?** See [Prerequisites](#prerequisites--getting-an-ai-coding-agent) — **as of
2026-07**, **Claude Opus 4.8 (high)** leads, then Codex 5.5 and Gemini 3.5 Flash.

**Does EADOS send my code or data anywhere?** No — it is markdown / YAML / standard-library Python with
no telemetry. Your AI agent is a separate tool with its own data policy.

---

## Contributing & governance

EADOS is **owner-governed**: contributors *suggest* via pull requests, the owner
(`@danielPoloWork`) *decides* and **squash-merges**. Nobody pushes to `main` directly.

- Start with [`CONTRIBUTING.md`](CONTRIBUTING.md): fork → feature branch → Conventional
  Commits → run the gates (`eados_lint`, render-smoke, `tools/tests/run_all.py`) → open a PR.
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
