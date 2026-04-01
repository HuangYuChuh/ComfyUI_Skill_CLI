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

## Commands

### Workflow Discovery & Execution

| Command | Description |
|---------|-------------|
| `comfyui-skill list` | List all available skills with parameters |
| `comfyui-skill info <id>` | Show skill details and parameter schema |
| `comfyui-skill run <id> --args '{...}'` | Execute a skill (blocking, returns images) |
| `comfyui-skill submit <id> --args '{...}'` | Submit a skill (non-blocking, returns prompt_id) |
| `comfyui-skill status <prompt-id>` | Check execution status and download results |
| `comfyui-skill upload <image>` | Upload image to ComfyUI for use in workflows |

### Workflow Management

| Command | Description |
|---------|-------------|
| `comfyui-skill workflow import <json>` | Import workflow from local JSON (auto-detect format, auto-convert, auto-generate schema) |
| `comfyui-skill workflow import --from-server` | Import workflows from ComfyUI server userdata |
| `comfyui-skill workflow enable <id>` | Enable a workflow |
| `comfyui-skill workflow disable <id>` | Disable a workflow |
| `comfyui-skill workflow delete <id>` | Delete a workflow |

### Server Management

| Command | Description |
|---------|-------------|
| `comfyui-skill server list` | List all configured servers |
| `comfyui-skill server status [id]` | Check if ComfyUI server is online |
| `comfyui-skill server add --id <id> --url <url>` | Add a new server |
| `comfyui-skill server enable <id>` | Enable a server |
| `comfyui-skill server disable <id>` | Disable a server |
| `comfyui-skill server remove <id>` | Remove a server |

### Dependency Management

| Command | Description |
|---------|-------------|
| `comfyui-skill deps check <id>` | Check missing custom nodes and models |
| `comfyui-skill deps install <id> --repos '[...]'` | Install missing custom nodes via Manager |
| `comfyui-skill deps install <id> --models` | Install missing models via Manager |
| `comfyui-skill deps install <id> --all` | Auto-detect and install all missing deps |

### Configuration Transfer

| Command | Description |
|---------|-------------|
| `comfyui-skill config export --output <path>` | Export config and workflows as bundle |
| `comfyui-skill config import <path>` | Import config bundle (supports --dry-run) |

### Execution History

| Command | Description |
|---------|-------------|
| `comfyui-skill history list <id>` | List execution history for a skill |
| `comfyui-skill history show <id> <run_id>` | Show details of a specific run |

### Global Options

| Option | Description |
|--------|-------------|
| `--json, -j` | Force JSON output |
| `--server, -s` | Specify server ID |
| `--dir, -d` | Specify data directory (default: current directory) |
| `--verbose, -v` | Verbose output |

### Skill ID Format

```bash
comfyui-skill run local/txt2img          # server_id/workflow_id
comfyui-skill run txt2img                # uses default server
comfyui-skill run txt2img -s my_server   # explicit server
```

### Output Modes

- **TTY** → Rich tables and progress bars (human-friendly)
- **Pipe / `--json`** → Structured JSON (agent-friendly)
- **Errors** → Always stderr

## For AI Agents

This CLI is designed to be called from `SKILL.md` definitions:

```bash
# Typical agent workflow
comfyui-skill server status --json          # 1. verify server is online
comfyui-skill list --json                   # 2. discover available skills
comfyui-skill info <id> --json              # 3. check required parameters
comfyui-skill run <id> --args '{...}' --json # 4. execute
```

### Import a new workflow

```bash
# Import and check dependencies in one step
comfyui-skill workflow import ./workflow.json --check-deps --json

# Install missing dependencies
comfyui-skill deps install <id> --all --json
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

## License

MIT
