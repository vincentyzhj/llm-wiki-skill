# wiki-ingest — 文档摄入命令

将文档摄入到 LLM Wiki 知识库（支持多模态）。

**触发**：`wiki-ingest <file>` 或 `把 <file> 加入 wiki`

## 参数

`$ARGUMENTS` 是 `raw/` 目录下的文件路径，例如：

```
wiki-ingest raw/papers/attention-is-all-you-need.pdf
wiki-ingest raw/slides/q1-review.pptx
wiki-ingest raw/reports/market-analysis.xlsx
wiki-ingest raw/articles/my-article.md
```

## 支持的格式

`.md` `.txt` `.pdf` `.docx` `.pptx` `.xlsx` `.png` `.jpg` `.jpeg` `.webp`

## 执行流程

严格按照 SKILL.md 中的 **摄入流程** 执行：

### 步骤 0 — 确定 WIKI_ROOT

按优先级解析工作区路径（命令行 `@<path>` → `.claude/config/llm-wiki.json` → cwd），展开 `~` 为绝对路径。目录不存在则自动创建完整目录结构后继续。后续所有路径均相对于 WIKI_ROOT。

### 步骤 1 — 去重检查

读取 `log.md`，按文件名检查是否已有摄入记录。如存在，询问用户是否强制重新摄入。

### 步骤 1.5 — 来源漂移检测（如适用）

如果是对已有 URL 的重新摄入，计算 SHA256 并与存储值比较。相同则跳过，不同则标记漂移。

### 步骤 2 — 多模态内容提取

根据文件扩展名选择提取方法：

| 文件类型 | 提取方法 |
|---|---|
| `.md` `.txt` `.json` `.yaml` | 直接 Read 工具 |
| `.pdf` | 使用 pdfplumber 提取文本和表格（见 pdf skill） |
| `.docx` | 使用 python-docx 提取正文、标题、表格（见 docx skill） |
| `.pptx` | 提取每页幻灯片的标题、正文、备注（见 pptx skill） |
| `.xlsx` `.csv` | 使用 pandas 转为 Markdown 表格（见 xlsx skill） |
| `.png` `.jpg` `.jpeg` `.webp` | 使用 Read 工具直接读取图像（Claude 视觉） |

提取结果统一为带标题层级的 Markdown 文本。

### 步骤 3-12 — Wiki 写入（按顺序执行）

1. 读取 `SCHEMA.md` 理解领域约定和标签分类法
2. 读取 `index.md` 和 `overview.md` 获取当前上下文
3. 搜索已有页面，针对提到的实体/概念查找现有页面
4. 写入 `sources/<slug>.md`（来源页格式，见 [../templates/wiki-page-templates.md](../templates/wiki-page-templates.md)）
5. 更新 `index.md`，在对应主题分区追加新条目
6. 更新 `overview.md`，修订跨来源合成摘要
7. 在 `entities/` 下创建/更新关键实体页
8. 在 `concepts/` 下创建/更新关键概念页
9. 如来源包含对比信息，在 `comparisons/` 下创建/更新对比页
10. 标记与现有 Wiki 内容的矛盾（写入相关页面的 `## Contradictions` 部分）
11. 追加日志到 `log.md`：`## [YYYY-MM-DD] ingest | <标题>`
12. 输出摘要：哪些页面被创建、哪些被更新、发现哪些矛盾

## 注意事项

- **永不修改** `raw/` 目录中的原始文档
- 矛盾标注优先级高于内容更新：先标注，再决定是否覆盖
- 批量摄入时，逐个处理文件，每个完成后追加一条日志
- 页面模板见 [../templates/wiki-page-templates.md](../templates/wiki-page-templates.md)
