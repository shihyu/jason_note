# Chapter 07: 資料結構性能分析

## 本章重點

深入分析常用資料結構的性能特徵，包括時間複雜度、空間複雜度、快取友善性等面向。

## STL 容器性能比較

### 1. 序列容器

| 容器 | 插入前端 | 插入尾端 | 插入中間 | 隨機存取 | 快取友善 |
|------|----------|----------|----------|----------|----------|
| vector | O(n) | O(1)* | O(n) | O(1) | 優秀 |
| deque | O(1) | O(1) | O(n) | O(1) | 良好 |
| list | O(1) | O(1) | O(1) | O(n) | 差 |
| forward_list | O(1) | O(n) | O(1) | O(n) | 差 |

*攤銷複雜度

### 2. 關聯容器

| 容器 | 插入 | 查找 | 刪除 | 有序 | 實作 |
|------|------|------|------|------|------|
| set/map | O(log n) | O(log n) | O(log n) | 是 | 紅黑樹 |
| unordered_set/map | O(1)* | O(1)* | O(1)* | 否 | 雜湊表 |
| multiset/multimap | O(log n) | O(log n) | O(log n) | 是 | 紅黑樹 |

## vector 優化技巧

### 1. 預配置容量
```cpp
std::vector<int> vec;
vec.reserve(10000);  // 避免多次重新配置

// 建構時指定大小
std::vector<int> vec(10000);  // 直接配置並初始化
```

### 2. 避免不必要的複製
```cpp
// 使用 emplace_back 而非 push_back
struct Complex {
    int a, b;
    Complex(int x, int y) : a(x), b(y) {}
};

vec.emplace_back(1, 2);  // 原地建構
// vs
vec.push_back(Complex(1, 2));  // 建構後複製
```

### 3. shrink_to_fit 謹慎使用
```cpp
vec.erase(vec.begin() + vec.size()/2, vec.end());
vec.shrink_to_fit();  // 可能觸發重新配置
```

## 雜湊表優化

### 1. 負載因子調整
```cpp
std::unordered_map<int, int> map;
map.max_load_factor(0.5);  // 降低碰撞，增加記憶體使用
map.reserve(10000);  // 預配置 bucket 數量
```

### 2. 自訂雜湊函數
```cpp
struct CustomHash {
    size_t operator()(const Key& k) const {
        // 好的雜湊函數減少碰撞
        return std::hash<int>()(k.a) ^
               (std::hash<int>()(k.b) << 1);
    }
};

std::unordered_map<Key, Value, CustomHash> map;
```

## 自訂資料結構

### 1. 快取友善的矩陣
```cpp
// 行主序存儲
template<typename T>
class Matrix {
    std::vector<T> data;
    size_t rows, cols;

public:
    T& operator()(size_t i, size_t j) {
        return data[i * cols + j];  // 連續記憶體存取
    }
};
```

### 2. 緊湊的位元集合
```cpp
class BitSet {
    std::vector<uint64_t> bits;
    size_t size;

public:
    bool test(size_t pos) const {
        return bits[pos / 64] & (1ULL << (pos % 64));
    }

    void set(size_t pos) {
        bits[pos / 64] |= (1ULL << (pos % 64));
    }
};
```

### 3. B+ 樹用於資料庫索引
```cpp
template<typename Key, typename Value, size_t ORDER = 256>
class BPlusTree {
    struct Node {
        bool is_leaf;
        std::vector<Key> keys;
        std::vector<Node*> children;  // 內部節點
        std::vector<Value> values;     // 葉節點
        Node* next;  // 葉節點鏈結
    };

    // 大節點提高快取利用率
    static constexpr size_t node_size = ORDER;
};
```

## 無鎖資料結構

### 1. 無鎖佇列
```cpp
template<typename T>
class LockFreeQueue {
    struct Node {
        std::atomic<T*> data;
        std::atomic<Node*> next;
    };

    std::atomic<Node*> head;
    std::atomic<Node*> tail;

public:
    void enqueue(T item) {
        Node* new_node = new Node;
        new_node->data.store(new T(std::move(item)));
        new_node->next.store(nullptr);

        Node* prev_tail = tail.exchange(new_node);
        prev_tail->next.store(new_node);
    }
};
```

## flat 容器

### flat_map 實作概念
```cpp
template<typename Key, typename Value>
class flat_map {
    std::vector<std::pair<Key, Value>> data;

public:
    auto find(const Key& key) {
        return std::lower_bound(
            data.begin(), data.end(), key,
            [](const auto& p, const Key& k) {
                return p.first < k;
            }
        );
    }

    // 批量插入後排序
    void sort() {
        std::sort(data.begin(), data.end());
    }
};
```

## 特殊用途結構

### 1. 環形緩衝區
```cpp
template<typename T, size_t N>
class RingBuffer {
    std::array<T, N> buffer;
    size_t head = 0;
    size_t tail = 0;

public:
    void push(T value) {
        buffer[head] = std::move(value);
        head = (head + 1) % N;
    }

    T pop() {
        T value = std::move(buffer[tail]);
        tail = (tail + 1) % N;
        return value;
    }
};
```

### 2. Bloom Filter
```cpp
class BloomFilter {
    std::vector<bool> bits;
    std::vector<std::function<size_t(const std::string&)>> hash_functions;

public:
    void insert(const std::string& item) {
        for (auto& hash : hash_functions) {
            bits[hash(item) % bits.size()] = true;
        }
    }

    bool possibly_contains(const std::string& item) {
        for (auto& hash : hash_functions) {
            if (!bits[hash(item) % bits.size()]) {
                return false;
            }
        }
        return true;  // 可能存在（有偽陽性）
    }
};
```

## 性能測量建議

```cpp
// 基準測試框架
template<typename Func>
void benchmark(const std::string& name, Func f, size_t iterations) {
    auto start = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < iterations; ++i) {
        f();
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    std::cout << name << ": "
              << duration.count() / iterations
              << " μs per operation\n";
}
```

## 選擇資料結構的考慮因素

1. **存取模式**
   - 順序 vs 隨機
   - 讀多寫少 vs 寫多讀少

2. **資料特性**
   - 資料量大小
   - 鍵值分布
   - 是否需要排序

3. **記憶體考慮**
   - 快取友善性
   - 記憶體開銷
   - 碎片化

4. **並發需求**
   - 是否需要執行緒安全
   - 讀寫比例
   - 競爭程度