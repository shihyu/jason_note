# Chapter 03: CPU 架構、管線和性能

## 本章重點

探討現代 CPU 架構如何影響程式性能，包括超純量執行、分支預測、管線化等關鍵概念。

## 核心概念

### 1. 超純量執行 (Superscalar Execution)
- **檔案**: `01_superscalar.C`
- **重點**:
  - CPU 可以同時執行多個指令
  - 指令級平行性 (ILP)
  - 資料相依性對性能的影響
  - 如何編寫能充分利用超純量架構的程式碼

### 2. 分支預測 (Branch Prediction)
- **檔案**: `02_branch.C`, `02_branch_func.C`
- **重點**:
  - 分支預測失敗的性能損失
  - 可預測 vs 不可預測的分支模式
  - 如何減少分支或使分支更可預測
  - 使用無分支程式碼的技巧

## 關鍵技術要點

### 超純量執行範例
```cpp
// 有資料相依性（較慢）
for (int i = 0; i < N; ++i) {
    sum = sum + array[i];  // 每次迭代都依賴前一次的 sum
}

// 循環展開，減少相依性（較快）
for (int i = 0; i < N; i += 4) {
    sum1 += array[i];
    sum2 += array[i+1];
    sum3 += array[i+2];
    sum4 += array[i+3];
}
sum = sum1 + sum2 + sum3 + sum4;
```

### 分支預測優化
```cpp
// 不可預測的分支（較慢）
for (int i = 0; i < N; ++i) {
    if (random_array[i] > threshold) {  // 隨機模式，預測困難
        sum += array[i];
    }
}

// 可預測的分支（較快）
// 先排序，使分支模式可預測
std::sort(random_array, random_array + N);
for (int i = 0; i < N; ++i) {
    if (random_array[i] > threshold) {  // 排序後模式可預測
        sum += array[i];
    }
}
```

### 無分支程式碼
```cpp
// 使用條件運算取代分支
int max = (a > b) ? a : b;  // 編譯器可能產生 cmov 指令

// 使用位元運算避免分支
int abs_diff = (a - b) & ~((a - b) >> 31);  // 絕對值差異
```

## CPU 管線概念

### 1. 指令管線階段
- **取指 (Fetch)**: 從記憶體讀取指令
- **解碼 (Decode)**: 解析指令內容
- **執行 (Execute)**: 執行運算
- **記憶體存取 (Memory)**: 讀寫記憶體
- **寫回 (Write-back)**: 將結果寫回暫存器

### 2. 管線危障 (Pipeline Hazards)
- **結構危障**: 硬體資源衝突
- **資料危障**: 指令間的資料相依性
- **控制危障**: 分支造成的管線清空

## 性能優化技巧

### 1. 增加指令級平行性
- 循環展開 (Loop Unrolling)
- 軟體管線化 (Software Pipelining)
- 減少資料相依鏈

### 2. 優化分支
- 使用 `__builtin_expect` 提示編譯器
- 將常見情況放在 if 分支
- 考慮使用查表取代複雜分支

### 3. 利用 CPU 特性
- 善用 SIMD 指令
- 對齊資料結構
- 考慮快取行大小

## 測量工具

```bash
# 使用 perf 測量分支預測
perf stat -e branches,branch-misses ./program

# 查看 CPU 管線使用情況
perf stat -e instructions,cycles,IPC ./program
```

## 實驗建議

1. 比較有序和隨機資料的分支預測效果
2. 測量循環展開對性能的影響
3. 分析不同分支密度的性能影響
4. 使用 perf 記錄分支預測失敗率

## 重要觀察

- 現代 CPU 的分支預測準確率通常超過 95%
- 即使 1% 的預測失敗也可能造成顯著性能損失
- 簡單可預測的程式碼往往比複雜"優化"更快
- 了解 CPU 架構對編寫高性能程式碼至關重要