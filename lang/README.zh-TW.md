# LLM Wiki — 多模態知識圖譜技能

> *"LLM 負責撰寫和維護 wiki；人負責閱讀和提問。"*

![LLM Wiki 架構圖](../skills/llm-wiki/assets/llm-wiki.svg)

**其他語言：** [English](../README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Русский](README.ru.md) | [Español](README.es.md)

---

## 這是什麼

`llm-wiki` 是一個運行在 Claude Code 中的 Skill，將任意格式的原始文件（PDF、DOCX、PPTX、XLSX、Markdown、圖片）攝入到結構化 Wiki，並自動建構可互動的知識圖譜（`graph.html`）。

它實現 Karpathy 提出的知識管理理念：**知識在攝入時合成，而非查詢時合成**。每次新文件加入時，LLM 自動提取要點、建立交叉引用、標記矛盾、更新綜合摘要，使知識庫隨每次攝入複利增長。

這與 RAG 的核心區別在於：RAG 把原始文件丟進向量庫，查詢時臨時組裝答案；llm-wiki 在攝入時就把知識編譯為耐久的 wiki 頁面，查詢時讀取已綜合好的結論。

---

## 目錄結構

```
<wiki-root>/
├── SCHEMA.md                    # 題域定義 + 標籤分類法 + 約定
├── index.md                     # 分區內容目錄
├── overview.md                  # 跨來源動態合成摘要
├── log.md                       # 按時間追加型操作日誌
│
├── raw/                         # 不可變原始來源
│   ├── articles/
│   ├── papers/
│   ├── transcripts/
│   ├── assets/
│   └── inbox/
│
├── sources/                     # 每個原始文件的摘要頁
├── entities/                    # 實體頁
├── concepts/                    # 概念頁
├── comparisons/                 # 對比分析頁
├── queries/                     # 查詢結果歸檔
├── archive/
│
└── graph/
    ├── graph.json
    └── graph.html
```

---

## 指令速查

| 指令 | 用途 |
|---|---|
| `wiki-config workspace <path>` | 設定 wiki 工作空間路徑 |
| `wiki-config show` | 查看目前設定及目錄狀態 |
| `wiki-input <path> [--topic <slug>]` | 攝入任意路徑文件（自動歸檔到 `raw/<topic>/`） |
| `wiki-ingest <file>` | 攝入已在 `raw/` 中的文件 |
| `wiki-query: <問題>` | 查詢知識庫，綜合答案 |
| `wiki-lint` | 檢查孤立頁面、斷鏈、矛盾等品質問題 |
| `wiki-graph` | 建構可視化知識圖譜（`graph.html`） |

**日常使用推薦 `wiki-input`**：接受本地或遠端路徑，自動複製到 `raw/<topic>/` 歸檔後再攝入，無需手動管理 `raw/` 目錄。

---

## 工作流程說明

### 攝入（Ingest）

攝入一份文件時，LLM 會依序執行：

1. 多模態內容提取（PDF/DOCX/PPTX/XLSX/圖片 → Markdown）
2. 寫入 `sources/<slug>.md`（摘要、要點、關鍵引用）
3. 更新 `index.md` 和 `overview.md`
4. 建立或更新 `entities/` 和 `concepts/` 頁面
5. 標記與已有內容的矛盾
6. 追加操作日誌到 `log.md`

### 查詢（Query）

讀取 `index.md` 識別相關頁面，綜合答案並以 `[[PageName]]` 格式內聯引用。可選將答案存為 `queries/<slug>.md` 歸檔備查。

### 知識圖譜（Graph）

提取頁面間的顯式 wikilink（`EXTRACTED`）和 AI 推斷的語義關聯（`INFERRED`，信賴度 ≥ 0.5），生成零依賴的自包含 `graph.html`，支援節點類型著色和社群分組。

---

## 支援格式

| 格式 | 提取方式 |
|---|---|
| `.md` `.txt` | 直接讀取 |
| `.pdf` | pdfplumber（文字 + 表格） |
| `.docx` | python-docx（正文 + 標題 + 表格） |
| `.pptx` | python-pptx（標題 + 正文 + 備註） |
| `.xlsx` `.csv` | pandas（轉 Markdown 表格） |
| `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` | Claude vision（多模態） |

---

## 多模態支援詳解

`llm-wiki` 使用 Claude 原生多模態能力理解圖像內容——不僅是 OCR 文字辨識，而是對圖表、流程圖、截圖的完整語義理解。

### 直接攝入圖片檔案

將圖片檔案直接傳給 `wiki-input` 或 `wiki-ingest`，Claude 讀取圖片並轉換為結構化 Markdown，再進入標準 Ingest 流程：

```bash
wiki-input ~/截圖/架構圖.png --topic system-design
wiki-input ~/照片/白板會議.jpg --topic meetings
```

**Claude 從圖片中提取的內容：**
- **圖表與折線圖** — 資料序列、座標軸標籤、趨勢、數值
- **架構圖與流程圖** — 節點、連線、關係、流向
- **截圖** — UI 結構、可見文字、版面配置上下文
- **手寫筆記 / 白板** — 轉錄文字和繪製的結構
- **圖片中的表格** — 重建為 Markdown 表格
- **混合內容** — 拍照或掃描的含文字和圖形的文件

### 文件內嵌圖片

攝入包含嵌入圖片的 PDF、DOCX 或 PPTX 時，提取工具會取得所有文字內容。若文件中的圖表對理解至關重要，而純文字提取不足以涵蓋，可將這些圖表另存為圖片檔案單獨攝入。

### 支援的圖片格式

| 格式 | 說明 |
|---|---|
| `.png` | 無損壓縮，適合截圖、架構圖 |
| `.jpg` / `.jpeg` | 照片、掃描文件 |
| `.webp` | 網路最佳化圖片 |
| `.gif` | 分析第一幀（靜態內容） |
| `.bmp` | 未壓縮點陣圖 |

### 多模態提取流程

所有圖片內容經過與文字文件相同的 Ingest 流程——圖片僅在進入流程前先轉換為 Markdown：

```
圖片檔案
    │
    ▼
Claude Vision（Read 工具）
    │  提取：文字、結構、資料、關係
    ▼
Markdown 描述
    │
    ▼
標準 Ingest 流程（步驟 2–10）
    │  sources/ entities/ concepts/ index/ overview/ log/
    ▼
Wiki 頁面 + 知識圖譜
```

---

## 快速開始

```bash
# 1. 設定 wiki 工作空間
wiki-config workspace ~/my-wiki

# 2. 攝入第一份文件
wiki-input ~/Downloads/paper.pdf --topic papers

# 3. 查詢
wiki-query: 這篇論文的核心貢獻是什麼？

# 4. 建構知識圖譜
wiki-graph
```

---

## 參考資料

- [Anthropic Skills — 官方技能倉庫](https://github.com/anthropics/skills)
- [Andrej Karpathy — LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [SamurAIGPT — llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent)
