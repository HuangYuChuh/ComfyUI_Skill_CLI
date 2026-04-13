<div align="center">

  <h1>ComfyUI Skill CLI</h1>

  <p><strong>Agent-friendly command-line tool for managing and executing ComfyUI workflow skills.</strong></p>

  <p>
    Any AI agent that can run shell commands (Claude Code, Codex, OpenClaw, etc.) can use ComfyUI through this CLI.
  </p>

  <p>
    <a href="https://pypi.org/project/comfyui-skill-cli/"><img src="https://img.shields.io/pypi/v/comfyui-skill-cli?style=flat&color=4F46E5&logo=pypi&logoColor=white" alt="PyPI"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=10B981" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3B82F6&style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/stargazers"><img src="https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=EAB308&logo=github" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#install">Install</a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="#commands">Commands</a> ·
    <a href="#for-ai-agents">For AI Agents</a>
  </p>

  <p>
    <strong>English</strong> ·
    <a href="./README.zh.md">简体中文</a> ·
    <a href="./README.zh-TW.md">繁體中文</a> ·
    <a href="./README.ja.md">日本語</a> ·
    <a href="./README.ko.md">한국어</a> ·
    <a href="./README.es.md">Español</a>
  </p>

</div>

---

## Why comfyui-skill?

| Capability | Why it matters |
|------------|----------------|
| **Agent-native** | Structured JSON output, pipe-friendly, designed for AI agents to call |
| **Zero config** | Reads `config.json` and `data/` from the current directory, no setup needed |
| **Full lifecycle** | Discover, import, execute, cancel, manage workflows and dependencies in one tool |
| **Multi-server** | Manage multiple ComfyUI instances, route jobs to different hardware |
| **Model discovery** | Inspect model folders and available model names directly from the target server |
| **Workflow fleet management** | Import, enable, disable, delete, and migrate multiple workflows across machines |
| **Error guidance** | Common failures (OOM, unauthorized, missing models) return actionable hints |

<a id="install"></a>
## Install

```bash
pipx install comfyui-skill-cli
```

Or with pip:

```bash
pip install comfyui-skill-cli
```

### Update

```bash
pipx upgrade comfyui-skill-cli
```

### Development Mode

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

<a id="quick-start"></a>
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

Workflows are addressed as `<server_id>/<workflow_id>`:

```bash
comfyui-skill run local/txt2img          # explicit server
comfyui-skill run txt2img                # uses default server
comfyui-skill run txt2img -s my_server   # override with --server flag
```

<a id="commands"></a>
## Commands

### Workflow Discovery & Execution

| Command | Description |
|---------|-------------|
| `comfyui-skill list` | List all available workflows with parameters |
| `comfyui-skill info <id>` | Show workflow details and parameter schema |
| `comfyui-skill run <id> --args '{...}'` | Execute a workflow (blocking, real-time WebSocket streaming) |
| `comfyui-skill run <id> --validate` | Validate workflow without executing |
| `comfyui-skill submit <id> --args '{...}'` | Submit a workflow (non-blocking) |
| `comfyui-skill status <prompt_id>` | Check execution status and show discovered results |
| `comfyui-skill cancel <prompt_id>` | Cancel a running or queued job |
| `comfyui-skill upload <file>` | Upload a file to ComfyUI for use in workflows |
| `comfyui-skill upload <file> --mask` | Upload a mask image for inpainting workflows |
| `comfyui-skill upload --from-output <prompt_id>` | Chain a previous run's output as input for the next workflow |

### Queue & Resource Management

| Command | Description |
|---------|-------------|
| `comfyui-skill queue list` | Show running and pending jobs |
| `comfyui-skill queue clear` | Clear all pending jobs |
| `comfyui-skill queue delete <prompt_id>...` | Remove specific jobs from queue |
| `comfyui-skill free` | Release GPU memory and unload models |
| `comfyui-skill free --models` | Unload models only |
| `comfyui-skill free --memory` | Free cached memory only |

### Node & Model Discovery

| Command | Description |
|---------|-------------|
| `comfyui-skill nodes list` | List all available ComfyUI nodes by category |
| `comfyui-skill nodes info <class>` | Show node input/output schema |
| `comfyui-skill nodes search <query>` | Search nodes by name or category |
| `comfyui-skill models list` | List all available model folders |
| `comfyui-skill models list <folder>` | List models in a specific folder (e.g., `checkpoints`, `loras`) |

### Workflow Management

| Command | Description |
|---------|-------------|
| `comfyui-skill workflow import <path>` | Import workflow (auto-detect format, auto-generate schema) |
| `comfyui-skill workflow import --from-server` | Import one or more workflows from ComfyUI server userdata |
| `comfyui-skill workflow enable <id>` | Enable a workflow |
| `comfyui-skill workflow disable <id>` | Disable a workflow |
| `comfyui-skill workflow delete <id>` | Delete a workflow |

### Server Management

| Command | Description |
|---------|-------------|
| `comfyui-skill server list` | List all configured servers |
| `comfyui-skill server status` | Check if ComfyUI server is online |
| `comfyui-skill server stats` | Show VRAM, RAM, GPU info (`--all` for multi-server) |
| `comfyui-skill server add --id <id> --url <url>` | Add a new server |
| `comfyui-skill server enable/disable <id>` | Toggle server availability |
| `comfyui-skill server remove <id>` | Remove a server |

### Dependency Management

| Command | Description |
|---------|-------------|
| `comfyui-skill deps check <id>` | Check missing custom nodes and models |
| `comfyui-skill deps install <id> --all` | Auto-detect and install all missing deps |
| `comfyui-skill deps install <id> --repos '[...]'` | Install specific custom nodes |
| `comfyui-skill deps install <id> --models` | Install missing models via Manager |

### Configuration & History

| Command | Description |
|---------|-------------|
| `comfyui-skill config export --output <path>` | Export config and workflows as bundle |
| `comfyui-skill config import <path>` | Import config bundle (supports `--dry-run`) |
| `comfyui-skill history list <id>` | List execution history |
| `comfyui-skill history show <id> <run_id>` | Show details of a specific run |
| `comfyui-skill jobs list` | List server-side job history (`--status` to filter) |
| `comfyui-skill jobs show <prompt_id>` | Show details of a specific job |
| `comfyui-skill logs show` | Show recent ComfyUI server logs |
| `comfyui-skill templates list` | List workflow templates from custom nodes |
| `comfyui-skill templates subgraphs` | List reusable subgraph components |

### Global Options

| Option | Description |
|--------|-------------|
| `--json, -j` | Force JSON output |
| `--output-format` | Output format: `text`, `json`, `stream-json` |
| `--server, -s` | Specify server ID |
| `--dir, -d` | Specify data directory (default: current directory) |
| `--verbose, -v` | Verbose output |
| `--no-update-check` | Skip automatic CLI update check |

### Output Modes

| Mode | When | Format |
|------|------|--------|
| Text | TTY terminal | Rich tables and progress bars |
| JSON | Pipe or `--json` | Single JSON result |
| Stream JSON | `--output-format stream-json` | NDJSON events in real time |
| Errors | Always | stderr |

## Common Management Tasks

### Inspect models on a server

```bash
comfyui-skill models list
comfyui-skill models list checkpoints
comfyui-skill models list loras
```

Use this when you need to confirm model names before wiring them into a workflow or schema.

### Manage multiple workflows

```bash
# Preview workflows available in ComfyUI server userdata
comfyui-skill workflow import --from-server --preview

# Import matching workflows from the server
comfyui-skill workflow import --from-server --name sdxl

# Temporarily disable or re-enable a workflow
comfyui-skill workflow disable local/old-flow
comfyui-skill workflow enable local/old-flow

# Remove a workflow you no longer want to expose
comfyui-skill workflow delete local/old-flow
```

### Move workflow bundles between machines

```bash
comfyui-skill config export --output ./bundle.json --portable-only
comfyui-skill config import ./bundle.json --dry-run
comfyui-skill config import ./bundle.json --apply-environment
```

Use this when you want to migrate many workflows at once instead of re-importing them manually.

### Check models and dependencies before running

```bash
comfyui-skill deps check local/txt2img
comfyui-skill deps install local/txt2img --models
comfyui-skill deps install local/txt2img --all
```

<a id="for-ai-agents"></a>
## For AI Agents

This CLI is designed to be called from `SKILL.md` definitions. A typical agent workflow:

```bash
comfyui-skill server status --json                    # 1. verify server
comfyui-skill list --json                             # 2. discover workflows
comfyui-skill info local/txt2img --json               # 3. check parameters
comfyui-skill run local/txt2img --args '{...}' --json # 4. execute
```

### Workflow chaining (multi-step pipelines)

```bash
# Run first workflow
comfyui-skill run local/txt2img --args '{"prompt": "a cat"}' --json

# Chain output into next workflow
comfyui-skill upload --from-output <prompt_id> --json
comfyui-skill run local/upscale --args '{"image": "<uploaded_name>"}' --json
```

### Import and validate

```bash
comfyui-skill workflow import ./workflow.json --check-deps --json
comfyui-skill deps install local/my-workflow --all --json
```

## Contributing

Contributions are welcome! Please read the [Contributing Guide](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/blob/main/CONTRIBUTING.md) in the main repository for design principles and PR workflow.

## Resources

- [ComfyUI Skills OpenClaw](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) — Main skills repository
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — The backend this CLI orchestrates
- [Typer](https://typer.tiangolo.com/) — CLI framework used by this project

Built with [Typer](https://typer.tiangolo.com/), the same framework as [comfy-cli](https://github.com/Comfy-Org/comfy-cli). Designed to be integrated as a `comfy skills` subcommand in the future.
