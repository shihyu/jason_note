#!/usr/bin/env python3
"""
線程安全裝飾器範例
使用裝飾器模式實現線程安全的方法
"""

import threading
import time
from functools import wraps


class ThreadSafe:
    """線程安全裝飾器類"""
    
    def __init__(self):
        self._lock = threading.Lock()
    
    def synchronized(self, func):
        """同步裝飾器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                return func(*args, **kwargs)
        return wrapper


class Counter:
    """線程安全的計數器"""
    
    def __init__(self):
        self._value = 0
        self._thread_safe = ThreadSafe()
    
    @property
    def increment(self):
        """獲取線程安全的增量方法"""
        return self._thread_safe.synchronized(self._increment)
    
    def _increment(self):
        """內部增量方法"""
        self._value += 1
        return self._value
    
    @property
    def value(self):
        """獲取當前值"""
        return self._value


def worker(counter, worker_id, iterations=10000):
    """工作者執行緒"""
    print(f"👷 工作者 {worker_id} 開始工作")
    
    for i in range(iterations):
        result = counter.increment()
        if i % 2000 == 0:
            print(f"📊 工作者 {worker_id}: 當前值 = {result}")
    
    print(f"✅ 工作者 {worker_id} 完成工作")


def test_decorator_lock():
    """測試裝飾器鎖"""
    print("🧪 測試裝飾器線程安全")
    print("=" * 50)
    
    counter = Counter()
    threads = []
    iterations = 10000
    num_threads = 5
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(counter, i, iterations))
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    expected = num_threads * iterations
    
    print(f"\n📊 測試結果:")
    print(f"✅ 最終計數: {counter.value}")
    print(f"🎯 預期計數: {expected}")
    print(f"⏱️  耗時: {end_time - start_time:.2f} 秒")
    print(f"🏆 正確性: {'✅ 正確' if counter.value == expected else '❌ 錯誤'}")


if __name__ == "__main__":
    test_decorator_lock()