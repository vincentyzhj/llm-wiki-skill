# Wiki Schema

> 本文件定义 Wiki 的领域范围、结构约定和标签分类法。
> 每次摄入、查询或 Lint 操作前，Agent 必须先读取此文件以确保遵循约定。
> 需要新标签时，必须先在此处添加，再在页面中使用。

## Domain

[定义此 Wiki 覆盖的领域 — 例如 "AI/ML 研究"、"个人健康"、"创业情报"、"技术笔记"]

> 示例：本 Wiki 覆盖人工智能和机器学习领域，包括模型架构、训练方法、应用案例、行业动态等。

---

## Conventions

### 文件命名
- 文件名：小写，连字符分隔，无空格（如 `transformer-architecture.md`）
- 实体页和概念页：`TitleCase.md`（如 `OpenAI.md`、`ReinforcementLearning.md`）
- 来源页和对比页：`kebab-case.md`（如 `karpathy-llm-wiki-2026.md`、`gpt4-vs-claude.md`）

### 页面结构
- 每个 Wiki 页面必须以 YAML frontmatter 开头（格式见下方）
- 使用 `[[wikilinks]]` 链接其他页面（每页至少 2 个出站链接）
- 更新页面时必须 bump `updated` 日期
- 新页面必须添加到 `index.md` 的正确分区
- 每个操作必须追加到 `log.md`

### 来源标记
- 综合 3+ 来源的页面，在段落末尾附加 `^[sources/来源slug]` 标记
- 单来源页面中，frontmatter 的 `sources:` 字段已足够，无需段落标记

### 页面阈值
- **创建页面**：当实体/概念在 2+ 来源中出现，或是一个来源的核心内容时
- **拆分页面**：当页面超过 ~200 行时，拆分为子主题并交叉链接
- **归档页面**：当内容完全被取代时，移至 `archive/`，从 index 移除

### 更新策略
- 新信息与现有内容冲突时，检查日期 — 更新的来源通常覆盖旧的
- 如果真正矛盾，标注两种立场及其日期和来源
- 在 frontmatter 中标记矛盾：`contradictions: [页面名]`
- 在 Lint 报告中标记供用户审查

---

## Frontmatter

### 通用 Frontmatter（所有页面类型）

```yaml
---
title: "页面标题"
type: entity | concept | comparison | query
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [来自下方分类法]
sources: [slug-1, slug-2]              # 来源页 slug 列表（不含路径前缀）
---
```

### 来源页额外字段

```yaml
---
type: source
date: YYYY-MM-DD                     # 原始文档日期
source_file: raw/<topic>/<文件名>
source_type: pdf | docx | pptx | xlsx | markdown | image
---
```

### 质量信号（可选但推荐）

```yaml
---
confidence: high | medium | low      # 主张的支撑程度
contested: true                      # 存在未解决的矛盾时设置
contradictions: [其他页面名]          # 与之冲突的页面
---
```

**quality 字段说明**：
- `confidence: high` — 主张跨多来源充分支撑
- `confidence: medium` — 主张有合理支撑但非共识
- `confidence: low` — 主张基于单一来源或推测
- `contested: true` — 页面与其他页面存在未解决的矛盾
- `contradictions` — 列出与之冲突的页面名

### Raw 来源 Frontmatter

`raw/` 中的原始来源文件也添加小型 frontmatter，以便重新摄入时检测漂移：

```yaml
---
source_url: https://example.com/article   # 原始 URL（如适用）
ingested: YYYY-MM-DD
sha256: <正文内容的十六进制摘要>
---
```

SHA256 计算范围：frontmatter 之后的正文内容，不包含 frontmatter 本身。
重新摄入同一 URL 时：重新计算 SHA256，与存储值比较 — 相同则跳过处理，不同则标记来源漂移并更新。

---

## 标签分类法

> 规则：每个页面上的标签**必须**出现在下方分类法中。
> 如果需要新标签，必须先添加到此处的分类法，然后再在页面中使用。
> 这防止标签泛滥导致噪声。

### 示例分类法（AI/ML 领域）

**模型相关**：
- `model` — 具体 AI/ML 模型
- `architecture` — 模型架构设计
- `benchmark` — 性能基准测试
- `training` — 训练方法/技巧

**人物/组织**：
- `person` — 研究人员/工程师
- `company` — 公司/企业
- `lab` — 研究实验室
- `open-source` — 开源项目/社区

**技术方法**：
- `optimization` — 优化技术
- `fine-tuning` — 微调方法
- `inference` — 推理/部署
- `alignment` — 对齐技术
- `data` — 数据处理/数据集

**元标签**：
- `comparison` — 对比分析
- `timeline` — 时间线/历史
- `controversy` — 争议/辩论
- `prediction` — 预测/展望

> 使用时从上述标签中选择。添加新标签时，请先在此处分类法中定义，再使用。

---

## raw/ 目录分类法

> `raw/` 目录下的来源文件归档分类。
> 固定分类目录由系统预设，自定义 topic 由用户通过 `--topic` 参数创建。
> **新 topic 会自动追加到此分类法中**。

### 固定分类目录

| 目录 | 用途 | 判断依据 |
|------|------|----------|
| `articles/` | 网页文章、剪报、博客 | URL 来源、HTML 结构 |
| `papers/` | PDF、arxiv 论文、学术文献 | `.pdf` 扩展名、标题/摘要结构 |
| `transcripts/` | 会议记录、访谈、对话 | 对话格式、时间戳标记 |
| `assets/` | 图片、图表、截图 | `.png/.jpg/.webp` 扩展名 |
| `inbox/` | 无法判断类型时的默认归档 | 无明确特征 |

### 自定义 Topic 目录

> 使用 `wiki-input <file> --topic <slug>` 时自动创建。
> Agent 会将新 topic 自动追加到下方列表。

**已有 topic 列表**：

- `inbox` — 默认归档（初始）
- （后续 topic 通过 `--topic` 参数自动追加）

> 添加新 topic 的格式：在上方列表中追加一行 `- `<slug>` — <简短描述>`

---

## 目录结构

```
<WIKI_ROOT>/
├── SCHEMA.md                    # 本文件
├── index.md                     # 分区内容目录
├── overview.md                  # 跨来源动态合成摘要
├── log.md                       # 按时间追加型操作日志
│
├── raw/                         # 不可变原始来源
│   ├── articles/                # 网页文章
│   ├── papers/                  # PDF/论文
│   ├── transcripts/             # 会议/访谈
│   └── assets/                  # 图片/图表
│
├── sources/                     # 每个原始文档的摘要页
├── entities/                    # 实体页
├── concepts/                    # 概念页
├── comparisons/                 # 对比分析页
├── queries/                     # 查询结果归档
├── archive/                    # 归档的过期页面
│
└── graph/                       # 知识图谱
    ├── graph.json
    └── graph.html
```

---

## 最后更新

- 最后修订：YYYY-MM-DD
- 修订者：[Agent 名称或用户名称]
