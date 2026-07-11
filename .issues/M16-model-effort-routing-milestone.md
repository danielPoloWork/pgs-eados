# Milestone M16 — Model & Effort Routing

**Status:** in progress · **Predecessor:** M15 (in progress; only 16.4 depends on an M15 item)
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

| Item | Issue | Title | Effort | Routing                                                  |
|---|---|---|---|----------------------------------------------------------|
| 16.1 | [#252](https://github.com/danielPoloWork/pgs-eados/issues/252) | Routing policy as data + ADR (`os/routing/routing.yaml` + `models.yaml` + `_schema`) | M | frontier-reasoning / high (decision-heavy, sets-pattern) |
| 16.2 | [#253](https://github.com/danielPoloWork/pgs-eados/issues/253) | `tools/route_advice.py` — pure evaluator + thin `gh` shell + batch mode | M | standard / high                                          |
| 16.3 | [#254](https://github.com/danielPoloWork/pgs-eados/issues/254) | Surface advice: Step-0 triage, `/eados status`, planning-doc `Routing` column, M15 backfill | M | standard / medium                                        |
| 16.4 | [#255](https://github.com/danielPoloWork/pgs-eados/issues/255) | Auto-apply for delegated subagent work via host adapters (depends on M15 [#239](https://github.com/danielPoloWork/pgs-eados/issues/239)) | M | opus4.8 / medium                                         |

## Delivery record

| Item | Issue | PR | Status |
|---|---|---|---|
| 16.1 | #252 | [#257](https://github.com/danielPoloWork/pgs-eados/pull/257) | **merged 2026-07-09** — `os/routing/` spec + ADR-0017 (catalog folded into `routing.yaml` as `catalog:`, stated deviation from the sketched `models.yaml`) |
| 16.2 | #253 | [#258](https://github.com/danielPoloWork/pgs-eados/pull/258) | **merged 2026-07-09** — `route_advice.py`: pure core + loud spec rejection + `--milestone` batch |
| 16.3 | #254 | [#259](https://github.com/danielPoloWork/pgs-eados/pull/259) | draft PR open — triage/status surfaces + `.issues/README.md` protocol; **M15 backfill APPLIED 2026-07-09** (owner-approved: the table below written to #234–#250 as `Routing:` body lines) |
| 16.4 | #255 | — | draft PR open — `os/routing/delegation.md` (the delegation hook: applied on hosts with per-delegation model control, advisory-only elsewhere; the four-role relay worked example); wired from `commands/README.md` §Host adapters + `os/routing/_schema.md` + ADR-0017; `routing-delegation` self-lint keeps it host-complete |

## M15 backfill table (feeds 16.3 / #254) — applied 2026-07-09

Maintainer-reviewed assessment of 2026-07-09, expressed in M16 vocabulary
(tier — today's Claude Code model — / effort; "ultracode" = the Claude Code alias of `max`):

| Issue                                                           | Title (summary) |  Model                                                                                                        | Effort        | Routing                             | Rationale                                                                |
|-----------------------------------------------------------------|---|--------------------------------------------------------------------------|---------------|-------------------------------------|--------------------------------------------------------------------------|
| ✅[#234](https://github.com/danielPoloWork/pgs-eados/issues/234) | [Wave 0] Ratify the command‑surface taxonomy (foundational ADR of M15)                                       |  **Fable 5** | **ultracode** | frontier-reasoning (Fable 5) / ultracode  | decision-heavy: the ADR the whole milestone hangs on                     |
| ✅[#235](https://github.com/danielPoloWork/pgs-eados/issues/235) | [Wave 0] Reconcile defect backlog 0001–0010 + regression index (severity: high)                              |  **Opus 4.8** | **high**      | standard (Opus 4.8) / high          | meticulous verification, not design                                      |
| ✅[#236](https://github.com/danielPoloWork/pgs-eados/issues/236) | [Wave 0] Rename phase ``refactor`` → ``migrate`` + ADR                                                       |  **Opus 4.8** | **medium**    | standard (Opus 4.8) / medium        | mechanical but wide rename + ADR                                         |
| ✅[#237](https://github.com/danielPoloWork/pgs-eados/issues/237) | [Wave 0] ROADMAP.md outdated: M10–M13 delivered but never recorded                                           |  **Sonnet 5** | **medium**    | fast (Sonnet 5) / medium            | doc reconciliation against recorded history                              |
| ✅[#238](https://github.com/danielPoloWork/pgs-eados/issues/238) | [Wave 0] Doc drift: ``commands/init.md`` and ``AGENTS.md`` omit ``web`` domain and Q0.5                      |  **Sonnet 5** | **low**       | fast (Sonnet 5) / low               | small doc-drift fix                                                      |
| ✅[#239](https://github.com/danielPoloWork/pgs-eados/issues/239) | [Wave 1] Host adapters: ``/eados ``<cmd>`` as discoverable slash‑command (severity: high)                    |  **Fable 5** | **high**      | frontier-reasoning (Fable 5) / high | sets-pattern: cross-host adapter design all commands inherit             |
| ✅[#240](https://github.com/danielPoloWork/pgs-eados/issues/240) | [Wave 1] Design‑phase folds: API contracts, data/schema, budget, algorithms                                  |  **Opus 4.8** | **high**      | standard (Opus 4.8) / high          | broad but contained template/orchestrator decisions                      |
| ✅[#241](https://github.com/danielPoloWork/pgs-eados/issues/241) | [Wave 1] Security/threat‑modeling surface discoverable (audit sub‑mode)                                      |  **Fable 5** | **high**      | frontier-reasoning (Fable 5) / high | security posture                                                         |
| ✅[#242](https://github.com/danielPoloWork/pgs-eados/issues/242) | [Wave 2] ``/eados ``debug`` — governed defect investigation + bug ledger                                     |  **Fable 5** | **high**      | frontier-reasoning (Fable 5) / high | sets-pattern: first cross-cutting command, fixes the template            |
| ✅[#243](https://github.com/danielPoloWork/pgs-eados/issues/243) | [Wave 2] ``/eados ``refactor`` — pattern‑guided code‑quality refactoring                                     |  **Opus 4.8** | **medium**    | standard (Opus 4.8) / medium        | follows the #242 pattern                                                 |
| ✅[#244](https://github.com/danielPoloWork/pgs-eados/issues/244) | [Wave 2] ``/eados ``optimize`` — measure‑first optimization against NFR budgets                              |  **Opus 4.8** | **high**      | standard (Opus 4.8) / high          | follows the #242 pattern; measurement design adds weight                 |
| ✅[#245](https://github.com/danielPoloWork/pgs-eados/issues/245) | [Wave 2] QA/test‑engineer persona + working ``config/agents/`` example                                       |  **Sonnet 5** | **medium**    | fast (Sonnet 5) / medium            | persona + example authoring                                              |
| ✅[#246](https://github.com/danielPoloWork/pgs-eados/issues/246) | [Wave 2] ``/eados ``testcases`` — governed test generation (QA‑owned)                                        |  **Opus 4.8** | **high**      | standard (Opus 4.8) / high          | follows the #242 pattern; QA-ownership wiring                            |
| ✅[#247](https://github.com/danielPoloWork/pgs-eados/issues/247) | [Wave 3] ``/eados ``adopt`` — brownfield adoption interview (severity: high)                                 |  **Fable 5** | **ultracode** | frontier-reasoning (Fable 5) / ultracode  | largest design surface of the milestone (brownfield interview + routing) |
| ✅[#248](https://github.com/danielPoloWork/pgs-eados/issues/248) | [Wave 3] ``governance.posture: ``enterprise`` has no effect on rendered output                               |  **Opus 4.8** | **high**      | standard (Opus 4.8) / high          | renderer/template materialization, contained decisions                   |
| ✅[#249](https://github.com/danielPoloWork/pgs-eados/issues/249)  | [Wave 3] Numeric and *enforced* NFR budgets (scalability/hardware/store)                                     |  **Fable 5** | **high**      | frontier-reasoning (Fable 5) / high | schema-first budget design + enforcement coherence                       |
| ✅[#250](https://github.com/danielPoloWork/pgs-eados/issues/250)  | [Wave 3] Honor‑system hardening: ``git_check.py``, ``gate_results`` persistence, evaluator traceability‑lint |  **Fable 5** | **high**      | frontier-reasoning (Fable 5) / high | enforcement coherent with the gate model, multi-tool                     |

## Out of scope (invariants)

- The agent switching its own top-level session model — a host limitation and a governance choice;
  the OS prints the advice and stops (RFC-0001 human-in-the-loop).
- Hardcoding model names in policy or code — names live only in the dated `models.yaml` catalog.
- A new phase — routing is metadata and advice over existing surfaces, not pipeline structure.
- Autonomous agent merge/publish authority (RFC-0001 N2) — agent drafts, human merges.
