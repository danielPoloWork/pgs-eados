# `/eados init` — initialize a governed project

The **entry command** of the pipeline. It frames the project and writes the initial manifest so
every later phase has state to read. Owned by the **enterprise-architect** role. `init` frames a
**new** project — for a repository that already has code and history, its brownfield sibling
[`/eados adopt`](adopt.md) (#247, ADR-0021) is the front door: gap map → goal menu → a legal
route into `design`/`audit`/`migrate`.

## Housekeeping (first run)

If the repo was set up via the **guided installer** ([`setup/`](../../../setup/setup.sh)), its
downloaded scripts are just the bootstrap and are no longer needed once `.eados-core/` is in place.
Tidy them — this removes **only** the known installer artifacts (`setup.sh` / `setup.ps1` /
`setup.bat` / `setup.command`, and a `setup/` dir only when it holds nothing but those); it never
touches `.eados-core/`, the agent contract, or your own files:

```bash
python .eados-core/tools/cleanup_installer.py .          # dry-run: list what would be removed
python .eados-core/tools/cleanup_installer.py . --apply  # remove them
```

## Procedure

1. **Preflight** — verify the toolchain the pipeline assumes is present before anything else:
   ```bash
   python .eados-core/tools/preflight.py        # add --no-gh for the pure, no-GitHub render path
   ```
   It checks the Python version, `git`, `gh`, and `gh auth status`, printing an OS-specific
   install/auth hint for anything missing and exiting non-zero — so a missing or unauthenticated
   tool surfaces here, not mid-run. (Python-missing-entirely is out of scope for a Python tool; the
   guided installer under [`setup/`](../../../setup/setup.sh) carries that non-Python bootstrap hint.)
   On a non-zero result, resolve what it flags, then continue.
2. **Frame** — run interview [Phase 0](../interview.md) (Q0.1–Q0.5), **including
   `Q0.4 — development target`** (`software` / `web` / `game` / `mobile`), which loads the
   matching [`domains/<domain>.yaml`](../domains/_schema.md), and `Q0.5 — enterprise posture`
   (`standard` default / `enterprise`) — orthogonal to the target, not a fifth domain.
3. **Write the manifest skeleton** — copy [`project.yaml.template`](../project.yaml.template) to
   `orchestrator/project.yaml` and fill the framing facts: `identity`, the top-level `domain`, the
   `schema_version`, and a `delivery_state` block with `phase: init` (empty `checkpoints` /
   `refs`). Leave the deeper sections (language, toolchain, spec, …) for their phases.
4. **Confirm** — present the skeleton to the maintainer (the cheap checkpoint; `AGENTS.md` §5).
5. **Report the next move** — run the deterministic phase runner:
   ```bash
   python .eados-core/tools/phase_runner.py orchestrator/project.yaml
   ```
   At `phase: init` it reports `-> design` (gate `manifest-valid`, **human-gated**) — the
   greenfield default — plus the two adoption edges (`-> audit`, `-> migrate`), which stay
   NOT READY for an ordinary project (their `adoption-recorded` gate reads `skipped` without the
   `adoption:` block only [`/eados adopt`](adopt.md) writes). Surface the preflight verdict from
   step 1 in the hand-off so the maintainer sees the environment is ready (or what to fix)
   alongside the next move.
6. **Hand off** — the maintainer chooses the next phase:
   - the **delivery pipeline** → `/eados design` (authoring RFCs; lands in M2); or
   - the **classic one-shot path** → finish the full interview (Phases 1–5) and `/eados scaffold`
     ([`generate.md`](../generate.md)) to render the repository as today.

## Boundary

The agent **drafts** the manifest and **proposes** the transition the phase runner reports; the
**human confirms** every human-gated move and owns the irreversible steps. `init` never renders
or commits anything on its own.

## Backward compatibility

`init` is additive. A maintainer who ignores the pipeline and runs the classic interview →
`render.py` flow is unaffected: `delivery_state` is optional and the renderer ignores it.
