# Roadmap — EADOS

The **single source of truth** for EADOS's own delivery plan, from start to finish.
[RFC-0001](0001-eados-delivery-os.md) ratifies the design and points here for the schedule.

- **Living & checkbox-driven.** When an item completes in a PR, flip its checkbox
  (`- [ ]` → `- [x]`) **in the same PR**. New work goes at the bottom of its milestone with a
  fresh `<milestone>.<task>` number; never renumber.
- **Versioning:** pre-1.0, milestone-driven (`AGENTS.md` §6).
- **Invariant:** the factory keeps working unchanged throughout; every phase is opt-in, so a
  user who only wants `scaffold` (today's generation) sees no behavior change.
- **Foundation:** [RFC-0001](0001-eados-delivery-os.md) + the machine-readable specs under
  [`orchestrator/os/`](../../orchestrator/os/README.md).

## Status

| Item | State |
|------|-------|
| Rename EAAO → EADOS | ✅ merged (#33) |
| Design package — RFC-0001 + OS specs + diagrams | ✅ merged (#35) |
| **M1 — Foundation** | ✅ **done** — M1-A..E merged (#37–#41) |
| **M2 — design phase + roles** | ✅ **done** — M2-A..E merged (#42–#46) |
| **M3 — plan phase + traceability** | 🚧 M3-A·B merged (#47, #48) · M3-C (`/eados plan`) drafted — closes M3 |
| **M4 — audit phase + risk** | ⏳ next |
| M5 | ⏳ not started |

Legend: ⏳ not started · 🚧 in progress · ✅ done.

---

## Milestone 1 — Foundation: domain axis, persistent manifest, role authority, `/eados init`

**Goal.** Lay the data foundation the whole pipeline reads from, and the entry command — without
changing how generation behaves today.

- [x] 1.1 Add the **domain/target axis** as data: `orchestrator/domains/_schema.md` +
      `_template.yaml`, and seeds `software.yaml`, `game.yaml`, `mobile.yaml` (each declaring its
      roles, artifacts — GDD vs PRD, NFR axes — RAM/GPU/framerate for `game`, and milestone
      vocabulary — Alpha/Beta/RC vs SemVer).
- [x] 1.2 `eados_lint`: a **`domain-completeness`** gate (every `domains/<d>.yaml` defines every
      schema key), mirroring `profile-completeness`.
- [x] 1.3 Interview: new **`Q0.4 — development target`** loads the domain profile; the manifest
      gains a `domain` field.
- [x] 1.4 Promote the manifest to a **persistent, reference-based `delivery_state`** block
      (current phase, checkpoints, cross-link ids) with a `schema_version` (**resolves OQ1**).
- [x] 1.5 Wire the **authority block** to the existing roles (persona in `agent/*.md` ↔ authority
      in `authority.yaml`), making the persona≠authority separation real.
- [x] 1.6 Ship the **`/eados init`** command surface (entry skill) + a thin state-driven
      phase-runner skeleton that reads `workflow.yaml` and reports the legal next transitions.

**Acceptance gate.** All lints green (incl. `domain-completeness`); render-smoke unchanged; a
chosen domain selects roles/artifacts/NFRs/milestone-vocabulary purely as data.
**Depends on:** RFC-0001, `orchestrator/os/` specs.

---

## Milestone 2 — `design` phase (RFC) + Product/Delivery roles + workflow checker + authority gate

**Goal.** Make the first governance phase real: author/import RFCs under a review protocol, with
the new org-chart roles and the deterministic engine that gates phase transitions.

- [x] 2.1 Add personas `agent/{product-manager,tech-lead,producer}.md` + the **domain-overlay**
      pattern (`agent/domains/<domain>/<role>.md`, e.g. the `game` `product-manager` = Game
      Designer); recursive `agent-registry` + `authority-personas` lints. **OQ4 resolved:** one
      authority role + a domain-specialized persona overlay (not two role IDs).
- [x] 2.2 RFC template + the **RFC-review protocol** under `orchestrator/os/rfc/` (schema +
      config + template + protocol), and `tools/rfc_check.py` enforcing the **`rfc-approved`** gate
      (required sections + a `tech-lead` approval record).
- [x] 2.3 The **deterministic workflow checker**: `phase_runner.py` returns the legal transitions
      and (new `--propose <to>`) validates a proposed transition and **emits the checkpoint** to
      write — read-only; the agent writes it, the human confirms H-gates.
- [x] 2.4 The **authority gate** — `tools/authority_check.py <role> <paths>` enforces the
      `authority.yaml` ownership map: a path the acting role may not write (outside its
      `owns`/`may_draft`) is rejected. Agent-invoked (CI can't know the actor's role), tested.
- [x] 2.5 Ship the **`/eados design`** command surface (`commands/design.md` — authority-check →
      author the RFC from the template → review → `rfc_check` → `phase_runner --propose plan`).

**Acceptance gate.** A sample RFC passes the review gate; an out-of-authority edit is rejected by
the authority gate; the checker computes the correct legal transitions for a given state.
**Depends on:** M1.

---

## Milestone 3 — `plan` phase: roadmap from RFCs + the traceability graph

**Goal.** Co-create the roadmap from RFCs through a real negotiation, and build the lineage graph
that makes delivery auditable.

- [x] 3.1 The **roadmap-negotiation protocol** under `orchestrator/os/plan/` (schema + `plan.yaml`
      config + `negotiation-protocol.md`): PM proposes → `tech-lead` sizes (T-shirt) → `producer`
      reconciles capacity, anchored to artifacts (no "multi-agent theatre").
- [x] 3.2 Ship the **`/eados plan`** command surface (`commands/plan.md` — negotiate via `plan.yaml`
      → write `ROADMAP.md` → `traceability.py` (`roadmap-covers-rfcs`) → `--propose scaffold`).
- [x] 3.3 The **traceability-graph builder** — `tools/traceability.py` builds the design-time
      `RFC → milestone` edges from the roadmap (the Git-side `PR → commit → release` edges land in
      M4, derived from the `git`-spec cross-links).
- [x] 3.4 The **`roadmap-covers-rfcs`** gate — `traceability.py` fails when an RFC is addressed by
      no milestone (every RFC maps to ≥1 milestone; generalizes the spec-coverage-map). Wired into
      `workflow.yaml`.

**Acceptance gate.** Every RFC maps to ≥1 milestone; the graph builds from a sample project's
cross-links.
**Depends on:** M2.

---

## Milestone 4 — `audit` phase: risk scoring + enforced `traceability-lint`

**Goal.** Stand up continuous audit with a real risk model, and turn the traceability graph into
a blocking gate.

- [ ] 4.1 A **risk model**: score = f(owned paths touched × change size × security surface),
      generalizing the `reviewer` + `security-auditor` roles into a standing audit.
- [ ] 4.2 Ship the **`/eados audit`** command surface; emit a risk register.
- [ ] 4.3 The **`traceability-lint`** gate: fail on a dangling edge (RFC without milestone,
      milestone at release without PR, …).
- [ ] 4.4 Risk-threshold → **mandatory `security-auditor` gate** above the threshold; decide
      whether the threshold is per-domain (**resolves OQ2**).

**Acceptance gate.** A seeded dangling edge fails `traceability-lint`; a change above the risk
threshold forces the security gate.
**Depends on:** M3.

---

## Milestone 5 — `refactor` (brownfield) — last, sandboxed

**Goal.** Bring an existing repository up to the standard via incremental, gated migrations —
the highest-risk phase (it edits real user code), so it is sequenced last and write-contained.

- [ ] 5.1 **Brownfield reader**: ingest an existing repo and map it against the EADOS standard
      (structure, governance, gates, profiles).
- [ ] 5.2 **Migration planner**: propose incremental migration PRs (one logical change each),
      ordered by risk/dependency.
- [ ] 5.3 A **write-contained sandbox** (defense-in-depth, building on the renderer write guards
      of [ADR-0007](../adr/0007-renderer-write-guards-and-validation-independence.md)) — no write
      escapes the target repo; every change is a reviewable, gated PR.
- [ ] 5.4 Ship the **`/eados refactor`** command surface.

**Acceptance gate.** A fixture repo is migrated via gated PRs; no write escapes the sandbox; each
PR passes the standard's gates.
**Depends on:** M4.

---

## Cross-cutting (every milestone)

- [ ] English on disk; agent drafts / human merges & publishes; Conventional Commits;
      one logical change per PR; one PR at a time.
- [ ] Each new spec/role/domain ships `_schema`-validated and lint-gated — never a special case
      in code (anti-fragmentation).
- [ ] Each milestone keeps RFC-0001, this roadmap, the affected specs, and the CHANGELOG in sync
      in the same PR.

## Open questions (each resolved within its milestone)

| OQ | Question | Resolved in |
|----|----------|-------------|
| OQ1 | Manifest schema-versioning mechanics | ✅ M1-B (item 1.4) — embedded `schema_version` |
| OQ4 | product-manager vs game-designer role shape | ✅ M2-A (item 2.1) — one authority role + domain persona overlay |
| OQ2 | Risk-score thresholds (per-domain?) | M4 (item 4.4) |
| OQ3 | Committed, CI-generated SVG vs Mermaid-only | Deferred (RFC §9 leans Mermaid-only) |
