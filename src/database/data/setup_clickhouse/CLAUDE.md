# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述
這是一個 ClickHouse 資料庫的 Docker 部署環境，專門用於處理金融市場交易數據（tick data）。支援快速部署、資料備份還原、效能監控等功能。

## 常用開發指令

### 服務管理
```bash
# 快速啟動（包含安裝、啟動、建立資料庫、測試）
make quick-start

# 服務控制
make up          # 啟動 ClickHouse 服務
make down        # 停止服務
make restart     # 重啟服務
make status      # 查看服務狀態
```

### 開發與測試
```bash
# 進入 ClickHouse CLI
make shell

# 建立基本資料庫結構
make db

# 建立優化的表結構（包含物化視圖、索引等）
make db-optimized

# 執行測試（導入 test_data.csv 並查詢統計）
make test

# 查看服務日誌
make logs
```

### 維護與監控
```bash
# 執行備份
make backup

# 還原備份（交互式選擇）
make restore

# 監控系統狀態（資源使用、查詢效能、健康檢查）
make monitor

# 完全重置環境
make reset
```

## 系統架構

### 核心組件
- **Docker 容器**: ClickHouse 24.8-alpine，配置 2 CPU / 4GB 記憶體限制
- **資料儲存**: `./data/` 掛載到容器內部，支援資料持久化
- **備份機制**: 自動備份到 `./backup/` 目錄，包含時間戳命名

### 資料庫結構
- **主資料庫**: `market_data`
- **基本表**: `market_ticks` - 儲存原始 tick 數據
- **優化表**: `tick_data_optimized` - 包含壓縮編碼、分區、TTL
- **物化視圖**:
  - `tick_1min_mv` - 1分鐘K線預聚合
  - `tick_5min_mv` - 5分鐘K線預聚合
  - `daily_stats_mv` - 每日統計數據

### 連線資訊
- 使用者: `trader`
- 密碼: `SecurePass123!`
- HTTP 端口: 8123
- Native 端口: 9000

## 效能優化策略

1. **資料壓縮**: 使用 DoubleDelta、T64 等編碼降低儲存空間
2. **分區設計**: 按月分區（`toYYYYMM`），便於資料管理與清理
3. **索引優化**: bloom_filter 索引加速 symbol 查詢，minmax 索引優化價格範圍查詢
4. **物化視圖**: 預聚合常用統計，避免重複計算
5. **TTL 設定**: 90天自動清理舊數據，控制儲存成本

## 監控重點

執行 `make monitor` 或 `scripts/monitor.sh` 會顯示：
- Docker 容器資源使用（CPU、記憶體）
- 各資料庫大小與資料筆數
- 最近查詢效能（記憶體使用、執行時間、讀寫行數）
- 系統健康狀態檢查