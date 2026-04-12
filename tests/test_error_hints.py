"""Tests for comfyui_skills_cli.error_hints — all error pattern matching."""

from __future__ import annotations

import unittest

from comfyui_skills_cli.error_hints import match_error_hint


class ErrorHintTests(unittest.TestCase):
    # -- Cloud API --
    def test_unauthorized(self) -> None:
        hint = match_error_hint("Unauthorized: Please login first to use this node.")
        self.assertIn("ComfyUI API Key", hint)

    # -- Missing models (specific) --
    def test_vae_not_found(self) -> None:
        hint = match_error_hint("Error: vae model not found in models/vae/")
        self.assertIn("VAE", hint)
        self.assertIn("deps check", hint)

    def test_clip_not_found(self) -> None:
        hint = match_error_hint("clip_vision.safetensors: No such file or directory")
        self.assertIn("CLIP", hint)

    def test_lora_not_found(self) -> None:
        hint = match_error_hint("LoRA model detail_tweaker.safetensors not found")
        self.assertIn("LoRA", hint)

    # -- Missing models (generic) --
    def test_ckpt(self) -> None:
        hint = match_error_hint("FileNotFoundError: model_v1.ckpt not found")
        self.assertIn("deps check", hint)

    def test_safetensors(self) -> None:
        hint = match_error_hint("Could not load sdxl_base.safetensors")
        self.assertIn("deps check", hint)

    # -- Custom nodes --
    def test_class_type_not_found(self) -> None:
        hint = match_error_hint("class_type not found: IPAdapterApply")
        self.assertIn("custom node", hint)

    def test_cannot_find_class(self) -> None:
        hint = match_error_hint("Cannot find class for node type 'ControlNetApply'")
        self.assertIn("custom node", hint)

    # -- Validation --
    def test_invalid_prompt(self) -> None:
        hint = match_error_hint("Error: prompt is not valid")
        self.assertIn("--validate", hint)

    # -- Connection --
    def test_connection_refused(self) -> None:
        hint = match_error_hint("ConnectionError: Connection refused")
        self.assertIn("not running", hint)

    def test_connection_timeout(self) -> None:
        hint = match_error_hint("ConnectionError: Connection timed out")
        self.assertIn("timed out", hint)

    def test_read_timeout(self) -> None:
        hint = match_error_hint("requests.exceptions.ReadTimeout: timeout")
        self.assertIn("timed out", hint)

    # -- GPU / memory --
    def test_cuda_oom(self) -> None:
        hint = match_error_hint("RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB")
        self.assertIn("comfyui-skill free", hint)

    def test_mps_oom(self) -> None:
        hint = match_error_hint("RuntimeError: MPS out of memory")
        self.assertIn("comfyui-skill free", hint)

    def test_cuda_driver_error(self) -> None:
        hint = match_error_hint("RuntimeError: CUDA error: no kernel image is available")
        self.assertIn("GPU driver", hint)

    def test_no_cuda_gpus(self) -> None:
        hint = match_error_hint("AssertionError: no CUDA GPUs are available")
        self.assertIn("GPU driver", hint)

    # -- General file --
    def test_file_not_found(self) -> None:
        hint = match_error_hint("FileNotFoundError: [Errno 2] No such file or directory: 'input.png'")
        self.assertIn("required file is missing", hint)

    # -- No match --
    def test_unknown_error(self) -> None:
        hint = match_error_hint("Some random error message")
        self.assertEqual(hint, "")


if __name__ == "__main__":
    unittest.main()
