# `/eados adopt` — adopt an existing repository (brownfield intake)

`init`'s **brownfield sibling** — the entry command for a repository that already has code and
history. Where [`init.md`](init.md) frames a *new* project, `adopt` greets the maintainer who just
installed EADOS into an **existing** codebase (the installers' default, `--mode existing`) and
asks what they want from it: a read-only **gap map**, a **goal menu**, and a manifest whose
`adoption:` block makes the chosen route **legal by data** (ADR-0021; the `init → audit` /
`init → migrate` workflow edges are gated on it). Owned by the **enterprise-architect** role. It
is an **intake, not a phase** (ADR-0019 §1): the state set is unchanged and the manifest lands at
`delivery_state.phase: init`.

## Preconditions

- **An existing repository.** Confirm the target is genuinely brownfield before anything else:
  a `.git` history and a source tree (`brownfield.py`'s `source tree` row — `src`/`lib`/`source`)
  or an equivalent body of existing work. An **empty or new** directory is greenfield — route to
  [`/eados init`](init.md) instead; `adopt` refuses it the way the code commands refuse
  manifest-less code (ADR-0019: route, don't guess).
- **Not already governed.** A repo that already carries an EADOS manifest with `delivery_state`
  needs no adoption — run [`/eados status`](status.md) and continue from its reported phase.

## Procedure

1. **Preflight + detect** — verify the toolchain exactly as `init` does, then confirm the target
   is brownfield (git history present, source tree present — the detect signals above):
   ```bash
   python .eados-core/tools/preflight.py        # add --no-gh for the pure, no-GitHub path
   ```
2. **Gap map (read-only)** — map the repository against the standard and **capture the report**;
   nothing is written into the repo except this capture, beside the manifest:
   ```bash
   python .eados-core/tools/brownfield.py <repo>   # read-only; exit 0 even with gaps
   ```
   Save the output as `orchestrator/adoption-gap-map.md` (additive — never overwrite an existing
   capture; the sandbox posture of every EADOS write applies). Present the `[x]`/`[ ]` rows and
   the `gaps to migrate` line to the maintainer — the menu below is chosen *over this evidence*.
3. **Goal menu (the adoption interview)** — conduct in the **maintainer's language**; the
   manifest lands in **English** (`AGENTS.md` §2, exactly as [`interview.md`](../interview.md)
   rules). One question, multi-choice, house style:

   > **QA.1 — What do you want from EADOS here?** (pick one or more)
   > `governance-docs` — render the missing documentation system (the gap map's `[ ]` rows) ·
   > `retro-design` — reconstruct the RFC/spec from the existing code ·
   > `audit` — a risk register over the current state ·
   > `migrate` — full migration to the standard ·
   > `bugfix` — investigate a defect (`/eados debug`)

   Refuse an empty or vague answer ("just improve it") the way Phase 5 refuses an untestable
   requirement: the menu is the closed vocabulary (`render.py` `_ADOPTION_GOALS`; extending it
   takes an ADR). Then fill the **framing facts** the `manifest-valid` gate requires — identity,
   ownership, language basics — mostly **`imported`** from the repository itself (the name from
   the repo, the license from `LICENSE`, the language from the source tree); ask only what the
   repo cannot answer (interview.md's ask-only-what-you-cannot-default rule).
4. **Record** — write `orchestrator/project.yaml` from
   [`project.yaml.template`](../project.yaml.template): the framing facts, `delivery_state` with
   `phase: init` (empty `checkpoints`/`refs`), and the **`adoption:` block** — `goals` (the menu
   answer), `gap_map_ref: orchestrator/adoption-gap-map.md`, and `provenance` per answer
   (`goals: asked`; `gap_map_ref: imported`). Validate, then **confirm with the maintainer**
   (the cheap checkpoint, `AGENTS.md` §5):
   ```bash
   python .eados-core/tools/render.py orchestrator/project.yaml --check
   ```
5. **Route** — propose the goal's route; the phase runner reports it as **legal by data**
   (ADR-0021 §5 — with multiple goals, the **earliest** target in pipeline order wins:
   `design < audit < migrate`; every later goal stays reachable from there):
   - `retro-design` → `--propose design` (the ordinary edge; the RFC is reconstructed from code);
   - `audit` → `--propose audit` (the adoption edge);
   - `migrate` or `governance-docs` → `--propose migrate` (rendering the missing docs *is*
     additive migration — [`migrate.md`](migrate.md)'s plan orders the gap-map rows);
   - `bugfix` → no transition: hand off to [`/eados debug`](debug.md), whose ADR-0019
     manifest precondition the new manifest now satisfies.
   ```bash
   python .eados-core/tools/phase_runner.py orchestrator/project.yaml --propose <to>
   ```
   Every adoption edge is gated on `manifest-valid` + `adoption-recorded` (evaluated in-process —
   a malformed block is NOT READY, never silently `manual`) and is **human-gated**: the agent
   writes the emitted checkpoint (with `confirmed_by:`) **after** the maintainer confirms.
6. **Hand off** — to the routed phase's own procedure (`design.md` / `audit.md` / `migrate.md` /
   `debug.md`). From there the ordinary machine governs; adoption is spent — the block stays in
   the manifest as the record of how this repository entered.

## Worked example — a fixture repo, end-to-end

An existing repo `acme-billing` (git history; `README.md`, `src/`, `.github/workflows/` present;
installed via `setup.sh --mode existing`):

1. **Preflight** OK; detect: `.git` history ✓, `src/` ✓ — brownfield confirmed.
2. **Gap map** — `brownfield.py` reports `3/9 standard artifacts present`; gaps:
   `agent contract, changelog, license, security policy, ADRs, spec` (all low-risk rows).
   Captured to `orchestrator/adoption-gap-map.md`.
3. **Goal menu** — the maintainer (in Italian, per §2) picks `governance-docs` + `audit`.
4. **Record** — manifest: identity imported (`acme-billing`), license `asked` (no LICENSE file —
   one of the gaps), `adoption: {goals: [governance-docs, audit], gap_map_ref:
   orchestrator/adoption-gap-map.md, provenance: {goals: asked, gap_map_ref: imported}}`;
   `render.py --check` green; maintainer confirms the skeleton.
5. **Route** — targets are `migrate` (governance-docs) and `audit`; the earliest in pipeline
   order is **`audit`** → `--propose audit` reports LEGAL (gates: `manifest-valid` OK,
   `adoption-recorded` OK; human-gated). The maintainer confirms; the checkpoint
   `{from: init, to: audit, confirmed_by: <owner>}` is recorded. After the audit's risk register,
   `audit → migrate` (the ordinary edge) reaches the `governance-docs` goal — the migrate plan
   orders the six gaps lowest-risk-first, one PR each.

## Boundary

Intake only — a gap map, a menu, a manifest, a proposal. The command **never migrates, renders,
audits, or fixes anything itself** (each goal routes to the phase or command that owns that work);
its only writes are the manifest and the gap-map capture, both **additive** and beside each other
under `orchestrator/` (never user code, never `.git` — the sandbox posture every EADOS write
obeys). Every route out is **human-gated**: the agent proposes, the maintainer confirms
(`AGENTS.md` §6). The **greenfield pipeline is untouched in behavior** — without an `adoption:`
block the adoption edges are listed but NOT READY (their gate reads `skipped`, which the
checkpoint validator never accepts as passing), so `→ design` remains the only takeable route
out of `init` for an ordinary project.

## Backward compatibility

`adopt` is additive, like `init`. A maintainer who ignores it and runs `init` (or the classic
interview → `render.py` flow) is unaffected: the `adoption:` section is optional, the renderer
never reads it as a placeholder source, and no existing manifest becomes invalid.
