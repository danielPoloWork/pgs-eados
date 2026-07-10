# [FEATURE] `/eados testcases` — governed unit/integration test generation (QA-owned)

**Labels:** `enhancement`, `severity:medium`, `area:commands`, `area:agent`
**Component:** `.eados-core/orchestrator/commands/testcases.md` (new), `.eados-core/agent/qa-engineer.md`, `.eados-core/orchestrator/os/authority/authority.yaml`
**Milestone:** M15 — Command Surface & Governed Assistants · **Wave 2**

## Context

`testcases` is a **true gap**: no test-generation command exists anywhere in the factory. Draft
0021 adds a QA/test-engineer *owner persona* and the `src/test/**` ownership record — but it does
**not** add the command that generates tests. Today verification is split between the tech-lead
(implicit authorship) and the reviewer (coverage enforcement), and rubric dimension 6 is
self-scored — a weak enterprise/AAA verification bar.

## Direction

A **cross-cutting command** `commands/testcases.md` (per ADR-0019, the taxonomy ADR drafted as
0022; **manifest required** — pasted/standalone code is refused and routed to
`/eados init` / `/eados adopt`), owned by the `qa-engineer` persona shipped in 0021:

1. **Intake** — the target unit/behavior + its spec §6 verification strategy; **refuse untestable /
   vague targets** the same way Phase 5 refuses untestable requirements.
2. **Generate** — unit and/or integration tests against spec §6, using the project's profile test
   toolchain; tests land under `src/test/**` (ownership from 0021).
3. **Verify + record** — the generated suite runs green against the current code (or is marked
   `xfail` with a linked defect via `/eados debug` 0016); ties into the coverage gate the reviewer
   enforces; draft the gated PR with standard cross-links; the human merges.

## Acceptance

A worked example generates a passing (or intentionally-failing, defect-linked) suite against a
fixture spec §6; the command file states owner role, preconditions, gates, and boundary like the
existing commands; `commands/README.md` gains its row and the 0011 adapter check covers it; the
`qa-engineer` owns the surface. Cites ADR-0019.

**Depends on:** 0021 (qa-engineer persona + `src/test/**` ownership), ADR-0019 (taxonomy;
draft 0022, delivered).
