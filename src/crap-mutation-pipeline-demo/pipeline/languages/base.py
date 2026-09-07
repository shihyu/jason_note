from dataclasses import dataclass
from typing import Callable, List


@dataclass
class LanguageConfig:
    name: str
    test_cmd: List[str]
    coverage_cmd: List[str]
    parse_coverage: Callable[[str], float]  # 解析工具原始輸出 -> 0.0~1.0 的覆蓋率
