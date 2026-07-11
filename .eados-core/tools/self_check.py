#!/usr/bin/env python3
"""EADOS pre-flight self-check (#223, M14) — the cheap, agent-facing checklist to answer on your OWN
draft BEFORE opening a PR (and before the gate).

Three neighbours, three jobs — this is the one that had no home:
  * `preflight.py`    verifies the *toolchain* (python / git / gh present + authenticated);
  * `self_review.py`  is the CI-style gate over a *rendered repo* (the scaffold self-review);
  * `self_check.py`   (this) is a short, ADVISORY checklist the acting agent answers about the CHANGE
                      it is about to propose — the common, cheap misses (a path it does not own, more
                      than one PR, a non-English on-disk value, unfilled PR metadata) that a gate
                      would otherwise catch only after a round-trip. The gate stays authoritative;
                      this just front-runs it so the miss is caught before the PR, not after.

Every item is DERIVED from a spec — `authority.ownership_map`, `git.commit`, `git.pr.metadata`,
`git.pr.required_crosslinks`, and (M17 17.4, #280) the `interaction` policy's operative blocks —
so the checklist can never rot away from the rules it front-runs (a
metadata field added to `git.yaml` shows up here automatically, proven in the tests). English-on-disk
and the precedence order are the two invariants with no single machine-readable field; they are cited
to `AGENTS.md` §2 and the `os/` README *Precedence* section, the way every file in the tree cites its
governing section.

Dependency-free (stdlib + the sibling renderer's YAML loader). It prints; it changes nothing.

    python .eados-core/tools/self_check.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # .eados-core/
sys.path.insert(0, HERE)
import render  # noqa: E402  — the hand-rolled, dependency-free YAML loader (sibling tool)

AUTHORITY = os.path.join(ROOT, "orchestrator", "os", "authority", "authority.yaml")
GIT = os.path.join(ROOT, "orchestrator", "os", "git", "git.yaml")
INTERACTION = os.path.join(ROOT, "orchestrator", "os", "interaction", "interaction.yaml")


def _load(path):
    """A spec loaded as data, or `{}` when it is absent/unreadable — a missing spec drops the items it
    would have sourced, never a traceback (the checklist is advisory, not load-bearing)."""
    try:
        with open(path, encoding="utf-8") as handle:
            return render.load_yaml(handle.read()) or {}
    except OSError:
        return {}


def preflight_checklist(authority, git, interaction=None):
    """The pre-PR self-check as a list of `(question, source)` pairs, each DERIVED from a spec field —
    or cited, for the two invariants with no machine-readable field. Pure (no I/O). When `interaction`
    is present (M17 17.4, #280), the checklist also front-runs the interaction contract's operative
    rules — the *how you communicate* half of the contract, sourced from the blocks the policy
    actually declares so a renamed block surfaces here rather than rotting."""
    commit = git.get("commit") or {}
    prpol = git.get("pr") or {}
    meta = prpol.get("metadata") or {}
    crosslinks = prpol.get("required_crosslinks") or []
    owns_rules = authority.get("ownership_map") or []

    items = [(
        f"does every path I changed resolve to a glob my role owns or may draft? "
        f"({len(owns_rules)} rules in authority.ownership_map)",
        "authority: ownership_map / roles[].may_draft")]
    if commit.get("one_logical_change_per_pr") or commit.get("one_pr_at_a_time"):
        items.append((
            "is this ONE logical change, and the only PR in flight?",
            "git: commit.one_logical_change_per_pr / one_pr_at_a_time"))
    if meta:
        fields = ", ".join(f"{k}={v}" for k, v in meta.items())
        items.append((
            f"will the PR carry every metadata field set on creation ({fields})?",
            "git: pr.metadata"))
    if crosslinks:
        items.append((
            f"does the PR body reference its required cross-links ({', '.join(crosslinks)})?",
            "git: pr.required_crosslinks"))
    if prpol.get("opened_by") == "human" or prpol.get("merged_by") == "human":
        items.append((
            "have I stopped at the draft/PR boundary — the human opens and merges, not me?",
            "git: pr.opened_by / pr.merged_by = human; AGENTS.md §6"))
    if interaction:
        blocks = ", ".join(k for k in ("confidence", "sycophancy", "dissent", "pushback")
                           if interaction.get(k)) or "the contract"
        items.append((
            "does the reply I am about to send calibrate — load-bearing claims confidence-tagged by "
            "evidence, no courtesy opener, and the dissent template (position/alternative/risk) when "
            "I disagree?",
            f"interaction: {blocks}; AGENTS.md §10"))
    items.append((
        "is every value I wrote on disk English?",
        "AGENTS.md §2"))
    items.append((
        "if I touched an overlapping layer, does my change respect precedence "
        "(a lesson / profile never overrides a gate, a spec, or the human)?",
        "os/README.md — Precedence"))
    return items


def format_checklist(items):
    """Render the `(question, source)` pairs as an aligned, tickable checklist block."""
    lines = ["pre-flight self-check — answer before opening the PR "
             "(advisory; the gate is authoritative):"]
    for question, source in items:
        lines.append(f"  [ ] {question}")
        lines.append(f"        ↳ {source}")
    return lines


def main(argv=None):
    # issue #128: force UTF-8 stdio so the ↳ arrow never mojibakes or crashes on cp1252 (Windows).
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser(
        description="EADOS pre-flight self-check - the agent-facing checklist to run before a PR.")
    ap.parse_args(argv)
    for line in format_checklist(preflight_checklist(_load(AUTHORITY), _load(GIT), _load(INTERACTION))):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
