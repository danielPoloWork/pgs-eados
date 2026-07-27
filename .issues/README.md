# `.issues/` — milestone plans & issue drafts

The factory's planning surface: draft tickets (`NNNN-*.md`) and one **canonical milestone plan**
per milestone (`M<N>-<slug>-milestone.md` — precedent: M15 #233, M16 #256). GitHub is the tracker
of record; a plan doc is the reviewed intent the tracker items are cut from, and it records the
tracker mapping once the issues are filed. Allow-listed as human-reviewed prose (`gate-coverage`).

## Milestone plan format

A plan doc carries: **Status/Owner header · Theme · Ratified decisions (dated) · the
wave/sequence table · Out of scope (invariants)**. Since M16 (ADR-0017) the sequence table has a
**`Routing` column** next to `Effort`:

| Item | Issue | Title | Effort | Routing |
|---|---|---|---|---|
| 16.1 | #252 | … | M | frontier-reasoning / high (decision-heavy, sets-pattern) |

`Routing` speaks the [`os/routing`](../.eados-core/orchestrator/os/routing/_schema.md) vocabulary:
a capability **tier** (`fast` / `standard` / `frontier-reasoning`) + an **effort**
(`low` / `medium` / `high` / `extra` / `max` — five levels since M19 19.2), with the asserted flags
in parentheses. Model names stay out of the table — the dated catalog in `routing.yaml` owns them,
and since M19 it is two-level (providers describe capability, hosts declare reach), so the same
tier resolves to a different model on a different host.

## Filing an issue

Every filed issue carries the tracker metadata (labels incl. a `severity:*`, the milestone, the
assignee — the PR-metadata parity rule) **and a `Routing:` line in its body**:

```markdown
**Routing** (ADR-0017/ADR-0024, advisory — reviewed YYYY-MM-DD): `tier` / `effort` — flags: `…`. Catalog (as of YYYY-MM-DD) resolves this to <name> on <host>.
```

The flags record what labels cannot say: `sets-pattern` (first of its class — followers inherit a
cheaper route) and `decision-heavy` (the decision is the deliverable). The line routes the ISSUE;
since M19 19.7 a **step** inside it (`design` / `implement` / `test` / `review` / `optimize`) can
raise the route further — never lower it — so a cheap item's design step earns more than its test
step while a protected item keeps its floor in every step. The line is the
**maintainer-reviewed call**; the policy's label-only advice is the starting point, checkable any
time with:

```bash
python .eados-core/tools/route_advice.py --issue N                 # one issue, from its labels
python .eados-core/tools/route_advice.py --milestone "M16 — …"     # one line per open issue
python .eados-core/tools/route_advice.py --labels "adr,severity:high" --flags decision-heavy
python .eados-core/tools/route_advice.py --labels "severity:low" --step design --explain
python .eados-core/tools/route_advice.py --labels "severity:low" --host codex   # any host
```

Advisory only, always: the human keeps final model authority (ADR-0017); an agent never switches
the session model.
