"""Check diagrams throughout the Rust Markdown notes."""

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = Path.home() / ".codex/skills/cjk-ascii-diagram/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from md_check import check_text  # noqa: E402
from align import analyze  # noqa: E402
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

    def test_tagged_box_diagrams_have_no_drift(self):
        failures = []
        fence = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
        for path in ROOT.rglob("*.md"):
            if path.name == "第二部分_進階部分_量化實戰.md":
                continue  # All Polars boxes are checked by column geometry below.
            lines = path.read_text(encoding="utf-8").splitlines()
            index = 0
            while index < len(lines):
                opening = fence.match(lines[index])
                if opening is None:
                    index += 1
                    continue
                marker = opening.group(1)
                language = opening.group(2).strip().split(" ")[0].lower()
                first_line = index + 2
                index += 1
                body = []
                closing = re.compile(
                    r"^ {0,3}" + re.escape(marker[0]) +
                    "{" + str(len(marker)) + r",}\s*$"
                )
                while index < len(lines) and closing.fullmatch(lines[index]) is None:
                    body.append(lines[index])
                    index += 1
                index += 1
                if language in ("", "text"):
                    continue  # Covered by md_check.py above.
                content = "\n".join(body)
                if not (
                    any(char in content for char in "┌┐└┘╔╗╚╝")
                    or any(line.lstrip().startswith("+---") for line in body)
                ):
                    continue
                _, issues = analyze(content)
                failures.extend(
                    f"{path.relative_to(ROOT)}:{first_line + line - 1}:{col}: {message}"
                    for line, col, message in issues
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
