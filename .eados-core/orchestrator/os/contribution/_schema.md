# `contribution.yaml` — schema

The **inbound-contribution review policy** as data: who counts as the owner, the trust tiers, the
checks every inbound PR must pass, the disposition + label vocabulary the reviewer may recommend,
and the load-bearing escalation (an external fork touching an owned path goes to a human). It
encodes the practice the maintainer already applies by hand to external PRs (verify the change, not
the person; honor a good idea via co-author + an in-house re-implementation; the human posts the
close — the #94 episode) so the `contribution-reviewer` role (M8 8.2) and `pr_review.py` (M8 8.3)
read one source of truth instead of hardcoding it.

`eados_lint` (`os-spec-completeness`) requires the instance to define every top-level key below;
`data-file-validity` requires it to parse; `cross-spec-consistency` resolves its role + disposition
cross-references.

## Required structure

```yaml
version:          # integer schema version
owner_identity:   # where "owned" comes from (CODEOWNERS, with a manifest fallback)
trust_tiers:      # the authorship tiers, least -> most scrutiny
required_checks:  # the checks every inbound PR is evaluated against
dispositions:     # the recommendations the reviewer may draft (id + label)
escalation:       # the external-fork-touches-owned-path -> human rule
boundary:         # recommends-only; the human disposes / closes
```

## Item shapes (consumed by `pr_review.py`, M8 8.3)

- **`owner_identity`** — `{ source, manifest_fallback }`. `source` is the authoritative owner record
  (`CODEOWNERS`); `manifest_fallback` is the `project.yaml` path used when it is absent.
- **`trust_tiers`** — list of `{ id, scrutiny }`, least → most scrutiny. `id` ∈
  `owner | collaborator | external-fork`; `scrutiny` ∈ `standard | high`. Scrutiny attaches to the
  diff + provenance, never to the author (the #94 principle).
- **`required_checks`** — the check ids an inbound PR must satisfy before a disposition is
  recommended (`ci-green`, `provenance-clear`, `no-added-secrets`, `scope-matches-intent`,
  `gate-coverage-holds`).
- **`dispositions`** — list of `{ id, label }`. The reviewer **recommends** one; the `label` is what
  `/eados review` (M8 8.4) drafts onto the PR. Drafts only — never an approval or a merge.
- **`escalation`** — `{ on, decider, disposition }`. `decider` resolves to an `authority.yaml` role
  or the `human-owner` terminal; `disposition` must be one of `dispositions`.
- **`boundary`** — `{ recommends_only, closes_by }`. Restates `AGENTS.md` §6 as data.

## Invariants

- `boundary.recommends_only` is `true` and `escalation.decider` terminates at the human: the
  reviewer **drafts and recommends; it never merges or closes** (`git.yaml` `pr.merged_by: human`).
- An `external-fork` PR touching an owned path always escalates to a human (`needs-maintainer`) —
  it is never auto-disposed.
- Trust gates the *scrutiny level*, not the *outcome*: a verified external change is as mergeable as
  any other (the change is judged, not the person).
