import re

from .base import LanguageConfig


def parse_coverage(output: str) -> float:
    match = re.search(r"All files\s*\|\s*([\d.]+)", output)
    if not match:
        raise ValueError("無法從 c8/nyc 輸出解析出覆蓋率")
    return float(match.group(1)) / 100.0


CONFIG = LanguageConfig(
    name="javascript",
    test_cmd=["node", "--test"],
    coverage_cmd=["c8", "node", "--test"],
    parse_coverage=parse_coverage,
)
