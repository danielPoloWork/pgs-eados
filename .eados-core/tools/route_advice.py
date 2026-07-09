#!/usr/bin/env python3
"""EADOS model & effort routing advisor (M16 16.2) — the `os/routing` policy as a tool. Given a
unit of work's signals (tracker labels + asserted flags) it recommends a capability tier, an
effort level, and the current model for a host — by the spec's monotonic escalation: start at the
`defaults` floor, every matched rule raises to at least its `min_tier`/`min_effort`, final = max.
It recommends only; the human keeps final model authority (ADR-0017, AGENTS.md §6).

Everything is data-driven: the policy is `orchestrator/os/routing/routing.yaml`; model names come
from its dated `catalog:`, never from this file. The core (`advise`) is pure and fixture-tested;
the spec is loud-rejected on load when it breaks its own `_schema.md` invariants. Only the
optional `--issue N` / `--milestone T` fetches shell out to `gh`, degrading cleanly (clear
message, exit 2) when `gh` is missing, unauthenticated, or offline — like `pr_review.py`.

    python .eados-core/tools/route_advice.py --labels "adr,severity:high" [--flags decision-heavy]
    python .eados-core/tools/route_advice.py --issue 247 [--repo OWNER/REPO] [--json]
    python .eados-core/tools/route_advice.py --milestone "M15 — command surface & governed assistants"
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # .eados-core/
sys.path.insert(0, HERE)
import render            # noqa: E402  — the dependency-free YAML loader

ROUTING_SPEC = os.path.join(ROOT, "orchestrator", "os", "routing", "routing.yaml")


# --- spec integrity (the _schema.md invariants, loud-rejected) -------------
def spec_problems(spec):
    """Pure referential-integrity check of a parsed routing spec. Returns a list of problem
    strings (empty == every reference resolves). This is the loud enforcement ADR-0017 assigns
    to the evaluator: a policy that parses but points at an unknown tier/effort/flag must fail
    here, not silently misroute."""
    problems = []
    if not isinstance(spec, dict):
        return ["routing spec is not a mapping"]
    tiers = spec.get("tiers") or []
    efforts = spec.get("efforts") or []
    flags = spec.get("flags") if isinstance(spec.get("flags"), dict) else {}
    if not isinstance(tiers, list) or not tiers:
        problems.append("`tiers` must be a non-empty ordered list")
    if not isinstance(efforts, list) or not efforts:
        problems.append("`efforts` must be a non-empty ordered list")

    defaults = spec.get("defaults") if isinstance(spec.get("defaults"), dict) else {}
    if defaults.get("tier") not in tiers:
        problems.append(f"defaults.tier {defaults.get('tier')!r} is not a `tiers` entry")
    if defaults.get("effort") not in efforts:
        problems.append(f"defaults.effort {defaults.get('effort')!r} is not an `efforts` entry")

    for i, rule in enumerate(spec.get("rules") or []):
        label = f"rules[{i}]"
        if not isinstance(rule, dict):
            problems.append(f"{label} must be a mapping")
            continue
        label = f"rule '{rule.get('id') or i}'"
        if not str(rule.get("id", "")).strip():
            problems.append(f"rules[{i}] has no id")
        when = rule.get("when")
        if not isinstance(when, list) or not when:
            problems.append(f"{label}: `when` must be a non-empty list of signals")
            when = []
        for sig in when:
            problems += _signal_problems(str(sig), flags, where=label)
        if rule.get("min_tier") is None and rule.get("min_effort") is None:
            problems.append(f"{label}: declares neither min_tier nor min_effort — it can raise nothing")
        if rule.get("min_tier") is not None and rule.get("min_tier") not in tiers:
            problems.append(f"{label}: min_tier {rule.get('min_tier')!r} is not a `tiers` entry")
        if rule.get("min_effort") is not None and rule.get("min_effort") not in efforts:
            problems.append(f"{label}: min_effort {rule.get('min_effort')!r} is not an `efforts` entry")

    catalog = spec.get("catalog") if isinstance(spec.get("catalog"), dict) else {}
    hosts = catalog.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        problems.append("`catalog.hosts` must be a non-empty list")
        hosts = []
    if not str(catalog.get("as_of", "")).strip():
        problems.append("`catalog.as_of` is missing — the dated catalog is the review cue")
    for h in hosts:
        if not isinstance(h, dict) or not str(h.get("host", "")).strip():
            problems.append("every catalog host entry needs a `host` id")
            continue
        hid = h["host"]
        models = h.get("models") if isinstance(h.get("models"), dict) else {}
        for tier in tiers:
            if not str(models.get(tier, "")).strip():
                problems.append(f"catalog host '{hid}' maps no model for tier '{tier}'")
        for tier in models:
            if tier not in tiers:
                problems.append(f"catalog host '{hid}' maps unknown tier '{tier}'")
        aliases = h.get("effort_aliases") if isinstance(h.get("effort_aliases"), dict) else {}
        for alias, effort in aliases.items():
            if effort not in efforts:
                problems.append(f"catalog host '{hid}' alias '{alias}' -> {effort!r} is not an "
                                "`efforts` entry")

    ex = spec.get("examples") if isinstance(spec.get("examples"), dict) else {}
    for verdict in (ex.get("verdicts") or []):
        if verdict not in tiers:
            problems.append(f"examples verdict '{verdict}' is not a `tiers` entry — the decision "
                            "surface must speak the policy's own vocabulary")
    return problems


def _signal_problems(sig, flags, where):
    """A signal is `label:<tracker label>` or `flag:<declared flags key>`. Unknown labels are
    fine (the tracker owns that vocabulary); an unknown FLAG is a typo the spec must catch."""
    if sig.startswith("label:"):
        return [] if sig[len("label:"):].strip() else [f"{where}: empty label signal"]
    if sig.startswith("flag:"):
        fid = sig[len("flag:"):].strip()
        if not fid:
            return [f"{where}: empty flag signal"]
        if fid not in flags:
            return [f"{where}: flag signal '{fid}' is not declared under `flags:`"]
        return []
    return [f"{where}: signal {sig!r} is neither 'label:<name>' nor 'flag:<id>'"]


def load_routing(path=ROUTING_SPEC):
    """Load + loud-reject: a spec that breaks its own invariants never reaches the core."""
    with open(path, encoding="utf-8") as handle:
        spec = render.load_yaml(handle.read())
    problems = spec_problems(spec)
    if problems:
        raise ValueError("routing spec invalid — " + "; ".join(problems))
    return spec


# --- the pure core ---------------------------------------------------------
def signals_for(labels=(), flags=(), spec=None):
    """Build the signal set from tracker label names + asserted flag ids. An asserted flag that
    the spec does not declare is a typo, rejected loudly (same posture as spec_problems)."""
    known = (spec.get("flags") if isinstance(spec, dict) and isinstance(spec.get("flags"), dict)
             else {})
    sigs = ["label:" + str(l).strip() for l in labels if str(l).strip()]
    for f in flags:
        fid = str(f).strip()
        if not fid:
            continue
        if spec is not None and fid not in known:
            raise ValueError(f"unknown flag '{fid}' — declared flags: {', '.join(sorted(known)) or 'none'}")
        sigs.append("flag:" + fid)
    return sigs


def advise(signals, spec, host=None):
    """Pure evaluator: monotonic escalation over the matched rules. `signals` is an iterable of
    'label:<name>' / 'flag:<id>' strings. Returns {tier, effort, model, host, matched[], floor}.
    Deterministic and order-independent: final = max(defaults, matched mins) in spec order."""
    tier_rank = {t: i for i, t in enumerate(spec["tiers"])}
    effort_rank = {e: i for i, e in enumerate(spec["efforts"])}
    have = {str(s) for s in signals}

    tier = spec["defaults"]["tier"]
    effort = spec["defaults"]["effort"]
    matched = []
    for rule in spec.get("rules") or []:
        if not all(str(sig) in have for sig in (rule.get("when") or [])):
            continue
        matched.append({"id": rule.get("id"), "why": rule.get("why")})
        mt, me = rule.get("min_tier"), rule.get("min_effort")
        if mt is not None and tier_rank[mt] > tier_rank[tier]:
            tier = mt
        if me is not None and effort_rank[me] > effort_rank[effort]:
            effort = me

    entry = _host_entry(spec, host)
    return {
        "tier": tier,
        "effort": effort,
        "model": entry["models"][tier],
        "host": entry["host"],
        "catalog_as_of": (spec.get("catalog") or {}).get("as_of"),
        "matched": matched,
        "floor": dict(spec["defaults"]),
        "boundary": "advisory only — the human keeps final model authority (ADR-0017)",
    }


def _host_entry(spec, host=None):
    """The catalog entry for `host` (default: the first host — the reference environment)."""
    hosts = (spec.get("catalog") or {}).get("hosts") or []
    if host is None:
        return hosts[0]
    for h in hosts:
        if h.get("host") == host:
            return h
    known = ", ".join(str(h.get("host")) for h in hosts)
    raise ValueError(f"unknown host '{host}' — catalog hosts: {known}")


def normalize_effort(word, spec, host=None):
    """Map a host-vocabulary effort word (e.g. Claude Code's 'ultracode') to the OS scale via the
    host's `effort_aliases`; an OS-scale word passes through. Unknown words are rejected loudly."""
    word = str(word).strip()
    if word in (spec.get("efforts") or []):
        return word
    aliases = _host_entry(spec, host).get("effort_aliases") or {}
    if word in aliases:
        return aliases[word]
    raise ValueError(f"unknown effort '{word}' — OS scale: {', '.join(spec.get('efforts') or [])}"
                     + (f"; host aliases: {', '.join(sorted(aliases))}" if aliases else ""))


def format_advice(advice, heading=None):
    """One human-readable advice block (the line the triage/status surfaces print)."""
    out = []
    if heading:
        out.append(heading)
    out.append(f"  route: tier={advice['tier']}  effort={advice['effort']}  "
               f"-> {advice['model']} (host: {advice['host']}, catalog as of "
               f"{advice['catalog_as_of']})")
    if advice["matched"]:
        for m in advice["matched"]:
            out.append(f"    matched {m['id']}: {m['why']}")
    else:
        out.append(f"    no rule matched — the floor applies "
                   f"(tier={advice['floor']['tier']}, effort={advice['floor']['effort']})")
    out.append(f"  {advice['boundary']}")
    return "\n".join(out)


# --- the thin `gh` shell (best-effort; degrades cleanly) ------------------
def _gh_json(args):
    import json
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise RuntimeError(f"could not run `gh` (is the GitHub CLI installed and on PATH?): {exc}")
    if proc.returncode != 0:
        raise RuntimeError(f"`gh {' '.join(args)}` failed (authenticated? online?): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    try:
        return json.loads(proc.stdout or "null")
    except ValueError as exc:
        raise RuntimeError(f"could not parse `gh` JSON output: {exc}")


def fetch_issue(number, repo=None):
    """{number, title, labels[]} for one issue. Raises RuntimeError when gh is unavailable."""
    args = ["issue", "view", str(number), "--json", "number,title,labels"]
    if repo:
        args += ["--repo", repo]
    data = _gh_json(args) or {}
    return {"number": data.get("number"), "title": data.get("title") or "",
            "labels": [l.get("name") for l in (data.get("labels") or []) if isinstance(l, dict)]}


def fetch_milestone_issues(milestone, repo=None):
    """Open issues of a milestone (by title), oldest first — the batch surface 16.3 prints."""
    args = ["issue", "list", "--state", "open", "--milestone", milestone,
            "--json", "number,title,labels", "--limit", "200"]
    if repo:
        args += ["--repo", repo]
    items = _gh_json(args) or []
    return sorted(({"number": it.get("number"), "title": it.get("title") or "",
                    "labels": [l.get("name") for l in (it.get("labels") or [])
                               if isinstance(l, dict)]}
                   for it in items if isinstance(it, dict)),
                  key=lambda it: it["number"] or 0)


def main(argv=None):
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Recommend a model tier + effort for a unit of work "
                                             "(advisory only — os/routing policy, ADR-0017).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--labels", help="comma-separated tracker labels (offline mode)")
    src.add_argument("--issue", type=int, help="fetch one issue's labels via gh")
    src.add_argument("--milestone", help="batch: one advice line per open issue of this milestone")
    ap.add_argument("--flags", default="", help="comma-separated asserted flags "
                                                "(e.g. sets-pattern,decision-heavy)")
    ap.add_argument("--repo", help="OWNER/REPO (default: the repo gh infers)")
    ap.add_argument("--host", default=None, help="catalog host (default: the first catalog entry)")
    ap.add_argument("--json", action="store_true", help="emit structured advice as JSON")
    args = ap.parse_args(argv)

    try:
        spec = load_routing()
    except (OSError, ValueError) as exc:
        print(f"route-advice: ERROR — {exc}", file=sys.stderr)
        return 1
    flags = [f for f in (args.flags or "").split(",") if f.strip()]

    try:
        if args.milestone is not None:
            if flags:
                print("route-advice: note — flags apply to every issue in the batch; per-issue "
                      "flags may raise individual routes further", file=sys.stderr)
            issues = fetch_milestone_issues(args.milestone, repo=args.repo)
            batch = [dict(advise(signals_for(it["labels"], flags, spec), spec, host=args.host),
                          issue=it["number"], title=it["title"]) for it in issues]
            if args.json:
                print(json.dumps({"milestone": args.milestone, "advice": batch}, indent=2))
            else:
                if not batch:
                    print(f"route-advice: no open issues in milestone '{args.milestone}'")
                for adv in batch:
                    print(f"#{adv['issue']} -> {adv['tier']}/{adv['effort']} ({adv['model']})  "
                          f"{adv['title']}")
                if batch:
                    print(f"advisory only — the human keeps final model authority (ADR-0017); "
                          f"asserted flags (sets-pattern, decision-heavy) may raise a route")
            return 0
        if args.issue is not None:
            it = fetch_issue(args.issue, repo=args.repo)
            advice = advise(signals_for(it["labels"], flags, spec), spec, host=args.host)
            heading = f"#{it['number']}  {it['title']}"
        else:
            labels = [l for l in args.labels.split(",") if l.strip()]
            advice = advise(signals_for(labels, flags, spec), spec, host=args.host)
            heading = f"labels: {', '.join(l.strip() for l in labels) or 'none'}" \
                      + (f"  flags: {', '.join(f.strip() for f in flags)}" if flags else "")
    except RuntimeError as exc:
        print(f"route-advice: SKIP — {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"route-advice: ERROR — {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(advice, indent=2))
    else:
        print(format_advice(advice, heading=heading))
    return 0


if __name__ == "__main__":
    sys.exit(main())
