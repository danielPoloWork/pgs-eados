#!/usr/bin/env python3
"""Tests for the cross-spec-consistency gate (eados_lint check #11) — referential integrity
ACROSS the delivery-OS specs. Pure-function tests on cross_spec_problems() with in-memory
fixtures: a complete clean spec set has no problems, and every kind of dangling cross-reference
(role / state / gate / overlay / level / domain) is caught. Dependency-free.

    python .eados-core/tools/tests/test_cross_spec.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import eados_lint as el  # noqa: E402  (the module under test)


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def clean():
    """A minimal but COMPLETE spec set in which every cross-reference resolves."""
    authority = {
        "roles": [{"name": "tech-lead"}, {"name": "producer"}, {"name": "product-manager"},
                  {"name": "security-auditor"}, {"name": "enterprise-architect"}],
        "ownership_map": [{"glob": "src/**", "role": "tech-lead", "action": "approve"}],
        "escalation": [{"level": 1, "decider": "tech-lead"},
                       {"level": 2, "decider": "human-owner"}],   # terminal, not a role
    }
    workflow = {
        "states": [{"id": "design", "role": "tech-lead"}, {"id": "plan", "role": "producer"},
                   {"id": "scaffold", "role": "enterprise-architect"}],
        "transitions": [{"from": "design", "to": "plan", "entry_gates": ["rfc-approved"]},
                        {"from": "plan", "to": "scaffold", "entry_gates": ["roadmap-covers-rfcs"]}],
        "gates": [{"id": "rfc-approved", "required_for": ["plan"]},
                  {"id": "roadmap-covers-rfcs", "required_for": ["scaffold"]}],
        "domain_overlays": {"software": {}, "game": {"add_gates": ["hardware-budget"]}},
    }
    plan = {"roles": {"proposes": "product-manager", "sizes": "tech-lead",
                      "reconciles": "producer"}, "gate": "roadmap-covers-rfcs"}
    rfc = {"author_roles": ["tech-lead"], "reviewer_roles": ["enterprise-architect"],
           "approver_role": "tech-lead", "gate": "rfc-approved"}
    risk = {"levels": ["low", "medium", "high"], "mandatory_gate_level": "high",
            "domain_overrides": {"game": {"mandatory_gate_level": "high"}}}
    domains = {
        "software.yaml": {"domain": "software", "roles": ["tech-lead", "producer"],
                          "role_labels": {"product-manager": "product-manager"},
                          "workflow_overlay": "software"},
        "game.yaml": {"domain": "game", "roles": ["tech-lead"], "workflow_overlay": "game"},
    }
    return authority, workflow, plan, rfc, risk, domains


def main():
    failures = []

    check("a complete clean spec set has no cross-spec problems",
          el.cross_spec_problems(*clean()) == [], failures)

    def caught(mutate, needle):
        """True if mutating a fresh clean set produces a problem mentioning `needle`."""
        a, w, p, r, rk, d = clean()
        mutate(a, w, p, r, rk, d)
        return any(needle in prob for prob in el.cross_spec_problems(a, w, p, r, rk, d))

    # The three failure modes the review named explicitly.
    check("a misspelled plan negotiation role is caught (tech-led)",
          caught(lambda a, w, p, r, rk, d: p["roles"].__setitem__("sizes", "tech-led"),
                 "tech-led"), failures)
    check("a phantom gate in a transition is caught",
          caught(lambda a, w, p, r, rk, d: w["transitions"][0].__setitem__(
              "entry_gates", ["ghost-gate"]), "ghost-gate"), failures)
    check("a dangling domain workflow_overlay is caught",
          caught(lambda a, w, p, r, rk, d: d["game.yaml"].__setitem__(
              "workflow_overlay", "nope"), "nope"), failures)

    # Every other cross-reference kind.
    check("an unknown transition target state is caught",
          caught(lambda a, w, p, r, rk, d: w["transitions"][0].__setitem__("to", "limbo"),
                 "limbo"), failures)
    check("an unknown state-owner role is caught",
          caught(lambda a, w, p, r, rk, d: w["states"][0].__setitem__("role", "ghost-role"),
                 "ghost-role"), failures)
    check("an unknown gate.required_for state is caught",
          caught(lambda a, w, p, r, rk, d: w["gates"][0].__setitem__("required_for", ["nowhere"]),
                 "nowhere"), failures)
    check("an unknown ownership_map role is caught",
          caught(lambda a, w, p, r, rk, d: w and a["ownership_map"][0].__setitem__("role", "nobody"),
                 "nobody"), failures)
    check("an unknown escalation decider is caught",
          caught(lambda a, w, p, r, rk, d: a["escalation"][0].__setitem__("decider", "wizard"),
                 "wizard"), failures)
    check("an unknown rfc approver role is caught",
          caught(lambda a, w, p, r, rk, d: r.__setitem__("approver_role", "phantom"),
                 "phantom"), failures)
    check("an unknown risk gate level is caught",
          caught(lambda a, w, p, r, rk, d: rk.__setitem__("mandatory_gate_level", "spicy"),
                 "spicy"), failures)
    check("a domain role missing from the authority model is caught",
          caught(lambda a, w, p, r, rk, d: d["software.yaml"].__setitem__(
              "roles", ["tech-lead", "ghost"]), "ghost"), failures)

    # No false positives: a gate DEFINED by a domain overlay (add_gates) is a legitimate id.
    a, w, p, r, rk, d = clean()
    w["transitions"][1]["entry_gates"] = ["hardware-budget"]   # defined via the game overlay
    check("an overlay-defined gate (add_gates) is accepted, not flagged",
          el.cross_spec_problems(a, w, p, r, rk, d) == [], failures)

    # Robustness: a missing/unparseable core spec is left to os-spec-completeness, not double-reported.
    check("a None workflow yields no problems (deferred to os-spec-completeness)",
          el.cross_spec_problems(clean()[0], None) == [], failures)

    if failures:
        print("test-cross-spec: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} expectation(s) failed.")
        return 1
    print("test-cross-spec: OK -- cross-spec references resolve; every dangling kind is caught.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
