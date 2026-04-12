"""Tests for the server stats command and client method."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from comfyui_skills_cli.client import ComfyUIClient


SAMPLE_STATS = {
    "system": {
        "os": "posix",
        "ram_total": 68719476736,
        "ram_free": 32000000000,
        "comfyui_version": "v0.3.10",
        "python_version": "3.11.5",
        "pytorch_version": "2.1.0",
        "embedded_python": False,
    },
    "devices": [
        {
            "name": "cuda:0",
            "type": "cuda",
            "index": 0,
            "vram_total": 25769803776,
            "vram_free": 20000000000,
            "torch_vram_total": 25769803776,
            "torch_vram_free": 22000000000,
        }
    ],
}


class GetSystemStatsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_system_stats_success(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = SAMPLE_STATS
        mock_get.return_value = mock_resp

        result = self.client.get_system_stats()

        self.assertEqual(result, SAMPLE_STATS)
        self.assertIn("/system_stats", mock_get.call_args.args[0])

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_system_stats_raises_on_error(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=500)
        mock_resp.raise_for_status.side_effect = Exception("Server error")
        mock_get.return_value = mock_resp

        with self.assertRaises(Exception):
            self.client.get_system_stats()


class ServerStatsAllTests(unittest.TestCase):
    """Test that --all queries multiple servers."""

    @patch("comfyui_skills_cli.client.requests.get")
    def test_all_queries_multiple_servers(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = SAMPLE_STATS
        mock_get.return_value = mock_resp

        # Create two clients (simulating what the command does)
        clients = [
            ComfyUIClient("http://server1:8188"),
            ComfyUIClient("http://server2:8188"),
        ]

        results = []
        for c in clients:
            results.append(c.get_system_stats())

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["system"]["comfyui_version"], "v0.3.10")
        self.assertEqual(results[1]["system"]["comfyui_version"], "v0.3.10")
        # Verify both servers were called
        self.assertEqual(mock_get.call_count, 2)
        urls_called = [call.args[0] for call in mock_get.call_args_list]
        self.assertIn("http://server1:8188/system_stats", urls_called)
        self.assertIn("http://server2:8188/system_stats", urls_called)


if __name__ == "__main__":
    unittest.main()
