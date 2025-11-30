# Python 與資料庫整合

> Python 應用與 Redis 整合、容器化開發環境配置。

## 🐍 Python + Redis

### Redis 連線
- [Python Connect Redis](python_connect_redis.md)

核心內容：
- Redis 連線配置
- 連線池管理
- 錯誤處理
- 最佳實踐

### Python-Redis 實戰
- [Python-Redis](python_redis.md)

核心內容：
- Redis 資料類型操作
- 快取策略
- 發布訂閱
- 實際應用案例

## 🛠️ 開發環境

### 本地開發配置
- [Docker Run Local](python_run_from_local.md)

核心內容：
- 本地程式碼掛載
- 熱重載配置
- 除錯設置
- 開發工作流

### 指令參考
- [Command](command.md)

核心內容：
- Docker 常用指令
- 容器管理
- 網路配置
- 故障排除

## 💡 Python + Redis 實戰

### 基本連線
```python
import redis

# 連接 Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# 測試連線
r.ping()
```

### 使用連線池
```python
import redis

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=10,
    decode_responses=True
)

r = redis.Redis(connection_pool=pool)
```

### 資料操作
```python
# 字串操作
r.set('key', 'value')
r.get('key')
r.setex('key', 3600, 'value')  # 設定過期時間

# Hash 操作
r.hset('user:1', 'name', 'John')
r.hset('user:1', 'email', 'john@example.com')
r.hgetall('user:1')

# List 操作
r.lpush('queue', 'task1')
r.lpush('queue', 'task2')
r.rpop('queue')

# Set 操作
r.sadd('tags', 'python', 'docker', 'redis')
r.smembers('tags')

# Sorted Set 操作
r.zadd('scores', {'player1': 100, 'player2': 200})
r.zrange('scores', 0, -1, withscores=True)
```

## 🐳 Docker Compose 整合

### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app  # 本地程式碼掛載
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis
    command: python app.py

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Python 應用配置
```python
import os
import redis

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)
```

## 🔧 開發環境最佳實踐

### Dockerfile (開發版)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 開發工具
RUN pip install --no-cache-dir ipython ipdb

# 不複製程式碼，使用 volume 掛載
CMD ["python", "-u", "app.py"]
```

### 熱重載配置
```python
# 使用 watchdog 實現熱重載
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f'Reloading {event.src_path}')
            # 重新載入邏輯

observer = Observer()
observer.schedule(ReloadHandler(), path='.', recursive=True)
observer.start()
```

### 除錯設置
```bash
# 進入容器除錯
docker-compose exec app bash

# 查看即時日誌
docker-compose logs -f app

# Python 除錯器
docker-compose run --rm app python -m pdb app.py
```

## 📊 快取策略

### 簡單快取
```python
import json
import redis

r = redis.Redis(host='redis', decode_responses=True)

def get_user(user_id):
    # 先查快取
    cache_key = f'user:{user_id}'
    cached = r.get(cache_key)

    if cached:
        return json.loads(cached)

    # 查詢資料庫
    user = db.query(user_id)

    # 寫入快取
    r.setex(cache_key, 3600, json.dumps(user))

    return user
```

### 發布訂閱
```python
# 發布者
r.publish('channel', 'message')

# 訂閱者
pubsub = r.pubsub()
pubsub.subscribe('channel')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(message['data'])
```

**最後更新**: 2025-12-01
