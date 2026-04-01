# CLI 功能开发路线图

本文档记录 ComfyUI Skill CLI 的完整功能规划、优先级和实现状态。

## 已实现 ✅

| 命令 | 说明 | 测试状态 |
|------|------|---------|
| `list` | 列出所有可用工作流及参数 | ✅ 已测通 |
| `info <id>` | 查看工作流详情和参数 schema | ✅ 已测通 |
| `run <id> --args '{...}'` | 阻塞执行工作流（等待完成后返回图片路径） | ✅ 已测通 |
| `submit <id> --args '{...}'` | 非阻塞提交工作流（立即返回 prompt_id） | ✅ 已测通 |
| `status <prompt_id>` | 查询执行状态 | ✅ 已测通 |
| `server list` | 列出已配置的服务器 | ✅ 已测通 |
| `server status [server_id]` | 检查服务器是否在线 | ✅ 已测通 |
| `deps check <id>` | 检查工作流缺失的自定义节点和模型 | ✅ 已测通 |
| `deps install <id> --repos '[...]'` | 通过 ComfyUI Manager 安装自定义节点 | ✅ 已实现 |

---

## P0 — Agent 核心流程必需

这些功能直接影响 Agent 的完整使用流程：用户给一个工作流 JSON → 自动导入 → 检查依赖 → 安装 → 执行。

### `workflow import <json_path>` — 导入本地工作流

从本地 JSON 文件导入工作流到项目中。自动检测格式（editor/API），自动转换为 API 格式，自动生成 schema。

```bash
# 导入单个工作流文件
comfyui-skill workflow import ./my-workflow.json

# 指定目标服务器和工作流 ID
comfyui-skill workflow import ./my-workflow.json --server local --name my-workflow

# 导入后自动检查依赖
comfyui-skill workflow import ./my-workflow.json --check-deps
```

**实现来源**: `ui/workflow_format.py` (格式检测 + 转换 + schema 生成)、`ui/workflow_import.py` (导入逻辑)

**核心逻辑**:
1. 读取 JSON 文件
2. 检测是 editor 格式还是 API 格式
3. 如果是 editor 格式，自动转换为 API 格式
4. 自动生成 schema.json（参数映射）
5. 写入 `data/<server_id>/<workflow_id>/workflow.json` + `schema.json`

**状态**: ⬜ 待实现

---

### `workflow import --from-server [server_id]` — 从 ComfyUI 服务器导入

从 ComfyUI 服务器的 userdata 中批量导入工作流。

```bash
# 预览可导入的工作流列表
comfyui-skill workflow import --from-server local --preview

# 导入所有工作流
comfyui-skill workflow import --from-server local

# 导入指定工作流
comfyui-skill workflow import --from-server local --name "my-workflow"
```

**实现来源**: `ui/comfyui_userdata.py` (读取 /userdata)、`ui/workflow_import.py` (批量导入)

**状态**: ⬜ 待实现

---

### `deps install --models` — 安装缺失模型

当前 `deps install` 只支持安装自定义节点，还需要支持通过 ComfyUI Manager 下载缺失模型。

```bash
# 自动安装缺失的节点和模型
comfyui-skill deps install <id> --all

# 只安装模型
comfyui-skill deps install <id> --models
```

**实现来源**: `ui/dependency_installer.py` 的 `_install_single_model()` 方法

**状态**: ⬜ 待实现

---

### `upload <image_path>` — 上传图片到 ComfyUI

部分工作流需要输入图片（如图生图、蛋糕白底图等），Agent 需要先上传图片再执行。

```bash
# 上传图片到指定服务器
comfyui-skill upload ./cake.png
comfyui-skill upload ./cake.png --server remote
```

返回上传后的文件名，可直接作为工作流参数使用。

**实现来源**: Web API `POST /api/servers/{sid}/upload/image`

**状态**: ⬜ 待实现

---

## P1 — 服务器和配置管理

无 Web UI 环境下（SSH 远程、headless 服务器）的管理能力。

### `server add` — 添加服务器

```bash
comfyui-skill server add --id remote --name "Remote GPU" --url http://10.0.0.1:8188
comfyui-skill server add --id remote --url http://10.0.0.1:8188 --output-dir ./outputs/remote
```

**实现来源**: `scripts/server_manager.py` 的 `add` 命令

**状态**: ⬜ 待实现

---

### `server enable/disable` — 启用/禁用服务器

```bash
comfyui-skill server enable remote
comfyui-skill server disable remote
```

**实现来源**: `scripts/server_manager.py`

**状态**: ⬜ 待实现

---

### `server remove` — 移除服务器

```bash
comfyui-skill server remove remote
```

**实现来源**: `scripts/server_manager.py`

**状态**: ⬜ 待实现

---

### `config export` — 导出配置

```bash
comfyui-skill config export --output ./backup.json
comfyui-skill config export --output ./backup.json --portable-only
```

**实现来源**: `scripts/transfer_manager.py` + `shared/transfer_bundle.py`

**状态**: ⬜ 待实现

---

### `config import` — 导入配置

```bash
# 预览变更
comfyui-skill config import ./backup.json --dry-run

# 执行导入
comfyui-skill config import ./backup.json

# 同时应用环境配置
comfyui-skill config import ./backup.json --apply-environment
```

**实现来源**: `scripts/transfer_manager.py` + `shared/transfer_bundle.py`

**状态**: ⬜ 待实现

---

## P2 — 历史和工作流管理

### `history list <skill_id>` — 查看执行历史

```bash
comfyui-skill history list local/txt2img
comfyui-skill history list local/txt2img --limit 10
```

**实现来源**: `shared/execution_history.py`

**状态**: ⬜ 待实现

---

### `history show <skill_id> <run_id>` — 查看运行详情

```bash
comfyui-skill history show local/txt2img abc123
```

**实现来源**: `shared/execution_history.py`

**状态**: ⬜ 待实现

---

### `workflow enable/disable <id>` — 启用/禁用工作流

```bash
comfyui-skill workflow enable local/txt2img
comfyui-skill workflow disable local/txt2img
```

**状态**: ⬜ 待实现

---

### `workflow delete <id>` — 删除工作流

```bash
comfyui-skill workflow delete local/txt2img
```

**状态**: ⬜ 待实现

---

## P3 — 增强

### `deps install` 多策略回退

当前只走 Manager Queue API。需要增加回退策略：
1. Manager Queue API（当前）
2. cm-cli.py 命令行
3. 直接 git clone 到 custom_nodes/

**实现来源**: `ui/dependency_installer.py` 的 `_try_cm_cli()` 和 `_try_git_clone()`

**状态**: ⬜ 待实现

---

### 参数验证和类型强制

`run` 命令增加参数类型校验（int/float/boolean/string 自动转换），与主项目的 `validate_and_coerce_params()` 对齐。

**实现来源**: `scripts/comfyui_client.py` 的 `validate_and_coerce_params()`

**状态**: ⬜ 待实现

---

### 完整的 Agent 工作流一键命令

将 P0 的多个步骤串联成一键命令：

```bash
# 从外部 JSON 一键导入 → 检查依赖 → 安装 → 就绪
comfyui-skill workflow setup ./downloaded-workflow.json
```

等价于依次执行：
1. `workflow import ./downloaded-workflow.json` — 导入并转格式
2. `deps check <id>` — 检查缺失依赖
3. `deps install <id>` — 安装缺失的节点和模型
4. 输出就绪状态

**状态**: ⬜ 待实现（依赖 P0 全部完成）

---

## 开发约定

- 所有命令支持 `--json` 输出
- TTY 模式使用 Rich 表格展示，保持可读性
- 错误输出到 stderr，正常输出到 stdout
- 命令实现放在 `comfyui_skills_cli/commands/` 下对应文件
- HTTP 通信统一走 `client.py` 的 `ComfyUIClient`
- 配置读写统一走 `config.py`
- 每个命令完成后更新 README 的命令列表
