# Runtime 與記憶體管理

> Go Runtime、GC 垃圾回收與記憶體管理機制。

## 🎯 Go Runtime

### Runtime 機制
- [Go Runtime 完整指南](Go_Runtime_Guide.md)

## 🗑️ 垃圾回收

### GC 機制
- [GC 全面解析](golang-memory-management.md)

核心內容：
- 三色標記法
- 寫屏障
- 併發標記清除
- GC 調優

## 🧠 記憶體管理

### Pointer 管理
- [Returning Pointer from a Function in Go](returning-pointer-from-a-function-in-go.md)

## 💡 GC 原理詳解

### 三色標記法
1. **白色**
   - 未訪問的對象
   - 可能被回收

2. **灰色**
   - 已訪問，但子對象未掃描
   - 工作隊列

3. **黑色**
   - 已訪問且子對象已掃描
   - 不會被回收

### GC 階段
1. **Mark Setup (STW)**
   - 開啟寫屏障
   - 準備標記

2. **Marking (併發)**
   - 併發標記
   - 三色標記

3. **Mark Termination (STW)**
   - 完成標記
   - 關閉寫屏障

4. **Sweep (併發)**
   - 併發清除
   - 回收記憶體

## 🔧 記憶體分配

### 內存分配器
1. **mspan**
   - 記憶體塊
   - 8KB 頁

2. **mcache**
   - 線程本地緩存
   - 無鎖分配

3. **mcentral**
   - 中心緩存
   - 鎖保護

4. **mheap**
   - 堆管理
   - 大對象分配

### 優化建議
1. **減少 GC 壓力**
   - 對象池復用
   - 減少小對象分配
   - 預分配 slice

2. **調整 GOGC**
   - 默認 100
   - 增大減少 GC 頻率
   - 減小降低記憶體使用

**最後更新**: 2025-12-01
