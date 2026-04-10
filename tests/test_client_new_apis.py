"""Tests for new client methods and error hint matching."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from comfyui_skills_cli.client import ComfyUIClient
from comfyui_skills_cli.error_hints import match_error_hint


class InterruptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_interrupt_with_prompt_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.interrupt("abc-123")
        self.assertTrue(result["success"])
        call_kwargs = mock_post.call_args
        self.assertIn("/interrupt", call_kwargs.args[0])
        self.assertEqual(call_kwargs.kwargs["json"], {"prompt_id": "abc-123"})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_interrupt_without_prompt_id(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.interrupt()
        self.assertTrue(result["success"])
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {})


class QueueManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_clear(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.queue_clear()
        self.assertTrue(result["success"])
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {"clear": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_queue_delete(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.queue_delete(["id-1", "id-2"])
        self.assertTrue(result["success"])
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {"delete": ["id-1", "id-2"]})


class FreeMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ComfyUIClient("http://localhost:8188")

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_both(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.free_memory(unload_models=True, free_memory=True)
        self.assertTrue(result["success"])
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {"unload_models": True, "free_memory": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_models_only(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.client.free_memory(unload_models=True, free_memory=False)
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {"unload_models": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_memory_only(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.client.free_memory(unload_models=False, free_memory=True)
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {"free_memory": True})

    @patch("comfyui_skills_cli.client.requests.post")
    def test_free_no_flags_sends_empty(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.client.free_memory(unload_models=False, free_memory=False)
        call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs.kwargs["json"], {})


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
            call_args = mock_post.call_args
            self.assertIn("/upload/image", call_args.args[0])
        finally:
            os.unlink(tmp_path)

    def test_upload_image_delegates_to_upload_file(self) -> None:
        with patch.object(self.client, "upload_file", return_value={"name": "x.png"}) as mock:
            result = self.client.upload_image("/fake/path.png")
            mock.assert_called_once_with("/fake/path.png")
            self.assertEqual(result["name"], "x.png")


class ErrorHintTests(unittest.TestCase):
    def test_unauthorized_hint(self) -> None:
        hint = match_error_hint("Unauthorized: Please login first to use this node.")
        self.assertIn("ComfyUI API Key", hint)
        self.assertIn("platform.comfy.org", hint)

    def test_cuda_oom_hint(self) -> None:
        hint = match_error_hint("RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB")
        self.assertIn("comfyui-skill free", hint)

    def test_mps_oom_hint(self) -> None:
        hint = match_error_hint("RuntimeError: MPS out of memory")
        self.assertIn("comfyui-skill free", hint)

    def test_connection_refused_hint(self) -> None:
        hint = match_error_hint("ConnectionError: Connection refused")
        self.assertIn("not running", hint)

    def test_missing_model_ckpt_hint(self) -> None:
        hint = match_error_hint("FileNotFoundError: model_v1.ckpt not found")
        self.assertIn("deps check", hint)

    def test_missing_model_safetensors_hint(self) -> None:
        hint = match_error_hint("Could not load sdxl_base.safetensors")
        self.assertIn("deps check", hint)

    def test_no_hint_for_unknown_error(self) -> None:
        hint = match_error_hint("Some random error message")
        self.assertEqual(hint, "")


if __name__ == "__main__":
    unittest.main()
