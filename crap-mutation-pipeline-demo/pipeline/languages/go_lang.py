import re

from .base import LanguageConfig


def parse_coverage(output: str) -> float:
    match = re.search(r"coverage:\s+([\d.]+)%\s+of statements", output)
    if not match:
        raise ValueError("無法從 go test -cover 輸出解析出覆蓋率")
    return float(match.group(1)) / 100.0


CONFIG = LanguageConfig(
    name="go",
    test_cmd=["go", "test", "./..."],
    coverage_cmd=["go", "test", "-cover", "./..."],
    parse_coverage=parse_coverage,
)
