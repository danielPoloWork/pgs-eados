#!/usr/bin/env python3
"""EADOS phase runner — the deterministic, state-driven checker behind `/eados <phase>`.

Given a project manifest, it reads `delivery_state.phase` and the workflow spec
(`orchestrator/os/workflow/workflow.yaml`) and prints the **legal next transitions** — each with
its entry gates and whether it needs human confirmation. It is the thin "engine" the RFC calls
for: a pure function over data. It **never advances state** — it reports what is legal; the agent
proposes a transition, the gates validate it, and the human confirms every human-gated step
(`AGENTS.md` §6).

Dependency-free: the Python standard library plus the sibling renderer's YAML loader.

    python .eados-core/tools/phase_runner.py <manifest>     # report the legal next transitions
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # .eados-core/
sys.path.insert(0, HERE)
import render  # noqa: E402  — the hand-rolled, dependency-free YAML loader (sibling tool)

WORKFLOW = os.path.join(ROOT, "orchestrator", "os", "workflow", "workflow.yaml")


def load_workflow(path=WORKFLOW):
    with open(path, encoding="utf-8") as handle:
        return render.load_yaml(handle.read())


def state_ids(workflow):
    return [s.get("id") for s in (workflow.get("states") or []) if isinstance(s, dict)]


def current_phase(manifest):
    """The manifest's current phase; defaults to `init` when there is no delivery_state yet
    (a legacy / freshly-initialized manifest)."""
    ds = manifest.get("delivery_state") if isinstance(manifest, dict) else None
    return ds.get("phase", "init") if isinstance(ds, dict) else "init"


def legal_transitions(workflow, phase):
    """The transitions whose `from` == phase, in declared order (deterministic)."""
    return [t for t in (workflow.get("transitions") or [])
            if isinstance(t, dict) and t.get("from") == phase]


def report(manifest_path, out=sys.stdout):
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = render.load_yaml(handle.read())
    workflow = load_workflow()
    states = state_ids(workflow)
    phase = current_phase(manifest)
    print(f"current phase: {phase}", file=out)
    if phase not in states:
        print(f"  ERROR: '{phase}' is not a declared workflow state {states}", file=out)
        return 1
    transitions = legal_transitions(workflow, phase)
    if not transitions:
        print("  (terminal phase — no outgoing transitions)", file=out)
        return 0
    print("legal next transitions:", file=out)
    for t in transitions:
        gates = ", ".join(t.get("entry_gates") or []) or "—"
        human = "  [human-gated — the owner confirms]" if t.get("human_gate") else ""
        print(f"  -> {t.get('to')}   (gates: {gates}){human}", file=out)
    return 0


def propose_transition(workflow, from_phase, to_phase):
    """The declared transition from_phase -> to_phase, or None if that move is not legal."""
    for t in legal_transitions(workflow, from_phase):
        if t.get("to") == to_phase:
            return t
    return None


def emit_checkpoint(from_phase, transition):
    """The delivery_state checkpoint the agent appends after a CONFIRMED transition. The runner
    returns it; the agent writes it to the manifest and the human confirms human-gated moves —
    the runner itself never writes state (reports, never advances)."""
    return {"from": from_phase, "to": transition.get("to"),
            "gates": transition.get("entry_gates") or []}


def report_propose(manifest_path, to_phase, out=sys.stdout):
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = render.load_yaml(handle.read())
    workflow = load_workflow()
    states = state_ids(workflow)
    frm = current_phase(manifest)
    print(f"proposed transition: {frm} -> {to_phase}", file=out)
    if to_phase not in states:
        print(f"  ILLEGAL: '{to_phase}' is not a declared workflow state {states}", file=out)
        return 1
    t = propose_transition(workflow, frm, to_phase)
    if t is None:
        legal = [x.get("to") for x in legal_transitions(workflow, frm)]
        print(f"  ILLEGAL: not a declared transition from '{frm}' (legal: {legal or 'none'})",
              file=out)
        return 1
    gates = ", ".join(t.get("entry_gates") or []) or "—"
    print(f"  LEGAL — gates to satisfy: {gates}; "
          f"human-gated: {'yes' if t.get('human_gate') else 'no'}", file=out)
    cp = emit_checkpoint(frm, t)
    print("  emit — append to delivery_state.checkpoints, then set delivery_state.phase:", file=out)
    print(f"    - {{ from: {cp['from']}, to: {cp['to']}, gates: {cp['gates']} }}", file=out)
    print(f"    phase: {to_phase}", file=out)
    return 0


def main(argv=None):
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser(description="EADOS phase runner — report or validate a transition.")
    ap.add_argument("manifest", help="path to a project manifest (project.yaml)")
    ap.add_argument("--propose", metavar="TO",
                    help="validate a proposed transition to phase TO and emit its checkpoint")
    args = ap.parse_args(argv)
    if args.propose:
        return report_propose(args.manifest, args.propose)
    return report(args.manifest)


if __name__ == "__main__":
    sys.exit(main())
