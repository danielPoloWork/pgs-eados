#!/usr/bin/env python3
"""Deterministic template renderer for EADOS (the Mustache subset of placeholders.md).

Dependency-free (Python 3 standard library only). Turns a confirmed project manifest into a
rendered repository, replacing the "careful manual pass" with a reproducible one:

    python tools/render.py orchestrator/project.yaml --in-place   # or: --out <dir-outside-eados>

It implements exactly the substitution grammar the dictionary documents:
  - {{SCALAR}}                       a manifest-derived value
  - {{#IF_FLAG}}...{{/IF_FLAG}}      render when the flag is truthy
  - {{^IF_FLAG}}...{{/IF_FLAG}}      render when the flag is falsy
  - {{#EACH_LIST}}...{{/EACH_LIST}}  repeat per item; {{.}} is the scalar item, {{field}} a field
GitHub Actions ${{ ... }} expressions are left untouched. An unresolved {{UPPER}} placeholder
is a hard error (the render aborts and lists them), per placeholders.md rendering rule 1.

The YAML loader lives in the sibling `yamlmini.py` (#166) — extracted so the parser under
every gate cannot be perturbed by renderer changes. `render.load_yaml` stays a re-export, so
every existing caller works unchanged.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yamlmini import load_yaml  # noqa: E402,F401  — re-exported for every render.load_yaml caller
import sandbox  # noqa: E402  — the ONE write-containment path, shared with the migrate phase

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")

SECTION_RE = re.compile(r"\{\{([#^])([A-Z][A-Z0-9_]*)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)
VAR_RE = re.compile(r"(?<!\$)\{\{\s*([^{}]+?)\s*\}\}")
UPPER_RE = re.compile(r"[A-Z][A-Z0-9_]*$")


# ---------------------------------------------------------------------------
# Manifest -> render context (scalars, boolean flags, list sections).
# ---------------------------------------------------------------------------
def _map(d, key):
    """A known section/sub-mapping must be a mapping; anything else degrades to {} so
    build_context never crashes on a mis-typed manifest (validate_manifest reports it)."""
    v = d.get(key) if isinstance(d, dict) else None
    return v if isinstance(v, dict) else {}


def build_context(m):
    if not isinstance(m, dict):
        m = {}
    ident = _map(m, "identity")
    own = _map(m, "ownership")
    lang = _map(m, "language")
    tool = _map(m, "toolchain")
    cmds = _map(tool, "commands")
    ci = _map(m, "ci")
    gov = _map(m, "governance")
    caps = _map(gov, "capabilities")
    spec = _map(m, "spec")
    i18n = _map(m, "i18n")
    ann = _map(m, "announce")

    slug = ident.get("project_slug", "")
    gpath = lang.get("group_path", "")  # no fallback: REQUIRED_SCALARS guards {{GROUP_PATH}} (#163)
    lng = lang.get("lang", "")
    bench = bool(caps.get("bench"))
    pkg_eco = tool.get("package_ecosystem", "") or ""
    series = ident.get("project_series", "") or ""

    scalars = {
        "PROJECT_NAME": ident.get("project_name", ""),
        "PROJECT_SLUG": slug,
        "PROJECT_TITLE": ident.get("project_title", ""),
        "PROJECT_TAGLINE": ident.get("project_tagline", ""),
        "PROJECT_SERIES": series,
        "PROJECT_KIND": ident.get("project_kind", ""),
        "OWNER": own.get("owner", ""),
        "MAINTAINER": own.get("maintainer", ""),
        "AUTHOR": own.get("author", ""),
        "YEAR": own.get("year", ""),
        "LICENSE_ID": own.get("license_id", ""),
        "DEFAULT_BRANCH": own.get("default_branch", ""),
        "ASSIGNEE": own.get("assignee") or own.get("owner", ""),   # #141: blank -> the owner, never "@me"
        "POSTURE": gov.get("posture") or "standard",   # standard (default) | enterprise (Q0.5, ADR-0015)
        "START_VERSION": gov.get("start_version", "0.0.0"),
        "VERSION_START": gov.get("version_start", ""),
        "LANG": lng,
        "LANG_NAME": lang.get("lang_name", ""),
        "LANG_STANDARD": lang.get("lang_standard", ""),
        "GROUP_PATH": gpath,
        "GROUP_DOTTED": lang.get("group_dotted", ""),
        "NAMESPACE": lang.get("namespace", ""),
        "SRC_EXT": lang.get("src_ext", ""),
        "PUBLIC_INCLUDE_HINT": lang.get("public_include_hint", ""),
        "SRC_MAIN": f"src/main/{lng}/{gpath}/{slug}",
        "SRC_TEST": f"src/test/{lng}/{gpath}/{slug}",
        "SRC_BENCH": f"src/bench/{lng}/{gpath}/{slug}" if bench else "",
        "BUILD_TOOL": tool.get("build_tool", ""),
        "PKG_MANAGER": tool.get("pkg_manager", ""),
        "TEST_FRAMEWORK": tool.get("test_framework", ""),
        "FORMATTER": tool.get("formatter", ""),
        "LINTER": tool.get("linter", ""),
        "SANITIZERS": tool.get("sanitizers", ""),
        "COVERAGE_TOOL": tool.get("coverage_tool", ""),
        "COVERAGE_TARGET": tool.get("coverage_target", ""),
        "DOC_TOOL": tool.get("doc_tool", ""),
        "VERSION_FILE": tool.get("version_file", ""),
        "VERSION_CONST_HINT": tool.get("version_const_hint", ""),
        "PKG_ECOSYSTEM": pkg_eco,
        "CMD_BUILD": cmds.get("build", ""),
        "CMD_TEST": cmds.get("test", ""),
        "CMD_FORMAT_CHECK": cmds.get("format_check", ""),
        "CMD_LINT": cmds.get("lint", ""),
        "CMD_BENCH": cmds.get("bench", ""),
        "TIER1_PLATFORMS": ci.get("tier1_platforms", ""),
        "CI_SETUP_STEPS": ci.get("setup_steps", ""),
        "CI_EXTRA_JOBS": ci.get("extra_jobs", ""),
        "CI_RACE_JOB": ci.get("race_job", ""),
        "SPEC_OBJECTIVE": spec.get("objective", ""),
        "SPEC_ARCHITECTURE": spec.get("architecture", ""),
        "ARCHITECTURE_STYLE": spec.get("architecture_style", ""),          # #151: structured §5 style
        "PATTERN_DISCIPLINE": spec.get("pattern_discipline") or "advisory",  # advisory (default) | enforced
        "SPEC_VERIFICATION": spec.get("verification", ""),
        "CODE_COMMENT_LANG": lang.get("comment_lang") or "en",   # #150: comment language, default en
        "DOC_DEFAULT_LANG": i18n.get("default_lang", "en"),
        "I18N_ENABLED": "True" if caps.get("i18n") else "False",
        "HOUSE_RULES": gov.get("house_rules", ""),
    }
    scalars = {k: ("" if v is None else str(v)) for k, v in scalars.items()}

    flags = {
        "IF_BENCH": bench,
        "IF_THREADING": bool(caps.get("threading")),
        "IF_PUBLIC_API": bool(caps.get("public_api")),
        "IF_I18N": bool(caps.get("i18n")),
        "IF_PACKAGING": bool(caps.get("packaging")),
        "IF_SERVICE": bool(caps.get("service")),
        "IF_ANNOUNCE": bool(caps.get("announce")),
        "IF_SERIES": bool(series.strip()),
        "IF_PKG_ECOSYSTEM": bool(pkg_eco.strip()),
        "IF_HOUSE_RULES": bool(str(gov.get("house_rules", "") or "").strip()),
        "IF_ARCHITECTURE_STYLE": bool(str(spec.get("architecture_style", "") or "").strip()),  # #151
        "IF_ENTERPRISE": (gov.get("posture") or "standard").strip().lower() == "enterprise",  # #248, ADR-0015
        "IF_LAYERED": bool(caps.get("layered")),   # #152: opt-in layered package skeleton
        "IF_API_SPEC": bool(caps.get("api_spec")),  # #240: opt-in docs/api/ OpenAPI/IDL stub (service/web)
        # #150: recorded authoring-language exceptions (ADR-0016) — non-English choices render an
        # explicit exception block into the generated AGENTS.md §2 instead of silently deviating.
        "IF_COMMENT_LANG_NONEN": scalars["CODE_COMMENT_LANG"].strip().lower() not in ("", "en"),
        "IF_DOC_LANG_NONEN": scalars["DOC_DEFAULT_LANG"].strip().lower() not in ("", "en"),
    }

    sections = {
        "EACH_CI_CELL": ci.get("matrix", []) or [],
        "EACH_SCOPE": gov.get("scopes", []) or [],
        "EACH_FUNCTIONAL_REQ": spec.get("functional_reqs", []) or [],
        "EACH_NONFUNCTIONAL_REQ": spec.get("nonfunctional_reqs", []) or [],
        "EACH_PUBLIC_API": spec.get("public_api", []) or [],
        "EACH_MILESTONE1_ITEM": spec.get("milestone1_items", []) or [],
        "EACH_MILESTONE": spec.get("milestones", []) or [],
        "EACH_PATTERN": spec.get("patterns", []) or [],   # #151: expected first-class patterns (name, why)
        "EACH_LAYER": spec.get("layers", []) or [],       # #152: layered package skeleton (name, purpose)
        "EACH_DOC_LANG": i18n.get("targets", []) or [],
        "EACH_ANNOUNCE_CHANNEL": ann.get("channels", []) or [],
    }
    return scalars, flags, sections


# ---------------------------------------------------------------------------
# Manifest pre-render validation (catch silent mistakes the renderer would paper over).
# ---------------------------------------------------------------------------
KNOWN_SECTIONS = {
    "identity", "ownership", "language", "toolchain", "ci",
    "governance", "i18n", "announce", "spec",
    "delivery_state",   # EADOS persistent delivery state (M1-B); state, not a placeholder source
    "interview",        # interview provenance — asked|defaulted|imported per answer key (#169);
                        # state for the confirmation step + the learning loop, never a placeholder source
    "adoption",         # brownfield adoption record — goals + gap_map_ref + its own provenance
                        # (#247, ADR-0021); state written by /eados adopt, never a placeholder source
}

# Known top-level SCALARS (not sections). `schema_version` versions the manifest schema for
# backward-compatible evolution (RFC-0001 §8 / OQ1); `domain` selects the target profile
# (orchestrator/domains/<domain>.yaml, M1-C); `manifest_rev` is the optimistic-concurrency counter
# (#214). All are metadata, not sections/placeholders.
KNOWN_SCALARS = {"schema_version", "domain", "manifest_rev"}

# How an interview answer got its value (#169): posed to the maintainer, assumed from the
# questionnaire default (and echoed back at confirmation), or carried in from an existing
# artifact (e.g. a validated PRD/SRS import, Q5.0).
_PROVENANCE_VALUES = {"asked", "defaulted", "imported"}

# Top-level keys that carry no interview answer, so need no provenance entry: the schema version
# (system metadata) and the state/meta sections. EVERY other top-level key present in the
# manifest must appear in interview.provenance (#201) — a partial block silently starves override
# derivation (derive_overrides treats an unrecorded key exactly like an explicitly `defaulted` one).
# `adoption` is exempt because its provenance lives INSIDE the block (#247, ADR-0021 §2).
PROVENANCE_EXEMPT = {"schema_version", "manifest_rev", "delivery_state", "interview", "adoption"}

# The brownfield adoption goal menu (#247, ADR-0021): what a maintainer may ask of an adopted
# repository. Closed — extending it takes an ADR, like every command-surface class (ADR-0019).
_ADOPTION_GOALS = {"governance-docs", "retro-design", "audit", "migrate", "bugfix"}
_ADOPTION_KEYS = {"goals", "gap_map_ref", "provenance"}


def adoption_problems(adoption):
    """Shape problems of a manifest's `adoption:` block (#247, ADR-0021): `goals` (non-empty,
    from the closed menu), `gap_map_ref` (where the read-only brownfield.py report was captured),
    and its own `provenance` sub-block (the section is PROVENANCE_EXEMPT — its provenance lives
    here, like delivery_state's state lives inside delivery_state). One source of truth for the
    shape: validate_manifest calls it when the section is present, and eados.py's
    `adoption-recorded` gate evaluator calls it directly."""
    problems = []
    if not isinstance(adoption, dict):
        return ["adoption must be a mapping (goals, gap_map_ref, provenance)"]
    for key in sorted(adoption):
        if key not in _ADOPTION_KEYS:
            problems.append(f"adoption.{key} is not a recognized key (expected one of: "
                            f"{', '.join(sorted(_ADOPTION_KEYS))})")
    goals = adoption.get("goals")
    if not isinstance(goals, list) or not goals:
        problems.append("adoption.goals must be a non-empty list drawn from "
                        f"{'|'.join(sorted(_ADOPTION_GOALS))} (ADR-0021)")
    else:
        for goal in goals:
            # isinstance guard: a hand-edited nested mapping is unhashable — it must land as a
            # problem string, never a TypeError traceback (the gate's malformed -> FAIL contract).
            if not isinstance(goal, str) or goal not in _ADOPTION_GOALS:
                problems.append(f"adoption.goals contains {goal!r} — not in the closed menu "
                                f"{'|'.join(sorted(_ADOPTION_GOALS))} (ADR-0021)")
    if not str(adoption.get("gap_map_ref") or "").strip():
        problems.append("adoption.gap_map_ref is missing or empty — record where the "
                        "brownfield.py gap map was captured")
    prov = adoption.get("provenance")
    if not isinstance(prov, dict) or not prov:
        problems.append("adoption.provenance must be a non-empty mapping of adoption "
                        "answer key -> asked|defaulted|imported")
    else:
        for key in sorted(prov):
            if key not in _ADOPTION_KEYS - {"provenance"}:
                problems.append(f"adoption.provenance names '{key}' which is not an adoption "
                                "answer key (goals, gap_map_ref)")
            # isinstance guard: an unhashable (nested-mapping) value must be a problem, not a crash.
            if not isinstance(prov[key], str) or prov[key] not in _PROVENANCE_VALUES:
                problems.append(f"adoption.provenance['{key}'] must be one of "
                                f"asked|defaulted|imported, got {prov[key]!r}")
        if "goals" not in prov:
            problems.append("adoption.provenance has no entry for 'goals' — the elicited "
                            "goal-menu answer must record how it was settled (#201 discipline)")
    return problems

# Scalars without which the generated repo is structurally broken (blank title, no owner,
# no license, nowhere to put source). build_context defaults every scalar to "", so without
# this guard a manifest missing these would render a hollow repo and still print "Render: OK".
REQUIRED_SCALARS = (
    "PROJECT_NAME", "PROJECT_SLUG", "PROJECT_KIND",
    "OWNER", "LICENSE_ID", "DEFAULT_BRANCH",
    "LANG", "GROUP_PATH",
)

# Fields that become filesystem path segments (src tree, spec filename). Anything other than
# plain segments — a path separator beyond '/', '.', '..', or an absolute/drive-qualified
# value — would let the manifest steer writes outside --out. Rejected before any file is
# created; write_file enforces a second, defense-in-depth containment check.
_SAFE_SEGMENT = re.compile(r"[A-Za-z0-9._-]+\Z")


def _unsafe_path_value(value):
    """True if `value` cannot be used as one or more safe relative path segments. A `.git` segment
    at any depth is refused by EXACT match — it steers writes into VCS metadata (`.git/hooks/` is an
    execution vector on the next commit), the same corruption class sandbox.resolve refuses. The
    exact match keeps a `.gitignore` file and a `foo.git/` directory legal. Refusing it here makes
    the failure land at manifest validation (`--check`), before write_file's sandbox backstop."""
    for part in str(value).replace("\\", "/").split("/"):
        if part in ("", ".", "..", ".git") or not _SAFE_SEGMENT.match(part):
            return True
    return False


def validate_manifest(m, scalars):
    """Guards that turn quiet manifest mistakes into a hard, actionable failure: an
    unknown/misspelled top-level section (which would otherwise resolve to an empty mapping
    and blank every field under it), a missing required field, a path-unsafe identifier, and
    a non-numeric start version (the classic `start_version`/`version_start` swap)."""
    problems = []
    if not isinstance(m, dict):
        return [f"manifest root must be a mapping, got {type(m).__name__}"]
    for key, val in m.items():
        if key in KNOWN_SCALARS:
            continue  # a known top-level scalar (e.g. schema_version), not a section
        if key not in KNOWN_SECTIONS:
            problems.append(
                f"unknown top-level section '{key}' (typo? expected one of: "
                f"{', '.join(sorted(KNOWN_SECTIONS))})"
            )
        elif val is not None and not isinstance(val, dict):
            problems.append(f"section '{key}' must be a mapping, got {type(val).__name__}")
    for key in REQUIRED_SCALARS:
        if not str(scalars.get(key, "")).strip():
            problems.append(f"required field for {{{{{key}}}}} is missing or empty")
    for field, key in (("identity.project_slug", "PROJECT_SLUG"),
                       ("language.lang", "LANG"),
                       ("language.group_path", "GROUP_PATH")):
        val = str(scalars.get(key, "")).strip()
        if val and _unsafe_path_value(val):
            problems.append(
                f"{field} '{val}' is not a safe path segment "
                "(no path separators beyond '/', no '.', '..', '.git', or absolute paths)"
            )
    sv = scalars.get("START_VERSION", "")
    if sv and not re.fullmatch(r"\d+\.\d+\.\d+", sv):
        problems.append(
            f"governance.start_version '{sv}' is not a numeric X.Y.Z version "
            "(did you swap it with version_start?)"
        )
    # #248: the governance posture is a closed vocabulary (ADR-0015). A typo or wrong case
    # (`entrprise`, `Enterprise`) would silently degrade to a `standard` repo with the raised-bar
    # clauses missing — exactly the silently-defaulted-answer failure this materialization closes.
    # Fail loud at --check instead. Absent == the `standard` default (POSTURE handles the fallback).
    posture = _map(m, "governance").get("posture")
    if posture is not None and str(posture) not in ("standard", "enterprise"):
        problems.append(f"governance.posture '{posture}' is not one of standard|enterprise "
                        "(ADR-0015; a typo would silently render a standard repo)")
    # #214: the optimistic-concurrency counter is a non-negative integer when present (absent == 0).
    rev = m.get("manifest_rev")
    if rev is not None and not (isinstance(rev, int) and not isinstance(rev, bool) and rev >= 0):
        problems.append(f"manifest_rev must be a non-negative integer (the optimistic-concurrency "
                        f"counter, #214), got {rev!r}")
    # #170: the spec-substance floor. The deterministic (no-agent) path had no floor at all — a
    # manifest with an empty spec rendered "Render: OK" and a hollow repository (blank SPEC.md,
    # a roadmap with nothing beyond the bootstrap). A FLOOR, not a taste test: presence only;
    # measurability stays the rubric's job (eval/rubric.md). No library escape hatch — even a
    # library has an objective and one requirement.
    spec = _map(m, "spec")
    if not str(spec.get("objective") or "").strip():
        problems.append("spec.objective is empty — the spec floor requires a stated objective "
                        "(what the project exists to do)")
    freqs = spec.get("functional_reqs")
    if not [r for r in (freqs if isinstance(freqs, list) else []) if str(r or "").strip()]:
        problems.append("spec.functional_reqs is empty — the spec floor requires at least one "
                        "functional requirement")
    if not str(spec.get("verification") or "").strip():
        problems.append("spec.verification is empty — the spec floor requires a verification "
                        "strategy (how CI proves a requirement failed)")
    mss = spec.get("milestones")
    if not (isinstance(mss, list) and any(isinstance(e, dict) for e in mss)):
        problems.append("spec.milestones is empty — the roadmap is defined up front (interview "
                        "Phase 5): record at least one forward milestone (number, title, goal, "
                        "items)")
    # #169: the interview provenance block is state with a fixed shape — a wrong value or a
    # dangling key would silently defeat the asked-vs-defaulted audit trail it exists to carry.
    # Optional (legacy manifests pass), but when present it must be honest.
    iv = m.get("interview")
    if isinstance(iv, dict):
        # #201: the block is mandated complete (interview.md) — questionnaire_version set and one
        # provenance entry per answer key. The #169 guard checked only the shape of what was
        # present, so a PARTIAL block passed and silently suppressed override derivation.
        if not str(iv.get("questionnaire_version") or "").strip():
            problems.append("interview.questionnaire_version is missing or empty — set it to "
                            "questionnaire.yaml's meta.version (#201)")
        prov = iv.get("provenance")
        if not isinstance(prov, dict) or not prov:
            problems.append("interview.provenance must be a non-empty mapping of "
                            "top-level manifest key -> asked|defaulted|imported")
        else:
            for key in sorted(prov):
                if prov[key] not in _PROVENANCE_VALUES:
                    problems.append(
                        f"interview.provenance['{key}'] must be one of "
                        f"asked|defaulted|imported, got {prov[key]!r}")
                if key not in m:
                    problems.append(
                        f"interview.provenance names '{key}' which is not a top-level key "
                        "of this manifest")
            # Coverage: an answer-bearing section present in the manifest but MISSING from
            # provenance is silently treated as `defaulted` and derives no override — the quiet,
            # compounding failure that starves autotune / lesson_audit. Require an entry for each.
            missing = sorted(k for k in m if k not in PROVENANCE_EXEMPT and k not in prov)
            if missing:
                problems.append(
                    "interview.provenance is incomplete — no entry for "
                    f"{', '.join(missing)}; record every answer key (an unrecorded section is "
                    "silently treated as defaulted and derives no override, #201)")
    # #247 / ADR-0021: the brownfield adoption block is state + elicited answers with a fixed
    # shape — a malformed block would silently defeat the `adoption-recorded` gate it feeds.
    # Optional (greenfield manifests pass); when present it must be honest. Non-dict values are
    # already rejected by the generic section-must-be-a-mapping check above.
    if isinstance(m.get("adoption"), dict):
        problems += adoption_problems(m["adoption"])
    # #199: delivery-state consistency. `delivery_state.checkpoints` must be a legal, contiguous
    # transition chain ending at the current phase, and a human-gated move must carry a
    # `confirmed_by:` — so `phase: scaffold` can no longer be asserted without the intervening
    # init->design->plan->scaffold checkpoints (the honor-system phase-skip). Optional (a legacy
    # manifest with no delivery_state passes). The chain logic + workflow live in phase_runner;
    # importing it here (lazily, to avoid a module-level import cycle — phase_runner imports render)
    # keeps ONE workflow engine. A missing/unreadable workflow.yaml degrades to "unchecked" rather
    # than blocking manifest validation on a factory-file problem.
    if isinstance(m.get("delivery_state"), dict):
        try:
            import phase_runner   # noqa: E402 — lazy: breaks the render<->phase_runner import cycle
            workflow = phase_runner.apply_overlay(phase_runner.load_workflow(),
                                                  phase_runner.manifest_domain(m))
            problems += phase_runner.checkpoint_chain_problems(m, workflow)
        except (OSError, ValueError):
            pass
    return problems


# ---------------------------------------------------------------------------
# Render engine.
# ---------------------------------------------------------------------------
def render(tmpl, scalars, flags, sections, local=None, where="", errors=None):
    # `errors` accumulates unresolved placeholders/fields. It is threaded explicitly (not a
    # module global) so render() is reentrant: standalone calls are self-contained, and one
    # run's failures never leak into the next. Callers that need the list pass their own.
    if errors is None:
        errors = []

    def repl_section(m):
        kind, name, body = m.group(1), m.group(2), m.group(3)
        # Nested loop over a list FIELD of the current item: {{#ITEMS}} inside {{#EACH_MILESTONE}}
        # iterates that milestone's `items`. The section name lowercased is the field, so a loop
        # item shadows a same-named global section (each milestone owns its own items).
        local_list = local.get(name.lower()) if isinstance(local, dict) else None
        if isinstance(local_list, list):
            if kind == "#":
                return "".join(
                    render(body, scalars, flags, sections, it, where, errors) for it in local_list
                )
            return render(body, scalars, flags, sections, local, where, errors) if not local_list else ""
        if name in sections:
            items = sections[name]
            if kind == "#":
                return "".join(
                    render(body, scalars, flags, sections, it, where, errors) for it in items
                )
            return render(body, scalars, flags, sections, local, where, errors) if not items else ""
        truthy = flags.get(name, False)
        keep = truthy if kind == "#" else not truthy
        return render(body, scalars, flags, sections, local, where, errors) if keep else ""

    out = SECTION_RE.sub(repl_section, tmpl)

    def block_indent(m, value):
        # If a multi-line value sits alone on an indented line, indent its continuation
        # lines to the same column (so injected YAML blocks nest correctly).
        if "\n" not in value:
            return value
        s = m.string
        line_start = s.rfind("\n", 0, m.start()) + 1
        prefix = s[line_start:m.start()]
        if prefix.strip():
            return value
        body = value[:-1] if value.endswith("\n") else value
        return body.replace("\n", "\n" + prefix)

    def repl_var(m):
        tok = m.group(1).strip()
        if tok == ".":
            return str(local) if isinstance(local, (str, int, float)) else ""
        if UPPER_RE.match(tok):
            if tok in scalars:
                return block_indent(m, scalars[tok])
            errors.append(f"{where}: unresolved placeholder {{{{{tok}}}}}")
            return ""
        if isinstance(local, dict) and tok in local:
            v = local[tok]
            return "" if v is None else str(v)
        errors.append(f"{where}: unresolved field {{{{{tok}}}}}")
        return ""

    return VAR_RE.sub(repl_var, out)


# ---------------------------------------------------------------------------
# File walking / output.
# ---------------------------------------------------------------------------
NOT_RENDERED = {"README.md"}  # templates/README.md is the templates-dir meta-doc


def out_relpath(rel, slug):
    if rel == "docs/specs/01_spec.md.tmpl":
        return f"docs/specs/01_spec_{slug}.md"
    if rel.endswith(".tmpl"):
        rel = rel[:-5]
    if rel == "gitignore":
        return ".gitignore"
    return rel


def write_file(out_dir, rel, text, overwrite=False):
    # One write path for the whole factory: delegate to sandbox.safe_write so containment
    # (realpath + commonpath), the `.git`-at-any-depth refusal, and the additive no-clobber guard
    # are a SINGLE implementation shared with the migrate phase (ADR-0007) — the renderer and the
    # sandbox can no longer drift. `overwrite=True` (via --force) is the only way to clobber; on a
    # violation sandbox raises SandboxError. The full-run pre-scan in main() is the all-or-nothing
    # gate; this is the per-file backstop underneath it.
    return sandbox.safe_write(out_dir, rel, text, overwrite=overwrite)


def _duplicate_top_level_keys(text):
    """Top-level keys repeated in the manifest (the loader silently keeps the last value).
    Best-effort, column-0 keys only — manifest sections live at the top level."""
    seen, dups = set(), []
    for raw in text.split("\n"):
        if not raw or raw[0] in " \t#-" or raw.lstrip() != raw:
            continue  # indented, comment, list item, or blank — not a top-level key
        m = re.match(r"([A-Za-z0-9_]+)\s*:", raw)
        if not m:
            continue
        key = m.group(1)
        if key in seen and key not in dups:
            dups.append(key)
        seen.add(key)
    return dups


def main():
    # issue #128: force UTF-8 stdio so non-ASCII output won't mojibake or crash on cp1252 (Windows)
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Render an EADOS manifest into a repository.")
    ap.add_argument("manifest", help="path to a filled project.yaml")
    ap.add_argument("--out", help="output directory, OUTSIDE the EADOS factory folder")
    ap.add_argument("--in-place", action="store_true",
                    help="render into the folder that holds .eados-core/ (a bundle copied into "
                         "your own repo): the project files land next to .eados-core/")
    ap.add_argument("--check", action="store_true",
                    help="validate the manifest and exit — nothing is written (the manifest-valid "
                         "gate command, workflow.yaml)")
    ap.add_argument("--force", "--overwrite", action="store_true", dest="force",
                    help="overwrite pre-existing files in the target (default: refuse to clobber, "
                         "like the migrate sandbox — a render is additive unless you pass this)")
    args = ap.parse_args()
    if sum((bool(args.out), args.in_place, args.check)) != 1:
        ap.error("provide exactly one of --out <dir>, --in-place, or --check")
    if args.force and args.check:
        ap.error("--force has no effect with --check (nothing is written)")
    mode = "Check" if args.check else "Render"

    with open(args.manifest, encoding="utf-8") as handle:
        raw = handle.read()
    if raw.startswith(chr(0xFEFF)):
        raw = raw[1:]   # Windows editors' UTF-8 BOM — load_yaml strips it too, but the raw
        #                 text also feeds _duplicate_top_level_keys, whose first-key regex
        #                 would silently skip a BOM-glued line
    manifest = load_yaml(raw)
    scalars, flags, sections = build_context(manifest)

    problems = validate_manifest(manifest, scalars)
    problems += [f"duplicate top-level key '{k}' (only the last value is kept)"
                 for k in _duplicate_top_level_keys(raw)]
    if problems:
        print(f"{mode}: FAIL — manifest validation\n")
        for p in sorted(set(problems)):
            print(f"  {p}")
        print(f"\n{len(set(problems))} manifest problem(s).")
        return 1
    if args.check:
        print("Check: OK — manifest is valid (nothing written).")
        return 0

    slug = scalars["PROJECT_SLUG"]
    eados_repo = os.path.realpath(os.path.dirname(ROOT))   # the folder that holds .eados-core/

    def _inside(child, parent):
        try:
            return child == parent or os.path.commonpath([child, parent]) == parent
        except ValueError:                                # different drives on Windows
            return False

    if args.in_place:
        # Generate INTO the folder that holds .eados-core/ — the bundle's intended home, copied
        # into the user's own repo (`<repo>/.eados-core/`), so the project files land in <repo>/
        # next to it. No template writes inside .eados-core/, so the factory stays intact, and the
        # generated .gitignore excludes it. Refuse only on the EADOS *development* repo, marked by
        # a root `.eados-dev` sentinel that never ships in a bundle — so a maintainer cannot
        # overwrite the factory's own source by running this from a clone.
        if os.path.exists(os.path.join(eados_repo, ".eados-dev")):
            print("Render: FAIL — refusing --in-place in the EADOS development repository "
                  "(the .eados-dev sentinel marks it). Use --out <dir> to render a separate copy.")
            return 1
        out_dir = eados_repo
    else:
        out_dir = os.path.abspath(args.out)
        # write_file confines writes within the output root, but nothing stops that root from
        # BEING the factory; `--out .` would overwrite EADOS's own AGENTS.md / CI / LICENSE. To
        # generate into a copied-in .eados-core/ on purpose, use --in-place instead.
        if _inside(os.path.realpath(out_dir), eados_repo):
            print("Render: FAIL — --out must be a directory OUTSIDE the EADOS repository "
                  f"(refusing {os.path.realpath(out_dir)}); use --in-place to generate into it).")
            return 1
    out_root = os.path.realpath(out_dir)

    # PLAN every write before touching disk. A render is all-or-nothing: an unresolved placeholder,
    # a path that escapes containment, or a clobber (absent --force) must abort the WHOLE run, so a
    # failed render never leaves the target repo half-written or half-overwritten.
    errors = []           # one accumulator for the whole run, threaded into every render()
    plan = []             # (rel, text) for every file this render would produce
    written = 0           # template-walk files only (the reported count; .gitkeep seeds excluded)
    for cur, dirs, files in os.walk(TEMPLATES):
        if "__pycache__" in cur:
            continue
        dirs.sort()           # deterministic walk order, independent of the filesystem
        for fn in sorted(files):
            src = os.path.join(cur, fn)
            rel = os.path.relpath(src, TEMPLATES).replace(os.sep, "/")
            if rel in NOT_RENDERED:
                continue
            if rel.startswith("docs/i18n/") and not flags["IF_I18N"]:
                continue
            if rel.startswith("docs/benchmarks/") and not flags["IF_BENCH"]:
                continue
            if rel.startswith("docs/api/") and not flags["IF_API_SPEC"]:
                continue
            if rel.startswith("docs/compliance/") and not flags["IF_ENTERPRISE"]:
                continue   # the compliance register is the enterprise posture's artifact (#248)
            if rel == "docs/workflow/announcements.md.tmpl" and not flags["IF_ANNOUNCE"]:
                continue
            if rel == "docs/workflow/operations.md.tmpl" and not flags["IF_SERVICE"]:
                continue
            if rel == "docs/workflow/packaging.md.tmpl" and not flags["IF_PACKAGING"]:
                continue
            with open(src, encoding="utf-8") as handle:
                text = handle.read()
            rendered = render(text, scalars, flags, sections, None, rel, errors)
            plan.append((out_relpath(rel, slug), rendered))
            written += 1

    # Seed the empty source-tree directories. (The project's LICENSE is templates/LICENSE.tmpl,
    # rendered in the walk above with the project's OWN {{AUTHOR}}/{{YEAR}} — never EADOS's: a repo
    # generated by anyone carries that user's copyright, not the factory owner's.)
    for key in ("SRC_MAIN", "SRC_TEST", "SRC_BENCH"):
        if scalars[key]:
            plan.append((f"{scalars[key]}/.gitkeep", ""))

    # Optional layered skeleton (#152): materialize the chosen internal packages under the main and
    # test source roots when the maintainer opted into a layered layout (capabilities.layered). A
    # library keeps the flat shape (no layers -> nothing seeded here). Only plain package segments are
    # honoured; the sandbox containment guard backstops anything unexpected.
    if flags["IF_LAYERED"]:
        for layer in sections["EACH_LAYER"]:
            name = (layer.get("name") if isinstance(layer, dict) else str(layer or "")).strip()
            if not re.match(r"^[A-Za-z0-9_]+$", name):
                continue   # skip non-identifier names rather than create an odd/unsafe path
            for root_key in ("SRC_MAIN", "SRC_TEST"):
                if scalars[root_key]:
                    plan.append((f"{scalars[root_key]}/{name}/.gitkeep", ""))

    if errors:
        print("Render: FAIL\n")
        for e in sorted(set(errors)):
            print(f"  {e}")
        print(f"\n{len(set(errors))} unresolved placeholder(s).")
        return 1

    # PRE-SCAN: resolve every destination through the shared sandbox guard (containment + `.git`)
    # and collect the ones that already exist. Refuse the whole render on any guard violation or —
    # unless --force — any clobber, before a single byte is written.
    guard_problems, collisions = [], []
    for rel, _text in plan:
        try:
            dest = sandbox.resolve(out_root, rel)
        except sandbox.SandboxError as exc:
            guard_problems.append(str(exc))
            continue
        if os.path.exists(dest):
            collisions.append(os.path.relpath(dest, out_root).replace(os.sep, "/"))
    if guard_problems:
        print("Render: FAIL — unsafe destination\n")
        for p in sorted(set(guard_problems)):
            print(f"  {p}")
        print(f"\n{len(set(guard_problems))} unsafe path(s). Nothing was written.")
        return 1
    if collisions and not args.force:
        print("Render: FAIL — refusing to overwrite existing files "
              "(pass --force to regenerate over them)\n")
        for c in sorted(set(collisions)):
            print(f"  {c}")
        print(f"\n{len(set(collisions))} existing file(s) would be overwritten "
              "(the render is additive by default). Nothing was written.")
        return 1

    # WRITE: the pre-scan has cleared containment, `.git`, and (absent --force) clobber, so this
    # is the point of no return — every planned file lands or none do.
    os.makedirs(out_dir, exist_ok=True)
    try:
        for rel, text in plan:
            write_file(out_dir, rel, text, overwrite=args.force)
    except sandbox.SandboxError as exc:      # a race created a file between pre-scan and write
        print(f"Render: FAIL — {exc}")
        return 1
    print(f"Render: OK — {written} template(s) -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
