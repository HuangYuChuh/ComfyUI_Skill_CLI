"""Tests for comfyui_skills_cli.client — all ComfyUIClient methods."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from comfyui_skills_cli.client import ComfyUIClient


# -- queue_prompt --

class QueuePromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_with_client_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"prompt_id": "p-123"})
        mock_post.return_value.raise_for_status = MagicMock()
        result = self.client.queue_prompt({"1": {}}, client_id="my-client-id")
        self.assertEqual(result["client_id"], "my-client-id")
        self.assertEqual(result["prompt_id"], "p-123")
        self.assertEqual(mock_post.call_args.kwargs["json"]["client_id"], "my-client-id")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_generates_client_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"prompt_id": "p-456"})
        mock_post.return_value.raise_for_status = MagicMock()
        result = self.client.queue_prompt({"1": {}})
        self.assertIn("client_id", result)
        self.assertTrue(len(result["client_id"]) > 0)

    @patch("comfyui_skills_cli.client.requests.post")
    def test_with_targets(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"prompt_id": "p-100"})
        mock_post.return_value.raise_for_status = MagicMock()
        self.client.queue_prompt({"1": {}}, targets=["5", "8"])
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["partial_execution_targets"], [["5"], ["8"]])

    @patch("comfyui_skills_cli.client.requests.post")
    def test_without_targets(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"prompt_id": "p-101"})
        mock_post.return_value.raise_for_status = MagicMock()
        self.client.queue_prompt({"1": {}}, targets=None)
        payload = mock_post.call_args.kwargs["json"]
        self.assertNotIn("partial_execution_targets", payload)

    @patch("comfyui_skills_cli.client.requests.post")
    def test_with_empty_targets(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"prompt_id": "p-102"})
        mock_post.return_value.raise_for_status = MagicMock()
        self.client.queue_prompt({"1": {}}, targets=[])
        payload = mock_post.call_args.kwargs["json"]
        self.assertNotIn("partial_execution_targets", payload)


# -- interrupt / queue management / free --

class InterruptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_with_prompt_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.interrupt("abc-123")
        self.assertTrue(result["success"])
        self.assertEqual(mock_post.call_args.kwargs["json"], {"prompt_id": "abc-123"})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_without_prompt_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.interrupt()
        self.assertTrue(result["success"])
        self.assertEqual(mock_post.call_args.kwargs["json"], {})


class QueueManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_clear(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.queue_clear()
        self.assertTrue(result["success"])
        self.assertEqual(mock_post.call_args.kwargs["json"], {"clear": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_delete(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.queue_delete(["id-1", "id-2"])
        self.assertTrue(result["success"])
        self.assertEqual(mock_post.call_args.kwargs["json"], {"delete": ["id-1", "id-2"]})


class FreeMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_both(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.free_memory(unload_models=True, free_memory=True)
        self.assertTrue(result["success"])
        self.assertEqual(mock_post.call_args.kwargs["json"], {"unload_models": True, "free_memory": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_models_only(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.client.free_memory(unload_models=True, free_memory=False)
        self.assertEqual(mock_post.call_args.kwargs["json"], {"unload_models": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_memory_only(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.client.free_memory(unload_models=False, free_memory=True)
        self.assertEqual(mock_post.call_args.kwargs["json"], {"free_memory": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_no_flags_sends_empty(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.client.free_memory(unload_models=False, free_memory=False)
        self.assertEqual(mock_post.call_args.kwargs["json"], {})


# -- upload --

class UploadFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_upload_file_calls_upload_image_endpoint(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"name": "test.png", "subfolder": "", "type": "input"}

        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake png data")
            tmp_path = f.name

        try:
            result = self.client.upload_file(tmp_path)
            self.assertEqual(result["name"], "test.png")
            self.assertIn("/upload/image", mock_post.call_args.args[0])
        finally:
            os.unlink(tmp_path)

    def test_upload_image_delegates_to_upload_file(self) -> None:
        with patch.object(self.client, "upload_file", return_value={"name": "x.png"}) as mock:
            result = self.client.upload_image("/fake/path.png")
            mock.assert_called_once_with("/fake/path.png")
            self.assertEqual(result["name"], "x.png")


# -- object_info --

class ObjectInfoNodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_found(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"KSampler": {"display_name": "KSampler", "category": "sampling"}},
        )
        result = self.client.get_object_info_node("KSampler")
        self.assertIsNotNone(result)
        self.assertEqual(result["display_name"], "KSampler")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_not_found(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=404)
        result = self.client.get_object_info_node("NonExistentNode")
        self.assertIsNone(result)


# -- system_stats --

SAMPLE_STATS = {
    "system": {
        "os": "posix", "ram_total": 68719476736, "ram_free": 32000000000,
        "comfyui_version": "v0.3.10", "python_version": "3.11.5",
        "pytorch_version": "2.1.0", "embedded_python": False,
    },
    "devices": [{
        "name": "cuda:0", "type": "cuda", "index": 0,
        "vram_total": 25769803776, "vram_free": 20000000000,
        "torch_vram_total": 25769803776, "torch_vram_free": 22000000000,
    }],
}


class SystemStatsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_success(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: SAMPLE_STATS)
        result = self.client.get_system_stats()
        self.assertEqual(result, SAMPLE_STATS)

    @patch("comfyui_skills_cli.client.requests.get")
    def test_raises_on_error(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=500)
        mock_resp.raise_for_status.side_effect = Exception("Server error")
        mock_get.return_value = mock_resp
        with self.assertRaises(Exception):
            self.client.get_system_stats()

    @patch("comfyui_skills_cli.client.requests.get")
    def test_multi_server(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: SAMPLE_STATS)
        clients = [ComfyUIClient("http://s1:8188"), ComfyUIClient("http://s2:8188")]
        results = [c.get_system_stats() for c in clients]
        self.assertEqual(len(results), 2)
        self.assertEqual(mock_get.call_count, 2)


# -- ws_events --

class WsEventsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("websocket.create_connection")
    def test_yields_matching_events(self, mock_ws_create: MagicMock) -> None:
        import websocket
        mock_ws = MagicMock()
        mock_ws_create.return_value = mock_ws
        events = [
            (websocket.ABNF.OPCODE_TEXT, json.dumps({"type": "execution_start", "data": {"prompt_id": "p-1"}}).encode()),
            (websocket.ABNF.OPCODE_TEXT, json.dumps({"type": "executing", "data": {"node": "5", "prompt_id": "p-1"}}).encode()),
            (websocket.ABNF.OPCODE_BINARY, b"\x01\x00\x00\x00fake-preview"),
            (websocket.ABNF.OPCODE_TEXT, json.dumps({"type": "executing", "data": {"node": None, "prompt_id": "p-1"}}).encode()),
        ]
        mock_ws.recv_data = MagicMock(side_effect=events)
        collected = list(self.client.ws_events("cid-1", "p-1"))
        self.assertEqual(len(collected), 3)
        self.assertEqual(collected[0]["type"], "execution_start")
        self.assertEqual(collected[1]["data"]["node"], "5")
        self.assertIsNone(collected[2]["data"]["node"])
        mock_ws.close.assert_called_once()

    @patch("websocket.create_connection")
    def test_filters_other_prompts(self, mock_ws_create: MagicMock) -> None:
        import websocket
        mock_ws = MagicMock()
        mock_ws_create.return_value = mock_ws
        events = [
            (websocket.ABNF.OPCODE_TEXT, json.dumps({"type": "executing", "data": {"node": "1", "prompt_id": "other"}}).encode()),
            (websocket.ABNF.OPCODE_TEXT, json.dumps({"type": "executing", "data": {"node": None, "prompt_id": "p-1"}}).encode()),
        ]
        mock_ws.recv_data = MagicMock(side_effect=events)
        collected = list(self.client.ws_events("cid-1", "p-1"))
        self.assertEqual(len(collected), 1)

    @patch("websocket.create_connection")
    def test_stops_on_error(self, mock_ws_create: MagicMock) -> None:
        import websocket
        mock_ws = MagicMock()
        mock_ws_create.return_value = mock_ws
        events = [
            (websocket.ABNF.OPCODE_TEXT, json.dumps({"type": "execution_error", "data": {"prompt_id": "p-1", "exception_message": "boom"}}).encode()),
        ]
        mock_ws.recv_data = MagicMock(side_effect=events)
        collected = list(self.client.ws_events("cid-1", "p-1"))
        self.assertEqual(len(collected), 1)
        self.assertEqual(collected[0]["type"], "execution_error")


# -- userdata workflows --

class ListUserdataWorkflowsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_v2_userdata_returns_list_of_dicts(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [
                {"name": "a.json", "path": "workflows/a.json", "type": "file"},
                {"name": "b.json", "path": "workflows/b.json", "type": "file"},
            ],
        )
        paths = self.client.list_userdata_workflows()
        self.assertEqual(paths, ["workflows/a.json", "workflows/b.json"])
        self.assertEqual(mock_get.call_args.kwargs["params"], {"path": "workflows"})

    @patch("comfyui_skills_cli.client.requests.get")
    def test_falls_back_to_userdata_bare_strings(self, mock_get: MagicMock) -> None:
        # /v2/userdata returns empty, /userdata returns bare filenames
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: []),
            MagicMock(status_code=200, json=lambda: ["a.json", "b.json"]),
        ]
        paths = self.client.list_userdata_workflows()
        self.assertEqual(paths, ["workflows/a.json", "workflows/b.json"])

    @patch("comfyui_skills_cli.client.requests.get")
    def test_both_endpoints_empty(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: [])
        self.assertEqual(self.client.list_userdata_workflows(), [])

    @patch("comfyui_skills_cli.client.requests.get")
    def test_filters_non_json_entries(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [
                {"path": "workflows/a.json"},
                {"path": "comfy.settings.json"},
                {"path": "workflows/readme.txt"},
            ],
        )
        paths = self.client.list_userdata_workflows()
        self.assertEqual(paths, ["workflows/a.json", "comfy.settings.json"])


class ReadUserdataWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_percent_encodes_full_path(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"nodes": []})
        self.client.read_userdata_workflow("workflows/MultiCharacter.json")
        called_url = mock_get.call_args.args[0]
        self.assertIn("/userdata/workflows%2FMultiCharacter.json", called_url)
        self.assertNotIn("/userdata/workflows/MultiCharacter.json", called_url)

    @patch("comfyui_skills_cli.client.requests.get")
    def test_returns_none_on_404(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=404)
        self.assertIsNone(self.client.read_userdata_workflow("workflows/missing.json"))


if __name__ == "__main__":
    unittest.main()
