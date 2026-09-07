import shutil
import subprocess
from pathlib import Path

import pytest

from pipeline.mutation import run_mutation_testing

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "go"


def _go_test_passes() -> bool:
    result = subprocess.run(["go", "test", "./..."], cwd=EXAMPLE_DIR, capture_output=True)
    return result.returncode == 0


@pytest.mark.skipif(shutil.which("go") is None, reason="go 未安裝")
def test_strengthened_suite_kills_all_mutants_real_go_test():
    source_path = EXAMPLE_DIR / "discount.go"
    original = source_path.read_text()

    result = run_mutation_testing(source_path, _go_test_passes)

    assert result.total >= 1
    assert result.survived == []
    assert result.score == 100.0
    assert source_path.read_text() == original
