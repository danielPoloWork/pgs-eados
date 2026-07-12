# Milestone M18 — Consumer-Side Routing & Model Checkpoint

**Status:** planned · **Predecessor:** M16 (the routing policy, evaluator, factory surfaces, and
delegation hook this milestone extends to the consumer side)
**Owner:** `@danielPoloWork` · **Planned:** 2026-07-12

## Theme

M16 made model & effort routing **data** (ADR-0017) — but only the *factory* reads it: filed
issues carry a `Routing:` line, `.issues/` plan docs a `Routing` column, triage and `/eados
status` state the advice. The **consumer** — a repo that installs the OS and runs the phase
pipeline — gets none of it: `/eados plan` writes a `ROADMAP.md` whose items carry a T-shirt size
but no route, and nothing ever compares the model the session is *actually on* against the tier a
step was routed to. The owner named the gap directly (2026-07-12): the roadmap doesn't say which
model/effort each step deserves, and the OS never warns when the session model isn't the routed
one. M18 closes both halves — a route per roadmap item, and a mechanical, advisory checkpoint
with a recorded bypass — without touching the ADR-0017 authority boundary.

## Ratified decisions (2026-07-12)

1. **Tiers, not names — in the roadmap too.** A roadmap item's route speaks the `os/routing`
   vocabulary (`fast` / `standard` / `frontier-reasoning` × `low`–`max`); concrete model names
   stay in the dated `catalog:` alone. A roadmap that hardcodes a model name rots on the next
   market refresh (the ADR-0017 invariant, extended to the consumer artifact).
2. **The checkpoint is advisory, never a gate.** `--check` prints `ROUTE-OK` / `ROUTE-MISMATCH`
   and always exits 0. A blocking model check would claim authority the OS does not have — the
   human keeps final model authority (ADR-0017), and the bypass is therefore the *baseline*, not
   a feature: proceeding past the advice **is** the accepted mismatch.
3. **An accepted mismatch is recorded, not silent.** The bypass lands in the run record
   (`record_run.py`), so the override has an audit trail the learning loop can read. Legitimate
   and visible — the same posture as recorded dissent (ADR-0022 §10.4).
4. **No session auto-swap, ever.** No host lets an agent change its own session model, and the OS
   would not do it if one did — `delegation.md`'s hard limit is reaffirmed: auto-application is
   *downward only* (delegated subagent work, M16 16.4). The deliverable is the loud signal, not
   the wheel.
5. **Effort is recommended, never verified.** No host exposes the session's effort setting to the
   agent; the checkpoint verifies the model half only and says so in its output (the
   ADR-0015/0016 honesty posture). The session model itself comes from the agent's self-report —
   the tool trusts its `--current-model` argument and is honest about that provenance.
6. **Scope: consumer = a repo with `.eados-core/` installed.** Generated repos do not ship `os/`
   (17.2 precedent) and are out of scope; if routing should ever reach the generated contract, it
   enters through `templates/AGENTS.md.tmpl` as its own decision, not as a side effect here.

## Sequence (one PR each, in order)

| Item | Issue | Title | Effort | Routing |
|---|---|---|---|---|
| 18.1 | [#296](https://github.com/danielPoloWork/pgs-eados/issues/296) | `/eados plan` attaches a route per roadmap item (negotiation protocol + item format, tiers-not-names) | S | standard / medium (sets-pattern) |
| 18.2 | [#297](https://github.com/danielPoloWork/pgs-eados/issues/297) | Route checkpoint: `route_advice.py --check --current-model` + mismatch advisory + recorded bypass + phase-boundary line | M | standard / high |
| 18.3 | [#298](https://github.com/danielPoloWork/pgs-eados/issues/298) | Capstone: routing end-to-end docs — USAGE section, README bullet ×3 (i18n), delivery record | S | fast / low |

## Delivery record

| Item | Issue | PR | Status |
|---|---|---|---|
| 18.1 | #296 | [#300](https://github.com/danielPoloWork/pgs-eados/pull/300) | merged — a route per roadmap item (negotiation protocol + item format, tiers-not-names) |
| 18.2 | #297 | [#301](https://github.com/danielPoloWork/pgs-eados/pull/301) | merged — `route_advice.py --check` + `record_run.py --route-mismatch` + `phase_runner.py` boundary route line |
| 18.3 | #298 | — | this PR — USAGE §9 routing section, README bullet ×3 (i18n hash refreshed), this delivery record, CHANGELOG |

## Out of scope (invariants)

- **Session auto-swap** — the agent never changes its own model; the checkpoint recommends, the
  human re-invokes or proceeds (decision 4).
- **A blocking route gate** — advisory always; exit 0 always (decision 2).
- **Effort verification** — mechanically impossible today; claiming it would violate the honesty
  posture (decision 5).
- **Generated-repo routing** — the generated contract has no `os/` to read; separate decision if
  ever wanted (decision 6).
- **Model names in governed artifacts** — catalog-only, as everywhere since ADR-0017
  (decision 1).
