"""Verify the lock-selection diagram stays aligned in the rendered Markdown."""

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = Path(
    "/home/shihyu/.codex/skills/cjk-ascii-diagram/scripts/md_check.py"
)


class RustLocksDiagramTest(unittest.TestCase):
    def test_lock_selection_diagram_has_no_drift(self):
        result = subprocess.run(
            ["python3", str(CHECKER), "rust_locks_guide.md"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
