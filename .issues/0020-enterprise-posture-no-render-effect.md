# [ENHANCEMENT] `governance.posture: enterprise` has no effect on rendered output

**Labels:** `enhancement`, `severity:medium`, `area:render`, `area:templates`
**Component:** `orchestrator/placeholders.md`, `tools/render.py`, `templates/`

## Summary

Q0.5 captures the enterprise posture (interview.md; ADR-0015 promises "mandatory ADRs for
security-relevant decisions, stricter review, an explicit compliance-docs expectation"), and the
manifest carries `governance.posture` — but no `{{POSTURE}}` placeholder or `IF_ENTERPRISE`
flag exists in `placeholders.md`, `render.py`, or any template. A considered `enterprise` answer
and the `standard` default produce **byte-identical** generated repositories: the promise is
prose-only.

## Proposed fix

1. Define `POSTURE` + `IF_ENTERPRISE` in `placeholders.md` (dictionary stays authoritative).
2. Templates consume the flag: `AGENTS.md.tmpl` gains the stricter-review / mandatory-ADR
   clauses under `{{#IF_ENTERPRISE}}`; seed a `docs/compliance/` index page when enterprise;
   optionally a stricter default coverage/review bar noted in the generated §10.
3. The generated `consistency_lint.py` learns the congruence check (posture in AGENTS.md ↔
   compliance docs present).
4. Render-smoke gains an enterprise-posture fixture variant.

Belongs to the M15 hardening wave; pairs naturally with draft issue 0008 (provenance
enforcement) since posture is a classic silently-defaulted answer.
