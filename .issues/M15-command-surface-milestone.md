# Milestone M15 — Command Surface & Governed Assistants

**Status:** planning · **Predecessor:** M14 (v2.8.0 — agent-contract hardening & runtime re-grounding)
**Owner:** `@danielPoloWork` · **Planned:** 2026-07-09

## Theme

Turn the maintainer's flat wishlist menu of eleven one-shot verbs into a **discoverable, governed
command surface** — host adapters + `design`/`audit` sub-modes + a small class of cross-cutting
commands — **without minting eleven phases** or weakening the manifest / gate / human-in-the-loop
model (RFC-0001). Restore governance-doc integrity **first**, so the wave lands on a trustworthy base.

## Ratified decisions (2026-07-09)

1. **Taxonomy = hybrid** (ADR in 0022): `systemdesign/api/database/scalability/pseudocode` →
   `design` sub-modes; `security` → `audit` sub-mode; `debug/optimize/refactor-cleanup` →
   cross-cutting commands (class of `status`/`review`); all via adapters + alias table.
2. **`enterprise` = posture that must materialize** (0020): stays orthogonal to
   software/web/game/mobile but must change rendered output (`{{POSTURE}}`/`IF_ENTERPRISE` +
   compliance/docs index + stricter gate selection).
3. **Rename brownfield `refactor` → `migrate` in Wave 0** (0014): frees `/eados refactor` for the
   code-cleanup command (0017) and lets `/eados adopt` (0015) route to `migrate`.
4. **Reconcile the 0001–0010 backlog in Wave 0** (0023): already fixed in-tree but left open — close
   with a trail + regression index.

## Waves (sequenced by dependency)

### Wave 0 — Unblock & integrity (P0)
| Issue | Title | Effort |
|---|---|---|
| 0022 | Command-surface taxonomy ADR | S |
| 0023 | Reconcile 0001–0010 backlog + regression index | S |
| 0014 | Rename brownfield `refactor` → `migrate` | M |
| 0013 | Backfill roadmap M10–M14 + freshness lint | M |
| 0012 | Fix `init.md`/`AGENTS.md` doc-drift (Q0.4 web, Q0.5 posture) | S |

### Wave 1 — Surface folded design/audit capabilities (P0/P1)
| Issue | Title | Effort |
|---|---|---|
| 0011 | Host adapters + canonical alias table (resolve `.claude/commands` vs `.claude/skills` split) | M |
| 0019 | Design-phase folds with per-item depth (api/database/scalability/pseudocode/systemdesign) | L |
| 0024 | Discoverable security / threat-modeling surface (audit sub-mode) | S |

### Wave 2 — New cross-cutting code commands (P1)
| Issue | Title | Effort |
|---|---|---|
| 0016 | `/eados debug` — governed defect investigation | M |
| 0017 | `/eados refactor` — code-quality command (after rename) | M |
| 0018 | `/eados optimize` — measure-first performance | M |
| 0021 | `qa-engineer` persona + worked `config/agents/` example | M |
| 0025 | `/eados testcases` — governed test generation (QA-owned) | M |

### Wave 3 — Brownfield & materialization (P1/P2)
| Issue | Title | Effort |
|---|---|---|
| 0015 | `/eados adopt` — brownfield adoption front door | L |
| 0020 | Enterprise posture + domain profiles materialize at render | L |
| 0026 | Numeric, enforced NFR budgets | M |
| 0010-res | Harden honor-system enforcement (`git_check.py`, `gate_results`, traceability-lint) | L |

## Wishlist → command mapping (target end-state)

| Wishlist verb | Resolves to | Via |
|---|---|---|
| interview | `/eados init` (+ `adopt` for brownfield) | alias |
| systemdesign · api · database · scalability · pseudocode | `/eados design` | sub-mode (0019) |
| security | `/eados audit` | sub-mode (0024) |
| debug | `/eados debug` | cross-cutting (0016) |
| refactor (cleanup) | `/eados refactor` | cross-cutting (0017, after 0014 rename) |
| optimizecode | `/eados optimize` | cross-cutting (0018) |
| testcases | `/eados testcases` | cross-cutting, QA-owned (0025 + 0021) |

## Refinements to fold into existing drafts when picked up

- **0013** — retitle/rescope: the backfill spans **M10–M14 (five milestones)**, not M10–M13; the
  freshness lint must key off the README/CHANGELOG version, currently v2.8.0.
- **0019** — split the omnibus into per-item work with **worked-example depth** each; add
  `systemdesign` explicitly to the alias set (today it is implied, not named).
- **0020** — now a **ratified requirement** (decision 2), not optional; scope also covers the
  domain-profile materialization gap (6 of 8 domain fields never reach disk).
- **0021** — links forward to **0025** (the QA persona owns the new `testcases` command).

## GitHub tracker mapping

Every work item is tracked as a GitHub issue in milestone
[`M15 — command surface & governed assistants`](https://github.com/danielPoloWork/pgs-eados/milestone/15)
(all assigned to `@danielPoloWork`). The in-repo drafts remain the canonical spec; the issues
carry the labels, wave, and dependency header.

| Draft | GitHub issue | Draft | GitHub issue |
|---|---|---|---|
| 0022 | [#234](https://github.com/danielPoloWork/pgs-eados/issues/234) | 0018 | [#244](https://github.com/danielPoloWork/pgs-eados/issues/244) |
| 0023 | [#235](https://github.com/danielPoloWork/pgs-eados/issues/235) | 0021 | [#245](https://github.com/danielPoloWork/pgs-eados/issues/245) |
| 0014 | [#236](https://github.com/danielPoloWork/pgs-eados/issues/236) | 0025 | [#246](https://github.com/danielPoloWork/pgs-eados/issues/246) |
| 0013 | [#237](https://github.com/danielPoloWork/pgs-eados/issues/237) | 0015 | [#247](https://github.com/danielPoloWork/pgs-eados/issues/247) |
| 0012 | [#238](https://github.com/danielPoloWork/pgs-eados/issues/238) | 0020 | [#248](https://github.com/danielPoloWork/pgs-eados/issues/248) |
| 0011 | [#239](https://github.com/danielPoloWork/pgs-eados/issues/239) | 0026 | [#249](https://github.com/danielPoloWork/pgs-eados/issues/249) |
| 0019 | [#240](https://github.com/danielPoloWork/pgs-eados/issues/240) | 0010-res | [#250](https://github.com/danielPoloWork/pgs-eados/issues/250) |
| 0024 | [#241](https://github.com/danielPoloWork/pgs-eados/issues/241) | | |
| 0016 | [#242](https://github.com/danielPoloWork/pgs-eados/issues/242) | | |
| 0017 | [#243](https://github.com/danielPoloWork/pgs-eados/issues/243) | | |

## Out of scope (invariants)

- Autonomous agent merge/publish authority (RFC-0001 N2) — agent drafts, human merges.
- Turning EADOS into an ungoverned per-snippet code chatbot — every command routes through a
  manifest/gate/human confirmation.
- A runtime kernel / scheduler / event bus (RFC-0001 N1).
- A fifth domain or a primary SQL/database profile (ADR-0004 keeps SQL secondary).
