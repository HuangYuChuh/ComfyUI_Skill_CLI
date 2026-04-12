"""Tests for server-side jobs/history client methods."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from comfyui_skills_cli.client import ComfyUIClient


class GetHistoryListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_history_list_default_params(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"abc123": {"status": {"completed": True}}}
        mock_get.return_value = mock_resp

        result = self.client.get_history_list()
        self.assertEqual(result, {"abc123": {"status": {"completed": True}}})

        call_kwargs = mock_get.call_args
        self.assertIn("/history", call_kwargs.args[0])
        self.assertEqual(call_kwargs.kwargs["params"], {"max_items": 20, "offset": 0})

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_history_list_custom_params(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp

        self.client.get_history_list(max_items=5, offset=10)
        call_kwargs = mock_get.call_args
        self.assertEqual(call_kwargs.kwargs["params"], {"max_items": 5, "offset": 10})


class GetJobsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_jobs_no_status_filter(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"jobs": []}
        mock_get.return_value = mock_resp

        result = self.client.get_jobs()
        self.assertEqual(result, {"jobs": []})

        call_kwargs = mock_get.call_args
        self.assertIn("/api/jobs", call_kwargs.args[0])
        params = call_kwargs.kwargs["params"]
        self.assertNotIn("status", params)
        self.assertEqual(params["limit"], 20)
        self.assertEqual(params["sort_by"], "created_at")
        self.assertEqual(params["sort_order"], "desc")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_jobs_with_status_filter(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"jobs": [{"id": "j1", "status": "completed"}]}
        mock_get.return_value = mock_resp

        result = self.client.get_jobs(status="completed", limit=5)
        self.assertEqual(len(result["jobs"]), 1)

        call_kwargs = mock_get.call_args
        params = call_kwargs.kwargs["params"]
        self.assertEqual(params["status"], "completed")
        self.assertEqual(params["limit"], 5)


class GetJobTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_job_found(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"id": "job-1", "status": "completed"}
        mock_get.return_value = mock_resp

        result = self.client.get_job("job-1")
        self.assertEqual(result, {"id": "job-1", "status": "completed"})
        self.assertIn("/api/jobs/job-1", mock_get.call_args.args[0])

    @patch("comfyui_skills_cli.client.requests.get")
    def test_get_job_not_found(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock(status_code=404)
        mock_get.return_value = mock_resp

        result = self.client.get_job("nonexistent")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
