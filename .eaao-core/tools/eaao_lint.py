#!/usr/bin/env python3
"""Self-lint for the EAAO factory itself (the bar EAAO imposes downstream, imposed upstream).

Dependency-free (Python 3 standard library only). Run from anywhere in the repo:

    python tools/eaao_lint.py

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
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")
PROFILES = os.path.join(ROOT, "orchestrator", "profiles")
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
    """Indentation-based key-path extractor (keys only; values/list-items ignored)."""
    paths, stack = set(), []
    for raw in text.splitlines():
        stripped = raw.lstrip(" ")
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            continue
        m = re.match(r"([A-Za-z0-9_]+)\s*:", stripped)
        if not m:
            continue
        indent = len(raw) - len(stripped)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, m.group(1)))
        paths.add(".".join(k for _, k in stack))
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
    profiles = sorted(glob.glob(os.path.join(PROFILES, "*.yaml")))
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
    for fn in sorted(os.listdir(agent_dir)):
        if not fn.endswith(".md") or fn == "README.md":
            continue
        if f"({fn})" not in index:
            fail(name, f"agent role '{fn}' is not listed in agent/README.md")


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


CHECKS = [
    check_placeholder_integrity,
    check_profile_completeness,
    check_generate_references,
    check_agent_registry,
    check_lessons,
]


def main():
    for fn in CHECKS:
        try:
            fn()
        except Exception as exc:  # a crashing check is itself a failure
            fail(fn.__name__, f"check crashed: {exc!r}")
    if failures:
        print("EAAO self-lint: FAIL\n")
        for check, message in failures:
            print(f"  [{check}] {message}")
        print(f"\n{len(failures)} factory-integrity problem(s) found.")
        return 1
    print("EAAO self-lint: OK — placeholders, profiles, and playbook references are congruent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
