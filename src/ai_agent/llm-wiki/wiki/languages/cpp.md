---
title: C++
tags: [cpp, systems, performance, embedded]
sources: []
created: 2026-04-07
updated: 2026-04-07
---

# C++

## 語言定位

> C++ 是一種追求極致效能的系統程式語言，從遊戲引擎到嵌入式裝置都需要它。

## 核心特性

- **零成本抽象**：抽象不會帶來執行期負擔
- **記憶體控制**：手動管理記憶體，自由度極高
- **指標**：直接記憶體操作
- **RAII**：資源取得即初始化
- **模板**：編譯期泛型程式設計

## 語法速查

```cpp
// 變數
int x = 10;
const int y = 20;  // 常數

// 指標與參考
int* ptr = &x;     // 指標
int& ref = x;      // 參考

// 智慧指標（C++11+）
#include <memory>
auto uptr = std::make_unique<int>(42);
auto sptr = std::make_shared<int>(42);

// 類別
class Point {
private:
    double x, y;
public:
    Point(double x, double y) : x(x), y(y) {}
    
    double distance(const Point& other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        return std::sqrt(dx*dx + dy*dy);
    }
};

// 模板
template<typename T>
T max(T a, T b) {
    return a > b ? a : b;
}

// Lambda（C++11）
auto add = [](int a, int b) { return a + b; };

// 錯誤處理
try {
    throw std::runtime_error("error message");
} catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
}
```

## C++ 併發模型

- **std::thread**：原生執行緒
- **std::mutex / lock_guard**：互斥鎖
- **std::atomic**：原子操作
- **std::future / promise**：非同步結果
- **C++20 coroutines**：協程支援

## C++ 生態

| 領域 | 常用庫/框架 |
|------|-------------|
| 遊戲 | Unreal Engine, Unity (C#), cocos2d-x |
| 嵌入式 | bare-metal, FreeRTOS |
| 影像處理 | OpenCV |
| 高效能網路 | Boost.Asio |

## 相關概念

- [[concepts/記憶體管理]]
- [[concepts/併發模型]]
- [[concepts/錯誤處理]]

## 相關專案

- [[projects/gpio-driver|GPIO Driver]] - C 嵌入式專案

## 外部資源

- [cppreference](https://en.cppreference.com/)
- [Learn C++](https://www.learncpp.com/)
