# ADR-0013: Dependabot action-pin auto-remediation

## Status

Accepted

## Context

[ADR-0009](0009-ci-supply-chain-pinning.md) SHA-pins the EADOS-authored workflow surfaces and adds
the `action-pins` lockstep gate: a SHA-pinned action shared by the factory CI
(`.github/workflows/ci.yml`) and the rendered templates (`templates/.github/workflows/*.tmpl`) must
pin the same commit. Its 2026-06-27 addendum added `tools/sync_action_pins.py` so the re-pin is one
deterministic command. But a command is still a manual step: Dependabot's `github-actions` ecosystem
only edits real workflow files, never the `.tmpl` copies, so **every** shared-pin bump drifts the
templates and the gate blocks the PR until a human runs the fix.

Removing that last manual step means CI must run `--fix` and commit the result back onto the
Dependabot PR. Two GitHub Actions facts constrain how:

- **Dependabot PRs run with a read-only `GITHUB_TOKEN`** (a 2021 hardening) — a `pull_request`-
  triggered job cannot push back.
- **`pull_request_target`** grants a write token *and* secrets but is a well-known privilege-
  escalation footgun if it checks out and executes PR-authored code.

## Decision

Add `.github/workflows/dependabot-pin-sync.yml`, triggered by **`workflow_run`** on completion of
`eados-ci` — **not** `pull_request_target`. It:

1. Runs the workflow definition from the **default branch** (trusted; a PR cannot alter what runs),
   with `permissions: contents: write` and nothing else.
2. Is gated to **genuine Dependabot, in-repo PRs that failed CI**:
   `workflow_run.event == 'pull_request'` && `conclusion == 'failure'` &&
   `actor.login == 'dependabot[bot]'` (an actor login cannot be forged) &&
   `head_repository.full_name == github.repository` (excludes forks).
3. Checks out the PR head branch, runs the repo's own deterministic `sync_action_pins.py --fix`
   (which only copies a SHA the factory CI already trusts — it never resolves a tag itself), and
   pushes the result back **only if the templates drifted**.

Token: `GITHUB_TOKEN` by default. A push by `GITHUB_TOKEN` does **not** re-trigger CI (GitHub's
recursion guard), so the fix lands but the failed check refreshes on the next event or a manual
re-run. An **optional** `DEPENDABOT_SYNC_TOKEN` secret (a repo-scoped PAT or GitHub App token) makes
the pushed commit re-trigger CI so the check goes green with no human action; the workflow uses it
when present, else `GITHUB_TOKEN`. Provisioning that token is the owner's choice and is not required
for the fix itself to land.

## Consequences

- A Dependabot `github-actions` bump that drifts the templates is **self-healed** — the lockstep
  gate's fix is committed automatically, with no manual companion edit (the goal of #76).
- **No loop, no privilege escalation.** The job is idempotent (no drift → no commit → no push), so a
  `GITHUB_TOKEN` push that does not re-trigger CI cannot loop, and an optional-token push that does
  re-trigger ends when the next run finds the templates already in lockstep (`conclusion == 'success'`
  fails the `failure` guard). `workflow_run` never executes PR-authored code with the write token; the
  unforgeable `actor` + in-repo guards keep non-Dependabot actors (incl. a collaborator pushing to a
  Dependabot branch — which shows as *their* actor) out of the privileged job.
- **Factory-only.** Generated repos render no `.tmpl` files, so they have no template drift and do
  not need this workflow; it lives in the factory's own `.github/workflows/`, not in the templates.
- The default (`GITHUB_TOKEN`) path lands the fix but leaves the stale check until re-run; full
  green-by-itself is opt-in via the documented secret ([setup guide](../../maintenance/dependabot-sync-token.md)).
  This is the deliberate trade for requiring no
  mandatory credential setup.

This supersedes the "tracked separately, its own reviewed PR" note in ADR-0009's 2026-06-27
addendum: the auto-remediation shipped together with the tool. See
[`maintenance/stay-current.md`](../../maintenance/stay-current.md) for the resulting maintainer flow.
