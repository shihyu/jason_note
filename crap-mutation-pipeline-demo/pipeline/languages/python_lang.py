import re

from .base import LanguageConfig


def parse_coverage(output: str) -> float:
    match = re.search(r"^TOTAL\s+\d+\s+\d+\s+([\d.]+)%", output, re.MULTILINE)
    if not match:
        raise ValueError("無法從 coverage.py 輸出解析出 TOTAL 覆蓋率")
    return float(match.group(1)) / 100.0


CONFIG = LanguageConfig(
    name="python",
    test_cmd=["python3", "-m", "pytest"],
    coverage_cmd=["coverage", "report"],
    parse_coverage=parse_coverage,
)
