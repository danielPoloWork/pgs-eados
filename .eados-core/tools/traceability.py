#!/usr/bin/env python3
"""EADOS traceability — the design-time lineage and the `roadmap-covers-rfcs` gate (roadmap 3.3 /
3.4; RFC-0001 §7).

Builds the `RFC → milestone` edges of the traceability graph from a roadmap, and enforces that
**every RFC is addressed by at least one milestone** (the `plan → scaffold` gate). The Git-side
edges (milestone → PR → commit → release) are added in M4, derived from the cross-links the `git`
spec mandates. Dependency-free (Python standard library only).

    python .eados-core/tools/traceability.py <roadmap.md> <RFC-id> [<RFC-id> ...]
"""

import re
import sys


def parse_milestones(text):
    """Ordered list of (number, title, body) for each `## Milestone N — ...` section."""
    out = []
    matches = list(re.finditer(r"(?m)^##\s+Milestone\s+(\d+)\s*[—:-]?\s*(.*)$", text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(1), m.group(2).strip(), text[start:end]))
    return out


def covering_milestones(text, rfc_id):
    """The milestone numbers whose section mentions `rfc_id` (the RFC → milestone edges)."""
    return [num for num, _title, body in parse_milestones(text) if rfc_id in body]


def uncovered_rfcs(text, rfc_ids):
    """RFC ids no milestone references — the roadmap-covers-rfcs violations."""
    return [r for r in rfc_ids if not covering_milestones(text, r)]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 1:
        print("usage: traceability.py <roadmap.md> <RFC-id> [<RFC-id> ...]", file=sys.stderr)
        return 2
    roadmap_path, rfc_ids = argv[0], argv[1:]
    with open(roadmap_path, encoding="utf-8") as handle:
        text = handle.read()
    milestones = parse_milestones(text)
    print(f"roadmap: {len(milestones)} milestone(s); RFCs to cover: {len(rfc_ids)}")
    for rfc in rfc_ids:
        cov = covering_milestones(text, rfc)
        where = ", ".join(f"M{n}" for n in cov) if cov else "—"
        print(f"  {rfc} -> {where}")
    missing = uncovered_rfcs(text, rfc_ids)
    if missing:
        print("roadmap-covers-rfcs: FAIL — no milestone addresses:")
        for r in missing:
            print(f"  {r}")
        return 1
    if rfc_ids:
        print("roadmap-covers-rfcs: OK — every RFC is addressed by a milestone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
