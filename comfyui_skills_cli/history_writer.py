"""Write and query execution history in data/{server_id}/{workflow_id}/history/."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _hist_dir(base_dir: Path, server_id: str, workflow_id: str) -> Path:
    return base_dir / "data" / server_id / workflow_id / "history"


def find_existing_run(
    base_dir: Path, server_id: str, workflow_id: str, job_id: str,
) -> dict[str, Any] | None:
    """O(1) idempotency check — returns cached record if job_id was already executed."""
    path = _hist_dir(base_dir, server_id, workflow_id) / f"{job_id}.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_run_record(
    base_dir: Path,
    server_id: str,
    workflow_id: str,
    prompt_id: str,
    args: dict[str, Any],
    status: str,
    *,
    job_id: str = "",
    duration_ms: int = 0,
    outputs: list[dict[str, str]] | None = None,
    error: str = "",
) -> None:
    """Persist a single execution record as JSON."""
    hist_dir = _hist_dir(base_dir, server_id, workflow_id)
    hist_dir.mkdir(parents=True, exist_ok=True)

    file_id = job_id or prompt_id

    record = {
        "run_id": file_id,
        "job_id": job_id,
        "prompt_id": prompt_id,
        "server_id": server_id,
        "workflow_id": workflow_id,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": duration_ms,
        "args": args,
    }
    if outputs:
        record["outputs"] = outputs
    if error:
        record["error"] = error

    path = hist_dir / f"{file_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
