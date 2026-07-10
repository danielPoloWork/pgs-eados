# [FEATURE] `/eados debug` — governed defect investigation: reproduce → root-cause → fix + regression test → bug ledger

> **✅ Delivered** (2026-07-10, closes [#242](https://github.com/danielPoloWork/pgs-eados/issues/242)).
> `/eados debug` ships as the **first cross-cutting code command** (ADR-0019 class 3) and the
> shape #243/#244/#246 inherit: `commands/debug.md` (falsifiable intake → reproduce-first →
> root-cause → one-change fix + regression guard → ledger record + gated draft PR, with the
> worked fixture example), the **available** registry row + live `debug` alias + `/eados:debug`
> pointer adapter, and `tech-lead` authority over `docs/bugs/**` (`may_draft` + ownership-map
> row; the reviewer verifies red → green). Found and fixed in passing: the ledger prose
> documents `rejected` but the generated lint's `BUG_STATUSES` only knew `wontfix` — `rejected`
> is now accepted. Guarded by `test_debug_command.py`.

**Labels:** `enhancement`, `severity:medium`, `area:commands`
**Component:** `orchestrator/commands/` (new `debug.md`)

## Context

No debugging procedure exists anywhere in the factory (grep hits only build presets). The
*artifacts* it should end in already ship: the bug-ledger template (`templates/docs/bugs/`),
the generated `AGENTS.md.tmpl` §7 reproduce-and-root-cause discipline, the audit phase's
"confirmed defect → bug ledger" hand-off, and `consistency_lint.py`'s ledger-integrity check.
What is missing is the command that walks a defect from report to closed, governed record.

## Direction

A **cross-cutting** command (usable in any phase, like `/eados status`; class ratified in
ADR-0019, drafted as 0022), `commands/debug.md`. **Manifest required** (ADR-0019 boundary):
pasted/standalone code is refused and routed to `/eados init` / `/eados adopt`.
Fix authorship belongs to the **tech-lead** (owns `src/**`); the **reviewer** verifies.

1. **Intake** — the observed failing behavior (bug report, failing CI job, or user description);
   refuse vague intake the same way Phase 5 refuses untestable requirements.
2. **Reproduce first** — encode the failure as a failing test *before* touching the fix
   (the generated-repo §7 contract, applied to the factory's own palette).
3. **Isolate & root-cause** — narrate the hypothesis chain; the root cause is recorded, not just
   the symptom.
4. **Fix** — one logical change; the reproduction test flips green and stays as the regression
   guard.
5. **Record & close** — bug-ledger entry (id, root cause, fix PR, regression test ref); draft the
   gated PR with the standard cross-links; the human merges.

## Acceptance

Worked example on a fixture defect reaches a merged-shape PR draft with ledger record and
regression test; the command file states owner role, preconditions, gates, and boundary like the
existing eight; `commands/README.md` gains its row (and the draft-0011 adapter check covers it).
