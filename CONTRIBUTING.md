# Contributing to EADOS

Thanks for your interest. EADOS is **owner-governed**: you are very welcome to *propose*
changes, but the owner (`@danielPoloWork`) is the sole maintainer who reviews and merges.
This page is the short how-to; the full contract is [`AGENTS.md`](AGENTS.md) (it governs
humans and AI agents alike).

## The model in one line

> Contributors **suggest** via pull requests; the owner **decides** and **squash-merges**.
> Nobody pushes to `main` directly.

## How to propose a change

1. **Fork** the repository (external contributors) or create a feature branch (collaborators).
2. **Branch** as `<type>/<short-kebab>`, with `type ∈ {feat, fix, refactor, perf, docs, test, build, chore, ci}`.
3. **Make one logical change.** Keep the README, the affected profile(s)/template(s), and an
   ADR (for non-trivial design decisions) in sync **in the same PR** — see `AGENTS.md` §7.
4. **Write [Conventional Commits](https://www.conventionalcommits.org/)** — e.g.
   `feat(profiles): seed a Zig toolchain profile`. Scopes: `interview`, `profiles`,
   `templates`, `lint`, `agent`, `docs`, `adr`, `ci`.
5. **Run the gates locally** (dependency-free, Python 3.12+ stdlib):

   ```bash
   python .eados-core/tools/eados_lint.py                                   # factory integrity
   python .eados-core/tools/tests/run_all.py                                # the whole test suite (discovered, never enumerated)
   python .eados-core/tools/render.py .eados-core/orchestrator/examples/reference.yaml --out /tmp/r
   python /tmp/r/tools/consistency_lint.py                                # generated-repo gate (render smoke)
   ```

6. **Open a pull request.** Fill the [PR template](.github/PULL_REQUEST_TEMPLATE.md); update
   `CHANGELOG.md` `[Unreleased]` for any user- or maintainer-visible change. CI re-runs the
   gates on every push.
7. **The owner reviews and squash-merges.** Address review feedback by pushing to the same
   branch. Do not merge your own PR.

## Common contributions

- **Teach EADOS a new language** — usually just a new `profiles/<lang>.yaml` (copy
  `profiles/_template.yaml`), an interview branch for its frameworks, an ADR, and a row in
  the README's supported-language note. Never edit templates to add a language (`AGENTS.md` §3, §7).
- **Improve a template / the tooling** — keep `placeholders.md`, the profiles, and the
  templates congruent (the self-lint enforces it).

## Reporting

- **Bugs / features** — use the [issue forms](.github/ISSUE_TEMPLATE/).
- **Security** — never a public issue; follow [`SECURITY.md`](SECURITY.md).
- **Questions / ideas** — use GitHub Discussions.

## Language

Every artifact that lands on disk or in Git is **English** (`AGENTS.md` §2). You may converse
in any language; translated docs live only under `.eados-core/docs/i18n/`.

By contributing, you agree your contributions are licensed under the repository's
[MIT License](LICENSE).
