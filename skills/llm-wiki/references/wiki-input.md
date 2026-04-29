# wiki-input — 任意路径文件摄入命令

接受任意本地路径（或远程 OSS 路径）的文件，**先复制到 `raw/<topic>/` 归档，再摄入**，触发完整摄入流程。

**WIKI_ROOT 严格由 `.claude/config/llm-wiki.json` 中的 `workspace` 确定，与输入文件路径无关。**

**触发**：`wiki-input <path> [--topic <slug>]` / `wiki 输入 <path>`

---

## 命令

### `wiki-input <path> [--topic <slug>]`

```
wiki-input ~/Documents/text.pdf --topic oneservice
wiki-input ~/Documents/image.png --topic user-profile
wiki-input ~/Downloads/test1.pptx
wiki-input C:/files/test1.md --topic inbox
wiki-input oss://my-bucket/documents/report.pdf --topic oneservice
wiki-input https://example.com/whitepaper.pdf
```

未指定 `--topic` 时，文件归档到 `raw/inbox/`。

---

## 执行流程

### 步骤 0 — 确定 WIKI_ROOT

从 `.claude/config/llm-wiki.json` 读取 `workspace` 字段，展开 `~` 为绝对路径。目录不存在则**在该路径自动创建完整目录结构**后继续。**不要从输入文件路径推断 WIKI_ROOT，配置文件存在时不要回退到 cwd。**

### 步骤 1 — 路径解析与验证

1. 展开路径：
   - `~` 展开为用户家目录
   - Windows 路径 `C:/...` 或 `C:\...` 直接使用
   - 相对路径基于当前工作目录展开
2. 验证文件存在且可读；如不可读，报错并终止
3. 识别文件扩展名，确认是支持的格式（见下方支持格式表）

对于远程路径，先下载到临时目录，再继续后续步骤：

| 路径前缀 | 下载方法 |
|---|---|
| `oss://` | `ossutil cp <path> /tmp/wiki-input-tmp/` |
| `s3://` | `aws s3 cp <path> /tmp/wiki-input-tmp/` |
| `http(s)://` | `curl -L <url> -o /tmp/wiki-input-tmp/<文件名>` |

如所需 CLI 工具未安装，提示用户安装并终止。

### 步骤 1.5 — 确定主题并归档到 raw/

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
- 首次使用新 topic 时，自动追加到 `SCHEMA.md` 的 `raw_topics` 分类法

**主题 slug 规则**：全小写，仅 `a-z`、`0-9`、连字符，最长 32 字符。

执行步骤：
1. 如果归档目录不存在，自动创建
2. 复制文件到归档目录
3. 如果同名文件已存在，询问用户是否覆盖；如拒绝，终止
4. 远程文件的临时副本在复制完成后删除
5. 如果是新 topic，追加到 `SCHEMA.md` 的 `raw_topics` 列表

### 步骤 2 — 触发摄入流程

对 `raw/<topic>/<文件名>` 执行完整摄入流程（去重检查 → 多模态提取 → Wiki 写入）。

- `source_file` 字段记录 `raw/<topic>/<文件名>` 路径
- 远程文件的原始 URL / OSS 路径记录在来源页的 `## 备注` 部分

---

## 支持的文件格式

| 扩展名 | 提取方法 |
|---|---|
| `.md` `.txt` `.json` `.yaml` | 直接 Read 工具 |
| `.pdf` | pdf skill（pdfplumber） |
| `.docx` | docx skill（python-docx） |
| `.pptx` `.ppt`（转换后） | pptx skill |
| `.xlsx` `.csv` | xlsx skill |
| `.png` `.jpg` `.jpeg` `.webp` | Claude 视觉 |

> `.ppt`（旧版 PowerPoint）需先用 LibreOffice 转为 `.pptx`：
> `libreoffice --headless --convert-to pptx file.ppt`

---

## 远程 OSS 文件支持

### 阿里云 OSS（`oss://`）

**前置条件**：
- 已安装 `ossutil`（`ossutil version` 可执行）
- 已配置访问凭证（`ossutil config` 或环境变量 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET`）
- 对相应 bucket 有读取权限

### AWS S3（`s3://`）

**前置条件**：
- 已安装 `aws` CLI
- 已配置凭证（`aws configure` 或环境变量 `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`）
- IAM 权限包含 `s3:GetObject`

### 其他远程协议

| 协议 | 支持方式 |
|---|---|
| `http://` / `https://` | curl，无需额外依赖 |
| `gs://` | `gsutil cp`（需 Google Cloud SDK） |
| `sftp://` / `scp` | 需手动下载，再使用本地路径 |

---

## 与 `wiki-ingest` 的区别

| | `wiki-ingest` | `wiki-input` |
|---|---|---|
| 文件位置 | 已在 `raw/` 目录中 | 任意本地或远程路径 |
| 文件复制 | 不需要 | 自动复制到 `raw/<topic>/` |
| 主题指定 | 文件路径即代表主题 | `--topic <slug>`，默认 `inbox` |
| 使用场景 | 手动管理 raw/ 后摄入 | 从任意位置直接摄入，自动归档 |
