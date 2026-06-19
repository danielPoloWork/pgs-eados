# Documentation translations (i18n)

Translations of EAAO's reader-facing landing page. **English is the single normative
source** — a translation is a convenience layer, never a second source of truth, and where
it conflicts with the English original the English wins.

This guide is intentionally English-only (it is contributor/agent tooling, per
[`AGENTS.md`](../../AGENTS.md) §6 — *English on disk, any language in chat*).

## Languages

| Code | Language | Index |
|------|----------|-------|
| `zh-Hans` | Simplified Chinese (简体中文) | [`zh-Hans/README.md`](zh-Hans/README.md) |
| `ja` | Japanese (日本語) | [`ja/README.md`](ja/README.md) |

## What is translated (the translatable surface)

Only the reader-facing narrative a newcomer needs to evaluate and start using the factory:

| English source | What it is |
|----------------|------------|
| [`README.md`](../../README.md) | Landing page (what EAAO is, the pipeline, getting started) |

**Not translated** (English-only, by design): `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` (the
agent contract), `.eaao-core/docs/USAGE.md` and the orchestrator playbooks (contributor/agent
tooling), the ADRs (immutable records), and the templates (rendered into *generated* repos,
which carry their own i18n). EAAO is a factory: the projects it generates get their own
`docs/i18n/` from the templates — this directory translates only EAAO's own front door.

## Layout

A translated page lives at the **same relative path** as its English source, under
`docs/i18n/<lang>/`:

```text
docs/i18n/zh-Hans/README.md   ← translates ../../README.md
docs/i18n/ja/README.md        ← translates ../../README.md
```

The 1:1 path mapping is what lets the freshness lint pair each translation with its source
mechanically.

## Adding or updating a translation

1. Copy the English source to the mirrored path under `docs/i18n/<lang>/` and translate the
   prose. Keep code blocks, identifiers, file paths, commands, and the terms marked *keep in
   English* in [`glossary.md`](glossary.md) **unchanged**.
2. Start the page with the standard banner (so a reader always knows it is a derived,
   possibly-stale artifact):

   ```markdown
   > 🌐 Translation of [`README.md`](../../README.md) as of commit `<short-sha>`.
   > **English is normative** — if this differs from the source, the English version wins.
   ```

3. Record it in [`translation-status.md`](translation-status.md): the source path, the
   **source commit hash** you translated from (`git rev-parse --short HEAD` after the English
   change landed), the translated-at commit, the status, and the reviewer.

When you **edit an English source** that has translations, refresh those translations (or
mark their manifest rows `stale`) in the same PR — otherwise the freshness lint flags the
commit-hash drift.

## Staleness gate

[`translation-status.md`](translation-status.md) pins each translation to the source commit it
was made from. A translation is **stale** when its source page has changed since that commit.
`.eaao-core/tools/eaao_lint.py` turns this into a CI-checkable condition (the `i18n-freshness`
check): it fails when `git log <recorded-commit>..HEAD -- <source>` is non-empty.

## Terminology

[`glossary.md`](glossary.md) is the canonical term map (English ↔ `zh-Hans` ↔ `ja`), including
explicit *keep in English* entries for terms of art (EAAO, orchestrator, manifest, profile,
template, ADR, SemVer, Conventional Commits). Translators must follow it.
