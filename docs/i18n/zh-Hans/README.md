# 企业级智能体架构编排器（EAAO）

[![CI](https://github.com/danielPoloWork/pgs-eaao/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eaao/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](../../../.eaao-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> 🌐 本页面是项目 [`README.md`](../../../README.md) 的简体中文翻译（基于提交 `8ca27b2`）。
> **英文版本为唯一权威来源** —— 如本译文与原文不一致，以英文版为准。
> 用其他语言阅读：[English](../../../README.md) · [日本語](../ja/README.md)。

> 一个与语言无关的元项目，它为*任何*新项目、*任何*语言、*任何*工具链，复刻
> `pbr-cpp-memory-pool` 的**企业级智能体系统** —— 方法是访谈维护者，将答案记录到单一
> manifest 中，并从参数化的 template 渲染出一个完整、受治理的仓库。

EAAO 不是产品。EAAO 是那座**工厂**，它批量生产的产品都共享同样的技术-企业级结构、同样的
GitHub 工作流、同样的质量门禁、同样的 AI 智能体契约 —— 无论编程语言、框架或工具如何。

它的存在是为了回答一个问题：

> *"我们把 `pbr-cpp-memory-pool` 做到了企业标准 —— 智能体、ADR、CI 矩阵、consistency
> lint、SemVer 治理。下一个项目用的是 Rust / Python / TypeScript / Go / Java / ……，
> 我们如何在它上面获得**同样**的严谨度？"*

答案是：把 **Enterprise Project Architect** 智能体指向 EAAO，运行**接入访谈**，让它生成新仓库。

> **初次接触？** 阅读 [`.eaao-core/docs/USAGE.md`](../../../.eaao-core/docs/USAGE.md) ——
> EAAO 能做什么、如何运作、哪些是固定的、哪些可由你定制的完整地图。

---

## 你能得到什么

针对一个全新的项目想法运行编排器，会产出一个在第零天就已经包含以下内容的新仓库：

| 关注点 | 复刻的产物 |
|---|---|
| **智能体契约** | `AGENTS.md`（唯一事实来源）+ `CLAUDE.md` / `GEMINI.md` 适配器，其中资深架构师人设已绑定到*新项目自身的*语言与技术栈 |
| **源码布局** | Maven 风格的跨语言树 `src/{main,test,bench}/<lang>/<group-path>/<project>/` —— 形状一致，语言对应的层段相应替换 |
| **Git 治理** | Conventional Commits、分支命名、一项一 PR / 一次一 PR、智能体与人类的边界、PR 模板 + PR 元数据策略 |
| **GitHub 自动化** | CI **与**发布工作流、Dependabot、CODEOWNERS、issue 表单（+ Discussions/Security 路由）、一套标签集，以及用于分支保护 / ruleset / Pages / Discussions 的一次性 `gh` 配置脚本 |
| **文档体系** | ADR（+ 模板 + 索引）、设计模式目录（+ 8 类分类法）、规范模板、会话日志、缺陷台账、changelog 拆分、发布说明，以及可选的 **i18n**（翻译文档 + 新鲜度门禁） |
| **质量门禁** | 一个接入所选工具链 build / test / format / lint / sanitize 命令的 GitHub Actions CI 工作流，外加可由智能体运行的 `consistency_lint.py` |
| **版本与对外沟通** | SemVer 策略、里程碑驱动的发布流程、发布后维护 / 热修复 / 弃用 / 安全协议，以及可选的**公告**工作流（X / Discord / LinkedIn / Reddit ……） |

以上每一项都是 `pbr-cpp-memory-pool` 中既有可用之物的**参数化副本**。通用性存在于三处：

1. **语言 profile**（`orchestrator/profiles/*.yaml`）将每种语言的工具链知识编码为数据
   （build 工具、测试框架、formatter、linter、sanitizer、CI 矩阵、源文件扩展名、命名空间
   风格、版本常量位置）。
2. **项目 manifest**（`orchestrator/project.yaml`）记录维护者的答案 —— 每个 placeholder
   的唯一事实来源。
3. **template**（`templates/**`）就是把项目特定事实替换为 `{{PLACEHOLDERS}}` 后的 `pbr`
   产物。

---

## 它如何运作（流水线）

```text
                 ┌─────────────────────────────────────────────────────────┐
                 │  Enterprise Project Architect agent (agent/...)         │
                 │  persona: senior architect, 20+ yrs, enterprise bar     │
                 └─────────────────────────────────────────────────────────┘
                                          │
   1. INTERVIEW            ───────────────┼───────────────  orchestrator/interview.md
      Ask the maintainer about language(s), frameworks, tools,                 +
      governance, and the project spec (with follow-up questions).   orchestrator/questionnaire.yaml
                                          │
   2. RESOLVE PROFILE      ───────────────┼───────────────  orchestrator/profiles/<lang>.yaml
      Load the toolchain profile(s) for the chosen language(s);
      the profile fills the toolchain-shaped placeholders.
                                          │
   3. WRITE MANIFEST       ───────────────┼───────────────  orchestrator/project.yaml
      Merge answers + profile into one parameter manifest.
                                          │
   4. RENDER              ────────────────┼───────────────  templates/**  →  <new-repo>/**
      Substitute {{PLACEHOLDERS}}, lay down the source tree,
      seed ADR-0001/0002, the roadmap's Milestone 1, the spec.
                                          │
   5. VERIFY              ────────────────┼───────────────  templates/tools/consistency_lint.py
      Run the consistency lint; initialize git; draft the first PR.
                                          ▼
                            A new, governed, enterprise-grade repository
```

完整、有序的流程即**生成手册**：
[`orchestrator/generate.md`](../../../.eaao-core/orchestrator/generate.md)。

---

## 仓库布局

```text
pgs-eaao/
├── README.md                          # this file
├── AGENTS.md                          # agent contract for EAAO itself (+ the meta-architect persona)
├── CLAUDE.md / GEMINI.md              # tool adapters → defer to AGENTS.md
├── LICENSE
├── .github/workflows/ci.yml           # EAAO's own CI (self-lint + render smoke)
└── .eaao-core/                        # ALL the factory machinery — one ignorable folder
    ├── agent/                         # enterprise-architect + composable roles + registry
    │   ├── README.md                  # the agent registry/index
    │   ├── enterprise-architect.md    # the orchestrating "senior project architect"
    │   └── reviewer.md  security-auditor.md  release-manager.md  profile-author.md
    ├── orchestrator/                  # the engine
    │   ├── README.md  interview.md  generate.md  recovery.md  placeholders.md
    │   ├── questionnaire.yaml         # machine-readable question bank
    │   ├── project.yaml.template      # the project manifest skeleton (copied to project.yaml per run)
    │   ├── examples/reference.yaml    # a worked manifest (pbr-cpp-memory-pool) + render-smoke fixture
    │   └── profiles/                  # per-language toolchain knowledge (+ _schema.md)
    ├── templates/                     # the parameterized enterprise scaffolding (the output)
    │   ├── AGENTS.md.tmpl  CLAUDE.md.tmpl  GEMINI.md.tmpl  README.md.tmpl  …
    │   ├── docs/**                    # adr/, patterns/, specs/, bugs/, journal/, workflow/, i18n/
    │   ├── .github/**                 # PR + issue templates, CODEOWNERS, dependabot, ci.yml + release.yml
    │   └── tools/consistency_lint.py  # generic, profile-driven congruence checker
    ├── tools/                         # the factory's own tooling
    │   ├── eaao_lint.py               # self-lint: placeholder/profile/playbook integrity
    │   ├── render.py                  # deterministic Mustache-subset renderer
    │   ├── autotune.py                # proposes default changes from accumulated run records
    │   └── self_review.py             # structural quality review of a generated repo
    ├── config/                        # customization overlays (defaults.yaml, house-rules.md)
    ├── learning/                      # lessons ledger + run records (memory / auto-tuning input)
    ├── eval/rubric.md                 # the self-evaluation rubric
    ├── maintenance/stay-current.md    # the profile-refresh routine (+ cron recipe)
    └── docs/adr/                      # ADRs governing EAAO's own design decisions
```

---

## 快速上手

### 前置要求

EAAO 是一座 markdown/YAML 工厂 —— 没有东西需要编译，几乎没有东西需要安装：

- **git** 和一个能读取 `AGENTS.md` 的 **AI 编码智能体** —— Claude Code、Gemini Antigravity
  或 ChatGPT Codex（通常你以此驱动它）；
- **Python 3.12+** —— 仅用于内置工具（`tools/render.py`、`tools/eaao_lint.py` 以及生成的
  `consistency_lint.py`）。三者均只依赖标准库；无需 `pip install`。

### 获取

```bash
git clone https://github.com/danielPoloWork/pgs-eaao.git
cd pgs-eaao
python tools/eaao_lint.py        # optional: confirm the factory is internally congruent
```

## Quickstart

你通过 Enterprise Project Architect 智能体以对话方式驱动 EAAO。

1. **用你的 AI 编码智能体打开本仓库**（Claude Code、Gemini、Codex）。它会读取
   `AGENTS.md` 并采用元架构师人设。
2. **说出你想构建什么。** 例如 *"新项目：一个 Rust 令牌桶限流器，library，GitHub owner
   `acme`，默认分支 `main`。"*
3. **回答访谈。** 架构师会走完
   [`orchestrator/interview.md`](../../../.eaao-core/orchestrator/interview.md) —— 语言、框架、
   工具、治理与功能规范 —— 只询问那些它无法安全使用默认值的问题。
4. **审阅 manifest。** 架构师写出 `orchestrator/project.yaml`，并在生成任何东西之前先展示给你确认。
5. **生成。** 架构师遵循
   [`orchestrator/generate.md`](../../../.eaao-core/orchestrator/generate.md) 渲染新仓库，运行
   consistency lint，并起草引导 PR。

你永远不必记住那些企业级规则 —— 它们已编码进 template 并由 lint 强制执行。你只需做项目特定的决定。

### 或者自己渲染（确定性，无需智能体）

访谈的唯一产物是一个填好的 manifest，因此你也可以手工填写并在没有智能体的情况下渲染：

```bash
cp orchestrator/project.yaml.template orchestrator/project.yaml
# edit orchestrator/project.yaml — see orchestrator/examples/reference.yaml for a worked one
python tools/render.py orchestrator/project.yaml --out ../my-new-repo
cd ../my-new-repo && python tools/consistency_lint.py     # the generated repo's own gate
```

`render.py` 严格执行
[`orchestrator/placeholders.md`](../../../.eaao-core/orchestrator/placeholders.md) 中的替换，
尊重 `capabilities.*` 门禁，保持 GitHub Actions 的 `${{ … }}` 不变，并在**遇到任何未解析的
placeholder 时中止**。EAAO 自身 CI 中的 render-smoke 任务会在每次推送时针对
[`orchestrator/examples/reference.yaml`](../../../.eaao-core/orchestrator/examples/reference.yaml)
运行它。

### 工具

| 工具 | 作用 |
|---|---|
| [`tools/render.py`](../../../.eaao-core/tools/render.py) | 将 manifest 渲染成一个仓库（确定性）。 |
| [`tools/eaao_lint.py`](../../../.eaao-core/tools/eaao_lint.py) | 自检：placeholder 完整性、profile 完整性、手册引用。 |
| `templates/tools/consistency_lint.py` | 随每个生成仓库一并交付；强制其跨产物一致性。 |

---

## 设计原则（为何如此塑形）

- **每个事实只有一个真理来源。** 一个项目事实（名称、语言、owner、命名空间）在
  `project.yaml` 中只记录一次，并通过 placeholder 流向每个产物。这与生成的
  `consistency_lint.py` 所强制的反漂移纪律如出一辙。
- **对任何语言开放。** EAAO 不局限于固定清单 —— 已交付的十九个 profile（C、C++、C#、
  VB.NET、Java、Kotlin、Scala、Python、Ruby、PHP、JavaScript、TypeScript、Go、Rust、
  Swift、Dart、Lua、COBOL、Pascal）都是**种子**。支持一门新语言意味着把
  [`profiles/_template.yaml`](../../../.eaao-core/orchestrator/profiles/_template.yaml) 复制为一个
  `profiles/<lang>.yaml` —— 永不修改 template，因为它只知道*角色*（build 工具、测试运行器、
  formatter），从不知道具体工具。不存在"不支持的语言"，只有"尚未建立 profile"。
- **生成的仓库自我治理。** EAAO 的职责止于生成。新仓库自带其 `AGENTS.md`、CI 与 lint，
  因此自给自足，且*不*回耦到 EAAO。
- **磁盘上是英文，聊天中可任意语言。** 与参考项目一样，每个生成的产物都是英文；访谈本身
  可以用维护者的语言进行。
- **不可逆步骤归人类所有。** 智能体起草分支、提交与 PR；人类负责打开、审阅与合并。EAAO 逐字
  复刻了这条边界。

---

## 贡献与治理

EAAO 由 **owner 治理**：贡献者通过 pull request *提出建议*，owner（`@danielPoloWork`）*决定*并执行
**squash-merge**。任何人都不得直接向 `main` 推送。

- 从 [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) 开始：fork → 特性分支 → Conventional Commits →
  运行门禁（`eaao_lint`、render-smoke、`tools/tests/`）→ 开启 PR。
- `main` 仅接受 **squash** 合并方式；完整的分支保护 ruleset（要求 PR、限制谁可推送）在仓库公开后生效。
- 安全问题绝不走公开 issue —— 见 [`SECURITY.md`](../../../SECURITY.md)。问题与想法请使用 GitHub
  Discussions。发布遵循 SemVer 并记录于 [`CHANGELOG.md`](../../../CHANGELOG.md)。完整契约见
  [`AGENTS.md`](../../../AGENTS.md)。

---

## 溯源

EAAO 是从 `pbr-cpp-memory-pool` 逆向工程而来 —— 这里的每条规则、template 与门禁，都在那个
项目的 `AGENTS.md`、`docs/`、`.github/` 和 `tools/consistency_lint.py` 中有确切的出处。
塑造此次泛化的决策记录见 [`docs/adr/`](../../../.eaao-core/docs/adr/)。
