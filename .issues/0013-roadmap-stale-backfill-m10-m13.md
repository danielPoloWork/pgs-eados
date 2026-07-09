# [BUG] ROADMAP.md is stale: M10–M13 delivered but never recorded (lockstep invariant broken)

**Labels:** `bug`, `severity:medium`, `area:docs`, `governance`
**Component:** `.eados-core/docs/rfc/ROADMAP.md`, `.eados-core/tools/eados_lint.py`

## Summary

`ROADMAP.md` declares itself "the **single source of truth** for EADOS's own delivery plan, from
start to finish", and the cross-cutting invariants section binds every milestone to keep it in
sync "in the same PR". Its status table and sections end at **M9 / v2.2.0** — while the CHANGELOG
and the published releases document four further delivered milestones:

- **M10** — post-v2.3.0 repository-audit remediation (v2.4.0)
- **M11** — PR-metadata contract, milestone seeding (`seed_milestones.py`), CI-live bootstrap gate (v2.5.0)
- **M12** — `web` domain + enterprise posture, authoring languages (ADR-0016), spec import branch, pattern elicitation, layered scaffold, preflight (v2.5.0)
- **M13** — audit remediation & learning loop: run recorder, lesson sweep/audit, provenance, spec-substance floor (v2.6.0)

The lockstep invariant was broken for four consecutive milestones.

## Proposed fix

1. Backfill the M10–M13 sections (goal, delivered items with PR references, acceptance recap)
   reconstructed from `CHANGELOG.md` and `gh` milestone/PR data, and extend the status table
   through v2.6.0.
2. Prevent recurrence mechanically: extend the existing `version-lockstep` gate in `eados_lint.py`
   (roadmap-freshness: the highest milestone named in the CHANGELOG's released sections must
   appear in ROADMAP.md's status table).

One PR for the backfill, one for the gate (or together if small).
