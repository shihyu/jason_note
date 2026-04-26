import pytest
from concurrent.futures import ThreadPoolExecutor
import json_parser

@pytest.fixture(scope="session")
def json_logs_small() -> list[str]:
    """產生一個規模稍小的資料集，因為我們會在單一測試中執行它兩次。"""
    return [f'{{"id": {i}, "value": {i * 0.1}}}' for i in range(500_000)]

def run_twice_in_threads(func, data):
    """使用一個有 2 個 worker 的執行緒池，同時呼叫指定的 func 兩次。"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(func, data)
        future2 = executor.submit(func, data)
        # 等待兩個任務都完成並加總結果
        return future1.result() + future2.result()

def test_sequential_from_threads(benchmark, json_logs_small):
    """
    測試：從 Python 執行緒呼叫【未釋放 GIL】的循序 Rust 函式。
    預期：耗時約為單次執行的 2 倍，因為 GIL 導致循序執行。
    """
    benchmark(
        run_twice_in_threads,
        json_parser.parse_and_sum_sequential,
        json_logs_small,
    )

def test_sequential_detached_from_threads(benchmark, json_logs_small):
    """
    測試：從 Python 執行緒呼叫【已釋放 GIL】的循序 Rust 函式。
    預期：耗時約為單次執行的 1 倍，因為兩個呼叫可以真正並行。
    """
    benchmark(
        run_twice_in_threads,
        json_parser.parse_and_sum_sequential_detached,
        json_logs_small,
    )