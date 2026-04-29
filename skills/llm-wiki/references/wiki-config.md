# wiki-config — 工作区路径配置命令

配置 llm-wiki 工作区路径，使 Wiki 命令可以从任意位置找到正确的 `raw/`、`entities/`、`concepts/`、`graph/` 等目录。

**触发**：`wiki-config workspace <path>` / `wiki 配置` / `设置 wiki 路径`

---

## 命令

### `wiki-config workspace <path>`

设置工作区路径，写入 `.claude/config/llm-wiki.json`。

```
wiki-config workspace /Users/me/projects/my-wiki
wiki-config workspace ~/notes/research-wiki
```

**执行流程**：

1. 展开路径为绝对路径（处理 `~`）
2. 验证目标目录是否存在；如不存在，询问用户是否创建
3. 读取或初始化 `.claude/config/llm-wiki.json`，写入 `workspace` 字段
4. 输出确认：`WIKI_ROOT 已设置为 /absolute/path`

> 配置文件格式见 [../config/llm-wiki.example.json](../config/llm-wiki.example.json)，可直接复制编辑。

---

### `wiki-config show`

显示当前 WIKI_ROOT 来源和子目录状态。

**示例输出**：

```
WIKI_ROOT:   /Users/me/projects/my-wiki   (来源: .claude/config/llm-wiki.json)
  raw/       存在
  entities/  存在
  concepts/  存在
  graph/     不存在（首次运行 wiki-graph 时自动创建）
```

如果未配置，输出：

```
WIKI_ROOT:   /当前工作目录   (来源: cwd 默认)
提示: 运行 wiki-config workspace <path> 设置固定工作区路径
```

---

### `wiki-config reset`

清除 `.claude/config/llm-wiki.json` 中的 `workspace` 字段，恢复为 cwd 默认。

---

## 使用场景

- **Wiki 目录不在项目根目录**：Claude Code 工作目录是代码仓库，Wiki 在另一个路径
- **多个 Wiki 项目**：使用 `@<path>` 临时覆盖，或修改配置文件切换
- **CI / 自动化**：通过 `@<path>` 显式指定，无需依赖配置文件
