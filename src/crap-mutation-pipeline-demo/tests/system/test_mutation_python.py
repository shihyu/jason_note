import subprocess
from pathlib import Path

from pipeline.mutation import run_mutation_testing

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "python"


def _pytest_passes() -> bool:
    result = subprocess.run(
        ["python3", "-m", "pytest", "test_discount.py", "-q"],
        cwd=EXAMPLE_DIR,
        capture_output=True,
    )
    return result.returncode == 0


def test_strengthened_suite_kills_all_mutants_real_pytest():
    source_path = EXAMPLE_DIR / "discount.py"
    result = run_mutation_testing(source_path, _pytest_passes)

    assert result.total >= 1  # discount.py 裡至少有一個可變異的 "<"
    assert result.survived == []
    assert result.score == 100.0
    # 跑完必須還原成原始（未變異）內容
    assert "price < 0" in source_path.read_text()
