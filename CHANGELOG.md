# Changelog

All notable changes to `pgs-eados` (EADOS) are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/).

Every PR that introduces a user- or maintainer-visible change adds a line to `[Unreleased]`
in the same PR. Releases follow Semantic Versioning; the latest is **v2.6.0**.

## [Unreleased]

### Added

- **A transition's checkpoint now records live `gate_results` — the phase-tagged audit trail is the
  runner's own observation (#213, epic #203).** #199 enriched the checkpoint with `at:` and
  `confirmed_by:` and made `checkpoint_chain_problems` validate `gate_results` *when present*, but
  the live population of those results was deferred to the #203 audit-trail child — this closes it.
  `phase_runner.report_propose` now evaluates the proposed transition's deterministic entry gates
  **live** and records `{gate -> mark}` in the emitted checkpoint's `gate_results`, so the recorded
  evidence is what the runner actually observed, not a copy of the declared `entry_gates` from
  `workflow.yaml`. The evaluation reuses `eados.evaluate_gates` (new) over the existing
  `GATE_EVALUATORS` — one source of truth for the deterministic marks, shared with `run_phase` — and
  is threaded via an **injected** evaluator so the engine stays testable and free of a
  `render ↔ phase_runner ↔ eados` import cycle (the `phase_runner` CLI imports `eados` lazily and
  gained `--rfc` / `--roadmap` to feed the gate inputs). A gate that is not `OK`/`manual` prints a
  **NOT READY** line — the move is not ready to record, the same rule `checkpoint_chain_problems`
  enforces at `manifest-valid` time — while the exit code stays `0` for a *legal* move (legality,
  not gate satisfaction; `eados.py <phase> --strict` remains the fail-closed gate check). Together
  with #199's `from`/`to`/`at`/`confirmed_by`, the enriched checkpoint is the phase-tagged action
  record for **every** transition (`design`/`plan`/`audit`/`refactor`), not just `scaffold` at
  Step 9. Covered by `test_phase_runner.py`, `test_eados.py`, and `test_phase_smoke.py`; the
  `walkthrough.md` transcript shows the live `gate_results`.

- **The `agent-registry` self-lint is now bidirectional — a dead index link is caught, not just a
  missing persona (#202).** `check_agent_registry` failed a persona file missing from
  `agent/README.md`, but never the reverse: a registry line linking a persona that was **deleted or
  renamed** stayed green (it only iterated files that exist on disk), unlike its sibling hygiene
  checks (`workflow-safety`, `gate-coverage`, `authority-personas`) which are all symmetric. The
  check now also fails when a persona-relative `.md` link in the index points at a file that does
  not exist under `agent/`. Links that **escape** `agent/` — `../config/README.md`,
  `../learning/README.md`, `http(s)://…`, absolute paths, and the index's own `README.md` — are
  correctly excluded from the on-disk probe. The both-directions contract is factored into a pure,
  injectable `agent_registry_problems(index_text, persona_rels)` helper (mirroring
  `workflow_safety_problems` / `gate_coverage_problems`), and a new `tools/tests/test_agent_registry.py`
  covers both directions plus the escaping-link exclusion.

- **Interview provenance is enforced *complete*, not just well-shaped — a partial block no longer
  silently starves the learning loop (#201).** The learning loop derives its entire input (every run
  record's `overrides:`) mechanically from the manifest's `interview:` provenance block, and
  `derive_overrides` treats an **unrecorded** section exactly like an explicitly `defaulted` one. The
  #169 guard checked only the *shape* of the entries present, so a lazily-filled block — `identity:
  asked` but `language`/`governance`/… omitted — passed the gate and quietly suppressed override
  derivation for the omitted sections, landing a short `overrides:` list that starves `autotune` /
  `lesson_audit`. `validate_manifest` now additionally requires, when an `interview:` block is
  present, a provenance entry for **every** answer-bearing top-level section that exists in the
  manifest (all top-level keys except `schema_version` / `delivery_state` / `interview`) and a
  non-empty `questionnaire_version` — naming the missing section(s). Block **absence** stays legal
  (legacy manifests). `record_run.py` gains a `provenance_gaps()` helper and prints a per-section
  **warning** at record time for any section missing an entry (a warning, not a failure — the gate
  already rejects a partial block; this catches a manifest recorded without `--check`). The
  `project.yaml.template` and `interview.md` now document the completeness requirement.
  `tools/tests/test_render_guards.py` covers the coverage-gap and missing-`questionnaire_version`
  rejections; `test_record_run.py` covers `provenance_gaps`.

- **Phase gates are fail-closed under `--strict`, and `eados.py` no longer carries a dead
  `--links` affordance (#200).** `eados.py <phase>` returned exit 0 unless a gate it could compute
  `FAIL`ed — but several gates returned `skipped` when their *input was withheld*, so a gate was
  **satisfiable by omission** (the cheapest way to pass `roadmap-covers-rfcs` was to record no RFC
  refs; `rfc-approved` passed whenever the caller forgot `--rfc`). That is the opposite of EADOS's
  fail-closed posture everywhere else. Gate marks now distinguish **`skipped`** (input genuinely not
  applicable — nothing to check yet) from **`needs-input`** (a checkable input was withheld), and a
  new **`--strict`** flag flips `needs-input` to a phase failure. `rfc-approved` returns
  `needs-input` (not `skipped`) when `delivery_state.refs.rfcs` is non-empty but no `--rfc` is given;
  `roadmap-covers-rfcs` returns `needs-input` when RFC refs or the roadmap are missing — so a project
  that *has* something to verify can no longer exit the phase without the check running. The dead
  `links=`/`ctx["links"]` plumbing is removed from `run_phase` (the `traceability-lint` gate is
  cross-cutting — `required_for: []` — and is evaluated on the `status`/doctor path, not as a
  transition gate), so no parameter is threaded without a reader. `tools/tests/test_phase_smoke.py`
  and `test_eados.py` cover the strict-fail and skipped-pass paths.

- **Phase-state transitions are no longer honor-system — a `delivery-state-consistent` check closes
  the phase-skip gap (#199).** The phase runner reports legal transitions but never advances state;
  the agent writes `delivery_state.phase` and the checkpoint. Nothing verified, after the fact, that
  the recorded chain justified the phase — so a hallucinating or shortcut-taking agent could set
  `phase: scaffold` without the intervening `init -> design -> plan -> scaffold` checkpoints, and no
  gate noticed. A new pure `phase_runner.checkpoint_chain_problems(manifest, workflow)` now validates
  that `delivery_state.checkpoints` is a **legal, contiguous transition chain** through the
  overlay-applied `workflow.yaml`, **ending at the current `phase`**, with a **`confirmed_by:`** on
  every human-gated move and (when present) all `gate_results` marked `OK`/`manual`. It is enforced
  by `validate_manifest` (the `manifest-valid` gate / `render.py --check`), so a phase-skip is now a
  hard, actionable failure; a legacy manifest with no `delivery_state` stays exempt. The checkpoint
  the runner emits is enriched to carry the evidence — `at:` (the transition date) and, for a
  human-gated move, `confirmed_by:` (a `<owner>` placeholder the human fills) — reconciling the
  `project.yaml.template` schema and the `walkthrough.md` transcripts with what the runner writes.
  `tools/tests/test_phase_runner.py` and `test_render_guards.py` cover the enriched checkpoint and
  both the legal-chain and illegal-skip/broken-chain/missing-`confirmed_by` cases. (Wiring the
  checkpoint's `gate_results` from a **live** evaluation of the deterministic gates is tracked with
  the audit-trail work in the #203 epic; the chain check already validates them when present.)

### Fixed

- **`yamlmini` rejects folded `>` block scalars loudly instead of silently dropping their body
  (#194).** The dependency-free loader documented folded `>`/`>-`/`>+` scalars as out of scope and
  claimed to reject them, but two code paths conspired to *skip* the body (`_reject_unsupported`)
  and keep the bare `">"` (`parse_map` fell through to `_scalar`) — the exact #153 silent-truncation
  class the loader exists to prevent. `_reject_unsupported` now raises a `ValueError` naming the
  offending line for the whole `>` family, both as a mapping value (`key: >`) and a sequence item
  (`- >`), before `parse_map` is reached. **This was live in the repo's own profiles:** every
  `orchestrator/profiles/*.yaml` (and `_template.yaml`) used `notes: >`, so the `notes` body had
  been silently loading as the one-character string `">"`; all 20 are converted to a literal block
  scalar (`notes: |`), which `yamlmini` parses byte-exactly and which now agrees with PyYAML. Four
  folded-scalar cases join `SUBSET_REJECTIONS` in `tools/tests/test_loader.py` (the differential
  confirms PyYAML parses them, proving the rejection is a deliberate subset boundary and not a
  misparse), and the module docstring's "reject, never guess" claim for `>` is now truthful.

- **A second same-day run record no longer requires falsifying its date (#197).** `record_run.py`
  refused to overwrite an existing `<date>-<slug>.yaml` — correct, records are facts — but its only
  suggested remedy was `--date`, which sets *both* the filename date and the record's `date:` field,
  so the maintainer had to write down a date the run did not happen on to record a second same-day
  run. That second run is the common case: a failed bootstrap (`--outcome failed`) then its fixed
  re-run hours later — exactly the failure→success pairing the auto-tuner (#172) and `lesson_audit`
  (#173) mine. The recorder now disambiguates the **filename** with a sequence suffix
  (`<date>-<slug>-2.yaml`, `-3`, … via the new pure `resolve_dest`) while the `date:` field stays
  the true run date, and the misleading "use `--date` to disambiguate" hint is gone. The
  `run-records` self-lint gate (#175) validates record *content*, not filenames, so the suffixed
  form needs no gate change; `learning/runs/README.md` documents it. `record_run.py`'s success
  message is also now cross-drive-safe (a display path must never crash the tool after the record is
  written). `tools/tests/test_run_records.py` covers the `-2`/`-3` progression and an end-to-end
  same-day pair asserting two distinct files and a truthful second `date:`.

- **The learning-loop miners skip one malformed run record instead of aborting the whole analysis
  (#198).** `autotune.py` and `lesson_audit.py` read every `learning/runs/*.yaml` through the
  minimal loader in a bare loop, so a single record outside its subset (a folded scalar, an unclosed
  quote) killed the entire run with an uncaught `ValueError` traceback — and `autotune` had no
  non-mapping-root guard either, so a record parsing to a scalar/list raised `AttributeError`. These
  are report-only tools that also run on bundles and fresh checkouts where the `run-records` gate may
  never have executed, so they must degrade **per file**. Both now wrap the per-record
  `load_yaml` in `try/except (OSError, ValueError)`, skip a non-mapping root, print a
  `skipping <file>: <error> (run eados_lint run-records)` line to stderr, and keep going at exit 0;
  the valid records still yield proposals. `autotune`'s "N run(s) analyzed" count now reflects the
  records actually parsed, not the raw file count. The advisory CI steps (`ci.yml`) therefore print
  a per-file skip rather than a stack trace. `tools/tests/test_autotune.py` and
  `tools/tests/test_lesson_audit.py` cover a mixed valid/malformed directory (and the non-mapping
  root for `autotune`).

### Security

- **The renderer refuses to clobber pre-existing files — additive by default, `--force` to
  regenerate (#195).** `render.write_file` opened every destination in truncating mode, so an
  `--in-place`/`--out` render silently overwrote a pre-existing `README.md`, `LICENSE`,
  `.gitignore`, `AGENTS.md`, `.github/workflows/*`, etc. — destructive, non-`git`-reversible data
  loss in exactly the "existing repo" scenario the guided installer advertises as safe, and the
  opposite of the "never overwriting" contract the `refactor` sandbox already enforced and the
  README "Security posture" already claimed the renderer honoured. The renderer now **plans every
  write and pre-scans for collisions across the whole template walk**, then — unless `--force` is
  passed — lists every colliding path and aborts **before writing a single byte** (all-or-nothing;
  a failed render never leaves a repo half-clobbered). `write_file` now **delegates to
  `sandbox.safe_write`**, so containment, the `.git`-at-any-depth refusal, and the no-clobber guard
  are a *single* implementation shared with the `refactor` phase and the two write paths cannot
  drift again (ADR-0007 addendum, 2026-07-06). A new `--force`/`--overwrite` flag is the sole opt-in
  for the greenfield/regeneration case, and `tools/tests/test_render_guards.py` covers the refusal,
  the byte-for-byte survival of the pre-existing file, and the `--force` path end-to-end.

- **A `.git` path segment in a manifest is rejected at validation time, not just at write time
  (#196).** `render._unsafe_path_value` accepted `.git` as an ordinary segment, so a manifest with
  `language.group_path: ".git/hooks"` passed `validate_manifest` and only tripped `write_file`'s
  guard at write time — and before #195 nothing stopped it, letting a manifest steer a seeded
  `.gitkeep` into VCS metadata (`.git/hooks/` is an execution vector on the next commit). It now
  fails `--check` up front: `_unsafe_path_value` refuses a `.git` segment at any depth by **exact
  match**, matching `sandbox.resolve`, so `.gitignore` files and `foo.git/` directories stay legal
  and the actionable message names `.git`. `tools/tests/test_render_guards.py` covers `.git`,
  `.git/hooks`, `a/.git/b`, and `src/.git` at the unit level (with `.gitignore`/`foo.git` proven
  still-legal) and end-to-end (`--check` and `--out` both exit non-zero; nothing lands under a
  `.git/`). Renderer and refactor sandbox now share the containment path *and* apply an equivalent
  `.git` guard at both validation and write time (ADR-0007).

## [2.6.0] - 2026-07-05

### Added

- **README: complete the tools table, add "How EADOS learns", date-stamp the model claims (#176,
  M13).** New **"The tools"** section groups the full `tools/` surface (all 27 tools) into
  *generate / govern / verify / learn* — the phase-pipeline spine (`eados.py`, `doctor.py`,
  `preflight.py`, `pr_review.py`, `seed_milestones.py`, …) is no longer invisible; the repo-layout
  tree gains `orchestrator/os/`, `domains/`, and `commands/`. New **"How EADOS learns"** section
  documents the versioned, human-gated memory (the `lessons.yaml` / `runs/` / `autotune` +
  `lesson_audit` / ADR table — who writes, approves, enforces) and the escalation path *incident →
  lesson → gate → meta-gate*, describing behavior that has now shipped (#171–#175). The stale
  *"Fable 5 not yet available"* model claim is fixed and **date-stamped** ("as of 2026-07") in both
  the prerequisites and the FAQ. i18n: EN source hash refreshed (`b8c027cdd842` → `dbf449c097c2`)
  and the `zh-Hans` / `ja` translations updated in the same PR (version-lockstep + i18n-freshness
  green).

- **The learning loop is inside the enforcement perimeter — `run-records` self-lint gate (#175,
  M13).** Per the gate-coverage mandate (*gate every externally-modifiable file class*),
  `learning/runs/**` moves from allow-listed prose to a **validated** class. A new `eados_lint`
  check (`run_record_problems` + `check_run_records`) validates every `learning/runs/*.yaml`
  against the recorder schema (#172): the five required keys (`slug`/`date`/`lang`/`kind`/
  `outcome`), the `outcome` vocabulary, `date` shape, override `{key, default, chosen}` triples,
  `failures` `{gate, message}` shape (with the rule that a recorded failure implies
  `outcome: failed`), `lessons_applied` id form, and rubric dimensions 0–2 drawn from the ten —
  reusing `record_run.py`'s own `OUTCOMES`/`RUBRIC_DIMENSIONS` so the writer and the gate share
  **one** schema. A malformed record now fails CI with a named, actionable message instead of
  silently poisoning the auto-tuner and the lesson audit; the gate-coverage meta-gate accounts
  for `learning/runs/**` as validated. The empty-dir state (only `runs/README.md`) stays green
  until the first record lands.

- **Review-time lesson capture — PR `Lesson:` field + `lesson_sweep.py` + ledger backfill (#174,
  M13).** The lessons ledger held two entries across ~160 merged PRs because the capture point was
  wrong: end-of-run recollection instead of review time. The factory **PR template** (and the
  generated-repo `PULL_REQUEST_TEMPLATE.md.tmpl` for parity) now carries an optional one-line
  `Lesson:` field; because squash-merge makes the PR body the permanent `main` commit
  (`os/git/git.yaml` `commit.squash_body`), **a merged lesson is owner-approved by construction**.
  New `tools/lesson_sweep.py` sweeps merged PR bodies for that field and **prints** draft
  `learning/lessons.yaml` entries for the owner to approve — it never writes the ledger (lessons
  stay human-approved), and, like `derive_links.py`, its parser is pure/tested while the `gh` fetch
  degrades cleanly offline (exit 2). **One-time backfill:** the #153 silent-truncation discovery
  and the ADR-0009 §3 "re-discovered design decision" episode are promoted to **L-0003 / L-0004**.

- **`lesson_audit.py` — the learning-loop watchdog (#173, M13).** A report-only tool
  (`tools/lesson_audit.py [--threshold N]`), same posture as `autotune.py`: it reads the
  accumulated run records (#172) and reports three learning-loop signals without touching disk.
  **Regression detection** — a run whose `failures` share keywords with a lesson it was in scope
  for means the factory violated its own recorded knowledge, which per the escalation path
  (*incident → lesson → gate → meta-gate*) is the trigger to promote that advisory lesson to a
  mechanical gate. **Dead-lesson report** — a lesson never present in any `lessons_applied`
  across at least `--threshold` runs it was *applicable* to (scope-matched, so a kind-scoped
  lesson is not called dead merely because no run of that kind exists) is flagged for retirement.
  **Rubric trending** — a `eval/rubric.md` dimension scoring ≤ 1 in the majority of the runs that
  scored it proposes drafting a lesson, mechanizing rubric §4. Dependency-free (reuses
  `render.load_yaml` and `record_run.RUBRIC_DIMENSIONS`; parses the sequence-rooted ledger
  textually like `eados_lint`'s `check_lessons`); fixture-tested end-to-end and pinned against
  the real ledger.

- **`record_run.py` — mechanized run records with a failure channel and rubric scores (#172,
  M13).** One command (`tools/record_run.py <manifest> [--outcome ok|failed]
  [--failure GATE=MESSAGE] [--lesson L-NNNN] [--rubric DIM=SCORE]`) replaces the hand-authored
  YAML that kept `learning/runs/` empty: the `overrides:` list derives **mechanically** from the
  manifest's `interview:` provenance block (#169) against the built-in defaults in
  `project.yaml.template` — a non-`defaulted` section's scalar leaf that differs from a
  non-empty template default becomes `{key, default, chosen}`; nothing is reconstructed from
  recollection. The run-record schema gains `outcome`, `lessons_applied` (ids must exist in the
  ledger), `failures` (**a red bootstrap CI lands durably as
  `--outcome failed --failure ci-bootstrap="…"`** instead of evaporating — audit finding U3),
  and `rubric` (the ten `eval/rubric.md` dimensions, 0–2). Records are facts: existing files are
  never overwritten; emission is loader-safe and round-trip-tested; `autotune.py` consumes the
  extended records unchanged. `generate.md` Step 9 now references the exact command; pure core +
  thin CLI per the `pr_review.py` pattern, fixture-tested end-to-end against `reference.yaml`
  (which yields its one genuine override: `governance.capabilities.bench` false→true).

- **The deterministic path has a spec-substance floor (#170, M13).** `validate_manifest` now
  rejects a hollow spec with actionable messages: an empty `spec.objective` or
  `spec.verification`, zero `spec.functional_reqs`, or zero `spec.milestones` each fail the
  render/`--check`/`manifest-valid` gate instead of producing "Render: OK" and a hollow
  repository (blank SPEC.md, a roadmap with nothing beyond the bootstrap). A **floor, not a
  taste test** — presence only; measurability stays the rubric's job — and no library escape
  hatch (even a library has an objective and one requirement). Documented at the authoring
  point (`project.yaml.template`); `examples/reference.yaml` passes untouched; minimal test
  fixtures raised to the floor.

- **The manifest records interview provenance — asked vs defaulted vs imported (#169, M13).**
  New `interview:` **state block** (same class as `delivery_state`; in `KNOWN_SECTIONS`, never a
  placeholder source): per top-level answer key, `asked | defaulted | imported`, plus
  `questionnaire_version`. `validate_manifest` rejects a wrong value, a key that is not a
  top-level key of the manifest, or a shapeless block — so a considered answer and a silent
  assumption can no longer look the same, and a manifest produced by a phase-skipping agent is
  distinguishable from a diligent one. `interview.md` now mandates transcribing provenance **as
  the interview proceeds** (never retrospectively) and its confirmation step points the
  maintainer at the `defaulted` entries; `questionnaire.yaml` `meta.provenance: as-you-go`
  records the rule as data; `project.yaml.template` carries a commented example and
  `examples/reference.yaml` a real block (render output byte-identical — state, not
  substitution input). This is the input feed `autotune.py` and the M13 run-recorder (#172)
  have been starving for.

- **Gate `runs:` commands are executable again — and gated (#164, M13).** `render.py` gains
  `--check` (validate-only: load → `build_context` → `validate_manifest` → report; **writes
  nothing**; mutually exclusive with `--out`/`--in-place`), so the `manifest-valid` gate command
  documented at `workflow.yaml` is now real. New `eados_lint` check #17 **`gate-executability`**
  guards the whole data→code seam: every `python <script> …` gate must name a script that exists
  (in the factory, or shipped via `templates/` into generated repos) whose source knows each
  `--flag` it is passed, and the new machine-readable `wired: in-process | external` gate key must
  match `eados.py`'s `GATE_EVALUATORS` exactly — the pre-M6 "future tooling" comment is replaced by
  enforcement. Schema updated; `tests/test_gate_executability.py` (incl. running the exact
  documented command against `reference.yaml`) wired into CI.

### Changed

- **The generation playbook itself now recalls and records — the learning loop is wired where
  the compliant agent actually walks (#171, M13).** `orchestrator/generate.md` — the ordered
  playbook whose header says *"do not improvise the order"* — gains **Step 0.a Recall** (read
  `learning/lessons.yaml`, apply every lesson whose `scope` matches `global`/`lang:*`/`kind:*`,
  carry the applied ids through the run) and **Step 9 Record** (append the run record —
  asked-vs-defaulted from the `interview:` provenance block, lessons applied, gate outcomes —
  and draft any generalizable lesson for maintainer approval; a run is not finished until it is
  recorded). The output report gains `lessons_applied:` and `run_record:` lines.
  `agent/enterprise-architect.md`'s operating loop now *points at* the playbook steps instead of
  restating them (single source of truth) while keeping Recall before the interview. Before
  this, Recall/Record lived only in the persona and the playbook never mentioned them — an
  agent following the playbook to the letter never touched memory (`learning/runs/` empty,
  2 lessons across ~160 merged PRs).

- **The test suite is discovered, never enumerated (#168, M13).** New
  `tools/tests/run_all.py` globs `test_*.py`, runs each in its own interpreter, echoes a failing
  script's output, and exits non-zero on any failure (`--exclude NAME`, repeatable, for scripts
  another job runs in a special context). `ci.yml`'s hand-maintained ~33-line unit block and
  ~60-path `py_compile` mega-line — two lists a new test had to remember to join, where a
  forgotten line meant a test that exists and **never runs** — are replaced by the single runner
  invocation and a recursive `python -m compileall -q .eados-core/tools`. A new `test_*.py`
  dropped into `tools/tests/` now runs in CI with **zero** ci.yml edits. `CONTRIBUTING.md` §5 and
  the README contribution flow (EN/zh-Hans/ja, i18n hash refreshed) now point at the runner.
- **`eados_lint` checks are reentrant — the failure reporter is threaded, not global (#167,
  M13).** Signature-only refactor: every `check_*(fail)` receives the reporting callable and the
  new `run_checks()` owns the per-run accumulator (mirroring how `render()` threads its `errors`
  list), removing the last module-global mutable state from the linter. All 17 checks become
  independently runnable/testable units without splitting the file; output is byte-identical
  (verified on the green tree and on a seeded broken fixture).
- **The YAML loader is its own module, and the #153 truncation class is rejected loudly (#166,
  M13).** The dependency-free loader moved from `render.py` into **`tools/yamlmini.py`** — every
  gate tool parses through this one module, so renderer changes can no longer perturb the parser
  under every gate (`render.load_yaml` stays a re-export; zero caller changes). The two constructs
  behind the #153 silent truncation are promoted from comment discipline to **mechanical
  rejection** in `_reject_unsupported`: a quoted scalar that opens but does not close on its line,
  and a flow collection (`[…]`/`{…}`) left open at end-of-line, each raise a loud `ValueError`
  naming the line instead of silently dropping everything after it (block-scalar bodies stay
  exempt — they are literal content). The PyYAML differential test gains a `SUBSET_REJECTIONS`
  corpus proving each rejected construct is *legal* YAML — so the loud rejection, never a
  misparse, is the honest subset boundary — plus false-positive guards (apostrophes in plain
  scalars, quoted list items, unbalanced quotes/brackets inside block scalars); the
  `questionnaire.yaml` #153 comments now point at the mechanical gate (ADR-0006/0008 posture:
  reject, never guess).

### Fixed

- **A leading UTF-8 BOM no longer breaks manifest parsing.** `yamlmini.load_yaml` strips exactly
  one leading U+FEFF (utf-8-sig semantics, PyYAML-verified) — a manifest saved by Windows Notepad
  or PowerShell 5.1's `Out-File -Encoding utf8` used to glue the BOM to the first top-level key
  and fail validation with a confusing `unknown top-level section '﻿identity'` plus phantom
  missing-field errors. `render.py` also strips it from the raw text feeding the duplicate-key
  scan. Two differential CASES (PyYAML must agree byte-for-byte) and two loader-only invariants
  (clean first key; a *double* BOM is content and stays) in `test_loader.py`.
- **Domain overlays are actually applied (#165, M13).** `workflow.yaml`'s `domain_overlays`
  (web → `accessibility-review` + `web-vitals-budget`; game → `asset-pipeline-review` +
  `hardware-budget`; mobile → `store-compliance`) were read by no engine — a game/web/mobile
  project silently got the base pipeline. New pure merge `phase_runner.apply_overlay(workflow,
  domain)` (wired into `eados.py`, `doctor.py`, and the phase-runner CLI via the manifest's
  `domain` scalar): `insert_states` join the machine as human-owner states and each `add_gates`
  id joins the `entry_gates` of every transition into the state(s) its registry entry names in
  `required_for` — the registry, not code, says where a domain gate bites. The four overlay gates
  now have honest registry entries (`kind: manual`, `wired: external`, `blocking: true`), `/eados
  status` surfaces the applied overlay (`domain: game (overlay applied: +state
  asset-pipeline-review, +gate hardware-budget)`), and cross-spec-consistency **rejects** a bare
  overlay id with no registry entry (the old lenience — an overlay id counted as a definition —
  is removed, and the test that codified the hole is flipped). A `software`/base project is
  byte-identical to before (pass-through, same object).
- **No silent `it/d4np` namespace fallback (#163, M13).** `render.py` no longer defaults a missing
  `language.group_path` to the reference project's `it/d4np` — the `{{GROUP_PATH}}` required-field
  guard (previously dead code, since the fallback was injected before validation) now fires, so the
  deterministic path fails loudly instead of stamping the factory owner's namespace into a
  stranger's repository. The questionnaire (Q1.3) and `project.yaml.template` drop their `it/d4np`
  pre-fills to match `interview.md` ("no built-in default"); `it/d4np` survives only in
  `examples/reference.yaml`, where it is truthful. Regression tests (unit + end-to-end) in
  `test_render_guards.py`.

### Security

---

## [2.5.0] - 2026-07-01

### Added

- **Authoring languages asked, not silently defaulted (#150, M12; ADR-0016).** `Q4.7` is now the
  **unconditional authoring-languages question**: it states and confirms the **documentation
  language** (`DOC_DEFAULT_LANG`, default `en`), a new **code-comment language**
  (`language.comment_lang` → `{{CODE_COMMENT_LANG}}`, default `en`), and any **extra doc
  languages** — naming targets is what enables i18n, instead of the i18n toggle hiding the language
  question. Identifiers, public API names, commits, branches, and PR text stay **English
  regardless** (the cross-project consistency bar); a non-English comment or doc choice is honoured
  as a **recorded exception** rendered into the generated `AGENTS.md` §2 (new derived flags
  `{{#IF_COMMENT_LANG_NONEN}}` / `{{#IF_DOC_LANG_NONEN}}`), so the generated contract always tells
  the agent the truth about the repo it governs. With the `en`/`en` defaults the rendered output is
  byte-identical to before. Decision recorded in **ADR-0016** (+ the missing ADR-0015 index row
  restored). Fixture-tested (`tests/test_authoring_language.py`) and wired into CI. Completes M12.
- **Spec provenance: import-and-validate branch (#153, M12).** Phase 5 no longer assumes the spec is
  co-authored from scratch: a new **`Q5.0 — provenance`** question (asked **first**; `import` |
  `coauthor`, default `coauthor`) lets a maintainer who already has a technical spec / PRD / SRS take
  an **import-and-validate** path — the document is mapped onto the six-section spec shape and run
  through a **gap audit** (each section/requirement gets the Phase-5 testability follow-up, "how
  would CI prove this failed?"), and only the flagged gaps are asked, instead of re-narrating the
  whole document through Q5.1–Q5.7. Both paths converge on the same frozen
  `docs/specs/01_spec_<slug>.md`; the manifest records `spec.provenance`. ADR-0002
  (interview-driven intake) updated. Fixture-tested (`tests/test_spec_provenance.py`) and wired
  into CI.

- **Optional layered package scaffold (#152, M12).** A `service` / `app` / `web` project can now opt
  into a **layered internal layout** instead of the flat source tree. A new Phase-5 interview
  follow-up (gated on `PROJECT_KIND in {service, app}` or `domain == web`, driven by the architecture
  style from #151) captures the layer packages; the manifest carries `capabilities.layered` +
  `spec.layers` (e.g. `[controller, service, repository, dto, mapper]`), and the generator seeds each
  as an empty (`.gitkeep`) package under **both** `src/main/…` and `src/test/…`, recording the layout
  in the generated **ADR-0002**. Non-identifier layer names are skipped (write containment
  backstops it), and a **library keeps the flat shape** (nothing seeded). New render placeholders
  `{{#IF_LAYERED}}` + `{{#EACH_LAYER}}` (documented in `placeholders.md`). Fixture-tested
  (`tests/test_layered_scaffold.py`: build_context wiring, end-to-end render of main+test packages,
  name-sanitisation, library-stays-flat, ADR record) and wired into CI.
- **Architecture-style & design-pattern elicitation (#151, M12).** The interview now captures the
  project's **architectural style** and **pattern posture** instead of shipping a rich taxonomy
  nobody commits to and an empty catalogue. `Q5.4` elicits a structured `spec.architecture_style`
  (from `design-patterns.md` §5, with per-kind/domain defaults — a library commits to none), the
  **expected first-class patterns** (`spec.patterns: [{name, why}]`), and a **pattern-discipline
  posture** (`spec.pattern_discipline: advisory | enforced`). These carry into the manifest and
  **seed the generated `docs/patterns/README.md`** — an architecture-style note (with a graceful
  inverted-section fallback for a library) + *Planned* rows for each named pattern — via new render
  placeholders `{{ARCHITECTURE_STYLE}}`, `{{PATTERN_DISCIPLINE}}`, `{{#EACH_PATTERN}}`, and the
  `{{#IF_ARCHITECTURE_STYLE}}` flag (documented in `placeholders.md`). The reference manifest shows
  it (Object Pool / Free List). Fixture-tested (`tests/test_architecture_style.py`: populated,
  empty-library, and reference end-to-end) and wired into CI.
- **First-class `web` domain + enterprise posture (#149, M12).** New shipped
  `orchestrator/domains/web.yaml` (website / web app / web service): baseline authority roles with a
  web vocabulary (`product-owner` / `web-architect` / `full-stack-lead` via `role_labels`),
  **hard** accessibility + Core Web Vitals NFR budgets (plus security + latency), a `[design, content]`
  cross-discipline pipeline, and a new `web` overlay in `workflow.yaml` (`accessibility-review` +
  `web-vitals-budget` gates). `Q0.4` now offers `web` (`interview.md` + `questionnaire.yaml`), and a
  new **`Q0.5 — enterprise posture`** captures `governance.posture: standard | enterprise` as an
  **orthogonal flag** that raises the governance/compliance bar on *any* domain — deliberately **not**
  a fourth domain (a `domain_overlays` key must be a domain id, and the posture is axis-independent).
  Decision recorded in **ADR-0015**; the manifest template carries `governance.posture` (default
  `standard`). Enumerations refreshed across the domain README/schema, workflow schema, RFC-0001
  diagram, and the (i18n-tracked) README tagline (EN/zh-Hans/ja + source-hash bump
  `8463caf13561`→`0a980fcdd7aa`). Fixture-tested (`tests/test_web_domain.py`) and wired into CI;
  passes `domain-completeness` + cross-spec.
- **Environment preflight (#154, M12).** New dependency-free `tools/preflight.py` detects the
  toolchain the pipeline assumes — the running Python version vs a floor, `git`, `gh`, and
  `gh auth status` — and prints an **OS-specific install/auth hint** (Windows / macOS / Linux) for
  anything missing, exiting non-zero so it doubles as a pre-flight gate. Partial environments (e.g.
  git present, gh absent) degrade to clear per-tool guidance, never a traceback; `--no-gh` drops the
  GitHub CLI to advisory for the pure render path. `/eados init` runs it first and surfaces the
  verdict in its hand-off; `generate.md` Step 0 re-runs it before scaffold/bootstrap. Because a
  Python tool cannot help when Python itself is absent, `setup/setup.sh` and `setup.ps1` carry a
  **non-Python bootstrap hint** that flags a missing interpreter with an OS-appropriate install line.
  Fixture-tested (`tests/test_preflight.py`, injected which/run/version/platform + a behavioural
  no-traceback tail), UTF-8-guarded, and wired into CI.
- **PR-metadata contract as data (#141, M11).** `os/git/git.yaml` now encodes a `pr.metadata`
  block — the GitHub fields **set on creation** (`assignee`, one type `label`, `milestone`,
  `project`-if-present) — kept distinct from `required_crosslinks` (the RFC/milestone references
  the PR *body* carries for traceability). The git-workflow docs (`AGENTS.md` §6 + the
  `git-workflow.md.tmpl` / `AGENTS.md.tmpl` / PR-template renders) now show the exact
  `gh pr create` flags, including `--project`. New advisory tool
  `tools/pr_metadata_check.py --pr N` verifies an open PR carries assignee + label + milestone
  (Project advisory); pure core fixture-tested, thin `gh` shell degrading offline, wired into CI.
- **Seed all roadmap milestones on GitHub (#143, M11).** New helper
  `tools/seed_milestones.py ROADMAP.md` reads the roadmap and prints (or `--run` executes) the exact
  `gh api …/milestones` calls to create **every** milestone as `MN — <name>` (em-dash) with a
  goal-derived description — not just the first. `generate.md` Step 6 and `github-setup.md.tmpl` §5
  now seed the full board so milestone-scoped PR delivery starts against a complete project, and the
  PR-metadata docs reference the open **roadmap** milestone (`MN — name`) rather than a `vX.Y.Z`
  release milestone — matching EADOS's own `M1 … MN`. Parser is markdown-only, dependency-free,
  UTF-8-guarded, fixture-tested (incl. the shipped EADOS roadmap), and wired into CI.
- **Explicit "CI live & green" bootstrap gate (#142, M11).** `generate.md` Step 8 now makes
  confirming CI is configured and green on the bootstrap PR an explicit gate that **opens
  per-milestone PR delivery** (against the seeded `MN — name` milestones); a red or not-yet-running
  CI is a hard stop. The Output report surfaces the precondition. Completes M11.
- **Verbose squash-body policy as data (#144, M11).** `os/git/git.yaml` `commit.squash_body`
  now requires the squash-merge commit (squash is the only method) to carry a verbose,
  professional body — subject = the Conventional-Commit one-liner, body = the PR description
  (context, change, verification) preserved on squash — never a one-line collapse. Documented in
  `AGENTS.md` §6 and the `git-workflow.md.tmpl` / `AGENTS.md.tmpl` renders; the PR templates
  already carry the Summary/Motivation/Changes/Verification sections that map into it.

### Changed

- **Assignee resolves to the owner, never `@me` (#141).** A blank manifest `assignee` now renders
  to `{{OWNER}}` (`render.py`), and the defaults/interview/placeholder hints recommend the owner —
  `@me` was wrong because it resolves to whichever actor (human or agent) runs `gh`.

### Fixed

- **`questionnaire.yaml` silently truncated by the hand-rolled loader (#153 discovery).** The
  loader does not fold multi-line double-quoted scalars or parse flow lists (`[…]`) spanning lines;
  the first such construct (`Q4.7`'s wrapped prompt) made it silently drop everything after —
  phases 4–5 were partly invisible to every machine consumer while `data-file-validity` still
  passed (the file "parsed"). All questionnaire prompts are now single-line and multi-line `ask`
  lists are block sequences (the loader-supported subset, same policy as `git.yaml` `scopes`), with
  a full-parse guard + an opportunistic PyYAML differential in `tests/test_spec_provenance.py`
  (executed with real PyYAML in the render-smoke CI job) so the truncation cannot silently return.

---

## [2.4.0] - 2026-06-28

### Changed

- **ADR-0009 addendum — profile action-pinning reaffirmed (#132).** A post-v2.3.0 re-audit re-flagged
  that `profiles/*.yaml` reference GitHub Actions by floating tag while the factory SHA-pins its own
  workflows; a dated addendum records this is the deliberate tiered policy of **ADR-0009 §3** (an
  apparent inconsistency surfaced on re-audit, not a design gap), with the two operating facts that
  reinforce it (Dependabot does not scan profiles; the factory maintains only the pins it itself
  uses). Documentation only — no renderer, gate, or behavior change.

### Fixed

- **Tooling no longer mojibakes or crashes on a non-UTF-8 console (Windows `cp1252`) (#128).** Every
  CLI tool now forces UTF-8 on `stdout`/`stderr` at `main()` entry, so non-ASCII output (the em-dash
  in status lines, `eados_lint`'s i18n-staleness `!=`, `→`/`✓` on failure paths) renders correctly
  instead of garbling — and the i18n-STALE path no longer raises `UnicodeEncodeError` on the
  development platform (CI on Linux/UTF-8 never surfaced it). New
  [`test_utf8_stdio.py`](.eados-core/tools/tests/test_utf8_stdio.py) proves it end-to-end (a tool run
  under a simulated ascii console) and statically asserts every CLI tool carries the guard. Surfaced
  by the post-v2.3.0 repository audit (milestone **M10**).
- **Documentation accuracy sweep (#130).** Post-v2.3.0 audit corrections: SECURITY.md's
  supported-versions note said "pre-`v1.0.0`" (the project is **v2.3.0**); a `USAGE.md` link in the
  zh-Hans + ja READMEs was repo-root-relative and 404'd from the translation's own directory; the
  `contribution` OS spec (M8) was missing from the
  [os/ spec index](.eados-core/orchestrator/os/README.md) and `AGENTS.md` §3; RFC-0001 §12 + the
  RFC index still described the roadmap as "M1 → M5" (now M1 → M9); and `templates/README.md`'s
  "What renders where" undercounted the rendered `.github/**` pack.
- **Defensive hardening of the tooling against latent edge cases (#131).** Fail-safe fixes for
  conditions that don't arise with shipped data but would otherwise crash or misfire on a
  hand-edited config or an exotic filesystem: `risk_score` requires the security gate (instead of
  raising) when a `risk.yaml` sets a `mandatory_gate_level` outside its `levels`; `cleanup_installer`
  matches the `setup/` leftover on entry *type*, not just name, so a subdir/symlink merely named
  like an installer file is never removed; `eados_lint`'s `gate-coverage` runs
  `git -c core.quotePath=false ls-files` so a non-ASCII filename can't spuriously fail it; the
  `doctor` / `eados` / `phase_runner` / `traceability` / `rfc_check` CLIs report a missing/invalid
  input path as a clean non-zero exit instead of a raw traceback (new `test_cli_guards.py`); and
  `git.yaml`'s commit `scopes` vocabulary is extended to the scopes actually in use. Found in the
  post-v2.3.0 audit (milestone **M10**).

### Security

- **Installer hardened against tar-slip via symlink/hardlink entries (#129).** `setup.sh` and
  `setup.ps1` inspected only entry *names* before extracting, so a bundle carrying a symlink whose
  target escapes the target root (then a file written through it) could write outside it. Both now
  refuse any symlink/hardlink entry in the archive (the EADOS bundle contains none) before
  extracting, and the guard runs even under `--no-verify`. Regression tests added to
  `test_setup_sh.py` / `test_setup_ps1.py`. Found in the post-v2.3.0 audit (milestone **M10**).

---

## [2.3.0] - 2026-06-28

### Added

- **M9 — guided cross-platform installer.** A newcomer installs EADOS into a repo by running a
  script and answering a few prompts, instead of hand-copying the USAGE §6 `curl`/`tar` snippets.
  Lives in a top-level **`setup/`** (outside `.eados-core/`, because it *delivers* it; `export-ignore`d
  from the bundle), one consistently-named script per platform:
  - [`setup/setup.sh`](setup/setup.sh) (POSIX) + a double-clickable macOS
    [`setup/setup.command`](setup/setup.command), and [`setup/setup.ps1`](setup/setup.ps1) (Windows
    PowerShell, 5.1/7-compatible, ASCII-only) + a [`setup/setup.bat`](setup/setup.bat) double-click
    shim. Each script is **scriptable via flags** (`--mode`/`--path`/`--repo-name`/`--ref`/`--from`/
    `--sha256`/`--sums-file`/…) **and interactive when run bare** (prompts for new-vs-existing repo,
    path, and name; shows the plan; confirms before writing).
  - It **downloads** the release bundle, **verifies its SHA256 fail-closed** (refuses to extract an
    unverified bundle unless `--no-verify`; checksum from the release `SHA256SUMS`, a `--sha256` pin,
    or a local `--sums-file`), and **extracts it additively** — refusing to overwrite any existing
    file (the [ADR-0007](.eados-core/docs/adr/0007-renderer-write-guards-and-validation-independence.md)
    no-clobber principle). On a **new** repo it `git init`s the target and (when `gh` is present)
    offers `gh repo create`.
  - The **release** ([`.github/workflows/release.yml`](.github/workflows/release.yml)) now attaches a
    **`SHA256SUMS`** over every asset (the installer's default integrity source) and the `setup.*`
    scripts themselves, so `releases/latest/download/setup.{sh,ps1}` (and `setup.command` /
    `setup.bat`) are stable links.
  - Gated by `setup/*` `gate-coverage` classes + `test_setup_sh.py` / `test_setup_ps1.py` (plan
    resolution, arg validation, fail-closed checksum incl. the published `SHA256SUMS` format,
    additive no-clobber, and the interactive new/existing flow — all offline via `--from`; the trivial
    `.bat` shim is allow-listed), **plus a CI static-analysis step**: `shellcheck` for `setup/*.sh` +
    `setup/*.command` and a dependency-free PowerShell parse-check for `setup/*.ps1`.
  - **Docs:** the README + [`USAGE.md`](.eados-core/docs/USAGE.md) §6 "Get it" gain the one-step
    installer path beside the manual `curl`/`tar` snippets (README i18n — zh-Hans + ja — refreshed in
    lockstep).
  - **Credit:** this milestone **re-implements and elevates [@AlexMnrs](https://github.com/AlexMnrs)'s
    closed PR #96** ("Add Windows PowerShell setup examples") — built in-house our way and
    **co-authored** to them, with thanks. With this, **M9 — guided cross-platform installer** is
    **complete**.

- **Carry-through release default.** The release boundary is now explicit policy: the agent always
  takes a release up to a **draft** — it creates + pushes the annotated tag and opens the GitHub
  Release as a draft (CI drafts it on tag-push in generated repos) — and the human only clicks
  **Publish** (`publish_by: human`; `delegation_flag: true` delegates the publish too). Encoded in
  `git.yaml`'s `release` (`tag_by` / `draft_release_by` / `publish_by`) + `git/_schema.md`, the
  `release-manager` role, both agent contracts (this repo's `AGENTS.md` + `templates/AGENTS.md.tmpl`),
  and the generated `release.md.tmpl` playbook — so every project EADOS builds inherits it.

- **Installer cleanup at `/eados init`.** A new
  [`tools/cleanup_installer.py`](.eados-core/tools/cleanup_installer.py) tidies the guided installer's
  leftovers from a repo root — the downloaded `setup.sh` / `setup.ps1` / `setup.bat` / `setup.command`
  (and a `setup/` dir only when it holds nothing but those). It removes **only** those known names —
  never `.eados-core/`, the agent contract, or your own files; symlinks are ignored; dry-run by
  default, `--apply` removes.
  [`/eados init`](.eados-core/orchestrator/commands/init.md) now runs it as a first-run housekeeping
  step, so however EADOS was installed the repo is left with just the factory (`.eados-core/` + the
  agent contract + `LICENSE`).

### Changed

- **README: standalone framing + license/owner + agent guidance.** The README (and its zh-Hans / ja
  translations) drop the internal seed-project origin story — EADOS now reads as a **standalone**
  enterprise factory (C++ remains a supported *language*); a new **License & ownership** section makes
  the **MIT © Daniel Polo** licensing and owner-governance explicit. Under *Prerequisites*, new agent
  guidance: which model does best today (**Claude Opus 4.8 high**; then **Codex 5.5**, **Gemini 3.5
  Flash**; **Mistral AI** / **Sakana AI** untested) and an **AI-can-hallucinate** caveat — review every
  diff/RFC/command; it is a power tool, most effective in expert hands. i18n source-hash refreshed.

- **README: comprehensive overhaul + new title + downloads badge.** Retitled to
  **`EADOS — Enterprise Agentic Delivery OS`** (brand-first, all languages) and restructured the README
  into a fuller, navigable doc for both newcomers and professionals: a **table of contents**,
  **Why EADOS** (incl. the vs-cookiecutter positioning), **Capabilities at a glance**, a
  **phase-pipeline** table (`init … refactor`), a **Security posture** section, and a **FAQ**; plus a
  **total-downloads** badge. zh-Hans + ja kept in lockstep; README i18n source-hash refreshed.

---

## [2.2.0] - 2026-06-28

### Added

- **M8 / 8.6 — dogfood + docs (M8 complete).**
  [ADR-0014](.eados-core/docs/adr/0014-inbound-contribution-trust-model.md) records the
  inbound-contribution trust model; USAGE gains a §7 **`/eados review` walkthrough** with EADOS's own
  **#94** episode as the worked example (the real evaluator output — `external-fork` touches an owned
  path → `needs-maintainer`, adopt via co-author, never merge the fork's commits); RFC-0001 §6 and the
  ADR index are kept in lockstep. With this, **M8 — inbound contribution review** is complete
  (8.1–8.6) — a v2.2.0 release follows.

- **M8 / 8.5 — `contribution-review` wired as a cross-cutting gate.** Registered the
  `contribution-review` gate in `workflow.yaml` (`required_for: []`, advisory/`blocking: false` —
  like `traceability-lint`, it is **not** a phase-transition gate), referenced from a new
  `git.yaml` `pr.review_gate` field (+ `git/_schema.md`), and extended `cross-spec-consistency` to
  resolve that reference (a typo'd review-gate id now fails the self-lint; `test_cross_spec.py`
  extended). **No change to the shipped phase pipeline.** The optional rendered CI template for
  generated repos is deferred — it would need a `pull_request_target` workflow, i.e. a deliberate
  `workflow-safety` allow-list entry.

- **M8 / 8.4 — `/eados review <PR#>` command surface.** New
  [`orchestrator/commands/review.md`](.eados-core/orchestrator/commands/review.md) + a
  `commands/README.md` row: runs `pr_review.py`, deepens with the `security-auditor` + `reviewer` on
  an owned-path touch or a REQUIRED risk score, **drafts** the review comment + `review:<disposition>`
  label via `gh`, and recommends a disposition. Cross-cutting like `/eados status` (not a phase
  transition). Drafts only — the human requests-changes / approves / merges / closes; a non-owner's
  commits are never merged (adopt via `re-implement-in-house`).

- **M8 / 8.3 — `tools/pr_review.py`, the inbound-PR evaluator.** Runs the `contribution-reviewer`
  procedure as a tool: classifies the author's trust tier, runs the contribution-policy
  `required_checks`, composes the **authority** (owned-path escalation) and **risk** (security/size/
  blast) lenses, and recommends a disposition — honoring the policy: **no auto-accept** and **never
  merge a non-owner's commits**, so a non-owner change is recommended for adoption via
  `re-implement-in-house` (its co-author/rationale/thank ritual), with `close-with-thanks` as the
  decline alternative, or `needs-maintainer` when an owned path / security gate is hit; it always
  thanks. Pure evaluator core (fixture-tested via `test_pr_review.py`) + a thin `gh` shell that
  degrades cleanly offline (the `derive_links.py` pattern). It reports and recommends — never merges
  or closes.

- **M8 / 8.2 — the `contribution-reviewer` role.** New portable persona
  `agent/contribution-reviewer.md` — the inbound-PR steward: composes `reviewer` + `security-auditor`,
  adds trust-tier classification + the contribution-policy checks + triage, and recommends a
  disposition (it judges the change, not the person; it never merges or closes). Plus an
  `authority.yaml` record (engineering pillar, `phases: []`, empty `owns`/`may_approve` like
  `reviewer`) and an `agent/README.md` registry row. Enforced by `agent-registry` +
  `authority-personas`. The role enforces the **full inbound-contribution protocol** the owner
  applies by hand (the #94 episode), now encoded in `contribution.yaml`: **we never merge a
  non-owner's commits** (`courtesy.merge_nonowner_commits: false`) — a good idea is **adopted via**
  `re-implement-in-house` (the B2 ritual: `reimplement-ourselves` + `co-author-credit` +
  `rationale-comment` on the contributor's PR + `thank-then-close`), declined via `close-with-thanks`,
  or escalated via `needs-maintainer`; plus a `courtesy` block (`always_thank`;
  `acceptance_requires_reasoning` — **never auto-accept**). Provenance stays 100% in-house. Schema +
  invariants updated to match.

- **M8 / 8.1 — inbound-contribution policy as data.** New OS spec
  `orchestrator/os/contribution/{_schema.md, contribution.yaml}`: the owner-identity source
  (CODEOWNERS + manifest fallback), the trust tiers (owner · collaborator · external-fork), the
  required inbound checks, the disposition + label vocabulary, and the load-bearing "external fork
  touches an owned path → escalate to a human" rule — encoding the maintainer's external-PR practice
  (the #94 episode) as one source of truth for the M8 reviewer + tooling. Auto-validated by
  `os-spec-completeness` + `data-file-validity` + `gate-coverage`; its escalation decider/disposition
  cross-references are resolved by `cross-spec-consistency` (+ `test_cross_spec.py`). First item of
  **M8 — inbound contribution review**.

- **Hardening — workflow-safety gate (contributor security surface).** New self-lint check
  (`eados_lint.py` #16): the sensitive CI triggers `pull_request_target` and `workflow_run` — which
  run with repository secrets on partially-untrusted events (the classic secret-exfiltration / self-
  merge vector) — are forbidden unless a workflow is allow-listed with a justification, both in this
  repo's `.github/workflows/` **and** in the workflow templates shipped to every generated repo
  (widest blast radius). The one legitimate `workflow_run` (`dependabot-pin-sync.yml`, ADR-0013) is
  allow-listed. Complements `action-pins` (SHA pinning) by guarding the trigger surface.
  `tests/test_workflow_safety.py` + CI registration.
- **Hardening — gate-coverage meta-gate + a data-file floor (contributor safety).** Two new
  self-lint checks make it structurally impossible for a factory file to ship ungated — the class of
  gap the #90/#94 episode exposed. **`data-file-validity`** (`eados_lint.py` #14) parses every
  `.eados-core/**/*.yaml`, closing the previously-unchecked `questionnaire.yaml` and
  `config/defaults.yaml`. **`gate-coverage`** (#15) asserts every tracked file is either covered by a
  named gate or consciously allow-listed as reviewed prose (with a reason), and **fails CI if a new
  file class slips in ungated** (it also flags stale registry patterns). `tests/test_gate_coverage.py`
  + CI registration.
- **M7 / 7.3 — `project.yaml` documented field-by-field + a guard for it (#90).** The manifest
  template (`orchestrator/project.yaml.template`) now carries a concise, self-documenting comment on
  every field (purpose + example + `-> {{PLACEHOLDER}}`), so a manifest can be hand-filled without
  reverse-engineering `reference.yaml` (the values are unchanged — render output is byte-identical).
  A new **`manifest-template`** self-lint check (`eados_lint.py` #13 +
  `tests/test_manifest_template.py`) keeps that file valid YAML, structurally complete, and free of
  dangling `-> {{…}}` annotations — closing a gap where this consumer-facing file was gated by
  nothing. Co-authored with @gxuxhxm, whose PR #94 prompted the field docs.
- **M7 / 7.5 — `rfc_check` scope documented (#91).** A new **Scope** section in
  [`orchestrator/os/rfc/review-protocol.md`](.eados-core/orchestrator/os/rfc/review-protocol.md)
  (and the `rfc_check.py` header) states that the `rfc-approved` gate targets *generated-project*
  RFCs following `os/rfc/template.md`; EADOS's own `docs/rfc/0001-eados-delivery-os.md` is a
  meta-design RFC and intentionally out of scope, so its FAIL is by design — not a defect.
  Docs/docstring only; no tool-behavior change (an M7 invariant).
- **M7 / 7.4 — end-to-end phase walkthrough (#87).** New
  [`.eados-core/docs/walkthrough.md`](.eados-core/docs/walkthrough.md): a follow-along run of the
  whole pipeline (`init → design → plan → scaffold → audit → refactor`) against a tiny worked
  example — every command shown actually runs, with the real console output, the human gate at each
  step, and how `delivery_state.phase` evolves. Linked from the README "New here?" note (with the
  i18n translations refreshed) and from USAGE §3.
- **M7 / 7.2 — Windows/PowerShell install & render variants (#88).** README's "Get it" and USAGE
  §3/§6 now show a **PowerShell** equivalent beside each Unix snippet — download via
  `Invoke-WebRequest`, extract with the Windows-bundled `tar`, `$env:TEMP` instead of `/tmp`, and
  `Copy-Item` for the manifest copy — so a Windows user reaches `<repo>/.eados-core/` without
  translating commands. The zh-Hans + ja READMEs get the PowerShell variant too (i18n-freshness
  refreshed). Docs only — no behavior change.
- **M7 / 7.1 — Prerequisites: getting an AI coding agent (#89).** README's "Getting started" gains a
  **Prerequisites — getting an AI coding agent** subsection: install links for Claude Code, Gemini
  Antigravity, and ChatGPT Codex, one line on what "open the folder" does (the agent auto-loads
  `AGENTS.md`), and an explicit no-agent fallback to the deterministic path; USAGE §3 routes the same.
  The zh-Hans + ja README translations are refreshed to match (i18n-freshness stays green). Docs only
  — no behavior change.

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [2.1.0] - 2026-06-27

**M6 — hardening & UX.** The post-v2.0.0 hardening milestone: the automation/completeness gaps
(G2–G4) and feature suggestions (F1–F4) surfaced by the v2.0.0 enterprise review, plus the deferred
cross-spec scope (#72). All opt-in and behind the unchanged pipeline — a MINOR release, no breaking
changes. Highlights: a thin executable phase orchestrator (`eados.py`), the `/eados status` doctor,
single-artifact render for `refactor`, an end-to-end phase smoke, risk-model weights as data,
auto-derived traceability links, hands-off Dependabot action-pin sync, and two new dogfooded gates
(`version-lockstep`, cross-cutting `cross-spec-consistency`).

### Added

- **M6 / 6.8 — cross-spec gate extended to cross-cutting gates (#72).** `traceability-lint` (the
  `git`-spec CI gate, not a phase-transition gate) is now registered in `workflow.yaml`'s gate list
  (cross-cutting, `required_for: []`), and `eados_lint`'s `cross-spec-consistency` validates
  `git.yaml`'s `traceability.gate` against that registry — so a typo'd cross-cutting gate id is
  caught too (the scope deferred from #62). `test_cross_spec.py` covers the resolve + typo cases.
  **Completes M6.** No pipeline behavior change.
- **M6 / 6.7 — version-lockstep dogfooding (F4, #69).** EADOS now dogfoods the `version-lockstep`
  gate it ships to generated repos: a new `eados_lint` check asserts every README release badge
  (EN + `docs/i18n/*`) and the CHANGELOG's "the latest is **vX.Y.Z**" prose match the CHANGELOG's
  latest released `## [X.Y.Z]` heading — so a release bump must move all of them in lockstep or the
  self-lint fails. Pure `version_lockstep_problems()`; covered by
  `tools/tests/test_version_lockstep.py`. No pipeline behavior change.
- **M6 / 6.6 — auto-derive traceability links from PR bodies (F2, #67).** A new
  `tools/derive_links.py` builds the `{pr, rfc, milestone, commit, release}` traceability edges from
  merged PRs — `pr`/`commit`/`milestone` from `gh` metadata, `rfc` parsed from the body, `release`
  from a release PR's title — and emits a `links.yaml` that `traceability.py --links` consumes, so
  the graph runs on real data instead of a hand-maintained file. By default it emits only delivery
  PRs (those with an rfc or milestone); `--all` emits every PR. The parser is pure and tested
  **gh-free**; the optional fetch degrades cleanly (clear message, exit 2) when `gh` is absent,
  unauthenticated, or offline — CI never depends on the network. Covered by
  `tools/tests/test_derive_links.py`. No pipeline behavior change.
- **M6 / 6.5 — thin CLI phase orchestrator (G3, #64).** A new `tools/eados.py <phase> <manifest>`
  runs a phase's **deterministic outgoing gates** — read from `workflow.yaml` (no hardcoded chain) —
  evaluating the ones it can (`manifest-valid`, `rfc-approved`, `roadmap-covers-rfcs`) via the
  sibling tools and marking render-time / human gates `[manual]`, then prints the legal next
  transitions and points at the procedure; `eados.py status` delegates to the doctor (6.4). It is
  the executable spine beneath the markdown `/eados <phase>` procedures — it reports and gates,
  never authoring or advancing state. Covered by `tools/tests/test_eados.py`. No pipeline behavior
  change.
- **M6 / 6.4 — `/eados status` doctor (F1, #66).** A new read-only `tools/doctor.py` (the
  `/eados status` surface, `commands/status.md`) reports a project's delivery health at a glance:
  current phase (+ its owning role and what it produces), the legal next transitions (+ gates and
  human-gating, via `phase_runner`), the recorded `rfcs`/`milestones` refs, and traceability
  coverage (`roadmap-covers-rfcs`, plus `traceability-lint` when a links file is present, via
  `traceability`). It composes the existing tools — never re-implements — and exits non-zero on an
  actionable problem (undeclared phase, uncovered RFC, dangling edge), doubling as a pre-flight
  check. Covered by `tools/tests/test_doctor.py`. Read-only; no pipeline behavior change.
- **M6 / 6.3 — single-artifact render for the `refactor` phase (G2, #63).** A new
  `tools/render_artifact.py` renders **one** template with the manifest context — reusing
  `render.py`'s engine and the `validate_manifest` + unresolved-placeholder gates, so a single
  artifact is byte-identical to its whole-render twin — and writes it into a target repo through
  `tools/sandbox.py` (`safe_write`: contained, never `.git`, additive). It performs the "render the
  missing artifact → sandbox" step `commands/refactor.md` describes (now invoked there instead of
  done by hand). Covered by `tools/tests/test_render_artifact.py`. Factory tooling; no pipeline
  behavior change.
- **CI — Dependabot pin-sync now auto-re-triggers via a GitHub App (ADR-0013 addendum).** The
  `dependabot-pin-sync` workflow mints a short-lived App token (`actions/create-github-app-token`,
  SHA-pinned) when `SYNC_APP_ID` + `SYNC_APP_PRIVATE_KEY` are set and pushes the pin re-sync with it,
  so CI re-triggers and the failed `action-pins` check goes **green by itself**; absent the App
  secrets it falls back to `GITHUB_TOKEN` (the fix still lands, check re-runs on the next event). The
  setup guide is rewritten App-first; `DEPENDABOT_SYNC_TOKEN` is now the swap-in PAT fallback, not the
  default. Factory-only; no pipeline behavior change.
- **M6 / 6.1 — end-to-end phase-flow smoke (G4, #65).** A new `tools/tests/test_phase_smoke.py`
  threads one coherent fixture project (manifest + RFC + ROADMAP + links) through `design → plan →
  audit` by invoking the real phase tool CLIs (`rfc_check`, `traceability`, `risk_score`,
  `phase_runner`) the way an agent runs a phase. It asserts each gate **passes** on the good
  fixture and **fails** on a deliberately broken one, that `phase_runner --propose` reports every
  transition declared in `workflow.yaml` LEGAL (and rejects an undeclared one), and that each entry
  gate's backing tool exists on disk — catching tool-integration (seam) bugs the per-tool unit
  tests cannot. Wired into the CI self-lint job. No pipeline behavior change.
- **M6 / 6.2 — risk-model weights as data (F3, #68).** The factor weights (security surface, size,
  blast radius), the `blast_radius_threshold`, and the points→level cutoffs move out of
  `risk_score.py` into `risk.yaml` as data — each **per-domain overridable** (weights shallow-merged),
  exactly as `mandatory_gate_level` already was (OQ2). The scorer reads them via a new
  `resolve(cfg, domain)` with built-in fallbacks, so a pre-6.2 `risk.yaml` still scores identically
  (back-compat) and the shipped default scores are unchanged. `risk/_schema.md` documents the new
  keys; covered by the expanded `test_risk_score.py`. Knowledge as data — no special-casing in code.
- **M6 / 6.9 — auto-sync shared action pins into the rendered templates (#76).** A new
  `tools/sync_action_pins.py` (`--check` / `--fix`) rewrites the workflow templates'
  (`templates/.github/workflows/*.tmpl`) action pins to the factory CI's pin for each shared action
  — reusing `eados_lint`'s pin regex so the fixer and the `action-pins` gate can never disagree. A
  weekly Dependabot `github-actions` bump now needs **no manual template edit** to pass the lockstep
  gate. The new `dependabot-pin-sync` workflow (`workflow_run`, **not** `pull_request_target`;
  ADR-0013) applies the fix automatically on a Dependabot PR — true zero-touch — gated to genuine
  in-repo Dependabot PRs; the same `--fix` is the manual/local fallback (stay-current routine).
  Deterministic and dependency-free; covered by `tools/tests/test_sync_action_pins.py`. Factory-only
  (generated repos render no templates). No pipeline behavior change.
- **Docs — `DEPENDABOT_SYNC_TOKEN` setup guide.** `maintenance/dependabot-sync-token.md` documents
  the optional token for *green-by-itself* Dependabot pin auto-sync (ADR-0013): fine-grained PAT
  (drop-in) vs GitHub App (robust, with the workflow snippet), least-privilege (Contents-write only),
  storage via `gh secret set`, verification, and rotation. Linked from the stay-current routine.
  Maintainer-facing; no behavior change.

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [2.0.0] - 2026-06-23

The EAAO → EADOS pivot: the language-agnostic factory becomes a phase-based **delivery operating
system** (`init → design → plan → scaffold → audit → refactor`), with the classic factory as the
`scaffold` phase. A breaking, consumer-visible release (repository, factory folder, bundle, and
command surface all renamed) — hence the MAJOR bump.

### Added

- **ADR-0011 — phase-based delivery operating system.** Records the owner-confirmed direction to
  evolve the factory into EADOS: an opt-in phase pipeline (`init → design → plan → scaffold →
  audit → refactor`) over the unchanged data-driven core, resident as a capability under each
  generated repo's own `AGENTS.md`. The detailed design lands in RFC-0001.
- **RFC-0001 + the machine-readable OS specs (the design package).** The full design for the
  delivery-OS pivot: [`docs/rfc/0001-eados-delivery-os.md`](.eados-core/docs/rfc/0001-eados-delivery-os.md)
  (phase state machine, role/authority model, ownership map, traceability graph, the enterprise
  lens, and the roadmap M1–M5), plus the three **schema-first** specs under
  `orchestrator/os/{workflow,authority,git}/` (each `_schema.md` + reference instance), validated
  by a new `os-spec-completeness` gate in `eados_lint.py`. Diagrams are Mermaid (code) under
  `docs/rfc/assets/`. No runtime behavior changes yet — this is design only; build starts at M1.
- **`docs/rfc/ROADMAP.md` — the delivery plan as a single source of truth.** The M1–M5 roadmap is
  now a living, checkbox-driven file; RFC-0001 §12 points to it instead of duplicating the table.
  Adds the `/eados <phase>` command surface to each milestone's deliverables.
- **M1-A — the domain/target axis (roadmap 1.1–1.2).** A second axis of genericity parallel to the
  language profiles: `orchestrator/domains/` with `_schema.md`, `_template.yaml`, a `README.md`,
  and the seeds `software` / `game` / `mobile` (each declaring its roles, artifacts — PRD vs GDD,
  NFR hard-budget axes — RAM/GPU/framerate for `game`, milestone vocabulary — SemVer vs
  Alpha/Beta/RC, cross-discipline deps, and workflow overlay). Validated by a new
  `domain-completeness` gate in `eados_lint.py`. Data only — no rendering or interview change yet
  (that is M1-C).
- **M1-B — persistent, reference-based manifest (roadmap 1.4, resolves OQ1).** The manifest skeleton
  gains an optional top-level `schema_version` and a `delivery_state` block (current `phase`,
  `checkpoints`, and cross-link `refs` — ids, not content; Git stays the source of truth). The
  renderer now accepts both (a known scalar + a known section) and **ignores them when rendering**,
  so a legacy manifest without the block renders unchanged. A new guard test covers the accepted
  shape. Schema versioning is embedded (`schema_version`); migrations are CHANGELOG notes, no
  separate ledger.
- **M1-C — the interview selects the development target (roadmap 1.3).** A new Phase-0 question
  `Q0.4 — development target` (`software` / `game` / `mobile`, default `software`) loads the
  matching `domains/<domain>.yaml` and records it as a top-level `domain` field in the manifest;
  the renderer accepts it as a known scalar. Added to `interview.md` and `questionnaire.yaml`
  (with a `domain_profile_exists` validation, mirroring the language `profile_exists` rule). The
  domain still informs only itself for now — the roles/artifacts/NFRs it selects are consumed by
  the `design`/`plan` phases in M2+.
- **M1-D — persona↔authority wiring (roadmap 1.5).** Makes the persona≠authority separation
  enforceable. `authority.yaml` gains the `profile-author` role (so every existing persona has an
  authority record) and a `pending_personas` list (`product-manager`, `tech-lead`, `producer` —
  their personas land in M2). A new `authority-personas` gate in `eados_lint.py` enforces the
  bidirectional pairing: every role has a persona **or** is pending, every persona maps to a role,
  and a pending role must not already have a persona. `agent/README.md` documents the split.
- **M1-E — `/eados init` command surface + the deterministic phase runner (roadmap 1.6, closes M1).**
  A portable command surface under `orchestrator/commands/` (`README.md` + `init.md`) and
  `tools/phase_runner.py` — a state-driven, dependency-free checker that reads a manifest's
  `delivery_state.phase` + `workflow.yaml` and prints the legal next transitions (with their gates
  and human-gating). It **reports; it never advances state**. Covered by
  `tools/tests/test_phase_runner.py` (legal transitions, the terminal phase, and workflow
  integrity), wired into CI. **Milestone 1 (foundation) is complete.**
- **M2-A — Product/Delivery personas + the domain-overlay pattern (roadmap 2.1, resolves OQ4).**
  Adds the personas `agent/{product-manager,tech-lead,producer}.md` and the domain-overlay
  convention `agent/domains/<domain>/<role>.md` (shipping the `game` overlay — the Game Designer).
  A domain specializes a role's *persona* without forking its *authority*: `pending_personas` is now
  empty, `product-manager` owns the product spec under either name (`docs/prd/**` + `docs/gdd/**`),
  and the `agent-registry` + `authority-personas` lints resolve overlays recursively. OQ4 resolved —
  one authority role + a domain persona overlay, not two role IDs.
- **M2-B — RFC review protocol + the `rfc-approved` gate (roadmap 2.2).** A new `rfc` OS spec under
  `orchestrator/os/rfc/` (`_schema.md` + `rfc.yaml` config + `template.md` + `review-protocol.md`)
  defines the author→reviewer→approver flow and the required RFC sections. `tools/rfc_check.py`
  enforces the gate mechanically — an RFC must have every required section and a well-formed approval
  record by the approver role (the human approves; the tool verifies the record). The `workflow.yaml`
  `rfc-approved` gate now runs `rfc_check`, and RFC-0001 carries an `## Approval` block (dogfooding).
  Covered by `tools/tests/test_rfc_check.py`, wired into CI.
- **M2-C — the workflow checker validates a proposed transition (roadmap 2.3).** `phase_runner.py`
  gains `--propose <to>`: it checks whether `current_phase → to` is a declared, legal transition,
  reports its gates and human-gating, and **emits the `delivery_state` checkpoint** to write — it
  does *not* write state (the agent writes it; the human confirms human-gated moves). New cases in
  `tools/tests/test_phase_runner.py` cover legal/illegal proposals and the emitted checkpoint.
- **M2-D — the authority gate enforces the ownership map (roadmap 2.4).** New
  `tools/authority_check.py <role> <paths>`: given the acting role and the paths a change touches, it
  rejects any path outside the role's writable surface (`owns` ∪ `may_draft`) per `authority.yaml`.
  Agent-invoked — CI cannot know a PR's acting role — with a `**`/`*`/exact glob matcher. Covered by
  `tools/tests/test_authority_check.py` (in-authority vs denied, glob edge cases, unknown role),
  wired into CI.
- **M2-E — `/eados design` command surface (roadmap 2.5, closes M2).** A portable procedure
  (`orchestrator/commands/design.md`) composing the M2 tooling into the design phase:
  `authority_check` (the author may write `docs/rfc/`) → author the RFC from the template → review
  → approval → `rfc_check` (the `rfc-approved` gate) → record the RFC in `delivery_state.refs.rfcs`
  → `phase_runner --propose plan` (the agent writes the checkpoint; the human confirms). The command
  surface README marks `/eados design` available. **Milestone 2 (the design phase) is complete.**
- **M3-A — traceability graph + the `roadmap-covers-rfcs` gate (roadmap 3.3–3.4).** New
  `tools/traceability.py <roadmap> <RFC-ids>` builds the design-time `RFC → milestone` edges from a
  roadmap and enforces that **every RFC is addressed by at least one milestone** (the
  `plan → scaffold` gate; generalizes the spec-coverage-map). The Git-side edges
  (`PR → commit → release`) land in M4. The `workflow.yaml` `roadmap-covers-rfcs` gate now runs it.
  Covered by `tools/tests/test_traceability.py`, wired into CI.
- **M3-B — the roadmap-negotiation protocol (roadmap 3.1).** A new `plan` OS spec under
  `orchestrator/os/plan/` (`_schema.md` + `plan.yaml` config + `negotiation-protocol.md`) makes the
  roadmap a collaborative artifact: `product-manager` proposes priorities → `tech-lead` gives the
  T-shirt sizing → `producer` reconciles capacity into milestones, every step anchored to a concrete
  artifact (no theatre). Validated by `os-spec-completeness`; the output is gated by the M3-A
  `roadmap-covers-rfcs` check.
- **M3-C — `/eados plan` command surface (roadmap 3.2, closes M3).** A portable procedure
  (`orchestrator/commands/plan.md`) composing the plan phase: negotiate via `plan.yaml`
  (`product-manager` → `tech-lead` → `producer`) → `authority_check producer ROADMAP.md` →
  write/update `ROADMAP.md` → `traceability.py` (`roadmap-covers-rfcs`) → record milestone ids in
  `delivery_state.refs.milestones` → `phase_runner --propose scaffold` (the agent writes the
  checkpoint; the human confirms). The command surface README marks `/eados plan` available.
  **Milestone 3 (the plan phase + traceability) is complete.**
- **M4-A — the audit risk model (roadmap 4.1, resolves OQ2).** A new `risk` OS spec
  (`orchestrator/os/risk/_schema.md` + `risk.yaml`) and `tools/risk_score.py`: a change's risk is a
  deterministic f(security surface × change size × blast radius) → `low/medium/high/critical`. At or
  above a `mandatory_gate_level` (default `high`, **per-domain configurable** — `mobile` is stricter
  at `medium`) the `security-auditor` gate is required. Generalizes the `reviewer` + `security-auditor`
  roles into a standing audit. Covered by `tools/tests/test_risk_score.py`, wired into CI.
- **M4-B — the `traceability-lint` gate (roadmap 4.3).** `tools/traceability.py` gains `--links`:
  given the Git-side cross-link edges (`{pr, rfc, milestone, commit, release}` records, from the
  `git` spec), it extends the graph to `milestone → PR → commit → release` and fails on a **dangling
  edge** — an RFC with no PR, a PR missing its RFC/milestone, or a release not tracing to a PR +
  commit. The M3-A coverage mode is unchanged (backward compatible). New cases in
  `tools/tests/test_traceability.py`.
- **M4-C — `/eados audit` command surface (roadmap 4.2, closes M4).** A portable procedure
  (`orchestrator/commands/audit.md`) composing the audit phase: `traceability.py --links` (no
  dangling edge) + `risk_score.py` (the per-domain mandatory-gate decision) → when REQUIRED, the
  `security-auditor` runs the deep audit and the `reviewer` returns structured findings → emit a
  **risk register** (score + traceability status + findings with severity/impact/mitigation) →
  propose the human-gated `audit → refactor`. Assessment-only; the human publishes any advisory. The
  command surface README marks `/eados audit` available. **Milestone 4 (audit + risk) is complete.**
- **M5-A — the brownfield reader (roadmap 5.1).** New `tools/brownfield.py` (**read-only**): it
  ingests an existing repository and maps it against the EADOS standard (agent contract, README,
  CHANGELOG, LICENSE, SECURITY, ADRs, spec, CI, source tree — with naming-variant tolerance) and
  reports the **gaps** a migration would close. It **never writes** — ingestion is safe; the
  migration planner (5.2) and its write-contained sandbox (5.3) are separate, later slices. Covered
  by `tools/tests/test_brownfield.py` (the standard map, the gaps, and a read-only assertion), wired
  into CI.
- **M5-B — the migration planner (roadmap 5.2).** New `tools/migration_planner.py` (**read-only**):
  from the brownfield gaps it produces an **ordered plan** of incremental migration steps — one
  logical change each (one PR), lowest-risk / most-foundational first (governance docs before CI
  before the source tree). It proposes; it does not write — edits happen one gated PR at a time in
  the refactor sandbox (M5-C). Covered by `tools/tests/test_migration_planner.py` (ordering,
  one-step-per-gap, read-only), wired into CI.
- **M5-C — the write-contained sandbox (roadmap 5.3).** New `tools/sandbox.py` — the mechanical
  backstop for the only phase that edits real user code. `safe_write(root, rel, content)` lands a
  write **only inside the target repo**: traversal is refused (realpath + commonpath, so a symlink
  pointing outside is caught), absolute/drive-qualified paths are refused, `.git/` is off-limits,
  and it is **additive by default** (no clobbering a file without explicit `overwrite=True`). Builds
  on the renderer's ADR-0007 write guard. Covered by `tools/tests/test_sandbox.py` — strong negative
  tests (traversal, absolute, `.git`, clobber, symlink-escape), wired into CI.
- **M5-D — `/eados refactor` command surface (roadmap 5.4, closes M5 and the delivery OS).** A
  portable procedure (`orchestrator/commands/refactor.md`) composing the brownfield phase: read
  (`brownfield.py`) → plan (`migration_planner.py`) → migrate **one step = one PR** (authority_check
  → render from the templates → `sandbox.safe_write` → `risk_score` / `/eados audit` → draft the
  gated PR → re-read to confirm the gap closed). Every write is sandboxed, additive, and
  human-merged; `refactor` is the terminal phase. The command surface README marks `/eados refactor`
  available. **Milestone 5 (brownfield refactor) is complete — the full pipeline `init → design →
  plan → scaffold → audit → refactor` is built.**
- **`cross-spec-consistency` gate — referential integrity across the OS specs (#62).** A new
  `eados_lint` check (#11) validates the cross-references *between* the delivery-OS specs, not just
  each spec's own keys: a role named in `workflow`/`plan`/`rfc`/a domain must exist in `authority`;
  a gate named in a workflow transition / `plan` / `rfc` must exist in the workflow gate registry
  (including overlay-defined `add_gates`); transition `from`/`to` and `required_for` states must
  exist; a domain's `workflow_overlay` must exist; risk levels and per-domain overrides must
  resolve. This stops the OS from silently fragmenting as the specs evolve. The logic is a pure
  `cross_spec_problems()` (unit-tested with `tools/tests/test_cross_spec.py`), wired into CI. The
  git spec's cross-cutting `traceability-lint` gate is intentionally outside this phase-gate
  registry check (deferred to M6).

### Changed

- **BREAKING — the project is renamed EAAO → EADOS** (*Enterprise Agentic Architecture
  Orchestrator* → **Enterprise Agentic Delivery Operating System**; ADR-0012). The factory folder
  `.eaao-core/` is now `.eados-core/`, the self-lint is `tools/eados_lint.py`, the dev sentinel is
  `.eados-dev`, and the distribution bundle is `pgs-eados-bundle.*`. Consumers who vendored the
  bundle must update their `.eados-core/` path and re-download from the new asset name. The GitHub
  repository is renamed `pgs-eaao` → `pgs-eados` (old URLs auto-redirect). Under SemVer this is a
  breaking, consumer-visible change — the next release should bump accordingly.
- **Roadmap cross-cutting section reframed as invariants (not checkboxes).** The English-on-disk /
  agent-drafts-human-merges / Conventional-Commits / one-PR-at-a-time / schema-validated-&-lint-gated
  / docs-in-sync rules are continuous **invariants** (upheld across M1–M5, binding on future work),
  now presented as such rather than as completable tasks. No behavior change — `docs/rfc/ROADMAP.md`
  only.
- **README + `AGENTS.md` reframed as a delivery operating system, not just a factory.** The
  front-door prose now positions EADOS as the phase pipeline (`init → design → plan → scaffold →
  audit → refactor`), with the **`scaffold` phase = the classic factory** (unchanged, opt-in).
  `AGENTS.md` §3 and the README opening updated. The `zh-Hans` / `ja` translations were re-translated
  to match (including the product name → "Delivery Operating System", which the rename had left as
  "Architecture Orchestrator"), and their `i18n-freshness` hashes refreshed. No behavior change.
- **OQ3 resolved — Mermaid-only (the last open question).** The RFC diagrams stay Mermaid
  (GitHub-rendered; the `.mmd` sources are committed); **no CI Node toolchain** is added to this
  Python-only repo, and SVGs remain on-demand via `mmdc`. RFC §13 and the roadmap OQ table updated.
  With OQ1 / OQ2 / OQ3 / OQ4 all resolved, **no open questions remain**.

### Deprecated

### Removed

### Fixed

- **B1 — traceability coverage matched RFC ids by raw substring (#60).** `roadmap-covers-rfcs`
  tested `rfc_id in body`, so a milestone citing a longer id (`RFC-00021`) falsely "covered" a
  shorter one (`RFC-0002`) and the gate could pass when it should fail. Now matched on a word
  boundary; regression test added.

### Security

- **B2 — the refactor sandbox rejected `.git` only at the top level (#61).** `safe_write` checked
  only the first path segment, so a nested or submodule `.git/` (e.g. `vendor/lib/.git/config`)
  could be written into — corrupting VCS metadata, the very thing the guard exists to prevent. Now
  `.git` is refused at **any** depth (a `.gitignore` file or a `foo.git/` directory is still
  allowed); the negative tests were extended.

---

## [1.2.1] - 2026-06-21

### Fixed

- **Generated projects carry their own owner, not EADOS's.** The renderer copied EADOS's root
  `LICENSE` verbatim into every generated repo (`Copyright (c) 2026 Daniel Polo`) even though the
  README rendered the maintainer's `{{AUTHOR}}`. A new `templates/LICENSE.tmpl`
  (`Copyright (c) {{YEAR}} {{AUTHOR}}`) is rendered into the generated `LICENSE` instead; EADOS's
  own `LICENSE` is untouched. The interview no longer defaults the reverse-domain group path to
  the reference's `it/d4np` — it asks the maintainer's own.

---

## [1.2.0] - 2026-06-21

### Added

- **In-place generation** — `render.py --in-place` writes the generated project into the folder
  that holds `.eados-core/` (the bundle copied into your own repo, `<repo>/.eados-core/`), so the
  project files land in `<repo>/` next to it. The rendered `.gitignore` excludes `.eados-core/`,
  and a root `.eados-dev` sentinel keeps the factory's own dev repo safe; `--out <dir>` still
  renders a separate copy.
- **Full roadmap up front** — the interview now elicits *all* milestones at generation, and
  `ROADMAP.md` + the README milestone table render every one. New `spec.milestones`
  (`number`/`title`/`goal`/`items`) plus a nested `{{#ITEMS}}` loop in the renderer.
- **Releases auto-attach the factory bundle** — a `release.yml` workflow uploads the version-less
  `pgs-eados-bundle.tar.gz` / `.zip` on every published release.

### Changed

- **The distribution bundle is prefix-less** — `git archive` no longer wraps the bundle in a
  `pgs-eados/` folder, so extracting it at the root of your project repo drops `.eados-core/` there
  directly (not in a subfolder).
- README getting-started reworked consumer-first (download the bundle, no clone), and the
  copy-paste commands fixed to their `.eados-core/` paths.

---

## [1.1.0] - 2026-06-20

### Added

- **Distribution bundle** — a `.gitattributes` `export-ignore` ruleset so `git archive` emits a
  clean, factory-only consumer bundle (the factory + the `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`
  contract + `LICENSE`), stripping this repository's own governance and plumbing. Adds an
  `.eados-core/README.md` entry-point how-to and a "Distribution bundle" section in
  `.eados-core/docs/USAGE.md`.

### Changed

- Consolidated all factory machinery under `.eados-core/`: the documentation i18n set moved from
  the repo-root `docs/i18n/` to `.eados-core/docs/i18n/`, with the `i18n-freshness` gate and every
  reference updated to match.
- `AGENTS.md`'s links to EADOS's own `CONTRIBUTING.md` and CI workflow are now absolute (canonical
  repo URLs) so they resolve from a distributed bundle.

---

## [1.0.0] - 2026-06-19

First public release. EADOS is a language-agnostic factory that interviews a maintainer,
records the answers in a single manifest, and renders a fully governed, enterprise-grade
repository from parameterized templates — for any of 19 language toolchains.

### Added

- **The factory** — the interview → resolve-profile → manifest → render → verify pipeline:
  a deterministic Mustache-subset renderer (`render.py`), a factory self-lint (`eados_lint.py`),
  19 seed language profiles, the parameterized enterprise templates, and the agent-runnable
  consistency lint shipped into every generated repository. Decisions recorded as ADRs
  (0001–0010).
- Self-governance artifacts so the factory meets the bar it imposes downstream:
  `SECURITY.md` (vulnerability policy + private reporting), `CHANGELOG.md`, a
  `.github/` pull-request template, issue forms (`bug_report`, `feature_request`, `config`),
  and `CODEOWNERS`.
- README status badges (CI, MIT, Python 3.12+, 19 language profiles, Conventional Commits).
- Documentation i18n: full `zh-Hans` + `ja` README translations under `docs/i18n/`, a
  `translation-status.md` freshness manifest, a glossary, and an enforced `i18n-freshness`
  check in `eados_lint.py`.
- `CONTRIBUTING.md` and the owner-governed contribution model in `AGENTS.md` §6:
  contributors suggest via PRs, the owner decides and squash-merges, `main` is protected.
- ADR-0010 — content-hash i18n freshness (squash-merge-proof).
- `.portfolio.json` — pinned title/tags/order + trilingual description for the portfolio card.

### Changed

- Repository merge policy set to **squash-only** (merge-commit and rebase disabled), with
  delete-branch-on-merge.
- `i18n-freshness` pins translations to the English source's **SHA-256 content hash** instead
  of a commit SHA, and no longer needs git history (`fetch-depth: 0` dropped from CI).

### Fixed

- `i18n-freshness` no longer falsely reports translations stale after a squash-merge orphans
  the recorded source commit (it broke `main` CI right after the squash-only policy landed) —
  see ADR-0010.

---

## Released versions

| Version | Date | Notes |
|---------|------|-------|
| [1.0.0](https://github.com/danielPoloWork/pgs-eados/releases/tag/v1.0.0) | 2026-06-19 | First public release |
