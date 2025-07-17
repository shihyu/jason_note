# C++ 智能指標指南：unique_ptr vs shared_ptr

## 概述

智能指標是 C++11 引入的重要特性，用於自動管理記憶體生命週期，避免記憶體洩漏和懸空指標問題。

## 主要差異對比

| 特性 | `std::unique_ptr` | `std::shared_ptr` |
|------|------------------|------------------|
| **所有權** | 獨佔所有權 | 共享所有權 |
| **複製** | 不可複製，只能移動 | 可複製 |
| **效能** | 幾乎無開銷 | 有參考計數開銷 |
| **記憶體使用** | 只存儲指標 | 存儲指標 + 控制塊 |
| **執行緒安全** | 不保證 | 參考計數操作是執行緒安全的 |
| **適用場景** | 單一擁有者 | 多個擁有者 |

## std::unique_ptr

### 特性
- **獨佔所有權**：同一時間只能有一個 `unique_ptr` 擁有物件
- **移動語意**：支援移動但不支援複製
- **零開銷**：沒有額外的記憶體和效能開銷
- **自動清理**：超出作用域時自動釋放記憶體

### 基本用法

```cpp
#include <memory>

// 建立 unique_ptr
std::unique_ptr<int> ptr1 = std::make_unique<int>(42);
std::unique_ptr<int> ptr2(new int(42));  // 較不推薦

// 使用
*ptr1 = 100;
std::cout << *ptr1 << std::endl;

// 移動所有權
std::unique_ptr<int> ptr3 = std::move(ptr1);
// ptr1 現在是 nullptr

// 重置
ptr3.reset(new int(200));

// 釋放所有權並取得原始指標
int* raw_ptr = ptr3.release();
delete raw_ptr;  // 需要手動刪除
```

### 自定義刪除器

```cpp
// 自定義刪除器
auto custom_deleter = [](int* p) {
    std::cout << "Custom deleting: " << *p << std::endl;
    delete p;
};

std::unique_ptr<int, decltype(custom_deleter)> ptr(new int(42), custom_deleter);
```

## std::shared_ptr

### 特性
- **共享所有權**：多個 `shared_ptr` 可以同時擁有同一物件
- **參考計數**：透過參考計數管理生命週期
- **執行緒安全**：參考計數操作是原子的
- **控制塊**：額外的記憶體存儲參考計數資訊

### 基本用法

```cpp
#include <memory>

// 建立 shared_ptr
std::shared_ptr<int> ptr1 = std::make_shared<int>(42);
std::shared_ptr<int> ptr2(new int(42));  // 較不推薦

// 複製（增加參考計數）
std::shared_ptr<int> ptr3 = ptr1;
std::cout << "參考計數: " << ptr1.use_count() << std::endl;  // 輸出 2

// 重置（減少參考計數）
ptr3.reset();
std::cout << "參考計數: " << ptr1.use_count() << std::endl;  // 輸出 1

// 檢查是否唯一
if (ptr1.unique()) {
    std::cout << "ptr1 是唯一的擁有者" << std::endl;
}
```

### 循環引用問題

```cpp
// 問題：循環引用導致記憶體洩漏
struct Node {
    std::shared_ptr<Node> next;
    std::shared_ptr<Node> prev;  // 循環引用！
};

// 解決方案：使用 weak_ptr 打破循環
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;    // 使用 weak_ptr
};
```

## 完整範例程式

```cpp
#include <iostream>
#include <memory>
#include <vector>

class Resource {
public:
    Resource(int id) : id_(id) {
        std::cout << "Resource " << id_ << " created\n";
    }
    
    ~Resource() {
        std::cout << "Resource " << id_ << " destroyed\n";
    }
    
    void use() {
        std::cout << "Using resource " << id_ << "\n";
    }
    
private:
    int id_;
};

void unique_ptr_demo() {
    std::cout << "\n=== unique_ptr 示範 ===\n";
    
    // 創建和使用
    auto ptr1 = std::make_unique<Resource>(1);
    ptr1->use();
    
    // 移動所有權
    auto ptr2 = std::move(ptr1);
    // ptr1 現在是 nullptr
    
    if (!ptr1) {
        std::cout << "ptr1 已失效\n";
    }
    
    ptr2->use();
}

void shared_ptr_demo() {
    std::cout << "\n=== shared_ptr 示範 ===\n";
    
    // 創建和共享
    auto ptr1 = std::make_shared<Resource>(2);
    std::cout << "參考計數: " << ptr1.use_count() << "\n";
    
    {
        auto ptr2 = ptr1;  // 複製
        std::cout << "複製後參考計數: " << ptr1.use_count() << "\n";
        ptr2->use();
    }  // ptr2 銷毀
    
    std::cout << "ptr2 銷毀後參考計數: " << ptr1.use_count() << "\n";
    ptr1->use();
}

int main() {
    unique_ptr_demo();
    shared_ptr_demo();
    
    std::cout << "\n程式結束\n";
    return 0;
}
```

## 選擇指南

### 使用 unique_ptr 當：
- ✅ 資源只需要一個擁有者
- ✅ 需要最佳效能（零開銷）
- ✅ 表達獨佔所有權的語意
- ✅ 替代原始指標和手動 delete
- ✅ 在容器中存儲獨有物件

### 使用 shared_ptr 當：
- ✅ 多個物件需要共享同一資源
- ✅ 不確定哪個物件最後使用資源
- ✅ 需要在不同執行緒間共享資源
- ✅ 實現觀察者模式或回調機制
- ✅ 需要延遲清理或弱引用

## 最佳實踐

1. **預設使用 unique_ptr**：大多數情況下不需要共享
2. **優先使用 make_unique/make_shared**：更安全且效率更高
3. **避免循環引用**：使用 weak_ptr 打破循環
4. **不要混用**：避免將 unique_ptr 轉換為 shared_ptr
5. **考慮效能**：shared_ptr 在多執行緒環境下有額外開銷

## 效能比較

| 操作 | unique_ptr | shared_ptr |
|------|------------|------------|
| 建立 | O(1) | O(1) |
| 複製 | 不支援 | O(1) 但有原子操作 |
| 移動 | O(1) | O(1) |
| 銷毀 | O(1) | O(1) 但可能觸發物件銷毀 |
| 記憶體使用 | 8 bytes | 16 bytes + 控制塊 |

## 常見陷阱

1. **循環引用**：shared_ptr 無法自動解決循環引用
2. **效能誤解**：shared_ptr 不是萬能的，有額外開銷
3. **執行緒安全**：只有參考計數是執行緒安全的，物件本身不是
4. **自引用**：避免物件持有指向自己的 shared_ptr

## 結論

智能指標是現代 C++ 的重要工具，能大幅提升程式碼的安全性和可維護性。選擇合適的智能指標類型對於寫出高品質的 C++ 程式碼至關重要。記住：「預設使用 unique_ptr，只有在真正需要共享時才使用 shared_ptr」。
