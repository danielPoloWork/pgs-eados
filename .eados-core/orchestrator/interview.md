# Intake Interview Protocol

The script the **Enterprise Project Architect** runs to gather everything needed to
generate a governed repository. Work the phases in order. The machine-readable question
bank is [`questionnaire.yaml`](questionnaire.yaml); this document is the human-readable
protocol with the *why* and the follow-up logic.

## How to run it

- **Load the customization overlay first.** Read [`../config/defaults.yaml`](../config/README.md):
  any value set there overrides the built-in default below (precedence: overlay → profile →
  built-in). Copy a non-empty [`../config/house-rules.md`](../config/house-rules.md) body into
  the manifest's `governance.house_rules`. Offer any custom roles under `../config/agents/`.
- **Conduct it in the maintainer's language.** The answers are transcribed into
  `project.yaml` in English (§2 of `AGENTS.md`).
- **Ask only what you cannot safely default.** Each question below carries a default. If
  the default is obviously right for the stated project, state the assumption and move on
  rather than asking. Reserve real questions for decisions that change the output.
- **Batch related questions.** Prefer a few grouped questions over a long interrogation.
  Phases 1–4 are usually 1–2 rounds; Phase 5 (the spec) is the substantive conversation.
- **Echo back.** After each phase, restate what you captured in one line so the maintainer
  can correct you cheaply.
- **End on the manifest.** The interview's only output is a filled
  [`project.yaml`](project.yaml.template); you show it for confirmation before rendering.

---

## Phase 0 — Frame the project

Establish the one-liner so every later question has context.

- **Q0.1 — What are we building, in one sentence?** → `PROJECT_TAGLINE`, `PROJECT_TITLE`.
- **Q0.2 — What kind of thing is it?** `library` / `service` / `cli` / `app`. Drives the
  capability flags (`IF_SERVICE`, packaging, public API). → `PROJECT_KIND`.
- **Q0.3 — Proposed repository name?** Kebab-case. Suggest one from the tagline if the
  maintainer has none (e.g. *Rust token-bucket rate limiter* → `acme-rust-ratelimiter`).
  → `PROJECT_NAME`, and derive `PROJECT_SLUG` (single lowercase word, e.g. `ratelimiter`).
- **Q0.4 — What is the development target?** `software` / `game` / `mobile` (default
  `software`). This loads [`domains/<domain>.yaml`](domains/_schema.md), which sets the active
  roles, the artifacts (PRD vs **GDD** for a game), the hard NFR budgets (RAM/GPU/framerate for a
  game; app-size/cold-start for mobile), and the milestone vocabulary (SemVer vs Alpha/Beta/RC)
  used from Phase 5 onward. If the chosen target has no profile yet, that is the normal path:
  author it from [`domains/_template.yaml`](domains/_template.yaml) first. → manifest `domain`.

## Phase 1 — Language(s)

The single most structural choice — it selects the profile and the source-tree segment.

**EADOS is open to *any* programming language.** The nineteen shipped profiles are seeds, not the
allowed set — there is no "unsupported language", only "language not yet profiled".

- **Q1.1 — Primary implementation language (and standard/edition)?** → `LANG`, `LANG_NAME`,
  `LANG_STANDARD`. If a profile already exists in [`profiles/`](profiles/), use it. **If not,
  that is the normal path, not an error:** author one by copying
  [`profiles/_template.yaml`](profiles/_template.yaml) to `profiles/<lang>.yaml` (schema:
  [`_schema.md`](profiles/_schema.md)), add an ADR, then resume — the `profile-author` role
  drives this. Never hardcode toolchain facts into a template to skip it.
- **Q1.1a — Language-fit check (advisory).** Weigh the requested language against the domain in
  the spec using [`language-fit.md`](language-fit.md). On a *clear* mismatch, surface 1–2 better
  fits with a one-line reason and let the maintainer confirm or override — **their choice is
  final.** On a sensible choice, say "good fit" and move on. (Phase 5 re-checks this once the
  spec is concrete.)
- **Q1.2 — Any secondary/interop language?** (e.g. a C ABI under a C++ core, Python
  bindings, a WASM target.) If yes, note the second profile and how the surfaces relate.
  **SQL, CSS, and HTML are declared here** — as the schema a backend owns, or the markup/styles
  of a frontend — not as the primary language (see [`language-fit.md`](language-fit.md)).
- **Q1.3 — Reverse-domain group path?** Ask for the maintainer's **own** reverse-domain (e.g.
  `com/acme`); there is no built-in default — `it/d4np` is only the reference project's value, not
  a fallback. → `GROUP_PATH`, `GROUP_DOTTED`. From `LANG` + `GROUP_DOTTED` + `PROJECT_SLUG` the
  profile derives `NAMESPACE` in the language's native idiom (`com::acme::ratelimiter`,
  `com.acme.ratelimiter`, `@acme/ratelimiter`, `github.com/acme/ratelimiter`, …).

> **Follow-up triggers (Phase 1):** a systems language (C/C++/Rust) → ask about ABI
> stability and memory model (feeds `IF_PUBLIC_API`, `IF_THREADING`). A managed/runtime
> language (Java/Python/TS/Go) → ask about the minimum runtime version (feeds the CI
> matrix floor).

## Phase 2 — Frameworks

What the project is built *with* and *against*.

- **Q2.1 — Application/domain frameworks?** Web (Axum, FastAPI, Spring, Express/Nest),
  data, UI, etc. — or "none, standard library only" (the reference project's stance).
- **Q2.2 — Runtime/concurrency model?** Sync, async (which runtime), threads, actor.
  Sets `IF_THREADING` and the sanitizer/race-tooling choices.
- **Q2.3 — Public surface & compatibility target?** Stable API/ABI? Supported consumers
  and platforms? Sets `IF_PUBLIC_API` and `TIER1_PLATFORMS`.

> **Follow-up triggers (Phase 2):** "async" → which executor, and does it need
> race-detection in CI? "web service" → health/readiness, config, and deploy target
> (feeds `IF_SERVICE`). "no framework / stdlib only" → record the zero-dependency stance
> as a future ADR-0002 sibling.

## Phase 3 — Tools

The toolchain the profile pre-fills; confirm or override per project.

- **Q3.1 — Build system & package manager?** Defaults from the profile (`BUILD_TOOL`,
  `PKG_MANAGER`). Override only if the project deviates.
- **Q3.2 — Test framework & coverage tool?** Defaults from the profile (`TEST_FRAMEWORK`,
  `COVERAGE_TOOL`). Confirm the coverage target (the reference uses ≥80% line).
- **Q3.3 — Formatter & linter?** Defaults from the profile (`FORMATTER`, `LINTER`). These
  become the CI `format` and `tidy`/lint jobs and the repo-root config files.
- **Q3.4 — Runtime checkers / sanitizers?** Defaults from the profile (`SANITIZERS`).
  Confirm which are feasible on the CI matrix.
- **Q3.5 — API documentation generator?** Defaults from the profile (`DOC_TOOL`).
- **Q3.6 — Benchmarks?** Does performance need a reproducible benchmark suite? Sets
  `IF_BENCH` and `SRC_BENCH` / `CMD_BENCH`.

## Phase 4 — Governance & GitHub

How the repository is run — reproduces the reference project's GitHub rules.

- **Q4.1 — GitHub owner/org and default branch?** → `OWNER`, `DEFAULT_BRANCH` (default
  `main`). Maintainer display name and copyright holder → `MAINTAINER`, `AUTHOR`.
- **Q4.2 — License?** Default `MIT`. → `LICENSE_ID`, `YEAR`.
- **Q4.3 — Conventional-commit scopes?** Propose a set from the architecture's components
  plus the standard `build, tests, docs, ci`. → the `EACH_SCOPE` list.
- **Q4.4 — Versioning start point?** Pre-1.0 milestone-driven (default, matches the
  reference) or start at 1.0.0? Confirm SemVer and the release cadence.
- **Q4.5 — PR metadata policy?** Confirm assignee (defaults to the **owner** — never `@me`,
  which resolves to whichever actor drafts the PR), the one-type-label scheme, and per-release
  milestones (reference ADR-0040). A GitHub **Project** is attached where one exists; reviewers
  are deferred until a second collaborator, exactly as upstream.
- **Q4.6 — Packaging/distribution?** Distributed via a package registry? Sets
  `IF_PACKAGING`. Default off unless the maintainer asks.
- **Q4.7 — Documentation translations (i18n)?** Default off. If on, capture the **canonical
  source language** (`DOC_DEFAULT_LANG`, default `en` — the English-only rule keeps sources
  English, so translations are *derived* copies under `docs/i18n/<code>/`) and the **target
  languages** as `code`+`name` pairs (`DOC_LANGS`, e.g. `it`=Italian, `es`=Spanish). Sets
  `IF_I18N`; seeds `docs/i18n/translation-status.md` and the lint's `i18n-freshness` gate.
- **Q4.8 — Release/news announcements on social channels?** Default off. If on, capture the
  channels (`ANNOUNCE_CHANNELS`, e.g. X, Discord, LinkedIn, Reddit, Mastodon, a blog) and who
  owns each handle/webhook. Sets `IF_ANNOUNCE`; seeds `docs/workflow/announcements.md`. The
  agent *drafts* the announcement; a human *publishes* it — the same boundary as releases.

## Phase 5 — The functional specification

This is the real conversation. The goal is a frozen spec
([`templates/docs/specs/template.md`](../templates/docs/specs/template.md)) that mirrors
the reference spec's shape: Objective, Functional Requirements, Non-Functional
Requirements, Logical Architecture, Public Interface, Verification Strategy.

Walk these, asking follow-ups until each is concrete enough to test against:

- **Q5.1 — Objective & business context.** What problem does this solve, and for whom?
  What pain (latency, fragmentation, correctness, cost) does it remove? → `SPEC_OBJECTIVE`.
  Now that the domain is concrete, **re-run the language-fit check** ([`language-fit.md`](language-fit.md)):
  if the spec reveals a clear mismatch with the Phase-1 language, say so with a one-line reason
  and let the maintainer confirm or switch — their choice is final, then continue.
- **Q5.2 — Functional requirements.** The observable behaviors. Push for measurable
  phrasing ("O(1) allocation", "p99 < 5 ms", "exactly-once") over adjectives. →
  `EACH_FUNCTIONAL_REQ`.
- **Q5.3 — Non-functional requirements.** Performance, memory, portability, security,
  no-leak / no-UB guarantees, dependency policy. → `EACH_NONFUNCTIONAL_REQ`.
- **Q5.4 — Logical architecture & core algorithm.** The central data structure or control
  flow. Capture it as prose + a diagram block; it seeds the first design ADRs.
- **Q5.5 — Public interface.** The functions/types/endpoints consumers depend on, with the
  error model. → `EACH_PUBLIC_API`, `PUBLIC_INCLUDE_HINT`.
- **Q5.6 — Verification & test strategy.** How correctness and performance are *proven* —
  unit tests, sanitizers, property tests, fuzzing, the canonical leak/race check, the
  benchmark methodology. → `SPEC_VERIFICATION`.
- **Q5.7 — The full roadmap, up front.** Milestone 1 is the universal bootstrap (build system,
  skeleton, CI) — automatic; you may add extra M1 items (→ `EACH_MILESTONE1_ITEM`). Then lay out
  **all** the project's milestones now, not one at a time: for each, a `number` (2, 3, …), a
  `title`, a one-line `goal`, and its `items` as pre-numbered tasks (`2.1`, `2.2`, …). Ask
  follow-up questions until the whole roadmap is concrete; never defer milestones to "later". →
  `EACH_MILESTONE`.

> **Follow-up discipline (Phase 5):** for every requirement, ask "how would CI prove this
> failed?" If there is no mechanical check, either refine the requirement until there is,
> or record it as an explicitly manual gate. This is what keeps the generated quality bar
> real rather than aspirational.

---

## Closing the interview

1. Merge the answers with the resolved profile(s) into `orchestrator/project.yaml`.
2. **Present the manifest to the maintainer**, highlighting every value you defaulted
   rather than asked, so a wrong default is caught now.
3. On confirmation, proceed to [`generate.md`](generate.md). On any change, edit the
   manifest and re-confirm — never render from an unconfirmed manifest.
