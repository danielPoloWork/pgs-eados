## Summary

One or two sentences: what changes and why it matters.

## Motivation

Link to the ADR, issue, or audit finding that prompted this work. Non-trivial design
decisions need an ADR under [`.eados-core/docs/adr/`](../.eados-core/docs/adr/).

## Changes

- bulleted list of meaningful changes (not a file list)

## Verification

- [ ] `python .eados-core/tools/eados_lint.py` passes (placeholder / profile / playbook /
      i18n-freshness integrity)
- [ ] Render-smoke green: `python .eados-core/tools/render.py .eados-core/orchestrator/examples/reference.yaml --out /tmp/r` and the generated `consistency_lint.py` passes
- [ ] Tooling tests pass (`tools/tests/test_*.py`) where touched
- [ ] `python -m py_compile` clean on any changed tool

## Documentation Impact

- [ ] `README.md` updated (if the maintainer-facing surface changed)
- [ ] ADR added/updated (if a non-trivial design decision was made)
- [ ] Translations refreshed + `.eados-core/docs/i18n/translation-status.md` bumped (if an English source with translations changed)
- [ ] `CHANGELOG.md` `[Unreleased]` updated
- [ ] PR metadata set — assignee + one type label

## Lesson

<!-- Optional, one line. A generalizable rule the next run should inherit — captured here at
review time, not from end-of-run recollection. Squash-merge makes this PR body the permanent
`main` commit (`os/git/git.yaml` `commit.squash_body`), so a merged lesson is owner-approved by
construction; `tools/lesson_sweep.py` harvests these into draft `learning/lessons.yaml` entries.
Write "none" if there is nothing durable to carry forward. -->

Lesson: none
