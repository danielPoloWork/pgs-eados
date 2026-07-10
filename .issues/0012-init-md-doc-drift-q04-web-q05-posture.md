# [BUG] Doc drift: `commands/init.md` and `AGENTS.md` omit the `web` domain and Q0.5

> **✅ Delivered** (2026-07-10, closes [#238](https://github.com/danielPoloWork/pgs-eados/issues/238)).
> `commands/init.md` step 2 now says "Q0.1–Q0.5" with the four-target list (`software`/`web`/
> `game`/`mobile`) + a one-line posture note; `AGENTS.md` §3's domain axis is now
> `{software,web,game,mobile}`. Docs-only.

**Labels:** `bug`, `severity:low`, `area:commands`, `docs`
**Component:** `.eados-core/orchestrator/commands/init.md`, `AGENTS.md`

## Summary

The interview moved ahead of the documents that invoke it. Since M12 (ADR-0015),
`interview.md` Phase 0 defines **four** targets at Q0.4 (`software / web / game / mobile`) plus
**Q0.5 — enterprise posture**; two governed documents still describe the pre-M12 state.

## Details

1. `commands/init.md` step 2: "run interview Phase 0 (**Q0.1–Q0.4**), including
   `Q0.4 — development target` (**`software` / `game` / `mobile`**)" — `web` is missing from the
   target list and Q0.5 is not part of the Phase-0 range.
2. `AGENTS.md` §3: "A parallel **domain axis** (`orchestrator/domains/{software,game,mobile}.yaml`)"
   — `web.yaml` is missing from the enumeration.

`interview.md` lines 43–57 and `questionnaire.yaml` are correct; `domains/web.yaml` exists and is
lint-gated (`domain-completeness`).

## Impact

An agent following `init.md` literally never offers the `web` target (the shipped seed for the
most common modern case) and never asks the posture question — silently reverting ADR-0015 for
pipeline users while the classic full-interview path applies it.

## Proposed fix

Update `init.md` step 2 to "Phase 0 (Q0.1–Q0.5)" with the four-target list and a one-line posture
note (default `standard`); update `AGENTS.md` §3 to `{software,web,game,mobile}`. Docs-only, one PR.
