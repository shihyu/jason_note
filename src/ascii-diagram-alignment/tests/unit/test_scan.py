"""Behavior and boundary cases for Markdown diagram detection."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scan import analyze_block, is_diagram, parse_fences  # noqa: E402


class DiagramScanUnitTest(unittest.TestCase):
    def test_parse_fences_keeps_language_and_original_line(self):
        blocks = parse_fences("# Title\n\n```plain\n+---+\n| x |\n+---+\n```\n")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].first_line, 4)
        self.assertEqual(blocks[0].language, "plain")
        self.assertEqual(blocks[0].lines[0], "+---+")

    def test_is_diagram_ignores_plain_code_and_accepts_tree(self):
        plain = parse_fences("```go\nfunc main() {}\n```")[0]
        tree = parse_fences("```text\nroot\n├─ child\n└─ leaf\n```")[0]
        self.assertFalse(is_diagram(plain))
        self.assertTrue(is_diagram(tree))

    def test_parse_fences_marks_missing_closing_fence(self):
        block = parse_fences("```text\n┌──┐\n│ x│")[0]
        self.assertFalse(block.closed)
        self.assertEqual(analyze_block(block)[0].message, "code block is not closed")

    def test_analyze_block_reports_cjk_border_drift(self):
        block = parse_fences("```text\n┌──────┐\n│ 中文  │\n└──────┘\n```")[0]
        issues = analyze_block(block)
        self.assertTrue(issues)
        self.assertTrue(any(issue.line == 3 for issue in issues))

    def test_analyze_block_preserves_emoji(self):
        source = "```text\n┌──────────┐\n│ 🔑 鑰匙  │\n└──────────┘\n```"
        block = parse_fences(source)[0]
        analyze_block(block)
        self.assertIn("🔑", "\n".join(block.lines))

    def test_aligned_variation_selector_emoji_is_not_reported(self):
        source = "```text\n┌──────────┐\n│ ℹ️ info  │\n└──────────┘\n```"
        block = parse_fences(source)[0]
        self.assertEqual(analyze_block(block), [])

    def test_nested_box_corners_are_checked_against_content_rows(self):
        from wcwidth import wcswidth

        def row(inner):
            prefix = "║ " + inner
            return prefix + " " * (16 - wcswidth(prefix)) + "║"

        source = "```text\n" + "\n".join(
            row(inner)
            for inner in (
                "┌────┐",
                "│ 中文 │",
                "│ text │",
                "└────┘",
            )
        ) + "\n```"
        block = parse_fences(source)[0]
        issues = analyze_block(block)
        self.assertTrue(any(issue.line == 2 for issue in issues), issues)
        self.assertTrue(any(issue.line == 5 for issue in issues), issues)

    def test_aligned_polars_output_is_not_reported_as_drift(self):
        source = "```text\n┌─────┬─────┐\n│ a   ┆ b   │\n╞═════╪═════╡\n│ 1   ┆ 2   │\n└─────┴─────┘\n```"
        block = parse_fences(source)[0]
        self.assertEqual(analyze_block(block), [])


if __name__ == "__main__":
    unittest.main()
