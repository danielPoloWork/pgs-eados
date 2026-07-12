# EADOS commands — the `/eados` surface

The opt-in phase commands a host exposes as `/eados <phase>`. Each is a thin entry point that runs
its phase's procedure and reports the **legal next move** via the deterministic
[`phase_runner.py`](../../tools/phase_runner.py) — which reads the manifest's
`delivery_state.phase` and [`workflow.yaml`](../os/workflow/workflow.yaml). The agent **proposes**
a transition; the human **confirms** every human-gated one (`AGENTS.md` §6).

## Step-0 — triage (before you pick a command)

Not every request is a generation run. Before any phase machinery, classify the request and route it
to the **minimal** path — the ordered, **stop-at-first-match** procedure in
[`../triage.yaml`](../triage.yaml) (data, not a hardcoded branch):

1. **question / status read** → answer directly (or `/eados status`); never enter the pipeline.
2. **bounded maintenance edit** to the factory (a tool, a spec, a doc, a profile) → one focused
   change → a drafted PR. It stays fully governed — the changed paths must resolve to a glob the role
   owns (`authority`), one PR at a time, and the human opens + merges (`AGENTS.md` §6) — it simply
   does **not** spin up interview → profile → manifest → render.
3. **generate or evolve a governed repository** → the full five-step loop (`/eados scaffold`).

`triage.yaml` carries worked `examples:` of each call, shape-checked by `eados_lint`'s `examples`
gate (#224). The point is to avoid firing the whole pipeline at a one-line doc fix while keeping a
maintenance edit under the same ownership + human-gate rules as everything else.

Once the route is decided (a `focused-change` or the `five-step-loop`), the host also **states the
recommended model tier + effort** for the work ahead — `triage.yaml` `routing_advice`, the
[`os/routing`](../os/routing/_schema.md) policy (ADR-0017) evaluated by
[`route_advice.py`](../../tools/route_advice.py). Advisory only: the human keeps final model
authority, and the session model is never switched by the agent.

| Command | Phase | Status | Procedure | What it does |
|---------|-------|--------|-----------|-------------|
| `/eados init` | init | **available** (M1) | [`init.md`](init.md) | Frame a new project, load the domain profile, write the manifest skeleton (`delivery_state`). |
| `/eados adopt` | init (brownfield intake) | **available** (M15 W3) | [`adopt.md`](adopt.md) | Brownfield intake for an existing repo: a read-only gap map + goal menu → a manifest whose `adoption:` record makes `init → audit` / `init → migrate` legal, human-gated. |
| `/eados design` | design | **available** (M2) | [`design.md`](design.md) | Author or import an RFC under the review protocol. |
| `/eados plan` | plan | **available** (M3) | [`plan.md`](plan.md) | Negotiate the roadmap from approved RFCs and build the traceability graph. |
| `/eados scaffold` | scaffold | **available** (today's factory) | [`../generate.md`](../generate.md) | Generate the governed repository from the manifest — the classic factory (render + `consistency_lint`). |
| `/eados audit` | audit | **available** (M4) | [`audit.md`](audit.md) | Continuous risk scoring + the enforced traceability lint and risk register. |
| `/eados migrate` | migrate | **available** (M5) | [`migrate.md`](migrate.md) | Bring an existing repo up to standard via gated, sandboxed, **additive** PRs. |
| `/eados status` | — (any) | **available** (M6) | [`status.md`](status.md) | Read-only doctor: current phase, legal next moves, traceability coverage at a glance. |
| `/eados review` | — (any) | **available** (M8) | [`review.md`](review.md) | Evaluate an inbound PR against the contribution policy and draft a disposition — **recommends, never merges**. |
| `/eados debug` | — (any) | **available** (M15 W2) | [`debug.md`](debug.md) | Governed defect investigation: reproduce → root-cause → one-change fix + regression test → bug-ledger record. |
| `/eados refactor` | — (any) | **available** (M15 W2) | [`refactor.md`](refactor.md) | Behavior-preserving code-quality refactoring: a green suite on both sides, guided by the patterns catalogue. |
| `/eados optimize` | — (any) | **available** (M15 W2) | [`optimize.md`](optimize.md) | Measure-first performance work against a numeric NFR budget: baseline → one change → re-measure. |
| `/eados testcases` | — (any) | **available** (M15 W2) | [`testcases.md`](testcases.md) | QA-owned test generation against spec §6: a green suite, or an `xfail` with a linked defect. |

`/eados status`, `/eados review`, `/eados debug`, `/eados refactor`, `/eados optimize`, and
`/eados testcases` are **cross-cutting** — not phases that advance. `/eados status` is a
**read-only doctor** (current phase, legal moves, traceability coverage at a glance; roadmap 6.4);
`/eados review` evaluates an **inbound PR** against the contribution policy and drafts a
recommended disposition (M8) — it **recommends, never merges**; `/eados debug` (#242) is the first
cross-cutting **code** command — governed defect investigation (reproduce → root-cause →
one-change fix + regression test → bug-ledger record); `/eados refactor` (#243) is
**behavior-preserving** code-quality refactoring (a green test suite on both sides of the change,
guided by the patterns catalogue); `/eados optimize` (#244) is **measure-first** performance work
(a numeric NFR budget, a benchmark baseline, one change, a re-measure — never "make it faster" on
a hunch); `/eados testcases` (#246) is governed **test generation** against spec §6 — the first
code command owned by the **`qa-engineer`** (not the tech-lead), producing a green suite (or an
`xfail` with a defect linked via `/eados debug`). The code commands **draft, never merge, and
never advance state**, and all follow the shape [`debug.md`](debug.md) set for the Wave-2 code
commands.

## Host adapters — `/eados <cmd>` as a discoverable slash command (#239, ADR-0019 class 4)

The canonical procedure is the markdown here; a **host adapter** surfaces it as a native command.
An adapter is a **pointer, never a copy** — it names the owning role and instructs the agent to
read and follow the canonical procedure file, exactly as `CLAUDE.md` / `GEMINI.md` point at
`AGENTS.md`. It carries no procedure body, so the file here stays the single source of truth.

- **Claude Code** (shipped): one adapter per available table row at
  **`.claude/commands/eados/<name>.md`** (repo root; in the bundle), surfacing as
  **`/eados:<name>`**. *Resolution of the commands-vs-skills split:* these are
  **`.claude/commands/`** slash commands, not `.claude/skills/` — an EADOS command is a
  **human-invoked, deterministic entry point**, which is exactly what a slash command is; a skill
  is model-triggered by description-matching, the fuzzy-intent routing RFC-0001 D2 rejects.
- **Codex** (documented): Codex auto-loads `AGENTS.md`, which points here — invoke a command by
  asking for it by name (`run /eados init`); a custom prompt registered in `~/.codex/prompts`
  may wrap the same one-line pointer.
- **Gemini Antigravity** (documented): `GEMINI.md` points at `AGENTS.md` → here; a project
  `.gemini/commands/` TOML entry may wrap the same pointer.

**Delivery.** The adapters travel **inside the release bundle** (tracked at the factory's repo
root, so `git archive` ships them). The guided installers place them **opt-in**: interactive runs
ask (default yes); scripted runs need `--with-adapters` / `-WithAdapters` (`--no-adapters` /
`-NoAdapters` declines, and a declined install neither scans nor touches `.claude/**` — the
additive no-clobber posture is unchanged).

**Enforced.** The `command-adapters` self-lint keeps this table and the adapters in lockstep,
symmetrically: every **available** row must ship an adapter that points at that row's own
procedure file; a **live alias-table verb** may optionally ship an **alias adapter** that must
point at its *target's* procedure (e.g. `/eados:security` → `audit.md`, #241 — an alias routes,
never adds behavior); and an adapter matching neither (a planned command/alias shipping early, a
deleted row) is an orphan failure — a new command cannot ship undiscoverable, and a planned one
cannot jump the queue.

**Routing hook — delegated sub-tasks carry a routed model + effort (#255, M16 16.4).** Surfacing a
command is one adapter job; the second is **applying** the model & effort routing (ADR-0017) when a
command **delegates** a sub-task. On a host with per-delegation model control (Claude Code's
Agent-tool `model:` parameter and subagent-definition `model:` frontmatter), the adapter resolves
the sub-task's route via [`route_advice.py`](../../tools/route_advice.py) and passes the concrete
model + effort with the delegation; on a host without it, the hook **degrades to advisory-only** —
it states the route and proceeds at the session model. The **top-level session model is never
switched** by the agent (a human action, e.g. `/model` — RFC-0001). The canonical contract, the
per-host application matrix, and the worked **architect → engineer → reviewer → optimizer** relay
live in [`../os/routing/delegation.md`](../os/routing/delegation.md).

## Command classes & the canonical alias table (ADR-0019)

The surface has exactly **four classes**
([ADR-0019](../../docs/adr/0019-command-surface-taxonomy.md)); each is closed — extending one
takes an ADR:

1. **Phases** — the `workflow.yaml` state machine above. No wishlist verb mints a phase.
   `interview` is the *intake* of this class, with two front doors: [`/eados init`](init.md)
   (greenfield) and [`/eados adopt`](adopt.md) (#247 — brownfield; the manifest lands at
   `phase: init` and the recorded `adoption:` block makes `init → audit`/`init → migrate`
   legal by data, ADR-0021).
2. **Phase sub-modes** — a deepened entry into an existing phase; no new state, transition, or
   authority. Design sub-modes: `systemdesign`/`api`/`database`/`scalability`/`pseudocode` (#240);
   audit sub-mode: `security` (#241).
3. **Cross-cutting commands** — advisory, **non-state-advancing** (never write
   `delivery_state.phase`), still role-owned, gated, and human-confirmed. Today: `status`,
   `review`, `debug` (#242 — the first cross-cutting *code* command; [`debug.md`](debug.md) is the
   shape the rest of the class follows), `refactor` (#243 — code-quality meaning, now the #236
   phase rename has vacated the name; behavior-preserving restructuring), and `optimize` (#244 —
   the wishlist's `optimizecode`; measure-first performance work against a numeric NFR budget),
   and `testcases` (#246 — governed test generation against spec §6, the first command owned by
   the `qa-engineer` rather than the tech-lead). This completes M15 Wave 2's cross-cutting class.
4. **Adapters + aliases** — the surfacing mechanism (#239). An alias routes a verb to its class
   target; it never adds behavior.

**Manifest boundary (ADR-0019).** A cross-cutting code command runs only against an initialized
project (a manifest with `delivery_state`). Pasted/standalone code → the command **refuses and
routes**: greenfield to `/eados init`, an existing ungoverned repo to
[`/eados adopt`](adopt.md) (#247).
Questions about code stay the Step-0 triage question route (`0-question` — answered directly,
no command run).

| Alias (wishlist verb) | Routes to | Class | Ref |
|---|---|---|---|
| `interview` | `/eados init` (brownfield: `/eados adopt`) | phase intake | #247 |
| `systemdesign` · `api` · `database` · `scalability` · `pseudocode` | `/eados design` | design sub-mode | #240 |
| `security` | `/eados audit` | audit sub-mode | #241 |
| `debug` | `/eados debug` | cross-cutting | #242 |
| `refactor` (code cleanup) | `/eados refactor` | cross-cutting | #243 |
| `optimizecode` | `/eados optimize` | cross-cutting | #244 |
| `testcases` | `/eados testcases` | cross-cutting, QA-owned | #246 |

A planned command keeps its `· planned` marker here until it ships; shipping adds its row to the
command table at the top **and** its host adapter (#239). This alias table is the **canonical
verb → command mapping**, and the `command-adapters` check (#239) reads both tables: every
`**available**` command row must ship its pointer adapter; a **live** alias verb here *may* ship
an optional alias adapter that must point at its target's procedure (#241 — `security` is the
first; `optimizecode` → `optimize.md` is the second, #244); and a planned command or alias must
ship none.

## The phase runner

```bash
python .eados-core/tools/phase_runner.py <manifest>
```

prints the legal next transitions for the manifest's current phase, each with its entry gates and
whether it is human-gated. It is **state-driven and deterministic, and never advances state on its
own** — it reports what is legal; the human decides. Example (a fresh manifest, phase `init`):

```text
current phase: init
legal next transitions:
  -> design   (gates: manifest-valid)  [human-gated — the owner confirms]
  -> audit    (gates: manifest-valid, adoption-recorded)  [human-gated — the owner confirms]
  -> migrate  (gates: manifest-valid, adoption-recorded)  [human-gated — the owner confirms]
```

(The two adoption edges, #247/ADR-0021, are listed for every manifest but stay NOT READY for a
greenfield project — their `adoption-recorded` gate reads `skipped` without the `adoption:` block
only `/eados adopt` writes.)

`--propose <to>` validates a *proposed* transition and **emits** the `delivery_state` checkpoint to
write — it does **not** write state (the agent does, after the human confirms a human-gated move):

```bash
python .eados-core/tools/phase_runner.py <manifest> --propose design
```

## The phase orchestrator

```bash
python .eados-core/tools/eados.py <phase> <manifest>     # or: eados.py status <manifest>
```

runs a phase's **deterministic outgoing gates** — read from `workflow.yaml` (no hardcoded chain) —
evaluating the ones it can (`manifest-valid`, `rfc-approved`, `roadmap-covers-rfcs`,
`adoption-recorded`, `nfr-budgets`, `traceability-lint`) via the sibling
tools and marking render-time / human gates `[manual]`, then prints the legal next transitions and
points at the procedure above for the authoring + human-gated steps. It is the **executable spine**
beneath the markdown procedures; like `phase_runner`, it **reports and gates — it never authors,
advances state, or writes**. `eados.py status` is the read-only doctor ([`status.md`](status.md)).
