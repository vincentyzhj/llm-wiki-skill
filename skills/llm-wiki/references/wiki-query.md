# wiki-query — 知识库查询命令

查询 Wiki 知识库并综合答案。

**触发**：`wiki-query: <问题>` 或 `wiki 查询：<问题>`

## 参数

`$ARGUMENTS` 是查询问题（自然语言），例如：

```
wiki-query: 什么是 RAG？
wiki-query: 项目中提到了哪些关键技术？
wiki-query: 不同来源对 Transformer 的观点有何差异？
```

## 执行流程

按照 SKILL.md 中的 **查询流程** 执行：

0. 解析 WIKI_ROOT（命令行 `@<path>` → `.claude/config/llm-wiki.json` → cwd），所有路径基于 WIKI_ROOT
1. 如果 `index.md` 不存在或无条目，提示用户先运行 `wiki-ingest`
2. 读取 `index.md`，识别与问题最相关的页面（最多 10 页）
3. 对于 100+ 页面的大型 Wiki，同时搜索所有 `.md` 文件中的关键词
4. 使用 Read 工具读取每个相关页面
5. 综合答案，使用 `[[页面名]]` wikilink 进行行内引用；直接引用不超过 125 字符
6. 在答案末尾附加 `## 来源` 部分，列出所有引用的页面路径
7. 如果答案是实质性的对比、深入分析或新颖综合，归档到 `queries/<slug>.md`
8. 追加日志到 `log.md`：`## [YYYY-MM-DD] query | <问题摘要>`

## 输出格式示例

```markdown
基于 [[RAG]] 和 [[VectorDB]] 的记录，检索增强生成（RAG）是...

## 来源
- concepts/RAG.md
- concepts/VectorDB.md
- wiki/sources/paper-rag-survey.md
```
