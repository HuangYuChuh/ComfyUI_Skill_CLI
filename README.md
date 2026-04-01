# ComfyUI Skill CLI

[中文版](./README.zh.md) | [English](./README.md)

Agent-friendly command-line tool for managing and executing [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow skills. Any AI agent that can run shell commands (Claude, Codex, OpenClaw, etc.) can use ComfyUI through this CLI.

[Install](#install) · [Quick Start](#quick-start) · [Commands](#commands) · [For AI Agents](#for-ai-agents)

## Why comfyui-skill?

- **Agent-native** — structured JSON output, pipe-friendly, designed for AI agents to call
- **Zero config** — reads `config.json` and `data/` from the current directory, no setup needed
- **Full lifecycle** — discover, import, execute, manage workflows and dependencies in one tool
- **Multi-server** — manage multiple ComfyUI instances, route jobs to different hardware

## Install

```bash
pipx install comfyui-skill-cli
```

### Development Mode

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

The `-e` flag (editable) links directly to your local source — any code change is reflected instantly.

### Update

```bash
pipx upgrade comfyui-skill-cli
```

## Quick Start

```bash
# 1. Go to your ComfyUI Skills project directory
cd /path/to/your-skills-project

# 2. Check server status
comfyui-skill server status

# 3. List available workflows
comfyui-skill list

# 4. Execute a workflow
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

Every command supports `--json` for structured output.

## ID Convention

This CLI uses two types of IDs:

| Notation | Meaning | Example |
|----------|---------|---------|
| `<workflow_id>` | Workflow identifier, format: `server_id/workflow_name` | `local/txt2img` |
| `<server_id>` | Server identifier | `local`, `remote-a100` |

When `<workflow_id>` omits the server prefix, the default server is used:

```bash
comfyui-skill run local/txt2img          # explicit server
comfyui-skill run txt2img                # uses default server
comfyui-skill run txt2img -s my_server   # override server via flag
```

## Commands

### Workflow Discovery & Execution

| Command | Description |
|---------|-------------|
| `comfyui-skill list` | List all available workflows with parameters |
| `comfyui-skill info <workflow_id>` | Show workflow details and parameter schema |
| `comfyui-skill run <workflow_id> --args '{...}'` | Execute a workflow (blocking, returns images) |
| `comfyui-skill submit <workflow_id> --args '{...}'` | Submit a workflow (non-blocking, returns prompt_id) |
| `comfyui-skill status <prompt_id>` | Check execution status and download results |
| `comfyui-skill upload <image_path>` | Upload image to ComfyUI for use in workflows |

### Workflow Management

| Command | Description |
|---------|-------------|
| `comfyui-skill workflow import <json_path>` | Import workflow from local JSON (auto-detect format, auto-convert, auto-generate schema) |
| `comfyui-skill workflow import --from-server` | Import workflows from ComfyUI server userdata |
| `comfyui-skill workflow enable <workflow_id>` | Enable a workflow |
| `comfyui-skill workflow disable <workflow_id>` | Disable a workflow |
| `comfyui-skill workflow delete <workflow_id>` | Delete a workflow |

### Server Management

| Command | Description |
|---------|-------------|
| `comfyui-skill server list` | List all configured servers |
| `comfyui-skill server status [<server_id>]` | Check if ComfyUI server is online |
| `comfyui-skill server add --id <server_id> --url <url>` | Add a new server |
| `comfyui-skill server enable <server_id>` | Enable a server |
| `comfyui-skill server disable <server_id>` | Disable a server |
| `comfyui-skill server remove <server_id>` | Remove a server |

### Dependency Management

| Command | Description |
|---------|-------------|
| `comfyui-skill deps check <workflow_id>` | Check missing custom nodes and models |
| `comfyui-skill deps install <workflow_id> --repos '[...]'` | Install missing custom nodes via Manager |
| `comfyui-skill deps install <workflow_id> --models` | Install missing models via Manager |
| `comfyui-skill deps install <workflow_id> --all` | Auto-detect and install all missing deps |

### Configuration Transfer

| Command | Description |
|---------|-------------|
| `comfyui-skill config export --output <path>` | Export config and workflows as bundle |
| `comfyui-skill config import <path>` | Import config bundle (supports --dry-run) |

### Execution History

| Command | Description |
|---------|-------------|
| `comfyui-skill history list <workflow_id>` | List execution history for a workflow |
| `comfyui-skill history show <workflow_id> <run_id>` | Show details of a specific run |

### Global Options

| Option | Description |
|--------|-------------|
| `--json, -j` | Force JSON output |
| `--server, -s <server_id>` | Specify server ID |
| `--dir, -d <path>` | Specify data directory (default: current directory) |
| `--verbose, -v` | Verbose output |

### Output Modes

- **TTY** → Rich tables and progress bars (human-friendly)
- **Pipe / `--json`** → Structured JSON (agent-friendly)
- **Errors** → Always stderr

## For AI Agents

This CLI is designed to be called from `SKILL.md` definitions:

```bash
# Typical agent workflow
comfyui-skill server status --json                        # 1. verify server is online
comfyui-skill list --json                                 # 2. discover available workflows
comfyui-skill info local/txt2img --json                   # 3. check required parameters
comfyui-skill run local/txt2img --args '{...}' --json     # 4. execute
```

### Import a new workflow

```bash
# Import and check dependencies in one step
comfyui-skill workflow import ./workflow.json --check-deps --json

# Install missing dependencies
comfyui-skill deps install local/my-workflow --all --json
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Server connection failed |
| 4 | Resource not found |
| 5 | Execution failed |
| 6 | Timeout |

## Compatibility

Built with [Typer](https://typer.tiangolo.com/), the same framework as [comfy-cli](https://github.com/Comfy-Org/comfy-cli). Designed to be integrated as a `comfy skills` subcommand in the future.