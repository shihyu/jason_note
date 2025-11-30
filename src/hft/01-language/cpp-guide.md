# 高頻交易 C++ 開發技術指南

## 目錄
- [核心編程原則](#核心編程原則)
- [性能優化策略](#性能優化策略)
- [零拷貝通信技術](#零拷貝通信技術)
- [編譯器自動 SIMD 優化](#編譯器自動-simd-優化)
- [關鍵路徑優化](#關鍵路徑優化)
- [實戰建議](#實戰建議)

## 核心編程原則

### 1. 強類型系統的重要性

永遠不要直接使用原始類型（如 `int`），而是要創建自定義類型：

```cpp
// ❌ 不好的做法
int price = 100;
int quantity = 50;

// ✅ 好的做法
class Price { /* ... */ };
class Quantity { /* ... */ };
```

**優點：**
- **類型安全**：編譯器能在編譯時期捕捉錯誤
- **自我文檔化**：程式碼更容易理解
- **防止誤用**：不會不小心把價格當成數量使用

### 2. 串流（Streams）的正確使用

串流並不慢，關鍵是要知道如何正確使用：
- 提供類型安全的輸出
- 支援高效的緩衝
- 避免格式化字串的開銷
- 使用 `std::format` 來實作串流物件

### 3. 真正的 OOP 理解

- **沒有 getter/setter**：物件應該封裝行為，而不是暴露資料
- **小而精的物件**：每個物件只負責一件事
- **組合優於繼承**：透過組合小物件來構建複雜功能
- **訊息傳遞**：物件之間通過訊息（在 C++ 中用串流實現）進行通信

> 💡 建議研究 Smalltalk（Squeak 實作）來理解純粹的 OOP

## 性能優化策略

### 1. 資料導向設計（Data-Oriented Design）

- 優先考慮資料的佈局和存取模式
- 批次處理比逐個處理更有效率
- 記憶體局部性（cache locality）至關重要
- 現代的資料導向設計 = 80年代的批次處理

### 2. 並發、並行與執行緒

```
並發 ≠ 並行 ≠ 執行緒
```

**關鍵觀點：**
- **並發**：多個任務在邏輯上同時進行
- **並行**：多個任務在物理上同時執行（使用執行緒）
- **IO 原則**：永遠不要在次要執行緒上做 IO
- **擴展性**：執行緒無法隨 IO 擴展（參考 Apache fork v2）

### 3. 程序（Process）架構

```
決策邏輯分離 → 多個專門的程序
              ↓
        零拷貝通信（頁面傳遞）
              ↓
         避免共享可寫記憶體
```

## 零拷貝通信技術

### 核心概念

1. **共享記憶體映射**
```cpp
// 創建共享記憶體
int shm_fd = shm_open(name, O_CREAT | O_RDWR, 0666);
ftruncate(shm_fd, size);

// 映射到進程地址空間 - 零拷貝的關鍵
void* ptr = mmap(nullptr, size, 
                 PROT_READ | PROT_WRITE, 
                 MAP_SHARED, shm_fd, 0);
```

2. **頁面傳遞（vmsplice）**
```cpp
struct iovec iov = {
    .iov_base = buffer,
    .iov_len = size
};

// 將頁面所有權轉移給內核，完全零拷貝
vmsplice(pipe_fd, &iov, 1, SPLICE_F_GIFT);
```

3. **直接傳輸（splice/sendfile）**
```cpp
// 在內核空間直接移動資料
splice(fd_in, nullptr, fd_out, nullptr, size, SPLICE_F_MOVE);

// 零拷貝發送文件
sendfile(socket_fd, file_fd, &offset, count);
```

### 實戰技巧

- 使用**環形緩衝區**避免資料移動
- 使用**大頁面**（2MB）提高 TLB 效率
- 使用 `mlock` 鎖定記憶體防止交換
- 對齊到快取行（64 bytes）避免 false sharing

## 編譯器自動 SIMD 優化

### 1. 編寫編譯器友好的程式碼

```cpp
// ✅ 容易向量化的程式碼
void simple_loop(float* __restrict a, 
                 float* __restrict b, 
                 float* __restrict c, 
                 int n) {
    #pragma omp simd
    for (int i = 0; i < n; i++) {
        c[i] = a[i] * b[i];  // 簡單操作
    }
}
```

### 2. 使用 Structure of Arrays (SoA)

```cpp
// ❌ Array of Structures (AoS) - 不利於 SIMD
struct TickDataAoS {
    float price, volume, bid, ask;
};

// ✅ Structure of Arrays (SoA) - 有利於 SIMD  
struct TickDataSoA {
    float* prices;
    float* volumes;
    float* bids;
    float* asks;
};
```

### 3. 編譯器提示

```cpp
// 告訴編譯器指針不重疊
float* __restrict a;

// 告訴編譯器資料對齊
__builtin_assume_aligned(ptr, 32);

// 提示編譯器進行向量化
#pragma GCC ivdep
#pragma omp simd
#pragma vector aligned
```

### 4. 編譯選項

```bash
# GCC/G++
g++ -O3 -march=native -mavx2 -mfma \
    -ffast-math -funroll-loops -ftree-vectorize

# Clang
clang++ -O3 -march=native -mavx2 -ffast-math \
        -Rpass=loop-vectorize

# Intel ICC
icc -O3 -xHost -qopt-report=5
```

## 關鍵路徑優化

### 1. 零日誌記錄策略

在關鍵交易路徑上完全不記錄日誌：

```
關鍵路徑 → 無日誌
    ↓
被動網路監聽（旁路）
    ↓
封包擷取記錄
    ↓
事後重播除錯
```

### 2. 硬體加速

- **專用網路卡**：600ns 延遲（2萬美元）
- **FPGA 加速**：關鍵運算硬體化
- **精簡功能**：網路卡甚至不處理 ICMP

> 💡 硬體投資往往比一週的開發時間更划算

## 實戰建議

### 開發原則

1. **遵循標準**
   - MISRA 準則（安全關鍵系統）
   - 關鍵系統準則
   - 核心準則（Core Guidelines）

2. **語言選擇的迷思**
   - 語言本身不是關鍵（Java、C#、C++ 都可以很快）
   - 重要的是對語言的深入理解
   - 正確的架構設計比語言選擇更重要

3. **優化策略**
   - 識別關鍵路徑並極致優化
   - 其他部分保持簡單和可維護
   - 測量效能，避免過早優化

### 關鍵技術總結

| 技術領域 | 關鍵技術 | 效果 |
|---------|---------|------|
| **記憶體** | 零拷貝、共享記憶體、大頁面 | 減少延遲 |
| **CPU** | 編譯器自動 SIMD、SoA 佈局 | 提高吞吐量 |
| **IO** | 非同步 IO、批次處理 | 提高擴展性 |
| **架構** | 程序分離、專用硬體 | 系統性優化 |

### 反模式警告 ⚠️

- 不要手寫複雜的 SIMD 程式碼
- 不要在執行緒上做 IO
- 不要使用原始迴圈
- 不要忽視資料佈局
- 不要在關鍵路徑上記錄日誌

## 總結

在 HFT 領域成功的關鍵不是使用最新的技術或最難的程式碼，而是：

1. 🎯 深入理解你的工具和環境
2. ⚡ 針對關鍵路徑進行極致優化
3. 🔧 其他部分保持簡單和可維護
4. 🚀 善用硬體加速
5. 📊 避免過早優化和過度工程

> "好的 C++ 程式碼會用到很多使用者自訂型別。要花很多耐心和痛苦，才能讓你停止鬼混，開始寫好的程式碼。"

這種方法論不僅適用於 HFT，也適用於任何需要極致性能的系統開發。