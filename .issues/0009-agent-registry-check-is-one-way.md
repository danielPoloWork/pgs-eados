# [GAP] eados_lint check_agent_registry is one-way: stale registry entries for deleted personas are not flagged

> **✅ Resolved — released in v2.7.0 (2026-07-07).** Fixed by [#212](https://github.com/danielPoloWork/pgs-eados/pull/212) (issue [#202](https://github.com/danielPoloWork/pgs-eados/issues/202), CLOSED; commit `08938f4`); `check_agent_registry` is now bidirectional (a dead index link fails), escaping links excluded. Guarded by `test_agent_registry.py` (both directions). See the [regression index](REGRESSION-INDEX.md) (#235). Kept as a historical record.

**Labels:** `enhancement`, `severity:low`, `area:lint`
**Component:** `.eados-core/tools/eados_lint.py` (`check_agent_registry`)

## Summary

The check walks `agent/**` and fails when a persona file is **missing from**
`agent/README.md`. The reverse direction is unchecked: a registry line whose
`(<rel-path>)` link points at a persona file that was deleted or renamed stays green.

The lint elsewhere holds itself to exactly this hygiene standard — e.g.
`check_workflow_safety` flags an allow-list entry for a *missing* workflow as stale. The
registry deserves the same symmetry: an index that lists dead personas misleads both the
authority model (personas are the persona≠authority split's catalogue) and any agent that
resolves a role through the registry.

## Proposed fix

Extract the `(...)`-relative links from `agent/README.md` (those resolving under `agent/`,
`.md` only) and fail on any that does not exist on disk:

```python
for rel in re.findall(r"\((?!https?://)([^)]+\.md)\)", index):
    if rel != "README.md" and not os.path.exists(os.path.join(agent_dir, rel)):
        fail(name, f"agent/README.md lists '{rel}' which does not exist")
```

Add both directions to the check's unit test.