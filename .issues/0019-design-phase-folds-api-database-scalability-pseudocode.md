# [FEATURE] Design-phase folds: API contracts, data/schema, scalability budgets, algorithm sketches

**Labels:** `enhancement`, `severity:low`, `area:orchestrator`, `area:templates`
**Component:** `orchestrator/os/rfc/template.md`, `templates/docs/specs/template.md`, `orchestrator/interview.md`

## Context

Four maintainer wishlist items (`api`, `database`, `scalability`, `pseudocode`) are best served
by strengthening the **design phase** rather than minting commands (decision of 2026-07-09,
ratified as the design-sub-mode class in ADR-0019, drafted as 0022):
the RFC template already prompts for "API contracts, data/schema, sequence"; spec §5 elicits the
public interface (Q5.5); ADR-0004 deliberately keeps SQL a secondary Q1.2 surface; "scalab*"
has zero occurrences in the factory content (its only hits are this planning wave: ROADMAP
item 14.13 and these drafts); spec §4 already captures the core algorithm as
prose + diagram.

## Direction (one small PR each, or paired)

1. **API** — expand the RFC template's interface prompt into a checklist (endpoints/functions,
   payloads, error model, versioning/SemVer surface) aligned with spec §5; optional
   `capabilities.api_spec` flag seeding a `docs/api/` stub (OpenAPI/IDL) for `service`/`web`
   projects.
2. **Database** — a data/schema subsection in the RFC template (entities, normalization,
   relations, migration policy), explicitly **within** ADR-0004's frame: SQL stays a secondary
   component declared at Q1.2; no primary profile, no `database` command without a superseding
   ADR.
3. **Scalability** — make the domains' `hard_budget` `nfr_axes` **numeric at intake** (Q5.3
   follow-up forces a value per hard axis) and surface them in the audit-phase overlay gates;
   add scalability/load vocabulary to spec §3 guidance.
4. **Pseudocode** — an optional **Algorithm sketch** block (language-free pseudocode) in spec §4
   and the RFC Decision section.

Every item keeps `placeholders.md`, the affected `_schema.md`, and the lints green in the same
PR (the §7 lockstep rule).

## Acceptance

A design-phase run on a `service`/`web` fixture elicits API + data/schema + numeric budgets +
an algorithm sketch without any new command; the wishlist mapping is documented in
`commands/README.md` (aliases: `systemdesign`/`api`/`database`/`scalability`/`pseudocode` →
`/eados design`; `security` → `/eados audit`).
