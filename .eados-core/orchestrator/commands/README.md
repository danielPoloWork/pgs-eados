# EADOS commands — the `/eados` surface

The opt-in phase commands a host exposes as `/eados <phase>`. Each is a thin entry point that runs
its phase's procedure and reports the **legal next move** via the deterministic
[`phase_runner.py`](../../tools/phase_runner.py) — which reads the manifest's
`delivery_state.phase` and [`workflow.yaml`](../os/workflow/workflow.yaml). The agent **proposes**
a transition; the human **confirms** every human-gated one (`AGENTS.md` §6).

| Command | Phase | Status | Procedure |
|---------|-------|--------|-----------|
| `/eados init` | init | **available** (M1) | [`init.md`](init.md) |
| `/eados design` | design | **available** (M2) | [`design.md`](design.md) |
| `/eados plan` | plan | **available** (M3) | [`plan.md`](plan.md) |
| `/eados scaffold` | scaffold | **available** (today's factory) | [`../generate.md`](../generate.md) |
| `/eados audit` | audit | **available** (M4) | [`audit.md`](audit.md) |
| `/eados refactor` | refactor | **available** (M5) | [`refactor.md`](refactor.md) |
| `/eados status` | — (any) | **available** (M6) | [`status.md`](status.md) |

`/eados status` is the odd one out — a **read-only doctor**, not a phase that advances: it reports
the current phase, the legal next moves, and traceability coverage at a glance (roadmap 6.4).

**Portable.** The canonical procedure is the markdown here; a host wraps it with its own skill
mechanism (Claude Code `.claude/skills/`, a Codex/Gemini agent registry). The adapter is thin — it
points at the procedure, exactly as `CLAUDE.md` / `GEMINI.md` point at `AGENTS.md`.

## The phase runner

```bash
python .eados-core/tools/phase_runner.py <manifest>
```

prints the legal next transitions for the manifest's current phase, each with its entry gates and
whether it is human-gated. It is **state-driven and deterministic, and never advances state on its
own** — it reports what is legal; the human decides. Example (a fresh manifest, phase `init`):

```text
current phase: init
legal next transitions:
  -> design   (gates: manifest-valid)  [human-gated — the owner confirms]
```

`--propose <to>` validates a *proposed* transition and **emits** the `delivery_state` checkpoint to
write — it does **not** write state (the agent does, after the human confirms a human-gated move):

```bash
python .eados-core/tools/phase_runner.py <manifest> --propose design
```
