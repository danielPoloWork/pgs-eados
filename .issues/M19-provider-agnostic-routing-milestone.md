# Milestone M19 — Provider-Agnostic Capability Routing

**Status:** planned · **Predecessor:** M16 (the routing policy and evaluator this milestone
generalizes) and M18 (the consumer-side checkpoint whose model-provenance decision it reconciles with)
**Owner:** `@danielPoloWork` · **Planned:** 2026-07-26

## Theme

M16 made model & effort routing **data** (ADR-0017) and got the central abstraction right: the
rules speak capability **tiers**, never model names. ADR-0017 even anticipated growth — *"a future
host (or a re-ranked market) is one catalog entry, not a schema change."*

That promise has never been exercised, and the gap between it and the shipped state is now
material. The owner named the requirement directly (2026-07-26): EADOS will not always run under
Claude — GPT, Gemini, Mistral, Qwen, Kimi, Sakana and others are all plausible — and the OS must
work out, **from whichever LLM it is actually running under**, the best model and effort for each
step, using the best available combination while treating tokens as a real but secondary
constraint.

Four things block that today, all verified in-tree on 2026-07-26:

1. **The catalog has one host.** `catalog.hosts` contains only `claude-code`, while
   `delegation.md`'s matrix documents `codex` and `gemini`. `route_advice.py --host codex` →
   `ERROR — unknown host`. The `routing-delegation` gate is one-way, so it never noticed (19.6).
2. **Nothing knows which host is running.** `_host_entry(spec, host=None)` returns `hosts[0]`, so
   every caller without an explicit `--host` silently receives Anthropic model names (19.4).
3. **Resolution is a name lookup**, not a capability match: `tier → "Opus 4.8"` per host. Context,
   effort ceiling, cost and availability are unrepresentable, so they cannot inform the decision
   (19.2, 19.3).
4. **No cost dimension, and freshness is a suggestion.** `catalog.as_of` is documented as *"the
   review cue"* with no gate — and the cue was missed: the catalog currently routes every ADR,
   security and foundational-decision unit of work to **Fable 5**, which all three READMEs
   describe as *not yet benchmarked for EADOS*, while **Opus 4.8**, which they call the best,
   sits one tier below (19.5).

M19 closes all four without disturbing what M16 got right.

## Ratified decisions (2026-07-26)

1. **Two-level catalog: `providers[] → models[]`, `hosts[] → providers[]`.** A provider is a
   vendor; a host is a runtime. The split is what makes model-agnostic hosts representable —
   `opencode` reaching six providers is one host entry, not six fictitious hosts. Adding either is
   configuration data, never code.
2. **Resolve by capability, not by name.** A model declares what it *meets* (`meets_tier`,
   `max_effort`, `context`, `relative_cost`). Resolution splits into **escalation → the floor**
   (unchanged, monotonic, deterministic) and **selection → the model** (cheapest reachable model
   that clears the floor).
3. **Quality-first with cost awareness, as a structural invariant, not a heuristic:**
   > **Cost may only choose among models that already clear the earned floor. It can never lower the floor.**
   "Minimum sufficient model" is not new behaviour — it is what the existing monotonic floor
   already computes. The floor is the minimum that satisfies quality; cost then picks the cheapest
   way to reach it. `protected:` (`label:security`, `label:adr`, `flag:decision-heavy`) is declared
   as data so the guarantee is checkable rather than merely true.
4. **Host identity comes from evidence, never from the model's self-belief.** Precedence: explicit
   flag / manifest declaration → environment markers declared per host as data → **unknown, loudly**.
   No `hosts[0]` default. Because tiers and efforts are vendor-neutral, an unknown host costs the
   model *name* and nothing else — the recommendation stays fully valid.
5. **Reconciliation with M18 decision 5.** M18 ratified that the consumer checkpoint takes the
   session model from `--current-model` and is *honest that the provenance is self-report*. That
   stands and is not reopened. The distinction M19 draws is narrower and compatible: an explicitly
   **supplied** model is authoritative input (ladder rung 1); what the OS must never do is
   **derive** the host by asking the agent to introspect. Where an agent fills the flag itself, the
   output labels the provenance as self-reported — exactly as M18 already requires.
6. **`extra` joins the effort scale**: `[low, medium, high, extra, max]`. Inserting a level changes
   what every existing `min_effort: high` rule means relative to the ceiling, so the rule table
   gets a deliberate re-read in 19.2 rather than a mechanical migration.
7. **Freshness becomes a gate** (`catalog.as_of` + `max_age_days`, per-model `verified:`).
   Auto-refreshing from vendor APIs is **rejected**: it needs network plus per-vendor auth inside a
   gate, and it re-runs the reasoning ADR-0009 §3 used to decline per-ecosystem SHA pinning. The
   catalog stays hand-maintained and staleness-gated.
8. **Unassessed models are catalogued, not credited.** Several named vendors have never been
   benchmarked for EADOS. A model the maintainer has not assessed is marked and **excluded from
   selection** rather than given an invented `meets_tier`. Fabricated capability claims are how
   this milestone's motivating bug (19.5) came to exist.

## Sequence (one PR each, in order)

| Item | Issue | PR | Title | Effort | Routing |
|---|---|---|---|---|---|
| 19.1 | [#322](https://github.com/danielPoloWork/pgs-eados/issues/322) | [#332](https://github.com/danielPoloWork/pgs-eados/pull/332) | ADR-0024 — provider-agnostic, capability-driven routing | L | frontier-reasoning / max (decision-heavy, sets-pattern) |
| 19.2 | [#323](https://github.com/danielPoloWork/pgs-eados/issues/323) | [#336](https://github.com/danielPoloWork/pgs-eados/pull/336) | Schema v2 — two-level catalog, capability models, five-level effort | L | frontier-reasoning / high (sets-pattern) |
| 19.3 | [#324](https://github.com/danielPoloWork/pgs-eados/issues/324) | [#337](https://github.com/danielPoloWork/pgs-eados/pull/337) | `route_advice` — resolve by capability, cheapest above the floor | M | standard / extra |
| 19.4 | [#325](https://github.com/danielPoloWork/pgs-eados/issues/325) | [#338](https://github.com/danielPoloWork/pgs-eados/pull/338) | Host detection from evidence — never default, never introspect | M | standard / high |
| 19.5 | [#326](https://github.com/danielPoloWork/pgs-eados/issues/326) | [#330](https://github.com/danielPoloWork/pgs-eados/pull/330) + [#339](https://github.com/danielPoloWork/pgs-eados/pull/339) | Catalog/README contradiction (data) + freshness & model-lockstep gates | M | standard / high |
| 19.6 | [#327](https://github.com/danielPoloWork/pgs-eados/issues/327) | [#340](https://github.com/danielPoloWork/pgs-eados/pull/340) | `routing-delegation` becomes two-way | S | fast / medium |
| 19.7 | [#328](https://github.com/danielPoloWork/pgs-eados/issues/328) | [#341](https://github.com/danielPoloWork/pgs-eados/pull/341) | Per-step routing + surfaces, docs, worked examples (capstone) | M | standard / medium |

**Delivery notes.** 19.5's data half shipped early as #330 — correcting a catalog that was routing
every ADR and security unit of work to a model the READMEs called unbenchmarked had no reason to
wait for its gate. Three gates enforced their own contracts unprompted during the milestone:
`routing-delegation` blocked 19.2 until `delegation.md` gained the `opencode` row; the #317 corpus
sweep blocked 19.5's predecessor until a stale known-divergent entry was removed; and CI caught a
19.4 test that read the environment the feature had just made meaningful.

**Dependencies.** 19.1 blocks everything. 19.2 blocks 19.3 / 19.4 / 19.7. 19.3 + 19.4 block 19.7.
19.5 and 19.6 are independent of the chain and can land at any point — and **19.5's first half
should not wait**: correcting the catalog/README contradiction is a small data fix whose only
reason to sit inside the milestone is bookkeeping.

## Out of scope (invariants this milestone does not touch)

- **The advisory-first posture.** The OS recommends; the human keeps final model authority
  (ADR-0017). Nothing here becomes a blocking gate on model choice.
- **No session auto-swap.** Application stays **downward only** — a run may route work it
  delegates, never itself (M18 decision 4, `delegation.md`'s hard limit).
- **Tiers, not names, in every artifact.** Model names live only in the dated catalog; roadmaps,
  issues and plan docs keep speaking tiers (M18 decision 1).
- **Determinism.** Same signals, same advice — no model in the resolution loop. Selection's
  tie-breaks are deterministic and order-independent, like escalation.
- **Escalation stays monotonic.** Rules only raise. Cost, `step:` signals and budget considerations
  are all forbidden from lowering a resolved floor.
- **Generated repos.** They do not ship `os/` (17.2 precedent); if routing should reach the
  generated contract it enters through `templates/AGENTS.md.tmpl` as its own decision.

## Provenance

Filed from a full-repo architecture audit on 2026-07-26 (tree at rest on v2.11.0, all gates green)
and the owner's requirement of the same date. The audit's non-routing findings are #315–#321.
