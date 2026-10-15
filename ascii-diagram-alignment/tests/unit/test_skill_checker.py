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

    def test_open_flow_stems_can_end_at_text_nodes(self):
        _, issues = analyze("│\n標籤\n│\n✓ 完成")
        self.assertEqual(issues, [])

    def test_single_row_box_with_cjk_overflow_is_reported(self):
        _, issues = analyze("┌────┐\n│ 中文 │\n└────┘")
        self.assertTrue(issues, issues)

    def test_flow_labels_and_horizontal_arrows_are_not_seam_kinks(self):
        _, issues = analyze(
            "                  │   │    │              │  │   │\n"
            "              STW掃描 並發 STW結束       前→後→存活  下次觸發門檻"
        )
        self.assertFalse(any("seam kink" in message for _, _, message in issues), issues)

    def test_tapered_pyramid_walls_are_not_seam_kinks(self):
        _, issues = analyze("  ┌───┐\n  │C/│\n │Rust│\n│Zig/C│")
        self.assertEqual(issues, [])

    def test_arrow_embedded_in_box_top_is_not_a_wall_kink(self):
        _, issues = analyze(
            "                       │      │        │\n"
            "                  ┌────▼───┐ ┌▼────┐  ┌▼─────────┐\n"
            "                  │  D1    │ │ KV  │  │   R2     │"
        )
        self.assertFalse(any("seam kink" in message for _, _, message in issues), issues)

    def test_unjustified_vertical_run_shift_is_reported(self):
        _, issues = analyze("│\n │\n │")
        self.assertTrue(any("seam kink" in message for _, _, message in issues), issues)

    def test_horizontal_exit_junction_preserves_frame_wall(self):
        diagram = (
            "┌───────────────────────────────┐\n"
            "│ itab ────────────────┐        │\n"
            "│                      ▼        │\n"
            "│        ┌───────────────────┐  │\n"
            "│        │ type: Dog         │  │\n"
            "│        │ method table      │  │\n"
            "│        │  Speak → func ptr │──┼──→ func(Dog) Speak\n"
            "│        └───────────────────┘  │\n"
            "│                               │\n"
            "└───────────────────────────────┘"
        )
        _, issues = analyze(diagram)
        self.assertFalse(any("frame right wall" in message for _, _, message in issues), issues)

    def test_ascii_plus_table_cjk_overflow_is_reported(self):
        _, issues = analyze("+------+\n| 中文  |\n+------+")
        self.assertTrue(any("ASCII table" in message for _, _, message in issues), issues)

    def test_ascii_staircase_rows_have_independent_left_edges(self):
        _, issues = analyze("+----------+\n|main      |\n+--+-------+\n   |a     |\n   +--+---+")
        self.assertEqual(issues, [])

    def test_ascii_merged_cell_is_clean(self):
        _, issues = analyze("+----+----+\n| header  |\n+----+----+")
        self.assertEqual(issues, [])

    def test_ascii_internal_separator_drift_is_reported(self):
        _, issues = analyze("+----+----+\n| a   |b  |\n+----+----+")
        self.assertTrue(any("ASCII table" in message for _, _, message in issues), issues)

    def test_aligned_ascii_plus_table_is_clean(self):
        _, issues = analyze("+------+\n| 中文 |\n+------+")
        self.assertEqual(issues, [])

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
