<div align="center">

  <h1>ComfyUI Skill CLI</h1>

  <p><strong>面向 AI Agent 的 ComfyUI 工作流程命令列工具</strong></p>

  <p>
    任何能執行 Shell 指令的 AI Agent（Claude Code、Codex、OpenClaw 等）都可以透過這個 CLI 呼叫 ComfyUI。
  </p>

  <p>
    <a href="https://pypi.org/project/comfyui-skill-cli/"><img src="https://img.shields.io/pypi/v/comfyui-skill-cli?style=flat&color=4F46E5&logo=pypi&logoColor=white" alt="PyPI"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=10B981" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3B82F6&style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/stargazers"><img src="https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=EAB308&logo=github" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#安裝">安裝</a> ·
    <a href="#快速開始">快速開始</a> ·
    <a href="#命令">命令</a> ·
    <a href="#ai-agent-使用">AI Agent 使用</a>
  </p>

  <p>
    <a href="./README.md">English</a> ·
    <a href="./README.zh.md">简体中文</a> ·
    <strong>繁體中文</strong> ·
    <a href="./README.ja.md">日本語</a>
  </p>

</div>

---

## 為什麼選擇 comfyui-skill？

| 能力 | 價值 |
|------|------|
| **Agent 原生** | 結構化 JSON 輸出、適合串接管線，專為 AI Agent 呼叫最佳化 |
| **零設定** | 從目前目錄讀取 `config.json` 和 `data/`，幾乎開箱即用 |
| **完整生命週期** | 發現、匯入、執行、取消，以及管理工作流程與依賴，全都整合在同一個工具裡 |
| **多伺服器** | 同時管理多台 ComfyUI 實例，依需求把任務分派到不同硬體 |
| **錯誤引導** | 常見失敗（顯存不足、未授權、模型缺失）都會回傳可操作的提示 |

## 安裝

```bash
pipx install comfyui-skill-cli
```

或使用 pip：

```bash
pip install comfyui-skill-cli
```

### 更新

```bash
pipx upgrade comfyui-skill-cli
```

### 開發模式

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

## 快速開始

```bash
# 1. 進入你的 ComfyUI Skills 專案目錄
cd /path/to/your-skills-project

# 2. 檢查伺服器狀態
comfyui-skill server status

# 3. 查看可用工作流程
comfyui-skill list

# 4. 執行工作流程
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

所有命令都支援 `--json`，可輸出結構化資料。

## ID 慣例

工作流程使用 `<server_id>/<workflow_id>` 格式：

```bash
comfyui-skill run local/txt2img          # 明確指定伺服器
comfyui-skill run txt2img                # 使用預設伺服器
comfyui-skill run txt2img -s my_server   # 透過 --server 覆寫
```

## 命令

### 工作流程發現與執行

| 命令 | 說明 |
|------|------|
| `comfyui-skill list` | 列出所有可用工作流程與參數 |
| `comfyui-skill info <id>` | 查看工作流程詳情與參數 schema |
| `comfyui-skill run <id> --args '{...}'` | 執行工作流程（阻塞） |
| `comfyui-skill submit <id> --args '{...}'` | 提交工作流程（非阻塞） |
| `comfyui-skill status <prompt_id>` | 查詢執行狀態並下載結果 |
| `comfyui-skill cancel <prompt_id>` | 取消執行中或排隊中的任務 |
| `comfyui-skill upload <file>` | 上傳檔案到 ComfyUI，供工作流程使用 |
| `comfyui-skill upload --from-output <prompt_id>` | 將前一次執行的輸出串接成下一個工作流程的輸入 |

### 佇列與資源管理

| 命令 | 說明 |
|------|------|
| `comfyui-skill queue list` | 查看執行中與排隊中的任務 |
| `comfyui-skill queue clear` | 清空所有排隊中的任務 |
| `comfyui-skill queue delete <prompt_id>...` | 從佇列中刪除指定任務 |
| `comfyui-skill free` | 釋放 GPU 記憶體並卸載模型 |
| `comfyui-skill free --models` | 只卸載模型 |
| `comfyui-skill free --memory` | 只釋放快取記憶體 |

### 模型探索

| 命令 | 說明 |
|------|------|
| `comfyui-skill models list` | 列出所有可用模型資料夾 |
| `comfyui-skill models list <folder>` | 列出指定資料夾中的模型（例如 `checkpoints`、`loras`） |

### 工作流程管理

| 命令 | 說明 |
|------|------|
| `comfyui-skill workflow import <path>` | 匯入工作流程（自動偵測格式、自動產生 schema） |
| `comfyui-skill workflow import --from-server` | 從 ComfyUI 伺服器匯入 |
| `comfyui-skill workflow enable <id>` | 啟用工作流程 |
| `comfyui-skill workflow disable <id>` | 停用工作流程 |
| `comfyui-skill workflow delete <id>` | 刪除工作流程 |

### 伺服器管理

| 命令 | 說明 |
|------|------|
| `comfyui-skill server list` | 列出所有已設定的伺服器 |
| `comfyui-skill server status` | 檢查 ComfyUI 伺服器是否在線 |
| `comfyui-skill server add --id <id> --url <url>` | 新增伺服器 |
| `comfyui-skill server enable/disable <id>` | 啟用或停用伺服器 |
| `comfyui-skill server remove <id>` | 移除伺服器 |

### 依賴管理

| 命令 | 說明 |
|------|------|
| `comfyui-skill deps check <id>` | 檢查缺失的自訂節點與模型 |
| `comfyui-skill deps install <id> --all` | 自動偵測並安裝所有缺失依賴 |
| `comfyui-skill deps install <id> --repos '[...]'` | 安裝指定的自訂節點 |
| `comfyui-skill deps install <id> --models` | 透過 Manager 安裝缺失模型 |

### 設定與歷史

| 命令 | 說明 |
|------|------|
| `comfyui-skill config export --output <path>` | 匯出設定與工作流程 |
| `comfyui-skill config import <path>` | 匯入設定（支援 `--dry-run`） |
| `comfyui-skill history list <id>` | 查看執行歷史 |
| `comfyui-skill history show <id> <run_id>` | 查看單次執行詳情 |

### 全域選項

| 選項 | 說明 |
|------|------|
| `--json, -j` | 強制輸出 JSON |
| `--output-format` | 輸出格式：`text`、`json`、`stream-json` |
| `--server, -s` | 指定伺服器 ID |
| `--dir, -d` | 指定資料目錄（預設：目前目錄） |
| `--verbose, -v` | 顯示詳細輸出 |
| `--no-update-check` | 跳過自動更新檢查 |

### 輸出模式

| 模式 | 場景 | 格式 |
|------|------|------|
| Text | TTY 終端機 | Rich 表格與進度條 |
| JSON | 管線或 `--json` | 單次 JSON 結果 |
| Stream JSON | `--output-format stream-json` | 即時 NDJSON 事件流 |
| 錯誤 | 一律 | stderr |

## AI Agent 使用

這個 CLI 專為 `SKILL.md` 的呼叫場景設計。Agent 的典型流程如下：

```bash
comfyui-skill server status --json                    # 1. 確認伺服器
comfyui-skill list --json                             # 2. 發現工作流程
comfyui-skill info local/txt2img --json               # 3. 查看參數
comfyui-skill run local/txt2img --args '{...}' --json # 4. 執行
```

### 工作流程串接（多步驟管線）

```bash
# 執行第一個工作流程
comfyui-skill run local/txt2img --args '{"prompt": "a cat"}' --json

# 將輸出串接到下一個工作流程
comfyui-skill upload --from-output <prompt_id> --json
comfyui-skill run local/upscale --args '{"image": "<uploaded_name>"}' --json
```

### 匯入並驗證

```bash
comfyui-skill workflow import ./workflow.json --check-deps --json
comfyui-skill deps install local/my-workflow --all --json
```

## 貢獻

歡迎貢獻！請先閱讀主倉庫中的 [Contributing Guide](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/blob/main/CONTRIBUTING.md)，了解設計原則與 PR 流程。

## 相關資源

- [ComfyUI Skills OpenClaw](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) — Skills 定義主倉庫
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — 本 CLI 所調度的後端
- [Typer](https://typer.tiangolo.com/) — 本專案使用的 CLI 框架
