"""Read config.json and data/ from the current working directory."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def get_base_dir(override: str = "") -> Path:
    if override:
        return Path(override).resolve()
    return Path.cwd()


def load_config(base_dir: Path) -> dict[str, Any]:
    config_path = base_dir / "config.json"
    data_dir = base_dir / "data"

    # Aggressive check for Agents: If neither config nor data exists, we are in the wrong place.
    if not config_path.exists() and not data_dir.exists():
        import sys
        print(
            f"[ERROR] comfyui-skill: No 'config.json' or 'data/' folder found in '{base_dir.resolve()}'.\n"
            f"You are likely running this command from the wrong directory.\n"
            f"Please 'cd' into your ComfyUI skill project root before execution.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not config_path.exists():
        return {"servers": []}
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def get_servers(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in config.get("servers", []) if isinstance(s, dict)]


def get_server(config: dict[str, Any], server_id: str) -> dict[str, Any] | None:
    for server in get_servers(config):
        if server.get("id") == server_id:
            return server
    return None


def get_default_server_id(config: dict[str, Any]) -> str:
    return config.get("default_server", "local")


def save_config(base_dir: Path, config: dict[str, Any]) -> None:
    config_path = base_dir / "config.json"
    tmp_path = config_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp_path.replace(config_path)
