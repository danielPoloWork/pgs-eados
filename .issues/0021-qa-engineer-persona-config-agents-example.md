# [FEATURE] Fill the persona gaps (QA/test engineer first) and ship a worked `config/agents/` example

**Labels:** `enhancement`, `severity:low`, `area:agent`
**Component:** `.eados-core/agent/`, `orchestrator/os/authority/authority.yaml`, `config/agents/`

## Context

The registry ships 9 roles, but test authorship falls implicitly to the tech-lead (owns
`src/**`) and test enforcement to the reviewer — no QA/test-engineer role owns the verification
strategy end-to-end. Likewise there is no data-engineer/DBA, performance-engineer, or SRE
persona, and `authority.yaml`'s ownership map has no globs for those surfaces. Meanwhile the
extension point designed for exactly this — `config/agents/` — ships empty (`.gitkeep` only),
and `defaults.yaml` / `house-rules.md` are blank scaffolds: an organization gets no worked
example of adding a role despite the README documenting the mechanism.

The M14 palette (debug/refactor/optimize, drafts 0016–0018) raises the value of a QA-shaped
owner for verification artifacts.

## Direction

1. **Ship `agent/qa-engineer.md`** + its `authority.yaml` record (engineering pillar; owns
   `src/test/**` and the spec's §6 verification strategy; may_draft test plans; approves nothing
   alone) + registry row — the existing `agent-registry` / `authority-personas` lints cover it
   automatically (anti-fragmentation invariant).
2. **Worked example in `config/agents/`** — a documented sample role file (e.g. a commented
   `example-role.md`) plus a filled-in `defaults.yaml` snippet, so the overlay mechanism is
   copy-adaptable.
3. **Document the boundary** — DBA / performance-engineer / SRE are *organization overlays*
   (config/agents/), not shipped roles, until a domain profile needs them (keeps the shipped
   registry small; same logic as ADR-0004 for languages).

## Acceptance

`qa-engineer` passes both persona lints and appears in the registry table; a maintainer can add
a custom role by copying the worked example without reading tool source; M15 scope.
