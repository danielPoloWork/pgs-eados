# `routing.yaml` — schema (v2)

The **model & effort routing policy** as data (M16 / ADR-0017, extended by **ADR-0024**). Given a
unit of work's **signals** — its tracker labels plus derived flags — the policy recommends a
**capability tier** and an **effort level**, then names the cheapest reachable model that clears
them. It is *advisory-first*: the OS states the recommendation at its read-points (Step-0 triage,
`/eados status`, the `.issues/` planning docs); the human keeps final model authority, and
auto-application exists only for host-delegated subagent work — the one place the advice is
*applied* rather than printed, specified in [`delegation.md`](./delegation.md). The evaluator is
[`../../../tools/route_advice.py`](../../../tools/route_advice.py).

**Tiers, not model names.** The rules speak capability tiers; concrete model names live *only* in
the dated `catalog:`, so model churn is a catalog edit — never a policy or code change.

**Capability, not lookup (v2).** A model declares what it *clears*; the evaluator selects. Adding a
provider, a model or a host is configuration data with no code change — which is what makes the
policy work under any LLM rather than the one it was written on.

`eados_lint` (`os-spec-completeness`) requires the instance to define every key below; the
`examples` gate (#224) shape-checks the worked-example decision surface; `routing-delegation`
requires every catalog host to declare a delegation posture.

## Required structure

```yaml
version:        # integer schema version (2)
tiers:          # ordered capability tiers, cheapest -> most capable
efforts:        # ordered effort levels, lowest -> highest (OS-neutral vocabulary)
flags:          # derived-signal vocabulary beyond tracker labels: flag id -> meaning
defaults:       # the floor when no rule matches
  tier:         # a `tiers` entry (the cheapest — rules only raise)
  effort:       # an `efforts` entry
protected:      # signals whose earned floor nothing may reduce (list of `label:`/`flag:` signals)
selection:      # how selection chooses AMONG models that already clear the floor
  objective:    # `quality-first`
  prefer:       # ordered criteria: `lowest_cost` | `lowest_latency`
rules:          # monotonic escalation rules; each { id, when, min_tier, min_effort, why }
catalog:        # the ONLY place concrete model names live
  as_of:        # "YYYY-MM-DD" the catalog was last verified against the market
  max_age_days: # staleness budget; beyond it the catalog needs re-verification
  providers:    # vendors: { id, name, models[], notes? }
  hosts:        # runtimes: { id, name, providers[], delegation, detect[], effort_aliases? }
examples:       # worked-example decision surface (#224): verdicts = the tiers
```

### `providers[].models[]` — a capability record

```yaml
- id:            # stable kebab identifier
  name:          # display name; what the evaluator returns and `--check` compares against
  meets_tier:    # the tier this model CLEARS — present if and only if `assessed: true`
  max_effort:    # optional: the highest effort that can be asked of it
  context:       # optional: context window in tokens
  relative_cost: # optional: cheapest catalogued model = 1
  assessed:      # has the maintainer judged this model against EADOS?
  verified:      # "YYYY-MM-DD" of that judgment
  notes:         # optional free text
```

### `hosts[].detect[]` — how the runtime is identified

```yaml
detect:
  - env: CLAUDECODE            # the variable is set
  - env: AI_AGENT              # …and its value matches
    matches: "^claude-code"
```

The OS works out which **runtime** it is in from the environment. It **never asks the agent which
model it is**: models misdescribe their own identity, most confidently right after a version change
— exactly when routing most needs to be right — and a route built on a hallucinated
self-description is worse than none, because it is wrong *and* it looks authoritative.

Only markers actually **observed** belong here. A host with `detect: []` never auto-detects and
must be named — the same honesty as an unassessed model. A guessed marker either never fires
(useless) or fires on the wrong host (harmful), and the second failure is worse than no detection.

**Host precedence** (ADR-0024 D4), highest first:

| Rung | Source | Why it wins |
|---|---|---|
| 1 | `--host` flag | a direct human instruction |
| 2 | `routing.host` in the manifest | a recorded human declaration |
| 3 | `detect[]` markers | deterministic environment evidence |
| 4 | **unresolved** | stated, with the reason — **never** a default |

There is deliberately **no fallback to the first catalog host**: that is how every non-Claude host
silently received Anthropic model names, and its absence is asserted by a test. Two hosts matching
is **ambiguous**, not a tie to be broken — it is reported with both named and falls to rung 4.

Rung 4 costs less than it appears: tiers and efforts are vendor-neutral, so an unresolved host
loses the model **name** and nothing else. The recommendation stays fully actionable, and the
output says what was determined and what was not.

## Resolution — two phases (ADR-0024 D2)

**Phase 1 — escalation → the floor.** Start at `defaults`; every matched rule raises the result to
at least its `min_tier` / `min_effort`; the answer is the **max** over the floor and all matches,
in `tiers` / `efforts` order. A rule matches when *all* of its `when` signals hold. Rules never
lower a result — the same only-add-never-relax principle as the workflow's domain overlays.
Deterministic and order-independent.

**Phase 2 — selection → the model.** Among the models of the providers the resolved host reaches,
keep those that are `assessed` and whose `meets_tier` is at or above the floor tier (and whose
`max_effort`, where declared, admits the floor effort). Rank by `selection.prefer`. Take the first.

**Signal vocabulary** (`when` entries, and `protected`):

- `label:<name>` — the unit of work carries that tracker label (`label:severity:high`, `label:adr`).
- `flag:<id>` — a derived flag from `flags:`, asserted by an evaluator heuristic or a human.

## The invariant cost must obey

> **Cost may only choose among models that already clear the earned floor. It can never lower the
> floor.**

This is why the phases are separate. *"Use the minimum model that satisfies the step"* is not an
extra behaviour: it is what the monotonic floor already computes. The floor **is** the minimum that
satisfies quality; `selection` then picks the cheapest way to reach it. Tokens are therefore a real
but strictly **secondary** constraint, and a `protected:` route cannot be degraded to save them —
not because a carve-out defends it, but because cost never operates on the floor at all.

When no reachable model clears the floor, the honest answer is the tier and effort **without a
model name**, and a stated reason — never the closest cheaper thing. Tiers and efforts are
vendor-neutral, so that answer is still fully actionable.

## Provenance — what `assessed` means

`assessed: true` records that the **maintainer has judged this model against EADOS** and placed it
on the ladder. It is a dated human judgment, not a benchmark run, and the distinction is written
down rather than implied. A model nobody has assessed is catalogued as **reachable** and carries no
`meets_tier`: you cannot claim a capability you have not verified, and selection skips it.

This rule exists because its absence caused a live incident (#326): the catalog routed every ADR,
security and foundational-decision unit of work to a model the project's own README described as
unbenchmarked, for weeks, because an unverified claim was indistinguishable from a verified one.
A provider with `models: []` records only that hosts can reach it.

## Effort vocabulary

`efforts` is OS-neutral: `low` | `medium` | `high` | `extra` | `max`. Hosts that use different
words map them in their catalog entry's `effort_aliases` (Claude Code: `ultracode` → `max`). Advice
is always *emitted* in the OS vocabulary; an adapter may translate at the edge.

Inserting a level changes what the existing ones **mean** relative to the ceiling, so a change here
requires re-reading every rule's `min_effort` rather than migrating it mechanically. The outcome of
that re-read is recorded per rule in [`routing.yaml`](./routing.yaml).

## Invariants

- `defaults` and every rule's `min_tier` / `min_effort` are entries of `tiers` / `efforts`. Every
  `flag:` signal (in a rule's `when` or in `protected`) references a `flags:` key.
- Every host's `providers[]` names a declared provider id, and is non-empty — a host that reaches
  nothing can route nothing. Host and provider ids are unique.
- `meets_tier` is present **iff** `assessed: true`, and is a `tiers` entry. `max_effort`, where
  present, is an `efforts` entry. Every `effort_aliases` value is an `efforts` entry.
- `catalog.as_of` is refreshed whenever a mapping changes, and is within `max_age_days`.
- The policy never contains a model name outside `catalog.providers[].models[]`. Prose that names
  models (the READMEs' ranking) must agree with the catalog — one fact, one home.
- Resolution is **deterministic** — same signals, same advice (no model/LLM in the loop). Selection
  ties break in declaration order, so a missing `relative_cost` cannot make the answer wobble.
- The host is resolved from an explicit flag, a manifest declaration, or environment evidence —
  never from asking the agent what model it is, and never by defaulting silently (ADR-0024 D4).
- Advice never overrides a human's explicit model/effort choice, and no rule can force a top-level
  session model switch — that action does not exist below the human (`AGENTS.md` §6). Application
  is **downward only**: the [delegation hook](./delegation.md) may set the model of a *delegated*
  sub-task on a capable host; it never re-routes the session itself.
