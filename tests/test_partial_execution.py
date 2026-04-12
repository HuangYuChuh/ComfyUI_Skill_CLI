"""Tests for partial execution targets in queue_prompt."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from comfyui_skills_cli.client import ComfyUIClient


class PartialExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_prompt_with_targets(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"prompt_id": "p-100"},
        )
        mock_post.return_value.raise_for_status = MagicMock()

        self.client.queue_prompt({"1": {}}, targets=["5", "8"])

        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["partial_execution_targets"], [["5"], ["8"]])

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_prompt_without_targets(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"prompt_id": "p-101"},
        )
        mock_post.return_value.raise_for_status = MagicMock()

        self.client.queue_prompt({"1": {}}, targets=None)

        payload = mock_post.call_args.kwargs["json"]
        self.assertNotIn("partial_execution_targets", payload)

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_prompt_with_empty_targets(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"prompt_id": "p-102"},
        )
        mock_post.return_value.raise_for_status = MagicMock()

        self.client.queue_prompt({"1": {}}, targets=[])

        payload = mock_post.call_args.kwargs["json"]
        self.assertNotIn("partial_execution_targets", payload)


if __name__ == "__main__":
    unittest.main()
