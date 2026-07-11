# [EPIC] Enterprise-readiness gaps: cross-phase audit trail, manifest concurrency, learning-loop phase coverage

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Epic delivered via its three children: audit trail [#216](https://github.com/danielPoloWork/pgs-eados/pull/216) (issue #213), manifest concurrency [#217](https://github.com/danielPoloWork/pgs-eados/pull/217) (issue #214, `manifest_rev`/`--expect-rev`), learning-loop coverage [#218](https://github.com/danielPoloWork/pgs-eados/pull/218) (issue #215 — refactor failure channel, corpus-scaled autotune floor, override redaction). Umbrella issue [#203](https://github.com/danielPoloWork/pgs-eados/issues/203) CLOSED. Guarded by `test_phase_runner.py`, `test_record_run.py`, `test_run_records.py`, `test_autotune.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

> **✅ Residuals delivered** (2026-07-11, closes [#250](https://github.com/danielPoloWork/pgs-eados/issues/250) — M15 Wave 3, the milestone closer).
> The enforcement whitespace this epic left is shut: **`git_check.py`** evaluates the
> `os/git/git.yaml` policy (branch naming, Conventional-Commit shape, one-PR — the new
> cross-cutting `git-policy` gate; `--advisory` for local pre-flight); a **human-gated
> checkpoint must record `gate_results`** covering its entry gates, and the last checkpoint's
> marks are **re-run for divergence** on the ctx-free gates (a recorded OK whose gate now FAILs
> — or now skips because its subject was removed — is stale, not evidence); the documented
> **`traceability-lint` gate finally evaluates in-process AND guards a real move** (the sixth
> evaluator; `--links` threaded into the gate context; now an entry gate of `audit → migrate`,
> the audit procedure's step 1 enforced at the transition); and
> `design`/`plan`/`audit`/`migrate` each instruct the **uniform phase-tagged
> `record_run --phase` step** — the homogeneous per-phase audit trail this epic's gap 1 asked
> for. Guarded by `test_git_check.py` + `test_honor_hardening.py`.

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