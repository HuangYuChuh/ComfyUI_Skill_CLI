"""Tests for comfyui_skills_cli.commands.run helpers."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer

from comfyui_skills_cli.commands.run import _upload_media


def _ctx() -> typer.Context:
    ctx = MagicMock(spec=typer.Context)
    ctx.obj = {"output_format": "json"}
    return ctx


class UploadMediaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ctx = _ctx()
        self.client = MagicMock()

    def test_rewrites_local_image_path_without_subfolder(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            self.client.upload_image.return_value = {"name": "uploaded.png", "subfolder": "", "type": "input"}
            parameters = {"image": {"type": "image"}}
            args = {"image": f.name}
            _upload_media(self.ctx, self.client, parameters, args)
            self.client.upload_image.assert_called_once_with(f.name)
            self.assertEqual(args["image"], "uploaded.png")

    def test_rewrites_local_image_path_with_subfolder(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            self.client.upload_image.return_value = {"name": "uploaded.png", "subfolder": "clipspace", "type": "input"}
            parameters = {"image": {"type": "image"}}
            args = {"image": f.name}
            _upload_media(self.ctx, self.client, parameters, args)
            self.assertEqual(args["image"], "clipspace/uploaded.png")

    def test_skips_non_existent_path(self) -> None:
        parameters = {"image": {"type": "image"}}
        args = {"image": "/nonexistent/path/to/image.png"}
        _upload_media(self.ctx, self.client, parameters, args)
        self.client.upload_image.assert_not_called()
        self.assertEqual(args["image"], "/nonexistent/path/to/image.png")

    def test_skips_bare_filename(self) -> None:
        parameters = {"image": {"type": "image"}}
        args = {"image": "already_on_server.png"}
        _upload_media(self.ctx, self.client, parameters, args)
        self.client.upload_image.assert_not_called()
        self.assertEqual(args["image"], "already_on_server.png")

    def test_skips_url(self) -> None:
        parameters = {"image": {"type": "image"}}
        args = {"image": "https://example.com/cat.png"}
        _upload_media(self.ctx, self.client, parameters, args)
        self.client.upload_image.assert_not_called()
        self.assertEqual(args["image"], "https://example.com/cat.png")

    def test_skips_non_image_param(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            parameters = {"seed": {"type": "int"}}
            args = {"seed": f.name}
            _upload_media(self.ctx, self.client, parameters, args)
            self.client.upload_image.assert_not_called()
            self.assertEqual(args["seed"], f.name)

    def test_upload_failure_raises_typer_exit(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            self.client.upload_image.side_effect = RuntimeError("server is down")
            parameters = {"image": {"type": "image"}}
            args = {"image": f.name}
            with self.assertRaises(typer.Exit):
                _upload_media(self.ctx, self.client, parameters, args)

    def test_skips_bare_filename_even_when_file_exists_in_cwd(self) -> None:
        # Regression: a bare filename must resolve on the ComfyUI server,
        # never on the caller's cwd. Otherwise `run` becomes cwd-dependent.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "cat.png").touch()
            original_cwd = os.getcwd()
            os.chdir(tmp)
            try:
                parameters = {"image": {"type": "image"}}
                args = {"image": "cat.png"}
                _upload_media(self.ctx, self.client, parameters, args)
                self.client.upload_image.assert_not_called()
                self.assertEqual(args["image"], "cat.png")
            finally:
                os.chdir(original_cwd)

    def test_expands_tilde_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "cat.png"
            test_file.touch()
            self.client.upload_image.return_value = {"name": "cat.png", "subfolder": "", "type": "input"}
            with patch.dict(os.environ, {"HOME": tmp}):
                parameters = {"image": {"type": "image"}}
                args = {"image": "~/cat.png"}
                _upload_media(self.ctx, self.client, parameters, args)
                self.client.upload_image.assert_called_once_with(str(test_file))
                self.assertEqual(args["image"], "cat.png")


if __name__ == "__main__":
    unittest.main()
