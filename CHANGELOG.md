# Changelog

All notable changes to `pgs-eados` (EADOS) are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/).

Every PR that introduces a user- or maintainer-visible change adds a line to `[Unreleased]`
in the same PR. Releases follow Semantic Versioning; the latest is **v2.1.0**.

## [Unreleased]

### Added

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
