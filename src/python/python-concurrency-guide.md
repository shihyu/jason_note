# Python 並發編程完整指南

## 目錄
1. [基礎概念：執行緒與進程](#基礎概念執行緒與進程)
2. [CPU 密集型 vs I/O 密集型任務](#cpu-密集型-vs-io-密集型任務)
3. [ThreadPoolExecutor 詳解](#threadpoolexecutor-詳解)
4. [ThreadPoolExecutor vs asyncio](#threadpoolexecutor-vs-asyncio)

---

## 基礎概念：執行緒與進程

### 什麼是執行緒（Thread）？

**執行緒（Thread）是程式執行的最小單位**。當作業系統運行程式時，會將每個程式視為一個「進程（Process）」，而每個進程內部可以有一個或多個執行緒來負責執行不同的工作。

#### 單執行緒範例
```python
import time

def task1():
    print("🔄 任務 1 開始執行")
    time.sleep(3)  # 模擬 3 秒的工作時間
    print("✅ 任務 1 完成")

def task2():
    print("🔄 任務 2 開始執行")
    time.sleep(2)  # 模擬 2 秒的工作時間
    print("✅ 任務 2 完成")

print("🚀 開始執行程式")
task1()
task2()
print("🎉 所有任務完成")
```

**執行結果：**
- 總執行時間：5 秒
- task1() 執行完後，task2() 才開始執行

#### 多執行緒範例
```python
import threading
import time

def task1():
    print("🔄 任務 1（執行緒 1）開始執行")
    time.sleep(3)
    print("✅ 任務 1（執行緒 1）完成")

def task2():
    print("🔄 任務 2（執行緒 2）開始執行")
    time.sleep(2)
    print("✅ 任務 2（執行緒 2）完成")

print("🚀 開始執行程式")

# 創建兩個執行緒
thread1 = threading.Thread(target=task1)
thread2 = threading.Thread(target=task2)

# 啟動執行緒
thread1.start()
thread2.start()

# 等待執行緒執行完畢
thread1.join()
thread2.join()

print("🎉 所有任務完成")
```

**執行結果：**
- 總執行時間：3 秒（比單執行緒快 2 秒）
- task1() 和 task2() 同時執行

### 進程 vs 執行緒比較

| 類別 | 進程（Process） | 執行緒（Thread） |
|------|-----------------|------------------|
| **定義** | 程式的執行實體 | 進程內的執行單位 |
| **記憶體** | 不共享記憶體 | 共享記憶體 |
| **建立成本** | 高（需要獨立記憶體） | 低（共用進程資源） |
| **適用場景** | CPU 密集型（影像處理、數據計算） | I/O 密集型（API 請求、爬蟲） |

### Python 實作範例

#### 進程範例（使用 multiprocessing）
```python
from multiprocessing import Process
import time

def task(name):
    print(f"🔄 進程 {name} 開始執行")
    time.sleep(2)
    print(f"✅ 進程 {name} 完成")

if __name__ == "__main__":
    process1 = Process(target=task, args=("P1",))
    process2 = Process(target=task, args=("P2",))
    
    process1.start()
    process2.start()
    
    process1.join()
    process2.join()
    
    print("🎉 所有進程完成")
```

#### 執行緒範例（使用 threading）
```python
import threading
import time

def task(name):
    print(f"🔄 執行緒 {name} 開始執行")
    time.sleep(2)
    print(f"✅ 執行緒 {name} 完成")

thread1 = threading.Thread(target=task, args=("T1",))
thread2 = threading.Thread(target=task, args=("T2",))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("🎉 所有執行緒完成")
```

### 真實世界的應用案例

| 應用程式 | 進程（Process） | 執行緒（Thread） |
|----------|-----------------|------------------|
| **Google Chrome** | 每個分頁是獨立進程 | 分頁內的 JavaScript、影片播放等 |
| **VS Code** | 主程式是一個進程 | 語法分析、插件運行等 |
| **遊戲（如 GTA 5）** | 遊戲本體是進程 | 渲染、物理計算、AI 行為 |
| **音樂播放器（Spotify）** | 播放器是進程 | 下載音樂、播放、UI 顯示 |

---

## CPU 密集型 vs I/O 密集型任務

### 什麼是 CPU 密集型（CPU-Bound）？

CPU 運算指的是程式執行速度受限於 CPU 的運算能力，這類運算通常需要大量計算。

**常見場景：**
- 機器學習與深度學習訓練
- 影像處理（如 Photoshop 濾鏡）
- 數學計算（矩陣運算、大量迴圈）
- 數據分析與統計運算

📌 **適合使用多進程（Multiprocessing）**來充分利用多核心 CPU。

### 什麼是 I/O 密集型（I/O-Bound）？

I/O 操作指的是程式執行速度受限於外部設備（網路、硬碟、資料庫）的存取速度。

**常見場景：**
- 讀取或寫入檔案
- 發送 API 請求
- 存取資料庫
- 網頁爬蟲

📌 **適合使用多執行緒（Threading）**來同時執行多個 I/O 任務。

### ThreadPoolExecutor vs ProcessPoolExecutor

| 功能 | ThreadPoolExecutor | ProcessPoolExecutor |
|------|-------------------|---------------------|
| **適用場景** | I/O 密集型（API、爬蟲、檔案讀寫） | CPU 密集型（數據計算、影像處理） |
| **資源使用** | 多執行緒（共享記憶體） | 多進程（獨立記憶體） |
| **GIL 限制** | 是（Python GIL 限制） | 否（每個進程有獨立解釋器） |
| **開銷** | 低（執行緒切換快） | 高（需要額外記憶體） |

### 實作範例

#### I/O 密集型：使用 ThreadPoolExecutor
```python
from concurrent.futures import ThreadPoolExecutor
import requests

URLS = [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/todos/2"
]

def fetch_data(url):
    response = requests.get(url)
    return response.json()

with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(fetch_data, URLS))
    print(results)  # 同時發送 API 請求
```

#### CPU 密集型：使用 ProcessPoolExecutor
```python
from concurrent.futures import ProcessPoolExecutor

def compute(n):
    return sum(i**2 for i in range(n))

numbers = [10**6, 10**6, 10**6]

with ProcessPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(compute, numbers))
    print(results)  # 使用多核心 CPU 計算
```

---

## ThreadPoolExecutor 詳解

### 什麼是 ThreadPoolExecutor？

`ThreadPoolExecutor` 是 Python `concurrent.futures` 模組的一部分，提供管理執行緒池（Thread Pool）的方式，讓程式能夠更快地處理大量 I/O 操作。

### 基本用法

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    """模擬一個需要 2 秒的工作"""
    print(f"🔄 任務 {n} 開始執行")
    time.sleep(2)
    print(f"✅ 任務 {n} 完成")
    return f"任務 {n} 的結果"

# 建立執行緒池，最多允許 3 個執行緒同時運行
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(task, range(5)))  # 執行 5 個任務
    print(results)
```

### submit() vs map() 的差異

| 功能 | submit() | map() |
|------|----------|-------|
| **提交方式** | 逐個提交（單次處理單一任務） | 批量提交（單次處理多個任務） |
| **回傳值** | Future 物件（需 .result() 取得） | 直接回傳結果列表 |
| **適用場景** | 需要逐步處理結果、錯誤處理 | 單輸入對應單輸出的批量處理 |
| **錯誤處理** | 更靈活，可單獨捕捉錯誤 | 一個任務失敗會中斷整個 map() |

#### submit() 範例
```python
from concurrent.futures import ThreadPoolExecutor

def square(n):
    return n * n

with ThreadPoolExecutor(max_workers=3) as executor:
    future1 = executor.submit(square, 2)
    future2 = executor.submit(square, 3)
    
    print(future1.result())  # 4
    print(future2.result())  # 9
```

#### submit() 錯誤處理
```python
def divide(n, d):
    if d == 0:
        raise ValueError("❌ 除數不能為 0")
    return n / d

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(divide, 10, i) for i in range(3)]
    
    for future in futures:
        try:
            print(future.result())
        except Exception as e:
            print(f"⚠️ 錯誤: {e}")
```

#### map() 範例
```python
def square(n):
    return n * n

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(square, [1, 2, 3, 4, 5])
    print(list(results))  # [1, 4, 9, 16, 25]
```

### ThreadPoolExecutor 應用場景

| 應用場景 | 為什麼適合 | 示例應用 |
|----------|------------|----------|
| **API 請求** | 同時發送多個請求，提高效率 | OpenAI API、天氣查詢 |
| **網路爬蟲** | 同時爬取多個網頁 | 新聞爬取、批量下載 |
| **檔案 I/O** | 同時處理多個文件 | 日誌分析、格式轉換 |
| **背景任務** | 不影響主流程 | 自動備份、數據同步 |

### 實戰應用

#### 同時發送多個 API 請求
```python
from concurrent.futures import ThreadPoolExecutor
import requests

API_URLS = [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/todos/2",
    "https://jsonplaceholder.typicode.com/todos/3"
]

def fetch_data(url):
    response = requests.get(url)
    return response.json()

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch_data, API_URLS))
    print(results)
```

#### 批量處理檔案
```python
from concurrent.futures import ThreadPoolExecutor

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

files = ["file1.txt", "file2.txt", "file3.txt"]

with ThreadPoolExecutor(max_workers=3) as executor:
    contents = list(executor.map(read_file, files))
    print(contents)
```

### 最佳實踐

1. **控制 max_workers**：通常設為 CPU 核心數 * 2
2. **使用 submit() 處理回傳值**：需要獲取結果時更靈活
3. **確保使用 with 語法**：自動關閉執行緒池，避免資源浪費

### 潛在問題與解決方案

| 問題 | 解決方案 |
|------|----------|
| 大量執行緒導致記憶體耗盡 | 適當限制 max_workers |
| 共享變數的 Race Condition | 使用 threading.Lock() 保護 |
| 網路請求異常（如超時） | 使用 try-except 捕捉錯誤 |

---

## ThreadPoolExecutor vs asyncio

### 兩種並發方式的比較

Python 提供兩種方式來提高 I/O 操作效率：

1. **多執行緒（Threading）**：使用 `ThreadPoolExecutor` 並行執行同步函式
2. **非同步（Asynchronous）**：使用 `asyncio` 非同步執行支援 async 的函式

### 核心差異

| 特性 | ThreadPoolExecutor | asyncio |
|------|-------------------|---------|
| **並行方式** | 多個執行緒 | 單執行緒 + 事件迴圈 |
| **適合場景** | 同步 I/O（requests、檔案讀寫） | 支援 async 的函式（aiohttp） |
| **GIL 限制** | 是（但 I/O 影響不大） | 否（非同步處理） |
| **CPU 密集型** | ❌ 不適合 | ❌ 不適合 |

### ThreadPoolExecutor 範例

```python
import requests
from concurrent.futures import ThreadPoolExecutor
import time

URLS = [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/todos/2",
    "https://jsonplaceholder.typicode.com/todos/3",
]

def fetch(url):
    """發送 HTTP 請求（同步）"""
    print(f"🔄 發送請求: {url}")
    response = requests.get(url)
    print(f"✅ 完成請求: {url}")
    return response.json()

start_time = time.time()

# 使用 ThreadPoolExecutor 讓多個請求同時執行
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, URLS))

end_time = time.time()
print(f"總執行時間: {end_time - start_time:.2f} 秒")
```

**優點：**
- 簡單易用，不需要修改現有同步程式碼
- 適合處理 `requests` 等同步庫

### asyncio 範例

```python
import aiohttp
import asyncio

URLS = [
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://jsonplaceholder.typicode.com/todos/2",
    "https://jsonplaceholder.typicode.com/todos/3",
]

async def fetch(session, url):
    """使用 aiohttp 非同步發送請求"""
    print(f"🔄 發送請求: {url}")
    async with session.get(url) as response:
        result = await response.json()
        print(f"✅ 完成請求: {url}")
        return result

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in URLS]
        results = await asyncio.gather(*tasks)
        return results

# 執行非同步主程式
results = asyncio.run(main())
print(results)
```

**優點：**
- 真正的非同步執行，效能更好
- 單執行緒，資源消耗更少

### asyncio + ThreadPoolExecutor 混合使用

當需要在 asyncio 環境中執行同步函式時，可以使用 `run_in_executor`：

```python
import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "https://jsonplaceholder.typicode.com/todos/1"

def fetch():
    """同步函式"""
    return requests.get(URL).json()

async def main():
    loop = asyncio.get_running_loop()
    
    # 在執行緒池中執行同步函式
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, fetch)
        print(result)

asyncio.run(main())
```

### 運作流程圖解

#### ThreadPoolExecutor 運作流程
```
主執行緒
    ├─> 執行緒 1: 執行 task1()
    ├─> 執行緒 2: 執行 task2()
    └─> 執行緒 3: 執行 task3()
    
所有執行緒同時運行，但受 GIL 限制
```

#### asyncio 運作流程
```
事件迴圈（單執行緒）
    ├─> task1(): 遇到 await，切換到 task2()
    ├─> task2(): 遇到 await，切換到 task3()
    └─> task3(): 遇到 await，切換回 task1()
    
單執行緒內快速切換，不會阻塞
```

### 效能比較

| 方法 | 執行方式 | 3 個請求耗時（每個 1 秒） |
|------|----------|---------------------------|
| **單執行緒（同步）** | 逐個請求 | ⏳ 3 秒 |
| **ThreadPoolExecutor** | 3 個執行緒同時 | 🚀 1 秒 |
| **asyncio** | 單執行緒非同步 | 🚀 1 秒 |

### 選擇建議

#### 使用 ThreadPoolExecutor 的情況：
- 使用 `requests` 等同步庫
- 現有程式碼是同步的，不想大幅修改
- 需要快速實現並發功能

#### 使用 asyncio 的情況：
- 使用 `aiohttp` 等非同步庫
- 需要處理大量並發連接（如 WebSocket）
- 追求更高的效能和更低的資源消耗

#### 混合使用的情況：
- 主體使用 asyncio，但需要呼叫某些同步函式
- 逐步將同步程式碼遷移到非同步

---

## 總結與最佳實踐

### 快速選擇指南

```
任務類型判斷：
├─> CPU 密集型？
│   └─> 使用 ProcessPoolExecutor
│
└─> I/O 密集型？
    ├─> 需要使用同步庫（requests）？
    │   └─> 使用 ThreadPoolExecutor
    │
    └─> 可以使用非同步庫（aiohttp）？
        └─> 使用 asyncio
```

### 核心要點

1. **執行緒 vs 進程**
   - 執行緒：共享記憶體，適合 I/O 密集型
   - 進程：獨立記憶體，適合 CPU 密集型

2. **Python GIL 限制**
   - 影響多執行緒的 CPU 運算效能
   - 不影響 I/O 操作的並發

3. **ThreadPoolExecutor 使用場景**
   - API 請求、檔案處理、網路爬蟲
   - 快速將同步程式碼並行化

4. **asyncio 優勢**
   - 真正的非同步執行
   - 更高效能、更低資源消耗

### 實戰建議

1. **從簡單開始**：先用 ThreadPoolExecutor 優化現有同步程式碼
2. **逐步遷移**：新專案考慮使用 asyncio
3. **混合使用**：在 asyncio 中用 run_in_executor 執行同步函式
4. **監控效能**：根據實際場景測試並選擇最佳方案

### 常見陷阱與解決方案

| 陷阱 | 解決方案 |
|------|----------|
| 過多執行緒導致資源耗盡 | 限制 max_workers 數量 |
| 同步函式阻塞 asyncio | 使用 run_in_executor |
| GIL 限制 CPU 運算 | 改用 ProcessPoolExecutor |
| Race Condition | 使用 Lock 或其他同步機制 |

---

## 參考資源

- [Python 官方文件 - concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
- [Python 官方文件 - asyncio](https://docs.python.org/3/library/asyncio.html)
- [Python 官方文件 - threading](https://docs.python.org/3/library/threading.html)
- [Python 官方文件 - multiprocessing](https://docs.python.org/3/library/multiprocessing.html)