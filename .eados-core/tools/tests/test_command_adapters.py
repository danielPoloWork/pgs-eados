#!/usr/bin/env python3
"""Tests for the command-adapters self-lint check (#239, ADR-0019 class 4) —
eados_lint.command_adapter_problems.

Every AVAILABLE `/eados <name>` row of orchestrator/commands/README.md must ship its Claude Code
adapter at .claude/commands/eados/<name>.md, and the adapter must POINT at the row's own canonical
procedure (never copy it). Symmetric: an orphan adapter with no available row is stale. These pin
the pure helper off in-memory fixtures plus the live factory tree. Dependency-free.

    python .eados-core/tools/tests/test_command_adapters.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import eados_lint as lint  # noqa: E402  (the module under test)

REPO_ROOT = os.path.dirname(lint.ROOT)

# A command table with two available rows (one with the scaffold-style ../ procedure link), one
# not-yet-available row, and an alias-table row — only the available rows demand adapters.
README = (
    "| Command | Phase | Status | Procedure |\n"
    "|---------|-------|--------|-----------|\n"
    "| `/eados init` | init | **available** (M1) | [`init.md`](init.md) |\n"
    "| `/eados scaffold` | scaffold | **available** (today's factory) | "
    "[`../generate.md`](../generate.md) |\n"
    "| `/eados debug` | — | planned (M15 W2) | [`debug.md`](debug.md) |\n"
    "| `refactor` (code cleanup) | `/eados refactor` | cross-cutting | #243 · planned |\n"
)
GOOD = {
    "init": "pointer -> `.eados-core/orchestrator/commands/init.md` (read and follow)",
    "scaffold": "pointer -> `.eados-core/orchestrator/generate.md` (read and follow)",
}


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def main():
    failures = []
    P = lint.command_adapter_problems

    # --- link resolution: plain and ../-style Procedure links both canonicalize ---
    check("a plain link resolves under orchestrator/commands/",
          lint._canonical_procedure("init.md") == ".eados-core/orchestrator/commands/init.md",
          failures)
    check("a ../ link resolves beside orchestrator/ (the scaffold case)",
          lint._canonical_procedure("../generate.md") == ".eados-core/orchestrator/generate.md",
          failures)

    # --- happy path: every available row has a pointing adapter; planned rows demand nothing ---
    check("available rows with pointing adapters are clean", P(README, GOOD) == [], failures)

    # --- a missing adapter for an available row is flagged ---
    missing = P(README, {"init": GOOD["init"]})
    check("a missing adapter is flagged",
          any("scaffold.md is missing" in p for p in missing), failures)

    # --- an adapter that does not point at ITS row's procedure is flagged (pointer contract) ---
    stale = P(README, {"init": GOOD["init"], "scaffold": "follow init.md instead"})
    check("an adapter without its canonical procedure path is flagged",
          any("does not point at its canonical procedure" in p and "generate.md" in p
              for p in stale), failures)

    # --- an orphan adapter (planned command shipping early, or a deleted row) is flagged ---
    orphan = P(README, dict(GOOD, debug="pointer -> .eados-core/orchestrator/commands/debug.md"))
    check("an orphan adapter with no available row is flagged",
          any("debug.md has no available" in p for p in orphan), failures)

    # --- parse-failure guard: a README with no parseable rows is a loud single problem ---
    none = P("nothing here\n", GOOD)
    check("an unparseable command table is reported loudly",
          len(none) == 1 and "could not parse" in none[0], failures)

    # --- live invariant: the factory's own table and adapters are in lockstep ---
    collected = []
    lint.check_command_adapters(lambda _name, msg: collected.append(msg))
    if os.path.exists(os.path.join(REPO_ROOT, ".eados-dev")):
        check(f"the shipped table and adapters are in lockstep (got {collected})",
              collected == [], failures)
    else:
        check("outside the factory checkout the check stays silent", collected == [], failures)

    if failures:
        print("test-command-adapters: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} expectation(s) failed.")
        return 1
    print("test-command-adapters: OK — every available row demands a pointing adapter, orphans "
          "and non-pointers are caught, planned rows are exempt, and the live tree is in lockstep.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
