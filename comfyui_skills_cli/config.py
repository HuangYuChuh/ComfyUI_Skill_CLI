"""Read config.json and data/ from the current working directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_base_dir(override: str = "") -> Path:
    if override:
        return Path(override).resolve()
    return Path.cwd()


def load_config(base_dir: Path) -> dict[str, Any]:
    config_path = base_dir / "config.json"
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
