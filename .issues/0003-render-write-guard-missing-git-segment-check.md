# [SECURITY] Renderer write guard lacks the `.git`-at-any-depth refusal that sandbox.py has

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#206](https://github.com/danielPoloWork/pgs-eados/pull/206) (issue [#196](https://github.com/danielPoloWork/pgs-eados/issues/196), CLOSED; commit `b468fff`); `.git` rejected at validation + via the single `sandbox` write path. Guarded by `test_render_guards.py` + `test_sandbox.py` and the `safe-write` lint. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `security`, `severity:medium`, `area:render`, `defense-in-depth`
**Component:** `.eados-core/tools/render.py` (`write_file`, `_SAFE_SEGMENT`), vs `.eados-core/tools/sandbox.py`

## Summary

There are **two independent write-containment implementations** with different guarantees:

| Guard | containment | absolute/drive | `.git` at any depth | no-clobber |
|---|---|---|---|---|
| `sandbox.resolve/safe_write` | ✅ | ✅ | ✅ | ✅ (default) |
| `render.write_file` | ✅ | (via validate) | ❌ | ❌ |

`render._SAFE_SEGMENT = r"[A-Za-z0-9._-]+\Z"` accepts the segment `.git`, and
`_unsafe_path_value` only rejects `""`, `.`, `..`. So a manifest with e.g.
`language.group_path: ".git/hooks"` passes `validate_manifest` and, in `--in-place` mode
against an existing repository, the seeded source-tree writes
(`{SRC_MAIN}/.gitkeep`, layered `.gitkeep`s) can land under a **real `.git/` directory** —
the exact corruption class `sandbox.py` refuses ("VCS metadata too; never corrupt it").

## Impact

Manifest-steered writes into VCS metadata (e.g. `.git/hooks/` — an execution vector on the
next `git commit`). Requires a malicious or careless manifest, but the manifest is exactly
the externally-supplied input the ADR-0007 guards exist for.

## Proposed fix

- Add the `.git`-segment check (exact-segment, any depth) to `render.write_file`, or better:
  make `render.py` delegate to `sandbox.resolve()` so there is **one** write guard
  (single source of truth — the project's own stated principle).
- Reject the `.git` segment in `_unsafe_path_value` too (fail at validation, not at write).
- Extend `test_render_guards.py` with a `group_path: .git/hooks` case.

