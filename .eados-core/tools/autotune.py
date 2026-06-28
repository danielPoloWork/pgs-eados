#!/usr/bin/env python3
"""Auto-tuner: propose default changes from accumulated generation run records.

Dependency-free (reuses render.py's YAML loader). Run:

    python .eados-core/tools/autotune.py [--threshold N]

It reads every record under learning/runs/*.yaml and, for each manifest key, looks at how
often the maintainer overrode the built-in/profile default and to what value. When a single
value replaces the default in at least `--threshold` records (default 2) and is the majority
choice, it proposes changing that default — a draft suggestion a human turns into a profile /
config / questionnaire PR. It NEVER edits anything itself; it only reports.

This is "auto-tuning" done safely: the data is version-controlled, the proposal is reviewable,
and a human applies it.
"""

import argparse
import collections
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import load_yaml  # noqa: E402  (same-dir tool)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "learning", "runs")


def main():
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Propose default changes from run history.")
    ap.add_argument("--threshold", type=int, default=2,
                    help="min records overriding a key to the same value before proposing")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(RUNS, "*.yaml")))
    if not files:
        print("autotune: no run records yet — nothing to propose. "
              "(Records accumulate under learning/runs/ as projects are generated.)")
        return 0

    # key -> Counter of chosen values; key -> set of seen default values; key -> total runs
    chosen = collections.defaultdict(collections.Counter)
    defaults = collections.defaultdict(set)
    totals = collections.Counter()
    for path in files:
        with open(path, encoding="utf-8") as handle:
            rec = load_yaml(handle.read())
        # Collapse duplicate overrides of the same key WITHIN one record (last wins): a key
        # listed twice must not inflate its chosen-count past totals[key] (a false majority).
        per_record = {}
        for ov in rec.get("overrides", []) or []:
            if not isinstance(ov, dict):
                continue
            key = str(ov.get("key", "")).strip()
            if not key:
                continue
            per_record[key] = (str(ov.get("chosen", "")).strip(),
                               str(ov.get("default", "")).strip())
        for key, (chosen_val, default_val) in per_record.items():
            chosen[key][chosen_val] += 1
            defaults[key].add(default_val)
            totals[key] += 1

    proposals = []
    for key, counter in chosen.items():
        # Most-chosen value, ties broken deterministically by value (Counter.most_common
        # leaves equal-count order implementation-defined, which would make output flaky).
        value = max(counter.items(), key=lambda kv: (kv[1], kv[0]))[0]
        n = counter[value]
        if n >= args.threshold and n * 2 > totals[key]:
            old = " / ".join(sorted(d for d in defaults[key] if d)) or "(built-in)"
            proposals.append((n, len(files), key, old, value))

    if not proposals:
        print(f"autotune: {len(files)} run(s) analyzed — no default is overridden often "
              f"enough (threshold {args.threshold}) to propose a change.")
        return 0

    print(f"autotune: {len(files)} run(s) analyzed — proposed default changes:\n")
    for n, total, key, old, value in sorted(proposals, reverse=True):
        print(f"  • {key}: overridden to '{value}' in {n}/{total} runs "
              f"(current default: {old}). Consider updating the profile/config/questionnaire.")
    print("\nThese are suggestions only — apply via a reviewed PR; autotune changes nothing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
