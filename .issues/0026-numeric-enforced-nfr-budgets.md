# [FEATURE] Numeric, enforced NFR budgets (scalability / hardware / store)

**Labels:** `enhancement`, `severity:medium`, `area:orchestrator`, `area:templates`
**Component:** `.eados-core/orchestrator/domains/*.yaml`, `.eados-core/orchestrator/os/workflow/workflow.yaml` (overlay gates), `.eados-core/orchestrator/interview.md` (Q5.3)
**Milestone:** M15 — Command Surface & Governed Assistants · **Wave 3**

## Context

The domains' `nfr_axes` carry a **boolean `hard_budget` only** — there is no enforced number. The
game domain's "60fps" lives as a **YAML comment**, and `scalab*` has **zero occurrences** in the
factory content. So the maintainer's "worthy of AAA/enterprise scaling" promise has **no mechanical
enforcement**: an NFR budget is an honor-system placeholder, not a gate. This is the enforcement
whitespace behind the `scalability` wishlist verb (whose design-phase fold is 0019).

## Direction

1. **Numeric at intake** — a Q5.3 follow-up forces a **value** per hard NFR axis (e.g. target FPS,
   p99 latency, memory ceiling, cold-start budget), typed per domain.
2. **Surfaced as gates** — the numeric budgets become **audit-phase overlay gates** (evaluated, not
   just declared), consistent with the domain overlay mechanism.
3. **Vocabulary** — add scalability/load vocabulary to spec §3 guidance so the design fold (0019)
   has content to elicit against.

## Acceptance

A domain run (e.g. `game`, `service`) elicits **numeric** budgets per hard axis; the audit overlay
gate evaluates them and fails on a missing/violated number; no honor-system boolean remains for a
hard axis; the game "60fps" is a typed value, not a comment. Self-lint + `_schema.md` green in the
same PR (§7 lockstep).

**Depends on:** 0020 (posture/domain materialization), 0019 (scalability design fold).
