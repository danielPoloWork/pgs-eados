# Using EAAO — capabilities, how it works, what is fixed, what you customize

A practical map of the Enterprise Agentic Architecture Orchestrator for anyone who just
downloaded it. For the install/quickstart see the [getting-started README](../README.md); the
binding rules live in [`AGENTS.md`](../../AGENTS.md). This page is the orientation in between.

---

## 1. What you can do

EAAO is a **factory**, not a product: it stamps out enterprise-grade repositories that all
share the same governance, quality gates, and AI-agent contract — in **any** language.

| Use | How |
|---|---|
| **Generate a new enterprise repo** (C++, Rust, Go, Java, Python, TypeScript, or any other language) | Conversationally via an AI agent (Claude / Gemini / Codex) that runs the interview, **or** deterministically: fill `project.yaml` and run [`render.py`](../tools/render.py) |
| **Work on the factory** (add a language, maintain templates) | The `profile-author` role + [`eaao_lint.py`](../tools/eaao_lint.py) + the render-smoke |

A generated repo ships, on day zero: the agent contract (AGENTS/CLAUDE/GEMINI), the
cross-language source tree `it.d4np.<project>`, the full docs system (ADR, patterns, spec, bug
ledger, journal, workflow, **releases**), the GitHub automation pack (CI + release + Dependabot
+ CODEOWNERS + issue forms + labels + a setup script), the quality gate
(`consistency_lint.py`), the SemVer/release flow, and — opt-in — **i18n**, **social
announcements**, and **benchmarks**.

**Composable agent roles** ([registry](../agent/README.md)): `enterprise-architect`,
`reviewer`, `security-auditor`, `release-manager`, `profile-author`.

**Self-improvement (safe, versioned, human-gated):** a [lessons ledger](../learning/README.md)
(memory), [`autotune.py`](../tools/autotune.py) (default tuning from run history),
[`self_review.py`](../tools/self_review.py) + [`eval/rubric.md`](../eval/rubric.md)
(self-evaluation), and the [stay-current routine](../maintenance/stay-current.md) (keeps
profiles modern). Every improvement is a draft PR a human approves — no opaque magic.

---

## 2. How it works

Three layers feed one renderer:

```
PROFILES (toolchain knowledge as data)  ┐
MANIFEST (your answers: project.yaml)   ┼──→ TEMPLATES ({{PLACEHOLDER}}) ──→ generated repo
PLACEHOLDER DICTIONARY (authoritative)  ┘
```

The architect runs a 5-step loop (plus memory): **Recall** (read lessons) → **Interview** →
**Resolve profile** → **Manifest** (you confirm) → **Render** → **Verify & hand off** →
**Record** (write lessons). Rendering is a Mustache subset; an unresolved placeholder is a hard
error. [`eaao_lint.py`](../tools/eaao_lint.py) and the render-smoke keep the factory itself
congruent in CI.

**The tools** (all standard-library Python, run from the repo root):

| Tool | Purpose |
|---|---|
| `python .eaao-core/tools/render.py <manifest> --in-place \| --out <dir>` | Render a manifest into a repository (deterministic) |
| `python .eaao-core/tools/eaao_lint.py` | Self-lint: placeholder integrity, profile completeness, playbook references |
| `python .eaao-core/tools/self_review.py <repo>` | Structural completeness review of a generated repo |
| `python .eaao-core/tools/autotune.py` | Propose default changes from accumulated run records |
| `tools/consistency_lint.py` | Shipped *into* each generated repo; enforces its cross-artifact congruence |

---

## 3. Running it (two paths)

**Conversational** — open the repo with an AI agent; it reads `AGENTS.md`, runs
[`interview.md`](../orchestrator/interview.md), writes `project.yaml` for your confirmation, then
follows [`generate.md`](../orchestrator/generate.md). If a step fails, it follows
[`recovery.md`](../orchestrator/recovery.md).

**Deterministic** — no agent needed. With this factory copied into your repo
(`<your-repo>/.eaao-core/`), `--in-place` generates the project into that repo, next to
`.eaao-core/` (which the rendered `.gitignore` excludes); use `--out <dir>` for a separate copy:

```bash
cp .eaao-core/orchestrator/project.yaml.template .eaao-core/orchestrator/project.yaml
# edit it — see .eaao-core/orchestrator/examples/reference.yaml for a worked manifest
python .eaao-core/tools/render.py .eaao-core/orchestrator/project.yaml --in-place
python tools/consistency_lint.py
```

---

## 4. What is FIXED — strict, do not change

These invariants are enforced by the lints and the agent contract; changing them breaks the
factory's guarantees.

| Invariant | Why it is load-bearing |
|---|---|
| **English on disk** (except derived i18n copies) | Cross-project consistency |
| **Agent-vs-human boundary** — the agent *drafts*; the human *opens / merges / publishes*. Never push to the default branch, never merge, never publish | Safety & auditability |
| **The placeholder dictionary is authoritative** — a template may only use defined placeholders | Enforced by `eaao_lint` |
| **Profile completeness** — every `<lang>.yaml` defines every `_schema.md` key | Enforced by `eaao_lint` |
| **Language knowledge is data, not code** — never hardcode a tool into a template | Genericity / open to any language |
| **Normative source tree** `src/{main,test,bench}/<lang>/<group>/<slug>/` | One shape across languages (ADR-0002) |
| **One source of truth per fact** (manifest → placeholders) | Anti-drift |
| **The generated repo governs itself** (no coupling back to EAAO) | Independence |
| **A rendered repo must pass `consistency_lint` + `self_review`** day zero | Quality floor |
| **Conventional Commits · one logical change per PR · one PR at a time** | Workflow |
| **`.eaao-core/` tooling self-locates** (ROOT-relative) | Don't scatter the machinery |

---

## 5. What you CAN customize

| What | Where | Effect |
|---|---|---|
| **Org defaults** | [`config/defaults.yaml`](../config/defaults.yaml) | branch, license, group path, coverage, scopes, i18n — precedence: overlay > profile > built-in |
| **House rules** | [`config/house-rules.md`](../config/house-rules.md) | injected as §13 of every generated `AGENTS.md` (wins over a conflicting default) |
| **Custom agent roles** | [`config/agents/`](../config/README.md) | add or override a role |
| **A new language** | copy [`profiles/_template.yaml`](../orchestrator/profiles/_template.yaml) → `<lang>.yaml` + ADR | any language; never edit templates |
| **The interview** | [`questionnaire.yaml`](../orchestrator/questionnaire.yaml) + [`interview.md`](../orchestrator/interview.md) | questions / follow-ups |
| **Scaffolding content** | `templates/**` | as long as placeholders stay in the dictionary |
| **Per project** | `project.yaml` | every value + the capability flags (`bench, threading, public_api, i18n, packaging, service, announce`) |
| **Memory / tuning** | [`learning/lessons.yaml`](../learning/README.md), `autotune` threshold, `stay-current` cadence | how the agent learns and stays current |

**Golden rule:** if a change would make `eaao_lint`/`consistency_lint` fail or violate the
agent-vs-human boundary → it is **fixed**. If it is a *value*, an *overlay*, a *profile*, or a
*capability* → it is **customizable**. Either way it stays versioned and reviewable.

---

## 6. Distribution bundle (ship just the factory)

The bundle is the factory you **operate** — `.eaao-core/` + the agent contract + `LICENSE` —
without this repository's own CI, changelog, and governance files. It is the easiest way to hand
EAAO to someone who only needs to *use* it.

### Get it (consumers) — no clone required

Download the ready-made bundle from the **latest GitHub release** and unpack it:

```bash
curl -L -o pgs-eaao-bundle.tar.gz \
  https://github.com/danielPoloWork/pgs-eaao/releases/latest/download/pgs-eaao-bundle.tar.gz
tar xzf pgs-eaao-bundle.tar.gz && cd pgs-eaao
# or, with the GitHub CLI:
#   gh release download --repo danielPoloWork/pgs-eaao --pattern 'pgs-eaao-bundle.tar.gz'
```

Then read [`.eaao-core/README.md`](../README.md) and run the factory (open the folder with an AI
agent, which auto-loads `AGENTS.md`, or call `render.py` directly). `git clone` is the *other*
path: it gives you the full repository (CI, changelog, history) and is for **contributing to
EAAO**, not for using it.

### What's in it

The whole factory (`.eaao-core/`, including its tools, templates, profiles, docs, and
[`.eaao-core/README.md`](../README.md)), the agent contract (`AGENTS.md` / `CLAUDE.md` /
`GEMINI.md`), and `LICENSE`. **`LICENSE` is kept on purpose**: `render.py` reads it as the source
for each generated project's license, so removing it would yield license-less projects.

The `export-ignore` rules in `.gitattributes` strip two groups: **repo-management plumbing** (CI,
issue/PR templates, Dependabot, CODEOWNERS, the portfolio card, `.gitignore`, `CHANGELOG.md`) and
**this repo's identity/governance docs** (`README.md`, `SECURITY.md`, `CONTRIBUTING.md`, and the
i18n translations under `docs/i18n/` — the generated project renders its own, and the i18n
translates this repo's own README).

### Build or publish one (maintainers)

Every published release attaches the bundle automatically: the `.github/workflows/release.yml`
workflow runs on release and uploads `pgs-eaao-bundle.tar.gz` / `.zip` with version-less names, so
`…/releases/latest/download/pgs-eaao-bundle.tar.gz` is a stable link. To build one by hand from a
clone:

```bash
git archive --format=tar.gz --prefix=pgs-eaao/ -o pgs-eaao-bundle.tar.gz HEAD
git archive HEAD | tar tf - | sort   # preview contents without writing a file
```

## 7. Go deeper

- [`AGENTS.md`](../../AGENTS.md) — the binding contract (source of truth).
- [`orchestrator/`](../orchestrator/README.md) — the engine (interview, generate, placeholders, profiles, recovery).
- [`agent/`](../agent/README.md) — the role registry.
- [`config/`](../config/README.md) · [`learning/`](../learning/README.md) · [`eval/rubric.md`](../eval/rubric.md) · [`maintenance/stay-current.md`](../maintenance/stay-current.md) — customization & self-improvement.
