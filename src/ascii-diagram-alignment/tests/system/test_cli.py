"""Scan a Markdown directory through the command-line entry point."""

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures"


class DiagramScanCliTest(unittest.TestCase):
    def test_check_reports_drift_in_tagged_block_with_source_line(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scan.py"), "--root", str(FIXTURES), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("sample.md:11:", result.stdout)
        self.assertNotIn("sample.md:5:", result.stdout)


    def test_check_reports_drift_in_indented_block_with_source_line(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scan.py"), "--root", str(FIXTURES / "indented.md"), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("indented.md:4:", result.stdout)

    def test_scan_entire_src_tree_from_cli(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scan.py"), "--root", str(ROOT.parent)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = re.search(
            r"Scanned (\d+) Markdown files, (\d+) diagram blocks, (\d+) findings",
            result.stdout,
        )
        self.assertIsNotNone(summary)
        self.assertGreater(int(summary.group(1)), 4000)
        self.assertGreater(int(summary.group(2)), 1000)
        self.assertIn("ascii-diagram-alignment/tests/fixtures/sample.md:11:", result.stdout)


if __name__ == "__main__":
    unittest.main()
