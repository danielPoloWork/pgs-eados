# `/eados plan` — negotiate the roadmap from the approved RFCs

The `plan` phase turns approved RFCs into a **negotiated** milestone roadmap. Owned by the
**producer** (the roadmap guardian); co-created with `product-manager` and `tech-lead`. Protocol:
[`../os/plan/negotiation-protocol.md`](../os/plan/negotiation-protocol.md); config:
[`../os/plan/plan.yaml`](../os/plan/plan.yaml).

## Preconditions

- The design phase produced ≥1 approved RFC (recorded in `delivery_state.refs.rfcs`).
- `phase_runner.py <manifest>` reports `-> plan` (or the manifest is already at `phase: plan`).

## Procedure

1. **Negotiate** — run [`negotiation-protocol.md`](../os/plan/negotiation-protocol.md) with the
   roles from [`plan.yaml`](../os/plan/plan.yaml): `product-manager` proposes priorities →
   `tech-lead` attaches T-shirt sizes (`sizing_scale`) + flags tech debt → `producer` reconciles
   capacity × dates into milestones (using the domain's `milestone_vocabulary`). Each step edits a
   concrete artifact.
2. **Check authority** — before writing the roadmap, the producer confirms it may:
   ```bash
   python .eados-core/tools/authority_check.py producer ROADMAP.md
   ```
3. **Write the roadmap** — produce/update `ROADMAP.md`: milestones with pre-numbered items, each
   item referencing the RFC it implements (so the gate can trace it).
4. **Gate: roadmap-covers-rfcs** — every approved RFC must be addressed by ≥1 milestone:
   ```bash
   python .eados-core/tools/traceability.py ROADMAP.md $(rfc ids from delivery_state.refs.rfcs)
   ```
   Must pass before `plan → scaffold` is legal.
5. **Record the cross-links** — add the milestone ids to `delivery_state.refs.milestones` (feeds
   the traceability graph; references, not content).
6. **Propose the transition** — emit the checkpoint for `plan → scaffold` (human-gated):
   ```bash
   python .eados-core/tools/phase_runner.py <manifest> --propose scaffold
   ```
   The agent writes the emitted checkpoint + `phase: scaffold` **after** the human confirms.
7. **Record the run** — append the phase-tagged run record (the learning loop's uniform shape;
   every phase leaves the same audit trail, #250):
   ```bash
   python .eados-core/tools/record_run.py <manifest> --phase plan   # add --failure GATE=MSG on a red gate
   ```
8. **Hand off** — to [`/eados scaffold`](../generate.md): render the repository as today, now with
   the roadmap and spec already agreed.

## Boundary

The agent **drafts** the roadmap and **proposes** the transition. The human **decides scope** in
the negotiation (cuts are a human call) and **confirms** the human-gated move. No roadmap ships
that leaves an RFC uncovered; no phase advances on the agent's authority (`AGENTS.md` §6).
