from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from comfyui_skills_cli import update_check


class UpdateCheckTests(unittest.TestCase):
    def test_version_comparison_handles_multi_digit_segments(self) -> None:
        self.assertTrue(update_check._is_newer_version("0.2.10", "0.2.3"))
        self.assertFalse(update_check._is_newer_version("0.2.3", "0.2.3"))
        self.assertFalse(update_check._is_newer_version("0.2.3", "0.2.10"))

    def test_notify_skips_disabled_check(self) -> None:
        with patch.object(update_check, "_latest_version_to_check") as latest:
            update_check.maybe_notify_update("0.2.3", disabled=True)
        latest.assert_not_called()

    def test_notify_prints_upgrade_hint_to_stderr(self) -> None:
        with (
            patch.object(update_check, "_latest_version_to_check", return_value="9.9.9"),
            patch.object(update_check, "_upgrade_command", return_value="upgrade now"),
            patch.object(sys.stderr, "write") as write,
        ):
            update_check.maybe_notify_update("0.2.3")

        output = "".join(call.args[0] for call in write.call_args_list)
        self.assertIn("0.2.3 -> 9.9.9", output)
        self.assertIn("upgrade now", output)


if __name__ == "__main__":
    unittest.main()
