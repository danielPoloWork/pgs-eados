# `DEPENDABOT_SYNC_TOKEN` — setup guide (optional, for green-by-itself)

This guide is for whoever **operates the EADOS factory repository** (the maintainer of `pgs-eados`,
or anyone who forks/vendors EADOS and runs its CI). It is **factory-only** — generated repositories
render no workflow templates, so they have no pin-drift and do not need this.

## What this is for

The [`dependabot-pin-sync`](../../.github/workflows/dependabot-pin-sync.yml) workflow
([ADR-0013](../docs/adr/0013-dependabot-action-pin-auto-remediation.md)) auto-commits the action-pin
re-sync onto a Dependabot `github-actions` PR (see the
[`action-pins` lockstep](../docs/adr/0009-ci-supply-chain-pinning.md) and
[`tools/sync_action_pins.py`](../tools/sync_action_pins.py)).

The catch: a commit pushed with the default **`GITHUB_TOKEN` does not re-trigger CI** (GitHub's
recursion guard). So with no extra setup, the fix *lands on the PR* but the failed `action-pins`
check stays red until the next event or a manual re-run. Pushing that commit with a token that is
**not** `GITHUB_TOKEN` (a PAT or a GitHub App token) makes CI re-run, so the check goes **green by
itself**.

**This token is optional.** Without it the auto-fix still lands; you just re-run the check (or merge,
since the templates are now correct). Set it up only if you want zero-touch green checks — most
useful once branch protection requires status checks (when the repo is public).

> ⚠️ **Never paste a token into a chat, an issue, a commit, or a log.** Set it only via the
> hidden-input paths below. Treat it like a password.

---

## Which to choose

| | Fine-grained PAT (Option A) | GitHub App (Option B) |
|---|---|---|
| Setup effort | Low — one secret, **works with the workflow as-is** | Higher — App + key + a small workflow edit |
| Tied to a person | **Yes** (breaks if they lose access) | **No** (survives team changes) |
| Token lifetime | Long-lived (≤ 1 year), **you must rotate** | Short-lived (minted per run) |
| Counts as | The user's actions | The App (a bot identity) |
| Best for | A solo maintainer, quick start | Orgs / long-lived projects |

**Recommendation:** Option A to get going (it needs no workflow change); migrate to Option B for an
org or anything long-lived.

---

## Option A — Fine-grained Personal Access Token (drop-in)

The workflow already reads `secrets.DEPENDABOT_SYNC_TOKEN` when present (else `GITHUB_TOKEN`), so a
PAT needs **no workflow change**.

1. **Create the token.** github.com → *Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token*.
   - **Resource owner:** the account/org that owns `pgs-eados`.
   - **Repository access:** *Only select repositories* → **`pgs-eados`**.
   - **Repository permissions:** **Contents → Read and write** — that is the *only* permission
     needed. (The sync edits `templates/.github/workflows/*.tmpl`, which are `.tmpl` files, **not**
     the repo's real `.github/workflows/*.yml`, so the *Workflows* permission is **not** required.
     Only add *Workflows: Read and write* if you ever extend the sync to touch real workflow files.)
   - **Expiration:** the shortest you'll tolerate re-issuing (≤ 1 year). Put a rotation reminder on
     your calendar — an expired token silently stops the green-by-itself behavior (the fix still
     lands via `GITHUB_TOKEN`).
2. **Generate** and copy the token (`github_pat_…`).
3. **Store it as the repo secret** — either:
   - **CLI (hidden prompt, recommended):**
     ```bash
     gh secret set DEPENDABOT_SYNC_TOKEN --repo danielPoloWork/pgs-eados
     # paste the token at the prompt (input is hidden), then Enter
     ```
     Or pipe from a file you delete right after:
     ```bash
     gh secret set DEPENDABOT_SYNC_TOKEN --repo danielPoloWork/pgs-eados < token.txt && rm token.txt
     ```
   - **UI:** repo → *Settings → Secrets and variables → Actions → New repository secret* →
     name **`DEPENDABOT_SYNC_TOKEN`**, value = the token.

Done — no workflow edit needed.

---

## Option B — GitHub App (robust, not tied to a person)

A GitHub App mints a short-lived token at run time. It needs a **small workflow edit** (the App
pattern can't be a single static secret).

1. **Create the App.** github.com → *Settings → Developer settings → GitHub Apps → New GitHub App*.
   - Homepage URL: anything (e.g. the repo URL). **Uncheck "Active" under Webhook** (not needed).
   - **Repository permissions → Contents → Read and write** (only this; see the Workflows note above).
   - **Where can this App be installed:** *Only on this account*.
2. **Generate a private key** (App settings → *Private keys → Generate*) and download the `.pem`.
   Note the **App ID**.
3. **Install the App** on `pgs-eados` (App settings → *Install App* → select the repo).
4. **Store two secrets** (UI or `gh secret set`):
   - `SYNC_APP_ID` = the App ID,
   - `SYNC_APP_PRIVATE_KEY` = the full contents of the `.pem`.
5. **Edit the workflow** `.github/workflows/dependabot-pin-sync.yml` to mint a token and hand it to
   checkout. Add a step before the checkout and reference its output (pin the action to a commit SHA
   per [ADR-0009](../docs/adr/0009-ci-supply-chain-pinning.md) — Dependabot then keeps it current):
   ```yaml
       steps:
         - name: Mint a short-lived App token
           id: app-token
           uses: actions/create-github-app-token@<SHA>   # vN — SHA-pin per ADR-0009
           with:
             app-id: ${{ secrets.SYNC_APP_ID }}
             private-key: ${{ secrets.SYNC_APP_PRIVATE_KEY }}
         - name: Check out the Dependabot PR branch
           uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
           with:
             ref: ${{ github.event.workflow_run.head_branch }}
             fetch-depth: 0
             token: ${{ steps.app-token.outputs.token }}   # replaces secrets.DEPENDABOT_SYNC_TOKEN
         # ... the remaining steps are unchanged
   ```
   With the App, `DEPENDABOT_SYNC_TOKEN` is no longer used — remove that secret if you set it for
   Option A.

---

## Verify it works

The token is exercised by the **next Dependabot `github-actions` PR that drifts a shared pin** — no
artificial trigger is reliable for the actions ecosystem. When that PR opens:

1. `eados-ci` runs and the `self-lint` job fails on `[action-pins]`.
2. The `dependabot-pin-sync` workflow fires (Actions tab → it runs only for `dependabot[bot]` PRs),
   runs `sync_action_pins.py --fix`, and pushes the re-sync commit.
3. **With the token:** that push re-triggers `eados-ci`, which now passes — the check turns green
   with no human action. **Without it:** the fix is committed but you re-run the check (or just
   merge, since the templates are correct).

To confirm the secret exists (names only, never values):
```bash
gh secret list --repo danielPoloWork/pgs-eados
```

## Security notes

- **Least privilege:** Contents-write only, scoped to this one repo. Nothing else.
- The token is consumed **only** by the `dependabot-pin-sync` workflow, which is itself gated to
  genuine in-repo Dependabot PRs (`actor == dependabot[bot]`) and runs from the trusted default
  branch (`workflow_run`, not `pull_request_target`) — see ADR-0013.
- **Rotate** a PAT before expiry; prefer the **App** (Option B) for orgs and longevity.
- Revoke immediately if leaked: PAT → delete it in *Developer settings*; App → regenerate its
  private key. Then re-issue and re-set the secret.
