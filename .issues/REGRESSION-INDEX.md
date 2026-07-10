# Regression index — the defect backlog `0001–0010` and its guarding tests

The ten defect/hardening drafts `.issues/0001-0010` were all **fixed and released in v2.7.0**
(2026-07-07, release [#219](https://github.com/danielPoloWork/pgs-eados/pull/219), commit
`83c6e4c`) and their originating GitHub issues **#194–#203 are CLOSED**. The drafts stayed in the
tree as an unclosed "open-work" picture; this index reconciles them (issue [#235](https://github.com/danielPoloWork/pgs-eados/issues/235))
and, more durably, **binds every closed defect to the named test that must stay green** — so a
future refactor that silently regresses a fixed defect trips a red gate instead of shipping.

Each fix was re-verified against the current tree before this index was written (the fix is present
in the code, the fix commit exists, and the listed test asserts the fixed behavior such that
reverting the fix turns it red). Every listed test is discovered and run by
[`tools/tests/run_all.py`](../.eados-core/tools/tests/run_all.py) in the self-lint CI job.

| Draft | Defect (one line) | GH issue | Fix PR | Merge commit | Guarding test(s) — the regression gate |
|---|---|---|---|---|---|
| [0001](0001-yamlmini-folded-scalar-silent-data-loss.md) | `yamlmini` silently dropped folded `>`/`>-`/`>+` block-scalar bodies instead of rejecting them | [#194](https://github.com/danielPoloWork/pgs-eados/issues/194) | [#204](https://github.com/danielPoloWork/pgs-eados/pull/204) | `6efebaf` | `test_loader.py` — the four folded-scalar cases in `SUBSET_REJECTIONS` must raise (`load_yaml` rejects loudly) |
| [0002](0002-render-in-place-clobbers-existing-files.md) | `render.py --in-place` overwrote pre-existing files, violating the additive/no-clobber posture | [#195](https://github.com/danielPoloWork/pgs-eados/issues/195) | [#205](https://github.com/danielPoloWork/pgs-eados/pull/205) | `2fc9aeb` | `test_render_guards.py` — `write_file` clobber-refusal unit + the all-or-nothing pre-scan E2E (`--force` opt-in) |
| [0003](0003-render-write-guard-missing-git-segment-check.md) | renderer write guard lacked the `.git`-at-any-depth refusal `sandbox.py` enforces | [#196](https://github.com/danielPoloWork/pgs-eados/issues/196) | [#206](https://github.com/danielPoloWork/pgs-eados/pull/206) | `b468fff` | `test_render_guards.py` — `_unsafe_path_value` + `group_path: .git/hooks` rejected at `--check`; `test_sandbox.py` — nested-`.git` write refused |
| [0004](0004-record-run-same-day-collision-forces-date-falsification.md) | a second same-day run could only be recorded by falsifying its `--date` | [#197](https://github.com/danielPoloWork/pgs-eados/issues/197) | [#207](https://github.com/danielPoloWork/pgs-eados/pull/207) | `4f1e0d1` | `test_run_records.py` — `resolve_dest` `-2`/`-3` suffix + the E2E asserting the second file's `date:` stays truthful |
| [0005](0005-autotune-lesson-audit-crash-on-malformed-record.md) | `autotune`/`lesson_audit` aborted with a raw traceback on one malformed run record | [#198](https://github.com/danielPoloWork/pgs-eados/issues/198) | [#208](https://github.com/danielPoloWork/pgs-eados/pull/208) | `273e1d2` | `test_autotune.py` + `test_lesson_audit.py` — one bad record is skipped+named, valid records still analyzed, exit 0 |
| [0006](0006-phase-state-advancement-is-honor-system.md) | phase-state advancement was honor-system — no check that gates were green at the transition | [#199](https://github.com/danielPoloWork/pgs-eados/issues/199) (+[#213](https://github.com/danielPoloWork/pgs-eados/issues/213)) | [#209](https://github.com/danielPoloWork/pgs-eados/pull/209) (+[#216](https://github.com/danielPoloWork/pgs-eados/pull/216)) | `4b9af49` (+`978ddb3`) | `test_phase_runner.py` — `checkpoint_chain_problems` (phase-skip/illegal-edge/`confirmed_by`) + live `gate_results`; `test_render_guards.py` — delivery-state consistency at `manifest-valid`; `test_phase_smoke.py` |
| [0007](0007-deterministic-gates-fail-open.md) | deterministic gates failed open (`skipped` never blocked); dead `--links` plumbing | [#200](https://github.com/danielPoloWork/pgs-eados/issues/200) | [#210](https://github.com/danielPoloWork/pgs-eados/pull/210) | `4917815` | `test_eados.py` — `--strict` fails `needs-input`, `skipped` still passes; `test_phase_smoke.py` — CLI exit-code (0 vs 1) |
| [0008](0008-interview-provenance-completeness-not-enforced.md) | `interview.provenance` completeness unenforced — partial blocks starved the learning loop | [#201](https://github.com/danielPoloWork/pgs-eados/issues/201) | [#211](https://github.com/danielPoloWork/pgs-eados/pull/211) | `ac16ce6` | `test_render_guards.py` — coverage + `questionnaire_version` required, block-absence still legal; `test_record_run.py` — `provenance_gaps` warns (not fails) |
| [0009](0009-agent-registry-check-is-one-way.md) | `check_agent_registry` was one-way — a README link to a deleted persona stayed green | [#202](https://github.com/danielPoloWork/pgs-eados/issues/202) | [#212](https://github.com/danielPoloWork/pgs-eados/pull/212) | `08938f4` | `test_agent_registry.py` — both directions (missing persona **and** dead index link), escaping links excluded |
| [0010](0010-enterprise-gaps-audit-trail-concurrency-phase-coverage.md) | enterprise epic: cross-phase audit trail, manifest concurrency, learning-loop coverage | [#203](https://github.com/danielPoloWork/pgs-eados/issues/203) (children [#213](https://github.com/danielPoloWork/pgs-eados/issues/213)/[#214](https://github.com/danielPoloWork/pgs-eados/issues/214)/[#215](https://github.com/danielPoloWork/pgs-eados/issues/215)) | [#216](https://github.com/danielPoloWork/pgs-eados/pull/216)/[#217](https://github.com/danielPoloWork/pgs-eados/pull/217)/[#218](https://github.com/danielPoloWork/pgs-eados/pull/218) | `978ddb3` / `4e67b13` / `eb3c348` | `test_phase_runner.py` — live `gate_results` + `manifest_rev`/`--expect-rev` CONFLICT; `test_record_run.py` — `phase:` tag + override redaction; `test_run_records.py` — `phase` schema gate; `test_autotune.py` — corpus-scaled floor |

## The shared invariant behind 0002 / 0003 — now lint-guarded

0002 and 0003 were closed by funnelling **every rendered-repo write through `sandbox.safe_write` /
`sandbox.resolve`** — the single guarded sink that enforces containment, the `.git`-segment refusal,
and no-clobber. `render.write_file` is now a pure delegator. To stop a future tool from silently
re-opening that defect class with its own `open(..., "w")`, the new **`safe-write` self-lint**
([`eados_lint.check_safe_write`](../.eados-core/tools/eados_lint.py)) asserts that no factory tool
writes directly outside the sandbox path, with an explicit, justified allow-list for the three
factory-internal writers that legitimately write outside a rendered repo (`record_run.py`,
`derive_links.py`, `sync_action_pins.py`) and the `sandbox.py` primitive itself. Guarded by
[`test_safe_write.py`](../.eados-core/tools/tests/test_safe_write.py) (a synthetic direct write is
caught; the shipped tree is clean).

## Verification note

Self-lint and the test suite run in CI on the reconciliation PR; the fix commits and CLOSED-issue
states above were confirmed via `git log` and `gh issue view` at reconciliation time (2026-07-10).
This is reconciliation, not re-fixing — no defect fix was modified.
