# [TASK] Ratify the command-surface taxonomy (ADR): phase vs sub-mode vs cross-cutting vs adapter

**Labels:** `enhancement`, `severity:high`, `area:orchestrator`, `adr`
**Component:** `.eados-core/docs/adr/`, `.eados-core/docs/rfc/0001-eados-delivery-os.md`, `.eados-core/orchestrator/commands/README.md`
**Milestone:** M15 — Command Surface & Governed Assistants · **Wave 0**

## Context

The maintainer's command wishlist is a flat menu of eleven one-shot verbs
(`interview/debug/refactor/optimizecode/systemdesign/api/database/scalability/security/testcases/pseudocode`),
but EADOS models work as a *small, gated phase machine over a manifest*, and RFC-0001 explicitly
rejects a monolithic orchestrator. Minting eleven phases would betray that design. The owner
**ratified a hybrid taxonomy on 2026-07-09**; this ADR records it so every downstream M15 command
issue has a single, cited authority instead of an alias line buried in draft 0019.

## Direction

Write an ADR under `docs/adr/` that classifies **every** wishlist verb into exactly one class:

1. **Design sub-modes** — `systemdesign`, `api`, `database`, `scalability`, `pseudocode` deepen the
   existing `design` phase (see 0019). No new phase, no new state.
2. **Audit sub-mode** — `security` is a sub-mode/alias of `audit` (see 0024).
3. **Cross-cutting commands** — `debug`, `optimize`, `refactor`-cleanup form a small new class in the
   same category as `/eados status` and `/eados review`: **advisory, non-state-advancing, still
   gated and human-confirmed** (see 0016/0017/0018).
4. **Adapters + alias table** — all verbs surface via host adapters (0011) and a canonical alias
   table in `commands/README.md`.

Amend **RFC-0001 non-goals** to explicitly admit the bounded cross-cutting-command class (so it is
not read as scope creep toward a monolith), and **decide the governance boundary**: may a
cross-cutting code command (`debug`/`optimize`/`refactor`) run against pasted/standalone code with
**no active `delivery_state` manifest**, or does it require an initialized project? This decision
prevents the ungoverned-chatbot failure mode and is a precondition for 0016/0017/0018.

## Acceptance

ADR merged and numbered sequentially; RFC-0001 non-goals updated to name the cross-cutting class;
`commands/README.md` documents the four-class taxonomy; the manifest-or-not governance boundary is
stated; every M15 command issue (0011, 0016–0019, 0024, 0025) cites this ADR. Self-lint green.
