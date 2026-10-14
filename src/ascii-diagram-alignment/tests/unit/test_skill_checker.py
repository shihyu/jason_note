"""Regression cases for the installed CJK diagram skill verifier."""

import sys
import unittest
from pathlib import Path


SCRIPTS = Path.home() / ".codex/skills/cjk-ascii-diagram/scripts"
sys.path.insert(0, str(SCRIPTS))

from align import analyze  # noqa: E402
from width import display_width  # noqa: E402


class SkillCheckerTest(unittest.TestCase):
    def test_variation_selector_uses_sequence_display_width(self):
        self.assertEqual(display_width("ℹ️"), 2)
        _, issues = analyze("┌──────────┐\n│ ℹ️ info  │\n└──────────┘")
        self.assertEqual(issues, [])

    def test_mixed_line_junction_connects_vertical_stem(self):
        _, issues = analyze("│\n╪\n│")
        self.assertEqual(issues, [])

    def test_nested_frame_checks_top_and_bottom_edges(self):
        from wcwidth import wcswidth

        def row(inner):
            prefix = "║ " + inner
            return prefix + " " * (16 - wcswidth(prefix)) + "║"

        diagram = "\n".join(row(inner) for inner in (
            "┌────┐", "│ 中文 │", "│ text │", "└────┘"
        ))
        _, issues = analyze(diagram)
        self.assertTrue(any(line == 1 for line, _, _ in issues), issues)
        self.assertTrue(any(line == 4 for line, _, _ in issues), issues)

    def test_arrow_crossing_line_is_not_a_target_box(self):
        _, issues = analyze("▼          ▼\n│◄─┼──────►│")
        self.assertFalse(
            any("misses target box span" in message for _, _, message in issues),
            issues,
        )

    def test_arrow_missing_real_box_is_reported(self):
        _, issues = analyze("▼\n     ┌────┐")
        self.assertTrue(
            any("misses target box span" in message for _, _, message in issues),
            issues,
        )

    def test_table_row_drift_is_still_reported(self):
        _, issues = analyze("┌──────┐\n│ text │\n│ 中文  │\n└──────┘")
        self.assertTrue(
            any("table line display width" in message for _, _, message in issues),
            issues,
        )

    def test_adjacent_connector_is_not_a_table_wall(self):
        _, issues = analyze(
            "┌──────┐      │\n"
            "│ text │      │\n"
            "│ more │      │\n"
            "└──────┘ ┌────┴────┐"
        )
        self.assertFalse(
            any("table line display width" in message for _, _, message in issues),
            issues,
        )


if __name__ == "__main__":
    unittest.main()
