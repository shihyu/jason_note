import shutil
import subprocess
from pathlib import Path

import pytest

from pipeline.crap import crap_score, cyclomatic_complexity
from pipeline.languages.rust_lang import CONFIG

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "rust"


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo 未安裝")
def test_rust_example_cleanup_stage_real_tools():
    result = subprocess.run(
        CONFIG.coverage_cmd,
        cwd=EXAMPLE_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    cov = CONFIG.parse_coverage(result.stdout)
    assert cov == 1.0

    source = (EXAMPLE_DIR / "src" / "lib.rs").read_text()
    comp = cyclomatic_complexity(source, "rust")
    assert comp == 3  # if + if + 1

    score = crap_score(comp, cov)
    assert score <= 6
