# エンタープライズ・エージェント型アーキテクチャ・オーケストレーター（EAAO）

[![CI](https://github.com/danielPoloWork/pgs-eaao/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eaao/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](../../../.eaao-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> 🌐 本ページはプロジェクト [`README.md`](../../../README.md) の日本語訳です（コミット `8ca27b2` 時点）。
> **英語版が唯一の正典** —— 本訳が原文と食い違う場合は英語版が優先されます。
> 他の言語で読む：[English](../../../README.md) · [简体中文](../zh-Hans/README.md)。

> 言語非依存のメタプロジェクト。維持者へのインタビューを行い、その回答を単一の manifest に
> 記録し、パラメータ化された template からレンダリングすることで、*あらゆる*新規プロジェクト・
> *あらゆる*言語・*あらゆる*ツールチェーンに対して `pbr-cpp-memory-pool` の
> **エンタープライズ・エージェント型システム**を再現します。

EAAO は製品ではありません。EAAO は、プログラミング言語・フレームワーク・ツールを問わず、
同じ技術-エンタープライズ構造、同じ GitHub ワークフロー、同じ品質ゲート、同じ AI エージェント
契約を備えた製品を打ち出す**ファクトリ**です。

EAAO はある一つの問いに答えるために存在します：

> *「`pbr-cpp-memory-pool` をエンタープライズ水準で作り上げた —— エージェント、ADR、CI 行列、
> consistency lint、SemVer ガバナンス。では、次のプロジェクト（Rust / Python / TypeScript /
> Go / Java / ……）で**同じ**厳密さをどう得るのか？」*

その答え：**Enterprise Project Architect** エージェントを EAAO に向け、**インテイク・
インタビュー**を実行し、新しいリポジトリを生成させること。

> **はじめての方へ。** [`.eaao-core/docs/USAGE.md`](../../../.eaao-core/docs/USAGE.md) を
> お読みください —— EAAO に何ができるか、どう動くか、何が固定で何をカスタマイズできるかの
> 全体地図です。

---

## 得られるもの

新しいプロジェクトのアイデアに対してオーケストレーターを実行すると、第0日の時点で次の内容を
すでに含む新規リポジトリが生成されます：

| 関心事 | 再現される成果物 |
|---|---|
| **エージェント契約** | `AGENTS.md`（唯一の真実の源）+ `CLAUDE.md` / `GEMINI.md` アダプタ。シニアアーキテクトのペルソナが*新規プロジェクト自身の*言語とスタックに束縛されます |
| **ソースレイアウト** | Maven 形式のクロス言語ツリー `src/{main,test,bench}/<lang>/<group-path>/<project>/` —— 形は同一、言語に応じたセグメントに置換 |
| **Git ガバナンス** | Conventional Commits、ブランチ命名、1項目1 PR / 同時1 PR、エージェントと人間の境界、PR テンプレート + PR メタデータ方針 |
| **GitHub 自動化** | CI **および**リリースワークフロー、Dependabot、CODEOWNERS、issue フォーム（+ Discussions/Security ルーティング）、ラベルセット、ブランチ保護 / ruleset / Pages / Discussions 用の一回限り `gh` セットアップスクリプト |
| **ドキュメント体系** | ADR（+ テンプレート + 索引）、デザインパターン目録（+ 8 分類のタクソノミー）、仕様テンプレート、セッションジャーナル、バグ台帳、changelog 分割、リリース、そしてオプトインの **i18n**（翻訳文書 + 新鮮度ゲート） |
| **品質ゲート** | 選択したツールチェーンの build / test / format / lint / sanitize コマンドに接続された GitHub Actions CI ワークフロー、加えてエージェントが実行可能な `consistency_lint.py` |
| **バージョニングと対外発信** | SemVer 方針、マイルストーン駆動のリリースフロー、リリース後の保守 / ホットフィックス / 非推奨化 / セキュリティ手順、そしてオプトインの**アナウンス**ワークフロー（X / Discord / LinkedIn / Reddit ……） |

これらはいずれも `pbr-cpp-memory-pool` で既に機能しているものの**パラメータ化されたコピー**です。
汎用性は三つの場所に宿ります：

1. **言語 profile**（`orchestrator/profiles/*.yaml`）は、言語ごとのツールチェーン知識を
   データとして符号化します（build ツール、テストフレームワーク、formatter、linter、
   sanitizer、CI 行列、ソースファイル拡張子、名前空間スタイル、バージョン定数の位置）。
2. **プロジェクト manifest**（`orchestrator/project.yaml`）は維持者の回答を取り込みます ——
   すべての placeholder にとっての唯一の真実の源です。
3. **template**（`templates/**`）は、プロジェクト固有の事実を `{{PLACEHOLDERS}}` に
   置き換えた `pbr` の成果物そのものです。

---

## どう動くか（パイプライン）

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

完全で順序づけられた手順が**生成プレイブック**です：
[`orchestrator/generate.md`](../../../.eaao-core/orchestrator/generate.md)。

---

## リポジトリ構成

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

## はじめかた

### 必要要件

EAAO は markdown/YAML のファクトリです —— コンパイルするものは何もなく、インストールも
ほとんど不要です：

- **git** と `AGENTS.md` を読む **AI コーディングエージェント** —— Claude Code、
  Gemini Antigravity、または ChatGPT Codex（通常これで駆動します）；
- **Python 3.12+** —— 同梱ツール（`tools/render.py`、`tools/eaao_lint.py`、および生成される
  `consistency_lint.py`）専用。三つとも標準ライブラリのみで `pip install` は不要です。

### 入手

```bash
git clone https://github.com/danielPoloWork/pgs-eaao.git
cd pgs-eaao
python tools/eaao_lint.py        # optional: confirm the factory is internally congruent
```

## Quickstart

EAAO は Enterprise Project Architect エージェントを通じて会話的に駆動します。

1. **本リポジトリを AI コーディングエージェントで開く**（Claude Code、Gemini、Codex）。
   エージェントは `AGENTS.md` を読み、メタアーキテクトのペルソナを採用します。
2. **作りたいものを伝える。** 例：*「新規プロジェクト：Rust のトークンバケット・レート
   リミッタ、library、GitHub owner `acme`、デフォルトブランチ `main`。」*
3. **インタビューに答える。** アーキテクトは
   [`orchestrator/interview.md`](../../../.eaao-core/orchestrator/interview.md) を辿り —— 言語、
   フレームワーク、ツール、ガバナンス、機能仕様 —— 安全に既定値を採れない問いだけを尋ねます。
4. **manifest を確認する。** アーキテクトは `orchestrator/project.yaml` を書き、何かを生成する
   前にあなたへ確認のため提示します。
5. **生成する。** アーキテクトは
   [`orchestrator/generate.md`](../../../.eaao-core/orchestrator/generate.md) に従って新リポジトリ
   をレンダリングし、consistency lint を実行し、ブートストラップ PR を起草します。

エンタープライズ規則を覚えておく必要はありません —— それらは template に符号化され lint で
強制されます。あなたはプロジェクト固有の決定だけを行います。

### あるいは自分でレンダリングする（決定的、エージェント不要）

インタビューの唯一の出力は埋められた manifest なので、手で埋めてエージェントなしで
レンダリングすることもできます：

```bash
cp orchestrator/project.yaml.template orchestrator/project.yaml
# edit orchestrator/project.yaml — see orchestrator/examples/reference.yaml for a worked one
python tools/render.py orchestrator/project.yaml --out ../my-new-repo
cd ../my-new-repo && python tools/consistency_lint.py     # the generated repo's own gate
```

`render.py` は
[`orchestrator/placeholders.md`](../../../.eaao-core/orchestrator/placeholders.md) の置換を
厳密に実行し、`capabilities.*` ゲートを尊重し、GitHub Actions の `${{ … }}` はそのまま残し、
**未解決の placeholder があれば中断**します。EAAO 自身の CI の render-smoke ジョブは、毎プッシュ
時にこれを
[`orchestrator/examples/reference.yaml`](../../../.eaao-core/orchestrator/examples/reference.yaml)
に対して実行します。

### ツール

| ツール | 役割 |
|---|---|
| [`tools/render.py`](../../../.eaao-core/tools/render.py) | manifest をリポジトリへレンダリング（決定的）。 |
| [`tools/eaao_lint.py`](../../../.eaao-core/tools/eaao_lint.py) | 自己 lint：placeholder の整合性、profile の完全性、プレイブック参照。 |
| `templates/tools/consistency_lint.py` | 各生成リポジトリへ同梱され、その成果物間の整合性を強制。 |

---

## 設計原則（なぜこの形なのか）

- **事実ごとに真実の源は一つ。** プロジェクトの事実（名前、言語、owner、名前空間）は
  `project.yaml` に一度だけ記録され、placeholder を介してすべての成果物へ流れます。これは
  生成される `consistency_lint.py` が強制するのと同じ反ドリフトの規律です。
- **あらゆる言語に開かれている。** EAAO は固定リストに縛られません —— 同梱の十九個の profile
  （C、C++、C#、VB.NET、Java、Kotlin、Scala、Python、Ruby、PHP、JavaScript、TypeScript、Go、
  Rust、Swift、Dart、Lua、COBOL、Pascal）は**種**です。新しい言語の対応とは
  [`profiles/_template.yaml`](../../../.eaao-core/orchestrator/profiles/_template.yaml) を一つの
  `profiles/<lang>.yaml` にコピーすることであり、template を編集することは決してありません。
  template は*役割*（build ツール、テストランナー、formatter）だけを知り、具体的なツールは
  知りません。「非対応の言語」は存在せず、あるのは「まだ profile 化していない」だけです。
- **生成されたリポジトリは自己統治する。** EAAO の職務は生成で終わります。新リポジトリは
  自前の `AGENTS.md`、CI、lint を備えるため自給自足で、EAAO へ逆結合し*ません*。
- **ディスク上は英語、チャットでは任意の言語。** 参照プロジェクトと同様、生成される成果物は
  すべて英語です。インタビュー自体は維持者の言語で行えます。
- **不可逆な手順は人間が所有する。** エージェントはブランチ・コミット・PR を起草し、人間が
  開き、レビューし、マージします。EAAO はこの境界を逐語的に再現します。

---

## コントリビューションとガバナンス

EAAO は **owner ガバナンス**です：コントリビューターは pull request で*提案*し、owner
（`@danielPoloWork`）が*決定*し **squash-merge** します。誰も `main` へ直接 push しません。

- まず [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) から：fork → フィーチャーブランチ →
  Conventional Commits → ゲート実行（`eaao_lint`、render-smoke、`tools/tests/`）→ PR を開く。
- `main` は **squash** マージ方式のみを受け付けます。完全なブランチ保護 ruleset（PR 必須、
  push できる者の制限）はリポジトリ公開後に有効になります。
- セキュリティ問題は公開 issue に書きません —— [`SECURITY.md`](../../../SECURITY.md) を参照。
  質問やアイデアは GitHub Discussions へ。リリースは SemVer に従い
  [`CHANGELOG.md`](../../../CHANGELOG.md) に記録されます。完全な契約は
  [`AGENTS.md`](../../../AGENTS.md) です。

---

## 来歴

EAAO は `pbr-cpp-memory-pool` からリバースエンジニアリングされています —— ここにあるすべての
規則・template・ゲートは、そのプロジェクトの `AGENTS.md`、`docs/`、`.github/`、
`tools/consistency_lint.py` に具体的な出自を持ちます。この一般化を形づくった決定については
[`docs/adr/`](../../../.eaao-core/docs/adr/) を参照してください。
