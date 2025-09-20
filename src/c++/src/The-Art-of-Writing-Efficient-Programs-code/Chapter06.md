# Chapter 06: 記憶體管理和優化

## 本章重點

探討 C++ 記憶體管理的性能影響，包括動態記憶體配置、自訂配置器、記憶體池等技術。

## 核心概念

### 1. 動態記憶體配置開銷
- **堆配置成本**: malloc/new 的時間複雜度
- **記憶體碎片化**: 內部和外部碎片
- **快取效應**: 堆配置的記憶體局部性較差

### 2. 智慧指標
- **std::unique_ptr**: 零開銷獨占所有權
- **std::shared_ptr**: 引用計數的開銷
- **std::weak_ptr**: 避免循環引用

## 記憶體配置策略

### 1. 棧配置 vs 堆配置
```cpp
// 棧配置 - 快速
void stack_allocation() {
    int array[1000];  // 自動釋放，快速配置
}

// 堆配置 - 較慢
void heap_allocation() {
    int* array = new int[1000];  // 需要手動管理
    // ... 使用 array
    delete[] array;
}
```

### 2. 記憶體池 (Memory Pool)
```cpp
template<typename T>
class MemoryPool {
    struct Block {
        alignas(T) char data[sizeof(T)];
        Block* next;
    };

    Block* free_list = nullptr;
    std::vector<std::unique_ptr<Block[]>> chunks;
    size_t chunk_size = 1024;

public:
    T* allocate() {
        if (!free_list) {
            expand();
        }
        Block* block = free_list;
        free_list = free_list->next;
        return reinterpret_cast<T*>(block);
    }

    void deallocate(T* ptr) {
        Block* block = reinterpret_cast<Block*>(ptr);
        block->next = free_list;
        free_list = block;
    }

private:
    void expand() {
        auto new_chunk = std::make_unique<Block[]>(chunk_size);
        for (size_t i = 0; i < chunk_size - 1; ++i) {
            new_chunk[i].next = &new_chunk[i + 1];
        }
        new_chunk[chunk_size - 1].next = free_list;
        free_list = &new_chunk[0];
        chunks.push_back(std::move(new_chunk));
    }
};
```

### 3. 自訂配置器
```cpp
template<typename T>
class CustomAllocator {
public:
    using value_type = T;

    T* allocate(size_t n) {
        // 自訂配置邏輯
        return static_cast<T*>(::operator new(n * sizeof(T)));
    }

    void deallocate(T* p, size_t) {
        ::operator delete(p);
    }
};

// 使用自訂配置器
std::vector<int, CustomAllocator<int>> vec;
```

## 小物件優化

### 1. Small String Optimization (SSO)
```cpp
class String {
    union {
        char small_buffer[16];  // 小字串直接存儲
        char* large_buffer;     // 大字串使用堆
    };
    size_t size;
    bool is_small;
};
```

### 2. Small Object Allocator
```cpp
class SmallObjectAllocator {
    // 不同大小的物件池
    MemoryPool<8> pool8;
    MemoryPool<16> pool16;
    MemoryPool<32> pool32;
    MemoryPool<64> pool64;

public:
    void* allocate(size_t size) {
        if (size <= 8) return pool8.allocate();
        if (size <= 16) return pool16.allocate();
        if (size <= 32) return pool32.allocate();
        if (size <= 64) return pool64.allocate();
        return ::operator new(size);
    }
};
```

## 記憶體存取模式優化

### 1. 預配置
```cpp
std::vector<int> vec;
vec.reserve(1000);  // 預先配置空間，避免重新配置
```

### 2. 物件池模式
```cpp
template<typename T>
class ObjectPool {
    std::stack<std::unique_ptr<T>> pool;

public:
    std::unique_ptr<T> acquire() {
        if (pool.empty()) {
            return std::make_unique<T>();
        }
        auto obj = std::move(pool.top());
        pool.pop();
        return obj;
    }

    void release(std::unique_ptr<T> obj) {
        obj->reset();  // 重置狀態
        pool.push(std::move(obj));
    }
};
```

## RAII 和異常安全

### 確保異常安全
```cpp
class Resource {
    std::unique_ptr<int[]> data;
    size_t size;

public:
    Resource(size_t n)
        : data(std::make_unique<int[]>(n)), size(n) {
        // 如果建構失敗，unique_ptr 自動清理
    }
    // 自動生成正確的移動語義
    Resource(Resource&&) = default;
    Resource& operator=(Resource&&) = default;
};
```

## 記憶體對齊

### 對齊配置
```cpp
// C++17 對齊的動態配置
void* aligned_alloc(size_t alignment, size_t size);

// 對齊的資料結構
struct alignas(64) CacheLineAligned {
    int data[16];
};
```

## 性能測量

### 記憶體使用分析
```bash
# Valgrind Massif
valgrind --tool=massif ./program
ms_print massif.out.<pid>

# 堆剖析
heaptrack ./program
heaptrack_gui heaptrack.program.<pid>.gz
```

## 最佳實踐

1. **優先使用棧配置**
   - 使用 std::array 而非動態陣列
   - 考慮 alloca 用於小型動態大小

2. **避免頻繁配置/釋放**
   - 使用物件池
   - 預配置容器容量
   - 重用物件

3. **智慧指標使用**
   - 預設使用 unique_ptr
   - 只在需要共享時使用 shared_ptr
   - 考慮 make_unique/make_shared

4. **自訂配置器**
   - 特殊用途的記憶體池
   - 減少碎片化
   - 改善局部性

## 常見陷阱

1. 記憶體洩漏
2. 使用已釋放的記憶體
3. 重複釋放
4. 緩衝區溢位
5. 未對齊的存取