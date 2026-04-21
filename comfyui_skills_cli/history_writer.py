"""Write execution history records to data/{server_id}/{workflow_id}/history/."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def save_run_record(
    base_dir: Path,
    server_id: str,
    workflow_id: str,
    prompt_id: str,
    args: dict[str, Any],
    status: str,
    *,
    duration_ms: int = 0,
    outputs: list[dict[str, str]] | None = None,
    error: str = "",
) -> None:
    """Persist a single execution record as JSON."""
    hist_dir = base_dir / "data" / server_id / workflow_id / "history"
    hist_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "run_id": prompt_id,
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

    path = hist_dir / f"{prompt_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
