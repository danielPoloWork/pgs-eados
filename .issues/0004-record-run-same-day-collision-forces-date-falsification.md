# [BUG] record_run.py: a second same-day run can only be recorded by falsifying its date

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#207](https://github.com/danielPoloWork/pgs-eados/pull/207) (issue [#197](https://github.com/danielPoloWork/pgs-eados/issues/197), CLOSED; commit `4f1e0d1`); `-2`/`-3` filename suffix keeps `date:` truthful. Guarded by `test_run_records.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `bug`, `severity:medium`, `area:learning`
**Component:** `.eados-core/tools/record_run.py`

## Summary

Records are declared to be **facts** ("never overwritten, never edited"), and the filename is
`<date>-<slug>.yaml`. When a second run of the same project happens the same day, the tool
fails with:
records are facts and are never overwritten (use --date to disambiguate a second same-day run)


But `--date` also sets the **`date:` field inside the record** (`today = args.date or …`), so
the only supported disambiguation is to record a *false date* — corrupting the very fact the
ledger exists to preserve. Same-day re-runs are the common case: a failed bootstrap
(`--outcome failed`) followed by the fixed re-run hours later is precisely the
failure→success pair the auto-tuner and lesson_audit want to see, and today it cannot be
recorded honestly.

## Proposed fix

- Add a sequence suffix to the filename on collision: `<date>-<slug>-2.yaml` (or accept
  `--seq N`), keeping `date:` truthful.
- Alternatively include a time component. Update `runs/README.md` schema, the eados_lint
  `run-records` filename expectations (if any), and `test_run_records.py`.
- Remove the misleading `--date` hint from the collision error message.