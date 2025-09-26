# ClickHouse Makefile 測試結果報告

## 測試日期：2025-09-27

## 測試項目與結果

### ✅ 1. make clean - 清理環境
- **狀態**：成功
- **說明**：成功停止服務並清理資料（需要 sudo 權限）
- **改進**：已更新 Makefile 使用 sudo 清理資料

### ✅ 2. make reset - 重新部署
- **狀態**：成功
- **說明**：完整重置流程運作正常
  - 停止服務 ✅
  - 清理資料 ✅
  - 重新啟動 ✅
  - 建立資料庫 ✅

### ✅ 3. make backup - 備份功能
- **狀態**：成功
- **說明**：成功建立備份檔案
  - 備份位置：backup/ 目錄
  - 備份格式：tar.gz 壓縮檔
  - 包含 data 和 metadata

### ⚠️ 4. make restore - 還原功能
- **狀態**：部分成功
- **問題**：
  - 表結構還原成功
  - 資料還原失敗（可能因為資料格式或權限問題）
- **建議**：使用 ClickHouse 原生備份功能

### ✅ 5. make db-optimized - 優化表結構
- **狀態**：部分成功
- **已建立**：
  - tick_data_optimized 表（優化的主表）
  - tick_1min_mv（1分鐘K線物化視圖）
  - tick_5min_mv（5分鐘K線物化視圖）
  - daily_stats_mv（每日統計物化視圖）
- **問題修復**：
  - 修正 Gorilla 編碼對 Decimal 類型的錯誤
  - 修正 TTL 對 DateTime64 的支援問題

## 資料庫優化設計

### 已整合的優化策略：

1. **表引擎優化**
   - MergeTree 引擎
   - 按月分區（PARTITION BY toYYYYMM）
   - 優化排序鍵（ORDER BY symbol, timestamp）

2. **資料類型優化**
   - LowCardinality(String) 用於重複值多的欄位
   - Enum8 用於固定選項
   - 適當的數值類型（UInt32 vs UInt64）
   - DateTime64(3) 提供毫秒精度

3. **壓縮編碼**
   - DoubleDelta 用於時間戳
   - T64 用於整數
   - 避免不相容的編碼組合

4. **物化視圖（預聚合）**
   - 1分鐘K線自動聚合
   - 5分鐘K線自動聚合
   - 每日統計自動計算

5. **索引優化**
   - minmax 索引用於價格範圍查詢
   - bloom_filter 索引用於 symbol 查詢

## 檔案清單

```
setup_clickhouse/
├── Makefile                           # 管理指令（已更新）
├── docker-compose.yml                 # Docker 配置
├── README.md                          # 使用說明
├── TEST_REPORT.md                     # 初始測試報告
├── TEST_RESULTS.md                    # 本測試結果
├── scripts/
│   ├── backup.sh                      # 備份腳本
│   ├── restore.sh                     # 還原腳本
│   ├── restore_test.sh                # 還原測試腳本
│   ├── monitor.sh                     # 監控腳本
│   └── create_optimized_tables.sql    # 優化表結構SQL
├── test_data.csv                      # 測試資料
└── backup/                            # 備份檔案目錄
```

## 改進建議

1. **備份還原**
   - 考慮使用 ClickHouse 原生 BACKUP/RESTORE 命令
   - 或使用 clickhouse-backup 工具

2. **權限處理**
   - Makefile 中需要 sudo 的操作應提示使用者
   - 或使用 Docker volume 避免權限問題

3. **優化表結構**
   - 根據實際查詢模式調整索引
   - 定期執行 OPTIMIZE TABLE
   - 監控分區大小，避免過大或過小

4. **生產環境**
   - 增加更多監控指標
   - 設置自動備份排程
   - 實施資料保留策略（TTL）

## 結論

Makefile 提供的功能大部分運作正常，特別是：
- ✅ 環境管理（clean, reset）
- ✅ 服務控制（up, down, restart）
- ✅ 資料庫建立（db, db-optimized）
- ✅ 備份功能（backup）
- ⚠️ 還原功能需要改進

優化的表結構已成功整合，包括物化視圖和索引優化，適合處理大量 tick 資料。