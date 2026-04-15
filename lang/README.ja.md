# LLM Wiki — マルチモーダル知識グラフスキル

> *「LLM が wiki を書いて維持する。人間は読んで質問する。」*

![LLM Wiki アーキテクチャ](../skills/llm-wiki/assets/llm-wiki.svg)

**他の言語：** [English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Español](README.es.md)

---

## これは何か

`llm-wiki` は Claude Code 上で動作する Skill で、任意フォーマットの生ドキュメント（PDF、DOCX、PPTX、XLSX、Markdown、画像）を構造化 Wiki に取り込み、インタラクティブな知識グラフ（`graph.html`）を自動生成します。

Karpathy が提唱した知識管理哲学を実装しています：**知識は取り込み時に合成する、クエリ時ではなく**。新しいドキュメントが追加されるたびに、LLM が自動的に要点を抽出し、相互参照を構築し、矛盾を特定し、統合サマリーを更新します。これにより、知識ベースは取り込みのたびに複利的に成長します。

RAG との根本的な違い：RAG は生ドキュメントをベクターストアに投入してクエリ時に一時的に回答を組み立てますが、llm-wiki は取り込み時に知識を耐久性のある wiki ページにコンパイルし、クエリ時には既に合成された結論を読み取ります。

---

## ディレクトリ構成

```
<wiki-root>/
  raw/                  # 生ドキュメント（絶対に変更しない）
    <topic>/            # トピック別に整理、1 段階サブディレクトリ
  wiki/
    index.md            # 全ページの目次（トピック別に区分）
    overview.md         # 全ソースを横断する living synthesis
    log.md              # 追記専用の操作ログ
    sources/            # 各生ドキュメントのサマリーページ
    entities/           # 人物 / 企業 / プロジェクト / 製品
    concepts/           # 概念 / フレームワーク / 方法論
    syntheses/          # クエリ回答のアーカイブ
    archive/            # アーカイブされた古いページ
  graph/
    graph.json          # ノード + エッジデータ
    graph.html          # vis.js ベースの自己完結型ビジュアライゼーション
```

---

## コマンドリファレンス

| コマンド | 用途 |
|---|---|
| `wiki-config workspace <path>` | wiki ワークスペースパスを設定 |
| `wiki-config show` | 現在の設定とディレクトリ状態を表示 |
| `wiki-input <path> [--topic <slug>]` | 任意パスのファイルを取り込む（`raw/<topic>/` に自動アーカイブ） |
| `wiki-ingest <file>` | `raw/` に既に存在するファイルを取り込む |
| `wiki-query: <質問>` | 知識ベースを照会して回答を合成 |
| `wiki-lint` | 孤立ページ、壊れたリンク、矛盾などの品質問題を確認 |
| `wiki-graph` | インタラクティブ知識グラフを構築（`graph.html`） |

**日常使用には `wiki-input` を推奨**：ローカルまたはリモートパスを受け付け、取り込み前に自動的に `raw/<topic>/` にコピーします。`raw/` ディレクトリの手動管理不要。

---

## ワークフロー

### 取り込み（Ingest）

ドキュメントを取り込む際、LLM は以下を順番に実行します：

1. マルチモーダルコンテンツ抽出（PDF/DOCX/PPTX/XLSX/画像 → Markdown）
2. `wiki/sources/<slug>.md` の書き込み（サマリー、要点、重要引用）
3. `wiki/index.md` と `wiki/overview.md` の更新
4. `wiki/entities/` と `wiki/concepts/` ページの作成または更新
5. 既存コンテンツとの矛盾のフラグ設定
6. `wiki/log.md` への操作ログの追記

### クエリ（Query）

`wiki/index.md` を読み取って関連ページを特定し、`[[PageName]]` 形式のインライン参照で回答を合成します。オプションで回答を `wiki/syntheses/<slug>.md` としてアーカイブできます。

### 知識グラフ（Graph）

ページ間の明示的な wikilink（`EXTRACTED`）と AI 推論による意味的関連（`INFERRED`、信頼度 ≥ 0.5）を抽出し、ノードタイプ着色とコミュニティグループ化をサポートするゼロ依存の自己完結型 `graph.html` を生成します。

---

## 対応フォーマット

| フォーマット | 抽出方法 |
|---|---|
| `.md` `.txt` | 直接読み取り |
| `.pdf` | pdfplumber（テキスト + テーブル） |
| `.docx` | python-docx（本文 + 見出し + テーブル） |
| `.pptx` | python-pptx（タイトル + 本文 + ノート） |
| `.xlsx` `.csv` | pandas（Markdown テーブルに変換） |
| `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` | Claude vision（マルチモーダル） |

---

## マルチモーダルサポート詳細

`llm-wiki` は Claude のネイティブマルチモーダル機能を使用して画像コンテンツを理解します——単なる OCR テキスト認識ではなく、図表・フローチャート・スクリーンショットの完全な意味理解を行います。

### 画像ファイルの直接取り込み

任意の画像ファイルを `wiki-input` または `wiki-ingest` に渡すだけです。Claude が画像を読み取り、構造化された Markdown に変換してから標準の Ingest ワークフローを実行します：

```bash
wiki-input ~/スクリーンショット/アーキテクチャ図.png --topic system-design
wiki-input ~/写真/ホワイトボードセッション.jpg --topic meetings
```

**Claude が画像から抽出するコンテンツ：**
- **チャート・グラフ** — データ系列、軸ラベル、トレンド、数値
- **アーキテクチャ図・フローチャート** — ノード、エッジ、関係、フロー方向
- **スクリーンショット** — UI 構造、表示テキスト、レイアウトコンテキスト
- **手書きメモ / ホワイトボード** — テキストの文字起こしと描画された構造
- **画像内のテーブル** — Markdown テーブルとして再構築
- **混在コンテンツ** — テキストと図形が含まれた撮影・スキャンドキュメント

### ドキュメント内の埋め込み画像

埋め込み画像を含む PDF、DOCX、PPTX を取り込む際、各抽出ツールはすべてのテキストコンテンツを取得します。理解に重要な図表がある場合で、テキスト抽出だけでは不十分な場合は、それらの図を画像ファイルとして単独で取り込んでください。

### 対応画像フォーマット

| フォーマット | 説明 |
|---|---|
| `.png` | ロスレス；スクリーンショット・図表に最適 |
| `.jpg` / `.jpeg` | 写真、スキャンドキュメント |
| `.webp` | Web 最適化画像 |
| `.gif` | 最初のフレームを分析（静的コンテンツ） |
| `.bmp` | 非圧縮ビットマップ |

### マルチモーダル抽出パイプライン

すべての画像コンテンツはテキストドキュメントと同じ Ingest パイプラインを経由します——画像はパイプラインに入る前に Markdown に変換されるだけです：

```
画像ファイル
    │
    ▼
Claude Vision（Read ツール）
    │  抽出：テキスト、構造、データ、関係
    ▼
Markdown 説明
    │
    ▼
標準 Ingest ワークフロー（ステップ 2–10）
    │  sources/ entities/ concepts/ index/ overview/ log/
    ▼
Wiki ページ + 知識グラフ
```

---

## クイックスタート

```bash
# 1. wiki ワークスペースを設定
wiki-config workspace ~/my-wiki

# 2. 最初のドキュメントを取り込む
wiki-input ~/Downloads/paper.pdf --topic papers

# 3. クエリ
wiki-query: この論文の核心的な貢献は何ですか？

# 4. 知識グラフを構築
wiki-graph
```

---

## 参考

- [Anthropic Skills — 公式スキルリポジトリ](https://github.com/anthropics/skills)
- [Andrej Karpathy — LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [SamurAIGPT — llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent)
