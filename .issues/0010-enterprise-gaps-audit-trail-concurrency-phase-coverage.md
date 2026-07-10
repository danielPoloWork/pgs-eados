# [EPIC] Enterprise-readiness gaps: cross-phase audit trail, manifest concurrency, learning-loop phase coverage

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Epic delivered via its three children: audit trail [#216](https://github.com/danielPoloWork/pgs-eados/pull/216) (issue #213), manifest concurrency [#217](https://github.com/danielPoloWork/pgs-eados/pull/217) (issue #214, `manifest_rev`/`--expect-rev`), learning-loop coverage [#218](https://github.com/danielPoloWork/pgs-eados/pull/218) (issue #215 — refactor failure channel, corpus-scaled autotune floor, override redaction). Umbrella issue [#203](https://github.com/danielPoloWork/pgs-eados/issues/203) CLOSED. Guarded by `test_phase_runner.py`, `test_record_run.py`, `test_run_records.py`, `test_autotune.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `epic`, `enhancement`, `severity:medium`, `agentic-governance`

## Context

Evaluated as an **enterprise agentic delivery OS** (procedural generation of enterprise
software via interview), the architecture is strong — persona/authority split, deterministic
offline gates, fail-loud loader, human-gated memory. Three structural gaps remain below the
enterprise bar:

## 1. No unified audit trail of agent actions

Run records exist **only for the scaffold phase** (`record_run.py`, generate.md Step 9).
`design`, `plan`, `audit`, `refactor` — the phases that touch RFCs, roadmaps, and *real user
code* — leave no mechanical record of what the agent did, which gates it ran, and what they
returned. An enterprise audit ("show me every agent action on this repo in June") cannot be
answered from the artifacts. Related: checkpoints carry no timestamp/actor (see issue 0006).

**Direction:** generalize the run-record schema to a phase-tagged action record
(`phase:`, `gates:` with results, `at:`), emitted by each phase's deterministic spine.

## 2. No concurrency story for the manifest

`project.yaml` is the single mutable source of truth, but nothing detects concurrent
mutation — two agent sessions (or an agent + a human editor) interleaving writes lose
updates silently. Enterprise teams *will* run parallel sessions.

**Direction:** cheap optimistic concurrency — a `manifest_rev:` counter or content-hash
check in the tools that read-then-expect-the-agent-to-write (`eados.py`, `phase_runner
--propose` prints the hash it validated against; the confirmation step compares).

## 3. Learning loop blind spots

- Lessons/rubric capture is generation-centric; refactor-phase incidents (the riskiest
  surface: real user code) have no `--failure` channel equivalent.
- `autotune --threshold 2` can propose a default flip from two records — fine for now, but
  document the confidence floor or scale it with corpus size before the corpus grows.
- Run records may embed manifest scalar values verbatim (`chosen:`); if a manifest ever
  carries a sensitive value (internal hostnames, registry URLs), it lands in the committed
  ledger. Consider a redaction/deny-list for override keys.

## Acceptance

Each numbered gap spun into its own scoped issue; this epic tracks the umbrella.