"""ComfyUI HTTP client — all server communication goes through here."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

import requests


class ComfyUIClient:
    def __init__(self, server_url: str, auth: str = "", comfy_api_key: str = "", timeout: float = 30.0):
        self.server_url = server_url.rstrip("/")
        self.auth = auth
        self.comfy_api_key = comfy_api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.auth:
            headers["Authorization"] = f"Bearer {self.auth}"
        return headers

    def _get(self, path: str, **kwargs: Any) -> requests.Response:
        return requests.get(
            f"{self.server_url}{path}",
            headers=self._headers(),
            timeout=self.timeout,
            **kwargs,
        )

    def _post(self, path: str, json_data: Any = None, **kwargs: Any) -> requests.Response:
        return requests.post(
            f"{self.server_url}{path}",
            headers=self._headers(),
            json=json_data,
            timeout=self.timeout,
            **kwargs,
        )

    # -- Health --

    def check_health(self) -> dict[str, Any]:
        try:
            resp = self._get("/system_stats")
            resp.raise_for_status()
            return {"status": "online", "data": resp.json()}
        except (requests.RequestException, ValueError) as exc:
            return {"status": "offline", "error": str(exc)}

    # -- Prompt execution --

    def queue_prompt(self, workflow: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "prompt": workflow,
            "client_id": str(uuid.uuid4()),
        }
        if self.comfy_api_key:
            payload["extra_data"] = {"api_key_comfy_org": self.comfy_api_key}
        resp = self._post("/prompt", json_data=payload)
        resp.raise_for_status()
        return resp.json()

    def get_history(self, prompt_id: str) -> dict[str, Any] | None:
        resp = self._get(f"/history/{prompt_id}")
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get(prompt_id)

    def get_queue(self) -> dict[str, Any]:
        resp = self._get("/queue")
        resp.raise_for_status()
        return resp.json()

    def download_output(self, filename: str, subfolder: str = "", output_type: str = "output") -> bytes:
        resp = self._get("/view", params={
            "filename": filename,
            "subfolder": subfolder,
            "type": output_type,
        })
        resp.raise_for_status()
        return resp.content

    # -- Node info --

    def get_object_info(self) -> dict[str, Any]:
        resp = self._get("/object_info")
        resp.raise_for_status()
        return resp.json()

    def get_models(self, folder: str) -> list[str]:
        resp = self._get(f"/models/{folder}")
        resp.raise_for_status()
        return resp.json()

    # -- Manager API (ComfyUI-Manager plugin) --

    def manager_start_queue(self) -> bool:
        try:
            resp = self._get("/manager/queue/start", timeout=10)
            return resp.status_code < 500
        except requests.RequestException:
            return False

    def manager_install_node(self, repo_url: str, pkg_name: str) -> dict[str, Any]:
        resp = self._post("/manager/queue/install", json_data={
            "id": pkg_name,
            "url": repo_url,
            "install_type": "git-clone",
        })
        if resp.status_code == 404:
            return {"success": False, "error": "ComfyUI Manager not installed"}
        if resp.status_code >= 400:
            return {"success": False, "error": f"Manager API error: {resp.status_code}"}
        return {"success": True}

    def manager_queue_status(self) -> dict[str, Any] | None:
        try:
            resp = self._get("/manager/queue/status", timeout=10)
            if resp.status_code != 200:
                return None
            return resp.json()
        except (requests.RequestException, ValueError):
            return None

    def manager_wait_for_queue(self, max_polls: int = 60, interval: float = 3.0) -> bool:
        for _ in range(max_polls):
            time.sleep(interval)
            status = self.manager_queue_status()
            if status is None:
                continue
            total = status.get("total", 0)
            done = status.get("done", 0)
            if total > 0 and done >= total:
                return True
        return False
