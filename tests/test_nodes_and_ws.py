"""Tests for nodes command helpers and WebSocket client methods."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from comfyui_skills_cli.client import ComfyUIClient


SAMPLE_OBJECT_INFO = {
    "KSampler": {
        "input": {
            "required": {
                "model": ["MODEL"],
                "seed": ["INT", {"default": 0, "min": 0, "max": 2**64 - 1}],
                "sampler_name": [["euler", "euler_ancestral", "heun"]],
            },
            "optional": {},
        },
        "input_order": {"required": ["model", "seed", "sampler_name"], "optional": []},
        "output": ["LATENT"],
        "output_is_list": [False],
        "output_name": ["LATENT"],
        "name": "KSampler",
        "display_name": "KSampler",
        "description": "Samples latents",
        "category": "sampling",
    },
    "CLIPTextEncode": {
        "input": {"required": {"text": ["STRING"], "clip": ["CLIP"]}, "optional": {}},
        "input_order": {"required": ["text", "clip"], "optional": []},
        "output": ["CONDITIONING"],
        "output_is_list": [False],
        "output_name": ["CONDITIONING"],
        "name": "CLIPTextEncode",
        "display_name": "CLIP Text Encode",
        "description": "",
        "category": "conditioning",
    },
}


class ObjectInfoNodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_object_info_node_found(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"KSampler": SAMPLE_OBJECT_INFO["KSampler"]},
        )
        result = self.client.get_object_info_node("KSampler")
        self.assertIsNotNone(result)
        self.assertEqual(result["display_name"], "KSampler")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_object_info_node_not_found(self, mock_get: MagicMock) -> None:
        mock_get.return_value = MagicMock(status_code=404)
        result = self.client.get_object_info_node("NonExistentNode")
        self.assertIsNone(result)


class QueuePromptClientIdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_prompt_with_client_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"prompt_id": "p-123"},
        )
        mock_post.return_value.raise_for_status = MagicMock()
        result = self.client.queue_prompt({"1": {}}, client_id="my-client-id")
        self.assertEqual(result["client_id"], "my-client-id")
        self.assertEqual(result["prompt_id"], "p-123")
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["client_id"], "my-client-id")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_prompt_generates_client_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"prompt_id": "p-456"},
        )
        mock_post.return_value.raise_for_status = MagicMock()
        result = self.client.queue_prompt({"1": {}})
        self.assertIn("client_id", result)
        self.assertTrue(len(result["client_id"]) > 0)


class WsEventsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("websocket.create_connection")
    def test_ws_events_yields_matching_events(self, mock_ws_create: MagicMock) -> None:
        import websocket

        mock_ws = MagicMock()
        mock_ws_create.return_value = mock_ws

        events = [
            (websocket.ABNF.OPCODE_TEXT, json.dumps({
                "type": "execution_start",
                "data": {"prompt_id": "p-1"},
            }).encode()),
            (websocket.ABNF.OPCODE_TEXT, json.dumps({
                "type": "executing",
                "data": {"node": "5", "prompt_id": "p-1"},
            }).encode()),
            (websocket.ABNF.OPCODE_BINARY, b"\x01\x00\x00\x00fake-preview"),
            (websocket.ABNF.OPCODE_TEXT, json.dumps({
                "type": "executing",
                "data": {"node": None, "prompt_id": "p-1"},
            }).encode()),
        ]
        mock_ws.recv_data = MagicMock(side_effect=events)

        collected = list(self.client.ws_events("cid-1", "p-1"))
        self.assertEqual(len(collected), 3)
        self.assertEqual(collected[0]["type"], "execution_start")
        self.assertEqual(collected[1]["type"], "executing")
        self.assertEqual(collected[1]["data"]["node"], "5")
        self.assertEqual(collected[2]["type"], "executing")
        self.assertIsNone(collected[2]["data"]["node"])
        mock_ws.close.assert_called_once()

    @patch("websocket.create_connection")
    def test_ws_events_filters_other_prompts(self, mock_ws_create: MagicMock) -> None:
        import websocket

        mock_ws = MagicMock()
        mock_ws_create.return_value = mock_ws

        events = [
            (websocket.ABNF.OPCODE_TEXT, json.dumps({
                "type": "executing",
                "data": {"node": "1", "prompt_id": "other-prompt"},
            }).encode()),
            (websocket.ABNF.OPCODE_TEXT, json.dumps({
                "type": "executing",
                "data": {"node": None, "prompt_id": "p-1"},
            }).encode()),
        ]
        mock_ws.recv_data = MagicMock(side_effect=events)

        collected = list(self.client.ws_events("cid-1", "p-1"))
        self.assertEqual(len(collected), 1)
        self.assertIsNone(collected[0]["data"]["node"])

    @patch("websocket.create_connection")
    def test_ws_events_stops_on_error(self, mock_ws_create: MagicMock) -> None:
        import websocket

        mock_ws = MagicMock()
        mock_ws_create.return_value = mock_ws

        events = [
            (websocket.ABNF.OPCODE_TEXT, json.dumps({
                "type": "execution_error",
                "data": {"prompt_id": "p-1", "exception_message": "boom"},
            }).encode()),
        ]
        mock_ws.recv_data = MagicMock(side_effect=events)

        collected = list(self.client.ws_events("cid-1", "p-1"))
        self.assertEqual(len(collected), 1)
        self.assertEqual(collected[0]["type"], "execution_error")


class NodesFlattenTests(unittest.TestCase):
    def test_flatten_all(self) -> None:
        from comfyui_skills_cli.commands.nodes import _flatten_nodes
        rows = _flatten_nodes(SAMPLE_OBJECT_INFO)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["category"], "conditioning")
        self.assertEqual(rows[1]["category"], "sampling")

    def test_flatten_with_category_filter(self) -> None:
        from comfyui_skills_cli.commands.nodes import _flatten_nodes
        rows = _flatten_nodes(SAMPLE_OBJECT_INFO, "sampling")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["class_type"], "KSampler")

    def test_flatten_with_nonexistent_category(self) -> None:
        from comfyui_skills_cli.commands.nodes import _flatten_nodes
        rows = _flatten_nodes(SAMPLE_OBJECT_INFO, "nonexistent")
        self.assertEqual(len(rows), 0)


class WsAvailableTests(unittest.TestCase):
    def test_ws_available_true(self) -> None:
        from comfyui_skills_cli.commands.run import _ws_available
        result = _ws_available()
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
