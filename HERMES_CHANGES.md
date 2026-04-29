# Hermes 版本变更说明

> 分支：`Hermes` | 基于原版 `llmrix/llm-wiki-skill` main 分支
> 提交：`d81fec9`

---

## 概述

Hermes 版本在原版 `llm-wiki-skill` 基础上，融合了 Hermes Agent 的 `llm-wiki` v2.1.0 Skill 的三层架构理念，实现了结构兼容、质量约束和对比分析等增强功能，同时保留了原版的全部功能（多模态摄入、知识图谱、`wiki-config` 命令、中断恢复等）。

**核心原则**：原版能做的，Hermes 版都能做；Hermes 版新增的，原版不冲突。

---

## 变更清单

### 一、新增文件

| 文件 | 说明 |
|------|------|
| `skills/llm-wiki/templates/SCHEMA.md` | 新增 SCHEMA.md 模板，定义领域、标签分类法、页面约定、Frontmatter 规范、页面阈值和更新策略 |

### 二、重写文件

#### 1. `skills/llm-wiki/SKILL.md` — 核心 Skill 定义（完全重写）

| 改动项 | 原版 | Hermes 版 |
|--------|------|-----------|
| 语言 | 英文 | 中文 |
| 目录结构 | `wiki/` 下扁平存放 entities/concepts | 三层架构：`raw/`（Layer 1）→ `entities/`/`concepts/`/`comparisons/`/`queries/`（Layer 2）→ `SCHEMA.md`（Layer 3） |
| 会话定向 | 无 | **新增**：每次会话开始必须先读 SCHEMA.md + index.md + 最近 log.md |
| SCHEMA.md | 不存在 | **新增**：初始化时自动创建，定义领域、标签分类法、页面约定 |
| comparisons/ | 不存在 | **新增**：对比分析页目录，摄入时自动检测多实体对比信息 |
| queries/ | 不存在（只有 `syntheses/`） | **新增**：查询结果归档目录，与 `syntheses/` 兼容并存 |
| Frontmatter | `title`, `type`, `tags`, `sources`, `date`, `source_file`, `source_type`, `last_updated` | 合并为 `title`, `type`, `tags`, `sources`, `created`, `updated`, `source_file`, `source_type`, `date` + **新增** `confidence`, `contested`, `contradictions` 质量信号 |
| 来源漂移检测 | 无 | **新增**：重新摄入同一 URL 时通过 SHA256 检测内容变化 |
| 标签约束 | 自由标签 | **必须**来自 SCHEMA.md 分类法，Lint 时审计 |
| 日志轮转 | 无 | **新增**：log.md 超 500 条自动轮转为 log-YYYY.md |
| 页面拆分 | 无 | **新增**：页面超 ~200 行时提示拆分为子主题 |
| 批量摄入优化 | 逐个处理 | **新增**：一次性搜索 + 一次性更新索引和日志 |
| 摄入步骤 | 10 步 | 扩展为 12 步（新增：读 SCHEMA、创建 comparisons、搜索已有页面） |
| Lint 检查项 | 8 项 | 扩展为 13 项（新增：标签审计、来源漂移、页面大小、日志轮转、质量信号） |
| 节点类型 | 4 种（source/entity/concept/synthesis） | 6 种（+comparison/query） |

#### 2. `skills/llm-wiki/templates/wiki-page-templates.md` — 页面模板（重写为中文）

| 改动项 | 说明 |
|--------|------|
| 语言 | 英文 → 中文 |
| 页面类型 | 5 种 → 6 种（新增 Comparison 对比分析页模板） |
| Frontmatter | 合并两个版本，新增 `confidence`/`contested`/`contradictions`/`created`/`updated` 字段 |
| Query 页面 | 原 Synthesis 页面改为 Query 页面，路径从 `syntheses/` 扩展为 `queries/`（兼容旧版） |
| Index 页面 | 新增扩展规则（50 条分区拆分子分区、200 条总量创建 topic-map） |
| Overview 页面 | **新增**：跨来源合成摘要模板 |

#### 3. `skills/llm-wiki/scripts/build_graph.py` — 图谱构建脚本

| 改动项 | 原版 | Hermes 版 |
|--------|------|-----------|
| 页面扫描 | 仅扫描 `wiki/` 目录 | 扫描 `PAGE_DIRS` 列表，兼容新旧两种目录结构 |
| 目录列表 | `WIKI_DIR` 单一目录 | `entities/`、`concepts/`、`comparisons/`、`queries/`（根目录）+ `wiki/sources/`、`wiki/syntheses/`、`wiki/entities/`、`wiki/concepts/`（兼容旧版） |
| 链接解析 | 搜索 `wiki/` 子目录 | 同时搜索根级和 `wiki/` 子目录 |
| 日志路径 | `wiki/log.md` | `log.md`（根级） |
| 节点颜色 | 4 种 | 6 种（+comparison 红色 `#E74C3C`、query 青色 `#1ABC9C`） |

#### 4. `skills/llm-wiki/references/*.md` — 6 个参考文档（全部翻译为中文）

| 文件 | 改动要点 |
|------|----------|
| `wiki-config.md` | 翻译为中文；目录示例更新为新的三层结构 |
| `wiki-ingest.md` | 翻译为中文；步骤从 10 扩展为 12（新增读 SCHEMA、创建 comparisons、来源漂移检测） |
| `wiki-input.md` | 翻译为中文；保持远程/OSS 支持不变 |
| `wiki-query.md` | 翻译为中文；归档路径从 `syntheses/` 扩展为 `queries/` |
| `wiki-lint.md` | 翻译为中文；检查项从 8 扩展为 13（新增标签审计、来源漂移、页面大小、日志轮转、质量信号） |
| `wiki-graph.md` | 翻译为中文；扫描目录更新为 `entities/`/`concepts/`/`comparisons/`/`queries/` |

#### 5. `README.md` — 项目说明（重写为中文）

| 改动项 | 说明 |
|--------|------|
| 语言 | 英文 → 中文 |
| 目录结构 | 更新为三层架构版本 |
| 新增 | 三层架构说明、新增功能表、SCHEMA.md 配置提示 |
| 快速开始 | 新增"首次初始化后编辑 SCHEMA.md"步骤 |

---

## 兼容性说明

### 向后兼容

| 原版功能 | Hermes 版状态 |
|----------|-------------|
| `wiki-config` 命令系统 | ✅ 完全保留 |
| `wiki-input` 远程/OSS 支持 | ✅ 完全保留 |
| 知识图谱（graph.html） | ✅ 完全保留，兼容新旧目录 |
| 多模态提取（PDF/DOCX/PPTX/XLSX/图片） | ✅ 完全保留 |
| 中断恢复机制 | ✅ 完全保留 |
| 中文触发词 | ✅ 完全保留 |
| `wiki/` 子目录结构 | ✅ 兼容，新页面优先写入根级目录 |

### 目录迁移

已有原版 Wiki 数据**无需迁移**。Hermes 版的 `build_graph.py` 同时扫描 `entities/`（新）和 `wiki/entities/`（旧）目录，两套结构可并存。

如需完全迁移到新结构：
1. 将 `wiki/entities/*.md` → `entities/`
2. 将 `wiki/concepts/*.md` → `concepts/`
3. 将 `wiki/syntheses/*.md` → `queries/`
4. 将 `wiki/index.md`、`overview.md`、`log.md` → 移到根级
5. 创建 `SCHEMA.md`、`comparisons/` 目录

### Frontmatter 兼容

原版 frontmatter 中的 `last_updated` 字段会被 Hermes 版的 `updated` 字段替代，但两者可共存。`build_graph.py` 通过 frontmatter 中的 `type` 字段识别页面类型，新增 `comparison` 和 `query` 类型。

---

## Hermes Agent 特有功能的取舍

| Hermes llm-wiki v2.1.0 功能 | Hermes 版处理 |
|------------------------------|-------------|
| Obsidian 集成 | ❌ 未植入（原版无 Obsidian 支持，按需另加） |
| `obsidian-headless` 同步 | ❌ 未植入（需要 Node.js 环境，不适合 Skill 依赖） |
| 批量摄入优化 | ✅ 植入（SKILL.md 中新增批量摄入策略说明） |
| 页面阈值规则 | ✅ 植入（2+ 来源才创建页面、200 行拆分） |
| 质量信号（confidence/contested） | ✅ 植入（Frontmatter 和 Lint 中） |
| 来源漂移检测（SHA256） | ✅ 植入（SKILL.md 摄入流程步骤 1.5） |

---

## 文件变更统计

```
 README.md                                      | 245 ++++---
 skills/llm-wiki/SKILL.md                       | 689 +++++++++++-----
 skills/llm-wiki/references/wiki-config.md      |  51 +--
 skills/llm-wiki/references/wiki-graph.md       |  44 +-
 skills/llm-wiki/references/wiki-ingest.md      |  92 +--
 skills/llm-wiki/references/wiki-input.md       | 126 ++---
 skills/llm-wiki/references/wiki-lint.md        |  49 +--
 skills/llm-wiki/references/wiki-query.md       |  47 +-
 skills/llm-wiki/scripts/build_graph.py         |  45 +-
 skills/llm-wiki/templates/SCHEMA.md            | 161 +++++
 skills/llm-wiki/templates/wiki-page-templates.md | 244 +++---
 11 files changed, 1134 insertions(+), 660 deletions(-)
```