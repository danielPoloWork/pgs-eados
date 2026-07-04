# `workflow.yaml` — schema

The project **state machine**: the phases (states), the legal transitions between them, the
registry of gates a transition must clear, and the per-domain overlays that adapt the machine
to a target (software / web / game / mobile). The orchestrator is **state-driven**: a thin
deterministic checker reads the persistent manifest's current state plus this spec and computes
which transitions are *legal now*; the agent **proposes** a transition, the gates validate it
mechanically, and a human confirms every `human_gate: true` step. No transition is automatic.

`eados_lint` (`os-spec-completeness`) requires the instance to define every top-level key
below. The item shapes (documented here) are enforced at runtime by the workflow checker built
in M2; the lint guarantees the file parses and is structurally present.

## Required structure

```yaml
version:            # integer schema version (manifest pins the version it was written against)
states:             # the phases, in canonical order
transitions:        # legal, gated moves between states; never automatic
gates:              # the gate registry — lint/test/security/build/human checks, uniform shape
domain_overlays:    # per-domain adaptations (insert/remove states, add gates, reorder)
```

## Item shapes (runtime-enforced, M2)

- **`states[]`** — `{ id, role, produces[] }`. `id` is the phase name; `role` is the owning
  role from [`authority.yaml`](../authority/authority.yaml); `produces` lists the artifact
  kinds the phase writes.
- **`transitions[]`** — `{ from, to, entry_gates[], human_gate }`. `entry_gates` are gate
  ids that must pass before the move; `human_gate: true` requires explicit human confirmation.
- **`gates[]`** — `{ id, kind, runs, wired, blocking, required_for[] }`. `kind ∈
  {lint, test, security, build, human, manual}`; `runs` is the command or `human:<who>` /
  `manual:<description>`; `wired ∈ {in-process, external}` says who executes it —
  `in-process` = the deterministic checker (`eados.py`'s `GATE_EVALUATORS`; the
  `gate-executability` lint keeps the two in exact sync), `external` = the agent following the
  phase procedure, CI, or a human; `blocking: true` means a red gate halts the transition;
  `required_for` lists the transition `to`-states that depend on it.
- **`domain_overlays`** — a mapping `domain → { insert_states[], add_gates[], … }`. Absent
  keys mean "inherit the base machine unchanged".

## Invariants

- Every `transitions[].from`/`to` is a declared `states[].id`.
- Every `transitions[].entry_gates[]` and `gates[].required_for[]` references a declared id.
- Every executable `runs:` (`python <script> …`) names a script that exists — in the factory
  or shipped under `templates/` into every generated repo — and each `--flag` it passes appears
  in that script's source; gates marked `wired: in-process` are exactly `eados.py`'s
  `GATE_EVALUATORS` (both enforced by `eados_lint`'s `gate-executability`, #164).
- `scaffold` is the only state that renders the repository (today's factory); it reads the
  manifest like every other phase and writes files — it never calls another phase directly,
  so generation stays decoupled from governance (they share state via the manifest only).
