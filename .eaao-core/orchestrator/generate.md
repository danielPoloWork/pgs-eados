# Generation Playbook

The ordered, executable procedure the architect follows to turn a confirmed
`project.yaml` into a governed repository. Do not improvise the order — each step depends
on the previous one. Prerequisite: a `project.yaml` the maintainer has confirmed
(see [`interview.md`](interview.md) → *Closing the interview*).

> **Rendering: deterministic or manual.** Steps 3–6 substitute placeholders. You may run the
> bundled renderer — `python .eaao-core/tools/render.py .eaao-core/orchestrator/project.yaml --in-place`
> (the project lands in the current repo, next to `.eaao-core/`; use `--out <dir>` for a separate
> copy) — which performs exactly the substitutions below, expands the source tree, honors the
> `capabilities.*` gates, leaves GitHub Actions `${{ … }}` untouched, and **aborts on any
> unresolved placeholder**. Or do a careful manual pass. Either way, Step 7 verifies the
> result, so the two paths converge.

> **When a step fails,** follow [`recovery.md`](recovery.md) — fix the cause (manifest,
> profile, template, or seed) and re-run; never silence a gate or hand-edit the output.

---

## Step 0 — Preconditions

- `orchestrator/project.yaml` exists, is filled, and the maintainer confirmed it.
- A language profile exists for every `language.lang` / `language.secondary_lang`. If not,
  author it from [`profiles/_schema.md`](profiles/_schema.md) and record an ADR **before**
  generating. Never inline toolchain facts into a template to work around a missing profile.
- Decide **where the project is generated**. The default, recommended model is **in place**: the
  `.eaao-core/` factory is copied into the user's project repo (`<repo>/.eaao-core/`) and the
  renderer writes the project files into `<repo>/` next to it (`render.py --in-place`). The
  rendered `.gitignore` excludes `.eaao-core/`, and `render.py` never writes inside it. To produce
  a *separate* copy instead, render to a directory **outside** the factory (`--out <dir>`). The
  renderer refuses `--in-place` in EAAO's own development repo (the `.eaao-dev` sentinel).

## Step 1 — Resolve derived values

Compute the values not entered directly:

- `src_main = src/main/<lang>/<group_path>/<project_slug>`; likewise `src_test`, and
  `src_bench` only if `capabilities.bench`.
- `namespace` if the maintainer did not give one: apply the profile's `namespace_pattern`
  to `group_dotted` + `project_slug`.
- `public_include_hint` from the profile's import idiom.
- Fill any blank `toolchain.*` from the profile defaults; keep maintainer overrides.
- Apply the [customization overlay](../config/README.md): `config/defaults.yaml` values
  override built-in defaults, and a non-empty `config/house-rules.md` body becomes
  `governance.house_rules` (rendered as `AGENTS.md` §13).

Re-read [`placeholders.md`](placeholders.md) and confirm **every** placeholder used by the
templates now resolves. An unresolved placeholder is a hard stop.

## Step 2 — Create the skeleton & source tree

In the output directory, create the directory shape (identical to the reference, with the
language segment substituted):

```text
<output>/
├── src/
│   ├── main/<lang>/<group_path>/<project_slug>/
│   ├── test/<lang>/<group_path>/<project_slug>/
│   └── bench/<lang>/<group_path>/<project_slug>/        # only if capabilities.bench
├── docs/{adr,patterns,specs,bugs,journal,workflow,development}/   # + i18n/ when capabilities.i18n
├── .github/{ISSUE_TEMPLATE/,workflows/}        # PR template, CODEOWNERS, issue forms, CI + release
└── tools/
```

This layout is normative — it is what makes every PBR-style project the same shape across
languages. It is fixed by the generated repo's ADR-0002.

## Step 3 — Render the governance & agent contract

Render, stripping the `.tmpl` suffix and substituting placeholders:

| Template | → Output |
|---|---|
| `templates/AGENTS.md.tmpl` | `AGENTS.md` |
| `templates/CLAUDE.md.tmpl` | `CLAUDE.md` |
| `templates/GEMINI.md.tmpl` | `GEMINI.md` |
| `templates/README.md.tmpl` | `README.md` |
| `templates/ROADMAP.md.tmpl` | `ROADMAP.md` |
| `templates/CHANGELOG.md.tmpl` | `CHANGELOG.md` |
| `templates/SECURITY.md.tmpl` | `SECURITY.md` |
| `templates/gitignore.tmpl` | `.gitignore` |
| `LICENSE` (EAAO's, with `{{AUTHOR}}`/`{{YEAR}}`) | `LICENSE` |

## Step 4 — Render the documentation system

| Template | → Output | Notes |
|---|---|---|
| `templates/docs/README.md.tmpl` | `docs/README.md` | docs index |
| `templates/docs/adr/template.md` | `docs/adr/template.md` | verbatim |
| `templates/docs/adr/README.md.tmpl` | `docs/adr/README.md` | seeds the ADR index |
| `templates/docs/adr/0001-record-architecture-decisions.md` | `docs/adr/0001-...md` | verbatim |
| `templates/docs/adr/0002-adopt-cross-language-source-layout.md.tmpl` | `docs/adr/0002-...md` | parameterized |
| `templates/docs/patterns/README.md.tmpl` | `docs/patterns/README.md` | empty catalogue, ready to fill |
| `templates/docs/patterns/design-patterns.md` | `docs/patterns/design-patterns.md` | verbatim taxonomy |
| `templates/docs/specs/template.md` | `docs/specs/template.md` | verbatim |
| `templates/docs/specs/01_spec.md.tmpl` | `docs/specs/01_spec_<slug>.md` | filled from Phase 5 |
| `templates/docs/bugs/template.md` | `docs/bugs/template.md` | verbatim |
| `templates/docs/bugs/README.md.tmpl` | `docs/bugs/README.md` | empty ledger index |
| `templates/docs/journal/README.md.tmpl` | `docs/journal/README.md` | empty journal index |
| `templates/docs/releases/README.md.tmpl` | `docs/releases/README.md` | empty release-notes index (day-zero) |
| `templates/docs/development/local-build.md.tmpl` | `docs/development/local-build.md` | local build/test guide (linked from README) |
| `templates/docs/workflow/*.tmpl` | `docs/workflow/*` | git-workflow, documentation, release, maintenance, github-setup; `announcements.md`/`operations.md`/`packaging.md` **only when `capabilities.announce`/`service`/`packaging`** |
| `templates/docs/benchmarks/README.md.tmpl` + `template.md` | `docs/benchmarks/*` | **only when `capabilities.bench`** — methodology + results index + report template |
| `templates/docs/i18n/*.tmpl` | `docs/i18n/*` | **only when `capabilities.i18n`** — index + `translation-status.md` manifest |

Seed the **spec** (`docs/specs/01_spec_<slug>.md`) from `spec.*`: Objective, Functional &
Non-Functional Requirements, Logical Architecture, Public Interface, Verification Strategy
— the reference spec's six-section shape.

## Step 5 — Render CI & tooling

| Template | → Output |
|---|---|
| `templates/.github/PULL_REQUEST_TEMPLATE.md.tmpl` | `.github/PULL_REQUEST_TEMPLATE.md` |
| `templates/.github/workflows/ci.yml.tmpl` | `.github/workflows/ci.yml` |
| `templates/.github/workflows/release.yml.tmpl` | `.github/workflows/release.yml` |
| `templates/.github/dependabot.yml.tmpl` | `.github/dependabot.yml` |
| `templates/.github/CODEOWNERS.tmpl` | `.github/CODEOWNERS` |
| `templates/.github/labels.yml.tmpl` | `.github/labels.yml` |
| `templates/.github/ISSUE_TEMPLATE/*.tmpl` | `.github/ISSUE_TEMPLATE/*` (bug_report, feature_request, config) |
| `templates/tools/consistency_lint.py` | `tools/consistency_lint.py` (set its `CONFIG` block from the manifest) |

`docs/workflow/github-setup.md` (rendered in Step 4) carries the one-time, admin-only repo
configuration that cannot be a committed file — branch protection / ruleset for
`{{DEFAULT_BRANCH}}`, squash-only merge, Discussions, Pages, label import, the first
milestone. Surface it in the hand-off report so the maintainer runs it once.

The CI workflow's setup steps and extra jobs come from the profile's `ci.setup_steps` /
`ci.extra_jobs`; the build/test/format/lint commands come from `toolchain.commands`. Drop
the benchmark and TSan jobs when `capabilities.bench` / `capabilities.threading` are false.

## Step 6 — Seed the roadmap & day-zero state

- `ROADMAP.md`: render the **full roadmap up front** — Milestone 1 (universal bootstrap + any
  `spec.milestone1_items`) and **every** `spec.milestones` entry (`number`, `title`, `goal`,
  `items`) — plus the *Spec Coverage Map* skeleton (one row per spec section) so the lint's
  `spec-map` check passes. Mirror the same milestone list into the README milestone table.
- `CHANGELOG.md`: a single `[Unreleased]` block + an empty *Released versions* index.
- The version constant in `version_file` set to `{{START_VERSION}}` (the same value the
  README `Status-vX.Y.Z` badge renders) — `0.0.0` pre-1.0, or as decided in Q4.4. Keeping
  the constant and the badge equal is what makes the lint's `version-lockstep` pass on day
  zero.
- `docs/adr/README.md`: index rows for ADR-0001 and ADR-0002 only.
- `docs/patterns/README.md`: empty *Adopted* table + the candidate-pattern scaffold.

## Step 7 — Verify

1. **Run the consistency lint:** `python tools/consistency_lint.py` from the output repo.
   It must pass. The day-zero seeds in Step 6 are specifically arranged so it does.
2. **Grep for stray placeholders:** no `{{` may remain anywhere under the output dir — when
   generating in place, exclude the copied-in `.eaao-core/`, whose `.tmpl` files legitimately
   contain them.
3. **Toolchain smoke (best effort):** run the profile's `CMD_BUILD` / `CMD_TEST` on the
   skeleton if the language allows a trivial buildable stub; otherwise note it as the first
   Milestone-1 task.

## Step 8 — Initialize git & draft the bootstrap PR

Reproduce the reference project's agent-vs-human boundary exactly:

1. `git init` (skip if the repo already exists, as in the in-place model), set
   `init.defaultBranch` to `default_branch`, first commit on a branch
   `chore/bootstrap-enterprise-scaffold` (Conventional Commits). The rendered `.gitignore`
   already excludes `.eaao-core/`, so the factory is never committed into the project.
2. If a remote exists and the maintainer authorized it, push the branch and **draft**
   (`gh pr create --draft`) — never open or merge. Otherwise print the suggested commands.
3. Hand off: from here, the generated repo's own `AGENTS.md` governs all further work. EAAO
   steps back.

## Output report

Conclude with a short report to the maintainer:

- output path, language(s), resolved toolchain, capability flags;
- the file tree created (counts per area);
- consistency-lint result;
- the exact next action (open the drafted PR / run the printed git commands);
- any spec requirement that has no mechanical CI check yet (flagged in Phase 5).
