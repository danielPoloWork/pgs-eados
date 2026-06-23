#!/usr/bin/env python3
"""Self-lint for the EADOS factory itself (the bar EADOS imposes downstream, imposed upstream).

Dependency-free (Python 3 standard library only). Run from anywhere in the repo:

    python tools/eados_lint.py

It enforces the orchestrator's own quality gates (AGENTS.md §8), which were previously only
asserted in prose:

  1. placeholder-integrity — every {{PLACEHOLDER}} used under templates/** is defined in
     orchestrator/placeholders.md (no orphans). GitHub Actions ${{ ... }} expressions and
     lower-case loop fields are ignored.
  2. profile-completeness  — every orchestrator/profiles/<lang>.yaml defines every key the
     schema (orchestrator/profiles/_schema.md) declares mandatory.
  3. generate-references   — every templates/... path the generation playbook
     (orchestrator/generate.md) names actually exists on disk (globs must match ≥1 file).

Each check runs independently; all failures are reported, then a non-zero exit on any.
"""

import glob
import hashlib
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import render  # noqa: E402  — the dependency-free YAML loader, reused to parse the OS specs

ROOT = os.path.dirname(TOOLS)
TEMPLATES = os.path.join(ROOT, "templates")
PROFILES = os.path.join(ROOT, "orchestrator", "profiles")
# The actual git repository root is one level above .eados-core/ — README.md and .github/
# live there, not under the factory folder (the i18n docs moved under .eados-core/docs/).
REPO_ROOT = os.path.dirname(ROOT)
failures = []  # (check, message)


def fail(check, message):
    failures.append((check, message))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def iter_text_files(root):
    for cur, _dirs, files in os.walk(root):
        if "__pycache__" in cur:
            continue
        for fn in files:
            if fn.endswith((".pyc", ".png", ".jpg", ".gif", ".ico")):
                continue
            yield os.path.join(cur, fn)


# Matches {{ ... }} not preceded by '$' (so GitHub Actions ${{ ... }} is excluded).
TOKEN_RE = re.compile(r"(?<!\$)\{\{\s*([^{}]*?)\s*\}\}")
UPPER_RE = re.compile(r"[A-Z][A-Z0-9_]*$")


# ---------------------------------------------------------------------------
# 1. Placeholder integrity
# ---------------------------------------------------------------------------
def known_placeholders():
    """Parse the dictionary's table rows for the authoritative scalar/section names."""
    scalars, sections = set(), set()
    for line in read(os.path.join(ROOT, "orchestrator", "placeholders.md")).splitlines():
        if not line.lstrip().startswith("|"):
            continue  # only table rows are authoritative; prose examples are ignored
        for inner in TOKEN_RE.findall(line):
            inner = inner.strip()
            if not inner or inner == ".":
                continue
            if inner[0] in "#^/":
                sections.add(inner[1:].strip())
            elif UPPER_RE.match(inner):
                scalars.add(inner)
    return scalars, sections


# templates/README.md is the templates-directory meta-doc — it is never rendered into a
# generated repo, and it cites {{PLACEHOLDER}} illustratively, so it is not scanned.
NOT_RENDERED = {"templates/README.md"}


def check_placeholder_integrity():
    name = "placeholder-integrity"
    scalars, sections = known_placeholders()
    if not scalars:
        fail(name, "could not parse any placeholders from orchestrator/placeholders.md")
        return
    for path in iter_text_files(TEMPLATES):
        try:
            text = read(path)
        except (UnicodeDecodeError, OSError):
            continue
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if rel in NOT_RENDERED:
            continue
        for inner in TOKEN_RE.findall(text):
            inner = inner.strip()
            if not inner or inner == ".":
                continue
            if inner[0] in "#^/":
                base = inner[1:].strip()
                if base not in sections:
                    fail(name, f"{rel}: section {{{{{inner}}}}} is not a known IF_/EACH_ "
                               "block in placeholders.md")
            elif UPPER_RE.match(inner):
                if inner not in scalars:
                    fail(name, f"{rel}: orphan placeholder {{{{{inner}}}}} is not defined "
                               "in placeholders.md")
            # lower-case / mixed tokens are loop fields ({{os}}, {{name}}) — not validated.


# ---------------------------------------------------------------------------
# 2. Profile completeness
# ---------------------------------------------------------------------------
def yaml_key_paths(text):
    """Indentation-based key-path extractor (keys only; values/list-items ignored).

    The body of a block scalar (`key: |`) is skipped — its lines are literal content
    (e.g. CI step YAML), not nested keys, so they must not become required paths.
    """
    lines = text.splitlines()
    paths, stack, i = set(), [], 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        stripped = raw.lstrip(" ")
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            continue
        m = re.match(r"([A-Za-z0-9_]+)\s*:(.*)$", stripped)
        if not m:
            continue
        indent = len(raw) - len(stripped)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, m.group(1)))
        paths.add(".".join(k for _, k in stack))
        if m.group(2).strip() in ("|", "|-", "|+", ">", ">-", ">+"):
            while i < len(lines) and (lines[i].strip() == "" or
                                      len(lines[i]) - len(lines[i].lstrip(" ")) > indent):
                i += 1
    return paths


def schema_required_paths():
    schema = read(os.path.join(PROFILES, "_schema.md"))
    block = re.search(r"```yaml\n(.*?)```", schema, re.DOTALL)
    if not block:
        return None
    return yaml_key_paths(block.group(1))


def check_profile_completeness():
    name = "profile-completeness"
    required = schema_required_paths()
    if not required:
        fail(name, "could not extract the schema YAML block from profiles/_schema.md")
        return
    # Real profiles are <lang>.yaml; underscore-prefixed files (_template.yaml) are
    # scaffolds, not languages, and are not held to completeness.
    profiles = sorted(p for p in glob.glob(os.path.join(PROFILES, "*.yaml"))
                      if not os.path.basename(p).startswith("_"))
    if not profiles:
        fail(name, "no profiles/*.yaml found")
        return
    for path in profiles:
        have = yaml_key_paths(read(path))
        missing = sorted(required - have)
        for key in missing:
            fail(name, f"profiles/{os.path.basename(path)}: missing schema key '{key}'")


# ---------------------------------------------------------------------------
# 3. Generation playbook references exist
# ---------------------------------------------------------------------------
def check_generate_references():
    name = "generate-references"
    gen = read(os.path.join(ROOT, "orchestrator", "generate.md"))
    refs = set(re.findall(r"templates/[A-Za-z0-9_./*-]+", gen))
    for ref in sorted(refs):
        ref = ref.rstrip(".,)")
        if ref in ("templates", "templates/") or "**" in ref:
            continue
        abspath = os.path.join(ROOT, ref.replace("/", os.sep))
        if "*" in ref:
            if not glob.glob(abspath):
                fail(name, f"generate.md glob '{ref}' matches no file on disk")
        elif not os.path.exists(abspath):
            fail(name, f"generate.md references '{ref}' which does not exist")


# ---------------------------------------------------------------------------
# 4. Agent registry — every role file is indexed in agent/README.md
# ---------------------------------------------------------------------------
def check_agent_registry():
    name = "agent-registry"
    agent_dir = os.path.join(ROOT, "agent")
    index_path = os.path.join(agent_dir, "README.md")
    if not os.path.isdir(agent_dir) or not os.path.exists(index_path):
        return
    index = read(index_path)
    # Walk recursively so domain-overlay personas (agent/domains/<domain>/<role>.md) are indexed
    # too, matched by their path RELATIVE to agent/ — not basename, since an overlay shares its
    # basename with the default persona it specializes.
    for cur, _dirs, files in os.walk(agent_dir):
        for fn in sorted(files):
            if not fn.endswith(".md") or fn == "README.md":
                continue
            rel = os.path.relpath(os.path.join(cur, fn), agent_dir).replace(os.sep, "/")
            if f"({rel})" not in index:
                fail(name, f"agent persona '{rel}' is not listed in agent/README.md")


# ---------------------------------------------------------------------------
# 5. Lessons ledger — schema of every entry (when the ledger exists)
# ---------------------------------------------------------------------------
LESSON_SCOPES_PREFIX = ("global", "lang:", "kind:")
LESSON_REQUIRED = ("id", "date", "scope", "context", "rule")


def check_lessons():
    name = "lessons"
    ledger = os.path.join(ROOT, "learning", "lessons.yaml")
    if not os.path.exists(ledger):
        return
    text = read(ledger)
    # Each entry begins with "- id:"; validate required keys + scope vocabulary per block.
    blocks = re.split(r"\n(?=- id:)", text)
    seen_ids = set()
    for block in blocks:
        if "id:" not in block:
            continue
        fields = dict(re.findall(r"^\s*-?\s*([a-z_]+):\s*(.+?)\s*$", block, re.MULTILINE))
        for key in LESSON_REQUIRED:
            if key not in fields:
                fail(name, f"lessons.yaml entry missing '{key}': {fields.get('id', '?')}")
        lid = fields.get("id", "")
        if lid in seen_ids:
            fail(name, f"lessons.yaml duplicate id '{lid}'")
        seen_ids.add(lid)
        scope = fields.get("scope", "").strip().strip('"')
        if scope and not scope.startswith(LESSON_SCOPES_PREFIX):
            fail(name, f"lessons.yaml entry '{lid}': scope '{scope}' not global|lang:*|kind:*")


# ---------------------------------------------------------------------------
# 6. Action-pin lockstep — SHA-pinned actions shared by the factory CI and the rendered
#    workflow templates must pin the SAME commit (templates are NOT seen by the factory's
#    Dependabot, so they silently drift behind; ADR-0009). Floating tags (@v6) are exempt
#    by design — only fully SHA-pinned `uses: …@<40hex> # vX.Y.Z` lines are governed.
# ---------------------------------------------------------------------------
PIN_RE = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@([0-9a-fA-F]{40})\s*#\s*(v[0-9][\w.-]*)")


def check_action_pins():
    name = "action-pins"
    factory_ci = os.path.join(os.path.dirname(ROOT), ".github", "workflows", "ci.yml")
    tmpl_wf = os.path.join(TEMPLATES, ".github", "workflows")
    if not os.path.exists(factory_ci) or not os.path.isdir(tmpl_wf):
        return  # standalone .eados-core checkout: nothing to cross-check
    fac = {a: (sha, ver) for a, sha, ver in PIN_RE.findall(read(factory_ci))}
    for path in sorted(glob.glob(os.path.join(tmpl_wf, "*.tmpl"))):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        for action, sha, ver in PIN_RE.findall(read(path)):
            if action in fac and (sha, ver) != fac[action]:
                fail(name, f"{rel}: {action} pinned {sha[:10]} ({ver}) but the factory CI pins "
                           f"{fac[action][0][:10]} ({fac[action][1]}) — keep them in lockstep")


# ---------------------------------------------------------------------------
# 7. i18n freshness — every `translated` row in .eados-core/docs/i18n/translation-status.md pins the
#    SHA-256 content hash of the English source it was made from; the translation is STALE
#    when the current source hashes differently. Content-based (not commit-based) so it is
#    immune to squash-merges, which rewrite history and would orphan a recorded commit
#    (ADR-0010). Git-independent. Opt-in: skipped when no manifest exists.
# ---------------------------------------------------------------------------
def _source_hash(path):
    """First 12 hex of the SHA-256 of the file's bytes — the stable content fingerprint."""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()[:12]


def check_i18n_freshness():
    name = "i18n-freshness"
    manifest_path = os.path.join(ROOT, "docs", "i18n", "translation-status.md")
    if not os.path.exists(manifest_path):
        return  # the factory ships no translations — nothing to check
    i18n_dir = os.path.join(ROOT, "docs", "i18n")
    rows = 0
    for line in read(manifest_path).splitlines():
        # Data rows begin with a link cell `| [...](...)`; skips the legend + header rows.
        if not line.lstrip().startswith("| [") or "`translated`" not in line:
            continue
        link = re.search(r"\]\(([^)]+)\)", line)
        rec = re.search(r"\|\s*`([0-9a-f]{12,64})`\s*\|", line)
        if link is None or rec is None:
            fail(name, f"could not parse translated manifest row: {line.strip()}")
            continue
        rows += 1
        src = os.path.normpath(os.path.join(i18n_dir, link.group(1)))
        rel = os.path.relpath(src, REPO_ROOT).replace(os.sep, "/")
        if not os.path.exists(src):
            fail(name, f"manifest references English source {rel} which does not exist")
            continue
        recorded, actual = rec.group(1), _source_hash(src)
        if actual != recorded:
            fail(name, f"i18n translation of {rel} is STALE: source content hash {actual} "
                       f"≠ recorded {recorded} — refresh the translation and update its "
                       "translation-status.md row")
    if rows == 0:
        fail(name, "translation-status.md exists but has no parseable `translated` rows")


# ---------------------------------------------------------------------------
# 8. OS-spec completeness — every orchestrator/os/<spec>/ ships a `_schema.md` (with a yaml
#    block) and a `<spec>.yaml` instance that defines every top-level key the schema declares.
#    The same data+schema contract as profile-completeness, applied to the machine-readable
#    delivery-OS specs (ADR-0011). Opt-in: skipped until the os/ directory exists.
# ---------------------------------------------------------------------------
def check_os_specs():
    name = "os-spec-completeness"
    os_dir = os.path.join(ROOT, "orchestrator", "os")
    if not os.path.isdir(os_dir):
        return  # the OS specs are introduced with the delivery-OS pivot; absent before it
    specs = sorted(d for d in os.listdir(os_dir)
                   if os.path.isdir(os.path.join(os_dir, d)))
    checked = 0
    for spec in specs:
        d = os.path.join(os_dir, spec)
        schema_path = os.path.join(d, "_schema.md")
        inst_path = os.path.join(d, f"{spec}.yaml")
        if not os.path.exists(schema_path):
            fail(name, f"orchestrator/os/{spec}/ has no _schema.md")
            continue
        if not os.path.exists(inst_path):
            fail(name, f"orchestrator/os/{spec}/ has no {spec}.yaml instance")
            continue
        block = re.search(r"```yaml\n(.*?)```", read(schema_path), re.DOTALL)
        if not block:
            fail(name, f"orchestrator/os/{spec}/_schema.md has no yaml schema block")
            continue
        required = yaml_key_paths(block.group(1))
        have = yaml_key_paths(read(inst_path))
        for key in sorted(required - have):
            fail(name, f"orchestrator/os/{spec}/{spec}.yaml: missing schema key '{key}'")
        checked += 1
    if specs and checked == 0:
        fail(name, "orchestrator/os/ exists but holds no <spec>/_schema.md + <spec>.yaml pair")


# ---------------------------------------------------------------------------
# 9. Domain-completeness — every orchestrator/domains/<domain>.yaml defines every key the domain
#    schema (orchestrator/domains/_schema.md) declares. The second axis of genericity, held to the
#    same data+schema contract as the language profiles (RFC-0001 §3-4). Underscore-prefixed files
#    (_template.yaml) are scaffolds, not domains. Opt-in: skipped until the domains/ dir exists.
# ---------------------------------------------------------------------------
def check_domains():
    name = "domain-completeness"
    ddir = os.path.join(ROOT, "orchestrator", "domains")
    if not os.path.isdir(ddir):
        return  # the domain axis is introduced in M1; absent before it
    schema_path = os.path.join(ddir, "_schema.md")
    if not os.path.exists(schema_path):
        fail(name, "orchestrator/domains/_schema.md is missing")
        return
    block = re.search(r"```yaml\n(.*?)```", read(schema_path), re.DOTALL)
    if not block:
        fail(name, "orchestrator/domains/_schema.md has no yaml schema block")
        return
    required = yaml_key_paths(block.group(1))
    domains = sorted(p for p in glob.glob(os.path.join(ddir, "*.yaml"))
                     if not os.path.basename(p).startswith("_"))
    if not domains:
        fail(name, "no orchestrator/domains/<domain>.yaml found")
        return
    for path in domains:
        have = yaml_key_paths(read(path))
        for key in sorted(required - have):
            fail(name, f"domains/{os.path.basename(path)}: missing schema key '{key}'")


# ---------------------------------------------------------------------------
# 10. Authority-personas — the persona <-> authority pairing (RFC-0001 §4 / roadmap 1.5). Every
#     role in orchestrator/os/authority/authority.yaml has an agent/<role>.md persona OR is listed
#     in `pending_personas`; every agent/<role>.md persona maps to a declared role; a pending role
#     must not already have a persona. Opt-in: skipped until the authority spec exists.
# ---------------------------------------------------------------------------
def check_authority_personas():
    name = "authority-personas"
    auth = os.path.join(ROOT, "orchestrator", "os", "authority", "authority.yaml")
    agent_dir = os.path.join(ROOT, "agent")
    if not os.path.exists(auth) or not os.path.isdir(agent_dir):
        return
    text = read(auth)
    roles = set(re.findall(r"(?m)^\s*-\s*name:\s*([A-Za-z][\w-]*)", text))
    if not roles:
        fail(name, "could not parse any role names from authority.yaml")
        return
    pend_m = re.search(r"pending_personas:\s*\[([^\]]*)\]", text)
    pending = {s.strip() for s in (pend_m.group(1).split(",") if pend_m else []) if s.strip()}
    # Persona role-ids, collected recursively: a default agent/<role>.md and a domain overlay
    # agent/domains/<d>/<role>.md both map to the same role id (the filename stem).
    personas = set()
    for cur, _dirs, files in os.walk(agent_dir):
        for fn in files:
            if fn.endswith(".md") and fn != "README.md":
                personas.add(os.path.splitext(fn)[0])
    for role in sorted(roles - personas - pending):
        fail(name, f"authority role '{role}' has no agent/{role}.md persona and is not in "
                   "pending_personas")
    for persona in sorted(personas - roles):
        fail(name, f"persona agent/{persona}.md has no role record in authority.yaml")
    for role in sorted(pending & personas):
        fail(name, f"role '{role}' is in pending_personas but agent/{role}.md exists — "
                   "remove it from pending_personas")


# ---------------------------------------------------------------------------
# 11. Cross-spec consistency — referential integrity ACROSS the delivery-OS specs. os-spec-
#     completeness checks that each spec carries its own keys; this checks that the references
#     BETWEEN them resolve. A role named in workflow/plan/rfc/a domain must exist in the authority
#     model; a gate named in a workflow transition / plan / rfc must exist in the workflow gate
#     registry; a from/to/required_for state must exist; a domain's workflow_overlay must exist;
#     a risk level / domain-override must resolve. This is the gate that stops the OS from
#     silently fragmenting as the specs evolve — a `tech-led` typo, a phantom transition gate, a
#     dangling overlay would otherwise pass unnoticed (the OS thesis: knowledge as data, applied
#     by gates). The git spec's cross-cutting `traceability` gate is NOT a phase-transition gate and
#     is intentionally outside this registry check. Opt-in: skipped until orchestrator/os/ exists.
# ---------------------------------------------------------------------------
def _load_spec(spec):
    """Parse orchestrator/os/<spec>/<spec>.yaml with the dependency-free loader; None if absent."""
    path = os.path.join(ROOT, "orchestrator", "os", spec, f"{spec}.yaml")
    return render.load_yaml(read(path)) if os.path.exists(path) else None


def _load_domains():
    """Parse every orchestrator/domains/<domain>.yaml (skipping _scaffolds) -> {filename: data}."""
    out = {}
    ddir = os.path.join(ROOT, "orchestrator", "domains")
    if os.path.isdir(ddir):
        for path in sorted(glob.glob(os.path.join(ddir, "*.yaml"))):
            if not os.path.basename(path).startswith("_"):
                out[os.path.basename(path)] = render.load_yaml(read(path))
    return out


def cross_spec_problems(authority, workflow, plan=None, rfc=None, risk=None, domains=None):
    """Pure referential-integrity check across the parsed delivery-OS specs. Returns a list of
    problem strings (empty == every cross-reference resolves). I/O-free so it is unit-testable
    with in-memory fixtures; check_cross_spec_consistency() supplies the on-disk specs."""
    problems = []
    if not isinstance(authority, dict) or not isinstance(workflow, dict):
        return problems   # a missing/unparseable core spec is os-spec-completeness's report, not ours
    domains = domains or {}

    def vocab(records, key):
        return {r[key] for r in (records or []) if isinstance(r, dict) and r.get(key) is not None}

    roles = vocab(authority.get("roles"), "name")
    states = vocab(workflow.get("states"), "id")
    gates = vocab(workflow.get("gates"), "id")
    overlays_map = workflow.get("domain_overlays") or {}
    if not isinstance(overlays_map, dict):
        overlays_map = {}
    overlays = set(overlays_map)
    for ov in overlays_map.values():        # an overlay may DEFINE extra gates — legitimate ids too
        if isinstance(ov, dict):
            gates |= set(ov.get("add_gates") or [])
    levels = set(risk.get("levels") or []) if isinstance(risk, dict) else set()
    domain_ids = {d["domain"] for d in domains.values()
                  if isinstance(d, dict) and d.get("domain") is not None}

    HUMAN = {"human-owner", "human"}   # escalation/PR terminals that are not authority roles

    def one(label, value, allowed, kind):
        if value is not None and value not in allowed:
            problems.append(f"{label} references unknown {kind} '{value}'")

    def many(label, values, allowed, kind):
        for v in (values if isinstance(values, list) else []):
            one(label, v, allowed, kind)

    # --- authority: routing + escalation reference its own roles ---
    for om in (authority.get("ownership_map") or []):
        if isinstance(om, dict):
            one(f"authority.ownership_map[{om.get('glob')!r}].role", om.get("role"), roles, "role")
    for esc in (authority.get("escalation") or []):
        if isinstance(esc, dict):
            one(f"authority.escalation L{esc.get('level')}.decider",
                esc.get("decider"), roles | HUMAN, "role")

    # --- workflow: state owners, transition states + gates, gate target states, overlay domains ---
    for st in (workflow.get("states") or []):
        if isinstance(st, dict):
            one(f"workflow.states[{st.get('id')!r}].role", st.get("role"), roles, "role")
    for tr in (workflow.get("transitions") or []):
        if isinstance(tr, dict):
            edge = f"workflow.transition {tr.get('from')}->{tr.get('to')}"
            one(f"{edge}.from", tr.get("from"), states, "state")
            one(f"{edge}.to", tr.get("to"), states, "state")
            many(f"{edge}.entry_gates", tr.get("entry_gates"), gates, "gate")
    for g in (workflow.get("gates") or []):
        if isinstance(g, dict):
            many(f"workflow.gate {g.get('id')!r}.required_for", g.get("required_for"), states, "state")
    if domain_ids:
        for ov_key in sorted(overlays):
            one("workflow.domain_overlays key", ov_key, domain_ids, "domain")

    # --- plan: negotiation roles + the plan->scaffold transition gate ---
    if isinstance(plan, dict):
        plan_roles = plan.get("roles")
        if isinstance(plan_roles, dict):
            for role_key, role_val in plan_roles.items():
                one(f"plan.roles.{role_key}", role_val, roles, "role")
        one("plan.gate", plan.get("gate"), gates, "gate")

    # --- rfc: author/reviewer/approver roles + the design->plan transition gate ---
    if isinstance(rfc, dict):
        many("rfc.author_roles", rfc.get("author_roles"), roles, "role")
        many("rfc.reviewer_roles", rfc.get("reviewer_roles"), roles, "role")
        one("rfc.approver_role", rfc.get("approver_role"), roles, "role")
        one("rfc.gate", rfc.get("gate"), gates, "gate")

    # --- risk: the mandatory gate level + per-domain overrides resolve ---
    if isinstance(risk, dict) and levels:
        one("risk.mandatory_gate_level", risk.get("mandatory_gate_level"), levels, "level")
        dov = risk.get("domain_overrides") if isinstance(risk.get("domain_overrides"), dict) else {}
        for dname, override in dov.items():
            if domain_ids:
                one(f"risk.domain_overrides[{dname!r}]", dname, domain_ids, "domain")
            if isinstance(override, dict):
                one(f"risk.domain_overrides[{dname!r}].mandatory_gate_level",
                    override.get("mandatory_gate_level"), levels, "level")

    # --- domains: declared roles, role-label keys, and the workflow overlay all resolve ---
    for fname, data in sorted(domains.items()):
        if not isinstance(data, dict):
            continue
        many(f"domains/{fname}.roles", data.get("roles"), roles, "role")
        if isinstance(data.get("role_labels"), dict):
            for rkey in data["role_labels"]:
                one(f"domains/{fname}.role_labels key", rkey, roles, "role")
        one(f"domains/{fname}.workflow_overlay", data.get("workflow_overlay"), overlays,
            "workflow_overlay")

    return problems


def check_cross_spec_consistency():
    name = "cross-spec-consistency"
    if not os.path.isdir(os.path.join(ROOT, "orchestrator", "os")):
        return  # the OS specs arrive with the delivery-OS pivot; absent before it
    authority, workflow = _load_spec("authority"), _load_spec("workflow")
    if not isinstance(authority, dict) or not isinstance(workflow, dict):
        return  # os-spec-completeness reports a missing/unparseable core spec
    problems = cross_spec_problems(authority, workflow, _load_spec("plan"),
                                   _load_spec("rfc"), _load_spec("risk"), _load_domains())
    for problem in problems:
        fail(name, problem)


CHECKS = [
    check_placeholder_integrity,
    check_profile_completeness,
    check_generate_references,
    check_agent_registry,
    check_lessons,
    check_action_pins,
    check_i18n_freshness,
    check_os_specs,
    check_domains,
    check_authority_personas,
    check_cross_spec_consistency,
]


def main():
    for fn in CHECKS:
        try:
            fn()
        except Exception as exc:  # a crashing check is itself a failure
            fail(fn.__name__, f"check crashed: {exc!r}")
    if failures:
        print("EADOS self-lint: FAIL\n")
        for check, message in failures:
            print(f"  [{check}] {message}")
        print(f"\n{len(failures)} factory-integrity problem(s) found.")
        return 1
    print("EADOS self-lint: OK — placeholders, profiles, and playbook references are congruent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
