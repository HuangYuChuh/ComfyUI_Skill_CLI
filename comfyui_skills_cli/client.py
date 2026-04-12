"""ComfyUI HTTP client — all server communication goes through here."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Generator

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

    def get_system_stats(self) -> dict[str, Any]:
        resp = self._get("/system_stats")
        resp.raise_for_status()
        return resp.json()

    # -- Prompt execution --

    def queue_prompt(self, workflow: dict[str, Any], client_id: str | None = None, targets: list[str] | None = None, priority: float | None = None) -> dict[str, Any]:
        cid = client_id or str(uuid.uuid4())
        payload: dict[str, Any] = {
            "prompt": workflow,
            "client_id": cid,
        }
        if priority is not None:
            payload["number"] = priority
        if targets:
            payload["partial_execution_targets"] = [[t] for t in targets]
        if self.comfy_api_key:
            payload["extra_data"] = {"api_key_comfy_org": self.comfy_api_key}
        resp = self._post("/prompt", json_data=payload)
        resp.raise_for_status()
        data = resp.json()
        data["client_id"] = cid
        return data

    def get_history(self, prompt_id: str) -> dict[str, Any] | None:
        resp = self._get(f"/history/{prompt_id}")
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get(prompt_id)

    def get_history_list(self, max_items: int = 20, offset: int = 0) -> dict[str, Any]:
        resp = self._get("/history", params={"max_items": max_items, "offset": offset})
        resp.raise_for_status()
        return resp.json()

    def get_jobs(self, status: str = "", limit: int = 20, offset: int = 0, sort_by: str = "created_at", sort_order: str = "desc") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset, "sort_by": sort_by, "sort_order": sort_order}
        if status:
            params["status"] = status
        resp = self._get("/api/jobs", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        resp = self._get(f"/api/jobs/{job_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def get_queue(self) -> dict[str, Any]:
        resp = self._get("/queue")
        resp.raise_for_status()
        return resp.json()

    def ws_events(self, client_id: str, prompt_id: str) -> Generator[dict[str, Any], None, None]:
        import websocket
        ws_url = self.server_url.replace("http://", "ws://").replace("https://", "wss://")
        ws = websocket.create_connection(
            f"{ws_url}/ws?clientId={client_id}",
            timeout=self.timeout,
        )
        ws.settimeout(None)
        try:
            while True:
                opcode, raw = ws.recv_data()
                if opcode == websocket.ABNF.OPCODE_BINARY:
                    continue
                if opcode != websocket.ABNF.OPCODE_TEXT:
                    continue
                msg = json.loads(raw)
                event_type = msg.get("type", "")
                data = msg.get("data", {})
                if data.get("prompt_id") and data["prompt_id"] != prompt_id:
                    continue
                yield {"type": event_type, "data": data}
                if event_type in ("execution_error", "execution_interrupted"):
                    break
                if event_type == "executing" and data.get("node") is None:
                    break
        finally:
            ws.close()

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

    def get_object_info_node(self, node_class: str) -> dict[str, Any] | None:
        resp = self._get(f"/object_info/{node_class}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        return data.get(node_class)

    def get_model_folders(self) -> list[str]:
        resp = self._get("/models")
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

    # -- Queue management --

    def interrupt(self, prompt_id: str = "") -> dict[str, Any]:
        payload = {"prompt_id": prompt_id} if prompt_id else {}
        resp = self._post("/interrupt", json_data=payload)
        resp.raise_for_status()
        return {"success": True}

    def queue_delete(self, prompt_ids: list[str]) -> dict[str, Any]:
        resp = self._post("/queue", json_data={"delete": prompt_ids})
        resp.raise_for_status()
        return {"success": True}

    def queue_clear(self) -> dict[str, Any]:
        resp = self._post("/queue", json_data={"clear": True})
        resp.raise_for_status()
        return {"success": True}

    # -- Memory management --

    def free_memory(self, unload_models: bool = False, free_memory: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if unload_models:
            payload["unload_models"] = True
        if free_memory:
            payload["free_memory"] = True
        resp = self._post("/free", json_data=payload)
        resp.raise_for_status()
        return {"success": True}

    # -- File upload --

    def upload_file(self, filepath: str) -> dict[str, Any]:
        import mimetypes
        import os
        filename = os.path.basename(filepath)
        content_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        with open(filepath, "rb") as f:
            content = f.read()

        boundary = f"----ComfyUIBoundary{id(content)}"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")

        headers = self._headers()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        resp = requests.post(
            f"{self.server_url}/upload/image",
            data=body,
            headers=headers,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def upload_image(self, filepath: str) -> dict[str, Any]:
        return self.upload_file(filepath)

    def upload_mask(self, filepath: str, original_ref: str = "") -> dict[str, Any]:
        import mimetypes
        import os
        filename = os.path.basename(filepath)
        content_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        with open(filepath, "rb") as f:
            content = f.read()

        boundary = f"----ComfyUIBoundary{id(content)}"
        parts = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8") + content + b"\r\n"

        if original_ref:
            parts += (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="original_ref"\r\n\r\n'
                f"{original_ref}\r\n"
            ).encode("utf-8")

        parts += f"--{boundary}--\r\n".encode("utf-8")

        headers = self._headers()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        resp = requests.post(
            f"{self.server_url}/upload/mask",
            data=parts,
            headers=headers,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # -- Node replacements, logs, templates --

    def get_node_replacements(self) -> dict[str, str]:
        resp = self._get("/node_replacements")
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        return resp.json()

    def get_logs(self) -> dict[str, Any]:
        resp = self._get("/internal/logs/raw")
        resp.raise_for_status()
        return resp.json()

    def get_subgraphs(self) -> dict[str, Any]:
        resp = self._get("/global_subgraphs")
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        return resp.json()

    def get_workflow_templates(self) -> dict[str, Any]:
        resp = self._get("/workflow_templates")
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        return resp.json()

    # -- ComfyUI Userdata API --

    def list_userdata_workflows(self) -> list[str]:
        for path in ["/v2/userdata", "/userdata"]:
            try:
                resp = self._get(f"{path}?dir=workflows&recurse=true")
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        return [f for f in data if isinstance(f, str) and f.endswith(".json")]
                    if isinstance(data, dict) and "files" in data:
                        return [
                            f.get("path", f.get("name", ""))
                            for f in data["files"]
                            if isinstance(f, dict) and (f.get("path", "") or f.get("name", "")).endswith(".json")
                        ]
            except (requests.RequestException, ValueError):
                continue
        return []

    def read_userdata_workflow(self, workflow_path: str) -> dict[str, Any] | None:
        import urllib.parse
        encoded = urllib.parse.quote(workflow_path, safe="")
        for base in ["/v2/userdata", "/userdata"]:
            try:
                resp = self._get(f"{base}/workflows/{encoded}")
                if resp.status_code == 200:
                    return resp.json()
            except (requests.RequestException, ValueError):
                continue
        return None

    # -- Manager model install --

    def manager_install_model(self, model_info: dict[str, str]) -> dict[str, Any]:
        resp = self._post("/manager/queue/install_model", json_data=model_info)
        if resp.status_code == 404:
            return {"success": False, "error": "ComfyUI Manager not installed"}
        if resp.status_code >= 400:
            return {"success": False, "error": f"Manager API error: {resp.status_code}"}
        return {"success": True}

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
