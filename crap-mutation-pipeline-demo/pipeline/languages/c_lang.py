import re

from .base import LanguageConfig


def parse_coverage(output: str) -> float:
    match = re.search(r"Lines executed:([\d.]+)% of \d+", output)
    if not match:
        raise ValueError("無法從 gcov 輸出解析出覆蓋率")
    return float(match.group(1)) / 100.0


# C 沒有單一指令能「編譯+執行+算覆蓋率」，需要先用 --coverage 編譯、跑過測試執行檔，
# 再對目標 .o 檔跑 gcov。test_cmd/coverage_cmd 這裡只記錄「最後一步」的指令片段，
# 實際編譯流程由呼叫端（system test / Stage3 orchestration）自行組裝。
CONFIG = LanguageConfig(
    name="c",
    test_cmd=["./run_tests"],
    coverage_cmd=["gcov"],
    parse_coverage=parse_coverage,
)
