# [FEATURE] `/eados optimize` — measure-first performance optimization against NFR budgets

**Labels:** `enhancement`, `severity:medium`, `area:commands`
**Component:** `orchestrator/commands/` (new `optimize.md`)

## Context

No optimization procedure exists; the measurement scaffolding does — the optional benchmarks
capability (`IF_BENCH`: CI bench job, `docs/benchmarks/` with its
record-the-configuration discipline), spec §3 non-functional budgets, and the domains' hard
`nfr_axes` (web: Core Web Vitals; game: framerate/RAM/GPU/load-time; mobile:
app-size/cold-start). "Try to make it faster" without a number is exactly the untestable-
requirement class the interview's Phase-5 discipline exists to refuse.

## Direction

A **cross-cutting** command, `commands/optimize.md` (class ratified in ADR-0019, drafted as
0022; **manifest required** — pasted/standalone code is refused and routed to
`/eados init` / `/eados adopt`), owned by the **tech-lead**:

1. **Target** — a numeric goal from spec §3 or the domain's `nfr_axes` (e.g. "p99 < 5 ms",
   "cold-start < 2 s"). No numeric target → elicit one first (the Phase-5 testability follow-up);
   never proceed on an adjective.
2. **Baseline** — run the benchmark suite and record the configuration
   (`docs/benchmarks` discipline); if `capabilities.bench` is off, enabling it is step zero.
3. **Profile → change** — locate the hotspot with evidence, apply **one** targeted change.
4. **Re-measure** — accept only if the target moves toward budget with no correctness/complexity
   regression (suite green; reviewer verdict on readability cost).
5. **Record** — before/after numbers in `docs/benchmarks` and in the PR body; draft the gated
   PR; the human merges.

Boundary with siblings: structure-only changes belong to `/eados refactor` (draft 0017);
defect fixes to `/eados debug` (draft 0016).

## Acceptance

Worked example on a fixture with a bench suite: baseline → change → re-measure recorded; the
refusal path ("make it faster", no number) is exercised; command file states owner,
preconditions, gates, boundary; `commands/README.md` row + host adapter present.
