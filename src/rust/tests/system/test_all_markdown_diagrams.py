"""Check diagrams throughout the Rust Markdown notes."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = Path.home() / ".codex/skills/cjk-ascii-diagram/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from md_check import check_text  # noqa: E402
from wcwidth import wcwidth  # noqa: E402


def columns(line, chars):
    positions = []
    position = 0
    for char in line:
        if char in chars:
            positions.append(position)
        position += wcwidth(char)
    return positions, position


class AllMarkdownDiagramsTest(unittest.TestCase):
    def test_text_diagrams_have_no_drift(self):
        failures = []
        for path in ROOT.rglob("*.md"):
            if path.name == "第二部分_進階部分_量化實戰.md":
                continue  # Polars uses ┆/╪; checked separately below.
            result = check_text(path.read_text(encoding="utf-8"))
            failures.extend(
                f"{path.relative_to(ROOT)}:{line}:{col}: {message}"
                for line, col, message in result.issues
            )
        self.assertEqual(failures, [])

    def test_polars_printed_tables_have_matching_columns(self):
        path = ROOT / "第二部分_進階部分_量化實戰.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        failures = []
        tables = 0
        for top_index, top in enumerate(lines):
            if not top.startswith("┌"):
                continue
            expected, width = columns(top, "┌┬┐")
            if not top.endswith("┐"):
                continue
            tables += 1
            for index in range(top_index + 1, len(lines)):
                line = lines[index]
                if not line.startswith(("│", "╞", "└")):
                    failures.append(f"line {index + 1}: table ends before └")
                    break
                actual, row_width = columns(line, "│┆╞╪╡└┴┘")
                if actual != expected or row_width != width:
                    failures.append(
                        f"line {index + 1}: columns {actual}, width {row_width}; "
                        f"expected {expected}, width {width}"
                    )
                if line.startswith("└"):
                    break
            else:
                failures.append(f"line {top_index + 1}: missing └")
        self.assertGreater(tables, 0)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
