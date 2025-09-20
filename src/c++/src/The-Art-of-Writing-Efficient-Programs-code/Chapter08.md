# Chapter 08: C++ 並發程式設計

## 本章重點

深入探討 C++ 的並發機制，包括原子操作、記憶體順序、無鎖程式設計和高階並發工具。

## 原子操作和記憶體順序

### 1. 原子類型
```cpp
std::atomic<int> counter{0};
std::atomic<bool> flag{false};
std::atomic<void*> ptr{nullptr};

// 原子操作
counter.fetch_add(1);  // 原子加法
int old = counter.exchange(5);  // 原子交換
```

### 2. 記憶體順序 (Memory Order)
```cpp
// 不同的記憶體順序選項
std::atomic<int> x;

// Relaxed - 最弱，只保證原子性
x.store(1, std::memory_order_relaxed);

// Release-Acquire - 同步語義
x.store(1, std::memory_order_release);
int val = x.load(std::memory_order_acquire);

// Sequential Consistency - 最強，預設
x.store(1, std::memory_order_seq_cst);
```

### 3. Compare-And-Swap (CAS)
```cpp
std::atomic<int> value{0};
int expected = 0;
int desired = 1;

// 強 CAS
bool success = value.compare_exchange_strong(expected, desired);

// 弱 CAS（可能偽失敗）
bool success = value.compare_exchange_weak(expected, desired);
```

## 無鎖程式設計

### 1. 無鎖棧
```cpp
template<typename T>
class LockFreeStack {
    struct Node {
        T data;
        Node* next;
    };

    std::atomic<Node*> head{nullptr};

public:
    void push(T value) {
        Node* new_node = new Node{std::move(value), nullptr};
        new_node->next = head.load();
        while (!head.compare_exchange_weak(new_node->next, new_node));
    }

    bool pop(T& result) {
        Node* old_head = head.load();
        while (old_head &&
               !head.compare_exchange_weak(old_head, old_head->next));
        if (old_head) {
            result = std::move(old_head->data);
            delete old_head;
            return true;
        }
        return false;
    }
};
```

### 2. 雙重檢查鎖定
```cpp
class Singleton {
    static std::atomic<Singleton*> instance;
    static std::mutex mutex;

public:
    static Singleton* getInstance() {
        Singleton* tmp = instance.load(std::memory_order_acquire);
        if (!tmp) {
            std::lock_guard<std::mutex> lock(mutex);
            tmp = instance.load(std::memory_order_relaxed);
            if (!tmp) {
                tmp = new Singleton();
                instance.store(tmp, std::memory_order_release);
            }
        }
        return tmp;
    }
};
```

## 高階同步原語

### 1. std::future 和 std::async
```cpp
// 非同步執行
std::future<int> result = std::async(std::launch::async, []() {
    return compute_heavy_task();
});

// 獲取結果（阻塞）
int value = result.get();

// 檢查是否完成
if (result.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
    // 已完成
}
```

### 2. std::promise
```cpp
void producer(std::promise<int> prom) {
    int value = compute_value();
    prom.set_value(value);
}

void consumer() {
    std::promise<int> prom;
    std::future<int> fut = prom.get_future();

    std::thread t(producer, std::move(prom));
    int value = fut.get();  // 等待結果
    t.join();
}
```

### 3. std::packaged_task
```cpp
std::packaged_task<int(int, int)> task([](int a, int b) {
    return a + b;
});

std::future<int> result = task.get_future();
std::thread t(std::move(task), 2, 3);
int sum = result.get();  // 5
t.join();
```

## 執行緒池實作

```cpp
class ThreadPool {
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex queue_mutex;
    std::condition_variable cv;
    bool stop = false;

public:
    ThreadPool(size_t num_threads) {
        for (size_t i = 0; i < num_threads; ++i) {
            workers.emplace_back([this] {
                for (;;) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(queue_mutex);
                        cv.wait(lock, [this] { return stop || !tasks.empty(); });
                        if (stop && tasks.empty()) return;
                        task = std::move(tasks.front());
                        tasks.pop();
                    }
                    task();
                }
            });
        }
    }

    template<typename F, typename... Args>
    auto enqueue(F&& f, Args&&... args)
        -> std::future<typename std::result_of<F(Args...)>::type> {
        using return_type = typename std::result_of<F(Args...)>::type;

        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );

        std::future<return_type> res = task->get_future();
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            tasks.emplace([task](){ (*task)(); });
        }
        cv.notify_one();
        return res;
    }

    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            stop = true;
        }
        cv.notify_all();
        for (std::thread& worker : workers) {
            worker.join();
        }
    }
};
```

## 平行演算法 (C++17)

```cpp
#include <execution>
#include <algorithm>

std::vector<int> data(1000000);

// 平行排序
std::sort(std::execution::par, data.begin(), data.end());

// 平行轉換
std::transform(std::execution::par_unseq,
               data.begin(), data.end(), data.begin(),
               [](int x) { return x * 2; });

// 平行歸約
int sum = std::reduce(std::execution::par,
                      data.begin(), data.end(), 0);
```

## 協程 (C++20)

```cpp
#include <coroutine>

struct Task {
    struct promise_type {
        Task get_return_object() {
            return {std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() {}
    };

    std::coroutine_handle<promise_type> h_;
};

Task async_task() {
    std::cout << "Start\n";
    co_await std::suspend_always{};
    std::cout << "Resume\n";
}
```

## 並發容器

### 1. 並發佇列
```cpp
template<typename T>
class ConcurrentQueue {
    mutable std::mutex mutex;
    std::queue<T> queue;
    std::condition_variable cv;

public:
    void push(T value) {
        {
            std::lock_guard<std::mutex> lock(mutex);
            queue.push(std::move(value));
        }
        cv.notify_one();
    }

    bool try_pop(T& value) {
        std::lock_guard<std::mutex> lock(mutex);
        if (queue.empty()) return false;
        value = std::move(queue.front());
        queue.pop();
        return true;
    }

    void wait_and_pop(T& value) {
        std::unique_lock<std::mutex> lock(mutex);
        cv.wait(lock, [this] { return !queue.empty(); });
        value = std::move(queue.front());
        queue.pop();
    }
};
```

## 效能考慮

### 1. 避免過度同步
- 減少鎖的粒度
- 使用讀寫鎖
- 考慮無鎖方案

### 2. 減少競爭
- 執行緒本地存儲
- 工作分區
- 批次處理

### 3. NUMA 感知
```cpp
// 綁定執行緒到特定 CPU
std::thread t([]() {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);  // 綁定到 CPU 0
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
    // 工作...
});
```

## 偵錯工具

```bash
# ThreadSanitizer
g++ -fsanitize=thread -g program.cpp

# Helgrind
valgrind --tool=helgrind ./program

# Intel VTune
vtune -collect threading ./program
```