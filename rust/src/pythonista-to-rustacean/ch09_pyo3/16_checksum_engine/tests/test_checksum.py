import pytest
from multiprocessing import Process, Queue as MPQueue
from threading import Thread
from queue import Queue as TQueue

import checksum_engine

# --- 產生測試資料 ---
@pytest.fixture(scope="session")
def string_logs() -> list[str]:
    """產生一百萬筆字串日誌，模擬需要計算 Checksum 的資料"""
    # 模擬簡單的日誌內容，長度適中以凸顯計算成本
    return [f"log_entry_data_{i}_timestamp_{i*100}" for i in range(1_000_000)]

# --- 核心任務函式 (供 Python 版本使用) ---
def calculate_chunk_checksums(logs: list[str], result_queue):
    """
    純 Python 版本的 Checksum 計算。
    這裡使用 sum(s.encode()) 來模擬 CPU 密集型運算。
    """
    chunk_results = []
    for s in logs:
        # 模擬 Rust 的 s.bytes().fold(...)
        # encode() 會產生 bytes，sum() 會將其加總，這是純 CPU 運算
        checksum = sum(s.encode("utf-8"))
        chunk_results.append(checksum)
    
    # 將整個區塊的結果放入佇列
    result_queue.put(chunk_results)

# --- Python 並行實作 ---

def run_multiprocessing(all_logs: list[str], n_workers: int) -> list[int]:
    """使用多進程 (multiprocessing) 實作"""
    result_queue = MPQueue()
    processes = []
    chunk_size = len(all_logs) // n_workers

    for i in range(n_workers):
        start = i * chunk_size
        end = None if i == n_workers - 1 else start + chunk_size
        chunk = all_logs[start:end]
        # 這裡會有巨大的 Pickle 序列化成本
        p = Process(target=calculate_chunk_checksums, args=(chunk, result_queue))
        p.start()
        processes.append(p)

    results = []
    for _ in range(n_workers):
        results.extend(result_queue.get())

    for p in processes:
        p.join()

    return results

def run_threading(all_logs: list[str], n_workers: int) -> list[int]:
    """使用多執行緒 (threading) 實作"""
    result_queue = TQueue()
    threads = []
    chunk_size = len(all_logs) // n_workers

    for i in range(n_workers):
        start = i * chunk_size
        end = None if i == n_workers - 1 else start + chunk_size
        # 共享記憶體，無複製成本，但受 GIL 限制
        chunk = all_logs[start:end]
        t = Thread(target=calculate_chunk_checksums, args=(chunk, result_queue))
        t.start()
        threads.append(t)

    results = []
    for _ in range(n_workers):
        results.extend(result_queue.get())

    for t in threads:
        t.join()

    return results

# --- Benchmark ---

def test_multiprocessing(benchmark, string_logs):
    """基準測試 Multiprocessing 版本"""
    # 預期：最慢，因為大量的字串序列化與反序列化成本
    benchmark(run_multiprocessing, string_logs, 4)

def test_threading(benchmark, string_logs):
    """基準測試 Threading 版本"""
    # 預期：普通，受限於 GIL，實際上是序列執行
    benchmark(run_threading, string_logs, 4)

def test_rust_strategy_1_batch(benchmark, string_logs):
    """
    基準測試 Rust 策略一：隔離計算區塊 (Batch)
    對應 Rust 函式：generate_checksums
    """
    # 預期：最快。
    # 雖然有一次性的 List -> Vec 轉換成本，
    # 但中間的計算完全釋放了 GIL，且沒有頻繁的鎖切換。
    benchmark(checksum_engine.generate_checksums, string_logs)

def test_rust_strategy_2_inplace(benchmark, string_logs):
    """
    基準測試 Rust 策略二：按需取得 GIL (In-Place)
    對應 Rust 函式：generate_checksums_in_place
    """
    # 預先建立一個等長的結果列表 (填滿 0)，供 Rust 就地修改
    # 注意：建立這個列表的時間不應計入 benchmark，所以放在外層
    destination = [0] * len(string_logs)
    
    def run_inplace():
        # 這個函式不回傳新列表，而是直接修改 destination
        checksum_engine.generate_checksums_in_place(string_logs, destination)

    # 預期：比策略一慢，可能與 Threading 持平甚至更慢。
    # 因為在 100 萬次迴圈中，頻繁地 attach/detach GIL
    benchmark(run_inplace)