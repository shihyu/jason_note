#!/usr/bin/env python3
"""
鎖效能比較與最佳實踐範例
比較不同鎖機制的效能，展示最佳實踐
"""

import threading
import time
import concurrent.futures
from contextlib import contextmanager
import functools
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class PerformanceResult:
    """效能測試結果"""
    lock_type: str
    execution_time: float
    final_value: int
    expected_value: int
    is_correct: bool
    operations_per_second: float


class PerformanceTester:
    """效能測試器"""
    
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()
        self.rlock = threading.RLock()
        self.condition = threading.Condition()
        self.semaphore = threading.Semaphore(1)  # 模擬互斥鎖
        self.results: List[PerformanceResult] = []
    
    @contextmanager
    def timer(self, name: str, iterations: int, num_threads: int):
        """計時器上下文管理器"""
        self.counter = 0  # 重置計數器
        start = time.time()
        yield
        end = time.time()
        
        execution_time = end - start
        expected = iterations * num_threads
        is_correct = self.counter == expected
        ops_per_second = expected / execution_time if execution_time > 0 else 0
        
        result = PerformanceResult(
            lock_type=name,
            execution_time=execution_time,
            final_value=self.counter,
            expected_value=expected,
            is_correct=is_correct,
            operations_per_second=ops_per_second
        )
        
        self.results.append(result)
        print(f"📊 {name}: {execution_time:.4f}s, "
              f"結果: {self.counter}/{expected}, "
              f"速度: {ops_per_second:.0f} ops/s, "
              f"{'✅' if is_correct else '❌'}")
    
    def test_no_lock(self, iterations: int, num_threads: int):
        """無鎖測試（不安全）"""
        def worker():
            for _ in range(iterations):
                self.counter += 1
        
        with self.timer("無鎖 (不安全)", iterations, num_threads):
            threads = [threading.Thread(target=worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_lock(self, iterations: int, num_threads: int):
        """Lock 測試"""
        def worker():
            for _ in range(iterations):
                with self.lock:
                    self.counter += 1
        
        with self.timer("threading.Lock", iterations, num_threads):
            threads = [threading.Thread(target=worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_rlock(self, iterations: int, num_threads: int):
        """RLock 測試"""
        def worker():
            for _ in range(iterations):
                with self.rlock:
                    self.counter += 1
        
        with self.timer("threading.RLock", iterations, num_threads):
            threads = [threading.Thread(target=worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_semaphore(self, iterations: int, num_threads: int):
        """Semaphore 測試"""
        def worker():
            for _ in range(iterations):
                with self.semaphore:
                    self.counter += 1
        
        with self.timer("threading.Semaphore(1)", iterations, num_threads):
            threads = [threading.Thread(target=worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_thread_local(self, iterations: int, num_threads: int):
        """Thread-local 測試"""
        local_data = threading.local()
        results = []
        results_lock = threading.Lock()
        
        def worker():
            local_data.counter = 0
            for _ in range(iterations):
                local_data.counter += 1
            
            with results_lock:
                results.append(local_data.counter)
        
        with self.timer("threading.local", iterations, num_threads):
            threads = [threading.Thread(target=worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            # 匯總結果
            self.counter = sum(results)
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取測試摘要"""
        if not self.results:
            return {}
        
        fastest = min(self.results, key=lambda x: x.execution_time)
        slowest = max(self.results, key=lambda x: x.execution_time)
        most_efficient = max(self.results, key=lambda x: x.operations_per_second)
        
        return {
            'total_tests': len(self.results),
            'fastest': fastest,
            'slowest': slowest,
            'most_efficient': most_efficient,
            'all_correct': all(r.is_correct for r in self.results)
        }


class BestPracticesDemo:
    """最佳實踐演示"""
    
    @staticmethod
    def good_lock_usage():
        """✅ 好的做法：使用 with 語句"""
        print("✅ 好的做法：使用 with 語句")
        lock = threading.Lock()
        shared_data = []
        
        def worker():
            with lock:  # 自動釋放，即使發生異常
                shared_data.append("data")
                # 即使這裡拋出異常，鎖也會被正確釋放
                if len(shared_data) > 5:
                    pass  # 模擬可能的異常情況
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"   共享資料: {len(shared_data)} 項")
    
    @staticmethod
    def bad_lock_usage_demo():
        """❌ 不好的做法演示（僅供說明）"""
        print("❌ 不好的做法：手動管理鎖（容易出錯）")
        print("   這種方式如果發生異常，鎖可能永遠不會被釋放")
        print("   建議總是使用 with 語句")
    
    @staticmethod
    def avoid_deadlock():
        """✅ 好的做法：避免死鎖"""
        print("✅ 好的做法：避免死鎖 - 統一鎖定順序")
        
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        results = []
        
        def worker1():
            with lock1:  # 統一的鎖定順序
                time.sleep(0.1)
                with lock2:
                    results.append("worker1")
        
        def worker2():
            with lock1:  # 相同的順序，避免死鎖
                time.sleep(0.1)
                with lock2:
                    results.append("worker2")
        
        threads = [threading.Thread(target=worker1), threading.Thread(target=worker2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"   結果: {results}")
    
    @staticmethod
    def minimize_lock_time():
        """✅ 好的做法：最小化鎖的持有時間"""
        print("✅ 好的做法：最小化鎖的持有時間")
        
        lock = threading.Lock()
        shared_data = []
        
        def worker(worker_id):
            # 在鎖外進行準備工作
            prepared_data = f"data-{worker_id}-{time.time()}"
            time.sleep(0.1)  # 模擬昂貴的計算
            
            # 只在必要時持有鎖
            with lock:
                shared_data.append(prepared_data)
            
            # 在鎖外進行後續處理
            time.sleep(0.05)  # 模擬後續處理
        
        start_time = time.time()
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"   處理了 {len(shared_data)} 項資料，耗時 {time.time() - start_time:.2f}s")
    
    @staticmethod
    def appropriate_granularity():
        """✅ 好的做法：使用適當的鎖粒度"""
        print("✅ 好的做法：使用適當的鎖粒度")
        
        # 為不同的資源使用不同的鎖
        user_data_lock = threading.Lock()
        log_data_lock = threading.Lock()
        
        user_data = []
        log_data = []
        
        def update_user(user_id):
            with user_data_lock:  # 只鎖定用戶資料
                user_data.append(f"user-{user_id}")
                time.sleep(0.05)
        
        def write_log(message):
            with log_data_lock:  # 只鎖定日誌資料
                log_data.append(message)
                time.sleep(0.02)
        
        def worker(worker_id):
            update_user(worker_id)
            write_log(f"Updated user {worker_id}")
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"   用戶資料: {len(user_data)} 項，日誌: {len(log_data)} 項")


class LockTimeoutDemo:
    """鎖超時演示"""
    
    @staticmethod
    def timeout_handling():
        """鎖的超時處理"""
        print("🕐 鎖超時處理演示")
        
        slow_lock = threading.Lock()
        results = []
        
        def slow_worker():
            """慢工作者，持有鎖較長時間"""
            if slow_lock.acquire(timeout=0.1):
                try:
                    print("   😴 慢工作者獲得鎖，工作3秒...")
                    time.sleep(3)
                    results.append("slow_work_done")
                finally:
                    slow_lock.release()
            else:
                results.append("slow_work_timeout")
        
        def fast_worker(worker_id):
            """快工作者，嘗試快速獲取鎖"""
            if slow_lock.acquire(timeout=1.0):
                try:
                    print(f"   ⚡ 快工作者 {worker_id} 獲得鎖")
                    time.sleep(0.1)
                    results.append(f"fast_work_{worker_id}")
                finally:
                    slow_lock.release()
            else:
                print(f"   ⏰ 快工作者 {worker_id} 獲取鎖超時")
                results.append(f"fast_work_{worker_id}_timeout")
        
        # 啟動慢工作者
        slow_thread = threading.Thread(target=slow_worker)
        slow_thread.start()
        
        time.sleep(0.5)  # 確保慢工作者先獲得鎖
        
        # 啟動快工作者
        fast_threads = [threading.Thread(target=fast_worker, args=(i,)) for i in range(2)]
        for t in fast_threads:
            t.start()
        
        # 等待所有執行緒完成
        slow_thread.join()
        for t in fast_threads:
            t.join()
        
        print(f"   結果: {results}")
    
    @staticmethod
    def non_blocking_attempt():
        """非阻塞鎖嘗試"""
        print("🚫 非阻塞鎖嘗試演示")
        
        busy_lock = threading.Lock()
        results = []
        
        def busy_worker():
            """忙碌工作者"""
            with busy_lock:
                print("   🔒 忙碌工作者獲得鎖")
                time.sleep(2)
                results.append("busy_work_done")
        
        def polling_worker(worker_id):
            """輪詢工作者"""
            attempts = 0
            while attempts < 5:
                if busy_lock.acquire(blocking=False):  # 非阻塞嘗試
                    try:
                        print(f"   ✅ 輪詢工作者 {worker_id} 在第 {attempts + 1} 次嘗試中獲得鎖")
                        results.append(f"polling_work_{worker_id}")
                        return
                    finally:
                        busy_lock.release()
                else:
                    attempts += 1
                    print(f"   ⏳ 輪詢工作者 {worker_id} 第 {attempts} 次嘗試失敗，等待0.5s")
                    time.sleep(0.5)
            
            print(f"   😞 輪詢工作者 {worker_id} 放棄嘗試")
            results.append(f"polling_work_{worker_id}_failed")
        
        # 啟動忙碌工作者
        busy_thread = threading.Thread(target=busy_worker)
        busy_thread.start()
        
        time.sleep(0.2)  # 確保忙碌工作者先獲得鎖
        
        # 啟動輪詢工作者
        polling_threads = [threading.Thread(target=polling_worker, args=(i,)) for i in range(2)]
        for t in polling_threads:
            t.start()
        
        # 等待所有執行緒完成
        busy_thread.join()
        for t in polling_threads:
            t.join()
        
        print(f"   結果: {results}")


def run_performance_comparison():
    """執行效能比較測試"""
    print("🧪 鎖效能比較測試")
    print("=" * 60)
    
    iterations = 10000
    num_threads = 4
    
    print(f"測試參數: 每個執行緒 {iterations} 次操作，{num_threads} 個執行緒")
    print("-" * 60)
    
    tester = PerformanceTester()
    
    # 執行各種測試
    tester.test_no_lock(iterations, num_threads)
    tester.test_thread_local(iterations, num_threads)
    tester.test_lock(iterations, num_threads)
    tester.test_rlock(iterations, num_threads)
    tester.test_semaphore(iterations, num_threads)
    
    # 顯示摘要
    summary = tester.get_summary()
    if summary:
        print(f"\n📈 效能摘要:")
        print(f"   🏆 最快: {summary['fastest'].lock_type} ({summary['fastest'].execution_time:.4f}s)")
        print(f"   🐌 最慢: {summary['slowest'].lock_type} ({summary['slowest'].execution_time:.4f}s)")
        print(f"   ⚡ 最高效: {summary['most_efficient'].lock_type} ({summary['most_efficient'].operations_per_second:.0f} ops/s)")
        print(f"   ✅ 全部正確: {'是' if summary['all_correct'] else '否'}")


def demonstrate_best_practices():
    """演示最佳實踐"""
    print(f"\n🎯 最佳實踐演示")
    print("=" * 60)
    
    demo = BestPracticesDemo()
    
    demo.good_lock_usage()
    print()
    demo.bad_lock_usage_demo()
    print()
    demo.avoid_deadlock()
    print()
    demo.minimize_lock_time()
    print()
    demo.appropriate_granularity()


def demonstrate_advanced_techniques():
    """演示進階技巧"""
    print(f"\n🚀 進階技巧演示")
    print("=" * 60)
    
    timeout_demo = LockTimeoutDemo()
    
    timeout_demo.timeout_handling()
    print()
    timeout_demo.non_blocking_attempt()


if __name__ == "__main__":
    run_performance_comparison()
    demonstrate_best_practices()
    demonstrate_advanced_techniques()
    
    print(f"\n💡 總結要點:")
    print("   1. 優先使用 with 語句管理鎖")
    print("   2. 最小化鎖的持有時間")
    print("   3. 統一鎖定順序避免死鎖")
    print("   4. 選擇合適的鎖粒度")
    print("   5. 考慮使用 threading.local 避免鎖競爭")
    print("   6. 測試併發場景確保正確性")