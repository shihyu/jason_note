# Python 鎖機制完整指南 🐍

## 📊 Python 鎖機制視覺化概覽

```
Python 鎖的選擇流程圖：
┌─────────────────┐
│   需要同步嗎？   │
└─────┬───────────┘
      │ 是
      ▼
┌─────────────────┐    ┌──────────────────┐
│   簡單計數？     │───▶│   使用 atomic    │
└─────┬───────────┘ 是 │   🔢 threading.local│
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐    ┌──────────────────┐
│   多讀少寫？     │───▶│使用 ReadWriteLock│
└─────┬───────────┘ 是 │   📖 讀寫鎖       │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐    ┌──────────────────┐
│   需要等條件？   │───▶│  使用 Condition  │
└─────┬───────────┘ 是 │   🚌 條件變數     │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐    ┌──────────────────┐
│   控制資源數？   │───▶│  使用 Semaphore  │
└─────┬───────────┘ 是 │   🚗 信號量       │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐
│   使用 Lock     │
│   🔒 互斥鎖      │
└─────────────────┘
```

---

## Python 內建鎖機制 🐍

### 1. threading.Lock 🔒

**白話解釋**: 就像廁所門鎖，一次只能一個人使用，其他人必須在外面等待  
**用途**: 保護共享資源，同一時間只允許一個執行緒存取  
**使用時機**: 當多個執行緒需要存取同一個變數或資料結構時

```
Lock 工作示意圖：
執行緒A: 🏃‍♂️ ──▶ 🔒[資源] ◀── ⏸️ 執行緒B (等待)
                              ⏸️ 執行緒C (等待)

時間線：
T1: A獲得鎖 🔒✅    B等待❌    C等待❌
T2: A釋放鎖 🔓      B獲得鎖✅   C等待❌  
T3: B釋放鎖 🔓      C獲得鎖✅
```

**🔥 基本使用範例:**
```python
import threading
import time

# 全域變數和鎖
counter = 0
lock = threading.Lock()

def increment_counter():
    global counter
    for _ in range(100000):
        # 使用 with 語句自動管理鎖
        with lock:
            counter += 1

def increment_manual():
    global counter
    for _ in range(100000):
        # 手動管理鎖
        lock.acquire()
        try:
            counter += 1
        finally:
            lock.release()

# 測試範例
def test_lock():
    global counter
    counter = 0
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=increment_counter)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"最終計數: {counter}")  # 應該是 500000

if __name__ == "__main__":
    test_lock()
```

**🎯 裝飾器版本:**
```python
import threading
from functools import wraps

class ThreadSafe:
    def __init__(self):
        self._lock = threading.Lock()
    
    def synchronized(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                return func(*args, **kwargs)
        return wrapper

# 使用範例
class Counter:
    def __init__(self):
        self._value = 0
        self._thread_safe = ThreadSafe()
    
    @property
    def increment(self):
        return self._thread_safe.synchronized(self._increment)
    
    def _increment(self):
        self._value += 1
        return self._value
    
    @property
    def value(self):
        return self._value
```

---

### 2. threading.RLock (遞迴鎖) 🔄

**白話解釋**: 像有記憶的門鎖，記得是誰鎖的，同一個人可以重複進入  
**用途**: 可重複鎖定的互斥鎖  
**使用時機**: 同一執行緒可能需要多次獲得鎖，特別是遞迴函數

```
RLock 遞迴示意圖：

執行緒A 獲得鎖計數：
func1() { 
  acquire(rlock); 🔒 計數=1
  func2();    
}
func2() { 
  acquire(rlock); 🔒 計數=2 ← 同一執行緒可以再鎖
  # 工作
  release();      🔓 計數=1
}
release();        🔓 計數=0 ← 完全釋放

一般Lock會死鎖 ❌:
Thread A: 🔒 → 🔒 → 💀 (死鎖)
```

**程式碼範例:**
```python
import threading
import time

class RecursiveCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.RLock()  # 使用 RLock
    
    def increment(self, n=1):
        with self._lock:
            if n > 1:
                # 遞迴呼叫，需要再次獲得鎖
                self.increment(n-1)
            self._value += 1
            print(f"執行緒 {threading.current_thread().name}: 值 = {self._value}")
    
    def get_value(self):
        with self._lock:
            return self._value

# 測試範例
def test_recursive_lock():
    counter = RecursiveCounter()
    
    def worker():
        counter.increment(3)  # 遞迴呼叫3次
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"最終值: {counter.get_value()}")

# 對比：如果用普通Lock會發生什麼
class BadRecursiveCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()  # 普通Lock
    
    def increment(self, n=1):
        with self._lock:
            if n > 1:
                # 💀 死鎖！同一執行緒無法再次獲得Lock
                self.increment(n-1)
            self._value += 1

if __name__ == "__main__":
    test_recursive_lock()
```

---

### 3. threading.Semaphore (信號量) 🚗

**白話解釋**: 像停車場管理員，有固定的停車位數量，滿了就要等有人開走  
**用途**: 控制同時存取資源的執行緒數量  
**使用時機**: 限制同時使用資源的執行緒數量，比如連線池、檔案下載

```
Semaphore 工作示意圖 (假設最多3個車位)：
停車場: [🚗][🚗][🚗] ← 滿了
等待區: 🚗💤 🚗💤 🚗💤

當有車離開：
停車場: [🚗][🚗][  ] ← 有空位
等待區: 🚗💤 🚗💤     ← 一臺車可以進入

數量控制：
semaphore = Semaphore(3)  # 最多3個同時進入
等待中: ████████░░     (8個等待，2個在執行)
```

**🔥 連線池範例:**
```python
import threading
import time
import random

class ConnectionPool:
    def __init__(self, max_connections=3):
        self.semaphore = threading.Semaphore(max_connections)
        self.connections = []
        self._lock = threading.Lock()
    
    def get_connection(self):
        # 獲取連線許可
        self.semaphore.acquire()
        try:
            with self._lock:
                if self.connections:
                    return self.connections.pop()
                else:
                    # 建立新連線
                    conn_id = f"conn-{random.randint(1000, 9999)}"
                    print(f"🔗 建立新連線: {conn_id}")
                    return conn_id
        except:
            self.semaphore.release()
            raise
    
    def return_connection(self, connection):
        with self._lock:
            self.connections.append(connection)
        # 釋放許可
        self.semaphore.release()
        print(f"🔙 歸還連線: {connection}")

# 使用範例
def worker(pool, worker_id):
    try:
        print(f"👤 工作者 {worker_id} 請求連線...")
        connection = pool.get_connection()
        print(f"✅ 工作者 {worker_id} 獲得連線: {connection}")
        
        # 模擬工作
        time.sleep(random.uniform(1, 3))
        
        print(f"🏁 工作者 {worker_id} 完成工作")
        pool.return_connection(connection)
        
    except Exception as e:
        print(f"❌ 工作者 {worker_id} 發生錯誤: {e}")

def test_semaphore():
    pool = ConnectionPool(max_connections=3)
    
    threads = []
    for i in range(8):  # 8個工作者競爭3個連線
        t = threading.Thread(target=worker, args=(pool, i))
        threads.append(t)
        t.start()
        time.sleep(0.1)  # 稍微錯開啟動時間
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    test_semaphore()
```

**🎯 檔案下載限制範例:**
```python
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor

class DownloadManager:
    def __init__(self, max_concurrent_downloads=3):
        self.semaphore = threading.Semaphore(max_concurrent_downloads)
        self.results = []
        self._lock = threading.Lock()
    
    def download_file(self, url, filename):
        thread_name = threading.current_thread().name
        
        print(f"📥 {thread_name} 等待下載許可...")
        with self.semaphore:
            print(f"🚀 {thread_name} 開始下載 {filename}")
            
            # 模擬下載
            time.sleep(random.uniform(2, 5))
            
            with self._lock:
                self.results.append(f"{filename} 下載完成")
            
            print(f"✅ {thread_name} 完成下載 {filename}")

# 使用範例
def test_download_manager():
    manager = DownloadManager(max_concurrent_downloads=2)
    
    urls = [
        ("http://example.com/file1.zip", "file1.zip"),
        ("http://example.com/file2.zip", "file2.zip"),
        ("http://example.com/file3.zip", "file3.zip"),
        ("http://example.com/file4.zip", "file4.zip"),
        ("http://example.com/file5.zip", "file5.zip"),
    ]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for url, filename in urls:
            future = executor.submit(manager.download_file, url, filename)
            futures.append(future)
        
        # 等待所有下載完成
        for future in futures:
            future.result()
    
    print("\n📋 下載結果:")
    for result in manager.results:
        print(f"  - {result}")
```

---

### 4. threading.Condition (條件變數) 🚌

**白話解釋**: 像等公車的站牌，只有當公車來了（條件滿足）才上車，否則就一直等  
**用途**: 讓執行緒等待特定條件成立  
**使用時機**: 生產者-消費者模式，或需要等待某個狀態改變

```
Condition Variable 工作流程：

生產者-消費者模式：
生產者: 🏭 ──▶ [緩衝區] ──▶ 📢 通知消費者
消費者: 👤💤 ──▶ 🔔收到通知 ──▶ 👤🏃‍♂️ 開始工作

等待流程：
1. 獲取鎖    🔒 condition.acquire()
2. 檢查條件  ❓ while not condition_met:
3. 如果不滿足 😴 condition.wait()
4. 收到信號  🔔 condition.notify()
5. 重新檢查  ❓ 
6. 執行工作  ⚙️
7. 釋放鎖    🔓 condition.release()
```

**🔥 生產者-消費者範例:**
```python
import threading
import time
import random
import queue

class ProducerConsumer:
    def __init__(self, buffer_size=5):
        self.buffer = []
        self.buffer_size = buffer_size
        self.condition = threading.Condition()
        self.produced_count = 0
        self.consumed_count = 0
    
    def producer(self, producer_id):
        for i in range(5):
            item = f"產品-{producer_id}-{i}"
            
            with self.condition:
                # 等待緩衝區有空間
                while len(self.buffer) >= self.buffer_size:
                    print(f"🏭 生產者 {producer_id} 等待空間...")
                    self.condition.wait()
                
                # 生產物品
                self.buffer.append(item)
                self.produced_count += 1
                print(f"✨ 生產者 {producer_id} 生產了 {item} (緩衝區: {len(self.buffer)})")
                
                # 通知消費者
                self.condition.notify_all()
            
            time.sleep(random.uniform(0.1, 0.5))
    
    def consumer(self, consumer_id):
        while True:
            with self.condition:
                # 等待有物品可消費
                while not self.buffer:
                    print(f"👤 消費者 {consumer_id} 等待產品...")
                    self.condition.wait(timeout=2)  # 設定超時
                    
                    # 如果超時且沒有更多產品，退出
                    if not self.buffer and self.consumed_count >= 10:  # 假設總共生產10個
                        print(f"🏁 消費者 {consumer_id} 退出")
                        return
                
                if self.buffer:
                    item = self.buffer.pop(0)
                    self.consumed_count += 1
                    print(f"🍽️ 消費者 {consumer_id} 消費了 {item} (緩衝區: {len(self.buffer)})")
                    
                    # 通知生產者
                    self.condition.notify_all()
            
            # 模擬消費時間
            time.sleep(random.uniform(0.2, 0.8))

# 測試範例
def test_producer_consumer():
    pc = ProducerConsumer(buffer_size=3)
    
    threads = []
    
    # 建立生產者執行緒
    for i in range(2):
        t = threading.Thread(target=pc.producer, args=(i,))
        threads.append(t)
        t.start()
    
    # 建立消費者執行緒
    for i in range(3):
        t = threading.Thread(target=pc.consumer, args=(i,))
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    print(f"\n📊 統計: 生產 {pc.produced_count} 個，消費 {pc.consumed_count} 個")

if __name__ == "__main__":
    test_producer_consumer()
```

**🎯 任務協調範例:**
```python
import threading
import time

class TaskCoordinator:
    def __init__(self):
        self.condition = threading.Condition()
        self.task_ready = False
        self.workers_ready = 0
        self.target_workers = 3
    
    def worker_ready(self, worker_id):
        """工作者報告準備就緒"""
        with self.condition:
            self.workers_ready += 1
            print(f"👷 工作者 {worker_id} 準備就緒 ({self.workers_ready}/{self.target_workers})")
            
            if self.workers_ready >= self.target_workers:
                print("🚀 所有工作者準備就緒，開始任務！")
                self.task_ready = True
                self.condition.notify_all()
            else:
                # 等待其他工作者
                while not self.task_ready:
                    print(f"⏳ 工作者 {worker_id} 等待其他工作者...")
                    self.condition.wait()
    
    def start_task(self, worker_id):
        """開始執行任務"""
        print(f"⚙️ 工作者 {worker_id} 開始執行任務")
        time.sleep(random.uniform(2, 4))  # 模擬任務執行
        print(f"✅ 工作者 {worker_id} 完成任務")

def worker(coordinator, worker_id):
    # 模擬準備時間
    time.sleep(random.uniform(1, 3))
    
    # 報告準備就緒並等待開始信號
    coordinator.worker_ready(worker_id)
    
    # 執行任務
    coordinator.start_task(worker_id)

def test_task_coordination():
    coordinator = TaskCoordinator()
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(coordinator, i))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    test_task_coordination()
```

---

### 5. threading.Event (事件) 📡

**白話解釋**: 像信號燈，可以設定為紅燈（停止）或綠燈（通行），所有等待的執行緒都會同時收到信號  
**用途**: 簡單的執行緒間通訊機制  
**使用時機**: 需要一對多通知，或等待某個事件發生

```
Event 狀態圖：

未設定狀態 (False) 🔴:
Event: 🔴 ← 👤💤 👤💤 👤💤 (所有執行緒等待)

設定狀態 (True) 🟢:
Event: 🟢 ← 👤🏃‍♂️ 👤🏃‍♂️ 👤🏃‍♂️ (所有執行緒繼續)

狀態轉換：
event.clear()  → 🔴 (重置為未設定)
event.set()    → 🟢 (設定為已發生)
event.wait()   → 等待事件發生
event.is_set() → 檢查當前狀態
```

**🔥 基本使用範例:**
```python
import threading
import time
import random

class EventDemo:
    def __init__(self):
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
    
    def worker(self, worker_id):
        print(f"👷 工作者 {worker_id} 等待開始信號...")
        
        # 等待開始事件
        self.start_event.wait()
        print(f"🚀 工作者 {worker_id} 開始工作！")
        
        # 執行工作直到收到停止信號
        while not self.stop_event.is_set():
            print(f"⚙️ 工作者 {worker_id} 正在工作...")
            time.sleep(random.uniform(0.5, 1.5))
        
        print(f"🛑 工作者 {worker_id} 收到停止信號，結束工作")
    
    def controller(self):
        print("🎮 控制器啟動")
        
        # 等待3秒後發送開始信號
        time.sleep(3)
        print("📢 發送開始信號...")
        self.start_event.set()
        
        # 讓工作者工作5秒
        time.sleep(5)
        print("📢 發送停止信號...")
        self.stop_event.set()

def test_event():
    demo = EventDemo()
    
    threads = []
    
    # 建立工作者執行緒
    for i in range(3):
        t = threading.Thread(target=demo.worker, args=(i,))
        threads.append(t)
        t.start()
    
    # 建立控制器執行緒
    controller_thread = threading.Thread(target=demo.controller)
    controller_thread.start()
    
    # 等待所有執行緒完成
    controller_thread.join()
    for t in threads:
        t.join()

if __name__ == "__main__":
    test_event()
```

**🎯 檔案下載進度監控範例:**
```python
import threading
import time
import random

class DownloadMonitor:
    def __init__(self):
        self.download_complete = threading.Event()
        self.download_progress = 0
        self.progress_lock = threading.Lock()
    
    def download_file(self, filename):
        """模擬檔案下載"""
        print(f"📥 開始下載 {filename}")
        
        for i in range(1, 11):
            # 模擬下載進度
            time.sleep(random.uniform(0.2, 0.5))
            
            with self.progress_lock:
                self.download_progress = i * 10
            
            print(f"📊 {filename} 下載進度: {self.download_progress}%")
        
        print(f"✅ {filename} 下載完成！")
        self.download_complete.set()  # 設定下載完成事件
    
    def progress_monitor(self):
        """監控下載進度"""
        print("👁️ 進度監控器啟動")
        
        while not self.download_complete.is_set():
            with self.progress_lock:
                current_progress = self.download_progress
            
            if current_progress < 100:
                print(f"📈 監控器報告: 當前進度 {current_progress}%")
            
            # 每秒檢查一次
            time.sleep(1)
        
        print("🏁 監控器：下載已完成，停止監控")
    
    def cleanup_task(self):
        """下載完成後的清理工作"""
        print("🧹 清理任務等待下載完成...")
        
        # 等待下載完成事件
        self.download_complete.wait()
        
        print("🧹 開始清理工作...")
        time.sleep(1)  # 模擬清理時間
        print("✨ 清理完成！")

def test_download_monitor():
    monitor = DownloadMonitor()
    
    # 建立下載執行緒
    download_thread = threading.Thread(
        target=monitor.download_file, 
        args=("large_file.zip",)
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

if __name__ == "__main__":
    test_download_monitor()
```

---

### 6. threading.Barrier (屏障) 🚧

**白話解釋**: 像集合點，必須等到指定數量的執行緒都到達後，才一起繼續執行  
**用途**: 同步多個執行緒，確保它們在某個點一起繼續  
**使用時機**: 需要多個執行緒同步執行某些階段的任務

```
Barrier 同步示意圖：

階段1: 各執行緒獨立工作
Thread A: ████████─────── ╱
Thread B: ██████───────── ╱ 🚧 Barrier (等待點)
Thread C: ████████████── ╱

階段2: 所有執行緒到達後一起繼續
Thread A: ──────────████████
Thread B: ──────────████████  
Thread C: ──────────████████

等待流程：
1. 執行緒到達 barrier.wait()
2. 如果未達到目標數量，等待
3. 最後一個執行緒到達時，釋放所有等待的執行緒
```

**程式碼範例:**
```python
import threading
import time
import random

class MultiPhaseTask:
    def __init__(self, num_workers=3):
        self.num_workers = num_workers
        # 建立屏障，需要3個執行緒同時到達
        self.phase1_barrier = threading.Barrier(num_workers)
        self.phase2_barrier = threading.Barrier(num_workers)
        self.results = []
        self.results_lock = threading.Lock()
    
    def worker(self, worker_id):
        # 階段1: 資料準備
        print(f"📋 工作者 {worker_id} 開始階段1: 資料準備")
        preparation_time = random.uniform(1, 3)
        time.sleep(preparation_time)
        print(f"✅ 工作者 {worker_id} 完成階段1 (耗時: {preparation_time:.1f}s)")
        
        try:
            # 等待所有工作者完成階段1
            print(f"⏳ 工作者 {worker_id} 等待其他工作者完成階段1...")
            self.phase1_barrier.wait()
            print(f"🚀 工作者 {worker_id} 進入階段2!")
        except threading.BrokenBarrierError:
            print(f"❌ 工作者 {worker_id}: 屏障被破壞")
            return
        
        # 階段2: 資料處理
        print(f"⚙️ 工作者 {worker_id} 開始階段2: 資料處理")
        processing_time = random.uniform(2, 4)
        time.sleep(processing_time)
        
        # 儲存結果
        result = f"工作者{worker_id}的結果"
        with self.results_lock:
            self.results.append(result)
        
        print(f"✅ 工作者 {worker_id} 完成階段2 (耗時: {processing_time:.1f}s)")
        
        try:
            # 等待所有工作者完成階段2
            print(f"⏳ 工作者 {worker_id} 等待其他工作者完成階段2...")
            self.phase2_barrier.wait()
            print(f"🎉 工作者 {worker_id} 所有階段完成!")
        except threading.BrokenBarrierError:
            print(f"❌ 工作者 {worker_id}: 屏障被破壞")
            return
        
        # 階段3: 結果匯總（只有一個工作者執行）
        if worker_id == 0:  # 讓工作者0負責匯總
            print("\n📊 開始結果匯總...")
            time.sleep(1)
            print("📋 所有結果:")
            for result in self.results:
                print(f"  - {result}")

def test_barrier():
    task = MultiPhaseTask(num_workers=3)
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=task.worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    test_barrier()
```

---

## 高級鎖機制與設計模式 🚀

### 1. 讀寫鎖 (ReadWriteLock) 📖

**白話解釋**: 像圖書館規則，很多人可以同時看書（讀），但只能一個人寫字（寫）  
**Python沒有內建**: 需要自己實現或使用第三方庫  
**使用時機**: 讀取頻繁但寫入較少的場景

```python
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

class SharedResource:
    def __init__(self):
        self._data = {"counter": 0, "items": []}
        self._lock = ReadWriteLock()
    
    def read_data(self, reader_id):
        """讀取資料"""
        self._lock.acquire_read()
        try:
            # 模擬讀取時間
            time.sleep(random.uniform(0.1, 0.5))
            counter = self._data["counter"]
            items_count = len(self._data["items"])
            print(f"👀 讀者 {reader_id}: counter={counter}, items={items_count}")
            return counter, items_count
        finally:
            self._lock.release_read()
    
    def write_data(self, writer_id, value):
        """寫入資料"""
        self._lock.acquire_write()
        try:
            print(f"✍️ 寫者 {writer_id} 開始寫入...")
            # 模擬寫入時間
            time.sleep(random.uniform(0.5, 1.0))
            
            self._data["counter"] += value
            self._data["items"].append(f"item-{value}")
            
            print(f"✅ 寫者 {writer_id} 完成寫入: +{value}")
        finally:
            self._lock.release_write()

def reader_worker(resource, reader_id):
    for _ in range(3):
        resource.read_data(reader_id)
        time.sleep(random.uniform(0.2, 0.8))

def writer_worker(resource, writer_id):
    for i in range(2):
        value = random.randint(1, 10)
        resource.write_data(writer_id, value)
        time.sleep(random.uniform(1, 2))

def test_read_write_lock():
    resource = SharedResource()
    
    threads = []
    
    # 建立多個讀者
    for i in range(4):
        t = threading.Thread(target=reader_worker, args=(resource, i))
        threads.append(t)
        t.start()
    
    # 建立少數寫者
    for i in range(2):
        t = threading.Thread(target=writer_worker, args=(resource, i))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    test_read_write_lock()
```

---

### 2. 上下文管理器與鎖 🎛️

**白話解釋**: 使用 `with` 語句自動管理鎖的獲取和釋放，就像自動門一樣  
**優點**: 確保即使發生異常也會正確釋放鎖  
**使用時機**: 所有需要鎖保護的場景都建議使用

```python
import threading
import time
from contextlib import contextmanager

class CustomLock:
    """自訂鎖，支援上下文管理器"""
    
    def __init__(self, name="CustomLock"):
        self._lock = threading.Lock()
        self.name = name
        self.acquired_by = None
    
    def __enter__(self):
        """進入 with 區塊時呼叫"""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """離開 with 區塊時呼叫"""
        self.release()
        # 如果返回 False 或 None，異常會繼續傳播
        return False
    
    def acquire(self):
        thread_name = threading.current_thread().name
        print(f"🔒 {thread_name} 嘗試獲取 {self.name}")
        self._lock.acquire()
        self.acquired_by = thread_name
        print(f"✅ {thread_name} 獲得 {self.name}")
    
    def release(self):
        thread_name = threading.current_thread().name
        print(f"🔓 {thread_name} 釋放 {self.name}")
        self.acquired_by = None
        self._lock.release()

# 使用範例
shared_resource = 0
custom_lock = CustomLock("SharedResourceLock")

def worker_with_context_manager(worker_id):
    global shared_resource
    
    # 使用 with 語句自動管理鎖
    with custom_lock:
        print(f"⚙️ 工作者 {worker_id} 開始工作")
        
        # 模擬可能拋出異常的工作
        if worker_id == 2:
            time.sleep(0.5)
            # raise Exception("模擬異常")  # 取消註解測試異常處理
        
        shared_resource += 1
        print(f"📊 工作者 {worker_id}: shared_resource = {shared_resource}")
        time.sleep(0.5)

@contextmanager
def timeout_lock(lock, timeout=2):
    """帶超時的鎖上下文管理器"""
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"無法在 {timeout} 秒內獲取鎖")
    
    try:
        yield lock
    finally:
        lock.release()

def worker_with_timeout(worker_id):
    global shared_resource
    
    try:
        # 使用帶超時的鎖
        with timeout_lock(threading.Lock(), timeout=1):
            print(f"⚙️ 工作者 {worker_id} 獲得鎖")
            shared_resource += 1
            time.sleep(0.5)  # 模擬工作
    except TimeoutError as e:
        print(f"⏰ 工作者 {worker_id} 鎖超時: {e}")

def test_context_managers():
    global shared_resource
    shared_resource = 0
    
    print("=== 測試自訂鎖上下文管理器 ===")
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_with_context_manager, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\n最終 shared_resource 值: {shared_resource}")

if __name__ == "__main__":
    test_context_managers()
```

---

### 3. 執行緒本地儲存 (threading.local) 🏠

**白話解釋**: 像每個人都有自己的私人儲物櫃，互不幹擾  
**用途**: 每個執行緒都有獨立的變數副本  
**使用時機**: 需要在執行緒內保存狀態，但不希望被其他執行緒影響

```python
import threading
import time
import random

# 全域執行緒本地儲存
thread_local_data = threading.local()

class DatabaseConnection:
    """模擬資料庫連線"""
    
    def __init__(self, connection_id):
        self.connection_id = connection_id
        self.queries_count = 0
    
    def execute_query(self, query):
        self.queries_count += 1
        time.sleep(random.uniform(0.1, 0.3))  # 模擬查詢時間
        return f"結果-{self.connection_id}-{self.queries_count}"

class ConnectionManager:
    """連線管理器，為每個執行緒維護獨立的連線"""
    
    def get_connection(self):
        # 檢查當前執行緒是否已有連線
        if not hasattr(thread_local_data, 'db_connection'):
            # 為當前執行緒建立新連線
            thread_name = threading.current_thread().name
            connection_id = f"conn-{thread_name}-{random.randint(1000, 9999)}"
            thread_local_data.db_connection = DatabaseConnection(connection_id)
            print(f"🔗 為執行緒 {thread_name} 建立連線: {connection_id}")
        
        return thread_local_data.db_connection
    
    def close_connection(self):
        if hasattr(thread_local_data, 'db_connection'):
            conn = thread_local_data.db_connection
            thread_name = threading.current_thread().name
            print(f"🔒 執行緒 {thread_name} 關閉連線: {conn.connection_id} (執行了 {conn.queries_count} 次查詢)")
            del thread_local_data.db_connection

# 全域連線管理器
connection_manager = ConnectionManager()

def database_worker(worker_id, num_queries=3):
    """模擬資料庫工作者"""
    thread_name = threading.current_thread().name
    print(f"👷 工作者 {worker_id} ({thread_name}) 開始工作")
    
    try:
        for i in range(num_queries):
            # 獲取執行緒本地連線
            conn = connection_manager.get_connection()
            
            # 執行查詢
            query = f"SELECT * FROM table_{worker_id} WHERE id = {i}"
            result = conn.execute_query(query)
            
            print(f"📊 工作者 {worker_id}: 查詢 {i+1} 完成，結果: {result}")
            
            time.sleep(random.uniform(0.2, 0.5))
    
    finally:
        # 清理連線
        connection_manager.close_connection()

def test_thread_local():
    threads = []
    
    # 建立多個工作者執行緒
    for i in range(4):
        t = threading.Thread(
            target=database_worker, 
            args=(i, 3),
            name=f"Worker-{i}"
        )
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()

# 進階範例：Web 請求上下文
class RequestContext:
    """模擬 Web 請求上下文"""
    
    def __init__(self):
        self.user_id = None
        self.request_id = None
        self.start_time = None
        self.data = {}
    
    def set_user(self, user_id):
        self.user_id = user_id
    
    def set_request_id(self, request_id):
        self.request_id = request_id
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        if self.start_time:
            return time.time() - self.start_time
        return 0

# 全域請求上下文
request_context = threading.local()

def get_current_context():
    """獲取當前執行緒的請求上下文"""
    if not hasattr(request_context, 'context'):
        request_context.context = RequestContext()
    return request_context.context

def simulate_web_request(request_id, user_id):
    """模擬 Web 請求處理"""
    # 設定請求上下文
    ctx = get_current_context()
    ctx.set_request_id(request_id)
    ctx.set_user(user_id)
    
    print(f"🌐 處理請求 {request_id} (用戶: {user_id})")
    
    # 模擬請求處理的各個階段
    authenticate_user()
    fetch_user_data()
    process_business_logic()
    
    elapsed = ctx.get_elapsed_time()
    print(f"✅ 請求 {request_id} 完成，耗時: {elapsed:.2f}s")

def authenticate_user():
    """模擬用戶認證"""
    ctx = get_current_context()
    print(f"🔐 認證用戶 {ctx.user_id} (請求: {ctx.request_id})")
    time.sleep(random.uniform(0.1, 0.3))

def fetch_user_data():
    """模擬獲取用戶資料"""
    ctx = get_current_context()
    print(f"📋 獲取用戶 {ctx.user_id} 的資料 (請求: {ctx.request_id})")
    ctx.data['user_profile'] = f"profile_of_{ctx.user_id}"
    time.sleep(random.uniform(0.2, 0.5))

def process_business_logic():
    """模擬業務邏輯處理"""
    ctx = get_current_context()
    print(f"⚙️ 處理用戶 {ctx.user_id} 的業務邏輯 (請求: {ctx.request_id})")
    time.sleep(random.uniform(0.3, 0.7))

def test_web_request_context():
    print("\n=== 測試 Web 請求上下文 ===")
    
    threads = []
    requests = [
        ("req-001", "user-alice"),
        ("req-002", "user-bob"),
        ("req-003", "user-charlie"),
        ("req-004", "user-diana"),
    ]
    
    for request_id, user_id in requests:
        t = threading.Thread(
            target=simulate_web_request,
            args=(request_id, user_id),
            name=f"Request-{request_id}"
        )
        threads.append(t)
        t.start()
        time.sleep(0.1)  # 稍微錯開請求時間
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    print("=== 測試執行緒本地儲存 ===")
    test_thread_local()
    test_web_request_context()
```

---

## 效能比較與最佳實踐 📊

### 鎖的效能比較

```python
import threading
import time
import concurrent.futures
from contextlib import contextmanager

class PerformanceTest:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()
        self.rlock = threading.RLock()
        self.condition = threading.Condition()
        self.semaphore = threading.Semaphore(1)  # 模擬互斥鎖
    
    @contextmanager
    def timer(self, name):
        start = time.time()
        yield
        end = time.time()
        print(f"{name}: {end - start:.4f} 秒")
    
    def test_no_lock(self, iterations):
        """無鎖測試（不安全）"""
        def worker():
            for _ in range(iterations):
                self.counter += 1
        
        with self.timer("無鎖 (不安全)"):
            threads = [threading.Thread(target=worker) for _ in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_lock(self, iterations):
        """Lock 測試"""
        def worker():
            for _ in range(iterations):
                with self.lock:
                    self.counter += 1
        
        with self.timer("threading.Lock"):
            threads = [threading.Thread(target=worker) for _ in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_rlock(self, iterations):
        """RLock 測試"""
        def worker():
            for _ in range(iterations):
                with self.rlock:
                    self.counter += 1
        
        with self.timer("threading.RLock"):
            threads = [threading.Thread(target=worker) for _ in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    
    def test_semaphore(self, iterations):
        """Semaphore 測試"""
        def worker():
            for _ in range(iterations):
                with self.semaphore:
                    self.counter += 1
        
        with self.timer("threading.Semaphore(1)"):
            threads = [threading.Thread(target=worker) for _ in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

def run_performance_test():
    iterations = 50000
    
    print(f"📊 鎖效能測試 (每個執行緒 {iterations} 次操作)")
    print("=" * 50)
    
    test = PerformanceTest()
    
    # 重置計數器並測試不同的鎖
    test.counter = 0
    test.test_no_lock(iterations)
    print(f"結果: {test.counter} (預期: {4 * iterations})")
    
    test.counter = 0
    test.test_lock(iterations)
    print(f"結果: {test.counter}")
    
    test.counter = 0
    test.test_rlock(iterations)
    print(f"結果: {test.counter}")
    
    test.counter = 0
    test.test_semaphore(iterations)
    print(f"結果: {test.counter}")

if __name__ == "__main__":
    run_performance_test()
```

### 最佳實踐指南

```python
# 🎯 最佳實踐範例

class BestPracticesDemo:
    
    # ✅ 好的做法：使用 with 語句
    def good_lock_usage(self):
        lock = threading.Lock()
        shared_data = []
        
        def worker():
            with lock:  # 自動釋放，即使發生異常
                shared_data.append("data")
                # 即使這裡拋出異常，鎖也會被正確釋放
    
    # ❌ 不好的做法：手動管理鎖
    def bad_lock_usage(self):
        lock = threading.Lock()
        shared_data = []
        
        def worker():
            lock.acquire()
            shared_data.append("data")
            # 如果這裡拋出異常，鎖永遠不會被釋放！
            lock.release()
    
    # ✅ 好的做法：避免死鎖
    def avoid_deadlock(self):
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        
        def worker1():
            with lock1:  # 統一的鎖定順序
                with lock2:
                    pass
        
        def worker2():
            with lock1:  # 相同的順序
                with lock2:
                    pass
    
    # ❌ 不好的做法：可能死鎖
    def potential_deadlock(self):
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        
        def worker1():
            with lock1:
                with lock2:  # 順序：lock1 -> lock2
                    pass
        
        def worker2():
            with lock2:
                with lock1:  # 順序：lock2 -> lock1 (危險！)
                    pass
    
    # ✅ 好的做法：最小化鎖的持有時間
    def minimize_lock_time(self):
        lock = threading.Lock()
        
        def worker():
            # 在鎖外進行準備工作
            prepared_data = expensive_computation()
            
            # 只在必要時持有鎖
            with lock:
                quick_update(prepared_data)
            
            # 在鎖外進行後續處理
            post_processing()
    
    # ✅ 好的做法：使用適當的鎖粒度
    def appropriate_granularity(self):
        # 為不同的資源使用不同的鎖
        user_data_lock = threading.Lock()
        log_data_lock = threading.Lock()
        
        def update_user():
            with user_data_lock:  # 只鎖定用戶資料
                update_user_data()
        
        def write_log():
            with log_data_lock:  # 只鎖定日誌資料
                write_to_log()

# 輔助函數
def expensive_computation():
    time.sleep(0.1)
    return "prepared_data"

def quick_update(data):
    pass

def post_processing():
    time.sleep(0.1)

def update_user_data():
    pass

def write_to_log():
    pass
```

---

## 總結與選擇指南 🎯

### Python 鎖選擇流程

```
選擇決策樹：
┌─────────────────────────────────┐
│          需要同步嗎？            │
└─────────────┬───────────────────┘
              │ 是
              ▼
┌─────────────────────────────────┐
│        什麼類型的同步？          │
├─────────────────────────────────┤
│ 🔢 簡單計數/狀態   → atomic ops  │
│ 🔒 基本互斥       → Lock         │
│ 🔄 遞迴呼叫       → RLock        │
│ 📖 多讀少寫       → ReadWriteLock│
│ 🚗 資源數量限制   → Semaphore    │
│ 🚌 等待條件       → Condition    │
│ 📡 事件通知       → Event        │
│ 🚧 階段同步       → Barrier      │
│ 🏠 執行緒隔離     → local        │
└─────────────────────────────────┘
```

### 效能排序 (從快到慢)

```
性能排行榜：
🥇 無鎖操作        ████████████████ (最快，但不安全)
🥈 threading.local ███████████████░ (執行緒隔離)
🥉 threading.Lock  ████████████░░░░ (基本互斥)
4️⃣ threading.RLock ███████████░░░░░ (遞迴鎖)
5️⃣ Semaphore       ██████████░░░░░░ (資源控制)
6️⃣ Condition       █████████░░░░░░░ (條件等待)
```

### 使用建議總表

| 場景 | 推薦鎖類型 | 原因 | 範例 |
|------|-----------|------|------|
| 🔢 簡單計數器 | `threading.local` | 避免鎖競爭 | 統計資料 |
| 🔒 保護共享變數 | `threading.Lock` | 基本互斥 | 全域計數器 |
| 🔄 遞迴函數 | `threading.RLock` | 避免自我死鎖 | 樹狀結構遍歷 |
| 📖 快取系統 | `ReadWriteLock` | 多讀少寫 | 設定檔快取 |
| 🚗 連線池 | `threading.Semaphore` | 限制資源數 | 資料庫連線 |
| 🚌 生產消費 | `threading.Condition` | 條件等待 | 任務佇列 |
| 📡 狀態通知 | `threading.Event` | 一對多通知 | 下載完成 |
| 🚧 分階段任務 | `threading.Barrier` | 同步執行 | MapReduce |

### 💡 最佳實踐重點

1. **優先使用 `with` 語句** - 自動管理鎖的生命週期
2. **最小化鎖的持有時間** - 只在必要時持有鎖
3. **統一鎖定順序** - 避免死鎖
4. **選擇合適的鎖粒度** - 不要過粗或過細
5. **考慮使用 `threading.local`** - 避免鎖競爭
6. **測試併發場景** - 確保程式正確性

### 🚀 進階技巧

```python
# 鎖的超時處理
def try_with_timeout():
    lock = threading.Lock()
    if lock.acquire(timeout=1.0):
        try:
            # 執行臨界區程式碼
            pass
        finally:
            lock.release()
    else:
        print("獲取鎖超時")

# 鎖的狀態檢查
def check_lock_state():
    lock = threading.Lock()
    if lock.acquire(blocking=False):  # 非阻塞嘗試
        try:
            # 執行臨界區程式碼
            pass
        finally:
            lock.release()
    else:
        print("鎖目前被其他執行緒持有")
```

記住：**選擇正確的工具解決對應的問題，簡單場景用簡單工具，複雜場景用複雜工具** 🎯

Python 的執行緒同步機制提供了豐富的選擇，掌握這些工具將幫助您寫出更安全、更高效的多執行緒程式！ 🐍✨