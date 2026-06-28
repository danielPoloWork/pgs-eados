# EADOS —— エンタープライズ・エージェント型デリバリー OS

[![CI](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v2.3.0-blue.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![Downloads](https://img.shields.io/github/downloads/danielPoloWork/pgs-eados/total.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../../LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Language profiles: 19](https://img.shields.io/badge/language%20profiles-19-success.svg)](../../../../.eados-core/orchestrator/profiles/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fe5196.svg)](https://www.conventionalcommits.org/)

> 🌐 本ページはプロジェクト [`README.md`](../../../../README.md) の日本語訳です。
> **英語版が唯一の正典** —— 本訳が原文と食い違う場合は英語版が優先されます。
> 他の言語で読む：[English](../../../../README.md) · [简体中文](../zh-Hans/README.md)。

> 言語非依存の**デリバリー・オペレーティング・システム**。エンタープライズのソフトウェア・
> ゲーム・モバイルアプリ向けに、オプトインのフェーズ・パイプライン
> —— `init → design → plan → scaffold → audit → refactor` —— で、最初の RFC からリリースまで
> プロジェクトを統治します。その `scaffold` フェーズは、単一の manifest とパラメータ化された
> template から、*あらゆる*言語向けに**エンタープライズ・エージェント型システム**を打ち出します。

EADOS は出荷する製品ではなく、**仕事の流れ方そのものを司るオペレーティング・システム**です
—— 宣言的で、ゲートで強制され、人間が確認する統治層（ランタイムのカーネルではありません）。
その **`scaffold` フェーズがファクトリ**であり、言語・フレームワーク・ツールを問わず、同じ
エンタープライズ構造・GitHub ワークフロー・品質ゲート・AI エージェント契約を備えたリポジトリを
打ち出します。ほかのフェーズ（`design`・`plan`・`audit`・`refactor`）はその統治をデリバリー・
ライフサイクル全体へ広げます。各フェーズは、永続的でゲート検査される manifest に対するオプトインの
`/eados <phase>` コマンドです（設計は [RFC-0001](../../../../.eados-core/docs/rfc/0001-eados-delivery-os.md)）。

> **はじめての方へ。** [`USAGE.md`](../../../../.eados-core/docs/USAGE.md) は EADOS に何ができるかの
> 全体地図、[フェーズ別ウォークスルー](../../walkthrough.md)は実際に動くところを見せます。とにかく
> インストールしたい方は[はじめかた](#はじめかた)へ。

## 目次

- [なぜ EADOS か](#なぜ-eados-か) · [機能ひとめ](#機能ひとめ)
- [得られるもの](#得られるもの) · [フェーズパイプライン](#フェーズパイプライン) · [生成のしくみ](#生成のしくみ)
- [リポジトリ構成](#リポジトリ構成) · [はじめかた](#はじめかた) · [Quickstart](#quickstart)
- [設計原則](#設計原則なぜこの形なのか) · [セキュリティ態勢](#セキュリティ態勢) · [FAQ](#faq)
- [コントリビューションとガバナンス](#コントリビューションとガバナンス) · [来歴](#来歴) · [ライセンスと所有](#ライセンスと所有)

## なぜ EADOS か

EADOS は一つの問いに答えます：

> *「どの言語でも —— Rust / Python / TypeScript / Go / Java / …… —— **すべての**プロジェクトで
> **同じ**エンタープライズの厳密さ（エージェント、ADR、CI 行列、consistency lint、SemVer
> ガバナンス）をどう得るのか？」*

**Enterprise Project Architect** エージェントを EADOS に向け、インテイク・インタビューを実行すれば
新しいリポジトリが生成されます —— あるいは manifest を手で埋めて決定的にレンダリングすれば、
エージェントは不要です。

**なぜ cookiecutter / copier / Yeoman ではないのか？** それらはリポジトリを*一度*足場作りして
立ち去ります。EADOS は一回限りのテンプレートではなく、**デリバリー・オペレーティング・システム**
です：

1. **データによる言語非依存** —— ツールチェーン知識は profile に置かれ、template にハードコード
   されません。だから一つのファクトリが 19+ 言語に対応します（新言語の追加はコードではなくデータ）。
2. **生成されたリポジトリは自己統治する** —— 自前のエージェント契約・CI・品質ゲート・SemVer
   フローを備え、自給自足です（ランタイムで EADOS に逆結合しません）。
3. **生成はそのうちの一フェーズに過ぎない** —— `design → plan → audit → refactor` が、役割権限と
   トレーサビリティ・グラフを持つ永続的でゲート検査される manifest 上で、統治をライフサイクル全体へ
   広げます。

**決定的で人間がゲートします**：エージェントが起草し、人間がレビューしてマージします。未解決の
placeholder は推測ではなくハードエラーです。

## 機能ひとめ

- **任意の言語**でエンタープライズ級リポジトリを**生成** —— 19 profile 同梱、新言語はデータ一つで追加。
- **ライフサイクル全体を統治** —— 六つのオプトイン・フェーズ（`init · design · plan · scaffold ·
  audit · refactor`）を持続 manifest 上で、各遷移にゲート付き。
- **合成可能なエージェント役割**、**ペルソナ ≠ 権限**の分離 —— アーキテクト、reviewer、
  security-auditor、release-manager、product-manager、tech-lead、producer、contribution-reviewer。
- **品質・安全ゲート** —— placeholder / profile / 仕様の完全性、生成される `consistency_lint`、
  リスクスコアリング、トレーサビリティ・グラフ（RFC → マイルストーン → PR → commit → release）。
- **入力コントリビューション・レビュー**（`/eados review`） —— 非 owner の PR を信頼ティア・ポリシー・
  リスクで分類し、処置を推奨（自動マージはしません）。
- **ガイド付きインストーラー** —— クロスプラットフォームの `setup.{sh,command,ps1,bat}`、
  **失敗時拒否の SHA256** 検証と追加方式・上書きなしの展開付き。
- **自己改善、バージョン管理され人間がゲート** —— 教訓台帳、オートチューナー、セルフレビュー。
- **オプトイン**の i18n（翻訳文書 + 新鮮度ゲート）、SNS アナウンス、ベンチマーク。
- **エージェント不要 / オフライン経路** —— 標準ライブラリ Python；manifest から決定的にレンダリング。

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

これらはいずれもエンタープライズ水準で作られた**パラメータ化された成果物**です。
汎用性は三つの場所に宿ります：

1. **言語 profile**（`orchestrator/profiles/*.yaml`）は、言語ごとのツールチェーン知識を
   データとして符号化します（build ツール、テストフレームワーク、formatter、linter、
   sanitizer、CI 行列、ソースファイル拡張子、名前空間スタイル、バージョン定数の位置）。
2. **プロジェクト manifest**（`orchestrator/project.yaml`）は維持者の回答を取り込みます ——
   すべての placeholder にとっての唯一の真実の源です。
3. **template**（`templates/**`）は、プロジェクト固有の事実を `{{PLACEHOLDERS}}` に
   置き換えたエンタープライズの成果物そのものです。

---

## フェーズパイプライン

一回限りの生成にとどまらず、EADOS は六つの**オプトイン**フェーズでプロジェクトを統治します ——
各フェーズは持続 manifest に対する `/eados <phase>` コマンドで、すべての遷移に決定的ゲートが
あります（人間ゲートの遷移は人間が確認）。欲しいフェーズだけ採用できます：生成だけが欲しいなら
`/eados scaffold` を実行し、残りは無視すればよいだけです。

| フェーズ | 役割 | 主な成果物 / ゲート |
|---|---|---|
| **`init`** | プロジェクトを枠組みし、初期 manifest（`delivery_state`）を書く。 | manifest スケルトン |
| **`design`** | レビュー手順のもとで RFC を執筆 / 取り込み。 | `rfc-approved` |
| **`plan`** | RFC からロードマップを共創し、トレーサビリティ・グラフを構築。 | `roadmap-covers-rfcs` |
| **`scaffold`** | 統治されたリポジトリを**生成** —— 従来のファクトリ。 | render + `consistency_lint` |
| **`audit`** | 継続的リスクスコアリング + 強制トレーサビリティ lint。 | `traceability-lint`、リスク閾値 |
| **`refactor`** | 既存リポジトリを、ゲート付き・サンドボックス化・**追加方式**の PR で標準へ。 | 書き込み制限サンドボックス |

詳細は [`USAGE.md`](../../../../.eados-core/docs/USAGE.md) と
[コマンド・プレイブック](../../../../.eados-core/orchestrator/commands/README.md) に。横断的な二つの
コマンドはどのフェーズでも使えます：[`/eados status`](../../../../.eados-core/orchestrator/commands/status.md)
（読み取り専用ドクター）と [`/eados review`](../../../../.eados-core/orchestrator/commands/review.md)
（入力 PR の分流）。

---

## 生成のしくみ

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
[`orchestrator/generate.md`](../../../../.eados-core/orchestrator/generate.md)。

---

## リポジトリ構成

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

## はじめかた

### 必要要件

EADOS は markdown/YAML のファクトリです —— コンパイルするものは何もなく、インストールも
ほとんど不要です。何が必要かは駆動方法によります：

- **会話的に使う（推奨）** —— `AGENTS.md` を読む **AI コーディングエージェント**：Claude Code、
  Gemini Antigravity、または ChatGPT Codex。
- **決定的に使う（エージェント不要）** —— 同梱ツール（`render.py`、`eados_lint.py`、および生成される
  `consistency_lint.py`）のための **Python 3.12+** のみ。標準ライブラリだけで `pip install` は不要です。
- **EADOS に貢献する** —— クローンして pull request を開くための **git**。ファクトリをダウンロード
  して使うだけなら git は**不要**です。

### 前提条件 —— AI コーディングエージェントの入手

推奨される（会話的）パスには、`AGENTS.md` を読む **AI コーディングエージェント**が必要です。いずれかを導入してください：

- **Claude Code** —— [インストールとセットアップ](https://docs.anthropic.com/en/docs/claude-code)
- **Gemini Antigravity** —— [antigravity.google](https://antigravity.google/)
- **ChatGPT Codex** —— [Codex CLI](https://developers.openai.com/codex/cli)

「**エージェントでフォルダを開く**」とは、プロジェクトのリポジトリ直下でエージェントを起動することです——
エージェントは `AGENTS.md` を自動的に読み込み、Enterprise Project Architect（エンタープライズ・プロジェクト・
アーキテクト）ペルソナを採用して、インタビューの準備が整います。

**どのモデル？** EADOS はエージェントの推論に依存するため、強力なモデルほど良い結果になります。現時点では
**Claude Opus 4.8（high）** が最も良く —— **Fable 5** はまだ利用できません —— 次いで **OpenAI Codex 5.5**
と **Gemini 3.5 Flash**；**Mistral AI** と **Sakana AI** は未検証です。

> **⚠ AI エージェントはハルシネーションを起こし得ます。** 自信ありげに、しかし時に誤って草案を作ります
> —— 行動に移す前に、**すべての diff・RFC・コマンドをレビュー**してください。EADOS は初心者の敷居を
> 下げますが、**強力なツール**です：経験者の手で最も効果を発揮します —— あなたが工学的判断を、
> エージェントが速度をもたらします。不可逆な手順はすべて人間が所有します（open / merge / publish）。

**エージェントがない？ それでも止まりません** —— **決定的パス**を使います：`project.yaml` を埋めて
`render.py` を実行してください（Python 3.12+ のみ、標準ライブラリだけ）。[Quickstart](#quickstart) と
[`USAGE.md`](../../USAGE.md) §3 を参照。

### 入手

**ガイド付きインストーラー（ワンステップ）—— 推奨。** 最新リリースからお使いの OS 向けインストーラーを
取得して実行します：インストール先（新規か既存のリポジトリ、パス）を尋ね、**バンドルの SHA256 を検証**
（失敗時は拒否）し、**追加方式**で展開します（既存ファイルを決して上書きしません）。全オプション
（macOS のダブルクリック、スクリプト用フラグ、オフライン検証）は
[`USAGE.md`](../../USAGE.md) §6 にあります。

```bash
# Linux / macOS —— ダウンロードしてから実行（対話プロンプトあり）
curl -fsSL https://github.com/danielPoloWork/pgs-eados/releases/latest/download/setup.sh -o setup.sh && sh setup.sh
```

```powershell
# Windows (PowerShell) —— またはリリースの setup.bat をダブルクリック
Invoke-WebRequest https://github.com/danielPoloWork/pgs-eados/releases/latest/download/setup.ps1 -OutFile setup.ps1; powershell -ExecutionPolicy Bypass -File setup.ps1
```

**または手動でバンドルをダウンロード** —— クローン不要で、何が実行されるかを正確に確認できます。バンドルは
ファクトリの自己完結・**プレフィックスなし**のコピー（CI・changelog・git 履歴なし）です。
**あなたのプロジェクトのリポジトリのルート**で展開すると、その中身 —— `.eados-core/` とエージェント
契約および `LICENSE` —— がサブフォルダ**ではなく**ルートに直接展開されます：

```bash
cd my-project        # あなたのプロジェクトのリポジトリのルート（新規または既存）
curl -L -o /tmp/pgs-eados-bundle.tar.gz \
  https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz
tar xzf /tmp/pgs-eados-bundle.tar.gz   # .eados-core/、AGENTS.md … をカレントフォルダへ展開
```

**Windows（PowerShell）** では —— `tar` は Windows 10+ に同梱されています：

```powershell
cd my-project
Invoke-WebRequest -Uri https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz -OutFile $env:TEMP/pgs-eados-bundle.tar.gz
tar -xzf $env:TEMP/pgs-eados-bundle.tar.gz   # .eados-core/、AGENTS.md … をカレントフォルダへ展開
```

これで `my-project/.eados-core/`（`AGENTS.md` の隣）ができているはずです。ZIP やブラウザがよいですか？
[最新リリース](https://github.com/danielPoloWork/pgs-eados/releases/latest)からいずれかのアセットを
ダウンロードし、**リポジトリのルート**で展開してください（中身は最上位 —— 外側のフォルダなし）。
その後、[Quickstart](#quickstart) のように確認して生成します：

```bash
ls .eados-core                           # orchestrator/ templates/ tools/ …
python .eados-core/tools/eados_lint.py    # 任意：ファクトリが内部的に整合しているか確認
```

**リポジトリをクローン —— EADOS に貢献する場合**（CI・changelog・履歴を含む完全なリポジトリ）：

```bash
git clone https://github.com/danielPoloWork/pgs-eados.git && cd pgs-eados
```

## Quickstart

EADOS は Enterprise Project Architect エージェントを通じて会話的に駆動します。

1. **プロジェクトフォルダを AI コーディングエージェントで開く**（Claude Code、Gemini、Codex）。
   エージェントは `AGENTS.md` を読み、メタアーキテクトのペルソナを採用します。
2. **作りたいものを伝える。** 例：*「新規プロジェクト：Rust のトークンバケット・レート
   リミッタ、library、GitHub owner `acme`、デフォルトブランチ `main`。」*
3. **インタビューに答える。** アーキテクトは
   [`orchestrator/interview.md`](../../../../.eados-core/orchestrator/interview.md) を辿り —— 言語、
   フレームワーク、ツール、ガバナンス、機能仕様 —— 安全に既定値を採れない問いだけを尋ねます。
4. **manifest を確認する。** アーキテクトは `orchestrator/project.yaml` を書き、何かを生成する
   前にあなたへ確認のため提示します。
5. **生成する。** アーキテクトは
   [`orchestrator/generate.md`](../../../../.eados-core/orchestrator/generate.md) に従って新リポジトリ
   をレンダリングし、consistency lint を実行し、ブートストラップ PR を起草します。

エンタープライズ規則を覚えておく必要はありません —— それらは template に符号化され lint で
強制されます。あなたはプロジェクト固有の決定だけを行います。

### あるいは自分でレンダリングする（決定的、エージェント不要）

インタビューの唯一の出力は埋められた manifest なので、手で埋めてエージェントなしで
レンダリングすることもできます：

```bash
cp .eados-core/orchestrator/project.yaml.template .eados-core/orchestrator/project.yaml
# edit .eados-core/orchestrator/project.yaml — see .eados-core/orchestrator/examples/reference.yaml for a worked one
python .eados-core/tools/render.py .eados-core/orchestrator/project.yaml --in-place
python tools/consistency_lint.py     # the generated repo's own gate (now at the repo root)
```

`render.py` は
[`orchestrator/placeholders.md`](../../../../.eados-core/orchestrator/placeholders.md) の置換を
厳密に実行し、`capabilities.*` ゲートを尊重し、GitHub Actions の `${{ … }}` はそのまま残し、
**未解決の placeholder があれば中断**します。EADOS 自身の CI の render-smoke ジョブは、毎プッシュ
時にこれを
[`orchestrator/examples/reference.yaml`](../../../../.eados-core/orchestrator/examples/reference.yaml)
に対して実行します。

### ツール

| ツール | 役割 |
|---|---|
| [`tools/render.py`](../../../../.eados-core/tools/render.py) | manifest をリポジトリへレンダリング（決定的）。 |
| [`tools/eados_lint.py`](../../../../.eados-core/tools/eados_lint.py) | 自己 lint：placeholder の整合性、profile の完全性、プレイブック参照。 |
| `templates/tools/consistency_lint.py` | 各生成リポジトリへ同梱され、その成果物間の整合性を強制。 |

---

## 設計原則（なぜこの形なのか）

- **事実ごとに真実の源は一つ。** プロジェクトの事実（名前、言語、owner、名前空間）は
  `project.yaml` に一度だけ記録され、placeholder を介してすべての成果物へ流れます。これは
  生成される `consistency_lint.py` が強制するのと同じ反ドリフトの規律です。
- **あらゆる言語に開かれている。** EADOS は固定リストに縛られません —— 同梱の十九個の profile
  （C、C++、C#、VB.NET、Java、Kotlin、Scala、Python、Ruby、PHP、JavaScript、TypeScript、Go、
  Rust、Swift、Dart、Lua、COBOL、Pascal）は**種**です。新しい言語の対応とは
  [`profiles/_template.yaml`](../../../../.eados-core/orchestrator/profiles/_template.yaml) を一つの
  `profiles/<lang>.yaml` にコピーすることであり、template を編集することは決してありません。
  template は*役割*（build ツール、テストランナー、formatter）だけを知り、具体的なツールは
  知りません。「非対応の言語」は存在せず、あるのは「まだ profile 化していない」だけです。
- **生成されたリポジトリは自己統治する。** EADOS の職務は生成で終わります。新リポジトリは
  自前の `AGENTS.md`、CI、lint を備えるため自給自足で、EADOS へ逆結合し*ません*。
- **ディスク上は英語、チャットでは任意の言語。** 生成される成果物はすべて英語です。インタビュー
  自体は維持者の言語で行えます。
- **不可逆な手順は人間が所有する。** エージェントはブランチ・コミット・PR を起草し、人間が
  開き、レビューし、マージします。EADOS はこの境界を逐語的に再現します。

---

## セキュリティ態勢

EADOS はサプライチェーンとエージェント境界を第一級として扱います：

- **失敗時拒否のインストーラー完全性。** ガイド付きインストーラーは展開前にリリースの `SHA256SUMS`
  で bundle の **SHA256** を検証し、未検証の bundle を拒否します（盲目的な `curl | sh` はなし）。
  展開は**追加方式**で、既存ファイルを決して上書きしません。
- **書き込み制限の生成。** レンダラーと `refactor` サンドボックスは、ターゲットの外へ逃げる書き込み
  —— パストラバーサル / 絶対パス / シンボリックリンク / `.git` / 上書き —— を拒否します
  （[ADR-0007](../../../../.eados-core/docs/adr/0007-renderer-write-guards-and-validation-independence.md)
  の原則）。
- **信頼できない入力コード。** `/eados review` は非 owner の PR を信頼ティアで分類し、汚染パイプライン
  の露出面（ワークフロー変更、新規依存、シークレットへの到達）を指摘します。非 owner のコミットは
  **決してマージされません** —— 良いアイデアはクレジット付きで自前で再実装されます。
- **固定され監査可能な CI。** GitHub Actions は SHA 固定（Dependabot + 自動同期ゲートが固定値を
  正直に保つ）。セルフ lint ゲートは**オフライン**で動きます（ゲート経路にネットワークなし）。
- **不可逆な手順はすべて人間が所有** —— エージェントが起草し、人間が開き、マージし、公開します。
- **監査可能な系譜。** トレーサビリティ・グラフが各リリースを PR → commit → マイルストーン → RFC へ
  さかのぼって結びつけます。ぶら下がったエッジは lint を失敗させます。

## FAQ

**これは cookiecutter / プロジェクトテンプレートですか？** いいえ —— [なぜ EADOS か](#なぜ-eados-か)
を参照。生成は統治されたデリバリー OS の一フェーズに過ぎず、成果物は自前の統治を備えます。

**AI エージェントは必要ですか？** いいえ。会話的経路を推奨しますが、**決定的経路**（`project.yaml`
を埋めて `render.py` を実行）は標準ライブラリ Python 3.12+ だけで足ります。

**対応言語は？** 任意です。今日 19 profile を同梱。新言語はデータファイル（`profiles/<lang>.yaml`）
であり、template を編集することはありません。

**生成されたリポジトリはランタイムで EADOS に依存しますか？** いいえ —— 自給自足で、自前の
`AGENTS.md`・CI・lint が付随します。EADOS の職務は生成で終わります。

**オフライン / エアギャップで使えますか？** はい。インストーラーは `--from` + `--sums-file`
（手動ダウンロードした bundle を検証）に対応し、決定的レンダリングとゲートはネットワーク不要です。

**どのモデルが最適ですか？** [前提条件](#前提条件--ai-コーディングエージェントの入手)を参照 ——
現状 **Claude Opus 4.8（high）** が最良で、次いで Codex 5.5 と Gemini 3.5 Flash。

**EADOS は私のコードやデータをどこかに送りますか？** いいえ —— markdown / YAML / 標準ライブラリ
Python で、テレメトリはありません。AI エージェントは別個のツールで、独自のデータ方針を持ちます。

---

## コントリビューションとガバナンス

EADOS は **owner ガバナンス**です：コントリビューターは pull request で*提案*し、owner
（`@danielPoloWork`）が*決定*し **squash-merge** します。誰も `main` へ直接 push しません。

- まず [`CONTRIBUTING.md`](../../../../CONTRIBUTING.md) から：fork → フィーチャーブランチ →
  Conventional Commits → ゲート実行（`eados_lint`、render-smoke、`tools/tests/`）→ PR を開く。
- `main` は **squash** マージ方式のみを受け付けます。完全なブランチ保護 ruleset（PR 必須、
  push できる者の制限）はリポジトリ公開後に有効になります。
- セキュリティ問題は公開 issue に書きません —— [`SECURITY.md`](../../../../SECURITY.md) を参照。
  質問やアイデアは GitHub Discussions へ。リリースは SemVer に従い
  [`CHANGELOG.md`](../../../../CHANGELOG.md) に記録されます。完全な契約は
  [`AGENTS.md`](../../../../AGENTS.md) です。

---

## 来歴

EADOS のすべての規則・template・ゲートは意図的なものです：設計は
[RFC-0001](../../../../.eados-core/docs/rfc/0001-eados-delivery-os.md) で批准され、各重要な決定は
[`docs/adr/`](../../../../.eados-core/docs/adr/) に記録されています。

## ライセンスと所有

EADOS は **[MIT ライセンス](../../../../LICENSE)** の下で公開されています —— © 2026 **Daniel Polo**。
**Daniel Polo**（`@danielPoloWork`）が保守し **owner ガバナンス**で運営します：コントリビューターは
pull request で*提案*し、owner が*決定*して squash-merge します
（[コントリビューションとガバナンス](#コントリビューションとガバナンス)を参照）。ファクトリと共に同梱される
`LICENSE` は意図的なものです —— `render.py` が各生成プロジェクトのライセンスの源として読み取るため、
EADOS が生み出す各リポジトリはそれぞれの owner に帰属し MIT ライセンスとなります。
