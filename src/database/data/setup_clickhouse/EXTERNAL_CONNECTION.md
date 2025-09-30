# ClickHouse 外部連線設定

## 連線資訊

### 本機連線
- **主機**: localhost 或 127.0.0.1
- **HTTP 端口**: 8123
- **Native 端口**: 9000
- **使用者**: trader
- **密碼**: SecurePass123!
- **資料庫**: market_data

### 外部連線
- **主機**: 219.68.168.47 (你的公網 IP)
- **HTTP 端口**: 8123
- **Native 端口**: 9000
- **使用者**: trader
- **密碼**: SecurePass123!
- **資料庫**: market_data

## Python 連線範例

### 本機連線
```python
from clickhouse_driver import Client

client = Client(
    host='localhost',
    port=9000,
    user='trader',
    password='SecurePass123!',
    database='market_data'
)

# 測試連線
result = client.execute('SELECT version()')
print(f"ClickHouse 版本: {result[0][0]}")
```

### 外部連線
```python
from clickhouse_driver import Client

client = Client(
    host='219.68.168.47',  # 外部 IP
    port=9000,
    user='trader',
    password='SecurePass123!',
    database='market_data'
)

# 測試連線
result = client.execute('SELECT version()')
print(f"ClickHouse 版本: {result[0][0]}")
```

## HTTP API 連線範例

### 使用 curl (本機)
```bash
# 查詢版本
curl -u trader:SecurePass123! 'http://localhost:8123/?query=SELECT%20version()'

# 查詢資料
curl -u trader:SecurePass123! 'http://localhost:8123/?query=SELECT%20*%20FROM%20market_data.market_ticks%20LIMIT%205'
```

### 使用 curl (外部)
```bash
# 查詢版本
curl -u trader:SecurePass123! 'http://219.68.168.47:8123/?query=SELECT%20version()'

# 查詢資料
curl -u trader:SecurePass123! 'http://219.68.168.47:8123/?query=SELECT%20*%20FROM%20market_data.market_ticks%20LIMIT%205'
```

### 使用 Python requests
```python
import requests
from requests.auth import HTTPBasicAuth

# HTTP API 連線
url = 'http://219.68.168.47:8123'
auth = HTTPBasicAuth('trader', 'SecurePass123!')

# 查詢
response = requests.get(
    f'{url}/?query=SELECT version()',
    auth=auth
)
print(f"版本: {response.text}")
```

## 防火牆設定

如果無法從外部連線，請確認防火牆設定：

### Ubuntu/Debian (使用 ufw)
```bash
# 允許 ClickHouse 端口
sudo ufw allow 8123/tcp
sudo ufw allow 9000/tcp

# 查看狀態
sudo ufw status
```

### CentOS/RHEL (使用 firewalld)
```bash
# 允許 ClickHouse 端口
sudo firewall-cmd --permanent --add-port=8123/tcp
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload

# 查看狀態
sudo firewall-cmd --list-all
```

### 檢查端口監聽
```bash
# 檢查端口是否正確監聽
netstat -tlnp | grep -E "(8123|9000)"

# 應該看到:
# tcp    0    0 0.0.0.0:8123    0.0.0.0:*    LISTEN
# tcp    0    0 0.0.0.0:9000    0.0.0.0:*    LISTEN
```

## 測試外部連線

### 從外部主機測試 (使用 telnet)
```bash
# 測試 HTTP 端口
telnet 219.68.168.47 8123

# 測試 Native 端口
telnet 219.68.168.47 9000
```

### 從外部主機測試 (使用 curl)
```bash
curl -u trader:SecurePass123! 'http://219.68.168.47:8123/?query=SELECT%201'
```

## 安全建議

⚠️ **重要安全提示**:

1. **修改預設密碼**: 請立即修改 `trader` 使用者的密碼
2. **使用防火牆**: 限制允許連線的 IP 地址
3. **使用 SSL/TLS**: 建議在生產環境中啟用 SSL
4. **定期更新**: 保持 ClickHouse 版本更新

### 修改密碼
```sql
-- 進入 ClickHouse CLI
docker exec -it clickhouse-server clickhouse-client --user trader --password SecurePass123!

-- 修改密碼
ALTER USER trader IDENTIFIED BY 'NewSecurePassword123!';
```

## 常見問題

### Q: 無法從外部連線？
A: 檢查以下項目:
1. 防火牆是否開放 8123 和 9000 端口
2. 路由器是否配置了端口轉發（如果在 NAT 後面）
3. 雲端服務商的安全組設定

### Q: 連線被拒絕？
A: 確認 ClickHouse 監聽 0.0.0.0 而不是 127.0.0.1:
```bash
docker exec clickhouse-server cat /etc/clickhouse-server/config.d/listen.xml
```

### Q: 認證失敗？
A: 確認使用者名稱和密碼正確:
- 使用者: trader
- 密碼: SecurePass123!
