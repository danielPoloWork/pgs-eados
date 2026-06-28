# EADOS —— 企业级智能体交付操作系统

[![CI](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v2.3.0-blue.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![Downloads](https://img.shields.io/github/downloads/danielPoloWork/pgs-eados/total.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../../LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](../../../../.eados-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> 🌐 本页面是项目 [`README.md`](../../../../README.md) 的简体中文翻译。
> **英文版本为唯一权威来源** —— 如本译文与原文不一致，以英文版为准。
> 用其他语言阅读：[English](../../../../README.md) · [日本語](../ja/README.md)。

> 一个与语言无关的**交付操作系统**，面向企业级软件、游戏与移动应用：一条可选用的阶段流水线
> —— `init → design → plan → scaffold → audit → refactor` —— 从第一份 RFC 一直治理到发布。其
> `scaffold` 阶段为*任何*语言批量生成一套**企业级智能体系统**，只需单一 manifest 与参数化的
> template。

EADOS 不是你交付的产品；它是**关于工作如何流转的操作系统** —— 一个声明式、由门禁强制、保留
人工确认的治理层（并非运行时内核）。其 **`scaffold` 阶段就是那座工厂**，批量生产共享同样企业级
结构、GitHub 工作流、质量门禁与 AI 智能体契约的仓库 —— 无论语言、框架或工具如何；其余阶段
（`design`、`plan`、`audit`、`refactor`）把这套治理扩展到整个交付生命周期。每个阶段都是一个可选用的
`/eados <phase>` 命令，作用于一份持久、受门禁校验的 manifest（设计见
[RFC-0001](../../../../.eados-core/docs/rfc/0001-eados-delivery-os.md)）。

> **初次接触？** [`USAGE.md`](../../../../.eados-core/docs/USAGE.md) 是 EADOS 能做什么的完整地图；
> [逐阶段演练](../../walkthrough.md)展示它实际运行。只想安装它？直接前往[快速上手](#快速上手)。

## 目录

- [为什么选择 EADOS](#为什么选择-eados) · [能力一览](#能力一览)
- [你能得到什么](#你能得到什么) · [阶段流水线](#阶段流水线) · [生成如何运作](#生成如何运作)
- [仓库布局](#仓库布局) · [快速上手](#快速上手) · [Quickstart](#quickstart)
- [设计原则](#设计原则为何如此塑形) · [安全态势](#安全态势) · [常见问题](#常见问题)
- [贡献与治理](#贡献与治理) · [溯源](#溯源) · [许可与归属](#许可与归属)

## 为什么选择 EADOS

它回答一个问题：

> *"无论用哪种语言 —— Rust / Python / TypeScript / Go / Java / …… —— 我如何在**每个**项目上
> 获得**同样**的企业级严谨度：智能体、ADR、CI 矩阵、consistency lint、SemVer 治理？"*

把 **Enterprise Project Architect** 智能体指向 EADOS，运行接入访谈，它就会生成新仓库 ——
或者你手工填写 manifest 并以确定性方式渲染，无需智能体。

**为什么不用 cookiecutter / copier / Yeoman？** 它们只**一次性**搭好脚手架就离开。EADOS 是一个
**交付操作系统**，而非一次性模板：

1. **以数据实现语言无关** —— 工具链知识存放在 profile 中，从不硬编码进 template，因此一座工厂
   服务 19+ 种语言（新增一门语言是加数据，而非改代码）。
2. **生成的仓库自我治理** —— 它自带智能体契约、CI、质量门禁与 SemVer 流程，且自给自足
   （运行时不回耦到 EADOS）。
3. **生成只是其中一个阶段** —— `design → plan → audit → refactor` 把治理扩展到整个生命周期，
   作用于一份带角色权限与可追溯性图谱、受门禁校验的持久 manifest。

它**确定且由人把关**：智能体起草，人类审阅并合并；未解析的 placeholder 是硬错误，绝不靠猜测。

## 能力一览

- **生成**任意语言的企业级仓库 —— 已交付 19 个 profile；新增一门语言即加一份数据。
- **治理整个生命周期** —— 六个可选用阶段（`init · design · plan · scaffold · audit · refactor`），
  作用于持久 manifest，并对每次转换设有门禁。
- **可组合的智能体角色**，采用**人设 ≠ 权限**的分离 —— 架构师、reviewer、security-auditor、
  release-manager、product-manager、tech-lead、producer、contribution-reviewer。
- **质量与安全门禁** —— placeholder / profile / 规范完整性、生成的 `consistency_lint`、风险评分，
  以及可追溯性图谱（RFC → 里程碑 → PR → commit → release）。
- **入站贡献评审**（`/eados review`） —— 按信任层级、策略与风险分流非 owner 的 PR；给出处置建议
  （绝不自动合并）。
- **引导式安装器** —— 跨平台 `setup.{sh,command,ps1,bat}`，带**失败即拒绝的 SHA256** 校验与
  追加式、不覆盖的解压。
- **自我改进，版本化且由人把关** —— 经验台账、自动调参器与自评。
- **可选的** i18n（翻译文档 + 新鲜度门禁）、社媒公告与基准测试。
- **无智能体 / 离线路径** —— 仅标准库 Python；从 manifest 确定性渲染。

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

以上每一项都是按企业标准打造的**参数化产物**。通用性存在于三处：

1. **语言 profile**（`orchestrator/profiles/*.yaml`）将每种语言的工具链知识编码为数据
   （build 工具、测试框架、formatter、linter、sanitizer、CI 矩阵、源文件扩展名、命名空间
   风格、版本常量位置）。
2. **项目 manifest**（`orchestrator/project.yaml`）记录维护者的答案 —— 每个 placeholder
   的唯一事实来源。
3. **template**（`templates/**`）就是把项目特定事实替换为 `{{PLACEHOLDERS}}` 后的企业级
   产物。

---

## 阶段流水线

除了一次性生成，EADOS 还在六个**可选用**阶段上治理一个项目 —— 每个都是作用于持久 manifest 的
`/eados <phase>` 命令，每次转换都有确定性门禁（人工确认需把关的转换）。你只采用想要的阶段：只想
生成的用户运行 `/eados scaffold`，其余忽略即可。

| 阶段 | 作用 | 关键产物 / 门禁 |
|---|---|---|
| **`init`** | 框定项目并写出初始 manifest（`delivery_state`）。 | manifest 骨架 |
| **`design`** | 在评审协议下撰写 / 导入 RFC。 | `rfc-approved` |
| **`plan`** | 从 RFC 共创路线图；构建可追溯性图谱。 | `roadmap-covers-rfcs` |
| **`scaffold`** | **生成**受治理的仓库 —— 经典工厂。 | render + `consistency_lint` |
| **`audit`** | 持续风险评分 + 强制的可追溯性 lint。 | `traceability-lint`、风险阈值 |
| **`refactor`** | 通过受门禁、沙箱化、**追加式**的 PR 把既有仓库带到标准。 | 写入受限的沙箱 |

完整细节见 [`USAGE.md`](../../../../.eados-core/docs/USAGE.md) 与
[命令手册](../../../../.eados-core/orchestrator/commands/README.md)。两个跨切面命令在任何阶段都可用：
[`/eados status`](../../../../.eados-core/orchestrator/commands/status.md)（只读体检）与
[`/eados review`](../../../../.eados-core/orchestrator/commands/review.md)（入站 PR 分流）。

---

## 生成如何运作

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
[`orchestrator/generate.md`](../../../../.eados-core/orchestrator/generate.md)。

---

## 仓库布局

```text
pgs-eados/
├── README.md                          # this file
├── AGENTS.md                          # agent contract for EADOS itself (+ the meta-architect persona)
├── CLAUDE.md / GEMINI.md              # tool adapters → defer to AGENTS.md
├── LICENSE
├── .github/workflows/ci.yml           # EADOS's own CI (self-lint + render smoke)
└── .eados-core/                        # ALL the factory machinery — one ignorable folder
    ├── agent/                         # enterprise-architect + composable roles + registry
    │   ├── README.md                  # the agent registry/index
    │   ├── enterprise-architect.md    # the orchestrating "senior project architect"
    │   └── reviewer.md  security-auditor.md  release-manager.md  profile-author.md
    ├── orchestrator/                  # the engine
    │   ├── README.md  interview.md  generate.md  recovery.md  placeholders.md
    │   ├── questionnaire.yaml         # machine-readable question bank
    │   ├── project.yaml.template      # the project manifest skeleton (copied to project.yaml per run)
    │   ├── examples/reference.yaml    # a worked manifest + render-smoke fixture
    │   └── profiles/                  # per-language toolchain knowledge (+ _schema.md)
    ├── templates/                     # the parameterized enterprise scaffolding (the output)
    │   ├── AGENTS.md.tmpl  CLAUDE.md.tmpl  GEMINI.md.tmpl  README.md.tmpl  …
    │   ├── docs/**                    # adr/, patterns/, specs/, bugs/, journal/, workflow/, i18n/
    │   ├── .github/**                 # PR + issue templates, CODEOWNERS, dependabot, ci.yml + release.yml
    │   └── tools/consistency_lint.py  # generic, profile-driven congruence checker
    ├── tools/                         # the factory's own tooling
    │   ├── eados_lint.py               # self-lint: placeholder/profile/playbook integrity
    │   ├── render.py                  # deterministic Mustache-subset renderer
    │   ├── autotune.py                # proposes default changes from accumulated run records
    │   └── self_review.py             # structural quality review of a generated repo
    ├── config/                        # customization overlays (defaults.yaml, house-rules.md)
    ├── learning/                      # lessons ledger + run records (memory / auto-tuning input)
    ├── eval/rubric.md                 # the self-evaluation rubric
    ├── maintenance/stay-current.md    # the profile-refresh routine (+ cron recipe)
    └── docs/adr/                      # ADRs governing EADOS's own design decisions
```

---

## 快速上手

### 前置要求

EADOS 是一座 markdown/YAML 工厂 —— 没有东西需要编译，几乎没有东西需要安装。具体需要什么，
取决于你如何驱动它：

- **以对话方式使用（推荐）** —— 一个能读取 `AGENTS.md` 的 **AI 编码智能体**：Claude Code、
  Gemini Antigravity 或 ChatGPT Codex。
- **以确定性方式使用（无需智能体）** —— 仅需 **Python 3.12+**，用于内置工具（`render.py`、
  `eados_lint.py` 以及生成的 `consistency_lint.py`）；只依赖标准库，无需 `pip install`。
- **为 EADOS 做贡献** —— **git**，用于克隆并提交 pull request。仅仅下载并使用工厂**无需** git。

### 前置准备 —— 获取一个 AI 编码智能体

推荐的（对话式）路径需要一个能读取 `AGENTS.md` 的 **AI 编码智能体**。任选其一安装：

- **Claude Code** —— [安装与配置](https://docs.anthropic.com/en/docs/claude-code)
- **Gemini Antigravity** —— [antigravity.google](https://antigravity.google/)
- **ChatGPT Codex** —— [Codex CLI](https://developers.openai.com/codex/cli)

“**用你的智能体打开该文件夹**”的意思是：在你项目的仓库根目录启动该智能体——它会自动加载
`AGENTS.md` 并采用 Enterprise Project Architect（企业项目架构师）人格，准备开始访谈。

**该用哪个模型？** EADOS 依赖智能体的推理能力，因此越强的模型表现越好。目前它在
**Claude Opus 4.8（high）** 上表现最佳 —— 而 **Fable 5** 尚不可用 —— 其次是 **OpenAI Codex 5.5**
与 **Gemini 3.5 Flash**；**Mistral AI** 与 **Sakana AI** 尚未测试。

> **⚠ AI 智能体可能产生幻觉。** 它们会自信地起草、有时却是错的 —— 在据此行动之前，请**审阅每一处
> diff、RFC 与命令**。EADOS 降低了新手的门槛，但它是一件**强力工具**：在有经验者手中最有效 ——
> 你提供工程判断，智能体提供速度。一切不可逆步骤都归人类所有（打开 / 合并 / 发布）。

**没有智能体？你也不会被卡住** —— 走**确定性路径**：填写 `project.yaml` 并运行 `render.py`
（仅需 Python 3.12+，只用标准库）。参见 [Quickstart](#quickstart) 与 [`USAGE.md`](../../USAGE.md) §3。

### 获取

**引导式安装器（一步）—— 推荐。** 从最新发布获取适合你操作系统的安装器并运行：它会询问安装位置
（新建还是已有仓库、路径），**校验 bundle 的 SHA256**（失败即拒绝），并以**追加方式**解压
（绝不覆盖已有文件）。完整选项（macOS 双击、脚本化参数、离线校验）见
[`USAGE.md`](../../USAGE.md) §6。

```bash
# Linux / macOS —— 下载后运行（会有交互提示）
curl -fsSL https://github.com/danielPoloWork/pgs-eados/releases/latest/download/setup.sh -o setup.sh && sh setup.sh
```

```powershell
# Windows (PowerShell) —— 或从发布中双击 setup.bat
Invoke-WebRequest https://github.com/danielPoloWork/pgs-eados/releases/latest/download/setup.ps1 -OutFile setup.ps1; powershell -ExecutionPolicy Bypass -File setup.ps1
```

**或手动下载 bundle** —— 无需克隆，且你能看到具体执行了什么。bundle 是工厂的自包含、**无前缀**副本
（不含 CI、changelog 或 git 历史）。在**你项目仓库的根目录**解压，其内容 —— `.eados-core/` 以及
智能体契约和 `LICENSE` —— 会直接落在根目录，**而不是**子文件夹里：

```bash
cd my-project        # 你项目的仓库根目录（新建或已有）
curl -L -o /tmp/pgs-eados-bundle.tar.gz \
  https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz
tar xzf /tmp/pgs-eados-bundle.tar.gz   # 将 .eados-core/、AGENTS.md 等解压到当前目录
```

在 **Windows（PowerShell）** 上 —— `tar` 随 Windows 10+ 一起提供：

```powershell
cd my-project
Invoke-WebRequest -Uri https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz -OutFile $env:TEMP/pgs-eados-bundle.tar.gz
tar -xzf $env:TEMP/pgs-eados-bundle.tar.gz   # 将 .eados-core/、AGENTS.md 等解压到当前目录
```

现在你应当得到 `my-project/.eados-core/`（与 `AGENTS.md` 并列）。想要 ZIP 或用浏览器？从
[最新发布](https://github.com/danielPoloWork/pgs-eados/releases/latest)下载任一资产，并在**仓库根目录**
解压（内容位于顶层 —— 无外层文件夹）。随后按 [Quickstart](#quickstart) 确认并生成：

```bash
ls .eados-core                           # orchestrator/ templates/ tools/ …
python .eados-core/tools/eados_lint.py    # 可选：确认工厂内部一致
```

**克隆仓库 —— 为 EADOS 做贡献**（完整仓库：CI、changelog、历史）：

```bash
git clone https://github.com/danielPoloWork/pgs-eados.git && cd pgs-eados
```

## Quickstart

你通过 Enterprise Project Architect 智能体以对话方式驱动 EADOS。

1. **用你的 AI 编码智能体打开该项目文件夹**（Claude Code、Gemini、Codex）。它会读取
   `AGENTS.md` 并采用元架构师人设。
2. **说出你想构建什么。** 例如 *"新项目：一个 Rust 令牌桶限流器，library，GitHub owner
   `acme`，默认分支 `main`。"*
3. **回答访谈。** 架构师会走完
   [`orchestrator/interview.md`](../../../../.eados-core/orchestrator/interview.md) —— 语言、框架、
   工具、治理与功能规范 —— 只询问那些它无法安全使用默认值的问题。
4. **审阅 manifest。** 架构师写出 `orchestrator/project.yaml`，并在生成任何东西之前先展示给你确认。
5. **生成。** 架构师遵循
   [`orchestrator/generate.md`](../../../../.eados-core/orchestrator/generate.md) 渲染新仓库，运行
   consistency lint，并起草引导 PR。

你永远不必记住那些企业级规则 —— 它们已编码进 template 并由 lint 强制执行。你只需做项目特定的决定。

### 或者自己渲染（确定性，无需智能体）

访谈的唯一产物是一个填好的 manifest，因此你也可以手工填写并在没有智能体的情况下渲染：

```bash
cp .eados-core/orchestrator/project.yaml.template .eados-core/orchestrator/project.yaml
# edit .eados-core/orchestrator/project.yaml — see .eados-core/orchestrator/examples/reference.yaml for a worked one
python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place
python tools/consistency_lint.py     # the generated repo's own gate (now at the repo root)
```

`render.py` 严格执行
[`orchestrator/placeholders.md`](../../../../.eados-core/orchestrator/placeholders.md) 中的替换，
尊重 `capabilities.*` 门禁，保持 GitHub Actions 的 `${{ … }}` 不变，并在**遇到任何未解析的
placeholder 时中止**。EADOS 自身 CI 中的 render-smoke 任务会在每次推送时针对
[`orchestrator/examples/reference.yaml`](../../../../.eados-core/orchestrator/examples/reference.yaml)
运行它。

### 工具

| 工具 | 作用 |
|---|---|
| [`tools/render.py`](../../../../.eados-core/tools/render.py) | 将 manifest 渲染成一个仓库（确定性）。 |
| [`tools/eados_lint.py`](../../../../.eados-core/tools/eados_lint.py) | 自检：placeholder 完整性、profile 完整性、手册引用。 |
| `templates/tools/consistency_lint.py` | 随每个生成仓库一并交付；强制其跨产物一致性。 |

---

## 设计原则（为何如此塑形）

- **每个事实只有一个真理来源。** 一个项目事实（名称、语言、owner、命名空间）在
  `project.yaml` 中只记录一次，并通过 placeholder 流向每个产物。这与生成的
  `consistency_lint.py` 所强制的反漂移纪律如出一辙。
- **对任何语言开放。** EADOS 不局限于固定清单 —— 已交付的十九个 profile（C、C++、C#、
  VB.NET、Java、Kotlin、Scala、Python、Ruby、PHP、JavaScript、TypeScript、Go、Rust、
  Swift、Dart、Lua、COBOL、Pascal）都是**种子**。支持一门新语言意味着把
  [`profiles/_template.yaml`](../../../../.eados-core/orchestrator/profiles/_template.yaml) 复制为一个
  `profiles/<lang>.yaml` —— 永不修改 template，因为它只知道*角色*（build 工具、测试运行器、
  formatter），从不知道具体工具。不存在"不支持的语言"，只有"尚未建立 profile"。
- **生成的仓库自我治理。** EADOS 的职责止于生成。新仓库自带其 `AGENTS.md`、CI 与 lint，
  因此自给自足，且*不*回耦到 EADOS。
- **磁盘上是英文，聊天中可任意语言。** 每个生成的产物都是英文；访谈本身可以用维护者的语言进行。
- **不可逆步骤归人类所有。** 智能体起草分支、提交与 PR；人类负责打开、审阅与合并。EADOS 逐字
  复刻了这条边界。

---

## 安全态势

EADOS 把供应链与智能体边界视为一等公民：

- **失败即拒绝的安装器完整性。** 引导式安装器在解压前会用发布的 `SHA256SUMS` 校验 bundle 的
  **SHA256**；未通过校验的 bundle 会被拒绝（没有盲目的 `curl | sh`），且以**追加方式**解压 ——
  绝不覆盖已有文件。
- **写入受限的生成。** 渲染器与 `refactor` 沙箱拒绝任何逃逸出目标的写入 —— 路径穿越 / 绝对路径 /
  符号链接 / `.git` / 覆盖（[ADR-0007](../../../../.eados-core/docs/adr/0007-renderer-write-guards-and-validation-independence.md)
  原则）。
- **不可信的入站代码。** `/eados review` 按信任层级分类非 owner 的 PR，并标记“投毒流水线”的暴露面
  （工作流改动、新依赖、对密钥的触达）；非 owner 的提交**绝不被合并** —— 好的想法以署名的方式
  在内部重新实现。
- **固定且可审计的 CI。** GitHub Actions 以 SHA 固定（Dependabot + 自动同步门禁保持固定值诚实）；
  自检门禁**离线**运行（门禁路径中无网络）。
- **每个不可逆步骤都归人类所有** —— 智能体起草；人类打开、合并并发布。
- **可审计的谱系。** 一张可追溯性图谱把每次发布回溯到 PR → commit → 里程碑 → RFC；悬空的边会让
  lint 失败。

## 常见问题

**这是 cookiecutter / 项目模板吗？** 不是 —— 见[为什么选择 EADOS](#为什么选择-eados)。生成只是一个受
治理的交付 OS 的一个阶段，且产物自带治理。

**我需要 AI 智能体吗？** 不需要。推荐对话式路径，但**确定性路径**（填写 `project.yaml`、运行
`render.py`）只需标准库 Python 3.12+。

**支持哪些语言？** 任意。今天交付 19 个 profile；新增一门语言是一份数据文件
（`profiles/<lang>.yaml`），从不改 template。

**生成的仓库在运行时依赖 EADOS 吗？** 不 —— 它自给自足；自带的 `AGENTS.md`、CI 与 lint 随其一同
存在。EADOS 的职责止于生成。

**能离线 / 气隙使用吗？** 能。安装器支持 `--from` + `--sums-file`（校验手工下载的 bundle），确定性
渲染与门禁都无需网络。

**哪个模型最好？** 见[前置准备](#前置准备--获取一个-ai-编码智能体) —— 目前 **Claude Opus 4.8
（high）** 领先，其次是 Codex 5.5 与 Gemini 3.5 Flash。

**EADOS 会把我的代码或数据发往任何地方吗？** 不会 —— 它是 markdown / YAML / 标准库 Python，无遥测。
你的 AI 智能体是独立工具，有其自己的数据策略。

---

## 贡献与治理

EADOS 由 **owner 治理**：贡献者通过 pull request *提出建议*，owner（`@danielPoloWork`）*决定*并执行
**squash-merge**。任何人都不得直接向 `main` 推送。

- 从 [`CONTRIBUTING.md`](../../../../CONTRIBUTING.md) 开始：fork → 特性分支 → Conventional Commits →
  运行门禁（`eados_lint`、render-smoke、`tools/tests/`）→ 开启 PR。
- `main` 仅接受 **squash** 合并方式；完整的分支保护 ruleset（要求 PR、限制谁可推送）在仓库公开后生效。
- 安全问题绝不走公开 issue —— 见 [`SECURITY.md`](../../../../SECURITY.md)。问题与想法请使用 GitHub
  Discussions。发布遵循 SemVer 并记录于 [`CHANGELOG.md`](../../../../CHANGELOG.md)。完整契约见
  [`AGENTS.md`](../../../../AGENTS.md)。

---

## 溯源

EADOS 中的每条规则、template 与门禁都是有意为之：设计在
[RFC-0001](../../../../.eados-core/docs/rfc/0001-eados-delivery-os.md) 中得到批准，每个非平凡决策都记录于
[`docs/adr/`](../../../../.eados-core/docs/adr/)。

## 许可与归属

EADOS 以 **[MIT 许可证](../../../../LICENSE)** 发布 —— © 2026 **Daniel Polo**。由 **Daniel Polo**
（`@danielPoloWork`）维护并实行 **owner 治理**：贡献者通过 pull request *提出建议*，owner *决定*并执行
squash-merge（见[贡献与治理](#贡献与治理)）。随工厂一起交付的 `LICENSE` 是有意为之的 ——
`render.py` 会以它作为每个生成项目许可证的来源，因此 EADOS 产出的每个仓库都归其各自 owner 所有并采用
MIT 许可。
