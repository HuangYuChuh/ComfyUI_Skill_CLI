# ComfyUI Skill CLI

[中文版](./README.zh.md) | [English](./README.md)

面向 AI Agent 的 ComfyUI 工作流命令行工具。任何能执行 Shell 命令的 AI Agent（Claude、Codex、OpenClaw 等）都可以通过这个 CLI 调用 ComfyUI。

[安装](#安装) · [快速开始](#快速开始) · [命令](#命令) · [AI Agent 使用](#ai-agent-使用)

## 为什么选 comfyui-skill？

- **为 Agent 原生设计** — 结构化 JSON 输出，管道友好，专为 AI Agent 调用优化
- **零配置** — 从当前目录读取 `config.json` 和 `data/`，开箱即用
- **全生命周期管理** — 发现、导入、执行、管理工作流和依赖，一个工具搞定
- **多服务器** — 同时管理多台 ComfyUI 实例，按需分发任务到不同算力

## 安装

```bash
pipx install comfyui-skill-cli
```

### 开发模式

如果你想修改 CLI 源码并让改动立刻生效：

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

`-e`（editable）会直接链接到本地源码，改完代码无需重新安装。

## 快速开始

```bash
# 1. 进入 ComfyUI Skills 项目目录
cd /path/to/your-skills-project

# 2. 检查服务器状态
comfyui-skill server status

# 3. 查看可用的工作流
comfyui-skill list

# 4. 执行工作流
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

所有命令均支持 `--json` 输出结构化数据。

## 命令

### 工作流发现与执行

| 命令 | 说明 |
|------|------|
| `comfyui-skill list` | 列出所有可用工作流及参数 |
| `comfyui-skill info <id>` | 查看工作流详情和参数 schema |
| `comfyui-skill run <id> --args '{...}'` | 执行工作流（阻塞，等待完成返回图片路径） |
| `comfyui-skill submit <id> --args '{...}'` | 提交工作流（非阻塞，立即返回 prompt_id） |
| `comfyui-skill status <prompt-id>` | 查询执行状态，完成后下载结果 |
| `comfyui-skill upload <image>` | 上传图片到 ComfyUI 供工作流使用 |

### 工作流管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill workflow import <json>` | 从本地 JSON 导入工作流（自动检测格式、自动转换、自动生成 schema） |
| `comfyui-skill workflow import --from-server` | 从 ComfyUI 服务器 userdata 导入工作流 |
| `comfyui-skill workflow enable <id>` | 启用工作流 |
| `comfyui-skill workflow disable <id>` | 禁用工作流 |
| `comfyui-skill workflow delete <id>` | 删除工作流 |

### 服务器管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill server list` | 列出所有已配置的服务器 |
| `comfyui-skill server status [id]` | 检查 ComfyUI 服务器是否在线 |
| `comfyui-skill server add --id <id> --url <url>` | 添加新服务器 |
| `comfyui-skill server enable <id>` | 启用服务器 |
| `comfyui-skill server disable <id>` | 禁用服务器 |
| `comfyui-skill server remove <id>` | 移除服务器 |

### 依赖管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill deps check <id>` | 检查缺失的自定义节点和模型 |
| `comfyui-skill deps install <id> --repos '[...]'` | 通过 Manager 安装缺失的自定义节点 |
| `comfyui-skill deps install <id> --models` | 通过 Manager 安装缺失的模型 |
| `comfyui-skill deps install <id> --all` | 自动检测并安装所有缺失的依赖 |

### 配置迁移

| 命令 | 说明 |
|------|------|
| `comfyui-skill config export --output <path>` | 导出配置和工作流为 bundle |
| `comfyui-skill config import <path>` | 导入 bundle（支持 --dry-run 预览） |

### 执行历史

| 命令 | 说明 |
|------|------|
| `comfyui-skill history list <id>` | 查看工作流的执行历史 |
| `comfyui-skill history show <id> <run_id>` | 查看单次运行的详细信息 |

### 全局选项

| 选项 | 说明 |
|------|------|
| `--json, -j` | 强制 JSON 输出 |
| `--server, -s` | 指定服务器 ID |
| `--dir, -d` | 指定数据目录（默认：当前目录） |
| `--verbose, -v` | 详细输出 |

### Skill ID 格式

```bash
comfyui-skill run local/txt2img          # server_id/workflow_id
comfyui-skill run txt2img                # 使用默认服务器
comfyui-skill run txt2img -s my_server   # 指定服务器
```

### 输出模式

- **终端（TTY）** → Rich 表格 + 进度条（人类友好）
- **管道 / `--json`** → 结构化 JSON（Agent 友好）
- **错误** → 始终输出到 stderr

## AI Agent 使用

这个 CLI 专为 `SKILL.md` 调用场景设计：

```bash
# Agent 的典型调用流程
comfyui-skill server status --json          # 1. 确认服务器在线
comfyui-skill list --json                   # 2. 发现可用工作流
comfyui-skill info <id> --json              # 3. 查看参数要求
comfyui-skill run <id> --args '{...}' --json # 4. 执行
```

### 导入新工作流

```bash
# 导入并检查依赖
comfyui-skill workflow import ./workflow.json --check-deps --json

# 安装缺失的依赖
comfyui-skill deps install <id> --all --json
```

## 退出码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 参数无效 |
| 3 | 服务器连接失败 |
| 4 | 资源未找到 |
| 5 | 执行失败 |
| 6 | 超时 |

## 兼容性

基于 [Typer](https://typer.tiangolo.com/) 构建，与 [comfy-cli](https://github.com/Comfy-Org/comfy-cli) 使用相同框架。未来计划作为 `comfy skills` 子命令集成。

## License

MIT
