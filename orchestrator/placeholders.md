# Placeholder Dictionary

The authoritative list of every `{{PLACEHOLDER}}` that may appear in `templates/**`. A
template may only use placeholders defined here; a placeholder defined here should be
resolvable from `orchestrator/project.yaml` (which merges the interview answers with the
chosen language profile).

**Conventions.** Placeholders are `{{UPPER_SNAKE}}` wrapped in double braces. Optional
blocks use `{{#IF_KEY}} ... {{/IF_KEY}}` (render only when the key is truthy); the
**inverted** form `{{^IF_KEY}} ... {{/IF_KEY}}` renders only when the key is falsy.
List expansion uses `{{#EACH_KEY}} ... {{/EACH_KEY}}`, with `{{.}}` for the current scalar
item or `{{field}}` for a field of the current object. Keep substitution literal and dumb —
all intelligence lives in the manifest, not the renderer. This is the Mustache subset; any
Mustache-compatible renderer (or a careful manual pass) works.

---

## 1. Identity

| Placeholder | Meaning | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | Repository / package name (kebab) | `pbr-cpp-memory-pool` |
| `{{PROJECT_SLUG}}` | Short single-word slug used in the source path & namespace leaf | `memorypool` |
| `{{PROJECT_TITLE}}` | Human-facing title | `High-Performance Memory Pool` |
| `{{PROJECT_TAGLINE}}` | One-sentence description | `Fixed-block O(1) memory pool` |
| `{{PROJECT_SERIES}}` | Optional umbrella/series name, blank if none | `Purpose-Built References (PBR)` |

## 2. Ownership & governance

| Placeholder | Meaning | Example |
|---|---|---|
| `{{OWNER}}` | GitHub owner/org login | `danielPoloWork` |
| `{{MAINTAINER}}` | Maintainer display name | `Daniel Polo` |
| `{{AUTHOR}}` | Copyright holder | `Daniel Polo` |
| `{{YEAR}}` | Copyright year | `2026` |
| `{{LICENSE_ID}}` | SPDX license id | `MIT` |
| `{{DEFAULT_BRANCH}}` | Mainline branch | `master` |
| `{{ASSIGNEE}}` | PR assignee handle (often `@me`) | `@me` |
| `{{PROJECT_KIND}}` | `library` \| `service` \| `cli` \| `app` | `library` |
| `{{START_VERSION}}` | Numeric start version (drives the README badge + day-zero version constant) | `0.0.0` |

## 3. Source tree & language

| Placeholder | Meaning | Example |
|---|---|---|
| `{{LANG}}` | Source-tree language segment | `cpp` |
| `{{LANG_NAME}}` | Display language + standard | `C++17` |
| `{{LANG_STANDARD}}` | Standard/edition string | `C++17 (ISO/IEC 14882:2017)` |
| `{{GROUP_PATH}}` | Reverse-domain path segment | `it/d4np` |
| `{{GROUP_DOTTED}}` | Same, dotted | `it.d4np` |
| `{{NAMESPACE}}` | Language-native namespace/package for the project | `it::d4np::memorypool` |
| `{{SRC_MAIN}}` | Production source root | `src/main/cpp/it/d4np/memorypool` |
| `{{SRC_TEST}}` | Test source root | `src/test/cpp/it/d4np/memorypool` |
| `{{SRC_BENCH}}` | Benchmark source root (blank if N/A) | `src/bench/cpp/it/d4np/memorypool` |
| `{{SRC_EXT}}` | Primary source file extension | `cpp` |
| `{{PUBLIC_INCLUDE_HINT}}` | How a consumer imports the public surface | `#include <it/d4np/memorypool/memory_pool.h>` |

## 4. Toolchain (from the language profile)

| Placeholder | Meaning | Example |
|---|---|---|
| `{{BUILD_TOOL}}` | Build system | `CMake + Ninja` |
| `{{PKG_MANAGER}}` | Dependency/package manager | `vcpkg / Conan` |
| `{{TEST_FRAMEWORK}}` | Test framework | `doctest` |
| `{{FORMATTER}}` | Code formatter | `clang-format` |
| `{{LINTER}}` | Static analyzer / linter | `clang-tidy` |
| `{{SANITIZERS}}` | Runtime checkers, comma list | `ASan, UBSan, TSan, Valgrind` |
| `{{COVERAGE_TOOL}}` | Coverage tool | `llvm-cov / gcovr` |
| `{{DOC_TOOL}}` | API docs generator | `Doxygen` |
| `{{CMD_BUILD}}` | Canonical build command | `cmake --build --preset debug` |
| `{{CMD_TEST}}` | Canonical test command | `ctest --preset debug` |
| `{{CMD_FORMAT_CHECK}}` | Format-check command | `clang-format --dry-run --Werror` |
| `{{CMD_LINT}}` | Lint command | `clang-tidy --warnings-as-errors='*'` |
| `{{CMD_BENCH}}` | Benchmark command (blank if N/A) | `cmake --build --preset bench` |
| `{{VERSION_FILE}}` | File holding the version constant | `src/main/cpp/it/d4np/memorypool/version.hpp` |
| `{{VERSION_CONST_HINT}}` | How the version constant is named | `PBR_MEMORY_POOL_VERSION_*` |
| `{{PKG_ECOSYSTEM}}` | Dependabot package ecosystem id (blank if none) | `cargo` |

## 5. CI matrix (from the language profile)

| Placeholder | Meaning | Example |
|---|---|---|
| `{{TIER1_PLATFORMS}}` | Human description of CI-gated platforms | `Linux x86_64, Windows x86_64, macOS arm64` |
| `{{#EACH_CI_CELL}}` | Loop over CI matrix cells (`os`, `toolchain`, `preset`) | — |
| `{{CI_SETUP_STEPS}}` | Profile-provided "set up the toolchain" YAML steps | — |
| `{{CI_EXTRA_JOBS}}` | Profile-provided extra jobs (sanitizers, valgrind, …) | — |

## 6. Conventional-commit scopes

| Placeholder | Meaning | Example |
|---|---|---|
| `{{#EACH_SCOPE}}` | Loop over the project's commit scopes | `api`, `build`, `tests`, `docs`, `ci` |

## 7. Spec (from the interview)

| Placeholder | Meaning | Example |
|---|---|---|
| `{{SPEC_OBJECTIVE}}` | Objective & business context paragraph | — |
| `{{#EACH_FUNCTIONAL_REQ}}` | Functional requirements list | — |
| `{{#EACH_NONFUNCTIONAL_REQ}}` | Non-functional requirements list | — |
| `{{#EACH_PUBLIC_API}}` | Public surface entries | — |
| `{{SPEC_VERIFICATION}}` | Verification & test strategy paragraph | — |
| `{{#EACH_MILESTONE1_ITEM}}` | Milestone-1 roadmap items | — |

## 8. Conditional capability flags

These gate optional sections so a CLI does not ship a library's packaging docs, etc.

| Flag | True when |
|---|---|
| `{{#IF_BENCH}}` | The project has a benchmark suite |
| `{{#IF_THREADING}}` | The project exposes concurrency (enables TSan job, thread-safety ADR seed) |
| `{{#IF_PUBLIC_API}}` | The project publishes a stable API/ABI (enables SemVer-ABR notes) |
| `{{#IF_I18N}}` | Docs are translated (enables the i18n manifest + lint check) |
| `{{#IF_PACKAGING}}` | The project is distributed via a package registry |
| `{{#IF_SERVICE}}` | The project is a long-running service (enables deploy/runtime ADR seeds) |
| `{{#IF_ANNOUNCE}}` | Releases/news are announced on social channels (enables the announcements workflow) |
| `{{#IF_PKG_ECOSYSTEM}}` | The language has a Dependabot ecosystem (derived: `PKG_ECOSYSTEM` non-empty) |

## 9. Documentation i18n & announcements

| Placeholder | Meaning | Example |
|---|---|---|
| `{{DOC_DEFAULT_LANG}}` | Canonical on-disk doc language (sources stay English) | `en` |
| `{{I18N_ENABLED}}` | Python literal for the lint's CONFIG (`True`/`False`, capitalized) | `False` |
| `{{#EACH_DOC_LANG}}` | Loop over translation target languages (`code`, `name`) | `it`/`Italian`, `es`/`Spanish` |
| `{{#EACH_ANNOUNCE_CHANNEL}}` | Loop over announcement channels (`name`, `handle`, `mode`) | `X`/`@d4np`/`draft` |

---

## Rendering rules

1. **Unresolved placeholder = hard error.** If a placeholder used in a template has no
   value in `project.yaml`, the render aborts; do not emit `{{...}}` literals to disk.
2. **Blank is intentional.** A key may resolve to empty string (e.g. `{{SRC_BENCH}}` for a
   project with no benchmarks); empty resolution is valid, missing key is not.
3. **`.tmpl` suffix is stripped** on output (`AGENTS.md.tmpl` → `AGENTS.md`). Files without
   `.tmpl` (e.g. `tools/consistency_lint.py`, `docs/adr/template.md`) are copied verbatim
   but still parameterized at their documented `{{...}}` config points.
4. **Path placeholders too.** Directory names in the source tree are produced by expanding
   `{{LANG}}` / `{{GROUP_PATH}}` / `{{PROJECT_SLUG}}`, not copied literally.
