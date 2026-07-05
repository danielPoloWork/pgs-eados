# Run records

One YAML file per generation run, named `<YYYY-MM-DD>-<project-slug>.yaml`. After a run
(generate.md **Step 9**), the architect appends a record with **one command** — no
hand-authored YAML (#172):

```bash
python .eados-core/tools/record_run.py <manifest> [--outcome ok|failed] \
    [--failure GATE=MESSAGE ...] [--lesson L-NNNN ...] [--rubric DIM=SCORE ...]
```

The `overrides:` list is derived **mechanically** from the manifest's `interview:` provenance
block (#169) against the built-in defaults in `project.yaml.template` — never from end-of-run
recollection. The records feed the auto-tuner
([`../../tools/autotune.py`](../../tools/autotune.py)), which mines defaults that are
*consistently* overridden, and the failure channel is where the highest-value signal EADOS
generates — a **red bootstrap CI** on a fresh repo — lands durably:
`--failure ci-bootstrap="<one-line summary>"` (with `--outcome failed`).

## Record schema

```yaml
slug: <project-slug>
date: YYYY-MM-DD
lang: <lang>
kind: <library|service|cli|app>
outcome: ok            # ok | failed
# Values the maintainer changed away from a built-in default (derived from provenance):
overrides:
  - key: ownership.license_id
    default: MIT
    chosen: Apache-2.0
  - key: toolchain.coverage_target
    default: 80
    chosen: 90
lessons_applied: []    # the lesson ids applied at Step 0.a, e.g. [L-0001, L-0002]
failures: []           # on a failed run: [{gate: ci-bootstrap, message: "..."}]
rubric: {}             # eval/rubric.md dimensions scored 0-2, e.g. spec_measurability: 2
```

Records are facts about past runs — never edited after the fact (`record_run.py` refuses to
overwrite an existing file). They contain no secrets (the manifest's identity/spec is fine;
tokens/webhooks never live in a manifest). The auto-tuner reads `overrides` and ignores the
other channels; it is a no-op until enough records accumulate.
