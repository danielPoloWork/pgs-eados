# `routing.yaml` — schema

The **model & effort routing policy** as data (M16 / ADR-0017). Given a unit of work's **signals**
— its tracker labels plus two derived flags — the policy recommends a **capability tier** and an
**effort level**. It is *advisory-first*: the OS states the recommendation at its read-points
(Step-0 triage, `/eados status`, the `.issues/` planning docs); the human keeps final model
authority, and auto-application exists only for host-delegated subagent work — the one place the
advice is *applied* rather than printed, specified in [`delegation.md`](./delegation.md) (M16 16.4,
#255; RFC-0001 human-in-the-loop). The evaluator is
[`../../../tools/route_advice.py`](../../../tools/route_advice.py)
(M16 16.2; until it lands, the policy is read by the agent directly).

**Tiers, not model names.** The rules speak capability tiers; concrete model names live *only* in
the dated `catalog:` below, so model churn is a catalog edit — never a policy or code change.
Precedent: risk-weights-as-data ([`../risk/_schema.md`](../risk/_schema.md)), the README model
ranking.

`eados_lint` (`os-spec-completeness`) requires the instance to define every key below; the
`examples` gate (#224) shape-checks the worked-example decision surface.

## Required structure

```yaml
version:        # integer schema version
tiers:          # ordered capability tiers, cheapest -> most capable
efforts:        # ordered effort levels, lowest -> highest (OS-neutral vocabulary)
flags:          # derived-signal vocabulary beyond tracker labels: flag id -> meaning
defaults:       # the floor when no rule matches
  tier:         # a `tiers` entry (the cheapest — rules only raise)
  effort:       # an `efforts` entry
rules:          # monotonic escalation rules; each { id, when, min_tier, min_effort, why }
catalog:        # the ONLY place concrete model names live
  as_of:        # "YYYY-MM-DD" the catalog was last verified against the market
  hosts:        # per-host entries { host, models: tier -> name, effort_aliases: alias -> effort }
examples:       # worked-example decision surface (#224): verdicts = the tiers
```

## Resolution — monotonic escalation

The recommendation starts at **`defaults`** (the cheapest floor) and every matched rule raises it
to at least the rule's `min_tier` / `min_effort` — the final answer is the **max** over the floor
and all matched rules, using the `tiers` / `efforts` order. A rule **matches** when *all* of its
`when` signals hold. Rules never lower a result — the same only-add-never-relax principle as the
workflow's domain overlays. Resolution is therefore deterministic and order-independent.

**Signal vocabulary** (`when` entries):

- `label:<name>` — the unit of work carries that tracker label (e.g. `label:severity:high`,
  `label:adr`, `label:security`).
- `flag:<id>` — a derived flag from `flags:`, asserted by the caller (an evaluator heuristic or a
  human judgment): `sets-pattern` (first of its class — the followers inherit a cheaper route) and
  `decision-heavy` (the decision is the deliverable).

## Effort vocabulary

`efforts` is OS-neutral: `low` | `medium` | `high` | `max`. Hosts that use different words map
them in their catalog entry's `effort_aliases` (Claude Code: "ultracode" → `max`). Advice is
always *emitted* in the OS vocabulary; an adapter may translate on the way out.

## Invariants

- `defaults.tier` / `defaults.effort` and every rule's `min_tier` / `min_effort` are entries of
  `tiers` / `efforts`. Every `flag:` signal references a `flags:` key. Every host's `models:` maps
  **every** tier; every `effort_aliases` value is an `efforts` entry. (Shape is linted today;
  referential integrity is enforced by the 16.2 evaluator's loud rejection.)
- `catalog.as_of` is refreshed whenever a mapping changes — a stale date is the review cue.
- The policy never contains a model name outside `catalog.hosts[].models`.
- Resolution is **deterministic** — same signals, same advice (no model/LLM in the loop).
- Advice never overrides a human's explicit model/effort choice, and no rule can force a
  top-level session model switch — that action does not exist below the human (`AGENTS.md` §6).
  Application is **downward only**: the [delegation hook](./delegation.md) may set the model of a
  *delegated* sub-task on a capable host; it never re-routes the session itself.
