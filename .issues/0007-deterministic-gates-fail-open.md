# [GAP] Deterministic gates fail open: `skipped` never blocks, and `--links` is accepted but never evaluated

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#210](https://github.com/danielPoloWork/pgs-eados/pull/210) (issue [#200](https://github.com/danielPoloWork/pgs-eados/issues/200), CLOSED; commit `4917815`); `--strict` fails `needs-input` (distinct from `skipped`), and the dead `--links` gate-path plumbing was removed (`links` stays live on the doctor path). Guarded by `test_eados.py` + `test_phase_smoke.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `enhancement`, `severity:medium`, `area:orchestrator`, `gates`
**Component:** `.eados-core/tools/eados.py`

## Summary

In `eados.py`, only an explicit `FAIL` flips `ok = False`; `skipped` and `[manual]` always
pass. Several skip paths make a gate **silently satisfiable by omission**:

1. `_ev_roadmap_covers` returns `skipped` when `delivery_state.refs.rfcs` is empty — so a
   project that simply never recorded its RFC refs passes the `plan → scaffold`
   `roadmap-covers-rfcs` gate with exit 0. The cheapest way to satisfy the gate is to not
   record the input it checks.
2. `_ev_rfc_approved` returns `skipped` without `--rfc` — the `design` phase exits 0 with
   zero verification unless the caller remembers the flag.
3. `main()` loads `links.yaml` and threads `ctx["links"]` — but **no evaluator reads it**.
   The documented `traceability-lint` gate is never evaluated in-process even when the data
   is present (dead parameter / silent under-delivery vs. the docs).

## Impact

Exit code 0 from `eados.py <phase>` reads as "gates green" in scripts and agent loops, but
can mean "gates not evaluated". Fail-open gate semantics are the opposite of the project's
fail-closed posture everywhere else (installer, renderer, loader).

## Proposed fix

- Distinguish `skipped` (input not applicable) from `needs-input` (input missing), and add
  `--strict` (default in CI) where `needs-input` fails.
- In `design` phase specifically, make a missing `--rfc` a `needs-input`, not a skip, when
  `delivery_state.refs.rfcs` is non-empty.
- Wire a `traceability-lint` evaluator that consumes `ctx["links"]` via `traceability.py`,
  or remove the `--links` plumbing until it does (no dead affordances).