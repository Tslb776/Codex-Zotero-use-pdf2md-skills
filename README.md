# Codex-Zotero-use-pdf2md-skills

## 中文简介

这是一个 Codex 控制 Zotero 进行文献阅读与分析的 skill 合集，包含用于连接 Codex 与 Zotero 的本地插件 `codex_zotero_bridge`（需要手动安装到 Zotero）、基于该插件的 `zotero-use` skill，以及基于 MinerU API 的 Zotero 条目 PDF 论文转 Markdown/HTML 工作流。MinerU API 需要在 [MinerU 官网](https://mineru.net/) 申请免费 API key。转换后的 Markdown 和 HTML 文件可以重新挂载到对应 Zotero 论文条目下，后续可根据需要用于 AI 图文并茂的论文解读、多篇论文对比分析和文献综述编写。

这是一个基于 Codex + Zotero + AI 模型构建的智能文献阅读与分析工具合集，旨在帮助科研人员实现从文献管理、PDF 解析、AI 辅助阅读到综述撰写的一体化工作流程。

本项目包含以下核心组件：

### 1. Codex Zotero Bridge

一个用于连接 Codex 与 Zotero 的本地桥接插件。

该插件需要手动安装到 Zotero 中，使 Codex 能够在 Zotero 保持运行的情况下，对本地文献库进行访问和操作，包括论文条目读取、标签管理、笔记创建、附件管理等功能。

### 2. Zotero 操作 Skill 集合

基于 Codex Zotero Bridge 开发的一系列自动化 skill，用于实现 AI 控制 Zotero 的科研工作流，例如：

- 自动整理文献条目；
- 添加标签与分类；
- 生成论文阅读笔记；
- 管理文献集合；
- 辅助构建个人科研知识库。

### 3. MinerU PDF 解析与 AI 阅读工作流

基于 MinerU API 实现 Zotero PDF 文献的自动解析。

该模块可以：

- 将 Zotero 中的 PDF 论文转换为 Markdown 和 HTML 格式；
- 自动保留论文中的文本、公式和图片信息；
- 将转换后的 Markdown/HTML 文件重新关联到 Zotero 文献条目下。

解析后的 Markdown 文档可以进一步用于 AI 辅助分析，包括：

- 单篇论文深度解读；
- 图文结合的论文总结；
- 多篇论文对比分析；
- 文献综述框架生成；
- 研究方向与技术路线梳理。

该项目希望构建一个面向科研人员的 AI 增强型文献管理与知识发现工作流，将传统 Zotero 文献管理工具与现代 AI Agent 能力结合，提高文献阅读、整理和科研写作效率。

## English Introduction

This project provides an AI-powered literature management and analysis workflow based on Codex, Zotero, and large language models. It aims to integrate reference management, PDF parsing, AI-assisted reading, and literature review generation into a unified research workflow.

The project consists of three main components:

### 1. Codex Zotero Bridge

A local bridge plugin that connects Codex with Zotero.

The plugin should be manually installed into Zotero. Once installed, it enables Codex to interact with the Zotero library while Zotero remains running, including:

- Reading Zotero items and metadata;
- Managing tags and collections;
- Creating and updating notes;
- Managing attachments and related files.

### 2. Codex Skills for Zotero Automation

A collection of Codex-based skills built on top of Codex Zotero Bridge, enabling AI-assisted Zotero workflows, including:

- Automated literature organization;
- Paper classification and tagging;
- AI-generated reading notes;
- Reference library management;
- Personal research knowledge base construction.

### 3. MinerU-based PDF Parsing and AI Literature Analysis Workflow

A PDF processing workflow based on the MinerU API. A free API key needs to be obtained from the official [MinerU website](https://mineru.net/).

This module enables automatic conversion of Zotero PDF papers into Markdown and HTML formats while preserving:

- Text content;
- Figures;
- Mathematical formulas;
- Document structure.

The generated Markdown/HTML files can then be re-linked to the corresponding Zotero items.

With AI models, the converted documents can be further analyzed for:

- In-depth single-paper interpretation;
- Figure-aware literature understanding;
- Multi-paper comparative analysis;
- Literature review generation;
- Research trend and methodology analysis.

This project aims to build an AI-enhanced research literature workflow, combining Zotero's powerful reference management capabilities with AI Agent technologies to improve the efficiency of literature reading, organization, knowledge discovery, and scientific writing.

## Repository Contents

一个简洁的 GitHub 分享包，包含两个 Codex skills 和一个本地 Zotero bridge 插件。

## 包含内容

```text
skills/
  zotero-use/              # Codex 操作 Zotero、检索文献、写 Word 引文
  zotero-mineru-md-html/   # Zotero PDF -> MinerU Markdown/HTML -> 挂回 Zotero
zotero-plugin/             # Codex Zotero Bridge Zotero 插件源码
python/
  codex_zotero_bridge_client.py
examples/
  codex_zotero_bridge_config.example.json
build-xpi.ps1
requirements.txt
```

## 能实现什么

- Codex 优先通过本地 Codex Zotero Bridge 读取/更新 Zotero 条目。
- 支持更新 Zotero 字段、Extra、标签。
- 支持添加 Zotero 子笔记。
- 支持把本地 Markdown/HTML/PDF 作为 Zotero 子附件链接或导入。
- 支持用 MinerU 将 Zotero PDF 批量转换为 `full.md` 和 `full.html`，再挂回 Zotero。
- 支持用 Pyzotero CLI 或 Zotero MCP 作为搜索/全文读取的补充路径。

## 安装

### 1. 安装两个 skills

把下面两个目录复制到你的 Codex skills 目录：

```text
skills/zotero-use
skills/zotero-mineru-md-html
```

例如：

```powershell
Copy-Item -Recurse .\skills\zotero-use "$env:USERPROFILE\.codex\skills\zotero-use"
Copy-Item -Recurse .\skills\zotero-mineru-md-html "$env:USERPROFILE\.codex\skills\zotero-mineru-md-html"
```

然后重启 Codex 或重新加载 skills。

### 2. 配置并安装 Zotero Bridge 插件

编辑：

```text
zotero-plugin/bridge.js
```

把：

```js
token: "CHANGE_ME_TO_A_LONG_RANDOM_LOCAL_TOKEN"
```

改成你自己的长随机 token。不要把真实 token 提交到 GitHub。

打包：

```powershell
.\build-xpi.ps1
```

在 Zotero 中安装：

```text
Tools -> Add-ons -> Install Add-on From File...
```

选择 `dist/codex-zotero-bridge.xpi`，然后重启 Zotero。

### 3. 创建本地 bridge 配置

复制：

```text
examples/codex_zotero_bridge_config.example.json
```

到你的本地工作目录，并改成真实 token：

```json
{
  "base_url": "http://127.0.0.1:23119/codex-zotero-bridge",
  "token": "YOUR_LOCAL_TOKEN"
}
```

不要提交真实配置。

## 测试 bridge

```powershell
python .\python\codex_zotero_bridge_client.py --config path\to\codex_zotero_bridge_config.json
```

或在脚本中：

```python
from codex_zotero_bridge_client import ZoteroBridge
bridge = ZoteroBridge("path/to/codex_zotero_bridge_config.json")
print(bridge.ping())
```

## MinerU 转换

先安装依赖：

```powershell
pip install -r requirements.txt
```

设置 MinerU token：

```powershell
$env:MINERU_API_TOKEN = "YOUR_MINERU_TOKEN"
```

设置 Zotero local API 地址，把 `<USER_ID>` 换成使用者自己的 Zotero local API 用户 ID：

```powershell
$env:ZOTERO_API = "http://localhost:23119/api/users/<USER_ID>"
```

先 dry-run：

```powershell
python .\skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --bridge-config path\to\codex_zotero_bridge_config.json --dry-run
```

正式转换：

```powershell
python .\skills\zotero-mineru-md-html\scripts\zotero_mineru_convert.py --root . --collection-key COLLECTION_KEY --bridge-config path\to\codex_zotero_bridge_config.json
```

## 安全

- 不要提交真实 token。
- 不要提交 Zotero 数据库、PDF、MinerU 输出全文。
- MinerU 会上传 PDF 到外部服务，使用前确认你有权限上传。
- 批量写 Zotero 前先 dry-run。
