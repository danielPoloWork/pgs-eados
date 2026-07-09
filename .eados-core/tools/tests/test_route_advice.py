#!/usr/bin/env python3
"""Tests for route_advice (M16 16.2) — the routing-policy evaluator core, on an in-memory fixture
spec AND the real shipped `os/routing/routing.yaml`. Exercises monotonic escalation (floor, raises,
order-independence), the loud rejection of a spec that breaks its own `_schema.md` invariants
(unknown tier/effort/flag, a host missing a tier), host/catalog resolution, effort-alias
normalization, and the advisory boundary. The `gh` shell is not touched. Dependency-free.

    python .eados-core/tools/tests/test_route_advice.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import route_advice as ra        # noqa: E402  (the module under test)


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def fixture_spec():
    """A minimal well-formed spec, structurally parallel to the shipped instance."""
    return {
        "version": 1,
        "tiers": ["fast", "standard", "frontier-reasoning"],
        "efforts": ["low", "medium", "high", "max"],
        "flags": {"sets-pattern": "first of its class", "decision-heavy": "the decision is the deliverable"},
        "defaults": {"tier": "fast", "effort": "low"},
        "rules": [
            {"id": "sev-med", "when": ["label:severity:medium"],
             "min_tier": "standard", "min_effort": "medium", "why": "significant gap"},
            {"id": "sev-high", "when": ["label:severity:high"],
             "min_tier": "standard", "min_effort": "high", "why": "core guarantee"},
            {"id": "adr", "when": ["label:adr"],
             "min_tier": "frontier-reasoning", "min_effort": "high", "why": "decision-heavy by definition"},
            {"id": "pattern", "when": ["flag:sets-pattern"],
             "min_tier": "frontier-reasoning", "min_effort": "high", "why": "fixes the template"},
            {"id": "foundational", "when": ["flag:decision-heavy", "label:severity:high"],
             "min_tier": "frontier-reasoning", "min_effort": "max", "why": "most expensive artifact"},
        ],
        "catalog": {
            "as_of": "2026-07-09",
            "hosts": [
                {"host": "claude-code",
                 "models": {"frontier-reasoning": "Fable 5", "standard": "Opus 4.8", "fast": "Sonnet 5"},
                 "effort_aliases": {"ultracode": "max"}},
                {"host": "other-host",
                 "models": {"frontier-reasoning": "X-large", "standard": "X-mid", "fast": "X-small"}},
            ],
        },
        "examples": {"verdicts": ["fast", "standard", "frontier-reasoning"], "cases": []},
    }


def main():
    failures = []
    spec = fixture_spec()

    # --- the fixture and the SHIPPED spec both satisfy the _schema invariants ---
    check("fixture spec is invariant-clean", ra.spec_problems(spec) == [], failures)
    shipped = ra.load_routing()          # raises (test fails loudly) if the shipped spec broke
    check("shipped routing.yaml loads under loud rejection", isinstance(shipped, dict), failures)

    # --- monotonic escalation: floor, single raise, max-of-matches, order-independence ---
    adv = ra.advise([], spec)
    check("no signals -> the floor (fast/low)",
          (adv["tier"], adv["effort"]) == ("fast", "low"), failures)
    check("the floor names the first catalog host's model",
          adv["model"] == "Sonnet 5" and adv["host"] == "claude-code", failures)
    check("no-match advice reports the floor", adv["matched"] == [], failures)

    adv = ra.advise(ra.signals_for(["severity:medium"], [], spec), spec)
    check("severity:medium -> standard/medium",
          (adv["tier"], adv["effort"]) == ("standard", "medium"), failures)

    adv = ra.advise(ra.signals_for(["adr", "severity:high"], [], spec), spec)
    check("adr + severity:high -> max of matches (frontier-reasoning/high)",
          (adv["tier"], adv["effort"]) == ("frontier-reasoning", "high"), failures)
    check("both rules are reported as matched",
          {m["id"] for m in adv["matched"]} == {"sev-high", "adr"}, failures)

    fwd = ra.advise(ra.signals_for(["adr", "severity:high"], ["decision-heavy"], spec), spec)
    rev = ra.advise(list(reversed(ra.signals_for(["adr", "severity:high"], ["decision-heavy"], spec))), spec)
    check("decision-heavy + severity:high -> the foundational max", fwd["effort"] == "max", failures)
    check("signal order never changes the advice",
          (fwd["tier"], fwd["effort"]) == (rev["tier"], rev["effort"]), failures)

    adv = ra.advise(ra.signals_for([], ["sets-pattern"], spec), spec)
    check("sets-pattern alone -> frontier-reasoning/high",
          (adv["tier"], adv["effort"]) == ("frontier-reasoning", "high"), failures)

    adv = ra.advise(ra.signals_for(["documentation", "severity:low"], [], spec), spec)
    check("unknown labels match nothing and stay on the floor",
          (adv["tier"], adv["effort"]) == ("fast", "low"), failures)

    check("advice states the advisory boundary", "advisory" in adv["boundary"], failures)
    check("advice carries the catalog date", adv["catalog_as_of"] == "2026-07-09", failures)

    # --- loud rejection: signals ---
    try:
        ra.signals_for([], ["sets-patern"], spec)   # typo'd flag
        failures.append("a typo'd asserted flag must be rejected")
    except ValueError:
        pass

    # --- loud rejection: a spec that breaks its own invariants ---
    def broken(mutate):
        s = fixture_spec()
        mutate(s)
        return ra.spec_problems(s)

    check("a rule with an unknown min_tier is a problem",
          broken(lambda s: s["rules"][0].update(min_tier="huge")), failures)
    check("a rule with an unknown min_effort is a problem",
          broken(lambda s: s["rules"][0].update(min_effort="extreme")), failures)
    check("a rule referencing an undeclared flag is a problem",
          broken(lambda s: s["rules"][0].update(when=["flag:nope"])), failures)
    check("a malformed signal is a problem",
          broken(lambda s: s["rules"][0].update(when=["severity:high"])), failures)
    check("bad defaults are a problem",
          broken(lambda s: s["defaults"].update(tier="huge")), failures)
    check("a host missing a tier's model is a problem",
          broken(lambda s: s["catalog"]["hosts"][0]["models"].pop("fast")), failures)
    check("a host mapping an unknown tier is a problem",
          broken(lambda s: s["catalog"]["hosts"][0]["models"].update(huge="Y")), failures)
    check("an alias to an unknown effort is a problem",
          broken(lambda s: s["catalog"]["hosts"][0]["effort_aliases"].update(mega="extreme")), failures)
    check("an examples verdict outside `tiers` is a problem",
          broken(lambda s: s["examples"]["verdicts"].append("huge")), failures)
    check("a missing catalog date is a problem",
          broken(lambda s: s["catalog"].pop("as_of")), failures)
    check("a rule that can raise nothing is a problem",
          broken(lambda s: [s["rules"][0].pop("min_tier"), s["rules"][0].pop("min_effort")]), failures)

    # --- host + effort-alias resolution ---
    adv = ra.advise([], spec, host="other-host")
    check("an explicit host resolves its own catalog", adv["model"] == "X-small", failures)
    try:
        ra.advise([], spec, host="unknown-host")
        failures.append("an unknown host must be rejected")
    except ValueError:
        pass
    check("a host alias maps to the OS scale (ultracode -> max)",
          ra.normalize_effort("ultracode", spec) == "max", failures)
    check("an OS-scale effort passes through", ra.normalize_effort("high", spec) == "high", failures)
    try:
        ra.normalize_effort("mega", spec)
        failures.append("an unknown effort word must be rejected")
    except ValueError:
        pass

    # --- the shipped spec routes the ratified M16 anchor cases (plan-doc backfill table) ---
    adv = ra.advise(ra.signals_for(["adr", "severity:high"], ["decision-heavy"], shipped), shipped)
    check("shipped spec: the foundational ADR routes to frontier-reasoning/max",
          (adv["tier"], adv["effort"]) == ("frontier-reasoning", "max"), failures)
    adv = ra.advise(ra.signals_for(["documentation", "severity:low"], [], shipped), shipped)
    check("shipped spec: a small doc fix stays on the floor",
          (adv["tier"], adv["effort"]) == (shipped["defaults"]["tier"], shipped["defaults"]["effort"]),
          failures)
    adv = ra.advise(ra.signals_for(["security", "severity:medium"], [], shipped), shipped)
    check("shipped spec: the security surface routes to frontier-reasoning",
          adv["tier"] == "frontier-reasoning", failures)

    # --- formatting: the surfaces print what the human needs to overrule ---
    text = ra.format_advice(adv, heading="#241  audit sub-mode")
    check("formatted advice carries the heading", "#241" in text, failures)
    check("formatted advice names tier, effort, and model",
          all(s in text for s in ["tier=", "effort=", adv["model"]]), failures)
    check("formatted advice states the advisory boundary", "advisory" in text, failures)

    if failures:
        print("\ntest-route-advice: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("test-route-advice: OK — monotonic escalation, loud spec rejection, catalog/alias "
          "resolution, and the advisory boundary all hold (M16 16.2).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
