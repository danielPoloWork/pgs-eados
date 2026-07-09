# [TASK] Reconcile the 0001–0010 defect backlog (fixed in-tree, still open) + add a regression index

**Labels:** `chore`, `severity:high`, `area:docs`, `governance`
**Component:** `.issues/0001`–`.issues/0010`, `CHANGELOG.md`, `.eados-core/docs/adr/`, `.eados-core/tools/tests/`
**Milestone:** M15 — Command Surface & Governed Assistants · **Wave 0**

## Context

The ten defect/hardening tickets `.issues/0001-0010` are **already fixed in the working tree**
(fix tags observed: #194, #199, #200, #201, #203, #213, #214) yet remain **open**. For an
enterprise repository this gives an auditor a materially **false open-work picture** — a
backlog-hygiene debt in its own right. Separately, there is **no index tying each closed defect to
its guarding test**, so a future refactor could silently regress a fixed defect without a red gate.

## Direction

1. **Close the trail** — mark 0001–0010 resolved and move them to a resolution trail
   (`CHANGELOG.md` entries and/or an ADR), each linking the fix commit/PR and the tag.
2. **Regression index** — add a mapping (issue number → guarding test, e.g.
   `test_phase_runner.py`, `test_render_guards.py`, `test_eados.py`) so every closed defect has a
   named test that must stay green.
3. **Protect the shared invariant** — add a lint asserting **every write routes through
   `sandbox.safe_write`** (the no-clobber path that closed 0002/0003), so the fix cannot be
   silently bypassed by new code.

## Acceptance

0001–0010 are marked resolved with a linked trail; the regression index resolves every issue number
to a test that exists and passes; the `safe_write` lint is green and fails on a synthetic direct
write. No new code beyond the lint + index; this is reconciliation, not re-fixing.
