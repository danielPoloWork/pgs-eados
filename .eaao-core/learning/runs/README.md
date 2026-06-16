# Run records

One YAML file per generation run, named `<YYYY-MM-DD>-<project-slug>.yaml`. After a run, the
architect appends a record: what was asked for, what was defaulted, and what the maintainer
overrode. These are the input the auto-tuner ([`../../tools/autotune.py`](../../tools/autotune.py))
mines to spot a default that is *consistently* overridden and propose changing it.

## Record schema

```yaml
slug: <project-slug>
date: YYYY-MM-DD
lang: <lang>
kind: <library|service|cli|app>
# Values the maintainer changed away from the built-in/profile default, as default -> chosen:
overrides:
  - key: ownership.license_id
    default: MIT
    chosen: Apache-2.0
  - key: toolchain.coverage_target
    default: 80
    chosen: 90
```

Records are facts about past runs — never edited after the fact. They contain no secrets (the
manifest's identity/spec is fine; tokens/webhooks never live in a manifest). Empty until the
first real run; the auto-tuner is a no-op until enough records accumulate.
