
# [BUG] `render.py --in-place` overwrites existing files in the user's repo — violates the additive/no-clobber posture

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#205](https://github.com/danielPoloWork/pgs-eados/pull/205) (issue [#195](https://github.com/danielPoloWork/pgs-eados/issues/195), CLOSED; commit `2fc9aeb`); `write_file` now delegates to `sandbox.safe_write` with an all-or-nothing pre-scan. Guarded by `test_render_guards.py` and the `safe-write` lint. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `bug`, `severity:high`, `area:render`, `security`
**Component:** `.eados-core/tools/render.py` (`write_file`, `--in-place`)

## Summary

The security posture (README "Security posture", installer docs, `sandbox.py`) is explicitly
**additive**: "never overwriting an existing file"; the refactor sandbox even raises
`SandboxError` on clobber unless `overwrite=True`. But the renderer's `write_file` overwrites
unconditionally:

```python
with open(dest, "w", encoding="utf-8", newline="\n") as handle:
    handle.write(text)
```
With `--in-place` — the documented flow for a bundle copied **into an existing repo** — a render will silently replace the user's pre-existing `README.md`, `LICENSE`, `.gitignore`, `AGENTS.md`, `.github/workflows/*`, etc. with generated versions. The `.eados-dev` sentinel only protects the _factory's own_ checkout, not the user's repository.

## Impact
Destructive, non-reversible-without-git data loss on real user files, in exactly the "existing repo" scenario the guided installer advertises. This is a direct contradiction of the documented contract, so users have been told it is safe.

## Proposed fix
- In `--in-place` mode, make `write_file` **fail-closed on clobber** (mirror `sandbox.safe_write`): collect all would-overwrite paths, print them, and abort before writing anything (atomic all-or-nothing pre-scan), with an explicit `--force` / `--overwrite` opt-in for the greenfield case.
- Reuse `sandbox.py` instead of a second private write path (see issue 0003).
- Add tests: render into a dir with a pre-existing `README.md` → FAIL listing the collision.
