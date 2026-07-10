# [FEATURE] Rename the brownfield phase `refactor` → `migrate` (ADR; frees the name for code-quality refactoring)

> **Delivered:** [ADR-0020](../.eados-core/docs/adr/0020-rename-refactor-phase-to-migrate.md)
> (2026-07-10, closes [#236](https://github.com/danielPoloWork/pgs-eados/issues/236)). Phase
> renamed across the machine + governed docs + i18n; `commands/refactor.md` → `commands/migrate.md`;
> back-compat: `delivery_state.phase: refactor` accepted as a deprecated alias for one minor version
> with a CLI warning. Unblocks #243 (`/eados refactor`, code-quality meaning).

**Labels:** `enhancement`, `severity:medium`, `area:orchestrator`, `area:commands`
**Component:** `orchestrator/os/workflow/workflow.yaml`, `orchestrator/commands/refactor.md`, `tools/eados.py`, docs

## Context

`/eados refactor` is a **false friend**: the phase migrates an existing repository toward the
EADOS *standard* by rendering missing governance artifacts through the sandbox
(`brownfield.py` → `migration_planner.py` → `render_artifact.py` + `sandbox.py`). It never
restructures application code for quality — yet "refactor" universally means exactly that. The
collision misleads users and blocks shipping a true code-quality refactoring command
(maintainer requirement, 2026-07-09; see draft issue 0017).

## Direction

1. **ADR** recording the rename and its rationale (naming honesty; the freed name).
2. Rename the state across the machine and its docs, in one PR:
   - `workflow.yaml` (state, transitions, gates), `_schema.md` if it enumerates phases
   - `commands/refactor.md` → `commands/migrate.md` (+ `commands/README.md` row)
   - `tools/eados.py` (`PHASES`, `PROCEDURE` map), `phase_runner.py`, `doctor.py`, tests
     (incl. `test_phase_smoke.py`)
   - prose: `AGENTS.md` §3 pipeline line, `README.md`, RFC-0001 mentions, `USAGE.md`
     walkthrough, `recovery.md` if it names phases
3. **Back-compat:** accept `delivery_state.phase: refactor` as a deprecated alias of `migrate`
   for one minor version (loader-level mapping + a deprecation warning), so existing manifests
   keep working.

## Acceptance

Grep for the old phase name in governed docs returns only the ADR/CHANGELOG history and the
alias note; the end-to-end phase smoke test is green; `/eados migrate` behaves exactly as the
old command. Blocks draft issue 0017 (`/eados refactor`, code-quality meaning).
