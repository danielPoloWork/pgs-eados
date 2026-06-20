# Translation status manifest

Machine-checkable record of every translation's freshness. Each row pins the **SHA-256
content hash** of the English source a translation was made from, so a translation is
**stale** when its English source hashes differently now. `.eaao-core/tools/eaao_lint.py`
(the `i18n-freshness` check) reads this file. Content-based (not commit-based) so it is
immune to squash-merges — see [ADR-0010](../../.eaao-core/docs/adr/0010-content-hash-i18n-freshness.md).

Status vocabulary:

| Status | Meaning |
|--------|---------|
| `missing` | No translation exists yet; readers fall back to the English source. |
| `translated` | Up to date with the recorded source hash. |
| `stale` | The English source hashes differently than recorded; needs a refresh. |

`Source hash` is the first 12 hex of the SHA-256 of the English source's bytes at translation
time (`sha256sum <file>` / `hashlib.sha256`). It is `—` while a row is `missing`.

## `zh-Hans` (Simplified Chinese)

| Source page | Source hash | Status | Reviewer |
|-------------|:-----------:|:------:|----------|
| [`README.md`](../../README.md) | `15d70afb0711` | `translated` | — |

## `ja` (Japanese)

| Source page | Source hash | Status | Reviewer |
|-------------|:-----------:|:------:|----------|
| [`README.md`](../../README.md) | `15d70afb0711` | `translated` | — |
