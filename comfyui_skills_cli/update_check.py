"""Best-effort PyPI update notification for the CLI."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PACKAGE_NAME = "comfyui-skill-cli"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
NO_UPDATE_CHECK_ENV = "COMFYUI_SKILL_NO_UPDATE_CHECK"
FORCE_UPDATE_CHECK_ENV = "COMFYUI_SKILL_FORCE_UPDATE_CHECK"
UPDATE_CHECK_TTL_SECONDS = 24 * 60 * 60
UPDATE_CHECK_ERROR_TTL_SECONDS = 60 * 60
UPDATE_CHECK_TIMEOUT_SECONDS = 2


def is_machine_output(json_output: bool, output_format: str) -> bool:
    fmt = output_format.strip().lower()
    if json_output or fmt in {"json", "stream-json"}:
        return True
    if fmt:
        return False
    return not sys.stdout.isatty()


def maybe_notify_update(current_version: str, *, disabled: bool = False) -> None:
    """Print a non-blocking update hint to stderr when a newer PyPI version exists."""
    if disabled or _env_truthy(NO_UPDATE_CHECK_ENV):
        return

    try:
        latest_version = _latest_version_to_check()
        if latest_version and _is_newer_version(latest_version, current_version):
            sys.stderr.write(
                f"[comfyui-skill] New CLI version available: {current_version} -> {latest_version}\n"
                f"[comfyui-skill] Upgrade with: {_upgrade_command()}\n"
            )
    except Exception:
        # Update checks must never affect the real CLI command.
        return


def _latest_version_to_check() -> str | None:
    now = time.time()
    cache = _read_cache()

    if not _env_truthy(FORCE_UPDATE_CHECK_ENV):
        last_checked = _as_float(cache.get("last_checked"))
        if last_checked and now - last_checked < UPDATE_CHECK_TTL_SECONDS:
            return None

        last_error_checked = _as_float(cache.get("last_error_checked"))
        if last_error_checked and now - last_error_checked < UPDATE_CHECK_ERROR_TTL_SECONDS:
            return None

    try:
        latest_version = _fetch_latest_version()
    except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError):
        cache["last_error_checked"] = now
        _write_cache(cache)
        return None

    _write_cache({"last_checked": now, "latest_version": latest_version})
    return latest_version


def _fetch_latest_version() -> str:
    req = urllib.request.Request(
        PYPI_JSON_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": f"{PACKAGE_NAME}/update-check",
        },
    )
    with urllib.request.urlopen(req, timeout=UPDATE_CHECK_TIMEOUT_SECONDS) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data["info"]["version"])


def _is_newer_version(latest: str, current: str) -> bool:
    try:
        from packaging.version import Version

        return Version(latest) > Version(current)
    except Exception:
        return _version_tuple(latest) > _version_tuple(current)


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version))


def _cache_path() -> Path:
    cache_home = os.environ.get("XDG_CACHE_HOME")
    if not cache_home and sys.platform == "win32":
        cache_home = os.environ.get("LOCALAPPDATA")
    base = Path(cache_home).expanduser() if cache_home else Path.home() / ".cache"
    return base / "comfyui-skill-cli" / "update-check.json"


def _read_cache() -> dict[str, Any]:
    path = _cache_path()
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        return {}
    return {}


def _write_cache(data: dict[str, Any]) -> None:
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except OSError:
        return


def _env_truthy(name: str) -> bool:
    value = os.environ.get(name, "")
    return value.lower() in {"1", "true", "yes", "on"}


def _as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _upgrade_command() -> str:
    executable_parts = {part.lower() for part in Path(sys.executable).parts}
    if "pipx" in executable_parts and "venvs" in executable_parts:
        return f"pipx upgrade {PACKAGE_NAME}"
    return f"{shlex.quote(sys.executable)} -m pip install -U {PACKAGE_NAME}"
