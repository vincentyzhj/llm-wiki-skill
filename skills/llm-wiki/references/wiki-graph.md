# wiki-graph — 知识图谱构建命令

构建 Wiki 知识图谱。

**触发**：`wiki-graph` 或 `构建知识图谱`

## 参数

无参数。

## 执行流程

按照 SKILL.md 中的 **图谱流程** 执行：

### 方法 A — Python 脚本（推荐）

> **重要**：脚本使用相对路径，必须在 **WIKI_ROOT 目录** 中执行。

```bash
cd <WIKI_ROOT>
python <skill-root>/scripts/build_graph.py [--skip-infer] [--open]
```

参数说明：
- `--skip-infer`：跳过 AI 语义推断，仅提取显式 wikilinks（快速模式，无需 `ANTHROPIC_API_KEY`）
- `--open`：构建完成后自动在浏览器中打开 `graph/graph.html`

脚本支持增量缓存，内容未变的页面复用之前的推断结果，缓存存储在 `graph/.graph_cache.json`。

依赖：`pip install networkx python-louvain anthropic`

### 方法 B — 纯 Claude 手动构建（无 Python 环境时）

1. 使用 Grep 在 `entities/`、`concepts/`、`comparisons/`、`queries/`、`sources/` 下查找所有 `[[wikilinks]]`
2. 构建节点列表：每个 Wiki 页面是一个节点，类型来自 frontmatter
3. 构建边列表：显式 wikilink 标记为 `EXTRACTED`，语义推断边（置信度 ≥ 0.5）标记为 `INFERRED`，置信度 < 0.5 的推断边被过滤
4. 写入 `graph/graph.json`（包含 build_date、nodes、edges）
5. 写入 `graph/graph.html`（使用 [../templates/wiki-graph-template.html](../templates/wiki-graph-template.html) 注入数据）
6. 追加日志到 `log.md`：`## [YYYY-MM-DD] graph | 知识图谱已重建`
7. 输出统计：节点数、边数、类型分布、前 5 个枢纽页面
