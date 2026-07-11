#!/usr/bin/env python3
"""git_check — the deterministic evaluator for the `os/git/git.yaml` policy (#250).

`git.yaml` declares the branch / commit / one-PR policy as data, but until now NO tool evaluated
it: branch naming, Conventional-Commit shape, and one-PR-at-a-time were advisory prose — the
honor system this issue closes. This tool reads the policy AS DATA (never hardcoded) and checks:

  * **branch**  — the current branch matches `<type>/<short-kebab>` with a declared type
                  (the default branch itself is exempt: the human lives there; agents branch);
  * **commit**  — HEAD's subject is a Conventional Commit: `type(scope): subject`, declared
                  type, declared scope when present, subject <= 72 chars (merge commits and the
                  bootstrap root are exempt — they are not authored change subjects);
  * **one-PR**  — at most one open PR (git.yaml `commit.one_pr_at_a_time`), via `gh`; no `gh`
                  (or no network) degrades to SKIP — offline work must not fail on a courtesy
                  check it cannot perform.

PR *metadata* (assignee / one type label / milestone) stays `pr_metadata_check.py`'s job — this
tool checks what is knowable from git alone plus the one-PR count. Registered in workflow.yaml
as the cross-cutting `git-policy` gate (`wired: external`, like `traceability-lint`): the agent
runs it pre-PR, CI may gate on it; `--advisory` reports without failing the exit code (the
"advisory locally, gating in CI" split is the caller's flag, not two tools).

    python .eados-core/tools/git_check.py [--repo DIR] [--advisory]
        [--branch NAME] [--message SUBJECT]     # overrides for testing / CI contexts

Pure helpers (branch_problems / commit_problems) + a thin CLI shell, per the pr_review.py
pattern. Dependency-free (stdlib + the sibling YAML loader).
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # .eados-core/
sys.path.insert(0, HERE)
import render  # noqa: E402  — the dependency-free YAML loader

GIT_POLICY = os.path.join(ROOT, "orchestrator", "os", "git", "git.yaml")

_KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*\Z")
_SUBJECT = re.compile(r"(?P<type>[a-z]+)(\((?P<scope>[^)]*)\))?(?P<bang>!)?: (?P<desc>.+)\Z")
_SUBJECT_MAX = 72


def load_policy(path=GIT_POLICY):
    with open(path, encoding="utf-8") as handle:
        return render.load_yaml(handle.read()) or {}


def branch_problems(branch, policy):
    """Violations of `branch_naming` for `branch`. The default branch is exempt (agents never
    push to it — a different rule, enforced by the human merge gate, not by naming)."""
    naming = policy.get("branch_naming") or {}
    types = [str(t) for t in (naming.get("types") or [])]
    default = str(((policy.get("pr") or {}).get("default_branch") or "main"))
    branch = str(branch or "").strip()
    if not branch or branch == "HEAD":
        return [f"cannot determine the current branch (got {branch!r}) — detached HEAD?"]
    if branch in (default, "main", "master"):
        return []
    if "/" not in branch:
        return [f"branch '{branch}' does not match '{naming.get('pattern') or '<type>/<kebab>'}' "
                f"— no '<type>/' prefix (declared types: {', '.join(types)})"]
    btype, _, rest = branch.partition("/")
    problems = []
    if types and btype not in types:
        problems.append(f"branch '{branch}': type '{btype}' is not a declared branch type "
                        f"({', '.join(types)})")
    if not _KEBAB.match(rest):
        problems.append(f"branch '{branch}': '{rest}' is not short-kebab "
                        "(lowercase a-z0-9 segments joined by '-')")
    return problems


def commit_problems(subject, policy):
    """Violations of `commit.convention` for one commit `subject`. Merge commits and the
    bootstrap root are exempt — they are not authored Conventional-Commit subjects."""
    commit = policy.get("commit") or {}
    if str(commit.get("convention") or "") != "conventional-commits":
        return []                                   # a policy without the convention checks nothing
    types = [str(t) for t in ((policy.get("branch_naming") or {}).get("types") or [])]
    scopes = [str(s) for s in (commit.get("scopes") or [])]
    subject = str(subject or "").strip()
    if not subject:
        return ["HEAD has no commit subject to check"]
    if subject.startswith(("Merge ", "Revert \"", "Initial commit")):
        return []
    m = _SUBJECT.match(subject)
    if not m:
        return [f"commit subject {subject!r} is not Conventional-Commit shaped "
                "(`type(scope): imperative subject`)"]
    problems = []
    if types and m.group("type") not in types:
        problems.append(f"commit type '{m.group('type')}' is not a declared type "
                        f"({', '.join(types)})")
    scope = m.group("scope")
    if scope is not None and scopes and scope not in scopes:
        problems.append(f"commit scope '{scope}' is not a declared scope "
                        f"({', '.join(scopes)})")
    if len(subject) > _SUBJECT_MAX:
        problems.append(f"commit subject is {len(subject)} chars — the convention caps it at "
                        f"{_SUBJECT_MAX}")
    return problems


def _git(repo, *args):
    """One git plumbing call; None when git is unavailable or the call fails."""
    try:
        proc = subprocess.run(["git", "-C", repo, *args],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def open_pr_count(repo):
    """The number of open PRs, via gh; None == gh unavailable/unauthenticated (SKIP, not FAIL —
    offline work must not fail a courtesy count it cannot perform)."""
    try:
        proc = subprocess.run(["gh", "pr", "list", "--state", "open", "--json", "number"],
                              cwd=repo, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.count('"number"')


def main(argv=None):
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser(description="EADOS git-policy check — the git.yaml evaluator "
                                             "(branch naming, commit convention, one-PR).")
    ap.add_argument("--repo", default=".", help="repository root (default: .)")
    ap.add_argument("--branch", help="branch name to check (default: the current branch)")
    ap.add_argument("--message", help="commit subject to check (default: HEAD's subject)")
    ap.add_argument("--advisory", action="store_true",
                    help="report violations but exit 0 (the local pre-flight mode; CI omits it)")
    args = ap.parse_args(argv)

    try:
        policy = load_policy()
    except (OSError, ValueError) as exc:
        print(f"git-check: ERROR — cannot read git.yaml policy: {exc}", file=sys.stderr)
        return 2

    branch = args.branch if args.branch is not None else _git(args.repo, "rev-parse",
                                                              "--abbrev-ref", "HEAD")
    subject = args.message if args.message is not None else _git(args.repo, "log", "-1",
                                                                 "--format=%s")
    problems, skips = [], []
    if branch is None:
        skips.append("branch: git unavailable — SKIP")
    else:
        problems += branch_problems(branch, policy)
    if subject is None:
        skips.append("commit: git unavailable — SKIP")
    else:
        problems += commit_problems(subject, policy)
    if (policy.get("commit") or {}).get("one_pr_at_a_time"):
        count = open_pr_count(args.repo)
        if count is None:
            skips.append("one-PR: gh unavailable — SKIP")
        elif count > 1:
            problems.append(f"{count} PRs are open — git.yaml commit.one_pr_at_a_time allows one")

    print(f"git-policy check ({args.repo}) — branch: {branch or '?'}")
    for s in skips:
        print(f"  [SKIP] {s}")
    if problems:
        print("  FAIL")
        for p in problems:
            print(f"  - {p}")
        if args.advisory:
            print("  (advisory mode — reporting only, exit 0)")
            return 0
        return 1
    print("  OK — branch, commit subject, and PR count meet the git.yaml policy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
