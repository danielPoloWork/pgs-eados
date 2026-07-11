# Milestone M17 — Interaction Contract & Confidence Calibration

**Status:** in progress · **Predecessor:** none hard — the M14 runtime hooks it plugs into shipped in
v2.8.0; interleaves with the open M15/M16 tails at the owner's discretion
**Owner:** `@danielPoloWork` · **Planned:** 2026-07-11

## Theme

EADOS governs *what* the agent may do (workflow, authority, git, contribution, routing) but says
nothing about **how it communicates while doing it** — when it must say it is guessing, how it
disagrees with the maintainer, whether it opens with flattery. The result is host-default behavior:
agreeable, uncalibrated, warm-up prose. M17 adopts the owner-provided 7-rule anti-sycophancy
interaction ruleset (2026-07-11) — **transformed, not verbatim** — as the OS's 9th spec
(`os/interaction/`), rendered into every agent contract surface, lockstep-gated, and reinforced at
runtime through the M14 re-grounding hooks. Third input of the prompt-pack family (11-prompts doc →
M15 / ADR-0018; routing table → M16).

## Ratified decisions (2026-07-11)

1. **Transformed, not verbatim.** Two source rules are counterproductive as written: "never start
   with agreement" forces contrarianism (manufactured challenges devalue real ones), and an
   absolute "don't fold" entrenches errors. ADR-0022 records every delta (disposition table below).
   *(Numbering correction: this plan originally reserved "ADR-0019", consumed meanwhile by the
   command-surface taxonomy — numbering is sequential and never reused, so the decision lands as
   ADR-0022.)*
2. **The enforcement ceiling is stated honestly.** Three tiers: *instruct* (live chat — no gate can
   verify a conversation turn), *verify* (on-disk artifacts, lint), *re-ground* (M14 runtime
   hooks). Never marketed as a guarantee — ADR-0015/0016 honesty posture.
3. **Policy-as-data.** The vocabulary, the banned-phrase list, and the protocols live in
   `interaction.yaml` (+ `_schema`); the contracts render them; an `interaction-lockstep` gate
   keeps prose and data congruent. Precedent: risk-weights (#79), routing (ADR-0017).
4. **Generic interaction core only.** No per-activity module catalog (architecture / research /
   code-review interaction modes): per-activity behavior already lives in commands and personas
   (M8 `/eados review`, M15 Wave 2 commands, the 9-role registry). A parallel catalog would drift
   EADOS toward a prompt library (RFC-0001 identity).
5. **Decisions vs claims.** A factual *claim* follows the evidence — hold under pushback only while
   the evidence holds, concede explicitly when wrong. A human *decision* is precedence layer 1
   (`os/README.md`): comply and record the dissent. The precedence order is untouched.

## Source ruleset → disposition (feeds 17.1 / ADR-0022)

| # | Source rule (owner ruleset, 2026-07-11) | Disposition | As adopted |
|---|---|---|---|
| 1 | Never start with agreement; first sentence must challenge | **transformed** | "Open with the most informative statement; never a courtesy opener." Forced contrarianism is as uncalibrated as flattery. |
| 2 | Tag every claim `[certain]` / `[likely]` / `[guessing]` | **adopted + hardened** | Vocabulary kept, with an **evidence criterion per level** (certain = verified this session / in-repo fact, cite it; likely = named-evidence inference; guessing = flagged gap-fill) and a **scope rule**: tag load-bearing claims, not every sentence. "Mostly guessing → say so first" kept. Aligns with interview provenance (#169): `guessing` ↔ `assumed`. |
| 3 | Kill sycophantic phrases ("Great question", …) | **adopted as data** | Banned-opener/phrase list in `interaction.yaml`, overridable via `config/`. Honest caveat: a denylist suppresses the worst offenders; the posture rules do the rest. |
| 4 | Structured disagreement: reason / alternative / specific risk | **adopted verbatim** | The ADR pattern applied to conversation; wired to the authority escalation ladder. |
| 5 | Uncomfortable answer first | **adopted verbatim** | First line, not paragraph three. |
| 6 | No warm-up paragraphs | **adopted verbatim** | Start with the most useful thing. |
| 7 | Don't fold on pushback without new information | **transformed** | Pushback protocol: **re-verify the evidence**; hold a claim only while the evidence still supports it; concede explicitly when wrong; a human decision is layer 1 — comply + record dissent, never relitigate. |
| — | Evolve into a framework with per-activity modules (architecture / research / code review) | **declined** | Identity creep toward a prompt library; per-activity behavior stays in commands + personas (M8, M15). Confidence calibration, uncertainty handling, challenge technique, and trade-off structure all enter the generic core instead. |

## Sequence (one PR each, in order)

| Item | Issue | Title | Effort | Routing |
|---|---|---|---|---|
| 17.1 | [#277](https://github.com/danielPoloWork/pgs-eados/issues/277) | Interaction policy as data + ADR-0022 (`os/interaction/` — confidence / sycophancy / dissent / pushback) | M | frontier-reasoning / high (decision-heavy, sets-pattern) |
| 17.2 | [#278](https://github.com/danielPoloWork/pgs-eados/issues/278) | Render the Interaction Contract into every agent surface (`AGENTS.md.tmpl`, factory `AGENTS.md`, `agent/README` pointer) | M | standard / medium |
| 17.3 | [#279](https://github.com/danielPoloWork/pgs-eados/issues/279) | Gates: `interaction-lockstep` + gate-coverage entries + cross-spec refs | S | standard / medium |
| 17.4 | [#280](https://github.com/danielPoloWork/pgs-eados/issues/280) | Runtime reinforcement: pre-flight / self-check / re-grounding + command reply-shape cues | M | standard / high |
| 17.5 | [#281](https://github.com/danielPoloWork/pgs-eados/issues/281) | Capstone: USAGE, README (×3, i18n), RFC-0001 pointer, delivery record | S | fast / low |

## Delivery record

| Item | Issue | PR | Status |
|---|---|---|---|
| 17.1 | #277 | [#288](https://github.com/danielPoloWork/pgs-eados/pull/288) | draft PR open — `os/interaction/` spec (confidence / sycophancy / dissent / pushback) + ADR-0022 (numbering corrected from the reserved "ADR-0019") |
| 17.2 | #278 | — | queued — depends on 17.1 |
| 17.3 | #279 | — | queued — depends on 17.2 |
| 17.4 | #280 | — | queued — depends on 17.2 |
| 17.5 | #281 | — | queued — depends on 17.1–17.4 |

## Out of scope (invariants)

- **Guaranteed live-chat compliance** — no gate can verify a conversation turn; the OS instructs,
  verifies artifacts, and re-grounds (the ADR-0022 ceiling). Claiming more would be dishonest.
- **Per-activity interaction modules** — review/debug/optimize interaction shapes belong to the
  commands and personas that own those activities (M8, M15), not to this spec.
- **Overriding the host harness** — a host's own system prompt sits above `AGENTS.md`; the
  contract applies where the host permits (ADR-0015/0016 posture).
- **Forced contrarianism** — the goal is calibration, not disagreement theater; source rule 1
  ships only in its transformed form.
- **Autonomous agent merge/publish authority** (RFC-0001 N2) — agent drafts, human merges.
