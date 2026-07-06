#!/usr/bin/env python3
"""Differential test: the hand-rolled manifest loader must agree with a real YAML parser.

EADOS renders with a dependency-free loader (yamlmini.load_yaml, re-exported as render.load_yaml;
#166) so the everyday path needs no third-party deps. This test pins that loader to PyYAML on the
documented supported subset, so a future regression (the kind ADR-0006/0008 were written about)
fails loudly instead of silently corrupting a generated repo. PyYAML is a CI-only dependency;
absent it, the test skips (exit 0).

    python .eados-core/tools/tests/test_loader.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from yamlmini import load_yaml  # noqa: E402  (the loader under test)
import render  # noqa: E402  (the re-export every caller relies on)

# Each case is idiomatic manifest YAML; load_yaml must equal yaml.safe_load on all of them.
# The previously-silent corruptions (quote escaping, block chomping) are first-class cases.
CASES = [
    # --- the regressions C2 fixes ---
    ("single-quote escaping",      "tagline: 'it''s a developer''s friend'"),
    ("double-quote escaping",      r'objective: "Parse \"key: value\" pairs"'),
    ("double-quote newline+tab",   r'msg: "line1\nline2\tend"'),
    ("block clip |",               "note: |\n  a\n  b\n"),
    ("block strip |-",             "note: |-\n  a\n  b\n"),
    # `|+` keep-chomping is intentionally out of the guaranteed subset (see render.py header).
    # --- core subset that must keep agreeing ---
    ("plain string",               "name: pbr-cpp-memory-pool"),
    ("string with colon value",    "url: http://example.com:8080/path"),
    ("comma-bearing plain scalar", "tier1: Linux x86_64, Windows x86_64, macOS arm64"),
    ("int",                        "coverage_target: 80"),
    ("bool true/false",            "bench: true\nthreading: false"),
    ("null forms",                 "a: null\nb: ~\nc:"),
    ("quoted empty",               'secondary_lang: ""'),
    ("at-sign quoted",             'assignee: "@me"'),
    ("flow list",                  "scopes: [api, build, tests, docs, ci]"),
    ("flow map in seq",            "matrix:\n  - { os: ubuntu-24.04, toolchain: gcc, preset: debug }\n"),
    ("block seq same indent",      "scopes:\n- api\n- build\n"),
    ("block seq deeper indent",    "scopes:\n  - api\n  - build\n"),
    ("nested mapping",             "language:\n  lang: cpp\n  group_path: it/d4np\n"),
    ("block-style map items",      "matrix:\n  - os: ubuntu-24.04\n    toolchain: gcc\n"),
    ("hash inside quotes",         'hint: "#include <memory_pool.h>"'),
    ("leading '---' tolerated",    "---\nname: acme\n"),
    # A leading UTF-8 BOM (Windows Notepad / PowerShell 5.1 Out-File) is stripped, exactly
    # like PyYAML — before the fix it glued itself to the first key and broke validation.
    ("UTF-8 BOM stripped (utf-8-sig semantics)", chr(0xFEFF) + "name: acme\n"),
    ("UTF-8 BOM before a leading '---'",         chr(0xFEFF) + "---\nname: acme\n"),
    # --- #166 false-positive guards: lines the truncation rejection must NOT fire on ---
    ("apostrophe in a plain scalar",   "desc: the maintainer's own namespace"),
    ("quoted item in a block seq",     'scopes:\n  - "api"\n  - plain\n'),
    ("unbalanced quote/bracket in a block-scalar body",
     'note: |\n  an unclosed "quote and a stray [ bracket\n  are literal here\n'),
]

# Inputs OUTSIDE the supported subset must fail LOUDLY (ValueError), not be silently
# mis-parsed (ADR-0008's "fail loudly" promise). PyYAML also rejects these.
MUST_RAISE = [
    ("multi-document stream", "a: 1\n---\nb: 2"),
    ("document end marker",   "a: 1\n...\n"),
    ("tab indentation",       "root:\n\tchild: 1"),
]

# LEGAL YAML the subset deliberately does not read — the #153 silent-truncation constructs
# (#166): the loader used to keep the first line and silently DROP the rest. It must now raise
# a loud ValueError. PyYAML parses every one of these fine, and the differential section below
# asserts exactly that: the rejection is a conscious subset boundary, never a misparse.
SUBSET_REJECTIONS = [
    ("multi-line double-quoted scalar", 'prompt: "first line\n  and a second"'),
    ("multi-line single-quoted scalar", "prompt: 'first line\n  and a second'"),
    ("wrapped flow sequence",           "sets: [GROUP_PATH,\n  GROUP_DOTTED]"),
    ("wrapped flow mapping",            "matrix: { os: linux,\n  arch: x64 }"),
    ("wrapped flow in a list item",     "steps:\n  - [a,\n    b]\n"),
    # Folded `>` block scalars (#194): parse_map has no `>` branch, so the loader used to skip
    # the body and keep the bare ">" — the #153 silent-truncation class, live in the repo's own
    # `notes: >` profiles. A literal `|` is byte-exact; `>` must now reject loudly, and PyYAML
    # (the differential below) parses every one of these fine, proving it is a subset boundary.
    ("folded scalar > (clip)",   "objective: >\n  a rate limiter\n  with O(1) admission\n"),
    ("folded scalar >- (strip)", "note: >-\n  folded\n  then stripped\n"),
    ("folded scalar >+ (keep)",  "note: >+\n  folded\n  then kept\n"),
    ("folded scalar in a seq",   "objectives:\n  - >\n    fold this item\n"),
]

# Documented deviations where load_yaml deliberately differs from PyYAML — asserted
# explicitly because the strict-equality corpus above structurally cannot cover them.
DEVIATIONS = [
    ("leading-zero int stays string", "code: 08540", {"code": "08540"}),
    ("decimal stays string",          "ver: 1.20",   {"ver": "1.20"}),
    ("norway: yes is not bool",       "flag: yes",   {"flag": "yes"}),
]


def main():
    failures = []

    # Loader-only invariants (no PyYAML needed): unsupported input must fail loudly, and the
    # documented deviations from PyYAML must hold exactly (the strict-equality corpus below
    # cannot cover them, since by definition they disagree with PyYAML).
    for label, text in MUST_RAISE + SUBSET_REJECTIONS:
        try:
            load_yaml(text)
            failures.append(f"{label}: expected a loud ValueError, but load_yaml accepted it")
        except ValueError:
            pass
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: expected ValueError, got {exc!r}")
    # #166: the extraction keeps every caller working — render.load_yaml IS yamlmini.load_yaml.
    if render.load_yaml is not load_yaml:
        failures.append("render.load_yaml is not the yamlmini.load_yaml re-export")
    # BOM fix, loader-only (also differentially pinned in CASES when PyYAML is present): the
    # first key must come out clean, and exactly ONE BOM is stripped — a second is content
    # and stays, matching utf-8-sig.
    got = load_yaml(chr(0xFEFF) + "identity: 1")
    if got != {"identity": 1}:
        failures.append(f"UTF-8 BOM not stripped from the first key: got {got!r}")
    got = load_yaml(chr(0xFEFF) + chr(0xFEFF) + "identity: 1")
    if "identity" in got:
        failures.append(f"a double BOM must not be swallowed (one is content): got {got!r}")
    for label, text, expected in DEVIATIONS:
        got = load_yaml(text)
        if got != expected:
            failures.append(f"{label}: load_yaml={got!r} != expected {expected!r}")

    try:
        import yaml
    except ImportError:
        if failures:
            print("test-loader: FAIL\n")
            for f in failures:
                print(f"  {f}")
            print(f"\n{len(failures)} loader-only failure(s).")
            return 1
        print("test-loader: SKIP (differential) — PyYAML not installed; "
              "loader-only checks passed.")
        return 0

    for label, text in CASES:
        try:
            mine = load_yaml(text)
        except Exception as exc:  # noqa: BLE001 — any crash is a failure
            mine = f"<EXC {exc!r}>"
        ref = yaml.safe_load(text)
        if mine != ref:
            failures.append(f"{label}: load_yaml={mine!r} != pyyaml={ref!r}")

    # #166 differential proof for the truncation rejections: each construct IS legal YAML
    # (PyYAML parses it), so silently returning anything would have been a misparse — the
    # loud rejection is the only honest behavior for the subset.
    for label, text in SUBSET_REJECTIONS:
        try:
            yaml.safe_load(text)
        except Exception:  # noqa: BLE001
            failures.append(f"{label}: expected PyYAML to PARSE this (it is legal YAML) — "
                            "the case belongs in MUST_RAISE, not SUBSET_REJECTIONS")

    # End-to-end: the shipped reference manifest must parse identically with both.
    ref_path = os.path.join(ROOT, "orchestrator", "examples", "reference.yaml")
    with open(ref_path, encoding="utf-8") as fh:
        raw = fh.read()
    if load_yaml(raw) != yaml.safe_load(raw):
        failures.append("orchestrator/examples/reference.yaml: load_yaml != pyyaml (deep)")

    if failures:
        print("test-loader: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} loader-fidelity divergence(s).")
        return 1
    print(f"test-loader: OK — agrees with PyYAML on {len(CASES)} cases + reference.yaml, "
          f"rejects {len(MUST_RAISE)} unsupported + {len(SUBSET_REJECTIONS)} truncation-class "
          f"inputs, honours {len(DEVIATIONS)} deviations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
