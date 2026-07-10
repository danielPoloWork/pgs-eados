# [BUG] autotune.py crashes with a raw traceback on a malformed run record

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#208](https://github.com/danielPoloWork/pgs-eados/pull/208) (issue [#198](https://github.com/danielPoloWork/pgs-eados/issues/198), CLOSED; commit `273e1d2`); both `autotune.py` and `lesson_audit.py` skip+report a bad record and exit 0. Guarded by `test_autotune.py` + `test_lesson_audit.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `bug`, `severity:low`, `area:learning`, `robustness`
**Component:** `.eados-core/tools/autotune.py` (and audit `lesson_audit.py` for the same pattern)

## Summary

`autotune.py` reads every `learning/runs/*.yaml` through `load_yaml` with **no error
handling**: python with open(path, encoding="utf-8") as handle: rec = load_yaml(handle.read())


`load_yaml` raises `ValueError` on anything outside the subset (unclosed quote, flow
collection, folded scalar, multi-doc marker). One bad record therefore kills the whole
analysis with an uncaught traceback — and since #173 wired autotune + lesson_audit as
advisory CI steps, it turns the advisory step red with a stack trace instead of a message.

The `run-records` lint gate protects the **factory repo's CI**, but autotune is also a
user-facing tool run on bundles/checkouts where the lint may never have run; a report-only
tool should degrade per-file, not die globally.

## Proposed fix

- Wrap the per-file load in `try/except ValueError/OSError`; report
  `autotune: skipping <file>: <error> (run eados_lint run-records)` and continue.
- Skip non-dict roots defensively.
- Same sweep for `lesson_audit.py` if it shares the pattern.
- Test: a directory with one valid + one malformed record → proposals still computed,
  malformed file named in output, exit 0.