# Go 並行程式設計範例集

這個目錄包含了完整的 Go 並行程式設計範例，從基礎概念到高級模式，所有程式都經過測試，可以直接運行學習。

## 📋 範例清單

| 編號 | 檔案名稱 | 主題 | 難度 | 主要概念 |
|------|----------|------|------|----------|
| 01 | `01_goroutine_basics.go` | Goroutine 基礎 | 🟢 初級 | Goroutine, WaitGroup |
| 02 | `02_channel_communication.go` | Channel 通訊 | 🟢 初級 | 無緩衝/緩衝通道 |
| 03 | `03_select_multiplexing.go` | Select 多路復用 | 🟡 中級 | Select, 超時控制 |
| 04 | `04_mutex_synchronization.go` | Mutex 同步 | 🟡 中級 | 互斥鎖, 共享狀態 |
| 05 | `05_rwmutex_optimization.go` | RWMutex 優化 | 🟡 中級 | 讀寫鎖, 性能優化 |
| 06 | `06_waitgroup_synchronization.go` | 同步控制 | 🟡 中級 | WaitGroup, Once |
| 07 | `07_atomic_operations.go` | 原子操作 | 🔴 高級 | 無鎖編程, 原子類型 |
| 08 | `08_context_control.go` | Context 控制 | 🔴 高級 | 超時, 取消, 值傳遞 |
| 09 | `09_producer_consumer_pattern.go` | 生產者-消費者 | 🔴 高級 | 並行模式, 工作隊列 |
| 10 | `10_pipeline_pattern.go` | Pipeline 管道 | 🔴 高級 | 數據流, 扇出-扇入 |
| 11 | `11_worker_pool_advanced.go` | 高級工作池 | 🔴 高級 | 動態調整, 負載均衡 |

## 🚀 快速開始

### 運行單個範例
```bash
# 運行 Goroutine 基礎範例
go run 01_goroutine_basics.go

# 運行 Channel 通訊範例
go run 02_channel_communication.go
```

### 使用 Makefile（從 concurrency_examples/ 目錄）
```bash
# 查看所有可用範例
make list

# 運行特定範例
make run-01    # Goroutine 基礎
make run-05    # RWMutex 範例
make run-11    # 高級 Worker Pool

# 運行所有測試
make test

# 依序演示所有範例
make demo
```

## 📚 學習路徑

### 🌱 初學者路徑（第一週）
1. **01_goroutine_basics.go** - 理解 Goroutine 的基本概念
2. **02_channel_communication.go** - 掌握 Channel 通訊機制
3. **04_mutex_synchronization.go** - 學習基本的同步控制

### 🚀 中級路徑（第二週）
4. **03_select_multiplexing.go** - 掌握 Select 多路復用
5. **05_rwmutex_optimization.go** - 理解讀寫鎖優化
6. **06_waitgroup_synchronization.go** - 深入同步控制

### 🎯 高級路徑（第三週以上）
7. **07_atomic_operations.go** - 無鎖並行編程
8. **08_context_control.go** - 上下文管理和控制
9. **09_producer_consumer_pattern.go** - 經典並行模式
10. **10_pipeline_pattern.go** - 數據處理管道
11. **11_worker_pool_advanced.go** - 企業級工作池

## 🔍 範例詳細說明

### 基礎範例

#### 01 - Goroutine 基礎操作
- **學習目標**: 理解 Goroutine 的創建和管理
- **關鍵概念**: `go` 關鍵字, `sync.WaitGroup`
- **實際應用**: 並行任務執行
- **運行時間**: ~2秒

#### 02 - Channel 通訊機制
- **學習目標**: 掌握 Go 的 CSP 模型核心
- **關鍵概念**: 無緩衝通道, 緩衝通道, `close()`
- **實際應用**: Goroutine 間安全通訊
- **運行時間**: ~5秒

#### 03 - Select 多路復用
- **學習目標**: 處理多個通道操作
- **關鍵概念**: `select`, `time.After()`, 非阻塞操作
- **實際應用**: 超時控制, 多源數據處理
- **運行時間**: ~8秒

### 同步控制範例

#### 04 - Mutex 互斥同步
- **學習目標**: 保護共享資源
- **關鍵概念**: `sync.Mutex`, 臨界區, 競爭條件
- **實際應用**: 共享狀態管理
- **運行時間**: ~3秒

#### 05 - RWMutex 讀寫鎖優化
- **學習目標**: 優化多讀少寫場景
- **關鍵概念**: `sync.RWMutex`, 並發讀取
- **實際應用**: 配置緩存, 數據緩存
- **運行時間**: ~4秒

#### 06 - WaitGroup 同步控制
- **學習目標**: 任務協調和單次執行
- **關鍵概念**: `sync.WaitGroup`, `sync.Once`
- **實際應用**: 批量任務, 單例模式
- **運行時間**: ~3秒

### 高級範例

#### 07 - 原子操作
- **學習目標**: 無鎖並行編程
- **關鍵概念**: `sync/atomic`, CAS 操作
- **實際應用**: 高性能計數器, 統計系統
- **運行時間**: ~5秒

#### 08 - Context 上下文控制
- **學習目標**: 請求生命週期管理
- **關鍵概念**: `context.Context`, 超時, 取消, 值傳遞
- **實際應用**: HTTP 服務, 微服務調用鏈
- **運行時間**: ~15秒

#### 09 - 生產者-消費者模式
- **學習目標**: 經典並行設計模式
- **關鍵概念**: 工作隊列, 負載均衡, 結果收集
- **實際應用**: 任務處理系統, 消息隊列
- **運行時間**: ~8秒

#### 10 - Pipeline 管道模式
- **學習目標**: 數據流處理
- **關鍵概念**: 管道組合, 扇出-扇入, 數據轉換
- **實際應用**: 數據處理流水線, ETL 系統
- **運行時間**: ~6秒

#### 11 - 高級工作池
- **學習目標**: 企業級並行系統設計
- **關鍵概念**: 動態縮放, 優先級隊列, 性能監控
- **實際應用**: 高並發服務, 任務調度系統
- **運行時間**: ~15秒

## 🛠️ 開發工具

### 編譯和運行
```bash
# 編譯特定範例
go build -o goroutine_demo 01_goroutine_basics.go

# 直接運行
go run 01_goroutine_basics.go

# 競爭條件檢測
go run -race 07_atomic_operations.go
```

### 性能分析
```bash
# CPU 性能分析
go run -cpuprofile=cpu.prof 11_worker_pool_advanced.go

# 記憶體分析
go run -memprofile=mem.prof 09_producer_consumer_pattern.go

# 查看 Goroutine 數量
GODEBUG=schedtrace=1000 go run 01_goroutine_basics.go
```

### 調試工具
```bash
# 查看 Goroutine 堆疊
kill -SIGQUIT <進程ID>

# 使用 delve 調試器
dlv debug 08_context_control.go
```

## 🎯 最佳實踐

### 代碼風格
- ✅ 使用有意義的變數名稱
- ✅ 適當的錯誤處理
- ✅ 清晰的註釋說明
- ✅ 遵循 Go 官方代碼規範

### 並行安全
- ✅ 正確使用同步原語
- ✅ 避免競爭條件
- ✅ 防止 Goroutine 洩漏
- ✅ 適當的資源清理

### 性能考慮
- ✅ 控制 Goroutine 數量
- ✅ 適當的 Channel 緩衝大小
- ✅ 使用對象池減少 GC 壓力
- ✅ 監控系統資源使用

## 🔧 故障排除

### 常見問題

#### 死鎖 (Deadlock)
```bash
# 症狀: fatal error: all goroutines are asleep - deadlock!
# 解決: 檢查 Channel 的發送/接收平衡，確保 Goroutine 有退出條件
```

#### 競爭條件 (Race Condition)
```bash
# 檢測: go run -race program.go
# 解決: 使用適當的同步原語保護共享資源
```

#### Goroutine 洩漏
```bash
# 檢測: 監控 runtime.NumGoroutine()
# 解決: 使用 Context 控制 Goroutine 生命週期
```

#### 記憶體洩漏
```bash
# 檢測: go tool pprof mem.prof
# 解決: 及時關閉 Channel，避免循環引用
```

## 📊 性能基準

### 測試環境
- **CPU**: 28 核心
- **記憶體**: 62GB
- **Go 版本**: 1.22.2
- **作業系統**: Linux

### 基準結果（參考）
| 範例 | 執行時間 | 記憶體使用 | Goroutine 峰值 |
|------|----------|------------|----------------|
| 01 | 2s | 2MB | 6 |
| 02 | 5s | 3MB | 3 |
| 03 | 8s | 2MB | 4 |
| 04 | 3s | 2MB | 6 |
| 05 | 4s | 3MB | 12 |
| 06 | 3s | 2MB | 7 |
| 07 | 5s | 4MB | 6 |
| 08 | 15s | 5MB | 8 |
| 09 | 8s | 6MB | 5 |
| 10 | 6s | 4MB | 15 |
| 11 | 15s | 8MB | 12 |

## 🤝 貢獻指南

### 提交新範例
1. 遵循命名規範: `NN_description.go`
2. 包含完整的註釋說明
3. 確保程式可以正常編譯和運行
4. 運行時間控制在合理範圍內

### 報告問題
- 描述問題和重現步驟
- 提供系統環境信息
- 附上相關的錯誤信息

## 📖 學習資源

### 官方文檔
- [Go Tour - Concurrency](https://tour.golang.org/concurrency/1)
- [Effective Go - Concurrency](https://golang.org/doc/effective_go.html#concurrency)
- [Go Memory Model](https://golang.org/ref/mem)

### 推薦閱讀
- "Go Concurrency Patterns" - Rob Pike
- "Advanced Go Concurrency Patterns" - Sameer Ajmani
- "Concurrency in Go" - Katherine Cox-Buday

### 相關工具
- [Go Race Detector](https://golang.org/doc/articles/race_detector.html)
- [pprof 性能分析](https://golang.org/pkg/net/http/pprof/)
- [Delve 調試器](https://github.com/go-delve/delve)

---

**🎉 開始你的 Go 並行編程學習之旅吧！**

記住 Go 的核心理念：*"Don't communicate by sharing memory; share memory by communicating."*