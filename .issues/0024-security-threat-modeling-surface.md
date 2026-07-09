# [FEATURE] Discoverable security / threat-modeling surface (audit sub-mode)

**Labels:** `enhancement`, `severity:medium`, `area:commands`, `area:agent`, `security`
**Component:** `.eados-core/orchestrator/commands/audit.md`, `.eados-core/agent/security-auditor.md`, `.eados-core/templates/docs/` (threat-model template), `.eados-core/orchestrator/os/risk/risk.yaml`
**Milestone:** M15 — Command Surface & Governed Assistants · **Wave 1**

## Context

Security is strong at the **role and phase** level — a dedicated defensive `security-auditor`
persona, a conditional deep-audit gate, and a risk register — but it has **no command identity**.
The only reference to a discoverable entry point is an aspirational alias line in draft 0019's
acceptance criteria, and the `risk-register-present` gate is wired `external`/`manual`. The
maintainer's `security` wishlist verb (controls + threat modeling) therefore has no front door.

## Direction

A **sub-mode/alias of `audit`** (not a new phase — per the taxonomy ADR 0022):

1. `/eados security` alias routes into an `audit` threat-modeling sub-mode via the adapter + alias
   table (0011).
2. Ship a **threat-model template** and a **STRIDE-style checklist** owned by the `security-auditor`,
   producing a governed threat-model artifact alongside the risk register.
3. Consider making `risk-register-present` **at least partially mechanical** (e.g. assert the
   register exists and covers the declared attack surface) rather than purely `external`/`manual`.

## Acceptance

`/eados security` is reachable via the adapter/alias and enters the audit threat-modeling sub-mode;
a fixture run renders a threat-model artifact with a STRIDE checklist owned by the security-auditor;
the wishlist mapping (`security → /eados audit`) is documented in `commands/README.md`; self-lint
green. Cites ADR 0022.

**Depends on:** 0022 (taxonomy ADR), 0011 (adapters + alias table).
