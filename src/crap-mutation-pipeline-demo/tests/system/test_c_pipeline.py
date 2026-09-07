import shutil
import subprocess
from pathlib import Path

import pytest

from pipeline.crap import crap_score, cyclomatic_complexity
from pipeline.languages.c_lang import parse_coverage

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "c"


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc 未安裝")
def test_c_example_cleanup_stage_real_tools():
    for pattern in ("*.gcno", "*.gcda", "*.gcov", "run_tests", "*.o"):
        for f in EXAMPLE_DIR.glob(pattern):
            f.unlink()

    subprocess.run(
        ["gcc", "--coverage", "-O0", "-c", "discount.c", "-o", "discount.o"],
        cwd=EXAMPLE_DIR,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["gcc", "--coverage", "-O0", "-c", "test_discount.c", "-o", "test_discount.o"],
        cwd=EXAMPLE_DIR,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["gcc", "--coverage", "-o", "run_tests", "discount.o", "test_discount.o"],
        cwd=EXAMPLE_DIR,
        check=True,
        capture_output=True,
    )
    subprocess.run(["./run_tests"], cwd=EXAMPLE_DIR, check=True, capture_output=True)
    result = subprocess.run(
        ["gcov", "discount.o"], cwd=EXAMPLE_DIR, check=True, capture_output=True, text=True
    )
    cov = parse_coverage(result.stdout)
    assert cov == 1.0

    source = (EXAMPLE_DIR / "discount.c").read_text()
    comp = cyclomatic_complexity(source, "c")
    assert comp == 3  # if + if + 1

    score = crap_score(comp, cov)
    assert score <= 6
