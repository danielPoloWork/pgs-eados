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

| Command | Phase | Status | Procedure |
|---------|-------|--------|-----------|
| `/eados init` | init | **available** (M1) | [`init.md`](init.md) |
| `/eados design` | design | **available** (M2) | [`design.md`](design.md) |
| `/eados plan` | plan | **available** (M3) | [`plan.md`](plan.md) |
| `/eados scaffold` | scaffold | **available** (today's factory) | [`../generate.md`](../generate.md) |
| `/eados audit` | audit | **available** (M4) | [`audit.md`](audit.md) |
| `/eados migrate` | migrate | **available** (M5) | [`migrate.md`](migrate.md) |
| `/eados status` | — (any) | **available** (M6) | [`status.md`](status.md) |
| `/eados review` | — (any) | **available** (M8) | [`review.md`](review.md) |

`/eados status` and `/eados review` are **cross-cutting** — not phases that advance. `/eados status`
is a **read-only doctor** (current phase, legal moves, traceability coverage at a glance; roadmap
6.4); `/eados review` evaluates an **inbound PR** against the contribution policy and drafts a
recommended disposition (M8) — it **recommends, never merges**.

**Portable.** The canonical procedure is the markdown here; a host wraps it with its own skill
mechanism (Claude Code `.claude/skills/`, a Codex/Gemini agent registry). The adapter is thin — it
points at the procedure, exactly as `CLAUDE.md` / `GEMINI.md` point at `AGENTS.md`.

## Command classes & the canonical alias table (ADR-0019)

The surface has exactly **four classes**
([ADR-0019](../../docs/adr/0019-command-surface-taxonomy.md)); each is closed — extending one
takes an ADR:

1. **Phases** — the `workflow.yaml` state machine above. No wishlist verb mints a phase.
2. **Phase sub-modes** — a deepened entry into an existing phase; no new state, transition, or
   authority. Design sub-modes: `systemdesign`/`api`/`database`/`scalability`/`pseudocode` (#240);
   audit sub-mode: `security` (#241).
3. **Cross-cutting commands** — advisory, **non-state-advancing** (never write
   `delivery_state.phase`), still role-owned, gated, and human-confirmed. Today: `status`,
   `review`. Ratified to join in M15 Wave 2: `debug` (#242), `refactor` — code-quality meaning,
   after the #236 phase rename (#243), `optimize` (#244), `testcases` (#246, QA-owned).
4. **Adapters + aliases** — the surfacing mechanism (#239). An alias routes a verb to its class
   target; it never adds behavior.

**Manifest boundary (ADR-0019).** A cross-cutting code command runs only against an initialized
project (a manifest with `delivery_state`). Pasted/standalone code → the command **refuses and
routes**: greenfield to `/eados init`, an existing ungoverned repo to `/eados adopt` (#247).
Questions about code stay the Step-0 triage question route (`0-question` — answered directly,
no command run).

| Alias (wishlist verb) | Routes to | Class | Ref |
|---|---|---|---|
| `interview` | `/eados init` (brownfield: `/eados adopt`) | phase intake | #247 |
| `systemdesign` · `api` · `database` · `scalability` · `pseudocode` | `/eados design` | design sub-mode | #240 |
| `security` | `/eados audit` | audit sub-mode | #241 |
| `debug` | `/eados debug` | cross-cutting | #242 · planned |
| `refactor` (code cleanup) | `/eados refactor` | cross-cutting | #243 · planned, after #236 |
| `optimizecode` | `/eados optimize` | cross-cutting | #244 · planned |
| `testcases` | `/eados testcases` | cross-cutting, QA-owned | #246 · planned, with #245 |

A planned command keeps its `· planned` marker here until it ships; shipping adds its row to the
command table at the top **and** its host adapter (#239). This alias table is the **canonical
registry**: the adapter-coverage check (#239) requires an adapter for every shipped target and
skips `· planned` rows.

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
```

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
evaluating the ones it can (`manifest-valid`, `rfc-approved`, `roadmap-covers-rfcs`) via the sibling
tools and marking render-time / human gates `[manual]`, then prints the legal next transitions and
points at the procedure above for the authoring + human-gated steps. It is the **executable spine**
beneath the markdown procedures; like `phase_runner`, it **reports and gates — it never authors,
advances state, or writes**. `eados.py status` is the read-only doctor ([`status.md`](status.md)).
