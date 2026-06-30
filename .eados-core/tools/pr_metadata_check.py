#!/usr/bin/env python3
"""EADOS PR-metadata presence check (roadmap M11 #141) — verifies that an open PR actually carries
the project-board metadata the contract requires: an **assignee** (the owner), **exactly one type
label**, and a **milestone**; the GitHub **Project** is advisory (set only where the repo has one).
The contract itself is data in `orchestrator/os/git/git.yaml` (`pr.metadata`); this tool reports
whether a live PR matches it.

The evaluator core (`evaluate_metadata`) is pure and fixture-tested; only `--pr N` shells out to
`gh`, degrading cleanly (clear message, exit 2) when gh is missing, unauthenticated, or offline —
like `pr_review.py`. It reports; it never sets metadata, opens, or merges (AGENTS.md §6).

    python .eados-core/tools/pr_metadata_check.py --pr 141 [--repo OWNER/REPO] [--json]

Exit: 0 = complete, 1 = a required field is missing, 2 = could not reach `gh`.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

REQUIRED = ("assignee", "label", "milestone")   # the fields the contract mandates on creation


# --- the pure evaluator ---------------------------------------------------
def evaluate_metadata(pr):
    """Given a PR's metadata, report which contract fields are set. `pr` keys: `assignees` (list of
    logins), `labels` (list of names), `milestone` (title or None), `project` (truthy when the PR is
    on a board). `assignee` passes with >=1 assignee; `label` wants exactly one (the one-type-label
    rule) and is `warn` when present but not exactly one; `milestone` passes when set; `project` is
    advisory — informational, never a failure (it exists only where the repo has a board)."""
    assignees = pr.get("assignees") or []
    labels = pr.get("labels") or []
    milestone = pr.get("milestone")
    project = pr.get("project")

    checks = [{
        "field": "assignee",
        "status": "pass" if assignees else "fail",
        "note": f"assigned to {', '.join(assignees)}" if assignees
                else "no assignee — set the owner (`--assignee`)",
    }]
    if len(labels) == 1:
        label_status, label_note = "pass", f"one type label: {labels[0]}"
    elif not labels:
        label_status, label_note = "fail", "no label — set exactly one type label (`--label`)"
    else:
        label_status = "warn"
        label_note = f"{len(labels)} labels ({', '.join(labels)}) — the rule is exactly one type label"
    checks.append({"field": "label", "status": label_status, "note": label_note})
    checks.append({
        "field": "milestone",
        "status": "pass" if milestone else "fail",
        "note": f"milestone: {milestone}" if milestone
                else "no milestone — set the open release/roadmap milestone (`--milestone`)",
    })
    checks.append({
        "field": "project",
        "status": "pass" if project else "advisory",
        "note": "on a Project board" if project
                else "no Project — advisory (set only where the repo has one)",
    })

    missing = [c["field"] for c in checks if c["field"] in REQUIRED and c["status"] == "fail"]
    warnings = [c["field"] for c in checks if c["status"] == "warn"]
    return {
        "pr": pr.get("number"),
        "checks": checks,
        "missing_required": missing,
        "warnings": warnings,
        "complete": not missing,
        "boundary": "reports only — set metadata with `gh pr create`/`gh pr edit` (AGENTS.md §6)",
    }


def format_report(report):
    """Render an `evaluate_metadata` report as a human-readable check."""
    mark = {"pass": "[OK]  ", "fail": "[MISS]", "warn": "[WARN]", "advisory": "[ -- ]"}
    out = [f"PR-metadata check: #{report.get('pr')}"]
    for c in report["checks"]:
        out.append(f"  {mark.get(c['status'], '[????]')} {c['field']} — {c['note']}")
    if report["complete"]:
        tail = " (see warnings above)" if report["warnings"] else ""
        out.append("  -> complete: assignee, label, and milestone are all set." + tail)
    else:
        out.append(f"  -> INCOMPLETE: missing {', '.join(report['missing_required'])} — "
                   "set it before opening the PR.")
    out.append(f"  {report['boundary']}")
    return "\n".join(out)


# --- the thin `gh` shell (best-effort; degrades cleanly) ------------------
def _gh_json(args):
    import json
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise RuntimeError(f"could not run `gh` (is the GitHub CLI installed and on PATH?): {exc}")
    if proc.returncode != 0:
        raise RuntimeError(f"`gh {' '.join(args)}` failed (authenticated? online?): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    try:
        return json.loads(proc.stdout or "null")
    except ValueError as exc:
        raise RuntimeError(f"could not parse `gh` JSON output: {exc}")


def fetch_pr_metadata(number, repo=None):
    """Assemble the evaluator's `pr` dict from `gh pr view`. Raises RuntimeError (not a crash) when
    gh is missing/unauthenticated/offline. The required fields (assignees, labels, milestone) are
    universally supported; `projectItems` is fetched separately and best-effort, since its JSON
    field name varies by gh version and the Project signal is only advisory."""
    base = ["pr", "view", str(number)]
    if repo:
        base += ["--repo", repo]
    data = _gh_json(base + ["--json", "number,assignees,labels,milestone"]) or {}
    project = []
    try:
        pdata = _gh_json(base + ["--json", "projectItems"]) or {}
        project = list(pdata.get("projectItems") or [])
    except RuntimeError:
        project = []   # old gh / unknown field -> no Project info (advisory, never a hard failure)
    milestone = data.get("milestone")
    return {
        "number": data.get("number"),
        "assignees": [a.get("login") for a in (data.get("assignees") or []) if isinstance(a, dict)],
        "labels": [lab.get("name") for lab in (data.get("labels") or []) if isinstance(lab, dict)],
        "milestone": milestone.get("title") if isinstance(milestone, dict) else None,
        "project": project,
    }


def main(argv=None):
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Check that an open PR carries assignee + one type "
                                             "label + milestone (and a Project where present).")
    ap.add_argument("--pr", type=int, required=True, help="the PR number to check")
    ap.add_argument("--repo", help="OWNER/REPO (default: the repo gh infers)")
    ap.add_argument("--json", action="store_true", help="emit the structured report as JSON")
    args = ap.parse_args(argv)
    try:
        pr = fetch_pr_metadata(args.pr, repo=args.repo)
    except RuntimeError as exc:
        print(f"pr-metadata-check: SKIP — {exc}", file=sys.stderr)
        return 2
    report = evaluate_metadata(pr)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_report(report))
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
