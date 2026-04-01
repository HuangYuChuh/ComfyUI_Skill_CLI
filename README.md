# ComfyUI Skill CLI

Agent-friendly command-line tool for managing and executing [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow skills.

## What is this?

ComfyUI Skill CLI turns ComfyUI workflows into callable commands. Any AI agent that can run shell commands (Claude, Codex, OpenClaw, etc.) can use ComfyUI through this CLI.

```bash
# List available skills
comfyui-skill list --json

# Execute a workflow
comfyui-skill run local/txt2img --args '{"prompt": "a white cat", "seed": 42}' --json

# Check server health
comfyui-skill server status --json
```

Every command supports `--json` for structured output. Pipe-friendly by default.

## Install

```bash
pipx install comfyui-skill-cli
```

### Development Mode

If you want to modify the CLI source code and have changes take effect immediately without reinstalling:

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

The `-e` flag (editable) links directly to your local source — any code change is reflected instantly.

## Usage

Run commands from within a [ComfyUI Skills](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) project directory:

```bash
cd /path/to/your-skills-project
comfyui-skill list
```

The CLI reads `config.json` and `data/` from the current working directory.

### Commands

#### Workflow Discovery & Execution

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill list` | List all available skills with parameters | ✅ |
| `comfyui-skill info <id>` | Show skill details and parameter schema | ✅ |
| `comfyui-skill run <id> --args '{...}'` | Execute a skill (blocking, returns images) | ✅ |
| `comfyui-skill submit <id> --args '{...}'` | Submit a skill (non-blocking, returns prompt_id) | ✅ |
| `comfyui-skill status <prompt-id>` | Check execution status and download results | ✅ |

#### Server Management

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill server list` | List all configured servers | ✅ |
| `comfyui-skill server status [id]` | Check if ComfyUI server is online | ✅ |
| `comfyui-skill server add --id <id> --url <url>` | Add a new server | 🔜 |
| `comfyui-skill server enable <id>` | Enable a server | 🔜 |
| `comfyui-skill server disable <id>` | Disable a server | 🔜 |
| `comfyui-skill server remove <id>` | Remove a server | 🔜 |

#### Dependency Management

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill deps check <id>` | Check missing custom nodes and models | ✅ |
| `comfyui-skill deps install <id> --repos '[...]'` | Install missing custom nodes via Manager | ✅ |
| `comfyui-skill deps install <id> --models` | Install missing models via Manager | 🔜 |

#### Workflow Management

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill workflow import <json>` | Import workflow from local JSON (auto-detect format, auto-convert, auto-generate schema) | 🔜 |
| `comfyui-skill workflow import --from-server` | Import workflows from ComfyUI server userdata | 🔜 |
| `comfyui-skill workflow enable <id>` | Enable a workflow | 🔜 |
| `comfyui-skill workflow disable <id>` | Disable a workflow | 🔜 |
| `comfyui-skill workflow delete <id>` | Delete a workflow | 🔜 |
| `comfyui-skill workflow setup <json>` | One-click: import → check deps → install → ready | 🔜 |

#### Image Upload

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill upload <image>` | Upload image to ComfyUI for use in workflows | 🔜 |

#### Configuration Transfer

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill config export --output <path>` | Export config and workflows as bundle | 🔜 |
| `comfyui-skill config import <path>` | Import config bundle (supports --dry-run) | 🔜 |

#### Execution History

| Command | Description | Status |
|---------|-------------|--------|
| `comfyui-skill history list <id>` | List execution history for a skill | 🔜 |
| `comfyui-skill history show <id> <run_id>` | Show details of a specific run | 🔜 |

> ✅ = implemented, 🔜 = planned. See [docs/cli-roadmap.md](./docs/cli-roadmap.md) for full roadmap.

### Global Options

| Option | Description |
|--------|-------------|
| `--json, -j` | Force JSON output |
| `--server, -s` | Specify server ID |
| `--dir, -d` | Specify data directory (default: current directory) |
| `--verbose, -v` | Verbose output |

### Output Modes

- **TTY** → Rich tables and progress bars (human-friendly)
- **Pipe / `--json`** → Structured JSON (agent-friendly)
- **Errors** → Always stderr

### Skill ID Format

```bash
comfyui-skill run local/txt2img          # server_id/workflow_id
comfyui-skill run txt2img                # uses default server
comfyui-skill run txt2img -s my_server   # explicit server
```

## For AI Agents

This CLI is designed to be called from `SKILL.md` definitions:

```markdown
## Available Commands
comfyui-skill list --json
comfyui-skill info <server_id>/<workflow_id> --json
comfyui-skill run <server_id>/<workflow_id> --args '{"prompt":"..."}' --json

## Typical Flow
1. `comfyui-skill server status --json` — verify server is online
2. `comfyui-skill list --json` — discover available skills
3. `comfyui-skill info <id> --json` — check required parameters
4. `comfyui-skill run <id> --args '{...}' --json` — execute
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
