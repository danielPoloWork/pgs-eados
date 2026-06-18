#!/usr/bin/env python3
"""Negative-path tests for the renderer's guards — they must FAIL on bad input.

The render-smoke proves the *happy path* (the reference manifest renders cleanly). This proves
the inverse, which is where the security/correctness value lives: a path-unsafe identifier, a
missing required field, an unknown section, or a bad version must each be a hard failure, and a
write can never escape --out. Dependency-free (no PyYAML): runnable in the self-lint job.

    python .eaao-core/tools/tests/test_render_guards.py
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import render  # noqa: E402  (the module under test)

RENDER_PY = os.path.join(TOOLS, "render.py")

# A minimal manifest with every required field present and valid — the positive control.
VALID = """
identity: { project_name: Acme, project_slug: acme, project_kind: library }
ownership: { owner: o, license_id: MIT, default_branch: main }
language: { lang: go, group_path: it/d4np }
governance: { start_version: "0.0.0" }
"""


def _problems(yaml_text):
    m = render.load_yaml(yaml_text)
    scalars, _flags, _sections = render.build_context(m)
    return render.validate_manifest(m, scalars)


def check(label, cond, failures):
    if not cond:
        failures.append(label)


def main():
    failures = []

    # --- validate_manifest: the positive control passes clean ---
    check("valid manifest yields no problems", _problems(VALID) == [], failures)

    # --- validate_manifest: each guard fires on the matching defect ---
    def has(yaml_text, needle):
        return any(needle in p for p in _problems(yaml_text))

    check("path-unsafe slug rejected",
          has(VALID.replace("project_slug: acme", 'project_slug: "../../evil"'),
              "not a safe path segment"), failures)
    check("path-unsafe lang rejected",
          has(VALID.replace("lang: go", 'lang: "../x"'), "not a safe path segment"), failures)
    check("missing required field rejected",
          has(VALID.replace("owner: o, ", ""), "required field"), failures)
    check("unknown top-level section rejected",
          has(VALID + "\nbogus: { x: 1 }\n", "unknown top-level section"), failures)
    check("non-numeric start_version rejected",
          has(VALID.replace('start_version: "0.0.0"', 'start_version: "pre-1.0"'),
              "not a numeric"), failures)

    # --- _unsafe_path_value unit cases ---
    for safe in ("acme", "memorypool", "it/d4np", "a.b-c_d"):
        check(f"_unsafe_path_value safe: {safe}", not render._unsafe_path_value(safe), failures)
    for bad in ("..", "a/../b", "", "/etc", "C:\\x", "a/..", "foo/./bar"):
        check(f"_unsafe_path_value unsafe: {bad!r}", render._unsafe_path_value(bad), failures)

    # --- write_file containment: a normal rel writes, an escaping rel raises ---
    with tempfile.TemporaryDirectory() as out:
        render.write_file(out, "docs/ok.md", "hi")
        check("normal write lands inside out_dir",
              os.path.exists(os.path.join(out, "docs", "ok.md")), failures)
        try:
            render.write_file(out, os.path.join("..", "..", "escape.md"), "x")
            check("escaping write must raise", False, failures)
        except ValueError:
            pass

    # --- end-to-end: render.py on a traversal manifest exits 1 and writes nothing outside ---
    with tempfile.TemporaryDirectory() as work:
        manifest = os.path.join(work, "bad.yaml")
        with open(manifest, "w", encoding="utf-8") as fh:
            fh.write(VALID.replace("project_slug: acme",
                                   'project_slug: "../../../../pwned"'))
        out = os.path.join(work, "out")
        proc = subprocess.run([sys.executable, RENDER_PY, manifest, "--out", out],
                              capture_output=True, text=True)
        check("traversal manifest -> non-zero exit", proc.returncode == 1, failures)
        check("traversal manifest -> actionable message",
              "not a safe path segment" in (proc.stdout + proc.stderr), failures)
        check("traversal manifest wrote nothing outside out_dir",
              not os.path.exists(os.path.join(work, "pwned")) and
              not os.path.exists(os.path.join(os.path.dirname(work), "pwned")), failures)

    if failures:
        print("test-render-guards: FAIL\n")
        for f in failures:
            print(f"  {f}")
        print(f"\n{len(failures)} guard(s) did not fire as expected.")
        return 1
    print("test-render-guards: OK — validation, containment, and the CLI all reject bad input.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
