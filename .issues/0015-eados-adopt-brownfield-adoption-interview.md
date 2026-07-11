# [FEATURE] `/eados adopt` — brownfield adoption interview: existing repo → goal menu → tailored route

> **✅ Delivered** (2026-07-11, closes [#247](https://github.com/danielPoloWork/pgs-eados/issues/247); **ADR-0021**).
> `/eados adopt` ships as `init`'s brownfield sibling intake (never a phase — the ADR-0019 §1
> state set is unchanged): preflight + detect → read-only gap map (`brownfield.py`, captured as
> `adoption-gap-map.md`) → goal menu (`governance-docs`/`retro-design`/`audit`/`migrate`/`bugfix`)
> → manifest `adoption:` block (goals + `gap_map_ref` + its own provenance) → the goal's legal,
> human-gated route. The adoption route is **data**: `workflow.yaml` gains `init → audit` /
> `init → migrate` gated on `manifest-valid` + the new in-process `adoption-recorded` gate
> (`eados.py` evaluator: absent → `skipped`, so the greenfield pipeline is untouched; malformed →
> FAIL); `render.py` admits + validates the optional `adoption:` section (`adoption_problems()`,
> closed goal menu, shared with the evaluator). Registry row + `/eados:adopt` adapter ship; the
> four Wave-2 refusal routes flip live; RFC-0001 §3 diagram gains the dotted adoption edges.
> Guarded by `test_adopt_command.py` + the rewritten `test_phase_runner.py` init-fork block.

**Labels:** `enhancement`, `severity:high`, `area:commands`, `area:orchestrator`
**Component:** `orchestrator/commands/` (new `adopt.md`), `orchestrator/os/workflow/workflow.yaml`, `orchestrator/interview.md`

## Context

The pieces for brownfield exist but the guided entry is missing:

- the `setup/` installers already install into an **existing** repo (interactive default is
  "existing"; `--mode existing`), additively;
- the brownfield phase (`refactor`, to be renamed `migrate` — draft issue 0014) maps gaps
  read-only and migrates via sandboxed PRs — but it is formally reachable only through `audit`
  (human-gated on `risk-register-present`);
- `/eados init` frames a **new** project.

Nothing greets a maintainer who just installed EADOS into an existing codebase and asks what
they want from it. Maintainer requirement (2026-07-09): choose via interview whether to generate
documentation, project design, run an audit, migrate/refactor, or fix bugs.

## Direction

A new **entry command** `commands/adopt.md`, sibling of `init` (owned by the
enterprise-architect):

1. **Preflight + detect** — `preflight.py`; confirm the target is an existing repo (git history,
   source tree present).
2. **Gap map (read-only)** — run `brownfield.py <repo>` and present the standard-gap report.
3. **Goal menu (the adoption interview)** — the maintainer picks one or more goals:
   `governance-docs` (render the missing documentation system) · `retro-design` (reconstruct
   RFC/spec from the existing code) · `audit` (risk register over the current state) ·
   `migrate` (full migration to the standard) · `bugfix` (route to `/eados debug`, draft 0016).
   Conduct in the maintainer's language; manifest lands in English (`AGENTS.md` §2).
4. **Record + route** — write the manifest with an `adoption:` block (`goals`, `gap_map_ref`,
   provenance) and a `delivery_state` the phase runner can act on; propose the legal next
   transition for the chosen goals.

Requires an explicit **adoption route** in `workflow.yaml` (data change + `_schema.md` +
lint coverage — the anti-fragmentation invariant: no special case in code) so entering `audit`
or `migrate` from an adopted state is *legal by data*, not by exception.

## Acceptance

On a fixture existing repo: `adopt` produces a manifest with goals + gap map; each goal routes
to a legal, gated phase; every write stays inside the sandbox posture; the greenfield pipeline
is untouched (adoption is opt-in). Self-lint + phase smoke green.
