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

This is a self-contained tool: it carries a tiny YAML loader (mappings, lists, flow
collections, and `|` block scalars — enough for project.yaml) so it needs no third-party deps.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")

SECTION_RE = re.compile(r"\{\{([#^])([A-Z][A-Z0-9_]*)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)
VAR_RE = re.compile(r"(?<!\$)\{\{\s*([^{}]+?)\s*\}\}")
UPPER_RE = re.compile(r"[A-Z][A-Z0-9_]*$")


# ---------------------------------------------------------------------------
# Minimal YAML loader. Supported subset (validated against PyYAML by
# tools/tests/test_loader.py): block/flow mappings and sequences, block-style
# mapping items, double-quoted scalars WITH escapes (\n \t \r \0 \" \\ \/),
# single-quoted scalars with '' escaping, `|` (clip) and `|-` (strip) block scalars,
# and int / true / false / null / ~ literals.
# Deliberate deviations from YAML 1.1, kept because they are safer for a manifest:
#   * yes/no/on/off are NOT booleans (avoids the "Norway problem"); only true/false are.
#   * unquoted decimals/exponents stay strings (versions like 1.22 are not coerced).
# Out of scope (best-effort, not guaranteed byte-identical): `|+` keep-chomping, folded `>`
# scalars, anchors, tags, and multi-document streams.
# ---------------------------------------------------------------------------
def _strip_comment(text):
    out, q, i = [], None, 0
    while i < len(text):
        c = text[i]
        if q:
            out.append(c)
            # Inside a double-quoted scalar a backslash escapes the next char, so an
            # escaped quote (\") must not be read as closing the string.
            if c == "\\" and q == '"' and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c
            out.append(c)
        elif c == "#" and (i == 0 or text[i - 1] == " "):
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).rstrip()


def _split_top(text, sep=","):
    parts, depth, q, buf, i = [], 0, None, [], 0
    while i < len(text):
        c = text[i]
        if q:
            buf.append(c)
            if c == "\\" and q == '"' and i + 1 < len(text):
                buf.append(text[i + 1])     # escaped char: never a separator or quote-close
                i += 2
                continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c
            buf.append(c)
        elif c in "[{":
            depth += 1
            buf.append(c)
        elif c in "]}":
            depth -= 1
            buf.append(c)
        elif c == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
        i += 1
    if buf:
        parts.append("".join(buf))
    return parts


# Recognised escapes in a YAML double-quoted scalar (the subset a manifest needs).
_DQ_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "0": "\0",
               '"': '"', "\\": "\\", "/": "/", " ": " "}


def _unescape_double(body):
    """Apply double-quoted YAML escapes; an unknown \\x degrades to the literal x."""
    out, i = [], 0
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            out.append(_DQ_ESCAPES.get(nxt, nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _scalar(s):
    s = s.strip()
    if s == "":
        return ""
    if s[0] == "[" and s[-1] == "]":
        inner = s[1:-1].strip()
        return [_scalar(x) for x in _split_top(inner)] if inner else []
    if s[0] == "{" and s[-1] == "}":
        inner, d = s[1:-1].strip(), {}
        if inner:
            for pair in _split_top(inner):
                k, _, v = pair.partition(":")
                d[k.strip()] = _scalar(v.strip())
        return d
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return _unescape_double(s[1:-1])
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")     # YAML single-quote escaping: '' -> '
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", s):
        # A leading-zero integer (e.g. a ZIP/year like "08540") would lose the zero if
        # coerced — keep it a string, consistent with "unquoted decimals stay strings".
        if re.fullmatch(r"-?0\d+", s):
            return s
        return int(s)
    return s


_DOC_MARKERS = ("---", "...")


def _reject_unsupported(text):
    """Fail loudly on constructs outside the supported subset rather than mis-parsing them.

    A single leading `---` document-start marker is tolerated (idiomatic, single-document);
    any *later* `---`/`...` marks a multi-document stream (out of scope) and a tab in the
    indentation is invalid YAML. Both would otherwise be silently flattened/merged.
    """
    seen_content = False
    for num, raw in enumerate(text.split("\n"), 1):
        s = raw.strip()
        if s in _DOC_MARKERS:
            if seen_content or s == "...":
                raise ValueError(
                    f"line {num}: multi-document streams / '...' end markers are not supported; "
                    "the manifest must be a single YAML document"
                )
            continue  # a leading '---' document-start is fine
        lead = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in lead:
            raise ValueError(f"line {num}: tab indentation is not valid YAML — use spaces")
        if s and not s.startswith("#"):
            seen_content = True


def load_yaml(text):
    _reject_unsupported(text)   # loud failure outside the subset, not silent guessing
    lines = text.split("\n")
    n = len(lines)
    pos = [0]

    def indent_of(line):
        return len(line) - len(line.lstrip(" "))

    def skip_blanks():
        # Comments, blank lines, and a tolerated leading '---' (validated by
        # _reject_unsupported, which rejects any non-leading marker) are not content.
        while pos[0] < n:
            s = lines[pos[0]].strip()
            if s and not s.startswith("#") and s != "---":
                return
            pos[0] += 1

    def parse_block_scalar(parent_indent, chomp=""):
        collected, base = [], None
        while pos[0] < n:
            line = lines[pos[0]]
            if line.strip() == "":
                collected.append("")
                pos[0] += 1
                continue
            if indent_of(line) <= parent_indent:
                break
            if base is None:
                base = indent_of(line)
            # Never slice into real content: if a later line is less-indented than the
            # first, dedent only by what it actually has.
            collected.append(line[min(base, indent_of(line)):])
            pos[0] += 1
        if chomp == "+":                       # keep: preserve trailing blank lines as-is
            return ("\n".join(collected) + "\n") if collected else ""
        while collected and collected[-1] == "":   # clip/strip both drop trailing blanks
            collected.pop()
        if not collected:
            return ""
        body = "\n".join(collected)
        return body if chomp == "-" else body + "\n"   # strip: no final newline; clip: one

    def parse_map(indent, first_line=None):
        # `first_line` lets a block-style sequence item ("- key: value") feed its dash-stripped
        # first line in without rewriting the shared `lines` buffer (the parser no longer
        # mutates its own input). Subsequent iterations read normally from the buffer.
        result = {}
        while True:
            skip_blanks()
            if pos[0] >= n:
                break
            line = first_line if first_line is not None else lines[pos[0]]
            first_line = None
            ind = indent_of(line)
            if ind != indent or line.strip().startswith("- "):
                break
            key, _, val = _strip_comment(line.strip()).partition(":")
            key, val = key.strip(), val.strip()
            pos[0] += 1
            if val in ("|", "|-", "|+"):
                result[key] = parse_block_scalar(indent, val[1:])  # "" clip, "-" strip, "+" keep
            elif val == "":
                skip_blanks()
                if pos[0] < n:
                    nxt = lines[pos[0]]
                    nind = indent_of(nxt)
                    is_item = nxt.strip().startswith("- ")
                    if is_item and nind == indent:
                        # YAML permits a block sequence at the SAME indent as its key;
                        # accept it instead of silently treating the key as null.
                        result[key] = parse_list(indent)
                    elif nind > indent:
                        result[key] = parse_list(nind) if is_item else parse_map(nind)
                    else:
                        result[key] = None
                else:
                    result[key] = None
            else:
                result[key] = _scalar(val)
        return result

    def parse_list(indent):
        items = []
        while True:
            skip_blanks()
            if pos[0] >= n:
                break
            line = lines[pos[0]]
            if indent_of(line) != indent or not line.strip().startswith("- "):
                break
            after_dash = line[indent + 1:]                       # everything past the '-'
            key_col = indent + 1 + (len(after_dash) - len(after_dash.lstrip(" ")))
            content = line[key_col:]
            if re.match(r"[A-Za-z0-9_]+\s*:(\s|$)", content):
                # Block-style mapping item ("- key: value" + aligned continuation lines).
                # Feed the dash-stripped first line to parse_map (no buffer mutation).
                items.append(parse_map(key_col, first_line=" " * key_col + content))
            else:
                items.append(_scalar(_strip_comment(content.strip())))
                pos[0] += 1
        return items

    skip_blanks()
    return parse_map(0)


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
    gpath = lang.get("group_path", "it/d4np")
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
        "ASSIGNEE": own.get("assignee", ""),
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
        "SPEC_VERIFICATION": spec.get("verification", ""),
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
    }

    sections = {
        "EACH_CI_CELL": ci.get("matrix", []) or [],
        "EACH_SCOPE": gov.get("scopes", []) or [],
        "EACH_FUNCTIONAL_REQ": spec.get("functional_reqs", []) or [],
        "EACH_NONFUNCTIONAL_REQ": spec.get("nonfunctional_reqs", []) or [],
        "EACH_PUBLIC_API": spec.get("public_api", []) or [],
        "EACH_MILESTONE1_ITEM": spec.get("milestone1_items", []) or [],
        "EACH_MILESTONE": spec.get("milestones", []) or [],
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
}

# Known top-level SCALARS (not sections). `schema_version` versions the manifest schema for
# backward-compatible evolution (RFC-0001 §8 / OQ1); `domain` selects the target profile
# (orchestrator/domains/<domain>.yaml, M1-C). Both are metadata, not sections/placeholders.
KNOWN_SCALARS = {"schema_version", "domain"}

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
    """True if `value` cannot be used as one or more safe relative path segments."""
    for part in str(value).replace("\\", "/").split("/"):
        if part in ("", ".", "..") or not _SAFE_SEGMENT.match(part):
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
                "(no path separators beyond '/', no '.', '..', or absolute paths)"
            )
    sv = scalars.get("START_VERSION", "")
    if sv and not re.fullmatch(r"\d+\.\d+\.\d+", sv):
        problems.append(
            f"governance.start_version '{sv}' is not a numeric X.Y.Z version "
            "(did you swap it with version_start?)"
        )
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


def write_file(out_dir, rel, text):
    # Containment guard: resolve both sides and refuse anything that escapes the output
    # root (path traversal via a manifest-derived rel). This backstops validate_manifest.
    out_root = os.path.realpath(out_dir)
    dest = os.path.realpath(os.path.join(out_root, rel.replace("/", os.sep)))
    try:
        contained = os.path.commonpath([out_root, dest]) == out_root
    except ValueError:            # different drives on Windows -> definitely outside
        contained = False
    if not contained:
        raise ValueError(f"refusing to write outside the output directory: {rel!r}")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


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
    ap = argparse.ArgumentParser(description="Render an EADOS manifest into a repository.")
    ap.add_argument("manifest", help="path to a filled project.yaml")
    ap.add_argument("--out", help="output directory, OUTSIDE the EADOS factory folder")
    ap.add_argument("--in-place", action="store_true",
                    help="render into the folder that holds .eados-core/ (a bundle copied into "
                         "your own repo): the project files land next to .eados-core/")
    args = ap.parse_args()
    if bool(args.out) == bool(args.in_place):
        ap.error("provide exactly one of --out <dir> or --in-place")

    with open(args.manifest, encoding="utf-8") as handle:
        raw = handle.read()
    manifest = load_yaml(raw)
    scalars, flags, sections = build_context(manifest)

    problems = validate_manifest(manifest, scalars)
    problems += [f"duplicate top-level key '{k}' (only the last value is kept)"
                 for k in _duplicate_top_level_keys(raw)]
    if problems:
        print("Render: FAIL — manifest validation\n")
        for p in sorted(set(problems)):
            print(f"  {p}")
        print(f"\n{len(set(problems))} manifest problem(s).")
        return 1

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
    os.makedirs(out_dir, exist_ok=True)

    errors = []           # one accumulator for the whole run, threaded into every render()
    written = 0
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
            if rel == "docs/workflow/announcements.md.tmpl" and not flags["IF_ANNOUNCE"]:
                continue
            if rel == "docs/workflow/operations.md.tmpl" and not flags["IF_SERVICE"]:
                continue
            if rel == "docs/workflow/packaging.md.tmpl" and not flags["IF_PACKAGING"]:
                continue
            with open(src, encoding="utf-8") as handle:
                text = handle.read()
            rendered = render(text, scalars, flags, sections, None, rel, errors)
            write_file(out_dir, out_relpath(rel, slug), rendered)
            written += 1

    # Seed the empty source-tree directories. (The project's LICENSE is templates/LICENSE.tmpl,
    # rendered in the walk above with the project's OWN {{AUTHOR}}/{{YEAR}} — never EADOS's: a repo
    # generated by anyone carries that user's copyright, not the factory owner's.)
    for key in ("SRC_MAIN", "SRC_TEST", "SRC_BENCH"):
        if scalars[key]:
            write_file(out_dir, f"{scalars[key]}/.gitkeep", "")

    if errors:
        print("Render: FAIL\n")
        for e in sorted(set(errors)):
            print(f"  {e}")
        print(f"\n{len(set(errors))} unresolved placeholder(s).")
        return 1
    print(f"Render: OK — {written} template(s) -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
