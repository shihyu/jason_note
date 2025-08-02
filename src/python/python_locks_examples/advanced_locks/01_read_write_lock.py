#!/usr/bin/env python3
"""
ReadWriteLock (讀寫鎖) 實現範例
Python 沒有內建讀寫鎖，這裡提供一個手動實現
允許多個讀者同時讀取，但寫入時需要獨佔存取
"""

import threading
import time
import random


class ReadWriteLock:
    """手動實現的讀寫鎖"""
    
    def __init__(self):
        self._read_ready = threading.Condition(threading.RLock())
        self._readers = 0
    
    def acquire_read(self):
        """獲取讀鎖"""
        self._read_ready.acquire()
        try:
            self._readers += 1
        finally:
            self._read_ready.release()
    
    def release_read(self):
        """釋放讀鎖"""
        self._read_ready.acquire()
        try:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notifyAll()
        finally:
            self._read_ready.release()
    
    def acquire_write(self):
        """獲取寫鎖"""
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()
    
    def release_write(self):
        """釋放寫鎖"""
        self._read_ready.release()


class AdvancedReadWriteLock:
    """進階讀寫鎖，支援更多功能"""
    
    def __init__(self):
        self._read_condition = threading.Condition(threading.RLock())
        self._write_condition = threading.Condition(threading.RLock())
        self._readers = 0
        self._writers = 0
        self._write_requests = 0
        self._current_writer = None
    
    def acquire_read(self):
        """獲取讀鎖（優先給寫者）"""
        self._read_condition.acquire()
        try:
            # 如果有寫者等待，讀者需要等待
            while self._writers > 0 or self._write_requests > 0:
                self._read_condition.wait()
            self._readers += 1
        finally:
            self._read_condition.release()
    
    def release_read(self):
        """釋放讀鎖"""
        self._read_condition.acquire()
        try:
            self._readers -= 1
            if self._readers == 0:
                self._read_condition.notifyAll()
        finally:
            self._read_condition.release()
    
    def acquire_write(self):
        """獲取寫鎖"""
        self._write_condition.acquire()
        try:
            self._write_requests += 1
            while self._writers > 0 or self._readers > 0:
                self._write_condition.wait()
            self._write_requests -= 1
            self._writers = 1
            self._current_writer = threading.current_thread().name
        finally:
            self._write_condition.release()
    
    def release_write(self):
        """釋放寫鎖"""
        self._write_condition.acquire()
        try:
            self._writers = 0
            self._current_writer = None
            self._write_condition.notifyAll()
        finally:
            self._write_condition.release()
        
        # 通知等待的讀者
        self._read_condition.acquire()
        try:
            self._read_condition.notifyAll()
        finally:
            self._read_condition.release()
    
    def get_status(self):
        """獲取鎖的狀態"""
        return {
            'readers': self._readers,
            'writers': self._writers,
            'write_requests': self._write_requests,
            'current_writer': self._current_writer
        }


class SharedResource:
    """使用讀寫鎖保護的共享資源"""
    
    def __init__(self, use_advanced=False):
        self._data = {
            "counter": 0, 
            "items": [], 
            "metadata": {"created": time.time()}
        }
        if use_advanced:
            self._lock = AdvancedReadWriteLock()
        else:
            self._lock = ReadWriteLock()
        self._read_count = 0
        self._write_count = 0
        self._access_log = []
        self._log_lock = threading.Lock()
    
    def read_data(self, reader_id):
        """讀取資料"""
        thread_name = threading.current_thread().name
        
        self._lock.acquire_read()
        try:
            # 模擬讀取時間
            read_time = random.uniform(0.01, 0.05)  # 大幅減少時間
            time.sleep(read_time)
            
            counter = self._data["counter"]
            items_count = len(self._data["items"])
            created_time = self._data["metadata"]["created"]
            
            with self._log_lock:
                self._read_count += 1
                self._access_log.append({
                    'type': 'read',
                    'reader_id': reader_id,
                    'thread': thread_name,
                    'time': time.time(),
                    'duration': read_time
                })
            
            print(f"👀 讀者 {reader_id} ({thread_name}): counter={counter}, items={items_count}, 耗時={read_time:.2f}s")
            return counter, items_count, created_time
            
        finally:
            self._lock.release_read()
    
    def write_data(self, writer_id, value):
        """寫入資料"""
        thread_name = threading.current_thread().name
        
        print(f"✍️  寫者 {writer_id} ({thread_name}) 請求寫入...")
        self._lock.acquire_write()
        try:
            print(f"🔒 寫者 {writer_id} 獲得寫鎖，開始寫入...")
            
            # 模擬寫入時間
            write_time = random.uniform(0.02, 0.1)  # 大幅減少時間
            time.sleep(write_time)
            
            self._data["counter"] += value
            self._data["items"].append(f"item-{writer_id}-{value}")
            self._data["metadata"]["last_updated"] = time.time()
            
            with self._log_lock:
                self._write_count += 1
                self._access_log.append({
                    'type': 'write',
                    'writer_id': writer_id,
                    'thread': thread_name,
                    'value': value,
                    'time': time.time(),
                    'duration': write_time
                })
            
            print(f"✅ 寫者 {writer_id} 完成寫入: +{value}, 新counter={self._data['counter']}, 耗時={write_time:.2f}s")
            
        finally:
            self._lock.release_write()
    
    def get_stats(self):
        """獲取統計資訊"""
        with self._log_lock:
            return {
                'read_count': self._read_count,
                'write_count': self._write_count,
                'total_accesses': len(self._access_log),
                'current_counter': self._data["counter"],
                'items_count': len(self._data["items"])
            }
    
    def get_access_log(self):
        """獲取存取日誌"""
        with self._log_lock:
            return self._access_log.copy()


def reader_worker(resource, reader_id, num_reads=3):
    """讀者工作者"""
    for i in range(num_reads):
        resource.read_data(reader_id)
        time.sleep(random.uniform(0.01, 0.05))  # 減少等待時間


def writer_worker(resource, writer_id, num_writes=2):
    """寫者工作者"""
    for i in range(num_writes):
        value = random.randint(1, 10)
        resource.write_data(writer_id, value)
        time.sleep(random.uniform(0.02, 0.1))  # 減少等待時間


def test_basic_read_write_lock():
    """測試基本讀寫鎖"""
    print("🧪 測試基本讀寫鎖")
    print("=" * 50)
    
    resource = SharedResource(use_advanced=False)
    threads = []
    
    num_readers = 3  # 減少執行緒數量
    num_writers = 2
    
    print(f"🎯 啟動 {num_readers} 個讀者和 {num_writers} 個寫者")
    
    start_time = time.time()
    
    # 建立讀者執行緒
    for i in range(num_readers):
        t = threading.Thread(target=reader_worker, args=(resource, i, 1))  # 減少讀取次數
        threads.append(t)
        t.start()
    
    # 稍微延遲後建立寫者執行緒
    time.sleep(0.1)
    for i in range(num_writers):
        t = threading.Thread(target=writer_worker, args=(resource, i, 1))  # 減少寫入次數
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # 顯示統計資訊
    stats = resource.get_stats()
    print(f"\n📊 統計結果:")
    print(f"   📖 讀取次數: {stats['read_count']}")
    print(f"   ✍️  寫入次數: {stats['write_count']}")
    print(f"   📝 總存取次數: {stats['total_accesses']}")
    print(f"   🔢 最終計數器: {stats['current_counter']}")
    print(f"   📦 項目數量: {stats['items_count']}")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_advanced_read_write_lock():
    """測試進階讀寫鎖"""
    print("\n🧪 測試進階讀寫鎖 (寫者優先)")
    print("=" * 50)
    
    resource = SharedResource(use_advanced=True)
    threads = []
    
    num_readers = 2  # 大幅減少
    num_writers = 1
    
    print(f"🎯 啟動 {num_readers} 個讀者和 {num_writers} 個寫者 (寫者優先)")
    
    start_time = time.time()
    
    # 先啟動一些讀者
    for i in range(num_readers):
        t = threading.Thread(target=reader_worker, args=(resource, i, 1))  # 減少次數
        threads.append(t)
        t.start()
    
    # 短暫延遲後啟動寫者
    time.sleep(0.05)
    for i in range(num_writers):
        t = threading.Thread(target=writer_worker, args=(resource, i, 1))  # 減少次數
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # 顯示統計資訊
    stats = resource.get_stats()
    access_log = resource.get_access_log()
    
    print(f"\n📊 統計結果:")
    print(f"   📖 讀取次數: {stats['read_count']}")
    print(f"   ✍️  寫入次數: {stats['write_count']}")
    print(f"   📝 總存取次數: {stats['total_accesses']}")
    print(f"   🔢 最終計數器: {stats['current_counter']}")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")
    
    # 分析存取模式
    print(f"\n📈 存取時間線:")
    for log in access_log[:5]:  # 只顯示前5個
        action = "📖 讀取" if log['type'] == 'read' else "✍️  寫入"
        worker_id = log.get('reader_id', log.get('writer_id'))
        print(f"   {action} - 工作者 {worker_id} ({log['thread']}) - {log['duration']:.2f}s")


if __name__ == "__main__":
    test_basic_read_write_lock()
    test_advanced_read_write_lock()