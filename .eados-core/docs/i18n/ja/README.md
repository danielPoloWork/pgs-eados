# エンタープライズ・エージェント型デリバリー・オペレーティング・システム（EADOS）

[![CI](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml/badge.svg)](https://github.com/danielPoloWork/pgs-eados/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.2.1-blue.svg)](https://github.com/danielPoloWork/pgs-eados/releases)
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
> template から、*あらゆる*言語向けに `pbr-cpp-memory-pool` の**エンタープライズ・エージェント
> 型システム**を再現します。

EADOS は出荷する製品ではなく、**仕事の流れ方そのものを司るオペレーティング・システム**です
—— 宣言的で、ゲートで強制され、人間が確認する統治層（ランタイムのカーネルではありません）。
その **`scaffold` フェーズがファクトリ**であり、言語・フレームワーク・ツールを問わず、同じ
エンタープライズ構造・GitHub ワークフロー・品質ゲート・AI エージェント契約を備えたリポジトリを
打ち出します。ほかのフェーズ（`design`・`plan`・`audit`・`refactor`）は、その統治を
デリバリー・ライフサイクル全体へ広げます。

> **パイプライン。** 各フェーズは、永続的でゲート検査される manifest に対するオプトインの
> `/eados <phase>` コマンドです。設計は [RFC-0001](../../../../.eados-core/docs/rfc/0001-eados-delivery-os.md)、
> 各フェーズは [`orchestrator/commands/`](../../../../.eados-core/orchestrator/commands/README.md) にあります。
> 生成のみ（従来のファクトリ）は今も `/eados scaffold` のままで、何も変わっていません。

EADOS はある一つの問いに答えるために存在します：

> *「`pbr-cpp-memory-pool` をエンタープライズ水準で作り上げた —— エージェント、ADR、CI 行列、
> consistency lint、SemVer ガバナンス。では、次のプロジェクト（Rust / Python / TypeScript /
> Go / Java / ……）で**同じ**厳密さをどう得るのか？」*

その答え：**Enterprise Project Architect** エージェントを EADOS に向け、**インテイク・
インタビュー**を実行し、新しいリポジトリを生成させること。

> **はじめての方へ。** [`.eados-core/docs/USAGE.md`](../../../../.eados-core/docs/USAGE.md) を
> お読みください —— EADOS に何ができるか、どう動くか、何が固定で何をカスタマイズできるかの
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
    │   ├── examples/reference.yaml    # a worked manifest (pbr-cpp-memory-pool) + render-smoke fixture
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

### 入手

**バンドルをあなたのプロジェクトのリポジトリにダウンロード —— 推奨、クローン不要。** バンドルは
ファクトリの自己完結・**プレフィックスなし**のコピー（CI・changelog・git 履歴なし）です。
**あなたのプロジェクトのリポジトリのルート**で展開すると、その中身 —— `.eados-core/` とエージェント
契約および `LICENSE` —— がサブフォルダ**ではなく**ルートに直接展開されます：

```bash
cd my-project        # あなたのプロジェクトのリポジトリのルート（新規または既存）
curl -L -o /tmp/pgs-eados-bundle.tar.gz \
  https://github.com/danielPoloWork/pgs-eados/releases/latest/download/pgs-eados-bundle.tar.gz
tar xzf /tmp/pgs-eados-bundle.tar.gz   # .eados-core/、AGENTS.md … をカレントフォルダへ展開
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
- **ディスク上は英語、チャットでは任意の言語。** 参照プロジェクトと同様、生成される成果物は
  すべて英語です。インタビュー自体は維持者の言語で行えます。
- **不可逆な手順は人間が所有する。** エージェントはブランチ・コミット・PR を起草し、人間が
  開き、レビューし、マージします。EADOS はこの境界を逐語的に再現します。

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

EADOS は `pbr-cpp-memory-pool` からリバースエンジニアリングされています —— ここにあるすべての
規則・template・ゲートは、そのプロジェクトの `AGENTS.md`、`docs/`、`.github/`、
`tools/consistency_lint.py` に具体的な出自を持ちます。この一般化を形づくった決定については
[`docs/adr/`](../../../../.eados-core/docs/adr/) を参照してください。
