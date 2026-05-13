"""Regression tests for ``_convert_node_inputs``.

These tests pin down the contract for mapping ``widgets_values`` to API field
names when some widget inputs are also connected to upstream nodes — a known
source of subtle index-misalignment bugs.

Two ComfyUI editor serialization formats must be handled:

  Verbose (comfy-core 0.3.71 and earlier):
    ``node["inputs"]`` lists every widget input. Connected ones have a
    ``link`` field; unconnected ones don't. ``widgets_values`` is a flat list
    aligned to this same order.

  Compact (comfy-core 0.3.73+):
    ``node["inputs"]`` only lists widget inputs that are *connected*.
    Unconnected widget fields are omitted entirely. ``widgets_values`` still
    contains an entry per widget (in schema order), including the ones whose
    inputs were promoted to connections.

The fixtures below are minimal extracts of real Flux2 workflows that exhibited
the bug described in PR #36.
"""

from __future__ import annotations

import unittest
from typing import Any

from comfyui_skills_cli.commands.workflow import _convert_node_inputs


# Schema for EmptyFlux2LatentImage as ComfyUI's /object_info reports it.
EMPTY_FLUX2_NODE_INFO: dict[str, Any] = {
    "input_order": {"required": ["width", "height", "batch_size"]},
    "input": {
        "required": {
            "width": ["INT", {"default": 1024, "min": 16, "max": 16384, "step": 16}],
            "height": ["INT", {"default": 1024, "min": 16, "max": 16384, "step": 16}],
            "batch_size": ["INT", {"default": 1, "min": 1, "max": 4096}],
        }
    },
}


# Schema for KSampler, mixing connection-only types (MODEL/CONDITIONING/LATENT)
# with widget types (INT/FLOAT/STRING) and COMBO widgets (lists in type slot).
KSAMPLER_NODE_INFO: dict[str, Any] = {
    "input_order": {
        "required": [
            "model", "seed", "steps", "cfg", "sampler_name",
            "scheduler", "positive", "negative", "latent_image", "denoise",
        ]
    },
    "input": {
        "required": {
            "model": ["MODEL"],
            "seed": ["INT", {"default": 0, "control_after_generate": True}],
            "steps": ["INT", {"default": 20}],
            "cfg": ["FLOAT", {"default": 8.0}],
            "sampler_name": [["euler", "euler_ancestral", "dpmpp_2m"]],
            "scheduler": [["normal", "karras", "simple"]],
            "positive": ["CONDITIONING"],
            "negative": ["CONDITIONING"],
            "latent_image": ["LATENT"],
            "denoise": ["FLOAT", {"default": 1.0}],
        }
    },
}


def _link_map_for_connected_slots(node: dict[str, Any]) -> dict[tuple[int, int], tuple[str, int]]:
    """Build a minimal link_map for the connected slots of *node*."""
    node_id = int(node["id"])
    return {
        (node_id, i): ("upstream", 0)
        for i, slot in enumerate(node.get("inputs", []))
        if isinstance(slot, dict) and slot.get("link") is not None
    }


class ConvertNodeInputsCompactFormatTests(unittest.TestCase):
    """comfy-core 0.3.73+: only connected widget inputs are listed in inputs[]."""

    def test_emptyflux2_with_width_height_connected(self) -> None:
        """Real-world fixture: extracted from a Klein_9B_Base Flux2 workflow.

        width and height are connected; batch_size is a pure widget with value
        1. widgets_values keeps placeholders for all three widget positions.
        """
        node = {
            "id": 91,
            "type": "EmptyFlux2LatentImage",
            "inputs": [
                {"name": "width", "type": "INT", "widget": {"name": "width"}, "link": 327},
                {"name": "height", "type": "INT", "widget": {"name": "height"}, "link": 330},
            ],
            "widgets_values": [832, 1216, 1],
        }
        link_map = _link_map_for_connected_slots(node)

        out = _convert_node_inputs(node, node["type"], EMPTY_FLUX2_NODE_INFO, link_map)

        self.assertEqual(out["width"], ["upstream", 0])
        self.assertEqual(out["height"], ["upstream", 0])
        # batch_size MUST come from widgets_values[2] (the widget default),
        # not get dropped, and not pick up widgets_values[0] = 832.
        self.assertEqual(out["batch_size"], 1)


class ConvertNodeInputsVerboseFormatTests(unittest.TestCase):
    """comfy-core 0.3.71: every widget input is listed in inputs[]."""

    def test_emptyflux2_with_width_height_connected(self) -> None:
        """Same logical scenario as compact format, different serialization.

        Extracted from a FLUX 2.0 Text-to-Image workflow. The unconnected
        batch_size still appears in inputs[] (without a link field).
        """
        node = {
            "id": 28,
            "type": "EmptyFlux2LatentImage",
            "inputs": [
                {"name": "width", "type": "INT", "widget": {"name": "width"}, "link": 31},
                {"name": "height", "type": "INT", "widget": {"name": "height"}, "link": 30},
                {"name": "batch_size", "type": "INT", "widget": {"name": "batch_size"}},
            ],
            "widgets_values": [1248, 2784, 1],
        }
        link_map = _link_map_for_connected_slots(node)

        out = _convert_node_inputs(node, node["type"], EMPTY_FLUX2_NODE_INFO, link_map)

        self.assertEqual(out["width"], ["upstream", 0])
        self.assertEqual(out["height"], ["upstream", 0])
        # Same expectation as compact: batch_size aligns to widgets_values[2].
        self.assertEqual(out["batch_size"], 1)


class ConvertNodeInputsMixedTypesTests(unittest.TestCase):
    """KSampler — connection types, widget types, COMBOs, and control_after_generate."""

    def test_ksampler_all_widgets_default(self) -> None:
        """Model/positive/negative/latent_image are connected; widgets at defaults.

        widgets_values contains a 'fixed' string immediately after seed — this
        is the control_after_generate placeholder that the converter must
        consume without assigning it to a field.
        """
        node = {
            "id": 3,
            "type": "KSampler",
            "inputs": [
                {"name": "model", "type": "MODEL", "link": 1},
                {"name": "positive", "type": "CONDITIONING", "link": 2},
                {"name": "negative", "type": "CONDITIONING", "link": 3},
                {"name": "latent_image", "type": "LATENT", "link": 4},
            ],
            "widgets_values": [42, "fixed", 20, 8.0, "euler", "normal", 1.0],
        }
        link_map = _link_map_for_connected_slots(node)

        out = _convert_node_inputs(node, node["type"], KSAMPLER_NODE_INFO, link_map)

        self.assertEqual(out["model"], ["upstream", 0])
        self.assertEqual(out["positive"], ["upstream", 0])
        self.assertEqual(out["negative"], ["upstream", 0])
        self.assertEqual(out["latent_image"], ["upstream", 0])
        self.assertEqual(out["seed"], 42)
        self.assertEqual(out["steps"], 20)
        self.assertEqual(out["cfg"], 8.0)
        self.assertEqual(out["sampler_name"], "euler")
        self.assertEqual(out["scheduler"], "normal")
        self.assertEqual(out["denoise"], 1.0)
        # 'fixed' is a control_after_generate marker, not a field value.
        self.assertNotIn("fixed", out.values())


class ConvertNodeInputsEdgeCaseTests(unittest.TestCase):
    def test_all_widgets_connected_produces_no_widget_fields(self) -> None:
        """If every widget input is also connected, widgets_values is consumed
        purely as placeholders and no widget keys appear in the output."""
        node = {
            "id": 5,
            "type": "EmptyFlux2LatentImage",
            "inputs": [
                {"name": "width", "type": "INT", "widget": {"name": "width"}, "link": 50},
                {"name": "height", "type": "INT", "widget": {"name": "height"}, "link": 51},
                {"name": "batch_size", "type": "INT", "widget": {"name": "batch_size"}, "link": 52},
            ],
            "widgets_values": [1024, 1024, 1],
        }
        link_map = _link_map_for_connected_slots(node)

        out = _convert_node_inputs(node, node["type"], EMPTY_FLUX2_NODE_INFO, link_map)

        self.assertEqual(
            out,
            {
                "width": ["upstream", 0],
                "height": ["upstream", 0],
                "batch_size": ["upstream", 0],
            },
        )


if __name__ == "__main__":
    unittest.main()
