---
name: llm-wiki
description: >
  多模态 Wiki 知识图谱 Skill。支持将 PDF、DOCX、PPTX、XLSX、Markdown、图片等格式摄入为结构化 Wiki，
  并自动构建交互式知识图谱 (graph.html)。融合 Karpathy LLM Wiki 三层架构，支持 SCHEMA 约束、标签分类法、
  质量信号、对比分析页、来源漂移检测等高级功能。
  激活触发词：wiki-ingest、wiki 摄入、build knowledge graph、wiki-graph、wiki-query、
  wiki-lint、wiki 检查、add document to wiki、knowledge base construction、
  wiki-config、wiki configuration、set wiki path、wiki-input、wiki 输入、
  创建 wiki、构建知识库、wiki lint、wiki 健康检查。
triggers:
  - wiki-ingest
  - wiki 摄入
  - wiki-graph
  - 构建知识图谱
  - wiki-query
  - wiki 查询
  - wiki-lint
  - wiki 检查
  - wiki 健康检查
  - 知识库构建
  - 把文档加入 wiki
  - 创建 wiki
  - wiki-config
  - wiki workspace
  - 设置 wiki 路径
  - wiki 配置
  - wiki-input
  - wiki 输入
---

# LLM Wiki — 多模态知识图谱 Skill

## 设计理念

> *"LLM 写入并维护 Wiki；人类阅读和提问。"*

本 Skill 实现了 Karpathy 风格的知识管理系统：原始文档摄入到 `raw/`，LLM 将其编译为持久的结构化 Wiki 页面，并持续交叉引用和更新。与 RAG 的核心区别：**知识在摄入时合成，而非查询时组装**，使知识库随每次摄入产生复利增长。

### 三层架构

```
Layer 3 — SCHEMA.md     定义领域、约定、标签分类法（约束层）
    ↓
Layer 2 — Wiki 页面      Agent 拥有的 entity/concept/comparison/query 页面（知识层）
    ↓
Layer 1 — raw/ 来源     不可变的原始文档（数据层）
```

**分工**：人类策展来源并指导分析方向；Agent 负责总结、交叉引用、归档和维护一致性。

---

## 目录结构

```
<WIKI_ROOT>/
├── SCHEMA.md                    # Layer 3: 领域定义 + 标签分类法 + 约定
├── index.md                     # 分区内容目录，每页一行摘要
├── overview.md                  # 跨来源动态合成摘要（living synthesis）
├── log.md                       # 按时间追加型操作日志（超 500 条自动轮转）
│
├── raw/                         # Layer 1: 不可变原始来源
│   │
│   ├── 固定分类目录（未指定 --topic 时自动判断归档）：
│   ├── articles/                # 网页文章、剪报
│   ├── papers/                  # PDF、arxiv 论文
│   ├── transcripts/             # 会议笔记、访谈记录
│   ├── assets/                  # 图片、图表
│   ├── inbox/                   # 无法判断类型时的默认归档
│   │
│   └── 自定义主题目录（指定 --topic 时使用）：
│   └── <topic>/                 # 用户自定义，新 topic 自动追加到 SCHEMA.md
│
├── sources/                     # Layer 2: 每个原始文档的摘要页
├── entities/                    # Layer 2: 实体页（人物/公司/项目/产品）
├── concepts/                    # Layer 2: 概念页（概念/框架/方法论）
├── comparisons/                 # Layer 2: 对比分析页
├── queries/                     # Layer 2: 有价值的查询结果归档
├── archive/                     # Layer 2: 归档的过期页面
│
└── graph/                       # 知识图谱
    ├── graph.json               # 节点 + 边数据
    └── graph.html               # 基于 vis.js 的独立可视化
```

### raw/ 目录归档规则

| 场景 | 归档位置 | 说明 |
|------|----------|------|
| `--topic xxx` 显式指定 | `raw/<topic>/` | 用户自定义主题，优先级最高 |
| 未指定 `--topic`，Agent 判断为文章 | `raw/articles/` | 网页内容、博客、新闻报道 |
| 未指定 `--topic`，Agent 判断为论文 | `raw/papers/` | PDF、arxiv、学术文献 |
| 未指定 `--topic`，Agent 判断为访谈 | `raw/transcripts/` | 会议记录、对话、访谈 |
| 未指定 `--topic`，Agent 判断为图片 | `raw/assets/` | 截图、图表、照片 |
| 未指定 `--topic`，无法判断类型 | `raw/inbox/` | 默认归档，用户可后续手动移动 |

**新 topic 自动注册**：首次使用新 topic 时，Agent 自动追加到 `SCHEMA.md` 的 `raw_topics` 分类法中。

---

## 会话定向（CRITICAL — 每次会话必做）

当用户已有 Wiki 时，**在执行任何操作之前**必须先定向：

1. **读取 SCHEMA.md** — 理解领域、约定和标签分类法
2. **读取 index.md** — 了解已有页面及其摘要
3. **扫描最近 log.md** — 读取最后 20-30 条记录，了解近期活动

```bash
read SCHEMA.md
read index.md
read log.md（最后 30 行）
```

**定向防止**：
- 为已存在的实体创建重复页面
- 遗漏与现有内容的交叉引用
- 违背 SCHEMA 的约定
- 重复已完成的工作

> 对于大型 Wiki（100+ 页面），在创建新页面之前，先针对主题搜索现有内容。

---

## 页面格式（Frontmatter）

每个 Wiki 页面使用以下 frontmatter（合并了两个插件的字段）：

```yaml
---
title: "页面标题"
type: source | entity | concept | comparison | query | synthesis
created: YYYY-MM-DD              # 创建日期
updated: YYYY-MM-DD              # 最后更新日期
tags: [来自 SCHEMA.md 分类法]
sources: [raw/articles/来源名.md]

# 来源页专用字段：
source_file: raw/<topic>/<文件名>
source_type: pdf | docx | pptx | xlsx | markdown | image
date: YYYY-MM-DD                 # 原始文档日期

# 质量信号（可选但推荐）：
confidence: high | medium | low  # 主张的支撑程度
contested: true                  # 存在未解决的矛盾时设置
contradictions: [其他页面名]      # 与之冲突的页面
---
```

**字段说明**：
- `confidence`：对于观点性强、快速变化或单来源的主张，设为 `medium` 或 `low`。只有跨多来源充分支撑的主张才标 `high`。
- `contested` 和 `contradictions`：当页面与其他页面存在冲突时标记，Lint 时会 surfaced 供用户审查。
- 标签**必须**来自 SCHEMA.md 中定义的分类法，禁止自由标签。

页面之间使用 `[[页面名]]` wikilink 格式互相引用。

**链接路径约定**：
- 同主题链接：直接用文件名 `[[文章名]]`
- 跨主题链接：使用相对路径 `[[../其他主题/文章名]]`

---

## 工作区配置

执行任何 Wiki 命令前，按以下优先级确定 **WIKI_ROOT**：

1. **命令行显式路径** — 命令包含 `@<path>` 参数（如 `wiki-ingest raw/papers/x.pdf @/data/myproject`）
2. **配置文件** — 读取 `.claude/config/llm-wiki.json`，使用 `workspace` 字段（展开 `~` 为绝对路径）
3. **当前工作目录** — 如果都未配置，使用 `cwd`

**WIKI_ROOT 一旦确定，不得以任何理由更改或从命令参数推断覆盖。**

### WIKI_ROOT 目录不存在时

如果确定的 WIKI_ROOT 路径在文件系统中不存在，**直接在该路径创建完整目录结构**，然后继续执行命令：

```
<WIKI_ROOT>/
├── SCHEMA.md                    # 待用户填写领域信息
├── index.md
├── overview.md
├── log.md
├── raw/
│   ├── articles/
│   ├── papers/
│   ├── transcripts/
│   ├── assets/
│   └── inbox/                   # 默认归档目录
├── sources/
├── entities/
├── concepts/
├── comparisons/
├── queries/
├── archive/
└── graph/
```

同时初始化三个基础文件：

**`SCHEMA.md`**（模板）：
```markdown
# Wiki Schema

## Domain
[定义此 Wiki 覆盖的领域 — 如 "AI/ML 研究"、"个人健康"、"创业情报"]

## Conventions
- 文件名：小写，连字符，无空格（如 `transformer-architecture.md`）
- 每个 Wiki 页面必须以 YAML frontmatter 开头
- 使用 `[[wikilinks]]` 链接页面（每页至少 2 个出站链接）
- 更新页面时必须 bump `updated` 日期
- 新页面必须添加到 index.md 的正确分区
- 每个操作必须追加到 log.md
- **来源标记**：综合 3+ 来源的页面，在段落末尾附加 `^[raw/articles/来源文件.md]`

## Frontmatter
（见 SKILL.md 的 Frontmatter 章节）

## 标签分类法
[定义 10-20 个顶级标签。使用前必须先在此处添加。]

## 页面阈值
- 当实体/概念在 2+ 来源中出现或是一个来源的核心时创建页面
- 页面超过 ~200 行时拆分为子主题
- 内容完全被取代时归档到 archive/
```

**`index.md`**：
```markdown
# Wiki Index

> 内容目录。每个 Wiki 页面在其类型下列出，带一行摘要。
> 查询前先读此文件定位相关页面。
> 最后更新：YYYY-MM-DD | 总页数：N

## Entities

## Concepts

## Comparisons

## Queries
```

**`log.md`**：
```markdown
# Wiki Log

> 所有操作的按时间记录。追加型。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`
> 操作类型：ingest, update, query, lint, create, archive, delete
> 当文件超过 500 条时，轮转：重命名为 log-YYYY.md，重新开始。

## [YYYY-MM-DD] create | Wiki 初始化
- 领域：[领域]
- 结构创建，包含 SCHEMA.md、index.md、log.md
```

**配置文件格式**（`.claude/config/llm-wiki.json`）：

```json
{
  "workspace": "/Users/me/projects/my-wiki",
  "description": "可选备注"
}
```

---

## 命令参考

| 用户命令 | 触发流程 | 参考文档 |
|---|---|---|
| `wiki-config workspace <path>` / `设置 wiki 路径` | 配置流程 | [references/wiki-config.md](references/wiki-config.md) |
| `wiki-config show` | 配置流程 | [references/wiki-config.md](references/wiki-config.md) |
| `wiki-config reset` | 配置流程 | [references/wiki-config.md](references/wiki-config.md) |
| `wiki-input <path>` / `wiki 输入 <path>` | 输入流程 | [references/wiki-input.md](references/wiki-input.md) |
| `wiki-ingest <file>` / `把 <file> 加入 wiki` | 摄入流程 | [references/wiki-ingest.md](references/wiki-ingest.md) |
| `wiki-query: <question>` / `wiki 查询：<question>` | 查询流程 | [references/wiki-query.md](references/wiki-query.md) |
| `wiki-lint` / `wiki 检查` | Lint 流程 | [references/wiki-lint.md](references/wiki-lint.md) |
| `wiki-graph` / `构建知识图谱` | 图谱流程 | [references/wiki-graph.md](references/wiki-graph.md) |

> 详见 `references/` 目录中各命令的参数格式、示例和注意事项。
> 页面模板见 [templates/wiki-page-templates.md](templates/wiki-page-templates.md)。

**`wiki-input` vs `wiki-ingest` — 用哪个？**

| | `wiki-input` | `wiki-ingest` |
|---|---|---|
| 文件来源 | 任意本地或远程路径 | 已在 `raw/` 目录中 |
| 归档行为 | 自动复制到 `raw/<topic>/` | 不需要，直接读取 |
| 使用场景 | 日常使用（推荐） | 手动管理 raw/ 的工作流 |

---

## 输入流程（任意路径摄入）

**触发**：`wiki-input <path> [--topic <slug>]` 或 `wiki 输入 <path>`

接受任意本地或远程路径的文件，**先复制到 `raw/<topic>/` 归档，再摄入**。WIKI_ROOT 严格从配置文件解析，与输入文件路径无关。

### 步骤 0 — 确定 WIKI_ROOT

按标准顺序解析（`@<path>` → `.claude/config/llm-wiki.json` → `cwd`），目录不存在则创建。**不要从输入文件路径推断 WIKI_ROOT；配置文件存在时不要回退到 cwd。**

### 步骤 1 — 路径解析与验证

展开路径（`~` → 家目录，Windows `C:/` 直接使用，相对路径基于 cwd 展开），验证文件存在且格式支持。
远程路径（`oss://`、`s3://`、`http(s)://`）先下载到临时目录，摄入完成后删除临时文件（`raw/` 中的归档副本保留）。

### 步骤 1.5 — 确定主题并归档到 raw/

将原始文件复制到 `raw/<topic>/` 作为永久归档，`source_file` 字段记录此归档路径。

**主题确定逻辑（并存模式）**：

| 优先级 | 条件 | 归档目录 |
|--------|------|----------|
| 1 | `--topic <slug>` 显式指定 | `raw/<slug>/` |
| 2 | 未指定，Agent 判断为网页文章 | `raw/articles/` |
| 3 | 未指定，Agent 判断为学术论文 | `raw/papers/` |
| 4 | 未指定，Agent 判断为会议/访谈 | `raw/transcripts/` |
| 5 | 未指定，Agent 判断为图片/图表 | `raw/assets/` |
| 6 | 未指定，无法判断类型 | `raw/inbox/` |

**判断依据**：
- 文件扩展名：`.pdf` → papers，`.png/.jpg` → assets
- 文件名关键词：`arxiv`、`paper`、`会议`、`访谈` 等
- 内容特征：有标题/摘要结构 → papers，有对话格式 → transcripts

**新 topic 自动注册**：
- 首次使用新 topic（`--topic new-topic`）时
- 自动追加到 `SCHEMA.md` 的 `raw_topics` 分类法
- 同时创建 `raw/<new-topic>/` 目录

**主题 slug 规则**：全小写，仅 `a-z`、`0-9`、连字符，最长 32 字符。

如果归档目录不存在则创建。如果同名文件已存在，询问用户是否覆盖。

### 步骤 2 — 触发摄入流程

对 `raw/<topic>/<文件名>` 执行完整摄入流程（去重 → 提取 → Wiki 写入）。`source_file` 字段记录 `raw/<topic>/<文件名>` 路径。

> 完整参数规格和 OSS 支持分析见 [references/wiki-input.md](references/wiki-input.md)。

---

## 摄入流程（多模态摄入）

**触发**：`wiki-ingest <file>` 或 `把 <file> 加入 wiki`

### 步骤 0 — 确定 WIKI_ROOT

按优先级解析工作区路径（命令行 `@<path>` → `.claude/config/llm-wiki.json` → cwd），展开 `~` 为绝对路径。目录不存在则自动创建完整目录结构后继续。后续所有路径均相对于 WIKI_ROOT。

### 步骤 1 — 去重检查

读取 `log.md`，检查此文件是否已有摄入记录（按文件名匹配）。如存在，询问用户是否强制重新摄入。

### 步骤 1.5 — 来源漂移检测（如适用）

如果是对已有 URL 的重新摄入：
1. 计算原始文件内容的 SHA256（frontmatter 之后的部分）
2. 与 `raw/` 中存储的 `sha256` 比较
3. 相同 → 跳过处理，记录"内容无变化"
4. 不同 → 标记来源漂移，继续更新流程

### 步骤 2 — 多模态内容提取

根据文件类型调用对应 skill，将内容转为纯文本：

| 文件类型 | 提取方法 |
|---|---|
| `.md` `.txt` `.json` `.yaml` | 直接 `Read` 工具 |
| `.pdf` | 调用 `pdf` skill — `pdfplumber` 提取文本+表格 |
| `.docx` | 调用 `docx` skill — `python-docx` 提取正文+表格+标题 |
| `.pptx` | 调用 `pptx` skill — 提取每页幻灯片标题+正文+备注 |
| `.xlsx` `.csv` | 调用 `xlsx` skill — 提取工作表内容，转为 Markdown 表格 |
| `.png` `.jpg` `.jpeg` `.webp` | 使用 Claude 视觉直接读取图像内容 |

提取结果统一为 **Markdown 格式纯文本**，保留标题层级和表格结构。

### 步骤 3-12 — 标准 Wiki 写入

内容提取后，按顺序执行以下步骤：

1. **读取** `SCHEMA.md` — 理解领域约定和标签分类法
2. **读取** `index.md` 和 `overview.md` — 获取当前 Wiki 上下文
3. **搜索** 已有页面 — 针对提到的实体/概念搜索现有页面（一次性搜索，非逐个）
4. **写入** `sources/<slug>.md` — 创建来源摘要页
5. **更新** `index.md` — 在对应主题分区追加新条目
6. **更新** `overview.md` — 修订跨来源合成摘要
7. **创建/更新** `entities/` — 为关键人物、公司、项目创建或更新页面
8. **创建/更新** `concepts/` — 为关键概念、框架创建或更新页面
9. **创建/更新** `comparisons/` — 如来源包含多个实体的对比信息，创建或更新对比页
10. **标记矛盾** — 在与现有 Wiki 内容冲突的相关页面的 `## Contradictions` 部分标注
11. **追加日志** `log.md`：`## [YYYY-MM-DD] ingest | <标题>`
12. **输出摘要** — 哪些页面被创建、哪些被更新、发现哪些矛盾

> **批量摄入优化**：当同时摄入多个来源时，先读取所有来源，一次性识别所有实体和概念，一次性搜索现有页面，然后一次性创建/更新所有页面，最后统一更新 index.md 和写入一条批量日志。

### 来源页格式

```markdown
---
title: "来源标题"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/<topic>/<文件名>
source_type: pdf | docx | pptx | xlsx | markdown | image
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## 摘要
2-4 句综合摘要，描述文档核心主张和价值。

## 关键主张
- 要点 1
- 要点 2
- 要点 3

## 关键引用 / 关键数据
> "直接引用内容" — 上下文描述（引用不超过 125 字符）

## 关联
- [[实体名]] — 关联原因
- [[概念名]] — 关联类型

## 矛盾
- 与 [[其他页面]] 在以下方面冲突：...
```

---

## 查询流程

**触发**：`wiki-query: <问题>` 或 `wiki 查询：<问题>`

0. 解析 WIKI_ROOT（命令行 `@<path>` → `.claude/config/llm-wiki.json` → cwd）
1. 如果 Wiki 为空（无 `index.md` 或索引无条目），提示用户先运行 `wiki-ingest`
2. **读取** `index.md` 识别与问题最相关的页面（最多 10 页）
3. 对于 100+ 页面的大型 Wiki，**同时搜索**所有 `.md` 文件中的关键词 — 仅靠 index 可能遗漏相关内容
4. 使用 `Read` 工具读取每个相关页面
5. 综合答案，使用 `[[页面名]]` wikilink 进行行内引用；直接引用不超过 125 字符
6. 在答案末尾附加 `## 来源` 部分，列出所有引用的页面路径
7. 如果答案是实质性的对比、深入分析或新颖综合，**归档到** `queries/` 或 `comparisons/`。不要归档简单查找 — 只归档重新推导会很痛苦的答案。
8. 追加日志：`## [YYYY-MM-DD] query | <问题摘要>`

### 输出格式示例

```markdown
基于 [[RAG]] 和 [[VectorDB]] 的记录，检索增强生成（RAG）是...

## 来源
- concepts/RAG.md
- concepts/VectorDB.md
- sources/paper-rag-survey.md
```

---

## Lint 流程

**触发**：`wiki-lint` 或 `wiki 检查` 或 `wiki 健康检查`

**步骤 0** — 解析 WIKI_ROOT（`.claude/config/llm-wiki.json` → cwd），所有路径基于 WIKI_ROOT。如果 `index.md` 不存在或无条目，提示用户先运行 `wiki-ingest`，然后停止。

### 第一阶段 — 确定性检查（Grep + Read）

1. **孤立页面** — 没有被任何其他页面的 `[[link]]` 引用的页面
2. **坏链** — 指向不存在页面的 `[[WikiLink]]`
3. **索引一致性** — `index.md` 中列出的页面是否实际存在
4. **缺失实体页** — 在 3+ 页面中提到但没有独立页面的实体
5. **标签审计** — 列出所有使用中的标签，标记不在 SCHEMA.md 分类法中的标签
6. **来源漂移** — 对 `raw/` 中有 `sha256` 的文件重新计算哈希，标记不匹配项
7. **页面大小** — 标记超过 200 行的页面 — 拆分候选
8. **日志轮转** — 如果 `log.md` 超过 500 条，轮转它

### 第二阶段 — 语义分析（Claude 读取最多 20 页样本）

9. **内容矛盾** — 跨页面的冲突主张。查找共享标签/实体但陈述不同事实的页面。暴露所有 `contested: true` 或 `contradictions:` frontmatter 的页面供用户审查
10. **过期摘要** — 在更新来源摄入后未更新的页面
11. **欠发达概念** — 被多处引用但内容单薄的概念页
12. **知识缺口** — Wiki 无法回答的典型问题，建议补充来源
13. **质量信号** — 列出 `confidence: low` 的页面，以及仅引用单一来源但未设置 confidence 字段的页面 — 这些是寻找佐证或降级为 `confidence: medium` 的候选

### 输出

生成结构化 Lint 报告，按类别和严重程度分组。询问是否保存为 `lint-report.md`。
追加日志：`## [YYYY-MM-DD] lint | 发现 N 个问题`

**严重程度排序**：坏链 > 孤立页 > 来源漂移 > 矛盾页 > 过期内容 > 样式问题

---

## 图谱流程

**触发**：`wiki-graph` 或 `构建知识图谱`

**步骤 0** — 解析 WIKI_ROOT（`.claude/config/llm-wiki.json` → cwd），脚本路径和 Wiki 路径均基于 WIKI_ROOT。

### 方法 A — 执行 Python 脚本（推荐）

```bash
cd <WIKI_ROOT>
python <skill-root>/scripts/build_graph.py [--skip-infer] [--open]
```

> **注意**：脚本使用相对路径，必须在 WIKI_ROOT 目录执行（包含 `entities/`、`concepts/`、`graph/` 等子目录的目录）。

参数说明：
- `--skip-infer`：跳过 AI 语义推断，仅提取显式 wikilinks（快速模式，无需 `ANTHROPIC_API_KEY`）
- `--open`：构建完成后自动在浏览器中打开 `graph/graph.html`

脚本支持增量缓存，内容未变的页面复用之前的推断结果，缓存存储在 `graph/.graph_cache.json`。

依赖：`pip install networkx python-louvain anthropic`

### 方法 B — 纯 Claude 手动构建（无 Python 环境时）

1. 使用 `Grep` 在 `entities/`、`concepts/`、`comparisons/`、`queries/`、`sources/` 下查找所有 `[[wikilinks]]`
2. 构建节点列表：每个 Wiki 页面是一个节点，类型来自 frontmatter
3. 构建边列表：显式 wikilink 标记为 `EXTRACTED`，语义推断边（置信度 ≥ 0.5）标记为 `INFERRED`（带 0-1 置信度），置信度 < 0.5 的推断边被过滤
4. 写入 `graph/graph.json`（格式见下）
5. 写入 `graph/graph.html`（使用 [templates/wiki-graph-template.html](templates/wiki-graph-template.html) 注入数据）
6. 追加日志：`## [YYYY-MM-DD] graph | 知识图谱已重建`
7. 输出统计：节点数、边数、类型分布、前 5 个枢纽页面

### graph.json 格式

```json
{
  "build_date": "YYYY-MM-DD",
  "nodes": [
    {
      "id": "concepts/RAG.md",
      "label": "RAG",
      "type": "concept",
      "community": 0,
      "degree": 5
    }
  ],
  "edges": [
    {
      "source": "sources/paper-rag.md",
      "target": "concepts/RAG.md",
      "type": "EXTRACTED"
    },
    {
      "source": "concepts/RAG.md",
      "target": "concepts/VectorDB.md",
      "type": "INFERRED",
      "confidence": 0.85,
      "label": "depends on"
    }
  ]
}
```

字段说明：
- `nodes[].community`：Louvain 社区编号（整数），安装 `python-louvain` 时自动计算；否则全为 `0`
- `nodes[].degree`：节点的入度/出度之和（边连接数）
- `edges[].type`：`EXTRACTED`（显式 wikilink）或 `INFERRED`（AI 推断，置信度 ≥ 0.5）

### 节点颜色规范

| 类型 | 颜色 |
|---|---|
| source | `#4A90D9`（蓝色） |
| entity | `#E8A838`（橙色） |
| concept | `#5BA85A`（绿色） |
| comparison | `#E74C3C`（红色） |
| query | `#1ABC9C`（青色） |
| synthesis | `#9B59B6`（紫色） |

---

## 命名约定

- 来源 slug：`kebab-case`，与原始文件名一致
- 实体页：`TitleCase.md`（如 `OpenAI.md`、`SamAltman.md`）
- 概念页：`TitleCase.md`（如 `ReinforcementLearning.md`、`RAG.md`）
- 对比页：`kebab-case.md`（如 `gpt4-vs-claude.md`）
- 来源页：`kebab-case.md`
- 归档页：保留原始文件名，移至 `archive/`

---

## 归档机制

当 Wiki 页面的内容完全被更新页面取代，或来源文档已过时时，可以归档：

1. 将文件移至 `archive/`
2. 在引用页面中，将 `[[页面名]]` 更新为 `[[archive/页面名]]`（附加 `[已归档]` 标记）
3. 从 `index.md` 中移除
4. 追加日志：`## [YYYY-MM-DD] archive | <页面名>`

> 归档是快照，不会随来源页面变化而更新。

---

## 页面阈值

- **创建页面**：当实体/概念在 2+ 来源中出现，或是一个来源的核心内容时
- **更新页面**：当来源提到已涵盖的内容时，添加到现有页面
- **不要创建页面**：对于路过提及、次要细节或超出领域范围的内容
- **拆分页面**：当页面超过 ~200 行时 — 拆分为子主题并交叉链接
- **归档页面**：当内容完全被取代时 — 移至 `archive/`，从 index 移除

---

## 更新策略

当新信息与现有内容冲突时：

1. **检查日期** — 更新的来源通常覆盖旧的来源
2. **如果真正矛盾** — 标注两种立场及其日期和来源
3. **在 frontmatter 中标记矛盾**：`contradictions: [页面名]`
4. **在 Lint 报告中标记供用户审查**

---

## vis.js HTML 模板

手动生成 `graph/graph.html` 时，使用 [`templates/wiki-graph-template.html`](templates/wiki-graph-template.html) 作为模板框架。

将文件中的 `/* GRAPH_JSON_PLACEHOLDER */` 替换为 `graph.json` 的实际 JSON 内容，即可得到零依赖的独立 HTML 文件。

---

## 多模态提取详细规格

### PDF 提取

```python
import pdfplumber

def extract_pdf(path: str) -> str:
    parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables()
            parts.append(f"<!-- Page {i+1} -->\n{text}")
            for tbl in tables:
                if tbl:
                    header = " | ".join(str(c) for c in tbl[0])
                    sep = " | ".join(["---"] * len(tbl[0]))
                    rows = "\n".join(" | ".join(str(c) for c in r) for r in tbl[1:])
                    parts.append(f"\n| {header} |\n| {sep} |\n{rows}\n")
    return "\n\n".join(parts)
```

### DOCX 提取

```python
from docx import Document

def extract_docx(path: str) -> str:
    doc = Document(path)
    parts = []
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            level = para.style.name.split(" ")[-1]
            parts.append(f"{'#' * int(level)} {para.text}")
        elif para.text.strip():
            parts.append(para.text)
    for table in doc.tables:
        rows = [[c.text for c in r.cells] for r in table.rows]
        if rows:
            header = " | ".join(rows[0])
            sep = " | ".join(["---"] * len(rows[0]))
            body = "\n".join(" | ".join(r) for r in rows[1:])
            parts.append(f"| {header} |\n| {sep} |\n{body}")
    return "\n\n".join(parts)
```

### PPTX 提取

```python
from pptx import Presentation

def extract_pptx(path: str) -> str:
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides):
        slide_parts = [f"## Slide {i+1}"]
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        slide_parts.append(text)
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                slide_parts.append(f"_Notes: {notes}_")
        parts.append("\n".join(slide_parts))
    return "\n\n---\n\n".join(parts)
```

### XLSX 提取

```python
import pandas as pd

def extract_xlsx(path: str) -> str:
    xl = pd.ExcelFile(path)
    parts = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet).fillna("")
        md = df.to_markdown(index=False)
        parts.append(f"### Sheet: {sheet}\n\n{md}")
    return "\n\n".join(parts)
```

---

## 图像内容理解

对于 `.png`、`.jpg`、`.jpeg`、`.webp` 等图像文件，直接使用 Claude 的视觉能力（`Read` 工具读取图像文件），从图表、流程图、表格截图中提取文本和结构，转为 Markdown 描述后进入摄入流程。

### 图像提取内容

- **图表和数据图** — 数据系列、轴标签、趋势和数值
- ** Diagrams 和流程图** — 节点、边、关系和流向
- **截图** — UI 结构、可见文本和布局上下文
- **手写笔记 / 白板** — 转录的文本和绘制的结构
- **图像中的表格** — 重建为 Markdown 表格
- **混合内容** — 同时包含文本和图的拍照/扫描文档

---

## 重要注意事项

1. **永不修改** `raw/` 目录中的原始文档
2. 每次摄入前检查 `log.md` 确认是否已摄入，避免重复
3. 矛盾标注优先级高于内容更新：先标注，再决定是否覆盖
4. graph.html 应为独立文件（内联 JSON 数据），无需服务器
5. **批量摄入时**，先读取所有来源，一次性搜索和更新，最后统一写入 index 和 log
6. `index.md` 按类型分区组织，每个分区维护文章列表（带摘要和更新日期）
7. `log.md` 是追加型的，永不修改历史记录，它是 Wiki 演进的完整审计追踪
8. **每次会话开始时必须先定向** — 读取 SCHEMA + index + 最近 log
9. **标签必须来自分类法** — 需要新标签时先在 SCHEMA.md 中添加，再使用
10. **保持页面可扫描** — Wiki 页面应在 30 秒内可读，超过 200 行时拆分
11. **触及 10+ 现有页面的大规模更新前**，先与用户确认范围
12. **明确处理矛盾** — 不要静默覆盖。标注两种主张及日期，标记 frontmatter，标记供用户审查

---

## 中断与恢复

多步骤流程（尤其是 12 步的 `wiki-ingest` 流程）可能因网络、会话超时或用户中断而中断。

### 判断中断

`log.md` 是唯一的完成状态指示器：

- **日志中有此文件的 `ingest` 条目** → 正常完成，无需操作
- **`sources/<slug>.md` 存在，但日志无对应条目** → 上次摄入在第 11 步前中断
- **`sources/` 中无对应文件** → 摄入在早期步骤中断或从未开始

### 恢复方法

重新运行 `wiki-ingest <file>`，在去重检查（步骤 1）时系统会提示"未找到日志记录，是否继续？"— 选择继续并从开头重新执行完整流程。如果某些页面已写入，重新摄入会以最新版本覆盖，不会产生重复内容。

### 批量摄入中断

批量摄入（多个文件）期间，每个文件完成后立即追加日志。中断后，只需从**最后一条日志之后的文件**继续，已完成文件无需重新处理。
