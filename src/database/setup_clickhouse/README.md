# ClickHouse Docker 部署

快速部署和管理 ClickHouse 資料庫的 Docker 環境。

## 快速開始

```bash
# 一鍵安裝並啟動
make quick-start
```

## 常用指令

| 指令 | 說明 |
|------|------|
| `make up` | 啟動 ClickHouse 服務 |
| `make down` | 停止服務 |
| `make status` | 查看服務狀態 |
| `make shell` | 進入 ClickHouse CLI |
| `make logs` | 查看服務日誌 |
| `make test` | 執行測試查詢 |
| `make backup` | 備份資料 |
| `make restore` | 還原備份 |
| `make monitor` | 執行監控 |
| `make clean` | 清理資料（保留備份） |
| `make reset` | 完全重置環境 |

## 連接資訊

- **使用者**: trader
- **密碼**: SecurePass123!
- **資料庫**: market_data
- **HTTP 端口**: 8123
- **Native 端口**: 9000

## 目錄結構

```
setup_clickhouse/
├── docker-compose.yml   # Docker 配置
├── Makefile            # 管理指令
├── config/             # 配置檔案
├── data/               # 資料儲存
├── logs/               # 日誌檔案
├── backup/             # 備份檔案
├── scripts/            # 管理腳本
└── test_data.csv       # 測試資料
```

## 進階操作

### 手動備份
```bash
make backup
```

### 還原特定備份
```bash
make restore
# 然後輸入備份檔名
```

### 完全重置（清理並重新部署）
```bash
make reset
```

### 監控系統狀態
```bash
make monitor
```

## 故障排除

如果服務無法啟動：
1. 檢查 Docker 是否正在運行
2. 確認端口 8123, 9000, 9009 未被佔用
3. 查看日誌：`make logs`
4. 嘗試重置：`make reset`

## 版本資訊

- ClickHouse: 24.8-alpine
- Docker Compose: 2.30.3+