# Changelog

All notable changes to `pgs-eados` (EADOS) are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/).

Every PR that introduces a user- or maintainer-visible change adds a line to `[Unreleased]`
in the same PR. Releases follow Semantic Versioning; the latest is **v1.2.1**.

## [Unreleased]

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

### Changed

- **BREAKING — the project is renamed EAAO → EADOS** (*Enterprise Agentic Architecture
  Orchestrator* → **Enterprise Agentic Delivery Operating System**; ADR-0012). The factory folder
  `.eaao-core/` is now `.eados-core/`, the self-lint is `tools/eados_lint.py`, the dev sentinel is
  `.eados-dev`, and the distribution bundle is `pgs-eados-bundle.*`. Consumers who vendored the
  bundle must update their `.eados-core/` path and re-download from the new asset name. The GitHub
  repository is renamed `pgs-eaao` → `pgs-eados` (old URLs auto-redirect). Under SemVer this is a
  breaking, consumer-visible change — the next release should bump accordingly.

### Deprecated

### Removed

### Fixed

### Security

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
