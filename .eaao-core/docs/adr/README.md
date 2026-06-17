# Architecture Decision Records — EAAO

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
