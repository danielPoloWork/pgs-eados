# ADR-0019: Command-surface taxonomy — phases, sub-modes, cross-cutting commands, adapters

## Status

Accepted (2026-07-10)

## Context

The maintainer's command wishlist is a flat menu of eleven one-shot verbs
(`interview / debug / refactor / optimizecode / systemdesign / api / database / scalability /
security / testcases / pseudocode`). EADOS, however, models work as a **small, gated phase
machine over a persistent manifest** (RFC-0001 §3), routes deterministically by phase +
ownership — never by fuzzy intent (RFC-0001 D2) — and explicitly rejects a monolithic 360°
orchestrator (RFC-0001 §1). Minting eleven phases would betray all three commitments; leaving
the verbs unmapped keeps the surface undiscoverable and invites exactly the ad-hoc, ungoverned
handling the OS exists to prevent.

The owner ratified a hybrid taxonomy on 2026-07-09 (M15 plan, decision 1; drafted as issue 0022 /
[#234](https://github.com/danielPoloWork/pgs-eados/issues/234)). This ADR records it as the single
citable authority for every M15 command issue, and decides the **governance boundary** the
cross-cutting code commands (#242/#243/#244/#246) were blocked on: may they run against
pasted/standalone code with no active `delivery_state` manifest?

## Decision

Every wishlist verb classifies into **exactly one** of four classes. The classes — not the verbs —
are the extension points of the command surface, and each class is closed: extending it takes an
ADR, never an ad-hoc addition.

1. **Phases.** The state machine stays the closed set
   `init → design → plan → scaffold → audit → refactor` (→ `migrate` once the #236 rename lands)
   defined in `workflow.yaml`. **No wishlist verb mints a phase.** `interview` is not a command at
   all: it is the intake of `init` (and of the planned brownfield front door `/eados adopt`, #247)
   and surfaces only as an alias.

2. **Phase sub-modes** — a deepened entry into an existing phase.
   `systemdesign`, `api`, `database`, `scalability`, `pseudocode` → sub-modes of `design` (#240);
   `security` (controls + threat modeling) → sub-mode of `audit` (#241). A sub-mode adds **no new
   state, no new transition, no new authority**: its artifacts are the phase's artifacts, its
   gates the phase's gates, its owner the phase's owner. `database` stays inside ADR-0004's frame
   (SQL remains a secondary Q1.2 component; no primary profile, no standalone command).

3. **Cross-cutting commands** — the class `/eados status` and `/eados review` already occupy,
   extended by `debug` (#242), `refactor` in its code-quality meaning (#243, after the #236
   rename vacates the name), `optimize` (#244 — the wishlist's `optimizecode`), and `testcases`
   (#246, QA-owned per #245; ratified as cross-cutting by the M15 plan's wishlist mapping).
   Members are **advisory and non-state-advancing** — they never write `delivery_state.phase` and
   never propose a phase transition — and everything they *do* write is **fully governed**:
   role-owned per `authority.yaml`, deterministically gated, human-confirmed, one logical change
   per drafted PR, artifacts landing only in governed surfaces (bug ledger, `docs/benchmarks`,
   patterns catalogue, `src/test/**`). Read-only members (`status`) satisfy these obligations
   vacuously — they produce no artifacts. A new member requires an ADR, exactly like a new phase.

4. **Adapters + aliases** — surfacing, not semantics. Every verb reaches users through thin host
   adapters (#239) and the **canonical alias table in `orchestrator/commands/README.md`**. An
   alias only routes a verb to its class target; it never adds behavior, state, or authority. The
   README table is the single registry the adapter-coverage check (#239) enforces against.

**Governance boundary — a manifest is required.** A cross-cutting code command runs **only
against an initialized project**: a repository whose manifest carries `delivery_state`. Given
pasted or standalone code with no active manifest, the command **refuses and routes** — greenfield
to `/eados init`, an existing ungoverned repository to `/eados adopt` (#247). A plain *question*
about code stays a Step-0 triage question (`0-question` in `triage.yaml` — answered directly,
no command run); what requires the manifest is the
*command run*, because everything a command produces presupposes governance: its artifacts need a
governed surface to land in, its owner is resolved from `authority.yaml` path globs (no paths →
no owner → no gate), and its PR needs traceability edges (RFC ↔ milestone ↔ PR) to anchor.
Dropping the boundary would rebuild the ungoverned per-snippet code chatbot that the M15 plan
lists as out of scope — this ADR closes that door deliberately.

**Alternatives rejected.** (a) *Eleven phases* — state-machine explosion; betrays RFC-0001 D2/D3
and the §1 monolith rejection. (b) *A free-standing "code assistant" mode* outside the manifest —
the ungoverned chatbot by another name. (c) *Intent-classification routing* of the flat verb menu
— already rejected as RFC-0001 D2 (arbitrary, non-deterministic). (d) *Aliases only, no taxonomy*
— leaves every downstream issue re-deciding phase-vs-command from scratch; an alias line buried in
a draft is not an authority.

## Consequences

- **RFC-0001 §2 gains non-goal N5** admitting the bounded cross-cutting class explicitly, so the
  class cannot be read as scope creep toward the rejected monolith.
- **`orchestrator/commands/README.md` documents the four classes and the canonical alias table**;
  planned commands appear there as planned, so the surface registry is complete before Wave 2
  ships.
- **#242/#243/#244/#246 are unblocked** with a citable precondition (manifest required, refusal
  route stated); #240/#241 build sub-modes without new machinery; #239's adapter-coverage check
  gets its canonical verb list. The M15 command drafts (0011, 0016–0019, 0024, 0025) cite this
  ADR.
- The `refactor` naming collision is resolved by sequencing, not by this ADR: the taxonomy defines
  the end-state; the phase rename (#236) must land before the cross-cutting `refactor` command
  (#243) may ship.
- Nothing changes in the phase machine, the manifest schema, or any tool today — this ADR is
  pure recorded authority; the machinery lands through the cited M15 issues.

## References

- Issue [#234](https://github.com/danielPoloWork/pgs-eados/issues/234) (draft 0022) — the
  decision request; owner ratification 2026-07-09 (`.issues/M15-command-surface-milestone.md`).
- RFC-0001 §1 (monolith rejected), §2 (goals/non-goals), §3 (phase machine), D2/D3 (routing and
  orchestration forks).
- ADR-0004 (SQL stays secondary), ADR-0011 (the phase-machine pivot), ADR-0014 (`/eados review`
  precedent for advisory cross-cutting), ADR-0015 (posture orthogonality — the sibling M15
  authority for #248).
- M15 issues: #239 (adapters), #240 (design folds), #241 (security sub-mode), #242 (debug),
  #243 (refactor-cleanup), #244 (optimize), #245/#246 (QA persona + testcases), #247 (adopt),
  #236 (phase rename).
