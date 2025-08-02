#!/usr/bin/env python3
"""
Event (事件) 使用範例
實現簡單的執行緒間通訊和一對多通知
"""

import threading
import time
import random


class EventDemo:
    """事件演示類"""
    
    def __init__(self):
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.worker_results = []
        self._lock = threading.Lock()
    
    def worker(self, worker_id):
        """工作者執行緒"""
        thread_name = threading.current_thread().name
        print(f"👷 工作者 {worker_id} ({thread_name}) 等待開始信號...")
        
        # 等待開始事件
        self.start_event.wait()
        print(f"🚀 工作者 {worker_id} 開始工作！")
        
        work_count = 0
        # 執行工作直到收到停止信號
        while not self.stop_event.is_set():
            work_count += 1
            print(f"⚙️  工作者 {worker_id} 正在工作... (第 {work_count} 次)")
            time.sleep(random.uniform(0.3, 0.8))
            
            # 檢查是否該停止
            if self.stop_event.wait(timeout=0):
                break
        
        # 記錄工作結果
        with self._lock:
            self.worker_results.append({
                'worker_id': worker_id,
                'work_count': work_count,
                'thread_name': thread_name
            })
        
        print(f"🛑 工作者 {worker_id} 收到停止信號，結束工作 (完成 {work_count} 次工作)")
    
    def controller(self, start_delay=2, work_duration=3):
        """控制器執行緒"""
        print("🎮 控制器啟動")
        
        # 等待一段時間後發送開始信號
        print(f"⏳ 控制器等待 {start_delay} 秒後發送開始信號...")
        time.sleep(start_delay)
        print("📢 控制器發送開始信號...")
        self.start_event.set()
        
        # 讓工作者工作一段時間
        print(f"⏳ 讓工作者工作 {work_duration} 秒...")
        time.sleep(work_duration)
        print("📢 控制器發送停止信號...")
        self.stop_event.set()
        
        print("🎮 控制器完成任務")


class DownloadMonitor:
    """下載監控器"""
    
    def __init__(self):
        self.download_complete = threading.Event()
        self.download_progress = 0
        self.progress_lock = threading.Lock()
        self.download_info = {}
    
    def download_file(self, filename, total_chunks=10):
        """模擬檔案下載"""
        print(f"📥 開始下載 {filename}")
        
        self.download_info = {
            'filename': filename,
            'start_time': time.time(),
            'total_chunks': total_chunks
        }
        
        for i in range(1, total_chunks + 1):
            # 模擬下載進度
            chunk_time = random.uniform(0.2, 0.6)
            time.sleep(chunk_time)
            
            with self.progress_lock:
                self.download_progress = (i / total_chunks) * 100
            
            print(f"📊 {filename} 下載進度: {self.download_progress:.1f}% (區塊 {i}/{total_chunks})")
        
        self.download_info['end_time'] = time.time()
        print(f"✅ {filename} 下載完成！")
        self.download_complete.set()  # 設定下載完成事件
    
    def progress_monitor(self):
        """監控下載進度"""
        print("👁️  進度監控器啟動")
        
        monitor_count = 0
        while not self.download_complete.is_set():
            with self.progress_lock:
                current_progress = self.download_progress
            
            monitor_count += 1
            if current_progress < 100:
                print(f"📈 監控器報告 #{monitor_count}: 當前進度 {current_progress:.1f}%")
            
            # 每0.8秒檢查一次
            if self.download_complete.wait(timeout=0.8):
                break
        
        print("🏁 監控器：下載已完成，停止監控")
    
    def cleanup_task(self):
        """下載完成後的清理工作"""
        print("🧹 清理任務等待下載完成...")
        
        # 等待下載完成事件
        self.download_complete.wait()
        
        print("🧹 開始清理工作...")
        time.sleep(0.5)  # 模擬清理時間
        
        # 計算下載統計
        if 'start_time' in self.download_info and 'end_time' in self.download_info:
            duration = self.download_info['end_time'] - self.download_info['start_time']
            filename = self.download_info['filename']
            chunks = self.download_info['total_chunks']
            print(f"📋 下載統計: {filename} - {chunks} 個區塊，耗時 {duration:.2f} 秒")
        
        print("✨ 清理完成！")


def test_basic_event():
    """測試基本事件功能"""
    print("🧪 測試基本 Event 功能")
    print("=" * 50)
    
    demo = EventDemo()
    threads = []
    num_workers = 4
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=demo.worker, args=(i,), name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    # 建立控制器執行緒
    controller_thread = threading.Thread(target=demo.controller, args=(1, 2))
    controller_thread.start()
    
    # 等待所有執行緒完成
    controller_thread.join()
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"\n📊 工作結果:")
    total_work = 0
    for result in demo.worker_results:
        print(f"   👷 工作者 {result['worker_id']}: {result['work_count']} 次工作 ({result['thread_name']})")
        total_work += result['work_count']
    
    print(f"📈 總工作次數: {total_work}")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_download_monitor():
    """測試下載監控"""
    print("\n🧪 測試下載監控")
    print("=" * 50)
    
    monitor = DownloadMonitor()
    
    start_time = time.time()
    
    # 建立下載執行緒
    download_thread = threading.Thread(
        target=monitor.download_file, 
        args=("large_file.zip", 8)
    )
    
    # 建立監控執行緒
    monitor_thread = threading.Thread(target=monitor.progress_monitor)
    
    # 建立清理執行緒
    cleanup_thread = threading.Thread(target=monitor.cleanup_task)
    
    # 啟動所有執行緒
    download_thread.start()
    monitor_thread.start()
    cleanup_thread.start()
    
    # 等待所有執行緒完成
    download_thread.join()
    monitor_thread.join()
    cleanup_thread.join()
    
    end_time = time.time()
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_event_states():
    """測試事件狀態"""
    print("\n🧪 測試事件狀態")
    print("=" * 50)
    
    event = threading.Event()
    
    print(f"🔴 初始狀態: {event.is_set()}")
    
    print("🟢 設定事件...")
    event.set()
    print(f"🟢 設定後狀態: {event.is_set()}")
    
    print("🔴 清除事件...")
    event.clear()
    print(f"🔴 清除後狀態: {event.is_set()}")
    
    # 測試超時等待
    print("⏰ 測試超時等待...")
    start = time.time()
    result = event.wait(timeout=1.0)
    elapsed = time.time() - start
    print(f"   等待結果: {result}, 耗時: {elapsed:.2f} 秒")


if __name__ == "__main__":
    test_basic_event()
    test_download_monitor()
    test_event_states()