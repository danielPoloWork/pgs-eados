#!/usr/bin/env python3
"""Tests for the EADOS phase runner — the legal-transition checker is correct, pure, and the
workflow spec is internally consistent. Dependency-free (runnable in the self-lint job).

    python .eados-core/tools/tests/test_phase_runner.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import phase_runner as pr  # noqa: E402  (the module under test)


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def main():
    failures = []
    wf = pr.load_workflow()

    # --- current_phase: defaults to init; reads delivery_state when present ---
    check("current_phase default init", pr.current_phase({}) == "init", failures)
    check("current_phase reads delivery_state",
          pr.current_phase({"delivery_state": {"phase": "plan"}}) == "plan", failures)
    check("current_phase tolerates malformed delivery_state",
          pr.current_phase({"delivery_state": "oops"}) == "init", failures)

    # --- legal_transitions: the entry phase ---
    init = pr.legal_transitions(wf, "init")
    check("init -> exactly one transition", len(init) == 1, failures)
    check("init -> design", init and init[0].get("to") == "design", failures)
    check("init -> design is human-gated", init and init[0].get("human_gate") is True, failures)
    check("init -> design gate is manifest-valid",
          init and init[0].get("entry_gates") == ["manifest-valid"], failures)

    # --- plan is a fork: forward to scaffold + resumable back to design ---
    plan = {t.get("to") for t in pr.legal_transitions(wf, "plan")}
    check("plan -> {scaffold, design}", plan == {"scaffold", "design"}, failures)

    # --- scaffold -> audit is automatic (not human-gated; the gates are mechanical) ---
    sc = pr.legal_transitions(wf, "scaffold")
    check("scaffold -> audit, not human-gated",
          sc and sc[0].get("to") == "audit" and not sc[0].get("human_gate"), failures)

    # --- refactor is terminal ---
    check("refactor is terminal", pr.legal_transitions(wf, "refactor") == [], failures)

    # --- an unknown phase yields no transitions (report() flags it; the function is total) ---
    check("unknown phase -> no transitions", pr.legal_transitions(wf, "bogus") == [], failures)

    # --- workflow integrity: every transition endpoint is a declared state ---
    states = set(pr.state_ids(wf))
    for t in wf.get("transitions") or []:
        check(f"transition from '{t.get('from')}' is a declared state",
              t.get("from") in states, failures)
        check(f"transition to '{t.get('to')}' is a declared state",
              t.get("to") in states, failures)

    # --- #165: domain overlays are applied by apply_overlay, data-driven from the registry ---
    check("manifest_domain defaults to software", pr.manifest_domain({}) == "software", failures)
    check("manifest_domain reads the top-level scalar",
          pr.manifest_domain({"domain": "game"}) == "game", failures)
    merged = pr.apply_overlay(wf, "game")
    check("game overlay appends asset-pipeline-review as a human-owner state",
          any(isinstance(s, dict) and s.get("id") == "asset-pipeline-review"
              and s.get("role") == "human-owner" for s in merged.get("states") or []), failures)
    sc_m = pr.legal_transitions(merged, "scaffold")
    check("game overlay gates scaffold -> audit with hardware-budget",
          sc_m and "hardware-budget" in (sc_m[0].get("entry_gates") or []), failures)
    check("the applied overlay is recorded for the doctor",
          (merged.get("applied_overlay") or {}).get("domain") == "game", failures)
    check("the base workflow object is not mutated",
          "hardware-budget" not in (pr.legal_transitions(wf, "scaffold")[0].get("entry_gates") or [])
          and "asset-pipeline-review" not in pr.state_ids(wf), failures)
    web = pr.apply_overlay(wf, "web")
    check("web overlay gates the audit entry with both web gates",
          all(g in (pr.legal_transitions(web, "scaffold")[0].get("entry_gates") or [])
              for g in ("accessibility-review", "web-vitals-budget")), failures)
    check("software is a pass-through (same object, byte-identical machine)",
          pr.apply_overlay(wf, "software") is wf, failures)
    check("an unknown domain is a pass-through", pr.apply_overlay(wf, "quantum") is wf, failures)

    # --- propose_transition: legal vs illegal, and the emitted checkpoint (M2-C) ---
    legal = pr.propose_transition(wf, "init", "design")
    check("propose init->design is legal", legal is not None, failures)
    check("propose init->scaffold is illegal (skips the pipeline)",
          pr.propose_transition(wf, "init", "scaffold") is None, failures)
    check("propose plan->design is legal (resumable)",
          pr.propose_transition(wf, "plan", "design") is not None, failures)
    cp = pr.emit_checkpoint("init", legal)
    check("checkpoint records from/to", cp["from"] == "init" and cp["to"] == "design", failures)
    check("checkpoint carries the entry gates", cp["gates"] == ["manifest-valid"], failures)

    # --- #199: the checkpoint now carries evidence — a date, and a confirmed_by on a human-gated
    #     move (a <owner> placeholder the human fills). A non-human-gated move carries none. ---
    cp_h = pr.emit_checkpoint("init", legal, at="2026-07-06")
    check("enriched checkpoint records the transition date", cp_h.get("at") == "2026-07-06", failures)
    check("a human-gated checkpoint carries a confirmed_by placeholder",
          cp_h.get("confirmed_by") == "<owner>", failures)
    auto = pr.emit_checkpoint("scaffold", pr.propose_transition(wf, "scaffold", "audit"))
    check("a non-human-gated checkpoint carries no confirmed_by", "confirmed_by" not in auto, failures)

    # --- #199: checkpoint_chain_problems — a legal contiguous chain ending at the current phase is
    #     clean; a phase-skip, illegal edge, broken chain, missing confirmed_by, a failing
    #     gate_result, and phase != chain-end are each rejected (the honor-system gap is closed) ---
    def ds(phase, cps):
        return {"delivery_state": {"phase": phase, "checkpoints": cps}}
    legal_chain = [{"from": "init", "to": "design", "confirmed_by": "owner"},
                   {"from": "design", "to": "plan", "confirmed_by": "owner"}]
    check("a legal contiguous chain ending at the current phase is clean",
          pr.checkpoint_chain_problems(ds("plan", legal_chain), wf) == [], failures)
    check("a legacy manifest with no delivery_state is exempt",
          pr.checkpoint_chain_problems({"identity": {}}, wf) == [], failures)
    check("an init phase with no checkpoints is fine",
          pr.checkpoint_chain_problems(ds("init", []), wf) == [], failures)
    check("phase: scaffold with no checkpoints is a rejected phase-skip",
          any("no checkpoints" in p for p in pr.checkpoint_chain_problems(ds("scaffold", []), wf)),
          failures)
    check("an illegal edge (init -> scaffold) is rejected",
          any("not a legal transition" in p for p in pr.checkpoint_chain_problems(
              ds("scaffold", [{"from": "init", "to": "scaffold", "confirmed_by": "o"}]), wf)), failures)
    check("a non-contiguous chain is rejected",
          any("not contiguous" in p for p in pr.checkpoint_chain_problems(
              ds("scaffold", [{"from": "init", "to": "design", "confirmed_by": "o"},
                              {"from": "plan", "to": "scaffold", "confirmed_by": "o"}]), wf)), failures)
    check("a human-gated move without confirmed_by is rejected",
          any("confirmed_by" in p for p in pr.checkpoint_chain_problems(
              ds("design", [{"from": "init", "to": "design"}]), wf)), failures)
    check("a phase that is not the chain's end is rejected",
          any("ends at" in p for p in pr.checkpoint_chain_problems(ds("scaffold", legal_chain), wf)),
          failures)
    check("a recorded failing gate_result is rejected",
          any("may not be taken" in p for p in pr.checkpoint_chain_problems(
              ds("design", [{"from": "init", "to": "design", "confirmed_by": "o",
                             "gate_results": {"manifest-valid": "FAIL"}}]), wf)), failures)

    if failures:
        print("test-phase-runner: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} expectation(s) failed.")
        return 1
    print("test-phase-runner: OK — legal transitions, terminal phase, and workflow integrity hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
