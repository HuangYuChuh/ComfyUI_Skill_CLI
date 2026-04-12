"""Tests for comfyui_skills_cli.commands.nodes — helper functions."""

from __future__ import annotations

import unittest

from comfyui_skills_cli.commands.nodes import _flatten_nodes

SAMPLE_OBJECT_INFO = {
    "KSampler": {
        "display_name": "KSampler",
        "description": "Samples latents",
        "category": "sampling",
    },
    "CLIPTextEncode": {
        "display_name": "CLIP Text Encode",
        "description": "",
        "category": "conditioning",
    },
}


class FlattenNodesTests(unittest.TestCase):
    def test_all(self) -> None:
        rows = _flatten_nodes(SAMPLE_OBJECT_INFO)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["category"], "conditioning")
        self.assertEqual(rows[1]["category"], "sampling")

    def test_with_category_filter(self) -> None:
        rows = _flatten_nodes(SAMPLE_OBJECT_INFO, "sampling")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["class_type"], "KSampler")

    def test_nonexistent_category(self) -> None:
        rows = _flatten_nodes(SAMPLE_OBJECT_INFO, "nonexistent")
        self.assertEqual(len(rows), 0)


class WsAvailableTests(unittest.TestCase):
    def test_returns_bool(self) -> None:
        from comfyui_skills_cli.commands.run import _ws_available
        self.assertIsInstance(_ws_available(), bool)


if __name__ == "__main__":
    unittest.main()
