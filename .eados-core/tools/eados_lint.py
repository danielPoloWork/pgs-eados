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
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import render  # noqa: E402  — the dependency-free YAML loader, reused to parse the OS specs
import record_run  # noqa: E402  — the run-record schema authority (OUTCOMES, RUBRIC_DIMENSIONS)

ROOT = os.path.dirname(TOOLS)
TEMPLATES = os.path.join(ROOT, "templates")
PROFILES = os.path.join(ROOT, "orchestrator", "profiles")
# The actual git repository root is one level above .eados-core/ — README.md and .github/
# live there, not under the factory folder (the i18n docs moved under .eados-core/docs/).
REPO_ROOT = os.path.dirname(ROOT)

# #167: no module-global failures list. Every check_*(fail) receives the reporting callable —
# fail(check, message) — and main() owns the accumulator, mirroring how render() threads its
# `errors` list. Checks are reentrant and standalone-runnable; a test never resets module state.


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


def check_placeholder_integrity(fail):
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


def check_profile_completeness(fail):
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
def check_generate_references(fail):
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
# 4. Agent registry — every role file is indexed in agent/README.md, AND every persona link in
#    the index resolves to a file that exists (both directions, mirroring workflow-safety /
#    gate-coverage — a renamed or deleted persona must not leave a dead catalogue entry).
# ---------------------------------------------------------------------------
_AGENT_MD_LINK = re.compile(r"\]\(([^)]+\.md)\)")


def _persona_relative_links(index_text):
    """The persona `.md` links in agent/README.md that resolve UNDER agent/ — i.e. NOT http(s)://,
    NOT absolute, NOT `../`-escaping (the `../config/README.md` / `../learning/README.md` links stay
    out of the on-disk probe), and not the index's own README.md."""
    out = set()
    for target in (m.group(1).strip() for m in _AGENT_MD_LINK.finditer(index_text)):
        norm = target.replace("\\", "/")
        if norm.startswith(("http://", "https://", "/")) or norm.startswith("../") or "/../" in norm:
            continue
        if norm == "README.md":
            continue
        out.add(norm)
    return out


def agent_registry_problems(index_text, persona_rels):
    """Both directions of the agent-registry contract, pure/injectable (mirrors
    workflow_safety_problems / gate_coverage_problems):
      * every persona present under agent/ (relpath, README.md excluded) must be LISTED in the index;
      * every persona-relative `.md` link in the index must EXIST as a persona file.
    Returns a list of problems (empty == the index and the files agree both ways)."""
    problems = []
    listed = _persona_relative_links(index_text)
    for rel in sorted(persona_rels):
        if rel not in listed:
            problems.append(f"agent persona '{rel}' is not listed in agent/README.md")
    for rel in sorted(listed):
        if rel not in persona_rels:
            problems.append(f"agent/README.md lists '{rel}' which does not exist under agent/")
    return problems


def check_agent_registry(fail):
    name = "agent-registry"
    agent_dir = os.path.join(ROOT, "agent")
    index_path = os.path.join(agent_dir, "README.md")
    if not os.path.isdir(agent_dir) or not os.path.exists(index_path):
        return
    # Walk recursively so domain-overlay personas (agent/domains/<domain>/<role>.md) are indexed
    # too, matched by their path RELATIVE to agent/ — not basename, since an overlay shares its
    # basename with the default persona it specializes.
    persona_rels = set()
    for cur, _dirs, files in os.walk(agent_dir):
        for fn in sorted(files):
            if not fn.endswith(".md") or fn == "README.md":
                continue
            persona_rels.add(os.path.relpath(os.path.join(cur, fn), agent_dir).replace(os.sep, "/"))
    for problem in agent_registry_problems(read(index_path), persona_rels):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 5. Lessons ledger — schema of every entry (when the ledger exists)
# ---------------------------------------------------------------------------
LESSON_SCOPES_PREFIX = ("global", "lang:", "kind:")
LESSON_REQUIRED = ("id", "date", "scope", "context", "rule")


def check_lessons(fail):
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


def check_action_pins(fail):
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


def check_i18n_freshness(fail):
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
def check_os_specs(fail):
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
def check_domains(fail):
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
def check_authority_personas(fail):
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


def cross_spec_problems(authority, workflow, plan=None, rfc=None, risk=None, domains=None, git=None,
                        contribution=None):
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
    # #165: an overlay's add_gates must resolve to the gate REGISTRY — a bare id is a reference,
    # never a definition (the old lenience left overlay gates with no kind/runs/blocking, and the
    # hole was codified in tests; apply_overlay needs the entry's required_for to place the gate).
    for ov_key in sorted(overlays):
        ov = overlays_map[ov_key]
        if isinstance(ov, dict):
            many(f"workflow.domain_overlays[{ov_key!r}].add_gates", ov.get("add_gates"),
                 gates, "gate")
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

    # --- git: the cross-cutting (non-phase) gate references resolve to the gate registry — the
    #     scope deferred from #62 (6.8), now also the inbound-review gate (M8 8.5). A typo'd
    #     cross-cutting gate id is caught here. ---
    if isinstance(git, dict):
        if isinstance(git.get("traceability"), dict):
            one("git.traceability.gate", git["traceability"].get("gate"), gates, "gate")
        if isinstance(git.get("pr"), dict):
            one("git.pr.review_gate", git["pr"].get("review_gate"), gates, "gate")

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

    # --- contribution: the escalation decider resolves to a role / the human terminal, and the
    #     escalation disposition is one the policy itself declares (M8 8.1 — the inbound-review
    #     policy is data, so a typo'd decider/disposition is caught here, not at review time) ---
    if isinstance(contribution, dict):
        esc = contribution.get("escalation")
        if isinstance(esc, dict):
            one("contribution.escalation.decider", esc.get("decider"), roles | HUMAN, "role")
            disp_ids = {d.get("id") for d in (contribution.get("dispositions") or [])
                        if isinstance(d, dict)}
            if esc.get("disposition") is not None and disp_ids and esc["disposition"] not in disp_ids:
                problems.append("contribution.escalation.disposition references unknown disposition "
                                f"'{esc['disposition']}'")

    return problems


def check_cross_spec_consistency(fail):
    name = "cross-spec-consistency"
    if not os.path.isdir(os.path.join(ROOT, "orchestrator", "os")):
        return  # the OS specs arrive with the delivery-OS pivot; absent before it
    authority, workflow = _load_spec("authority"), _load_spec("workflow")
    if not isinstance(authority, dict) or not isinstance(workflow, dict):
        return  # os-spec-completeness reports a missing/unparseable core spec
    problems = cross_spec_problems(authority, workflow, _load_spec("plan"),
                                   _load_spec("rfc"), _load_spec("risk"), _load_domains(),
                                   _load_spec("git"), _load_spec("contribution"))
    for problem in problems:
        fail(name, problem)


# ---------------------------------------------------------------------------
# 12. Version lockstep — EADOS dogfoods the `version-lockstep` gate it ships to generated repos
#     (roadmap 6.7 / F4): every README release badge (EN + i18n) and the CHANGELOG's "latest is"
#     prose must match the CHANGELOG's latest released `## [X.Y.Z]`. The factory is held to the bar
#     it imposes downstream — a release bump now moves every badge + the prose in lockstep or fails.
# ---------------------------------------------------------------------------
RELEASE_BADGE_RE = re.compile(r"release-v(\d+\.\d+\.\d+)")


def version_lockstep_problems(changelog_text, readmes):
    """Pure check: every (label, text) README's `release-vX.Y.Z` badge — and the CHANGELOG's
    'the latest is **vX.Y.Z**' prose — must equal the CHANGELOG's latest released `## [X.Y.Z]`
    heading. Returns a list of problem strings (empty == in lockstep)."""
    releases = re.findall(r"(?m)^##\s*\[(\d+\.\d+\.\d+)\]", changelog_text)
    if not releases:
        return ["CHANGELOG.md has no released `## [X.Y.Z]` heading to lock the badges to"]
    latest = releases[0]   # CHANGELOG is newest-first; `[Unreleased]` is not an X.Y.Z, so skipped
    problems = []
    prose = re.search(r"the latest is \*\*v(\d+\.\d+\.\d+)\*\*", changelog_text)
    if prose and prose.group(1) != latest:
        problems.append(f"CHANGELOG 'the latest is v{prose.group(1)}' != latest release v{latest}")
    for label, text in readmes:
        badge = RELEASE_BADGE_RE.search(text)
        if badge is None:
            problems.append(f"{label}: no `release-vX.Y.Z` badge found")
        elif badge.group(1) != latest:
            problems.append(f"{label}: release badge v{badge.group(1)} != latest release v{latest}")
    return problems


def check_version_lockstep(fail):
    name = "version-lockstep"
    changelog_path = os.path.join(REPO_ROOT, "CHANGELOG.md")
    if not os.path.exists(changelog_path):
        return  # a partial checkout without the changelog — nothing to lock to
    readmes = []
    en = os.path.join(REPO_ROOT, "README.md")
    if os.path.exists(en):
        readmes.append(("README.md", read(en)))
    i18n_dir = os.path.join(ROOT, "docs", "i18n")
    if os.path.isdir(i18n_dir):
        for sub in sorted(os.listdir(i18n_dir)):
            readme = os.path.join(i18n_dir, sub, "README.md")
            if os.path.isfile(readme):
                readmes.append((f"docs/i18n/{sub}/README.md", read(readme)))
    for problem in version_lockstep_problems(read(changelog_path), readmes):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 12.5. Roadmap freshness (#237) — ROADMAP.md declares itself the single source of truth for
#     EADOS's own delivery plan, but nothing enforced that a milestone the CHANGELOG documents as
#     RELEASED actually got a "done" row in the roadmap's status table — the gap that let M10–M14
#     ship undocumented for four consecutive milestones before this check existed. Every milestone
#     number tagged in a RELEASED CHANGELOG section (`(#NNN, M<n>` — the citation style every entry
#     has used since M11) must appear as a done row (`**M<n>` + a ✅ on the same line) in
#     ROADMAP.md's status table. Unreleased milestones (still under `## [Unreleased]`, e.g. M15+)
#     are exempt — they are tracked by their own `.issues/M<n>-*-milestone.md` plan doc until
#     released, per the roadmap-vs-issues-plan-doc split that emerged starting M15.
# ---------------------------------------------------------------------------
_CHANGELOG_MILESTONE_TAG_RE = re.compile(r"\(#\d+,\s*M(\d+)\b")
_ROADMAP_DONE_ROW_RE = re.compile(r"\*\*M(\d+)\b[^\n]*✅")


def roadmap_freshness_problems(changelog_text, roadmap_text):
    """Pure check: every milestone number tagged in a RELEASED CHANGELOG section (text from the
    first `## [X.Y.Z]` heading onward — `[Unreleased]` is excluded) must have a done row in
    ROADMAP.md's status table. Returns problem strings (empty == fresh)."""
    released_start = re.search(r"(?m)^##\s*\[\d+\.\d+\.\d+\]", changelog_text)
    if released_start is None:
        return []  # nothing released yet — nothing to backfill
    released_text = changelog_text[released_start.start():]
    tagged = {int(m) for m in _CHANGELOG_MILESTONE_TAG_RE.findall(released_text)}
    done = {int(m) for m in _ROADMAP_DONE_ROW_RE.findall(roadmap_text)}
    missing = sorted(tagged - done)
    if not missing:
        return []
    names = ", ".join(f"M{n}" for n in missing)
    return [f"ROADMAP.md's status table has no done row for {names} — the CHANGELOG documents "
            f"{'it' if len(missing) == 1 else 'them'} as released; backfill the milestone "
            "section(s) + status row(s) in the same PR (the cross-cutting lockstep invariant)"]


def check_roadmap_freshness(fail):
    name = "roadmap-freshness"
    changelog_path = os.path.join(REPO_ROOT, "CHANGELOG.md")
    roadmap_path = os.path.join(ROOT, "docs", "rfc", "ROADMAP.md")
    if not os.path.exists(changelog_path) or not os.path.exists(roadmap_path):
        return  # a partial checkout without one of the two documents — nothing to check
    for problem in roadmap_freshness_problems(read(changelog_path), read(roadmap_path)):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 13. Manifest-template integrity — orchestrator/project.yaml.template is the one factory file a
#     consumer copies and hand-fills, yet nothing validated it: it is not under templates/** (so
#     placeholder-integrity skips it) and render-smoke renders reference.yaml instead. A broken
#     hand-edit here (invalid YAML, a dropped section, a typo'd `-> {{MARKER}}`) would ship
#     silently. This gate keeps it valid, complete, and well-annotated — the safety net the
#     issue-#90 episode showed was missing for a file external contributors can touch.
# ---------------------------------------------------------------------------
MANIFEST_TEMPLATE = os.path.join(ROOT, "orchestrator", "project.yaml.template")
MANIFEST_SECTIONS = ["schema_version", "domain", "identity", "ownership", "language",
                     "toolchain", "ci", "governance", "i18n", "announce", "spec"]
# A `-> {{MARKER}}` annotation points a field at the placeholder it resolves; capture the optional
# section sigil (#/^//) so both scalars ({{X}}) and sections ({{#EACH_X}}) are validated.
ANNOTATION_RE = re.compile(r"->\s*\{\{\s*([#^/]?)\s*([^{}]*?)\s*\}\}")


def manifest_template_problems(text, scalars, sections):
    """Pure check of the manifest template: (a) parses as a YAML mapping, (b) keeps every expected
    top-level section, (c) every `-> {{MARKER}}` annotation names a placeholder defined in
    placeholders.md. Returns a list of problem strings (empty == clean)."""
    try:
        data = render.load_yaml(text)
    except Exception as exc:                       # a hand-edit that breaks YAML must be caught
        return [f"does not parse as YAML: {exc!r}"]
    if not isinstance(data, dict):
        return ["does not parse to a top-level mapping"]
    problems = [f"missing required top-level section '{s}'" for s in MANIFEST_SECTIONS
                if s not in data]
    known = scalars | sections
    for sigil, name in ANNOTATION_RE.findall(text):
        name = name.strip()
        if not name or name.endswith("_*"):
            continue                               # an illustrative wildcard, not a real placeholder
        if name not in known:
            marker = "{{" + sigil + name + "}}"
            problems.append(f"annotation '-> {marker}' names an undefined placeholder")
    return problems


def check_manifest_template(fail):
    name = "manifest-template"
    if not os.path.exists(MANIFEST_TEMPLATE):
        return  # a partial checkout without the template — nothing to validate
    scalars, sections = known_placeholders()
    for problem in manifest_template_problems(read(MANIFEST_TEMPLATE), scalars, sections):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 14. Data-file validity — the universal floor for the factory's machine-read data: every
#     .eados-core/**/*.yaml must parse with the hand-rolled loader. Most are already loaded by a
#     semantic check (profiles, os-specs, domains, lessons); this also covers the ones nothing else
#     parsed inside the self-lint — questionnaire.yaml, config/defaults.yaml, the reference manifest
#     — so a syntax slip in any data file fails here rather than at a consumer's render.
# ---------------------------------------------------------------------------
def data_file_problems(items):
    """items: (relpath, text) pairs for every tracked .eados-core YAML. Returns a problem per file
    that does not parse — empty == all data files are syntactically valid."""
    problems = []
    for rel, text in items:
        try:
            render.load_yaml(text)
        except Exception as exc:                       # a hand-edit that breaks YAML must be caught
            problems.append(f"{rel}: not valid YAML — {exc!r}")
    return problems


def check_data_files(fail):
    name = "data-file-validity"
    items = []
    for cur, _dirs, fns in os.walk(ROOT):
        for fn in fns:
            if fn.endswith((".yaml", ".yml")):
                path = os.path.join(cur, fn)
                items.append((os.path.relpath(path, REPO_ROOT).replace("\\", "/"), read(path)))
    for problem in data_file_problems(items):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 14b. Run-record schema — learning/runs/*.yaml is an externally-modifiable data class (per the
#      gate-coverage mandate). record_run.py (#172) gives it a real schema; a malformed record
#      silently poisons the auto-tuner and the lesson audit, so it must be inside the perimeter,
#      not prose. Syntax is data-file-validity's job (parse errors are its report); this validates
#      the STRUCTURE of the records that parse. The empty-dir state (only runs/README.md) is
#      trivially green — there is nothing to validate until the first record lands.
# ---------------------------------------------------------------------------
RUN_RECORD_REQUIRED = ("slug", "date", "lang", "kind", "outcome")


def run_record_problems(records):
    """records: (relpath, parsed_record) pairs. Validate each against the recorder schema
    (record_run.py: the five required keys; outcome vocabulary; date shape; overrides triples;
    failures {gate, message} with the outcome-consistency rule; rubric dims 0-2 drawn from the
    ten). Pure so the contract is unit-testable — empty == every record is well-formed."""
    problems = []

    def bad(rel, msg):
        problems.append(f"{rel}: {msg}")

    for rel, rec in records:
        if not isinstance(rec, dict):
            bad(rel, "a run record must be a YAML mapping")
            continue
        for key in RUN_RECORD_REQUIRED:
            if key not in rec or str(rec.get(key)).strip() == "":
                bad(rel, f"missing or empty required key '{key}'")
        date = str(rec.get("date", "")).strip()
        if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            bad(rel, f"date '{date}' is not YYYY-MM-DD")
        outcome = rec.get("outcome")
        if outcome is not None and outcome not in record_run.OUTCOMES:
            bad(rel, f"outcome {outcome!r} not one of {'|'.join(record_run.OUTCOMES)}")
        # #215: `phase` is an optional phase tag (records default to scaffold); when present it must
        # name a real delivery phase, so a mistyped phase can't slip into the ledger.
        phase = rec.get("phase")
        if phase is not None and phase not in record_run.PHASES:
            bad(rel, f"phase {phase!r} not one of {'|'.join(record_run.PHASES)}")

        overrides = rec.get("overrides", [])
        if not isinstance(overrides, list):
            bad(rel, "overrides must be a list")
        else:
            for i, ov in enumerate(overrides):
                if not isinstance(ov, dict) or not all(k in ov for k in ("key", "default", "chosen")):
                    bad(rel, f"overrides[{i}] must be a {{key, default, chosen}} mapping")
                elif str(ov.get("key")).strip() == "":
                    bad(rel, f"overrides[{i}] has an empty key")

        failures = rec.get("failures", [])
        if not isinstance(failures, list):
            bad(rel, "failures must be a list")
        else:
            for i, f in enumerate(failures):
                if not isinstance(f, dict) or "gate" not in f or "message" not in f:
                    bad(rel, f"failures[{i}] must be a {{gate, message}} mapping")
                elif str(f.get("gate")).strip() == "":
                    bad(rel, f"failures[{i}] has an empty gate")
            if failures and outcome != "failed":
                bad(rel, "a recorded failure means the run failed — outcome must be 'failed'")

        applied = rec.get("lessons_applied", [])
        if not isinstance(applied, list):
            bad(rel, "lessons_applied must be a list")
        else:
            for lid in applied:
                if not re.fullmatch(r"L-\d{4}", str(lid).strip()):
                    bad(rel, f"lessons_applied entry {lid!r} is not an L-NNNN id")

        rubric = rec.get("rubric", {})
        if not isinstance(rubric, dict):
            bad(rel, "rubric must be a mapping")
        else:
            for dim, score in rubric.items():
                if dim not in record_run.RUBRIC_DIMENSIONS:
                    bad(rel, f"rubric dimension {dim!r} is not one of the ten eval/rubric.md "
                             "dimensions")
                elif str(score).strip() not in ("0", "1", "2"):
                    bad(rel, f"rubric {dim} score {score!r} is not 0, 1, or 2")
    return problems


def check_run_records(fail):
    name = "run-records"
    runs_dir = os.path.join(ROOT, "learning", "runs")
    records = []
    for path in sorted(glob.glob(os.path.join(runs_dir, "*.yaml"))):
        rel = os.path.relpath(path, REPO_ROOT).replace("\\", "/")
        try:
            rec = render.load_yaml(read(path))
        except Exception:
            continue                        # a syntax error is data-file-validity's report
        records.append((rel, rec))
    for problem in run_record_problems(records):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 15. Gate coverage (meta-gate) — every tracked file is either covered by a named gate or
#     consciously allow-listed as human-reviewed prose (with a reason). A NEW file class that
#     nobody gated fails CI until it is gated or allow-listed — so coverage can never silently
#     regress. This is the enforcement behind "gate every externally-modifiable file": the
#     issue-#90 episode (project.yaml.template was gated by nothing) becomes structurally
#     impossible to repeat. `*` matches within a path segment; `**` spans directories.
# ---------------------------------------------------------------------------
GATE_COVERAGE = [
    (".eados-core/templates/**",                          "render-smoke + placeholder-integrity"),
    (".eados-core/orchestrator/profiles/*.yaml",          "profile-completeness"),
    (".eados-core/orchestrator/profiles/_schema.md",      "profile-completeness (schema)"),
    (".eados-core/orchestrator/os/**",                    "os-spec-completeness + cross-spec-consistency + gate-executability (workflow runs:)"),
    (".eados-core/orchestrator/domains/*.yaml",           "domains + data-file-validity"),
    (".eados-core/orchestrator/placeholders.md",          "placeholder-integrity (the dictionary)"),
    (".eados-core/orchestrator/generate.md",              "generate-references"),
    (".eados-core/orchestrator/project.yaml.template",    "manifest-template"),
    (".eados-core/orchestrator/examples/*.yaml",          "render-smoke (the reference manifest)"),
    (".eados-core/orchestrator/questionnaire.yaml",       "data-file-validity"),
    (".eados-core/orchestrator/triage.yaml",              "examples + data-file-validity"),
    (".eados-core/config/defaults.yaml",                  "data-file-validity"),
    (".eados-core/agent/*.md",                            "agent-registry"),
    (".eados-core/learning/lessons.yaml",                 "lessons + data-file-validity"),
    (".eados-core/learning/scope-examples.yaml",          "examples + data-file-validity"),
    (".eados-core/learning/runs/**",                      "run-records (schema) + data-file-validity"),
    (".eados-core/tools/*.py",                            "byte-compile + unit tests (CI)"),
    (".eados-core/tools/tests/*.py",                      "byte-compile + unit tests (CI)"),
    (".eados-core/docs/i18n/**",                          "i18n-freshness"),
    ("README.md",                                         "version-lockstep + i18n-freshness"),
    ("CHANGELOG.md",                                      "version-lockstep"),
    (".github/workflows/*.yml",                           "action-pins + workflow-safety"),
    ("setup/*.sh",                                        "installer-smoke (test_setup_sh.py) + shellcheck (CI)"),
    ("setup/*.command",                                   "installer-smoke (test_setup_sh.py) + shellcheck (CI)"),
    ("setup/*.ps1",                                       "installer-smoke (test_setup_ps1.py) + PowerShell parse-check (CI)"),
]
# Intentionally NOT machine-validated — prose/config under human review. Each needs a reason; this
# is the conscious record of "we looked and chose not to gate this", not a blind skip.
GATE_ALLOWLIST = [
    ("AGENTS.md",                                  "agent contract — human-reviewed prose"),
    ("CLAUDE.md",                                  "agent contract — human-reviewed prose"),
    ("GEMINI.md",                                  "agent contract — human-reviewed prose"),
    ("CONTRIBUTING.md",                            "governance prose — human-reviewed"),
    ("SECURITY.md",                                "governance prose — human-reviewed"),
    ("LICENSE",                                    "license text — render.py's source, exercised by render-smoke"),
    (".gitattributes",                             "VCS / bundle export-ignore config"),
    (".gitignore",                                 "VCS config"),
    (".eados-dev",                                 "repo marker file"),
    (".portfolio.json",                            "portfolio-card metadata"),
    (".issues/**",                                 "issue drafts / milestone backlog — human-reviewed prose"),
    (".github/CODEOWNERS",                         "GitHub config"),
    (".github/dependabot.yml",                     "GitHub config"),
    (".github/PULL_REQUEST_TEMPLATE.md",           "GitHub PR template"),
    (".github/ISSUE_TEMPLATE/**",                  "GitHub issue forms"),
    (".eados-core/README.md",                      "bundle entry-point prose"),
    (".eados-core/orchestrator/*.md",              "orchestrator playbook prose (interview, recovery, …)"),
    (".eados-core/orchestrator/commands/*.md",     "phase command playbook prose"),
    (".eados-core/orchestrator/domains/*.md",      "domain schema/readme prose"),
    (".eados-core/agent/domains/**",               "domain persona prose"),
    (".eados-core/config/*.md",                    "config prose (README, house-rules)"),
    (".eados-core/config/agents/**",               "user role-override dir"),
    (".eados-core/learning/*.md",                  "learning-ledger prose"),
    (".eados-core/docs/*.md",                      "docs prose (USAGE, walkthrough)"),
    (".eados-core/docs/adr/**",                    "ADR prose"),
    (".eados-core/docs/rfc/**",                    "RFC / roadmap / diagram prose"),
    (".eados-core/eval/**",                        "eval rubric prose"),
    (".eados-core/maintenance/**",                 "maintenance prose"),
    (".eados-core/tools/requirements-ci.txt",      "CI pinned + hashed deps (render-smoke)"),
    ("setup/*.bat",                                "Windows cmd double-click shim - trivial pass-through to setup.ps1 (the logic + its gate live there); no Linux analyzer"),
]


def _glob_re(pattern):
    """gitignore-ish glob: `*` matches within a path segment, `**` spans directories."""
    out, i = [], 0
    while i < len(pattern):
        if pattern[i:i + 2] == "**":
            out.append(".*"); i += 2
        elif pattern[i] == "*":
            out.append("[^/]*"); i += 1
        elif pattern[i] == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(pattern[i])); i += 1
    return re.compile("^" + "".join(out) + "$")


def gate_coverage_problems(tracked, covered=GATE_COVERAGE, allowlist=GATE_ALLOWLIST):
    """tracked: repo-relative paths. A problem for any file matched by neither a covered nor an
    allow-listed pattern. Pure (the registry is injectable) so the contract is unit-testable."""
    cov = [_glob_re(p) for p, _ in covered]
    allow = [_glob_re(p) for p, _ in allowlist]
    problems = []
    for path in tracked:
        if any(rx.match(path) for rx in cov):
            continue
        if any(rx.match(path) for rx in allow):
            continue
        problems.append(f"{path}: no gate covers it and it is not allow-listed — add a validating "
                        f"gate (GATE_COVERAGE) or, if it is reviewed prose, a GATE_ALLOWLIST entry")
    return problems


def check_gate_coverage(fail):
    name = "gate-coverage"
    tracked = _tracked_files()
    if tracked is None:
        return  # not a git checkout (e.g. an extracted bundle) — cannot enumerate the tree
    for problem in gate_coverage_problems(tracked):
        fail(name, problem)
    # registry hygiene: a pattern that matches nothing is dead weight / a moved path — surface it.
    for pattern, _ in GATE_COVERAGE + GATE_ALLOWLIST:
        rx = _glob_re(pattern)
        if not any(rx.match(t) for t in tracked):
            fail(name, f"stale registry entry — pattern matches no tracked file: '{pattern}'")


def _tracked_files():
    """The repo's tracked files (git ls-files), repo-relative with forward slashes. None when not
    in a git checkout — the meta-gate then skips, like the other checks do on a partial tree."""
    try:
        out = subprocess.run(["git", "-c", "core.quotePath=false", "ls-files"], cwd=REPO_ROOT,
                             capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# 16. Workflow safety — the external-contributor *security* surface. A workflow triggered by
#     `pull_request_target` or `workflow_run` runs with the base repo's secrets + write token on a
#     partially-untrusted event; combined with checking out PR-authored code it is the classic
#     secret-exfiltration / self-merge vector. Such triggers are forbidden — in this repo's own
#     workflows AND in the workflow templates shipped to every generated repo (a bad trigger there
#     has the widest blast radius) — unless a workflow is allow-listed with a justification.
#     Complements `action-pins` (which pins action SHAs); this guards the trigger surface.
# ---------------------------------------------------------------------------
SENSITIVE_TRIGGERS = ("pull_request_target", "workflow_run")
WORKFLOW_SAFETY_ALLOWLIST = {
    "dependabot-pin-sync.yml":
        "ADR-0013 — workflow_run runs the trusted default-branch workflow definition (never PR "
        "code), gated to actor==dependabot[bot] + same-repo (no forks), and executes only the "
        "repo's deterministic sync_action_pins.py.",
}
_TRIGGER_KEY_RE = re.compile(r"(?m)^\s{0,6}(pull_request_target|workflow_run)\s*:")
_ON_INLINE_RE = re.compile(r"(?m)^on\s*:\s*[\[{](.+)[\]}]\s*$")


def workflow_safety_problems(items, allowlist=WORKFLOW_SAFETY_ALLOWLIST):
    """items: (name, text) for each workflow (this repo's *.yml + the rendered *.tmpl). Flags any
    that uses a sensitive trigger unless allow-listed. `name` is the basename so a workflow and its
    template share one allow-list key. Pure (allow-list injectable) so the contract is testable."""
    problems = []
    for name, text in items:
        triggers = set(_TRIGGER_KEY_RE.findall(text))
        inline = _ON_INLINE_RE.search(text)
        if inline:
            triggers.update(t for t in SENSITIVE_TRIGGERS
                            if re.search(r"\b" + t + r"\b", inline.group(1)))
        if triggers and name not in allowlist:
            problems.append(f"{name}: uses sensitive trigger(s) {sorted(triggers)} that run with "
                            f"repository secrets on a partially-untrusted event — review and add to "
                            f"WORKFLOW_SAFETY_ALLOWLIST with a justification, or use pull_request/push")
    return problems


def _workflow_items():
    """(basename, text) for this repo's workflows + the rendered workflow templates. A template's
    trailing '.tmpl' is dropped so it shares an allow-list key with its rendered form."""
    items = []
    for root in (os.path.join(REPO_ROOT, ".github", "workflows"),
                 os.path.join(ROOT, "templates", ".github", "workflows")):
        if not os.path.isdir(root):
            continue
        for fn in sorted(os.listdir(root)):
            if fn.endswith((".yml", ".yaml", ".tmpl")):
                base = fn[:-5] if fn.endswith(".tmpl") else fn
                items.append((base, read(os.path.join(root, fn))))
    return items


def check_workflow_safety(fail):
    name = "workflow-safety"
    items = _workflow_items()
    if not items:
        return  # a partial checkout without workflows
    for problem in workflow_safety_problems(items):
        fail(name, problem)
    # hygiene: an allow-list entry for a workflow that is gone, or no longer uses a sensitive
    # trigger, is stale — surface it so the allow-list stays honest.
    by_name = {}
    for n, text in items:
        by_name.setdefault(n, text)
    for fname in WORKFLOW_SAFETY_ALLOWLIST:
        if fname not in by_name:
            fail(name, f"workflow-safety allow-list names a missing workflow: '{fname}'")
        elif not workflow_safety_problems([(fname, by_name[fname])], allowlist={}):
            fail(name, f"workflow-safety allow-list entry no longer needed (no sensitive trigger): "
                       f"'{fname}'")


# ---------------------------------------------------------------------------
# 17. Gate executability — the data→code seam of the workflow spec (#164). workflow.yaml's gate
#     registry documents `runs:` commands and `wired:` execution claims, but nothing executed the
#     declarative side, so it had already drifted (the documented `render.py --check` did not
#     exist). This check keeps the data honest: every `python <script> …` gate must name a script
#     that exists — in the factory checkout, or shipped under templates/ into every generated
#     repo — whose source mentions each `--flag` it is invoked with (a cheap static proxy for
#     "the flag is real"), and the set of gates marked `wired: in-process` must equal the
#     GATE_EVALUATORS registry in eados.py, so a gate wired (or unwired) in code without
#     updating the data fails here instead of rotting silently.
# ---------------------------------------------------------------------------
GATE_WIRED_VALUES = {"in-process", "external"}


def wired_in_process_ids(eados_source):
    """Gate ids the checker evaluates in-process, read statically from eados.py's
    GATE_EVALUATORS dict source (no import: the lint stays side-effect-free)."""
    m = re.search(r"GATE_EVALUATORS\s*=\s*\{(.*?)\}", eados_source, re.DOTALL)
    return set(re.findall(r"\"([\w-]+)\"\s*:", m.group(1))) if m else set()


def gate_executability_problems(gates, find_script, wired_in_code):
    """Pure check of the gate registry's executable claims. `gates`: workflow.yaml gates[];
    `find_script(rel)` -> the script's source text or None if it exists nowhere;
    `wired_in_code`: gate ids evaluated in-process. Returns problem strings (empty == honest)."""
    problems = []
    wired_in_data = set()
    for g in (gates if isinstance(gates, list) else []):
        if not isinstance(g, dict):
            continue
        gid = g.get("id", "?")
        wired = g.get("wired")
        if wired not in GATE_WIRED_VALUES:
            problems.append(f"gate '{gid}': wired must be one of "
                            f"{sorted(GATE_WIRED_VALUES)}, got {wired!r}")
        elif wired == "in-process":
            wired_in_data.add(gid)
        runs = str(g.get("runs") or "")
        if not runs.startswith("python "):
            continue                       # manual:/human: gates make no executable claim
        tokens = runs.split()
        script = tokens[1] if len(tokens) > 1 else ""
        source = find_script(script)
        if source is None:
            problems.append(f"gate '{gid}': runs references missing script '{script}'")
            continue
        for flag in (t for t in tokens[2:] if t.startswith("--")):
            if flag not in source:
                problems.append(f"gate '{gid}': script '{script}' does not know flag '{flag}'")
    for gid in sorted(wired_in_data - wired_in_code):
        problems.append(f"gate '{gid}' claims wired: in-process but eados.py's "
                        "GATE_EVALUATORS has no entry for it")
    for gid in sorted(wired_in_code - wired_in_data):
        problems.append(f"eados.py evaluates gate '{gid}' in-process but workflow.yaml "
                        "does not mark it wired: in-process")
    return problems


def find_gate_script(rel):
    """Resolve a gate's script path to its source text: a factory path (repo-root-relative,
    e.g. .eados-core/tools/render.py) or a generated-repo path the factory ships via
    templates/ (e.g. tools/consistency_lint.py, with or without a .tmpl suffix)."""
    for cand in (os.path.join(REPO_ROOT, rel.replace("/", os.sep)),
                 os.path.join(TEMPLATES, rel.replace("/", os.sep)),
                 os.path.join(TEMPLATES, rel.replace("/", os.sep) + ".tmpl")):
        if os.path.isfile(cand):
            return read(cand)
    return None


def check_gate_executability(fail):
    name = "gate-executability"
    workflow = _load_spec("workflow")
    if not isinstance(workflow, dict):
        return  # a missing/unparseable workflow spec is os-spec-completeness's report
    wired = wired_in_process_ids(read(os.path.join(TOOLS, "eados.py")))
    for problem in gate_executability_problems(workflow.get("gates"), find_gate_script, wired):
        fail(name, problem)


# ---------------------------------------------------------------------------
# 19. Worked-example decision surfaces (#224) — the judgment-laden "which way?" calls that used to
#     live only as prose (ask-vs-default in the interview, adopt/decline/escalate on a contribution,
#     apply-vs-skip a lesson's scope) are now few-shot policy AS DATA: an `examples:` block with a
#     verdict vocabulary and labelled cases. This validates their SHAPE only (never that the agent
#     obeyed them — that stays the reviewer's job, exactly like the lessons ledger): every case has
#     input+verdict+why, verdicts are drawn from the block's declared set, and the block covers >= 2
#     verdicts with >= 2 cases each (a genuine decision surface — >= 2 "positive" + >= 2 "negative").
# ---------------------------------------------------------------------------
EXAMPLE_FILES = (
    "orchestrator/os/contribution/contribution.yaml",   # adopt / decline / escalate
    "orchestrator/questionnaire.yaml",                  # ask / default
    "learning/scope-examples.yaml",                     # apply / skip (companion to the lessons ledger)
    "orchestrator/triage.yaml",                         # answer / focused-change / five-step-loop (Step-0)
    "orchestrator/os/routing/routing.yaml",             # fast / standard / frontier-reasoning (tier calls)
)
EXAMPLE_CASE_REQUIRED = ("input", "verdict", "why")


def examples_problems(name, data):
    """Pure shape check of one `examples:` block (a mapping with `verdicts` + `cases`). Returns a
    list of problem strings (empty == a well-formed decision surface). No I/O — unit-testable."""
    problems = []
    ex = data.get("examples") if isinstance(data, dict) else None
    if ex is None:
        return [f"{name}: no `examples:` block — issue #224 requires a worked-example decision surface"]
    if not isinstance(ex, dict):
        return [f"{name}: `examples:` must be a mapping with `verdicts` and `cases`"]
    verdicts = ex.get("verdicts")
    if not isinstance(verdicts, list) or len(verdicts) < 2:
        problems.append(f"{name}: `examples.verdicts` must list >= 2 allowed verdicts")
        verdicts = verdicts if isinstance(verdicts, list) else []
    vset = {str(v).strip() for v in verdicts}
    cases = ex.get("cases")
    if not isinstance(cases, list) or not cases:
        problems.append(f"{name}: `examples.cases` must be a non-empty list")
        cases = []
    counts = {}
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            problems.append(f"{name}: `examples.cases[{i}]` must be a mapping")
            continue
        for key in EXAMPLE_CASE_REQUIRED:
            if not str(case.get(key, "")).strip():
                problems.append(f"{name}: `examples.cases[{i}]` missing/empty '{key}'")
        verdict = str(case.get("verdict", "")).strip()
        if verdict and vset and verdict not in vset:
            problems.append(f"{name}: `examples.cases[{i}]` verdict '{verdict}' not in "
                            f"verdicts {sorted(vset)}")
        elif verdict:
            counts[verdict] = counts.get(verdict, 0) + 1
    covered = [v for v, n in counts.items() if n >= 2]
    if len(covered) < 2:
        problems.append(f"{name}: `examples` must cover >= 2 verdicts with >= 2 cases each "
                        f"(>= 2 positive + >= 2 negative); have {counts or '{}'}")
    return problems


def check_examples(fail):
    name = "examples"
    for rel in EXAMPLE_FILES:
        path = os.path.join(ROOT, *rel.split("/"))
        if not os.path.exists(path):
            fail(name, f"{rel}: expected an `examples:` decision surface (#224) but the file is missing")
            continue
        try:
            data = render.load_yaml(read(path))
        except (ValueError, OSError) as exc:
            fail(name, f"{rel}: cannot parse for the examples check ({exc!r})")
            continue
        for problem in examples_problems(rel, data):
            fail(name, problem)


# ---------------------------------------------------------------------------
# 19. safe-write containment (#235, guards #195/#196) — every file write in the factory's tools
#     must route through `sandbox` (safe_write/resolve), the single guarded sink that closed the
#     `render --in-place` clobber (#195) and the `.git`-segment escape (#196). render.write_file
#     is now a pure delegator to sandbox.safe_write; a tool that opens its own truncating write
#     path bypasses the containment + no-clobber + `.git` refusal and silently re-opens that defect
#     class. The factory-internal writers that legitimately write OUTSIDE a rendered repo — the
#     learning ledger, a maintainer `--out`, the factory's own workflow templates — are allow-listed
#     WITH a justification (mirroring WORKFLOW_SAFETY_ALLOWLIST), and the sandbox primitive itself is
#     the sink they all funnel into. Symmetric hygiene: an allow-list entry that no longer writes
#     directly is flagged stale, exactly like workflow-safety and agent-registry.
# ---------------------------------------------------------------------------
SAFE_WRITE_ALLOWLIST = {
    "sandbox.py": "the guarded write primitive itself — safe_write's open() is the single sink "
                  "every other writer funnels through (containment + .git refusal + no-clobber)",
    "record_run.py": "writes the factory's own learning ledger under learning/runs/ with its own "
                     "#197 same-day no-clobber suffix; never a rendered-repo path",
    "derive_links.py": "writes the traceability links file to an explicit maintainer --out (or "
                       "stdout) — a CI/factory artifact, not a rendered repo file",
    "sync_action_pins.py": "rewrites the factory's OWN templates/**/.github workflows in --fix "
                           "mode; never a rendered-repo path",
}

# The lint reads its own source when it walks the tools dir; its regex literals below name the very
# write verbs it hunts for, which would self-trip. A lint that performs no file writes need not
# police itself — exclude it rather than allow-list it (an entry that never fires reads as noise).
SAFE_WRITE_UNSCANNED = {"eados_lint.py"}

# Direct file-creation/write sites: open(...) with a w/a/x/+ mode, pathlib write_*, os.replace/
# rename, shutil copy/move. A static proxy (like gate-executability's flag check) — good enough to
# catch a new private write path; the allow-list carries the reviewed exceptions.
_DIRECT_WRITE_RE = re.compile(
    r"""open\([^)]*["'][rbt+]*[wax][rwaxbt+]*["']"""             # open(..., "w"/"a"/"x"/"w+"/"wb"…)
    r"""|\.write_text\(|\.write_bytes\("""                       # pathlib.Path.write_*
    r"""|\bos\.(?:replace|rename)\("""                           # atomic replace / rename
    r"""|\bshutil\.(?:copy|copyfile|copy2|copytree|move)\("""    # shutil file copy/move
)


def _strip_line_comments(text):
    """Drop whole-line `#` comments so a commented-out example write isn't flagged. Inline comments
    and docstrings are left in — a proxy check tolerates the rare docstring hit, and the
    guard-required scope plus the allow-list keep false positives out of practice."""
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def safe_write_problems(items, allowlist=SAFE_WRITE_ALLOWLIST):
    """items: (basename, source_text) per tool module. Flags a direct file-write outside the
    allow-list. Pure (allow-list injectable) so the synthetic-direct-write contract is testable."""
    problems = []
    for name, text in items:
        if name in allowlist:
            continue
        if _DIRECT_WRITE_RE.search(_strip_line_comments(text)):
            problems.append(
                f"{name}: opens a file for writing directly instead of routing through "
                f"sandbox.safe_write — the containment / .git / no-clobber guard that closed "
                f"#195/#196 is bypassed. Delegate to sandbox.safe_write/resolve, or add '{name}' "
                f"to SAFE_WRITE_ALLOWLIST with a justification if it writes outside a rendered repo")
    return problems


def _tool_sources():
    """(basename, source) for each production tool module (tests/, __pycache__, and the lint's own
    self-tripping source excluded)."""
    items = []
    for fn in sorted(os.listdir(TOOLS)):
        if fn.endswith(".py") and fn not in SAFE_WRITE_UNSCANNED:
            items.append((fn, read(os.path.join(TOOLS, fn))))
    return items


def check_safe_write(fail):
    name = "safe-write"
    items = _tool_sources()
    if not items:
        return  # a partial checkout without the tools
    for problem in safe_write_problems(items):
        fail(name, problem)
    by_name = {n: t for n, t in items}
    for fname in SAFE_WRITE_ALLOWLIST:
        if fname not in by_name:
            fail(name, f"safe-write allow-list names a missing tool: '{fname}'")
        elif not safe_write_problems([(fname, by_name[fname])], allowlist={}):
            fail(name, f"safe-write allow-list entry no longer needed (no direct write): '{fname}'")


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
    check_version_lockstep,
    check_roadmap_freshness,
    check_manifest_template,
    check_data_files,
    check_run_records,
    check_gate_coverage,
    check_workflow_safety,
    check_gate_executability,
    check_examples,
    check_safe_write,
]


def run_checks(checks=CHECKS):
    """Run `checks`, each receiving its own view of the one reporter. Returns the (check,
    message) findings — the accumulator lives HERE, per run, not in the module (#167)."""
    failures = []

    def fail(check, message):
        failures.append((check, message))

    for fn in checks:
        try:
            fn(fail)
        except Exception as exc:  # a crashing check is itself a failure
            fail(fn.__name__, f"check crashed: {exc!r}")
    return failures


def main():
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    failures = run_checks()
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
