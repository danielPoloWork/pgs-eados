# [GAP] Phase-state advancement is honor-system: nothing verifies gates were green when `delivery_state.phase` changed

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#209](https://github.com/danielPoloWork/pgs-eados/pull/209) (issue [#199](https://github.com/danielPoloWork/pgs-eados/issues/199), CLOSED; commit `4b9af49`) + [#216](https://github.com/danielPoloWork/pgs-eados/pull/216) (live `gate_results`, issue #213, commit `978ddb3`); checkpoint chain + `at:`/`confirmed_by:`/`gate_results` validated. Optional `manifest_sha:` intentionally not adopted (the issue marked it optional; `manifest_rev` covers concurrency, #214). Guarded by `test_phase_runner.py`, `test_render_guards.py`, `test_phase_smoke.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `enhancement`, `severity:high`, `area:orchestrator`, `agentic-governance`
**Component:** `.eados-core/tools/phase_runner.py`, `eados.py`, `orchestrator/os/workflow/workflow.yaml`

## Summary

The phase engine deliberately "reports, never advances" — the **agent** edits
`delivery_state.phase` and appends the checkpoint. For an enterprise *agentic* OS this is a
trust hole: a hallucinating or shortcut-taking agent can simply write
`delivery_state.phase: scaffold` without ever satisfying `manifest-valid` /
`rfc-approved` / `roadmap-covers-rfcs`, and **no gate ever detects it after the fact**.

Concretely:

1. `emit_checkpoint` records only `{from, to, gates}` — no timestamp, no actor, no
   **gate results** (pass/fail evidence), no hash of the manifest at transition time.
2. Nothing validates the checkpoint chain: `validate_manifest` does not check that
   `delivery_state.checkpoints` forms a legal path through `workflow.yaml`, or that the
   current `phase` is reachable from the recorded chain.
3. A phase-skipped manifest is indistinguishable from a diligent one — the same problem
   #169 fixed for interview answers, unfixed for phase transitions.

## Impact

The whole "gate-enforced pipeline" claim rests on the agent's cooperation. The human
confirming a transition sees the agent's *narrative*, not mechanical evidence.

## Proposed fix (incremental)

- Extend the checkpoint schema: `at:` (ISO date), `gate_results:` (id → OK/manual),
  optionally `manifest_sha:`.
- Add a `delivery-state-consistent` check (in `validate_manifest` or eados_lint when
  pointed at a project): checkpoints must form a legal transition chain in the (overlay-
  applied) workflow, ending at the current `phase`; a human-gated transition must carry a
  `confirmed_by:` entry.
- `phase_runner --propose` already emits the checkpoint — make `eados.py` re-run the
  deterministic gates at proposal time and embed their results in the emitted block.