#!/usr/bin/env python3
"""Deterministic template renderer for EAAO (the Mustache subset of placeholders.md).

Dependency-free (Python 3 standard library only). Turns a confirmed project manifest into a
rendered repository, replacing the "careful manual pass" with a reproducible one:

    python tools/render.py orchestrator/project.yaml --out ../my-new-repo

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

errors = []


# ---------------------------------------------------------------------------
# Minimal YAML loader (mappings, lists, flow [..]/{..}, and `|` block scalars).
# ---------------------------------------------------------------------------
def _strip_comment(text):
    out, q, i = [], None, 0
    while i < len(text):
        c = text[i]
        if q:
            out.append(c)
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
    parts, depth, q, buf = [], 0, None, []
    for c in text:
        if q:
            buf.append(c)
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
    if buf:
        parts.append("".join(buf))
    return parts


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
    if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
        return s[1:-1]
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


def load_yaml(text):
    lines = text.split("\n")
    n = len(lines)
    pos = [0]

    def indent_of(line):
        return len(line) - len(line.lstrip(" "))

    def skip_blanks():
        while pos[0] < n:
            s = lines[pos[0]].strip()
            if s and not s.startswith("#"):
                return
            pos[0] += 1

    def parse_block_scalar(parent_indent):
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
            collected.append(line[base:])
            pos[0] += 1
        while collected and collected[-1] == "":
            collected.pop()
        return ("\n".join(collected) + "\n") if collected else ""

    def parse_map(indent):
        result = {}
        while True:
            skip_blanks()
            if pos[0] >= n:
                break
            line = lines[pos[0]]
            ind = indent_of(line)
            if ind != indent or line.strip().startswith("- "):
                break
            key, _, val = _strip_comment(line.strip()).partition(":")
            key, val = key.strip(), val.strip()
            pos[0] += 1
            if val in ("|", "|-", "|+"):
                result[key] = parse_block_scalar(indent)
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
                # Rewrite the "- " lead-in to spaces so parse_map reads a normal entry.
                lines[pos[0]] = " " * key_col + content
                items.append(parse_map(key_col))
            else:
                items.append(_scalar(_strip_comment(content.strip())))
                pos[0] += 1
        return items

    skip_blanks()
    return parse_map(0)


# ---------------------------------------------------------------------------
# Manifest -> render context (scalars, boolean flags, list sections).
# ---------------------------------------------------------------------------
def build_context(m):
    ident = m.get("identity", {}) or {}
    own = m.get("ownership", {}) or {}
    lang = m.get("language", {}) or {}
    tool = m.get("toolchain", {}) or {}
    cmds = tool.get("commands", {}) or {}
    ci = m.get("ci", {}) or {}
    gov = m.get("governance", {}) or {}
    caps = gov.get("capabilities", {}) or {}
    spec = m.get("spec", {}) or {}
    i18n = m.get("i18n", {}) or {}
    ann = m.get("announce", {}) or {}

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
}


def validate_manifest(m, scalars):
    """Guards that turn quiet manifest mistakes into a hard, actionable failure:
    an unknown/misspelled top-level section (which would otherwise resolve to an empty
    mapping and blank every field under it), and a non-numeric start version (the classic
    `start_version`/`version_start` swap)."""
    problems = []
    for key in m:
        if key not in KNOWN_SECTIONS:
            problems.append(
                f"unknown top-level section '{key}' (typo? expected one of: "
                f"{', '.join(sorted(KNOWN_SECTIONS))})"
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
def render(tmpl, scalars, flags, sections, local=None, where=""):
    def repl_section(m):
        kind, name, body = m.group(1), m.group(2), m.group(3)
        if name in sections:
            items = sections[name]
            if kind == "#":
                return "".join(
                    render(body, scalars, flags, sections, it, where) for it in items
                )
            return render(body, scalars, flags, sections, local, where) if not items else ""
        truthy = flags.get(name, False)
        keep = truthy if kind == "#" else not truthy
        return render(body, scalars, flags, sections, local, where) if keep else ""

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
    dest = os.path.join(out_dir, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main():
    ap = argparse.ArgumentParser(description="Render an EAAO manifest into a repository.")
    ap.add_argument("manifest", help="path to a filled project.yaml")
    ap.add_argument("--out", required=True, help="output directory (must be outside EAAO)")
    args = ap.parse_args()

    with open(args.manifest, encoding="utf-8") as handle:
        manifest = load_yaml(handle.read())
    scalars, flags, sections = build_context(manifest)

    problems = validate_manifest(manifest, scalars)
    if problems:
        print("Render: FAIL — manifest validation\n")
        for p in sorted(set(problems)):
            print(f"  {p}")
        print(f"\n{len(set(problems))} manifest problem(s).")
        return 1

    slug = scalars["PROJECT_SLUG"]
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    written = 0
    for cur, _dirs, files in os.walk(TEMPLATES):
        if "__pycache__" in cur:
            continue
        for fn in files:
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
            rendered = render(text, scalars, flags, sections, None, rel)
            write_file(out_dir, out_relpath(rel, slug), rendered)
            written += 1

    # Render EAAO's LICENSE (with author/year) and seed the source-tree directories.
    # LICENSE lives at the actual repo root (one level above .eaao-core/).
    lic = next((p for p in (os.path.join(ROOT, "LICENSE"),
                            os.path.join(os.path.dirname(ROOT), "LICENSE"))
                if os.path.exists(p)), None)
    if lic:
        with open(lic, encoding="utf-8") as handle:
            write_file(out_dir, "LICENSE", render(handle.read(), scalars, flags, sections, None, "LICENSE"))
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
