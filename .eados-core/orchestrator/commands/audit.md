# `/eados audit` — risk-score, traceability-lint, and the security gate

Continuous audit. Scores a change's risk, verifies the traceability graph is whole, and — above
the (per-domain) threshold — requires the `security-auditor` gate, emitting a **risk register**.
Owned by the **security-auditor** (with the **reviewer** for structured findings). Config:
[`../os/risk/risk.yaml`](../os/risk/risk.yaml); the graph: [`traceability.py`](../../tools/traceability.py).

## Preconditions

- The `scaffold` phase passed `consistency-lint` + `self-review` (so `scaffold → audit` is legal —
  this transition is automatic, not human-gated).

## Procedure

1. **Traceability-lint** — the graph must have **no dangling edge**:
   ```bash
   python .eados-core/tools/traceability.py ROADMAP.md $(refs.rfcs) --links links.yaml
   ```
   (`links.yaml` = the PR cross-link edges the `git` spec mandates: `{pr, rfc, milestone, commit,
   release}`.) An RFC with no PR, a PR missing its RFC/milestone, or a release with no PR+commit
   fails the audit. **Derive `links.yaml` from the merged PRs** instead of hand-writing it:
   `python .eados-core/tools/derive_links.py --out links.yaml` (via `gh`; roadmap 6.6).
2. **Risk score** — score the change and learn whether the security gate is mandatory:
   ```bash
   python .eados-core/tools/risk_score.py $(changed paths) --lines N --domain <domain>
   ```
3. **Security gate (conditional)** — when the score says **REQUIRED**, the `security-auditor` runs
   the deep audit (trust boundaries, code-level risk, dependency/supply-chain, secret hygiene, the
   `SECURITY.md` policy — per the role) and the `reviewer` returns **structured findings** the owner
   resolves.
4. **Emit the risk register** — record the outcome: the risk **score**, the **traceability** status,
   and each finding with `severity` (low/medium/high/critical), affected component, realistic
   impact, and a concrete mitigation. A confirmed defect → the bug ledger; a vulnerability → a
   **draft** advisory (the human publishes).
5. **Record & hand off** — note the audit in `delivery_state`; if a migration is needed, propose
   the human-gated `audit → migrate`:
   ```bash
   python .eados-core/tools/phase_runner.py <manifest> --propose migrate
   ```
   Otherwise the audit is the standing gate before a release.

## Boundary

The audit is **assessment and remediation only** — it never weaponizes a finding, never disables a
control to "unblock", and never publishes an advisory (the human does). The agent runs the checks,
**drafts** the register, and **proposes** the transition; the human confirms (`AGENTS.md` §6).
