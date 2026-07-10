#!/usr/bin/env python3
"""EADOS thin phase orchestrator (roadmap 6.5 / G3) — the executable counterpart to `/eados <phase>`.

`/eados <phase>` is a markdown *procedure* an agent reads ([`commands/`](../orchestrator/commands/)).
This is the deterministic spine underneath it: `eados.py <phase> <manifest>` runs that phase's
**outgoing-transition entry gates** — the gates you must satisfy to leave the phase, read straight
from [`workflow.yaml`](../orchestrator/os/workflow/workflow.yaml) (knowledge as data, no hardcoded
chain) — evaluating the ones it can compute from the project (`manifest-valid`, `rfc-approved`,
`roadmap-covers-rfcs`) and marking the rest `[manual]` / `[needs-input]`. It then prints the legal
next transitions and points at the procedure for the authoring + human-gated steps. `eados.py status`
is the read-only doctor ([`doctor.py`](doctor.py)).

It reports and gates; it never authors an artifact, advances state, or runs a phase tool that writes.
Exit 0 unless a deterministic gate FAILs (or the phase is undeclared). Dependency-free (stdlib + the
sibling tools — one source of truth, never a re-implementation).

    python .eados-core/tools/eados.py <phase|status> <manifest> [--rfc P] [--roadmap P] [--links P] [--strict] [--root D]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render          # noqa: E402  — YAML loader + manifest validation (manifest-valid)
import phase_runner    # noqa: E402  — workflow + legal transitions (the deterministic engine)
import traceability    # noqa: E402  — roadmap-covers-rfcs
import rfc_check        # noqa: E402  — rfc-approved
import doctor          # noqa: E402  — the `status` readout (reused, not re-implemented)

PHASES = ("init", "design", "plan", "scaffold", "audit", "migrate")


def _rfcs(manifest):
    ds = manifest.get("delivery_state") if isinstance(manifest, dict) else None
    refs = (ds.get("refs") or {}) if isinstance(ds, dict) else {}
    return list(refs.get("rfcs") or [])


# --- gate evaluators: each returns (mark, detail). mark ∈ {OK, FAIL, skipped, needs-input}. -----
#     skipped     = the input is genuinely not applicable (nothing to check yet).
#     needs-input = a CHECKABLE input is missing — the project HAS something to verify, but the
#                   caller withheld the file/refs. Under --strict it fails the phase (#200), so a
#                   gate can no longer be satisfied by omission (EADOS's fail-closed posture).
def _ev_manifest_valid(manifest, ctx):
    scalars, _f, _s = render.build_context(manifest)
    problems = render.validate_manifest(manifest, scalars)
    return ("FAIL", f"{len(problems)} problem(s) (e.g. {problems[0]})") if problems else ("OK", "")


def _ev_rfc_approved(manifest, ctx):
    if ctx.get("rfc_text") is None:
        if _rfcs(manifest):
            return ("needs-input", "delivery_state records RFC refs but no --rfc <path> was given — "
                    "the rfc-approved check cannot run (withholding the file must not pass the gate)")
        return ("skipped", "no RFC refs recorded yet; provide --rfc <path> once an RFC exists")
    problems = rfc_check.check_rfc(ctx["rfc_text"], rfc_check.load_protocol())
    return ("FAIL", problems[0]) if problems else ("OK", "")


def _ev_roadmap_covers(manifest, ctx):
    rfcs = _rfcs(manifest)
    if not rfcs:
        return ("needs-input", "no RFC refs recorded in delivery_state — record them so coverage "
                "can be checked (withholding refs must not silently satisfy the gate)")
    if ctx.get("roadmap_text") is None:
        return ("needs-input", "no ROADMAP.md found — coverage of the recorded RFCs cannot be checked")
    uncovered = traceability.uncovered_rfcs(ctx["roadmap_text"], rfcs)
    return ("FAIL", f"uncovered: {', '.join(uncovered)}") if uncovered else ("OK", "")


GATE_EVALUATORS = {
    "manifest-valid": _ev_manifest_valid,
    "rfc-approved": _ev_rfc_approved,
    "roadmap-covers-rfcs": _ev_roadmap_covers,
}

# The procedure a phase points at for its authoring + human-gated steps.
PROCEDURE = {p: f"orchestrator/commands/{p}.md" for p in PHASES}
PROCEDURE["scaffold"] = "orchestrator/generate.md"


def evaluate_gates(gate_ids, manifest, ctx):
    """{gate id -> mark} for `gate_ids`: the in-process gates (GATE_EVALUATORS) evaluated over the
    project, the rest marked `manual` (run by the phase procedure / CI / a human). One source of
    truth for the deterministic marks — run_phase's display and the checkpoint's LIVE gate_results
    (#213) both resolve a gate through GATE_EVALUATORS, so the two can never diverge."""
    out = {}
    for g in gate_ids:
        evaluator = GATE_EVALUATORS.get(g)
        out[g] = evaluator(manifest, ctx or {})[0] if evaluator else "manual"
    return out


def run_phase(phase, manifest, workflow, roadmap_text=None, rfc_text=None, strict=False):
    """Run `phase`'s deterministic outgoing gates over the project. Returns (lines, ok): `ok` is
    False when a gate the orchestrator can evaluate FAILs (manual/skipped never fail), or — under
    `strict` (#200) — when a gate is `needs-input` (a checkable input was withheld), so a gate can
    no longer be satisfied by omission. The phase not being a declared state is also not-ok."""
    ctx = {"roadmap_text": roadmap_text, "rfc_text": rfc_text}
    states = phase_runner.state_ids(workflow)
    if phase not in states:
        return [f"'{phase}' is not a declared workflow state {states}"], False

    lines, ok = [], True
    transitions = phase_runner.legal_transitions(workflow, phase)
    gates = []
    for t in transitions:
        for g in t.get("entry_gates") or []:
            if g not in gates:
                gates.append(g)

    if gates:
        lines.append(f"gates to leave '{phase}':")
        for g in gates:
            evaluator = GATE_EVALUATORS.get(g)
            if evaluator is None:
                lines.append(f"  [manual] {g} (run it in the procedure; needs a rendered repo or a "
                             "human decision)")
                continue
            mark, detail = evaluator(manifest, ctx)
            lines.append(f"  [{mark}] {g}" + (f" - {detail}" if detail else ""))
            if mark == "FAIL" or (mark == "needs-input" and strict):
                ok = False
    else:
        lines.append(f"phase '{phase}': terminal — no outgoing gates")

    if transitions:
        lines.append("legal next transitions:")
        for t in transitions:
            gs = ", ".join(t.get("entry_gates") or []) or "-"
            human = "  [human-gated]" if t.get("human_gate") else ""
            lines.append(f"  -> {t.get('to')}   (gates: {gs}){human}")
    else:
        lines.append("(terminal phase — no outgoing transitions)")

    lines.append(f"next: {PROCEDURE.get(phase, '?')} — the authoring + human-gated steps.")
    return lines, ok


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv=None):
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser(description="EADOS thin phase orchestrator - run a phase's "
                                             "deterministic gates, or `status` for the doctor.")
    ap.add_argument("command", choices=PHASES + ("status",),
                    help="a phase (init|design|plan|scaffold|audit|migrate) or 'status'")
    ap.add_argument("manifest", help="path to a project manifest (project.yaml)")
    ap.add_argument("--root", help="project root for ROADMAP.md / links (default: the manifest's dir)")
    ap.add_argument("--roadmap", help="path to ROADMAP.md (default: <root>/ROADMAP.md)")
    ap.add_argument("--links", help="traceability links file (default: <root>/links.yaml if present)")
    ap.add_argument("--rfc", help="an RFC file to check for the rfc-approved gate (design)")
    ap.add_argument("--strict", action="store_true",
                    help="fail the phase on a needs-input gate too (a checkable input was withheld) "
                         "— the fail-closed posture for CI; skipped (not applicable) still passes")
    args = ap.parse_args(argv)

    try:
        manifest = render.load_yaml(_read(args.manifest))
    except (OSError, ValueError) as exc:
        print(f"eados: cannot read manifest {args.manifest!r}: {exc}", file=sys.stderr)
        return 2
    workflow = phase_runner.apply_overlay(phase_runner.load_workflow(),
                                          phase_runner.manifest_domain(manifest))
    root = args.root or os.path.dirname(os.path.abspath(args.manifest))
    roadmap_path = args.roadmap or os.path.join(root, "ROADMAP.md")
    roadmap_text = _read(roadmap_path) if os.path.isfile(roadmap_path) else None
    links_path = args.links or os.path.join(root, "links.yaml")
    links = (render.load_yaml(_read(links_path)) or {}).get("links") if os.path.isfile(links_path) else None
    rfc_text = _read(args.rfc) if args.rfc else None

    if args.command == "status":
        lines, ok = doctor.status_report(manifest, workflow, roadmap_text, links)
    else:
        lines, ok = run_phase(args.command, manifest, workflow, roadmap_text, rfc_text,
                              strict=args.strict)

    # #214: surface the optimistic-concurrency counter the readout validated against, so a caller
    # can pass it to `phase_runner --propose --expect-rev N` before writing.
    print(f"EADOS {args.command} - {args.manifest}  (manifest_rev {phase_runner.manifest_rev(manifest)})")
    for line in lines:
        print(f"  {line}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
