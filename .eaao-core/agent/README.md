# Agent Registry

The composable agent roles EAAO ships. Each file is a **portable agent definition** (a persona
+ an operating procedure + the agent-vs-human boundary). Drop one into a host that supports
subagents (`.claude/agents/`, a Codex/Gemini agent registry) or follow it inline. Every role
defers to the project's `AGENTS.md` as the source of truth and never crosses the human
boundary (draft/propose; the human opens, merges, publishes).

## Roles

| Role | Use it to… |
|---|---|
| [`enterprise-architect`](enterprise-architect.md) | Stand up and govern a project; drive the EAAO interview → generate loop. The orchestrating role. |
| [`reviewer`](reviewer.md) | Review a diff/PR against the spec, quality bar, and patterns policy; return structured findings. |
| [`security-auditor`](security-auditor.md) | Threat-model and audit for vulnerabilities, unsafe deps, and secret leaks; draft advisories. |
| [`release-manager`](release-manager.md) | Cut a SemVer release: bump, changelog, notes, tag, announcement draft. |
| [`profile-author`](profile-author.md) | Add or refresh a language profile (toolchain knowledge as data). |

## How they compose

A generation run is the **architect**; before the bootstrap PR it invokes the **reviewer** and
(for sensitive surfaces) the **security-auditor**; a release is the **release-manager**; adding
a language is the **profile-author**. They share one contract, so handing off between them does
not change the rules — only the focus.

## Customizing and adding roles

- **Override** a shipped role or **add** your own under
  [`../config/agents/`](../config/README.md) — overlays take precedence over these defaults, so
  you tune behavior without editing the core.
- A custom role should keep the same shape: frontmatter (`name`, `description`, `tools`), a
  persona, an operating procedure, and an explicit boundary. List it here (the self-lint checks
  that every role file is registered).

## Shared rules (all roles)

- **English on disk**, any language in chat (`AGENTS.md` §2).
- **Agent drafts; human opens/merges/publishes** (`AGENTS.md` §6.1 / §11).
- **Measurable over asserted** — prove with tests/checks, not prose.
- **Learn** — record a generalizable lesson in [`../learning/lessons.yaml`](../learning/README.md).
