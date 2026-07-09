# [FEATURE] `/eados refactor` — code-quality refactoring: readability, modularity, idiom (pattern-guided)

**Labels:** `enhancement`, `severity:medium`, `area:commands`
**Component:** `orchestrator/commands/` (new `refactor.md`, post-rename)

## Context

Blocked by draft issue 0014 (the brownfield phase must vacate the name first). Once freed,
`refactor` takes its universal meaning: behavior-preserving restructuring of application code
for readability, modularity, and idiom. The guidance layer already exists — the 8-category
design-pattern taxonomy and living catalogue (`templates/docs/patterns/`), the architecture
style + first-class patterns + `spec.pattern_discipline` (`advisory` | `enforced`) elicited at
interview Q5.4, and the reviewer persona's quality bar — but no command applies it to code.

## Direction

A **cross-cutting** command, `commands/refactor.md` (new meaning). Owned by the **tech-lead**
(owns `src/**`); the **reviewer** holds the quality-bar verdict.

1. **Scope** — one named smell/target per run (a module, a pattern violation, a duplication
   cluster); refuse open-ended "clean everything" scope.
2. **Behavior-preservation gate** — the affected surface must be test-covered *before*
   restructuring: run the suite green, add characterization tests where coverage is missing.
3. **Restructure** — one logical change per PR, guided by the adopted architecture style and the
   patterns catalogue; a *structural* pattern introduction gets its ADR (the same rule the
   generated repos live under).
4. **Prove** — suite green after; formatter/linter gates from the profile pass; no public-API
   change without the SemVer/ADR path.
5. **Record** — update the patterns catalogue row (Planned → Adopted) when a planned pattern
   lands; draft the gated PR; the human merges.

Boundary with siblings: performance work belongs to `/eados optimize` (draft 0018); defect
fixing to `/eados debug` (draft 0016); migration-to-standard to `/eados migrate` (0014).

## Acceptance

Worked example: a fixture module is restructured behavior-preservingly (tests green
before/after, catalogue updated); the command file states owner, preconditions, gates, boundary;
`commands/README.md` row + host adapter present.
