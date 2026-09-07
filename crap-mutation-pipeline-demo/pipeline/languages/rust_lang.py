import re

from .base import LanguageConfig


def parse_coverage(output: str) -> float:
    match = re.search(r"([\d.]+)% coverage", output)
    if not match:
        raise ValueError("無法從 cargo-tarpaulin 輸出解析出覆蓋率")
    return float(match.group(1)) / 100.0


CONFIG = LanguageConfig(
    name="rust",
    test_cmd=["cargo", "test"],
    coverage_cmd=["cargo", "tarpaulin"],
    parse_coverage=parse_coverage,
)
