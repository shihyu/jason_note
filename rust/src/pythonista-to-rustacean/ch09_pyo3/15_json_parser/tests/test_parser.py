import json
from multiprocessing import Process, Queue as MPQueue
from threading import Thread
from queue import Queue as TQueue

import pytest
import json_parser # 導入我們用 Rust 編寫的模組

### --- 產生測試資料 ---
@pytest.fixture(scope="session")
def json_logs() -> list[str]:
    """產生一百萬筆 JSON 字串日誌，模擬真實場景"""
    return [
        f'{{"id": {i}, "value": {i * 0.1}, "level": "INFO"}}' for i in range(1_000_000)]

### --- 核心任務函式 ( 供 Python 版本使用) ---
def parse_json_chunk_and_sum(json_strings: list[str], result_queue):
    """
    解析一個 JSON 字串區塊，並將 'value' 欄位的總和放入佇列。
    """
    total = 0
    for string in json_strings:
        try:
            total += json.loads(string)["value"]
        except (json.JSONDecodeError, KeyError):
            continue
    result_queue.put(total)

### --- 待測的三種實作 ---
def run_multiprocessing(all_json_strings: list[str], n_workers: int) -> float:
    """使用多進程 (multiprocessing) 實作"""
    result_queue = MPQueue()
    processes = []
    chunk_size = len(all_json_strings) // n_workers
    for i in range(n_workers):
        start = i * chunk_size
        end = None if i == n_workers - 1 else start + chunk_size
        
        # 核心痛點：這裡的 chunk 會被 pickle 序列化，產生巨大的 I/O 開銷
        chunk = all_json_strings[start:end]
        p = Process(target=parse_json_chunk_and_sum, args=(chunk, result_queue))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()

    return sum(result_queue.get() for _ in range(len(processes)))

def run_threading(all_json_strings: list[str], n_workers: int) -> float:
    """使用多執行緒 (threading) 實作"""
    result_queue = TQueue()
    threads = []
    chunk_size = len(all_json_strings) // n_workers
    for i in range(n_workers):
        start = i * chunk_size
        end = None if i == n_workers - 1 else start + chunk_size
        # 優勢：共享記憶體，chunk 只是原始列表的一個視圖，沒有複製/ 序列化開銷
        chunk = all_json_strings[start:end]
        t = Thread(target=parse_json_chunk_and_sum, args=(chunk, result_queue))
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join()
        
    return sum(result_queue.get() for _ in range(len(threads)))

### --- 基準測試 (Benchmark) ---
def test_multiprocessing(benchmark, json_logs):
    """基準測試 Multiprocessing 版本"""
    benchmark(run_multiprocessing, json_logs, 4)

def test_threading(benchmark, json_logs):
    """基準測試 Threading 版本"""
    benchmark(run_threading, json_logs, 4)

def test_rust_parallel(benchmark, json_logs):
    """基準測試 Rust + Rayon 版本"""
    benchmark(json_parser.parse_and_sum_parallel, json_logs)