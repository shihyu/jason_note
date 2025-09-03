#!/usr/bin/env python3
"""
Threading Lock 基本使用範例
使用 Lock 保護共享資源，確保同一時間只有一個執行緒可以存取
"""

import threading
import time


# 全域變數和鎖
counter = 0
lock = threading.Lock()


def increment_counter():
    """使用 with 語句自動管理鎖"""
    global counter
    for _ in range(100000):
        # 使用 with 語句自動管理鎖
        with lock:
            counter += 1


def increment_manual():
    """手動管理鎖（不推薦的方式）"""
    global counter
    for _ in range(100000):
        # 手動管理鎖
        lock.acquire()
        try:
            counter += 1
        finally:
            lock.release()


def test_lock():
    """測試 Lock 功能"""
    global counter
    counter = 0
    
    print("🧪 測試 threading.Lock")
    print("=" * 50)
    
    start_time = time.time()
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=increment_counter, name=f"Thread-{i}")
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"✅ 最終計數: {counter} (預期: 500000)")
    print(f"⏱️  耗時: {end_time - start_time:.2f} 秒")
    print(f"🎯 正確性: {'✅ 正確' if counter == 500000 else '❌ 錯誤'}")


if __name__ == "__main__":
    test_lock()