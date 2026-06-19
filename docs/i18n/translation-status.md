# Translation status manifest

Machine-checkable record of every translation's freshness. Each row pins the **source
commit** a translation was made from, so a translation is **stale** when its English source
has changed since that commit. `.eaao-core/tools/eaao_lint.py` (the `i18n-freshness` check)
reads this file.

Status vocabulary:

| Status | Meaning |
|--------|---------|
| `missing` | No translation exists yet; readers fall back to the English source. |
| `translated` | Up to date with the recorded source commit. |
| `stale` | The English source changed after the recorded source commit; needs a refresh. |

`Source commit` is the short SHA of the English source's latest commit at translation time;
`Translated at` is the commit that added/updated the translation. Both are `—` while a row is
`missing`.

## `zh-Hans` (Simplified Chinese)

| Source page | Source commit | Translated at | Status | Reviewer |
|-------------|:-------------:|:-------------:|:------:|----------|
| [`README.md`](../../README.md) | `8ca27b2` | `8ca27b2` | `translated` | — |

## `ja` (Japanese)

| Source page | Source commit | Translated at | Status | Reviewer |
|-------------|:-------------:|:-------------:|:------:|----------|
| [`README.md`](../../README.md) | `8ca27b2` | `8ca27b2` | `translated` | — |
