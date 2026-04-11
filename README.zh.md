<div align="center">

  <h1>ComfyUI Skill CLI</h1>

  <p><strong>面向 AI Agent 的 ComfyUI 工作流命令行工具</strong></p>

  <p>
    任何能执行 Shell 命令的 AI Agent（Claude Code、Codex、OpenClaw 等）都可以通过这个 CLI 调用 ComfyUI。
  </p>

  <p>
    <a href="https://pypi.org/project/comfyui-skill-cli/"><img src="https://img.shields.io/pypi/v/comfyui-skill-cli?style=flat&color=4F46E5&logo=pypi&logoColor=white" alt="PyPI"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=10B981" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3B82F6&style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/stargazers"><img src="https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=EAB308&logo=github" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#安装">安装</a> ·
    <a href="#快速开始">快速开始</a> ·
    <a href="#命令">命令</a> ·
    <a href="#ai-agent-使用">AI Agent 使用</a>
  </p>

  <p>
    <a href="./README.md">English</a> ·
    <strong>简体中文</strong> ·
    <a href="./README.zh-TW.md">繁體中文</a> ·
    <a href="./README.ja.md">日本語</a>
  </p>

</div>

---

## 为什么选 comfyui-skill？

| 能力 | 价值 |
|------|------|
| **Agent 原生** | 结构化 JSON 输出，管道友好，专为 AI Agent 调用优化 |
| **零配置** | 从当前目录读取 `config.json` 和 `data/`，开箱即用 |
| **全生命周期** | 发现、导入、执行、取消、管理工作流和依赖，一个工具搞定 |
| **多服务器** | 同时管理多台 ComfyUI 实例，按需分发任务到不同算力 |
| **错误引导** | 常见失败（显存不足、未授权、模型缺失）自动返回可操作的提示 |

## 安装

```bash
pipx install comfyui-skill-cli
```

或用 pip：

```bash
pip install comfyui-skill-cli
```

### 更新

```bash
pipx upgrade comfyui-skill-cli
```

### 开发模式

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

## 快速开始

```bash
# 1. 进入 ComfyUI Skills 项目目录
cd /path/to/your-skills-project

# 2. 检查服务器状态
comfyui-skill server status

# 3. 查看可用工作流
comfyui-skill list

# 4. 执行工作流
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

所有命令均支持 `--json` 输出结构化数据。

## ID 约定

工作流使用 `<server_id>/<workflow_id>` 格式：

```bash
comfyui-skill run local/txt2img          # 指定服务器
comfyui-skill run txt2img                # 使用默认服务器
comfyui-skill run txt2img -s my_server   # 通过 --server 指定
```

## 命令

### 工作流发现与执行

| 命令 | 说明 |
|------|------|
| `comfyui-skill list` | 列出所有可用工作流及参数 |
| `comfyui-skill info <id>` | 查看工作流详情和参数 schema |
| `comfyui-skill run <id> --args '{...}'` | 执行工作流（阻塞） |
| `comfyui-skill submit <id> --args '{...}'` | 提交工作流（非阻塞） |
| `comfyui-skill status <prompt_id>` | 查询执行状态 |
| `comfyui-skill cancel <prompt_id>` | 取消运行中或排队中的任务 |
| `comfyui-skill upload <file>` | 上传文件到 ComfyUI 供工作流使用 |
| `comfyui-skill upload --from-output <prompt_id>` | 将上次运行的输出作为下一个工作流的输入 |

### 队列与资源管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill queue list` | 查看运行中和排队中的任务 |
| `comfyui-skill queue clear` | 清空排队中的任务 |
| `comfyui-skill queue delete <prompt_id>...` | 从队列删除指定任务 |
| `comfyui-skill free` | 释放 GPU 显存并卸载模型 |
| `comfyui-skill free --models` | 仅卸载模型 |
| `comfyui-skill free --memory` | 仅释放缓存 |

### 模型发现

| 命令 | 说明 |
|------|------|
| `comfyui-skill models list` | 列出所有模型文件夹 |
| `comfyui-skill models list <folder>` | 列出指定文件夹中的模型（如 `checkpoints`、`loras`） |

### 工作流管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill workflow import <path>` | 导入工作流（自动检测格式、自动生成 schema） |
| `comfyui-skill workflow import --from-server` | 从 ComfyUI 服务器导入 |
| `comfyui-skill workflow enable <id>` | 启用工作流 |
| `comfyui-skill workflow disable <id>` | 禁用工作流 |
| `comfyui-skill workflow delete <id>` | 删除工作流 |

### 服务器管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill server list` | 列出所有已配置的服务器 |
| `comfyui-skill server status` | 检查 ComfyUI 服务器是否在线 |
| `comfyui-skill server add --id <id> --url <url>` | 添加新服务器 |
| `comfyui-skill server enable/disable <id>` | 启用/禁用服务器 |
| `comfyui-skill server remove <id>` | 移除服务器 |

### 依赖管理

| 命令 | 说明 |
|------|------|
| `comfyui-skill deps check <id>` | 检查缺失的自定义节点和模型 |
| `comfyui-skill deps install <id> --all` | 自动检测并安装所有缺失依赖 |
| `comfyui-skill deps install <id> --repos '[...]'` | 安装指定的自定义节点 |
| `comfyui-skill deps install <id> --models` | 通过 Manager 安装缺失模型 |

### 配置与历史

| 命令 | 说明 |
|------|------|
| `comfyui-skill config export --output <path>` | 导出配置和工作流 |
| `comfyui-skill config import <path>` | 导入配置（支持 `--dry-run`） |
| `comfyui-skill history list <id>` | 查看执行历史 |
| `comfyui-skill history show <id> <run_id>` | 查看单次运行详情 |

### 全局选项

| 选项 | 说明 |
|------|------|
| `--json, -j` | 强制 JSON 输出 |
| `--output-format` | 输出格式：`text`、`json`、`stream-json` |
| `--server, -s` | 指定服务器 ID |
| `--dir, -d` | 指定数据目录（默认：当前目录） |
| `--verbose, -v` | 详细输出 |
| `--no-update-check` | 跳过自动更新检查 |

### 输出模式

| 模式 | 场景 | 格式 |
|------|------|------|
| Text | 终端 TTY | Rich 表格和进度条 |
| JSON | 管道或 `--json` | 单次 JSON 结果 |
| Stream JSON | `--output-format stream-json` | 实时 NDJSON 事件流 |
| 错误 | 始终 | stderr |

## AI Agent 使用

这个 CLI 专为 `SKILL.md` 调用场景设计。Agent 的典型流程：

```bash
comfyui-skill server status --json                    # 1. 确认服务器
comfyui-skill list --json                             # 2. 发现工作流
comfyui-skill info local/txt2img --json               # 3. 查看参数
comfyui-skill run local/txt2img --args '{...}' --json # 4. 执行
```

### 工作流串联（多步管线）

```bash
# 执行第一个工作流
comfyui-skill run local/txt2img --args '{"prompt": "a cat"}' --json

# 将输出串联到下一个工作流
comfyui-skill upload --from-output <prompt_id> --json
comfyui-skill run local/upscale --args '{"image": "<uploaded_name>"}' --json
```

### 导入并验证

```bash
comfyui-skill workflow import ./workflow.json --check-deps --json
comfyui-skill deps install local/my-workflow --all --json
```

## 贡献

欢迎贡献！请阅读主仓库的 [Contributing Guide](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/blob/main/CONTRIBUTING.md) 了解设计原则和 PR 流程。

## 相关资源

<<<<<<< HEAD
- [ComfyUI Skills OpenClaw](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) — 主仓库（Skills 定义）
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — 本 CLI 调度的后端
- [Typer](https://typer.tiangolo.com/) — 本项目使用的 CLI 框架
=======
基于 [Typer](https://typer.tiangolo.com/) 构建，与 [comfy-cli](https://github.com/Comfy-Org/comfy-cli) 使用相同框架。未来计划作为 `comfy skills` 子命令集成。
>>>>>>> 246e194 (docs: add zh-TW and ja readmes)
