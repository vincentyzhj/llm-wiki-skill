# Wiki 页面模板

本文档提供 llm-wiki 中六种页面类型的标准模板。

---

## 1. 来源页（Source Summary Page）

路径：`sources/<slug>.md`

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
2-4 句综合摘要，描述文档的核心主张和价值。

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
- 与 [[其他页面]] 在以下方面冲突：具体描述
```

---

## 2. 概念页 / 实体页（Knowledge Pages）

路径：`concepts/<名称>.md` 或 `entities/<名称>.md`

```markdown
---
title: "页面标题"
type: concept | entity
tags: [来自 SCHEMA.md 分类法]
sources: [slug-1, slug-2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
# 可选质量信号：
confidence: high | medium | low
contested: true
contradictions: [其他页面名]
---

## 概述
2-4 句概述，综合所有来源的核心理解。不要逐字复制来源内容，要重新组织和表达。

## 主要内容（按主题组织，而非按来源）

### 子主题一
...

### 子主题二
...

## 参见
- [[相关概念]] — 关联原因（同主题）
- [[../其他主题/另一概念]] — 关联原因（跨主题）
```

---

## 3. 对比分析页（Comparison Page）

路径：`comparisons/<对比名称>.md`

```markdown
---
title: "A vs B 对比"
type: comparison
tags: [comparison, 相关标签]
sources: [slug-1, slug-2]             # 来源页 slug 列表
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---

## 对比对象与目的
[对比什么，为什么对比]

## 对比维度

| 维度 | A | B | 备注 |
|------|---|---|------|
| 性能 | ... | ... | |
| 成本 | ... | ... | |
| 生态 | ... | ... | |
| 易用性 | ... | ... | |

## 综合结论
[综合判断和推荐]

## 来源
- [[sources/来源1]] — 引用原因
- [[sources/来源2]] — 引用原因

## 参见
- [[相关概念A]]
- [[相关概念B]]
```

---

## 4. 索引页（Directory Page）

路径：`index.md`

```markdown
# Wiki Index

> 内容目录。每个 Wiki 页面在其类型下列出，带一行摘要。
> 查询前先读此文件定位相关页面。
> 最后更新：YYYY-MM-DD | 总页数：N

## Entities
<!-- 按字母顺序排列 -->

- [[OpenAI]] — 领先的人工智能研究实验室
- [[SamAltman]] — OpenAI CEO

## Concepts

- [[ReinforcementLearning]] — 通过与环境交互学习最优策略
- [[RAG]] — 检索增强生成，结合外部知识源的生成方法

## Comparisons

- [[gpt4-vs-claude]] — GPT-4 与 Claude 的多维度对比

## Queries

- [[transformer-attention-mechanism]] — Transformer 注意力机制详解
```

**扩展规则**：当任何分区超过 50 个条目时，按首字母或子领域拆分子分区。当索引总条目超过 200 时，创建 `topic-map.md` 按主题分组页面以便更快导航。

---

## 5. 查询归档页（Query Answer Archive）

路径：`queries/<slug>.md`

```markdown
---
title: "问题摘要"
type: query
tags: [相关标签]
sources: [slug-1, slug-2]
query_date: YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## 问题

完整的查询问题。

## 答案

综合答案，使用 `[[页面名]]` 行内引用指向 Wiki 页面。直接引用不超过 125 字符。

## 来源

- [[sources/来源1]] — 引用原因
- [[concepts/概念名]] — 引用原因

## 矛盾

- 与 [[其他页面]] 在以下方面冲突：具体描述（如无矛盾则省略此部分）
```

> **归档规则**：只归档实质性的对比、深入分析或新颖综合。不要归档简单查找 — 只归档重新推导会很痛苦的答案。

---

## 6. 归档页（Archived Page）

路径：`archive/<原始名称>.md`

```markdown
---
title: "原始页面标题 [已归档]"
type: source | concept | entity
archived_date: YYYY-MM-DD
superseded_by: "[[新页面名]]"
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

> **此页面已归档**，内容已被 [[新页面名]] 取代，不再随来源变化而更新。

## 概述（归档时的快照）
...

## 参见
- [[新页面名]] — 当前有效版本
```

---

## Raw 来源模板（原始材料归档）

路径：`raw/<topic>/<文件名>`（原始文件，可选添加 frontmatter 注释）

```
---
title: "原始文档标题"
url: https://...（如来自网络）
date: YYYY-MM-DD
author: 作者名
ingested: YYYY-MM-DD
sha256: <正文内容的十六进制摘要>
---

{原始内容，不可修改}
```

> `raw/` 中的文件**永不修改**，这是 Wiki 系统的不可变性基石。
> 修正应写入 Wiki 页面，而非修改原始来源。

---

## Overview 页模板（跨来源合成摘要）

路径：`overview.md`

```markdown
# Wiki Overview

> 跨所有来源的动态合成摘要。每次摄入新来源后自动更新。
> 最后更新：YYYY-MM-DD

## 核心主题概览

### 主题一
[综合多个来源的概要]

### 主题二
[综合多个来源的概要]

## 关键趋势
[从所有来源中识别出的趋势]

## 未解决问题
[跨来源识别的开放问题或争议]
```
