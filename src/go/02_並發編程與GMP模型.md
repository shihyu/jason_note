# 並發編程與 GMP 模型

> Goroutine、Channel、GMP 調度模型深度解析。

## 🚀 Goroutine 與調度

### GMP 模型
- [Goroutine 與 GMP 原理全面分析](golang-goroutine.md)
- [Go 語言 CPU、GMP 模型與多程式執行完整指南](go-cpu-gmp-guide.md)

### 協程對比
- [Goroutine vs C++/Rust 協程完整對比指南](goroutine_complete_guide.md)
- [行程、執行緒、協程，傻傻分得清楚！](Coroutine.md)

## 📡 並發機制

### Channel 與同步
- [Go 併發](goroutine-and-channel.md) - Goroutine 與 Channel
- [Go 並行機制完整指南](go_concurrency_guide.md)

### 鎖機制
- [sync.Mutex 和 sync.RWMutex](mutex-rwmutex.md)

## 💡 GMP 模型詳解

### 核心組件
1. **G (Goroutine)**
   - 輕量級線程
   - 2KB 初始棧
   - 動態擴縮容

2. **M (Machine)**
   - OS 線程
   - 執行 Goroutine
   - 綁定到 P

3. **P (Processor)**
   - 邏輯處理器
   - 本地運行隊列
   - GOMAXPROCS 控制數量

### 調度策略
1. **Work Stealing**
   - 從其他 P 偷取任務
   - 負載均衡

2. **Hand Off**
   - M 阻塞時交出 P
   - 保持並發度

3. **搶占式調度**
   - 基於信號的搶占
   - 防止長時間佔用

## 🔒 並發同步

### Channel 模式
1. **無緩衝 Channel**
   - 同步通訊
   - 阻塞發送/接收

2. **緩衝 Channel**
   - 異步通訊
   - 容量控制

3. **Select**
   - 多路複用
   - 超時控制

### 鎖的使用
1. **Mutex**
   - 互斥鎖
   - 保護共享資源

2. **RWMutex**
   - 讀寫鎖
   - 讀多寫少場景

**最後更新**: 2025-12-01
