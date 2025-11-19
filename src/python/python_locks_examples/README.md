# Python 鎖機制範例集合 🐍🔒

這個專案包含了 Python 中各種鎖機制的完整範例，從基本的 `threading.Lock` 到進階的讀寫鎖，以及最佳實踐指南。

## 📁 專案結構

```
python_locks_examples/
├── basic_locks/              # 基本鎖機制範例
│   ├── 01_threading_lock.py     # Lock 基本使用
│   ├── 02_decorator_lock.py     # 裝飾器模式
│   ├── 03_recursive_lock.py     # RLock 遞迴鎖
│   ├── 04_semaphore.py          # Semaphore 信號量
│   ├── 05_condition.py          # Condition 條件變數
│   ├── 06_event.py              # Event 事件
│   └── 07_barrier.py            # Barrier 屏障
├── advanced_locks/           # 進階鎖機制範例
│   ├── 01_read_write_lock.py    # 讀寫鎖實現
│   ├── 02_context_manager.py    # 上下文管理器
│   └── 03_thread_local.py       # 執行緒本地儲存
├── best_practices/           # 最佳實踐範例
│   ├── 01_performance_comparison.py  # 效能比較
│   └── 02_lock_selection_guide.py    # 選擇指南
├── tests/                    # 測試工具
│   └── test_all_examples.py     # 測試執行器
└── README.md                 # 本檔案
```

## 🚀 快速開始

### 執行所有範例

```bash
# 進入專案目錄
cd python_locks_examples

# 執行所有範例
python tests/test_all_examples.py --all
```

### 執行特定分類

```bash
# 只執行基本鎖範例
python tests/test_all_examples.py --basic

# 只執行進階鎖範例
python tests/test_all_examples.py --advanced

# 只執行最佳實踐範例
python tests/test_all_examples.py --best-practices
```

### 執行單個範例

```bash
# 執行 Lock 基本範例
python basic_locks/01_threading_lock.py

# 執行信號量範例
python basic_locks/04_semaphore.py
```

## 📚 範例說明

### 基本鎖機制 (basic_locks/)

| 檔案 | 說明 | 主要概念 |
|------|------|----------|
| `01_threading_lock.py` | 基本互斥鎖使用 | Lock, with 語句, 線程安全 |
| `02_decorator_lock.py` | 裝飾器模式的線程安全 | 裝飾器, 函數包裝 |
| `03_recursive_lock.py` | 遞迴鎖的使用場景 | RLock, 遞迴函數, 死鎖避免 |
| `04_semaphore.py` | 信號量控制資源存取 | Semaphore, 連線池, 資源限制 |
| `05_condition.py` | 條件變數協調執行緒 | Condition, 生產者-消費者, wait/notify |
| `06_event.py` | 事件機制進行通訊 | Event, 一對多通知, 狀態信號 |
| `07_barrier.py` | 屏障同步多個執行緒 | Barrier, 階段同步, 集合點 |

### 進階鎖機制 (advanced_locks/)

| 檔案 | 說明 | 主要概念 |
|------|------|----------|
| `01_read_write_lock.py` | 讀寫鎖的實現與使用 | 讀寫分離, 並行讀取, 獨佔寫入 |
| `02_context_manager.py` | 上下文管理器與鎖 | with 語句, 自動管理, 異常安全 |
| `03_thread_local.py` | 執行緒本地儲存 | threading.local, 執行緒隔離 |

### 最佳實踐 (best_practices/)

| 檔案 | 說明 | 主要概念 |
|------|------|----------|
| `01_performance_comparison.py` | 各種鎖的效能比較 | 效能測試, 最佳實踐, 避免死鎖 |
| `02_lock_selection_guide.py` | 鎖選擇指南 | 場景分析, 決策樹, 使用建議 |

## 🎯 學習路徑

### 初學者路徑
1. `01_threading_lock.py` - 瞭解基本概念
2. `02_decorator_lock.py` - 學習實用模式
3. `04_semaphore.py` - 理解資源控制
4. `06_event.py` - 掌握事件通訊

### 進階學習路徑
1. `03_recursive_lock.py` - 處理複雜場景
2. `05_condition.py` - 學習執行緒協調
3. `07_barrier.py` - 掌握同步技巧
4. `01_read_write_lock.py` - 實現高效同步

### 實踐應用路徑
1. `03_thread_local.py` - 避免鎖競爭
2. `02_context_manager.py` - 安全管理資源
3. `01_performance_comparison.py` - 效能優化
4. `02_lock_selection_guide.py` - 正確選擇

## 🧪 測試與驗證

### 驗證檔案結構
```bash
python tests/test_all_examples.py --validate
```

### 設定測試超時
```bash
# 設定 60 秒超時
python tests/test_all_examples.py --all --timeout 60
```

### 測試輸出範例
```
🚀 開始執行所有 Python 鎖範例測試
============================================================
📋 找到 12 個測試檔案

🧪 測試: 01_threading_lock.py
   ✅ 成功 (2.34s)

🧪 測試: 02_decorator_lock.py
   ✅ 成功 (1.87s)

...

📊 測試報告
============================================================
總測試數: 12
成功數: 12
失敗數: 0
成功率: 100.0%
總執行時間: 25.43s
```

## 💡 重要概念

### 鎖選擇決策樹
```
需要同步嗎？
├─ 否 → 無需鎖
└─ 是
    ├─ 執行緒隔離？ → threading.local
    ├─ 遞迴呼叫？ → RLock
    ├─ 限制資源數量？ → Semaphore
    ├─ 多讀少寫？ → ReadWriteLock
    ├─ 等待條件？ → Condition
    ├─ 事件通知？ → Event
    ├─ 階段同步？ → Barrier
    └─ 基本互斥 → Lock
```

### 效能排序 (從快到慢)
1. 🥇 `threading.local` - 最快，無鎖競爭
2. 🥈 `threading.Lock` - 基本互斥鎖
3. 🥉 `threading.RLock` - 遞迴鎖
4. 4️⃣ `threading.Semaphore` - 資源控制
5. 5️⃣ `threading.Condition` - 條件等待

### 最佳實踐
- ✅ 優先使用 `with` 語句管理鎖
- ✅ 最小化鎖的持有時間
- ✅ 統一鎖定順序避免死鎖
- ✅ 選擇合適的鎖粒度
- ✅ 考慮使用 `threading.local` 避免鎖競爭
- ✅ 在實際場景中測試併發性

## 🔧 環境需求

- Python 3.6+
- 標準庫 threading 模組
- 無需額外安裝套件

## 📖 相關資源

- [Python threading 官方文檔](https://docs.python.org/3/library/threading.html)
- [並行程式設計指南](https://realpython.com/python-threading/)
- [多執行緒最佳實踐](https://docs.python.org/3/library/concurrent.futures.html)

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request 來改進這些範例！

## 📄 授權

本專案採用 MIT 授權條款。

---

🎉 開始探索 Python 鎖機制的奇妙世界吧！
