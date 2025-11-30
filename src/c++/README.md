# C++ 程式設計完整指南

> C++ 核心概念、高性能程式設計與HFT應用。

## 📊 文檔統計

- **核心文檔**: 20 個
- **主題分類**: 4 個領域
- **適用對象**: C++ 開發者、HFT 工程師

---

## 🗂️ 主題分類

### 📗 核心語法與特性

#### [01. 智能指標與記憶體管理](01_智能指標與記憶體管理.md)
**Smart Pointers、RAII** | 難度: ⭐⭐⭐

核心內容：
- Smart Pointer 基礎
- unique_ptr vs shared_ptr 深度對比
- L&R Value 左值右值
- Move 語意完整指南
- 記憶體管理最佳實踐

**適合**: 中級以上 C++ 開發者

---

### 📘 並發與性能優化

#### [02. 高性能程式設計](02_高性能程式設計.md)
**Benchmark、鎖機制、性能優化** | 難度: ⭐⭐⭐⭐

核心內容：
- Google Benchmark 完整指南
- 性能測試方法
- 乘以 0.01 vs 除以 100 性能對比
- CAS 無鎖編程
- Linux 系統鎖與 C++ 鎖機制
- 高效儲存大規模資料

**適合**: 性能優化工程師、系統開發者

---

### 📙 HFT 高頻交易

#### [03. HFT開發指南](03_HFT開發指南.md)
**高頻交易、低延遲** | 難度: ⭐⭐⭐⭐⭐

核心內容：
- 為什麼選擇 C++ 開發 HFT
- C++ HFT 開發完整指南
- HFT 核心技術
- UC_CAPITAL 實戰案例
- 低延遲優化技巧

**適合**: HFT 開發者、量化交易工程師

---

### 📙 實用技巧與面試

#### [04. 實戰技巧集](04_實戰技巧集.md)
**面試、工程實踐** | 難度: ⭐⭐⭐

核心內容：
- C++ 面試題
- C++ 學習筆記
- gcc finstrument-functions 函數追蹤
- 工程實踐技巧

**適合**: 求職者、C++ 學習者

---

## 🎯 學習路徑建議

### 新手路徑（2-4週）

**第一階段：基礎語法**
1. [智能指標與記憶體管理](01_智能指標與記憶體管理.md)
   - 理解 RAII
   - 學習 Smart Pointer
   - 掌握 Move 語意

**第二階段：實戰練習**
1. 實作簡單專案
2. 使用智能指標管理資源
3. 練習 Move 語意優化

---

### 進階路徑（1-3個月）

**高性能開發**
1. [高性能程式設計](02_高性能程式設計.md)
   - Google Benchmark 性能測試
   - 鎖機制深入理解
   - CAS 無鎖編程

**HFT 專業**
1. [HFT開發指南](03_HFT開發指南.md)
   - HFT 系統架構
   - 低延遲優化
   - 實戰案例分析

---

### 專家路徑（持續學習）

**系統級優化**
1. 硬體級別優化
2. CPU Cache 優化
3. SIMD 向量化

**生產級開發**
1. 大規模系統設計
2. 可維護性與性能平衡
3. 工程最佳實踐

---

## 💡 使用說明

### 學習智能指標
→ [智能指標與記憶體管理](01_智能指標與記憶體管理.md)

### 性能優化
→ [高性能程式設計](02_高性能程式設計.md) - Benchmark/鎖機制

### HFT 開發
→ [HFT開發指南](03_HFT開發指南.md) - 完整 HFT 技術棧

### 面試準備
→ [實戰技巧集](04_實戰技巧集.md) - 面試題/筆記

---

## 🔗 相關資源

### 其他章節
- [HFT 高頻交易](../hft/) - HFT 策略與系統
- [Python 程式設計](../python/) - Python 與 C++ 互操作
- [Rust 程式設計](../rust/) - Rust vs C++ 對比

### 外部資源
- [C++ Reference](https://en.cppreference.com/)
- [ISO C++ Guidelines](https://isocpp.github.io/CppCoreGuidelines/)
- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)

---

## 🚀 快速開始

### 智能指標範例

```cpp
#include <memory>

// unique_ptr - 獨占所有權
std::unique_ptr<int> ptr1 = std::make_unique<int>(42);

// shared_ptr - 共享所有權
std::shared_ptr<int> ptr2 = std::make_shared<int>(100);

// Move 語意
auto ptr3 = std::move(ptr1);  // ptr1 變為 nullptr
```

### Move 語意範例

```cpp
class MyClass {
    std::vector<int> data;
public:
    // Move constructor
    MyClass(MyClass&& other) noexcept
        : data(std::move(other.data)) {}

    // Move assignment
    MyClass& operator=(MyClass&& other) noexcept {
        data = std::move(other.data);
        return *this;
    }
};
```

### Benchmark 範例

```cpp
#include <benchmark/benchmark.h>

static void BM_Example(benchmark::State& state) {
    for (auto _ : state) {
        // 測試代碼
        std::vector<int> v(1000);
    }
}
BENCHMARK(BM_Example);
```

---

**最後更新**: 2025-12-01
**維護狀態**: ✅ 活躍更新
**貢獻**: 歡迎補充與修正
