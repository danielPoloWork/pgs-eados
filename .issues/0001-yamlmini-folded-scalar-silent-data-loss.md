# [BUG] yamlmini silently drops folded (`>`) block-scalar content instead of rejecting it

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#204](https://github.com/danielPoloWork/pgs-eados/pull/204) (issue [#194](https://github.com/danielPoloWork/pgs-eados/issues/194), CLOSED; commit `6efebaf`); guarded by `test_loader.py`. See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `bug`, `severity:high`, `area:tools`, `loader`
**Component:** `.eados-core/tools/yamlmini.py`

## Summary

The module docstring and ADR-0006/0008 posture promise that anything outside the supported
subset "fails LOUDLY (reject, never guess)". Folded scalars (`>`, `>-`, `>+`) violate this:
they are neither supported nor rejected — they are **silently mis-parsed with data loss**.

## Details

1. `_reject_unsupported` treats `>`-style values as block scalars and **skips their bodies**
   without raising:

   ```python
   if value.rstrip() in ("|", "|-", "|+", ">", ">-", ">+"):
       # A block-scalar body is literal content — skip it ...
   ```

2. But `parse_map` only handles the literal variants:

   ```python
   if val in ("|", "|-", "|+"):
       result[key] = parse_block_scalar(indent, val[1:])
   ```

   For `key: >` the value falls through to `_scalar(">")`, storing the literal string `">"`,
   and the deeper-indented body lines then break out of `parse_map`/`parse_list` and are
   **silently discarded** (or worse, glued onto a parent scope).

## Impact

A manifest author who writes `spec.objective: >` (a perfectly idiomatic YAML choice) gets a
manifest whose objective is the string `">"` and whose body vanished — exactly the #153
silent-truncation bug class the loader was hardened against. Downstream, `validate_manifest`
may even pass (`">"` is non-empty), so the hollow value reaches the render.

## Reproduction

```yaml
spec:
  objective: >
    Provide a rate limiter
    with O(1) admission.
```

`load_yaml` returns `{"spec": {"objective": ">"}}` — no error, body gone.

## Proposed fix
In `parse_map`, when `val` starts with `>` raise `ValueError(f"line …: folded block scalars ('>') are not supported — use a literal block scalar (|)")`, and remove `>`-variants from `_reject_unsupported`'s _skip_ list (or turn the skip into a loud rejection there, which also covers `>` inside sequences). Add a differential case to `tools/tests/test_loader.py`.