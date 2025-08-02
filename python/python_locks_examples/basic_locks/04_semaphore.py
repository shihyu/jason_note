#!/usr/bin/env python3
"""
Semaphore (信號量) 使用範例
控制同時存取資源的執行緒數量，實現連線池功能
"""

import threading
import time
import random


class ConnectionPool:
    """連線池實現"""
    
    def __init__(self, max_connections=3):
        self.semaphore = threading.Semaphore(max_connections)
        self.connections = []
        self._lock = threading.Lock()
        self.max_connections = max_connections
    
    def get_connection(self):
        """獲取連線"""
        thread_name = threading.current_thread().name
        print(f"📞 {thread_name} 請求連線...")
        
        # 獲取連線許可
        self.semaphore.acquire()
        try:
            with self._lock:
                if self.connections:
                    conn = self.connections.pop()
                    print(f"♻️  {thread_name} 重用連線: {conn}")
                    return conn
                else:
                    # 建立新連線
                    conn_id = f"conn-{random.randint(1000, 9999)}"
                    print(f"🔗 {thread_name} 建立新連線: {conn_id}")
                    return conn_id
        except:
            self.semaphore.release()
            raise
    
    def return_connection(self, connection):
        """歸還連線"""
        thread_name = threading.current_thread().name
        with self._lock:
            self.connections.append(connection)
        # 釋放許可
        self.semaphore.release()
        print(f"🔙 {thread_name} 歸還連線: {connection}")
    
    def get_stats(self):
        """獲取連線池統計資訊"""
        with self._lock:
            available = len(self.connections)
            return {
                'max_connections': self.max_connections,
                'available_connections': available,
                'active_connections': self.max_connections - available
            }


class DownloadManager:
    """下載管理器，限制同時下載數量"""
    
    def __init__(self, max_concurrent_downloads=3):
        self.semaphore = threading.Semaphore(max_concurrent_downloads)
        self.results = []
        self._lock = threading.Lock()
    
    def download_file(self, url, filename):
        """模擬檔案下載"""
        thread_name = threading.current_thread().name
        
        print(f"📥 {thread_name} 等待下載許可...")
        with self.semaphore:
            print(f"🚀 {thread_name} 開始下載 {filename}")
            
            # 模擬下載時間
            download_time = random.uniform(1, 3)
            time.sleep(download_time)
            
            with self._lock:
                self.results.append({
                    'filename': filename,
                    'url': url,
                    'download_time': download_time,
                    'thread': thread_name
                })
            
            print(f"✅ {thread_name} 完成下載 {filename} (耗時: {download_time:.1f}s)")


def worker(pool, worker_id):
    """連線池工作者"""
    try:
        connection = pool.get_connection()
        
        # 模擬使用連線進行工作
        work_time = random.uniform(0.5, 2.0)
        print(f"⚙️  工作者 {worker_id} 使用連線工作 {work_time:.1f}s...")
        time.sleep(work_time)
        
        print(f"🏁 工作者 {worker_id} 完成工作")
        pool.return_connection(connection)
        
    except Exception as e:
        print(f"❌ 工作者 {worker_id} 發生錯誤: {e}")


def download_worker(manager, file_info):
    """下載工作者"""
    url, filename = file_info
    manager.download_file(url, filename)


def test_connection_pool():
    """測試連線池"""
    print("🧪 測試連線池 (Semaphore)")
    print("=" * 50)
    
    pool = ConnectionPool(max_connections=3)
    threads = []
    num_workers = 8
    
    print(f"🎯 建立 {num_workers} 個工作者競爭 3 個連線")
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=worker, args=(pool, i), name=f"Worker-{i}")
        threads.append(t)
        t.start()
        time.sleep(0.1)  # 稍微錯開啟動時間
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    stats = pool.get_stats()
    
    print(f"\n📊 連線池統計:")
    print(f"   最大連線數: {stats['max_connections']}")
    print(f"   可用連線數: {stats['available_connections']}")
    print(f"   活躍連線數: {stats['active_connections']}")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_download_manager():
    """測試下載管理器"""
    print("\n🧪 測試下載管理器")
    print("=" * 50)
    
    manager = DownloadManager(max_concurrent_downloads=2)
    files = [
        ("http://example.com/file1.zip", "file1.zip"),
        ("http://example.com/file2.zip", "file2.zip"),
        ("http://example.com/file3.zip", "file3.zip"),
        ("http://example.com/file4.zip", "file4.zip"),
        ("http://example.com/file5.zip", "file5.zip"),
    ]
    
    print(f"🎯 下載 {len(files)} 個檔案，最多同時 2 個下載")
    
    threads = []
    start_time = time.time()
    
    # 建立下載執行緒
    for file_info in files:
        t = threading.Thread(target=download_worker, args=(manager, file_info))
        threads.append(t)
        t.start()
        time.sleep(0.1)
    
    # 等待所有下載完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"\n📋 下載結果:")
    for result in manager.results:
        print(f"   ✅ {result['filename']} - {result['download_time']:.1f}s ({result['thread']})")
    
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


if __name__ == "__main__":
    test_connection_pool()
    test_download_manager()