#!/usr/bin/env python3
"""EADOS doctor — the `/eados status` at-a-glance health readout (roadmap 6.4 / F1).

Read-only. For a project manifest it aggregates, in one place:
  - the **current phase** (+ its owning role and what it produces),
  - the **legal next transitions** (+ entry gates, human-gating) — via `phase_runner`,
  - the recorded cross-link **refs** (`rfcs` / `milestones`) from `delivery_state`,
  - **traceability** coverage — `roadmap-covers-rfcs` over `ROADMAP.md`, and `traceability-lint`
    when a links file is present — via `traceability`.

It reports; it never advances state or runs a phase. It exits 0 when healthy and **non-zero when it
finds an actionable problem** (an undeclared phase, an uncovered RFC, or a dangling traceability
edge), so it doubles as a pre-flight check. Dependency-free (stdlib + the sibling phase_runner /
traceability / render tools — one source of truth, never a re-implementation).

    python .eados-core/tools/doctor.py <manifest> [--root DIR] [--roadmap PATH] [--links PATH]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render          # noqa: E402  — the hand-rolled YAML loader
import phase_runner    # noqa: E402  — current phase + legal transitions (the deterministic engine)
import traceability    # noqa: E402  — coverage + dangling-edge checks


def _state(workflow, phase):
    for s in workflow.get("states") or []:
        if isinstance(s, dict) and s.get("id") == phase:
            return s
    return None


def status_report(manifest, workflow, roadmap_text=None, links=None):
    """Build the readout. Returns (lines, healthy): `lines` is the printable report; `healthy` is
    False on a structural problem (phase not a declared state) or an actionable one (an uncovered
    RFC, a dangling traceability edge). Neutral conditions (no roadmap, no refs) stay healthy."""
    lines, healthy = [], True
    phase = phase_runner.current_phase(manifest)
    states = phase_runner.state_ids(workflow)
    ds = manifest.get("delivery_state") if isinstance(manifest, dict) else None
    refs = (ds.get("refs") or {}) if isinstance(ds, dict) else {}
    rfcs = list(refs.get("rfcs") or [])
    milestones = list(refs.get("milestones") or [])

    st = _state(workflow, phase)
    if st is None:
        lines.append(f"phase: {phase}   ERROR: not a declared workflow state {states}")
        return lines, False
    lines.append(f"phase: {phase}   (role: {st.get('role', '-')}; "
                 f"produces: {', '.join(st.get('produces') or []) or '-'})")

    transitions = phase_runner.legal_transitions(workflow, phase)
    if transitions:
        lines.append("legal next transitions:")
        for t in transitions:
            gates = ", ".join(t.get("entry_gates") or []) or "-"
            human = "  [human-gated]" if t.get("human_gate") else ""
            lines.append(f"  -> {t.get('to')}   (gates: {gates}){human}")
    else:
        lines.append("legal next transitions: none (terminal phase)")

    lines.append(f"refs: rfcs={rfcs or '-'}; milestones={milestones or '-'}")

    if roadmap_text is None:
        lines.append("traceability: no ROADMAP.md found - coverage not checked")
    elif not rfcs:
        lines.append("traceability: no RFC refs recorded - nothing to cover")
    else:
        uncovered = traceability.uncovered_rfcs(roadmap_text, rfcs)
        if uncovered:
            lines.append(f"roadmap-covers-rfcs: FAIL - uncovered: {', '.join(uncovered)}")
            healthy = False
        else:
            cov = "; ".join(
                f"{r} -> {', '.join('M' + m for m in traceability.covering_milestones(roadmap_text, r))}"
                for r in rfcs)
            lines.append(f"roadmap-covers-rfcs: OK ({cov})")
        if links is not None:
            problems = traceability.traceability_lint(roadmap_text, rfcs, links)
            if problems:
                lines.append(f"traceability-lint: FAIL - {len(problems)} dangling edge(s)")
                healthy = False
            else:
                lines.append("traceability-lint: OK - the graph is whole")
        else:
            lines.append("traceability-lint: skipped (no links file)")

    return lines, healthy


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="EADOS doctor - /eados status at-a-glance readout.")
    ap.add_argument("manifest", help="path to a project manifest (project.yaml)")
    ap.add_argument("--root", help="project root for ROADMAP.md / links (default: the manifest's dir)")
    ap.add_argument("--roadmap", help="path to ROADMAP.md (default: <root>/ROADMAP.md)")
    ap.add_argument("--links", help="traceability links file (default: <root>/links.yaml if present)")
    args = ap.parse_args(argv)

    manifest = render.load_yaml(_read(args.manifest))
    workflow = phase_runner.load_workflow()

    root = args.root or os.path.dirname(os.path.abspath(args.manifest))
    roadmap_path = args.roadmap or os.path.join(root, "ROADMAP.md")
    roadmap_text = _read(roadmap_path) if os.path.isfile(roadmap_path) else None
    links_path = args.links or os.path.join(root, "links.yaml")
    links = (render.load_yaml(_read(links_path)) or {}).get("links") if os.path.isfile(links_path) else None

    lines, healthy = status_report(manifest, workflow, roadmap_text, links)
    print(f"EADOS status - {args.manifest}")
    for line in lines:
        print(f"  {line}")
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
