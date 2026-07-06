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

import copy
import datetime
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


def manifest_domain(manifest):
    """The manifest's target domain (the top-level `domain` scalar); `software` when absent."""
    dom = manifest.get("domain") if isinstance(manifest, dict) else None
    return dom.strip() if isinstance(dom, str) and dom.strip() else "software"


def apply_overlay(workflow, domain):
    """The workflow adapted to `domain` (#165): `domain_overlays[<domain>]` merged into a deep
    copy. `insert_states` are appended as human-owner states (no automated role exists for them),
    and each `add_gates` id joins the entry_gates of every transition into a state its REGISTRY
    entry names in `required_for` — the registry, not code, says where a domain gate bites
    (cross-spec lint guarantees every add_gates id has an entry). The merge is recorded under
    `applied_overlay` so the doctor can surface it. A domain with no overlay effects (`software`,
    absent, unknown) returns the SAME object, so the base machine stays byte-identical."""
    overlays = workflow.get("domain_overlays") if isinstance(workflow, dict) else None
    ov = overlays.get(domain) if isinstance(overlays, dict) else None
    if not isinstance(ov, dict) or not (ov.get("insert_states") or ov.get("add_gates")):
        return workflow
    merged = copy.deepcopy(workflow)
    inserted = [s for s in (ov.get("insert_states") or []) if isinstance(s, str)]
    added = [g for g in (ov.get("add_gates") or []) if isinstance(g, str)]
    for sid in inserted:
        merged.setdefault("states", []).append(
            {"id": sid, "role": "human-owner", "produces": [], "overlay": domain})
    required = {g.get("id"): (g.get("required_for") or [])
                for g in (merged.get("gates") or []) if isinstance(g, dict)}
    for gid in added:
        for t in (merged.get("transitions") or []):
            if isinstance(t, dict) and t.get("to") in required.get(gid, []):
                entry = t.setdefault("entry_gates", [])
                if gid not in entry:
                    entry.append(gid)
    merged["applied_overlay"] = {"domain": domain, "insert_states": inserted, "add_gates": added}
    return merged


def report(manifest_path, out=sys.stdout):
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = render.load_yaml(handle.read())
    workflow = apply_overlay(load_workflow(), manifest_domain(manifest))
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


def emit_checkpoint(from_phase, transition, at=None, confirmed_by=None, gate_results=None):
    """The delivery_state checkpoint the agent appends after a CONFIRMED transition: the transition
    edge (`from`/`to`), the declared `gates`, the date `at`, and — for a human-gated move —
    `confirmed_by` (who approved it; a `<owner>` placeholder the human fills in). `gate_results`
    (gate id -> OK/manual) is recorded only when the caller evaluated the gates; wiring that live
    evaluation lands with the audit-trail work (#203), and `checkpoint_chain_problems` already
    validates it when present. The runner returns the checkpoint; the agent writes it and the human
    confirms human-gated moves — the runner itself never writes state (reports, never advances)."""
    cp = {"from": from_phase, "to": transition.get("to"),
          "gates": transition.get("entry_gates") or [],
          "at": at or datetime.date.today().isoformat()}
    if transition.get("human_gate"):
        cp["confirmed_by"] = confirmed_by or "<owner>"
    if gate_results is not None:
        cp["gate_results"] = gate_results
    return cp


_CHECKPOINT_OK_MARKS = ("OK", "manual")


def checkpoint_chain_problems(manifest, workflow):
    """Validate `delivery_state.checkpoints` as a legal, contiguous transition chain through the
    (overlay-applied) `workflow`, ending at the current `phase`. This closes the honor-system gap
    (#199): a hallucinating or shortcut-taking agent can no longer set `phase: scaffold` without the
    intervening `init -> design -> plan -> scaffold` checkpoints. Rules:

      * a legacy manifest with no `delivery_state` is exempt (backward-compat, M1-B);
      * `checkpoints` must be a list; each item a `{from, to}` mapping;
      * every `{from, to}` must be a declared transition, and each must continue from the previous
        checkpoint's `to` (the chain is contiguous, rooted at `init`);
      * a human-gated transition (`human_gate: true`) must carry a `confirmed_by:` — mechanical
        evidence a human approved it, not the agent's narrative;
      * a recorded `gate_results` (when present) must be all `OK`/`manual` — a transition taken over
        a failing gate is illegal;
      * the last checkpoint's `to` must equal the current `phase`; with no checkpoints the phase
        must still be `init`.

    Pure — no I/O. Returns a list of problem strings (empty == consistent)."""
    ds = manifest.get("delivery_state") if isinstance(manifest, dict) else None
    if not isinstance(ds, dict):
        return []                                # no delivery_state — nothing to enforce (legacy)
    phase = ds.get("phase", "init")
    checkpoints = ds.get("checkpoints")
    if checkpoints is None:
        checkpoints = []
    if not isinstance(checkpoints, list):
        return ["delivery_state.checkpoints must be a list of {from, to} transitions"]

    problems, prev_to = [], "init"
    for i, cp in enumerate(checkpoints):
        if not isinstance(cp, dict):
            problems.append(f"delivery_state.checkpoints[{i}] must be a {{from, to}} mapping")
            continue
        frm, to = cp.get("from"), cp.get("to")
        if frm != prev_to:
            problems.append(f"delivery_state.checkpoints[{i}] starts at '{frm}' but the previous "
                            f"state is '{prev_to}' — the checkpoint chain is not contiguous")
        transition = propose_transition(workflow, frm, to)
        if transition is None:
            problems.append(f"delivery_state.checkpoints[{i}] '{frm} -> {to}' is not a legal "
                            "transition in the workflow")
        else:
            if transition.get("human_gate") and not str(cp.get("confirmed_by") or "").strip():
                problems.append(f"delivery_state.checkpoints[{i}] '{frm} -> {to}' is human-gated "
                                "and needs a 'confirmed_by:' entry (who approved the move)")
            results = cp.get("gate_results")
            if isinstance(results, dict):
                for gate, mark in results.items():
                    if str(mark).strip() not in _CHECKPOINT_OK_MARKS:
                        problems.append(f"delivery_state.checkpoints[{i}] '{frm} -> {to}' records "
                                        f"gate '{gate}' as {mark!r} — a transition may not be taken "
                                        f"over a gate that is not {' / '.join(_CHECKPOINT_OK_MARKS)}")
        if to is not None:
            prev_to = to
    if checkpoints:
        if prev_to != phase:
            problems.append(f"delivery_state.phase is '{phase}' but the checkpoint chain ends at "
                            f"'{prev_to}' — the current phase must be the last transition's target")
    elif phase != "init":
        problems.append(f"delivery_state.phase is '{phase}' but there are no checkpoints — a "
                        "non-init phase must record the transitions that reached it (no phase-skip)")
    return problems


def report_propose(manifest_path, to_phase, out=sys.stdout):
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = render.load_yaml(handle.read())
    workflow = apply_overlay(load_workflow(), manifest_domain(manifest))
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
    confirmed = f", confirmed_by: {cp['confirmed_by']}" if "confirmed_by" in cp else ""
    print(f"    - {{ from: {cp['from']}, to: {cp['to']}, gates: {cp['gates']}, "
          f"at: {cp['at']}{confirmed} }}", file=out)
    print(f"    phase: {to_phase}", file=out)
    if "confirmed_by" in cp:
        print("    (human-gated — replace <owner> in confirmed_by with who approved the move)",
              file=out)
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
    try:
        if args.propose:
            return report_propose(args.manifest, args.propose)
        return report(args.manifest)
    except (OSError, ValueError) as exc:
        print(f"phase-runner: cannot read manifest {args.manifest!r}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
