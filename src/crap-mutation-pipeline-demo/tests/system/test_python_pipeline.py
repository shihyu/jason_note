import subprocess
from pathlib import Path

from pipeline.crap import crap_score, cyclomatic_complexity
from pipeline.languages.python_lang import CONFIG

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "python"


def test_python_example_cleanup_stage_real_tools():
    subprocess.run(
        ["coverage", "run", "-m", "pytest", "test_discount.py"],
        cwd=EXAMPLE_DIR,
        check=True,
        capture_output=True,
    )
    report = subprocess.run(
        CONFIG.coverage_cmd + ["discount.py"],
        cwd=EXAMPLE_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    cov = CONFIG.parse_coverage(report.stdout)
    assert cov == 1.0  # 三個測試已覆蓋所有分支

    source = (EXAMPLE_DIR / "discount.py").read_text()
    comp = cyclomatic_complexity(source, "python")
    assert comp == 3  # if + if + 1

    score = crap_score(comp, cov)
    assert score <= 6  # Cleanup 階段門檻
