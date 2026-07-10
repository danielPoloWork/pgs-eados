# [FEATURE] Ship host adapters so `/eados <cmd>` is a discoverable slash command

**Labels:** `enhancement`, `severity:high`, `area:commands`, `dx`
**Component:** `.claude/commands/`, `setup/`, `.eados-core/orchestrator/commands/`

## Context

The eight `/eados` commands exist only as portable markdown procedures under
`.eados-core/orchestrator/commands/`. `commands/README.md` (the "Portable." paragraph) explicitly delegates
the "thin adapter" to the host ("a host wraps it with its own skill mechanism — Claude Code
`.claude/skills/`, a Codex/Gemini agent registry"), but **no adapter exists on disk**: `.claude/`
contains only `settings.local.json`, and the `setup/` installers deliver the bundle only
("install = bundle download + placement only", `setup.sh` header).

Consequence: on a fresh install, typing `/eados init` in Claude Code resolves to nothing. The
command surface is undiscoverable until the agent happens to read `commands/README.md`.

## Direction

1. Add thin adapters `.claude/commands/eados/<name>.md` (→ `/eados:<name>` in Claude Code), one
   per row of the `commands/README.md` table. Each adapter is a pointer, not a copy: it names the
   owning role and instructs the agent to read and follow the canonical procedure file — exactly
   as `CLAUDE.md` points at `AGENTS.md`.
2. Extend the `setup/` installers to place the adapters (opt-in prompt / `--with-adapters`),
   keeping the additive no-clobber posture.
3. Document the Codex / Gemini Antigravity equivalents (registry entry / `GEMINI.md` note).
4. `eados_lint`: a new check (or a `gate-coverage` class) asserting every `commands/*.md` row has
   a matching adapter, so a new command cannot ship undiscoverable.

## Acceptance

A fresh install into an empty repo exposes the full `/eados` palette as host slash commands; the
canonical procedure remains the single source of truth (adapter carries no procedure body);
self-lint green with the new coverage check.

**Depends on:** ADR-0019 (taxonomy, drafted as 0022) — the `commands/README.md` alias table it
ratifies is the canonical registry the adapters and the coverage check enforce against.
