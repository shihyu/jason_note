# Python 異步編程完整指南

## 目錄
- [架構層次關係](#架構層次關係)
- [核心組件詳解](#核心組件詳解)
- [實戰範例](#實戰範例)
- [性能優化建議](#性能優化建議)
- [常見問題與解決方案](#常見問題與解決方案)
- [最佳實踐總結](#最佳實踐總結)

## 架構層次關係

```
┌─────────────────────────────────────────────────────────┐
│                     應用程式碼                            │
├─────────────────────────────────────────────────────────┤
│ async/await (語法層)                                     │
├─────────────────────────────────────────────────────────┤
│ asyncio (事件循環層)                                     │
├─────────────────────────────────────────────────────────┤
│ aiohttp (HTTP 客戶端層)                                  │
├─────────────────────────────────────────────────────────┤
│ connector (連線管理層)                                   │
└─────────────────────────────────────────────────────────┘
```

### 組件關係圖

```
async/await (語法) → asyncio (事件循環) → aiohttp (HTTP客戶端) → connector (連線管理)
     ↓                    ↓                    ↓                     ↓
   異步語法            事件循環框架          異步HTTP庫            連線池配置
```

### 各組件職責

| 組件 | 職責 | 必需性 |
|------|------|--------|
| **async/await** | 定義異步函數語法 | 必需 |
| **asyncio** | 事件循環管理 | 必需 |
| **aiohttp** | HTTP 客戶端實現 | 可選* |
| **connector** | 連線池配置 | 可選 |

*可選意思是你也可以用其他異步 HTTP 庫如 `httpx`

## 核心組件詳解

### 1. async/await - 異步語法基礎

#### 基本語法
```python
# 異步函數定義
async def async_function():
    """異步函數定義"""
    result = await some_async_operation()
    return result

# 錯誤示範
def normal_function():
    # SyntaxError: 'await' outside async function
    result = await some_async_operation()  # ❌ 錯誤
```

#### 語法要點
```python
# 這只是語法，告訴 Python 這是異步函數
async def my_function():
    await some_async_operation()
```

### 2. asyncio - 事件循環引擎

#### 基本使用
```python
import asyncio

# asyncio 提供事件循環，管理所有異步任務
async def main():
    # 在這裡運行異步任務
    await asyncio.sleep(1)
    return "完成"

# 啟動事件循環
asyncio.run(main())
```

#### 三種運行方式
```python
# 方式 1: asyncio.run() (Python 3.7+) - 推薦
result = asyncio.run(main())

# 方式 2: 手動管理事件循環
loop = asyncio.get_event_loop()
try:
    result = loop.run_until_complete(main())
finally:
    loop.close()

# 方式 3: 在 Jupyter 中
await main()  # Jupyter 已有事件循環
```

### 3. aiohttp - 異步 HTTP 客戶端

#### 基本使用
```python
import aiohttp

# aiohttp 是基於 asyncio 的 HTTP 庫
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://example.com') as response:
            return await response.text()
```

#### 多請求並行
```python
async def fetch_multiple(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = session.get(url)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        results = []
        for response in responses:
            results.append(await response.json())
        return results
```

### 4. TCPConnector - 連線池管理

#### 基本配置
```python
import aiohttp

# connector 是 aiohttp 的連線池配置
connector = aiohttp.TCPConnector(
    limit=100,           # 連線池參數
    limit_per_host=20
)

async with aiohttp.ClientSession(connector=connector) as session:
    # session 使用這個 connector 的設定
    pass
```

#### 詳細配置選項
```python
connector = aiohttp.TCPConnector(
    # 連線池大小
    limit=100,                    # 總連線數限制
    limit_per_host=30,           # 每個 host 連線數
    
    # 連線保持
    keepalive_timeout=60,        # Keep-alive 超時
    force_close=False,           # 是否強制關閉連線
    
    # DNS 相關
    ttl_dns_cache=300,          # DNS 快取時間
    
    # SSL/TLS
    ssl=True,                   # 啟用 SSL
    verify_ssl=True,            # 驗證 SSL 證書
    
    # 性能優化
    enable_cleanup_closed=True,  # 清理關閉的連線
)
```

## 完整組合使用範例

```python
import asyncio
import aiohttp

async def fetch_multiple_urls(urls):
    # 1. connector: 配置連線池
    connector = aiohttp.TCPConnector(
        limit=200,
        limit_per_host=50,
        keepalive_timeout=60
    )
    
    # 2. aiohttp: 提供異步 HTTP 功能
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # 3. async/await: 異步語法
        async def fetch_one(url):
            async with session.get(url) as response:
                return await response.text()
        
        # 4. asyncio.gather: 並行執行多個任務
        tasks = [fetch_one(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
    return results

# 5. asyncio.run: 啟動事件循環
if __name__ == "__main__":
    urls = ["http://example.com"] * 100
    results = asyncio.run(fetch_multiple_urls(urls))
```

## 對比不同組合

```python
# 組合1: 只有 async，沒有 aiohttp
async def basic_async():
    await asyncio.sleep(1)  # 只能做基本異步操作

# 組合2: aiohttp 但沒有自定義 connector  
async def default_aiohttp():
    async with aiohttp.ClientSession() as session:  # 使用默認 connector
        return await session.get(url)

# 組合3: 完整組合
async def optimized_aiohttp():
    connector = aiohttp.TCPConnector(limit_per_host=50)  # 自定義 connector
    async with aiohttp.ClientSession(connector=connector) as session:
        return await session.get(url)
```

## 為什麼需要 Connector？

```python
# 沒有 connector 配置
async with aiohttp.ClientSession() as session:
    # 默認：每個 host 只有 30 條連線
    tasks = [session.get(url) for url in urls_1000]  # 可能很慢

# 有 connector 優化
connector = aiohttp.TCPConnector(limit_per_host=100)
async with aiohttp.ClientSession(connector=connector) as session:
    # 現在：每個 host 可以 100 條並行連線
    tasks = [session.get(url) for url in urls_1000]  # 快很多！
```

## 實戰範例

### 範例 1: 基礎爬蟲

```python
import asyncio
import aiohttp
import time

async def fetch_url(session, url):
    """抓取單個 URL"""
    try:
        async with session.get(url, timeout=10) as response:
            return {
                'url': url,
                'status': response.status,
                'content': await response.text()
            }
    except Exception as e:
        return {
            'url': url,
            'error': str(e)
        }

async def crawl_websites(urls):
    """並行爬取多個網站"""
    # 配置連線池
    connector = aiohttp.TCPConnector(
        limit=50,
        limit_per_host=10
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
    return results

# 使用範例
if __name__ == "__main__":
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/delay/3',
    ]
    
    start = time.time()
    results = asyncio.run(crawl_websites(urls))
    print(f"完成時間: {time.time() - start:.2f} 秒")
```

### 範例 2: API 客戶端封裝

```python
class AsyncAPIClient:
    """異步 API 客戶端"""
    
    def __init__(self, base_url, max_connections=100):
        self.base_url = base_url
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=30,
            keepalive_timeout=60
        )
        self.session = None
    
    async def __aenter__(self):
        """進入上下文管理器"""
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            headers={'User-Agent': 'AsyncClient/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """離開上下文管理器"""
        await self.session.close()
    
    async def get(self, endpoint, **kwargs):
        """GET 請求"""
        url = f"{self.base_url}{endpoint}"
        async with self.session.get(url, **kwargs) as response:
            return await response.json()
    
    async def post(self, endpoint, data=None, **kwargs):
        """POST 請求"""
        url = f"{self.base_url}{endpoint}"
        async with self.session.post(url, json=data, **kwargs) as response:
            return await response.json()

# 使用範例
async def main():
    async with AsyncAPIClient('https://api.github.com') as client:
        # 並行請求
        user, repos = await asyncio.gather(
            client.get('/users/python'),
            client.get('/users/python/repos')
        )
        print(f"User: {user['name']}")
        print(f"Repos: {len(repos)}")

asyncio.run(main())
```

### 範例 3: 速率限制與重試

```python
import asyncio
import aiohttp
from asyncio import Semaphore
from typing import List, Dict, Any

class RateLimitedClient:
    """帶速率限制的客戶端"""
    
    def __init__(self, rate_limit: int = 10, retry_count: int = 3):
        self.semaphore = Semaphore(rate_limit)
        self.retry_count = retry_count
        self.connector = aiohttp.TCPConnector(limit=rate_limit * 2)
    
    async def fetch_with_retry(self, session, url):
        """帶重試機制的請求"""
        for attempt in range(self.retry_count):
            try:
                async with self.semaphore:  # 速率限制
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Too Many Requests
                            wait_time = int(response.headers.get('Retry-After', 2 ** attempt))
                            await asyncio.sleep(wait_time)
                        else:
                            response.raise_for_status()
            except aiohttp.ClientError as e:
                if attempt == self.retry_count - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指數退避
    
    async def fetch_all(self, urls: List[str]) -> List[Dict[Any, Any]]:
        """批量請求"""
        async with aiohttp.ClientSession(connector=self.connector) as session:
            tasks = [self.fetch_with_retry(session, url) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)

# 使用範例
async def main():
    client = RateLimitedClient(rate_limit=5)
    urls = [f'https://httpbin.org/delay/{i}' for i in range(10)]
    results = await client.fetch_all(urls)
    print(f"成功請求: {sum(1 for r in results if not isinstance(r, Exception))}")

asyncio.run(main())
```

## 性能優化建議

### 1. 連線池優化

```python
# 針對不同場景的優化配置

# 高並發場景
high_concurrency_connector = aiohttp.TCPConnector(
    limit=1000,
    limit_per_host=100,
    ttl_dns_cache=300,
    enable_cleanup_closed=True
)

# 長連線場景
persistent_connector = aiohttp.TCPConnector(
    limit=50,
    keepalive_timeout=300,
    force_close=False
)

# 受限 API 場景
rate_limited_connector = aiohttp.TCPConnector(
    limit=10,
    limit_per_host=2,
    keepalive_timeout=30
)
```

### 2. 記憶體優化

```python
async def stream_large_file(url):
    """串流處理大文件"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # 不要使用 await response.read()
            async for chunk in response.content.iter_chunked(1024):
                process_chunk(chunk)  # 逐塊處理
```

### 3. 超時設置

```python
# 全局超時
timeout = aiohttp.ClientTimeout(
    total=300,      # 總超時
    connect=10,     # 連線超時
    sock_read=60    # 讀取超時
)

async with aiohttp.ClientSession(timeout=timeout) as session:
    # 所有請求都使用這個超時設置
    pass
```

## 常見問題與解決方案

### 問題 1: "Event loop is closed"

```python
# 問題代碼
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
loop.run_until_complete(another_task())  # ❌ 錯誤

# 解決方案
asyncio.run(main())         # 自動管理循環
asyncio.run(another_task())  # 每次創建新循環
```

### 問題 2: "Session is closed"

```python
# 問題代碼
session = aiohttp.ClientSession()
await session.get(url)
await session.close()
await session.get(another_url)  # ❌ 錯誤

# 解決方案
async with aiohttp.ClientSession() as session:
    await session.get(url)
    await session.get(another_url)  # ✅ 正確
```

### 問題 3: 並發數過高導致錯誤

```python
# 使用 Semaphore 限制並發
async def limited_fetch(semaphore, session, url):
    async with semaphore:
        return await session.get(url)

async def main():
    semaphore = asyncio.Semaphore(10)  # 最多 10 個並發
    async with aiohttp.ClientSession() as session:
        tasks = [limited_fetch(semaphore, session, url) for url in urls]
        await asyncio.gather(*tasks)
```

## 最佳實踐總結

1. **永遠使用上下文管理器** 管理 Session 和 Connector
2. **設置合理的超時時間** 避免無限等待
3. **使用 Semaphore** 控制並發數量
4. **實現重試機制** 處理暫時性錯誤
5. **監控連線池狀態** 進行性能調優
6. **處理異常** 確保程式穩定性
7. **使用串流處理** 處理大文件
8. **合理配置 DNS 快取** 減少 DNS 查詢

## 關鍵概念總結

**記住：它們是一個完整異步 HTTP 解決方案的不同層次，而不是競爭關係！**

- **async/await**: 提供異步語法支持
- **asyncio**: 管理事件循環和任務調度
- **aiohttp**: 實現異步 HTTP 客戶端功能
- **connector**: 優化連線池和網路性能

## 相關資源

- [asyncio 官方文檔](https://docs.python.org/3/library/asyncio.html)
- [aiohttp 官方文檔](https://docs.aiohttp.org/)
- [Python 異步編程指南](https://realpython.com/async-io-python/)
- [aiohttp 性能優化](https://docs.aiohttp.org/en/stable/client_advanced.html)
- [Python Async/Await 教程](https://www.python.org/dev/peps/pep-0492/)

---

*最後更新：2025*