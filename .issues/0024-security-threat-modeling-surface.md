# [FEATURE] Discoverable security / threat-modeling surface (audit sub-mode)

> **✅ Delivered** (2026-07-10, closes [#241](https://github.com/danielPoloWork/pgs-eados/issues/241)).
> `/eados security` ships as the first **alias adapter** (→ `audit.md`'s new *Threat-modeling
> sub-mode* section); every generated repo scaffolds `docs/security/threat-model.md` (STRIDE per
> trust boundary) + the `docs/security/README.md` surface, owned by the `security-auditor`
> (authority + ownership-map row added); `risk.yaml` `threat_model:` block pins
> artifact/method/owner as data (schema in lockstep). The `command-adapters` lint learned the
> alias-adapter class. Item 3 (partially mechanizing `risk-register-present`) was **considered and
> deferred to #250's enforcement-hardening residuals**, recorded in `audit.md`. Guarded by
> `test_threat_model.py` + the extended `test_command_adapters.py`.

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

A **sub-mode/alias of `audit`** (not a new phase — per ADR-0019, the taxonomy ADR drafted
as 0022):

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
green. Cites ADR-0019.

**Depends on:** ADR-0019 (taxonomy; draft 0022, delivered), 0011 (adapters + alias table).
