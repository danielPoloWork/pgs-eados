# [GAP] interview.provenance completeness is not enforced — partial blocks silently starve the learning loop

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#211](https://github.com/danielPoloWork/pgs-eados/pull/211) (issue [#201](https://github.com/danielPoloWork/pgs-eados/issues/201), CLOSED; commit `ac16ce6`); `validate_manifest` enforces coverage (via `PROVENANCE_EXEMPT`, a superset of the draft's list — also `ownership`/`domain`) + non-empty `questionnaire_version`, block-absence still legal; `record_run` warns on gaps. Guarded by `test_render_guards.py` + `test_record_run.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `enhancement`, `severity:medium`, `area:render`, `area:learning`
**Component:** `.eados-core/tools/render.py` (`validate_manifest`), `record_run.py` (`derive_overrides`)

## Summary

`interview.md` mandates "one entry per top-level answer key, `questionnaire_version` set",
but `validate_manifest` only checks the block when present for: non-empty mapping, enum
values, no dangling keys. It does **not** check:

1. **Coverage** — answer-bearing top-level sections (`identity`, `language`, `toolchain`,
   `ci`, `governance`, `i18n`, `announce`, `spec`) missing from `provenance` pass silently.
2. **`questionnaire_version`** — never validated (presence or shape).

The failure mode is quiet and compounding: `record_run.derive_overrides` treats an
**unrecorded** key exactly like `defaulted` (`prov.get(top) in (None, "defaulted") → skip`),
so a lazily-filled provenance block suppresses override derivation, the run record shows
`overrides: []`, and autotune/lesson_audit are starved of their entire input — the same
"phase-skipping agent indistinguishable from a diligent one" problem #169 was meant to close.

## Proposed fix

- In `validate_manifest`, when the `interview:` block is present require: an entry for every
  answer-bearing top-level section present in the manifest (state sections excluded), and a
  non-empty `questionnaire_version`.
- Keep block **absence** legal (legacy manifests), so this stays backward-compatible.
- In `record_run.py`, warn (not fail) when a section present in the manifest has no
  provenance entry, so the gap is visible at recording time.
- Negative tests in `test_render_guards.py` / `test_record_run.py`.