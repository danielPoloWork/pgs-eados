# Architecture Decision Records — EADOS

Decisions governing the orchestrator's own design (not the projects it generates — those
get their own `docs/adr/` from the templates). Lightweight Michael Nygard format; numbering
is sequential and never reused. Template: the generated
[`templates/docs/adr/template.md`](../../templates/docs/adr/template.md).

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-templating-and-genericity-model.md) | Three-layer genericity model (profiles, manifest, templates) | Accepted |
| [0002](0002-interview-driven-intake.md) | Interview-driven intake before generation | Accepted |
| [0003](0003-generated-repos-are-self-governing.md) | Generated repositories are self-governing | Accepted |
| [0004](0004-seed-language-profiles.md) | Seed profiles for C, C#, VB.NET, JS, PHP, Lua (SQL/CSS/HTML stay secondary) | Accepted |
| [0005](0005-seed-modern-and-legacy-profiles.md) | Seed Scala/Kotlin/Swift/Dart/Ruby + legacy COBOL/Pascal (QBasic deferred) | Accepted |
| [0006](0006-manifest-loader-and-emitted-yaml-validation.md) | Spec-correct manifest loader + real-parser gate for emitted YAML | Accepted |
| [0008](0008-loader-scalar-fidelity-and-differential-gate.md) | Loader scalar fidelity (quote escaping, chomping) + PyYAML differential gate | Accepted |
| [0009](0009-ci-supply-chain-pinning.md) | CI supply-chain pinning (SHA-pin EADOS-authored workflows, kill @latest, pin+hash PyYAML) | Accepted |
| [0007](0007-renderer-write-guards-and-validation-independence.md) | Renderer write-containment, required-field validation, independent CI-YAML gate | Accepted |
| [0010](0010-content-hash-i18n-freshness.md) | Content-hash i18n freshness (squash-merge-proof) | Accepted |
| [0011](0011-eados-phase-based-delivery-operating-system.md) | EADOS — phase-based agentic delivery operating system (the pivot) | Accepted |
| [0012](0012-project-rename-to-eados.md) | Rename EAAO → EADOS: repo, path, and bundle migration | Accepted |
| [0013](0013-dependabot-action-pin-auto-remediation.md) | Dependabot action-pin auto-remediation (`workflow_run` template re-sync) | Accepted |
| [0014](0014-inbound-contribution-trust-model.md) | Inbound-contribution trust model (verify the change, never merge non-owner commits, adopt via co-author) | Accepted |
