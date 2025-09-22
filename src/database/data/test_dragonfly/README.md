# DragonflyDB 安裝與測試套件

這個專案提供完整的 DragonflyDB 安裝腳本和 Python 測試套件。

## 📁 檔案說明

- **install_dragonfly.sh** - DragonflyDB 自動安裝腳本
- **comprehensive_test.py** - 綜合測試套件（功能、性能、壓力測試）
- **test_dragonfly.py** - 基本功能測試腳本

## 🚀 快速開始

### 1. 安裝 DragonflyDB

```bash
# 使用預設設定安裝（端口 6379，2GB 記憶體，4 執行緒）
./install_dragonfly.sh

# 自訂安裝
./install_dragonfly.sh [端口] [記憶體] [執行緒數]
# 例如：
./install_dragonfly.sh 6380 4gb 8
```

### 2. 執行測試

#### 基本功能測試
```bash
python3 test_dragonfly.py
```

#### 綜合測試（包含性能測試）
```bash
python3 comprehensive_test.py
```

#### 包含壓力測試
```bash
python3 comprehensive_test.py --stress
```

#### 指定連接參數
```bash
python3 comprehensive_test.py --host localhost --port 6379 --verbose
```

## 📊 測試內容

### comprehensive_test.py 測試項目

**功能測試：**
- ✅ 字串操作 (SET/GET, MSET/MGET, APPEND, GETRANGE)
- ✅ 數值操作 (INCR/DECR, INCRBYFLOAT)
- ✅ 列表操作 (LPUSH/LPOP, LINDEX/LSET, LTRIM)
- ✅ 哈希操作 (HSET/HGET, HINCRBY, HKEYS/HVALS)
- ✅ 集合操作 (SADD/SREM, SINTER/SUNION/SDIFF)
- ✅ 有序集合 (ZADD/ZRANGE, ZINCRBY)
- ✅ 鍵操作 (EXISTS/DELETE, EXPIRE/TTL, RENAME)
- ✅ 事務 (Pipeline)
- ✅ Pub/Sub
- ✅ 大值處理 (1MB)

**性能測試：**
- SET/GET 吞吐量
- Pipeline 批量操作
- 延遲統計

**壓力測試：**
- 多線程並發
- 延遲分析 (P95, P99)
- 吞吐量測試

## 🔧 DragonflyDB 管理

### 常用 Docker 命令

```bash
# 查看容器狀態
docker ps | grep dragonfly-main

# 查看日誌
docker logs dragonfly-main --tail 50

# 進入 Redis CLI
docker exec -it dragonfly-main redis-cli

# 停止服務
docker stop dragonfly-main

# 啟動服務
docker start dragonfly-main

# 重啟服務
docker restart dragonfly-main

# 查看統計
docker exec dragonfly-main redis-cli INFO
```

### Python 連接範例

```python
import redis

# 連接 DragonflyDB
r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# 測試連接
r.ping()

# 基本操作
r.set('key', 'value')
value = r.get('key')
print(value)
```

## 📋 系統需求

- Docker
- Python 3.x
- redis-py 套件
- hiredis 套件 (可選，提升性能)

## 🎯 測試結果範例

```
============================================================
         DragonflyDB 綜合測試套件
============================================================
服務器版本: 7.4.0
運行時間: 1091 秒

📝 字串操作測試
✅ SET/GET
✅ MSET/MGET
✅ APPEND
✅ GETRANGE

⚡ 性能測試 (5000 操作)
  操作              時間(秒)        吞吐量(ops/s)
  ------------------------------------------
  SET             0.518        9653
  GET             0.493        10151
  Pipeline        0.020        247204

測試結果總結
============================================================
  通過: 22
  失敗: 0
  成功率: 100.0%

✅ 所有測試通過！
```

## 📝 注意事項

1. DragonflyDB 完全相容 Redis 協議
2. 使用 Docker 容器運行，確保 Docker 服務正常
3. 預設數據儲存在 Docker volume `dragonfly-data`
4. 支援持久化，重啟後數據不會丟失

## 🔗 相關資源

- [DragonflyDB 官方文檔](https://www.dragonflydb.io/docs)
- [Redis 命令參考](https://redis.io/commands)
- [redis-py 文檔](https://redis-py.readthedocs.io/)