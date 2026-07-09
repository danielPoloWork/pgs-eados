# Milestone M16 — Model & Effort Routing

**Status:** planning · **Predecessor:** M15 (in progress; only 16.4 depends on an M15 item)
**Owner:** `@danielPoloWork` · **Planned:** 2026-07-09

## Theme

Teach EADOS to recommend — and, where the host allows, apply — the **right model tier and effort
level per unit of work**. Today the maintainer routes by hand (the M15 issue set was assessed
manually on 2026-07-09). M16 turns that judgement into policy-as-data: a routing spec mapping work
signals to a capability tier + effort, a dated per-host model catalog, a pure evaluator, and
surfacing through the read-points that already exist (Step-0 triage, `/eados status`, the
`.issues/` planning docs).

## Ratified decisions (2026-07-09)

1. **Advisory-first.** No host lets an agent switch its own top-level session model; that remains a
   human action (e.g. `/model`). Auto-application is only real for *delegated* subagent work where
   the host supports per-delegation model selection. The human keeps final model authority
   (RFC-0001 human-in-the-loop).
2. **Tiers, not model names, in policy.** `routing.yaml` speaks `frontier-reasoning` / `standard` /
   `fast`; the dated catalog `models.yaml` maps tiers to current names per host (today, Claude
   Code: Fable 5 / Opus 4.8 / Sonnet 5). Models churn; policy must not rot. Precedent:
   risk-weights-as-data (#79), README model ranking (#122).
3. **Effort scale is OS-neutral:** `low` | `medium` | `high` | `max`, with documented host aliases
   (Claude Code: "ultracode" → `max`).
4. **Signals are what the tracker already carries:** `severity:*`, `area:*`, type labels, plus two
   derived flags — `sets-pattern` (first of its class; followers inherit a cheaper route) and
   `decision-heavy` (the decision *is* the deliverable: ADR / architecture).

## Sequence (one PR each, in order)

| Item | Issue | Title | Effort | Routing |
|---|---|---|---|---|
| 16.1 | [#252](https://github.com/danielPoloWork/pgs-eados/issues/252) | Routing policy as data + ADR (`os/routing/routing.yaml` + `models.yaml` + `_schema`) | M | frontier-reasoning / high (decision-heavy, sets-pattern) |
| 16.2 | [#253](https://github.com/danielPoloWork/pgs-eados/issues/253) | `tools/route_advice.py` — pure evaluator + thin `gh` shell + batch mode | M | standard / high |
| 16.3 | [#254](https://github.com/danielPoloWork/pgs-eados/issues/254) | Surface advice: Step-0 triage, `/eados status`, planning-doc `Routing` column, M15 backfill | M | standard / medium |
| 16.4 | [#255](https://github.com/danielPoloWork/pgs-eados/issues/255) | Auto-apply for delegated subagent work via host adapters (depends on M15 [#239](https://github.com/danielPoloWork/pgs-eados/issues/239)) | M | standard / medium |

## M15 backfill table (feeds 16.3 / #254)

Maintainer-reviewed assessment of 2026-07-09, expressed in M16 vocabulary
(tier — today's Claude Code model — / effort):

| Issue | Routing | Rationale |
|---|---|---|
| [#234](https://github.com/danielPoloWork/pgs-eados/issues/234) | frontier-reasoning (Fable 5) / max | decision-heavy: the ADR the whole milestone hangs on |
| [#235](https://github.com/danielPoloWork/pgs-eados/issues/235) | standard (Opus 4.8) / high | meticulous verification, not design |
| [#236](https://github.com/danielPoloWork/pgs-eados/issues/236) | standard (Opus 4.8) / medium | mechanical but wide rename + ADR |
| [#237](https://github.com/danielPoloWork/pgs-eados/issues/237) | fast (Sonnet 5) / medium | doc reconciliation against recorded history |
| [#238](https://github.com/danielPoloWork/pgs-eados/issues/238) | fast (Sonnet 5) / low | small doc-drift fix |
| [#239](https://github.com/danielPoloWork/pgs-eados/issues/239) | frontier-reasoning (Fable 5) / high | sets-pattern: cross-host adapter design all commands inherit |
| [#240](https://github.com/danielPoloWork/pgs-eados/issues/240) | standard (Opus 4.8) / high | broad but contained template/orchestrator decisions |
| [#241](https://github.com/danielPoloWork/pgs-eados/issues/241) | frontier-reasoning (Fable 5) / high | security posture |
| [#242](https://github.com/danielPoloWork/pgs-eados/issues/242) | frontier-reasoning (Fable 5) / high | sets-pattern: first cross-cutting command, fixes the template |
| [#243](https://github.com/danielPoloWork/pgs-eados/issues/243) | standard (Opus 4.8) / medium | follows the #242 pattern |
| [#244](https://github.com/danielPoloWork/pgs-eados/issues/244) | standard (Opus 4.8) / high | follows the #242 pattern; measurement design adds weight |
| [#245](https://github.com/danielPoloWork/pgs-eados/issues/245) | fast (Sonnet 5) / medium | persona + example authoring |
| [#246](https://github.com/danielPoloWork/pgs-eados/issues/246) | standard (Opus 4.8) / high | follows the #242 pattern; QA-ownership wiring |
| [#247](https://github.com/danielPoloWork/pgs-eados/issues/247) | frontier-reasoning (Fable 5) / max | largest design surface of the milestone (brownfield interview + routing) |
| [#248](https://github.com/danielPoloWork/pgs-eados/issues/248) | standard (Opus 4.8) / high | renderer/template materialization, contained decisions |
| [#249](https://github.com/danielPoloWork/pgs-eados/issues/249) | frontier-reasoning (Fable 5) / high | schema-first budget design + enforcement coherence |
| [#250](https://github.com/danielPoloWork/pgs-eados/issues/250) | frontier-reasoning (Fable 5) / high | enforcement coherent with the gate model, multi-tool |

## Out of scope (invariants)

- The agent switching its own top-level session model — a host limitation and a governance choice;
  the OS prints the advice and stops (RFC-0001 human-in-the-loop).
- Hardcoding model names in policy or code — names live only in the dated `models.yaml` catalog.
- A new phase — routing is metadata and advice over existing surfaces, not pipeline structure.
- Autonomous agent merge/publish authority (RFC-0001 N2) — agent drafts, human merges.
