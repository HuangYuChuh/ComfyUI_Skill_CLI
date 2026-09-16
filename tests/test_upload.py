"""Regression tests for upload server selection."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from comfyui_skills_cli.commands.upload import upload_cmd
from comfyui_skills_cli.main import app


class UploadServerOptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def _ctx(self, server: str = "") -> typer.Context:
        ctx = MagicMock(spec=typer.Context)
        ctx.obj = {"base_dir": ".", "server": server, "output_format": "json"}
        return ctx

    @patch("comfyui_skills_cli.commands.upload.ComfyUIClient")
    def test_server_option_is_accepted_after_file(self, client_cls: MagicMock) -> None:
        client_cls.return_value.upload_file.return_value = {
            "name": "image.png", "subfolder": "", "type": "input"
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "image.png"
            image.write_bytes(b"image")
            (root / "config.json").write_text(json.dumps({
                "servers": [
                    {"id": "remote", "url": "http://remote:8188", "auth": "token"}
                ]
            }), encoding="utf-8")

            result = self.runner.invoke(app, [
                "--json", "--dir", tmp, "upload", str(image), "--server", "remote"
            ])

        self.assertEqual(result.exit_code, 0, result.output)
        client_cls.assert_called_once_with(server_url="http://remote:8188", auth="token")

    @patch("comfyui_skills_cli.commands.upload.ComfyUIClient")
    def test_global_server_option_remains_supported(self, client_cls: MagicMock) -> None:
        client_cls.return_value.upload_file.return_value = {
            "name": "image.png", "subfolder": "", "type": "input"
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / "image.png"
            image.write_bytes(b"image")
            (root / "config.json").write_text(json.dumps({
                "servers": [
                    {"id": "remote", "url": "http://remote:8188", "auth": "token"}
                ]
            }), encoding="utf-8")

            result = self.runner.invoke(app, [
                "--json", "--dir", tmp, "--server", "remote", "upload", str(image)
            ])

        self.assertEqual(result.exit_code, 0, result.output)
        client_cls.assert_called_once_with(server_url="http://remote:8188", auth="token")

    @patch("comfyui_skills_cli.commands.upload.ComfyUIClient")
    def test_url_option_is_accepted_without_config(self, client_cls: MagicMock) -> None:
        client_cls.return_value.upload_file.return_value = {
            "name": "image.png", "subfolder": "", "type": "input"
        }
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "image.png"
            image.write_bytes(b"image")
            result = self.runner.invoke(app, [
                "--json", "--dir", tmp, "upload", str(image),
                "--url", "http://remote:8188/",
            ])

        self.assertEqual(result.exit_code, 0, result.output)
        client_cls.assert_called_once_with(server_url="http://remote:8188/", auth="")

    def test_server_and_url_are_mutually_exclusive(self) -> None:
        ctx = self._ctx()
        with patch("comfyui_skills_cli.commands.upload.output_error") as output_error:
            output_error.side_effect = typer.Exit(1)
            with self.assertRaises(typer.Exit):
                upload_cmd(ctx, "image.png", "", False, "", "remote", "http://remote:8188")
            output_error.assert_called_once_with(
                ctx, "CONFLICTING_SERVER", "Provide either --server or --url, not both."
            )


if __name__ == "__main__":
    unittest.main()
