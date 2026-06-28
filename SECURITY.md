# Security Policy

## Scope

EADOS is a **markdown/YAML factory** with a small, dependency-free Python toolchain
(`tools/render.py`, `tools/eados_lint.py`, and the `consistency_lint.py` it ships into
generated repos). It has no runtime service and no third-party runtime dependencies, so its
security surface is:

- **the tooling** — e.g. a path-traversal or arbitrary-write in the renderer (manifest-driven
  output paths), or a code-execution vector in a tool;
- **the supply chain** — the GitHub Actions it pins and the one third-party dev dependency
  (PyYAML, pinned + hashed for the CI-only differential gate), governed by
  [ADR-0009](.eados-core/docs/adr/0009-ci-supply-chain-pinning.md);
- **the generated output** — a template or profile that would render an insecure default into
  every downstream repository.

## Supported versions

EADOS follows Semantic Versioning; only the latest release and `main` receive fixes.

| Version | Supported |
|---------|-----------|
| latest `main` | ✅ |
| anything older | ❌ |

## Reporting a vulnerability

**Do not open a public issue or PR for a security problem.** Report it privately via
[GitHub private vulnerability reporting](https://github.com/danielPoloWork/pgs-eados/security/advisories/new)
(the repository's **Security** tab → *Report a vulnerability*), to `danielPoloWork`.

Please include:

- the affected commit (or `main` at a given date) and your platform / Python version;
- a minimal reproduction — a failing `tools/` invocation or a manifest that triggers it is
  ideal;
- the observed impact and, if known, the root cause.

## What to expect

1. **Acknowledgement** of the report.
2. **Triage & fix under embargo** on a private branch / draft advisory.
3. **Coordinated disclosure**: the fix lands, then the advisory is published. The fix is
   recorded in [`CHANGELOG.md`](CHANGELOG.md) under a **Security** entry with the advisory
   reference, and — if it changed an emitted default — in the relevant ADR.

Thank you for reporting responsibly.
