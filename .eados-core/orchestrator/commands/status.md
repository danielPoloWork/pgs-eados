# `/eados status` — at-a-glance delivery health (the doctor)

A **read-only** readout of where a project sits in the pipeline and whether its lineage is whole. It
**reports; it never advances state or runs a phase.** Phase-agnostic — run it in any state; owned by
no single role.

## Procedure

```bash
python .eados-core/tools/doctor.py <manifest>
```

It prints, for the manifest's `delivery_state`:

- **current phase** — with its owning role and what it produces (from
  [`workflow.yaml`](../os/workflow/workflow.yaml));
- **legal next transitions** — each with its entry gates and whether it is human-gated (via the
  deterministic [`phase_runner.py`](../../tools/phase_runner.py));
- **refs** — the recorded `rfcs` / `milestones` cross-links;
- **traceability** — `roadmap-covers-rfcs` over `ROADMAP.md`, plus `traceability-lint` when a links
  file is present (via [`traceability.py`](../../tools/traceability.py)).

By default it looks for `ROADMAP.md` and `links.yaml` next to the manifest; `--root` / `--roadmap` /
`--links` override. It **exits non-zero when it finds an actionable problem** (an undeclared phase,
an uncovered RFC, or a dangling traceability edge), so it doubles as a pre-flight check.

## Boundary

Assessment only — `status` makes no change, proposes no transition, and runs no phase tool that
writes. To *act*, use the phase command the readout points to (`/eados <phase>`), per `AGENTS.md` §6.
