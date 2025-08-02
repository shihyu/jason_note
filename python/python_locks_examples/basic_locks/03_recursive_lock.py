#!/usr/bin/env python3
"""
RLock (遞迴鎖) 使用範例
演示遞迴函數中需要重複獲得同一個鎖的情況
"""

import threading
import time


class RecursiveCounter:
    """支援遞迴操作的計數器"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.RLock()  # 使用 RLock
    
    def increment(self, n=1):
        """遞迴增量方法"""
        with self._lock:
            if n > 1:
                # 遞迴呼叫，需要再次獲得鎖
                self.increment(n-1)
            self._value += 1
            thread_name = threading.current_thread().name
            print(f"📈 執行緒 {thread_name}: 值 = {self._value} (剩餘遞迴: {n-1})")
    
    def get_value(self):
        """獲取當前值"""
        with self._lock:
            return self._value


class BadRecursiveCounter:
    """錯誤示範：使用普通 Lock 會導致死鎖"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()  # 普通Lock
    
    def increment(self, n=1):
        """會造成死鎖的遞迴方法"""
        with self._lock:
            if n > 1:
                # 💀 死鎖！同一執行緒無法再次獲得Lock
                self.increment(n-1)
            self._value += 1


def worker(counter, worker_id, depth=3):
    """工作者執行緒"""
    thread_name = threading.current_thread().name
    print(f"🚀 {thread_name} 開始遞迴操作 (深度: {depth})")
    
    try:
        counter.increment(depth)  # 遞迴呼叫
        print(f"✅ {thread_name} 完成操作")
    except Exception as e:
        print(f"❌ {thread_name} 發生錯誤: {e}")


def test_recursive_lock():
    """測試遞迴鎖"""
    print("🧪 測試 threading.RLock (遞迴鎖)")
    print("=" * 50)
    
    counter = RecursiveCounter()
    threads = []
    num_threads = 3
    recursion_depth = 3
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(counter, i, recursion_depth), name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    expected = num_threads * recursion_depth
    
    print(f"\n📊 測試結果:")
    print(f"✅ 最終值: {counter.get_value()}")
    print(f"🎯 預期值: {expected}")
    print(f"⏱️  耗時: {end_time - start_time:.2f} 秒")
    print(f"🏆 正確性: {'✅ 正確' if counter.get_value() == expected else '❌ 錯誤'}")


def demonstrate_deadlock():
    """演示普通 Lock 在遞迴中會造成死鎖"""
    print("\n⚠️  演示：普通 Lock 在遞迴中會造成死鎖")
    print("=" * 50)
    print("注意：這個範例會造成死鎖，請謹慎運行！")
    
    # 取消註解下面的程式碼來演示死鎖
    # counter = BadRecursiveCounter()
    # try:
    #     counter.increment(2)  # 這會造成死鎖
    # except Exception as e:
    #     print(f"❌ 發生錯誤: {e}")
    
    print("💡 提示：如果使用普通 Lock，程式會在這裡停止回應")


if __name__ == "__main__":
    test_recursive_lock()
    demonstrate_deadlock()