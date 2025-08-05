#!/usr/bin/env python3
"""
上下文管理器與鎖的使用範例
演示如何使用 with 語句和自訂上下文管理器來管理鎖
"""

import threading
import time
from contextlib import contextmanager
import functools


class CustomLock:
    """自訂鎖，支援上下文管理器和詳細日誌"""
    
    def __init__(self, name="CustomLock"):
        self._lock = threading.Lock()
        self.name = name
        self.acquired_by = None
        self.acquire_count = 0
        self.total_wait_time = 0.0
        self._stats_lock = threading.Lock()
    
    def __enter__(self):
        """進入 with 區塊時呼叫"""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """離開 with 區塊時呼叫"""
        self.release()
        # 如果返回 False 或 None，異常會繼續傳播
        if exc_type:
            print(f"⚠️  在 {self.name} 中發生異常: {exc_type.__name__}: {exc_val}")
        return False
    
    def acquire(self):
        """獲取鎖"""
        thread_name = threading.current_thread().name
        print(f"🔒 {thread_name} 嘗試獲取 {self.name}")
        
        start_time = time.time()
        self._lock.acquire()
        wait_time = time.time() - start_time
        
        with self._stats_lock:
            self.acquired_by = thread_name
            self.acquire_count += 1
            self.total_wait_time += wait_time
        
        if wait_time > 0.001:  # 只在有明顯等待時間時顯示
            print(f"✅ {thread_name} 獲得 {self.name} (等待: {wait_time:.3f}s)")
        else:
            print(f"✅ {thread_name} 獲得 {self.name}")
    
    def release(self):
        """釋放鎖"""
        thread_name = threading.current_thread().name
        print(f"🔓 {thread_name} 釋放 {self.name}")
        
        with self._stats_lock:
            self.acquired_by = None
        
        self._lock.release()
    
    def get_stats(self):
        """獲取鎖的統計資訊"""
        with self._stats_lock:
            return {
                'name': self.name,
                'acquire_count': self.acquire_count,
                'total_wait_time': self.total_wait_time,
                'average_wait_time': self.total_wait_time / max(1, self.acquire_count),
                'currently_held_by': self.acquired_by
            }


@contextmanager
def timeout_lock(lock, timeout=2):
    """帶超時的鎖上下文管理器"""
    thread_name = threading.current_thread().name
    print(f"⏰ {thread_name} 嘗試在 {timeout}s 內獲取鎖")
    
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"⏰ {thread_name} 無法在 {timeout} 秒內獲取鎖")
    
    print(f"✅ {thread_name} 在時限內獲取鎖")
    try:
        yield lock
    finally:
        lock.release()
        print(f"🔓 {thread_name} 釋放超時鎖")


@contextmanager
def multiple_locks(*locks):
    """管理多個鎖的上下文管理器"""
    thread_name = threading.current_thread().name
    print(f"🔐 {thread_name} 嘗試獲取 {len(locks)} 個鎖")
    
    acquired_locks = []
    try:
        for i, lock in enumerate(locks):
            print(f"🔒 {thread_name} 獲取第 {i+1} 個鎖")
            lock.acquire()
            acquired_locks.append(lock)
        
        print(f"✅ {thread_name} 成功獲取所有 {len(locks)} 個鎖")
        yield locks
        
    finally:
        # 以相反順序釋放鎖
        for i, lock in enumerate(reversed(acquired_locks)):
            print(f"🔓 {thread_name} 釋放第 {len(acquired_locks)-i} 個鎖")
            lock.release()
        print(f"🔓 {thread_name} 釋放了所有鎖")


class ThreadSafeCounter:
    """使用上下文管理器的線程安全計數器"""
    
    def __init__(self):
        self._value = 0
        self._lock = CustomLock("CounterLock")
    
    def increment(self, amount=1):
        """增加計數"""
        with self._lock:
            old_value = self._value
            time.sleep(0.001)  # 模擬一些處理時間
            self._value += amount
            thread_name = threading.current_thread().name
            print(f"📈 {thread_name}: {old_value} + {amount} = {self._value}")
            return self._value
    
    def get_value(self):
        """獲取當前值"""
        with self._lock:
            return self._value
    
    def get_lock_stats(self):
        """獲取鎖的統計資訊"""
        return self._lock.get_stats()


def synchronized(lock):
    """同步裝飾器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


class BankAccount:
    """使用裝飾器同步的銀行帳戶"""
    
    def __init__(self, initial_balance=0):
        self._balance = initial_balance
        self._lock = CustomLock("BankAccountLock")
        self._transaction_history = []
    
    @synchronized(CustomLock("DepositLock"))
    def deposit(self, amount):
        """存款"""
        if amount <= 0:
            raise ValueError("存款金額必須大於0")
        
        thread_name = threading.current_thread().name
        old_balance = self._balance
        time.sleep(0.01)  # 模擬處理時間
        self._balance += amount
        
        transaction = {
            'type': 'deposit',
            'amount': amount,
            'balance_before': old_balance,
            'balance_after': self._balance,
            'thread': thread_name,
            'time': time.time()
        }
        self._transaction_history.append(transaction)
        
        print(f"💰 {thread_name}: 存款 ${amount}, 餘額: ${old_balance} → ${self._balance}")
        return self._balance
    
    def withdraw(self, amount):
        """提款"""
        with self._lock:
            if amount <= 0:
                raise ValueError("提款金額必須大於0")
            if amount > self._balance:
                raise ValueError("餘額不足")
            
            thread_name = threading.current_thread().name
            old_balance = self._balance
            time.sleep(0.01)  # 模擬處理時間
            self._balance -= amount
            
            transaction = {
                'type': 'withdraw',
                'amount': amount,
                'balance_before': old_balance,
                'balance_after': self._balance,
                'thread': thread_name,
                'time': time.time()
            }
            self._transaction_history.append(transaction)
            
            print(f"💸 {thread_name}: 提款 ${amount}, 餘額: ${old_balance} → ${self._balance}")
            return self._balance
    
    def get_balance(self):
        """獲取餘額"""
        with self._lock:
            return self._balance
    
    def get_transaction_history(self):
        """獲取交易歷史"""
        with self._lock:
            return self._transaction_history.copy()


def counter_worker(counter, worker_id, iterations=5):
    """計數器工作者"""
    for i in range(iterations):
        try:
            result = counter.increment(1)
            time.sleep(0.01)
        except Exception as e:
            print(f"❌ 工作者 {worker_id} 發生錯誤: {e}")


def bank_worker(account, worker_id, operations=3):
    """銀行帳戶工作者"""
    for i in range(operations):
        try:
            if i % 2 == 0:
                amount = 10 + (worker_id * 5)
                account.deposit(amount)
            else:
                amount = 5 + (worker_id * 2)
                try:
                    account.withdraw(amount)
                except ValueError as e:
                    print(f"⚠️  工作者 {worker_id}: {e}")
            
            time.sleep(0.05)
        except Exception as e:
            print(f"❌ 工作者 {worker_id} 發生錯誤: {e}")


def timeout_worker(worker_id):
    """測試超時鎖的工作者"""
    slow_lock = threading.Lock()
    
    try:
        if worker_id == 0:
            # 第一個工作者持有鎖較長時間
            with slow_lock:
                print(f"😴 工作者 {worker_id} 持有鎖 3 秒...")
                time.sleep(3)
        else:
            # 其他工作者嘗試在短時間內獲取鎖
            with timeout_lock(slow_lock, timeout=1):
                print(f"⚡ 工作者 {worker_id} 快速完成工作")
                time.sleep(0.1)
    except TimeoutError as e:
        print(f"⏰ 工作者 {worker_id}: {e}")


def test_custom_lock():
    """測試自訂鎖"""
    print("🧪 測試自訂上下文管理器鎖")
    print("=" * 50)
    
    counter = ThreadSafeCounter()
    threads = []
    num_workers = 4
    iterations = 3
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=counter_worker, args=(counter, i, iterations), name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # 顯示結果
    final_value = counter.get_value()
    expected = num_workers * iterations
    stats = counter.get_lock_stats()
    
    print(f"\n📊 計數器測試結果:")
    print(f"   最終值: {final_value}")
    print(f"   預期值: {expected}")
    print(f"   正確性: {'✅ 正確' if final_value == expected else '❌ 錯誤'}")
    print(f"   鎖統計: 獲取 {stats['acquire_count']} 次，平均等待 {stats['average_wait_time']:.3f}s")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_bank_account():
    """測試銀行帳戶"""
    print("\n🧪 測試銀行帳戶")
    print("=" * 50)
    
    account = BankAccount(initial_balance=100)
    threads = []
    num_workers = 3
    operations = 3
    
    print(f"💰 初始餘額: ${account.get_balance()}")
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=bank_worker, args=(account, i, operations), name=f"Banker-{i}")
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # 顯示結果
    final_balance = account.get_balance()
    history = account.get_transaction_history()
    
    print(f"\n📊 銀行帳戶測試結果:")
    print(f"   最終餘額: ${final_balance}")
    print(f"   交易次數: {len(history)}")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")
    
    print(f"\n📋 交易歷史:")
    for transaction in history[-5:]:  # 顯示最後5筆交易
        action = "存款" if transaction['type'] == 'deposit' else "提款"
        print(f"   {action} ${transaction['amount']} by {transaction['thread']} "
              f"(${transaction['balance_before']} → ${transaction['balance_after']})")


def test_timeout_lock():
    """測試超時鎖"""
    print("\n🧪 測試超時鎖")
    print("=" * 50)
    
    threads = []
    num_workers = 3
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=timeout_worker, args=(i,), name=f"TimeoutWorker-{i}")
        threads.append(t)
        t.start()
        time.sleep(0.1)  # 錯開啟動時間
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()


def test_multiple_locks():
    """測試多重鎖管理"""
    print("\n🧪 測試多重鎖管理")
    print("=" * 50)
    
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    lock3 = threading.Lock()
    
    def multi_lock_worker(worker_id):
        try:
            with multiple_locks(lock1, lock2, lock3):
                print(f"🔐 工作者 {worker_id} 在所有鎖保護下工作")
                time.sleep(0.5)
                print(f"✅ 工作者 {worker_id} 完成工作")
        except Exception as e:
            print(f"❌ 工作者 {worker_id} 發生錯誤: {e}")
    
    threads = []
    for i in range(2):
        t = threading.Thread(target=multi_lock_worker, args=(i,), name=f"MultiLockWorker-{i}")
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


if __name__ == "__main__":
    test_custom_lock()
    test_bank_account()
    test_timeout_lock()
    test_multiple_locks()