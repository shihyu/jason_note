# Flamegraph 火焰圖完整指南

## 一、什麼是 Flamegraph？

### 1.1 基本概念

Flamegraph（火焰圖）是一種性能分析的視覺化工具，由 Brendan Gregg 發明。它能夠快速識別程式中最耗費 CPU 時間的代碼路徑。

```
     ┌─────────────────────────────────┐  ← 寬度 = CPU 時間佔比
     │         function_d()             │
     ├──────────┬──────────────────────┤
     │function_c│    function_e()       │  ← 每層 = 調用棧深度
     ├──────────┴──────────┬───────────┤
     │    function_b()      │function_f │
     ├──────────────────────┴───────────┤
     │           function_a()           │  ← 底部 = 程式入口
     └─────────────────────────────────┘
```

### 1.2 視覺化原理

- **X 軸（寬度）**：表示採樣數量（CPU 時間佔比）
- **Y 軸（高度）**：表示調用棧深度
- **顏色**：通常用來區分不同類型的函數（系統/用戶/庫函數）
- **火焰形狀**：因為越往上函數越少，看起來像火焰

---

## 二、Flamegraph 類型

### 2.1 CPU 火焰圖
最常見的類型，顯示 CPU 時間消耗

```bash
# 採集 CPU 性能數據
perf record -F 99 -p <PID> -g -- sleep 60
perf script > out.perf
```

### 2.2 Memory 火焰圖
顯示記憶體分配的調用棧

```bash
# 使用 brendangregg/FlameGraph 工具
perf record -e malloc -g -p <PID> -- sleep 60
```

### 2.3 Off-CPU 火焰圖
顯示程式阻塞（非 CPU 執行）的時間

```bash
# 追蹤 off-CPU 時間
bpftrace -e 'tracepoint:sched:sched_switch { @[kstack, ustack, comm] = sum(nsecs); }'
```

### 2.4 Differential 火焰圖
比較兩個版本的性能差異

```bash
# 紅色表示增加的時間，藍色表示減少的時間
flamegraph.pl --title="Diff" --colors=java diff.folded > diff.svg
```

---

## 三、安裝與使用

### 3.1 安裝 FlameGraph 工具

```bash
# Clone Brendan Gregg 的官方倉庫
git clone https://github.com/brendangregg/FlameGraph.git
cd FlameGraph

# 添加到 PATH（可選）
export PATH=$PATH:$(pwd)
```

### 3.2 基本使用流程

```bash
# 步驟 1: 收集性能數據
perf record -F 99 -p $(pgrep myapp) -g -- sleep 30

# 步驟 2: 生成性能報告
perf script > out.perf

# 步驟 3: 摺疊調用棧
./stackcollapse-perf.pl out.perf > out.folded

# 步驟 4: 生成火焰圖
./flamegraph.pl out.folded > flamegraph.svg

# 步驟 5: 在瀏覽器中查看
firefox flamegraph.svg
```

---

## 四、高頻交易場景應用

### 4.1 延遲分析範例

```cpp
// 範例：高頻交易系統的關鍵路徑
class TradingEngine {
public:
    void processMarketData(const MarketData& data) {
        // 標記性能追蹤點
        TRACE_ENTER("processMarketData");
        
        parseData(data);           // 10% CPU
        updateOrderBook(data);      // 15% CPU
        calculateSignals();         // 45% CPU ← 火焰圖會顯示這是熱點
        executeStrategy();          // 20% CPU
        sendOrders();              // 10% CPU
        
        TRACE_EXIT("processMarketData");
    }
};
```

### 4.2 採集腳本

```bash
#!/bin/bash
# hft_flamegraph.sh - 高頻交易系統火焰圖生成腳本

PID=$(pgrep trading_engine)
DURATION=60
OUTPUT_DIR="./flamegraphs"

mkdir -p $OUTPUT_DIR

# CPU 火焰圖
echo "Collecting CPU samples..."
perf record -F 999 -p $PID -g -o $OUTPUT_DIR/perf.data -- sleep $DURATION
perf script -i $OUTPUT_DIR/perf.data > $OUTPUT_DIR/out.perf
./stackcollapse-perf.pl $OUTPUT_DIR/out.perf > $OUTPUT_DIR/out.folded
./flamegraph.pl --title="HFT CPU Flamegraph" \
                --subtitle="Sample rate: 999 Hz" \
                --width=1800 \
                $OUTPUT_DIR/out.folded > $OUTPUT_DIR/cpu_flame.svg

echo "Flamegraph saved to $OUTPUT_DIR/cpu_flame.svg"
```

### 4.3 延遲熱點識別

```python
# 分析火焰圖數據，找出延遲熱點
def analyze_flamegraph_data(folded_file):
    """
    解析 folded 格式的火焰圖數據
    格式: stack;frame1;frame2;frame3 count
    """
    hotspots = {}
    total_samples = 0
    
    with open(folded_file, 'r') as f:
        for line in f:
            stack, count = line.rsplit(' ', 1)
            count = int(count)
            total_samples += count
            
            # 提取每個函數的採樣數
            for func in stack.split(';'):
                hotspots[func] = hotspots.get(func, 0) + count
    
    # 計算百分比並排序
    sorted_hotspots = sorted(
        [(func, count, count/total_samples*100) 
         for func, count in hotspots.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    print("Top 10 CPU Hotspots:")
    for func, count, percentage in sorted_hotspots[:10]:
        print(f"{percentage:6.2f}% - {func}")
```

---

## 五、進階技巧

### 5.1 自定義顏色方案

```perl
# 修改 flamegraph.pl 的顏色配置
my %palette = (
    "hot" => "rgb(255,0,0)",      # 熱點函數 - 紅色
    "kernel" => "rgb(255,128,0)",  # 核心函數 - 橘色  
    "jit" => "rgb(255,255,0)",     # JIT 代碼 - 黃色
    "user" => "rgb(0,255,0)",      # 用戶代碼 - 綠色
);
```

### 5.2 過濾和聚焦

```bash
# 只顯示包含特定函數的調用棧
grep processOrder out.folded | ./flamegraph.pl > order_processing.svg

# 排除某些函數
grep -v idle out.folded | ./flamegraph.pl > no_idle.svg

# 聚焦特定模組
./flamegraph.pl --title="Strategy Module" \
                --minwidth=0.5 \
                --grep="strategy" \
                out.folded > strategy_focus.svg
```

### 5.3 即時火焰圖

```bash
#!/bin/bash
# 即時生成火焰圖（每 10 秒更新）

while true; do
    perf record -F 99 -p $PID -g -o perf.data -- sleep 10
    perf script -i perf.data | \
        ./stackcollapse-perf.pl | \
        ./flamegraph.pl --title="Real-time $(date +%T)" > realtime.svg
    
    # 更新網頁顯示
    mv realtime.svg /var/www/html/flamegraph.svg
done
```

### 5.4 與 BPF 結合

```python
#!/usr/bin/python
# 使用 BPF 生成更精確的火焰圖

from bcc import BPF
import time

# BPF 程式
bpf_text = """
#include <uapi/linux/ptrace.h>

BPF_STACK_TRACE(stack_traces, 10240);
BPF_HASH(counts, u32);

int do_trace(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    // 只追蹤特定 PID
    if (pid != TARGET_PID)
        return 0;
    
    u32 stackid = stack_traces.get_stackid(ctx, BPF_F_USER_STACK);
    counts.increment(stackid);
    
    return 0;
}
"""

# 編譯並載入 BPF
b = BPF(text=bpf_text.replace('TARGET_PID', str(target_pid)))
b.attach_perf_event(ev_type=PerfType.SOFTWARE,
                    ev_config=PerfSWConfig.CPU_CLOCK,
                    fn_name="do_trace",
                    sample_freq=99)

# 收集數據
time.sleep(60)

# 生成火焰圖數據
for k, v in b["counts"].items():
    stack = b["stack_traces"].lookup(k)
    # 處理並輸出調用棧...
```

---

## 六、優化建議

### 6.1 採樣頻率選擇

```yaml
採樣頻率建議:
  日常分析: 99 Hz    # 避免與常見定時器頻率共振
  詳細分析: 999 Hz   # 更高精度，但開銷較大
  生產環境: 49 Hz    # 最小化性能影響
  
計算公式:
  樣本數 = 採樣頻率 × 採集時間
  建議最少 1000 個樣本以獲得有意義的結果
```

### 6.2 降低採集開銷

```bash
# 使用 Intel PT (Processor Trace) - 硬體級追蹤
perf record -e intel_pt// -p $PID -- sleep 10

# 只採集特定事件
perf record -e cycles:u -p $PID -- sleep 10  # 只採集用戶空間

# 使用 LBR (Last Branch Record)
perf record --call-graph lbr -p $PID -- sleep 10
```

### 6.3 高頻交易系統特別優化

```cpp
// 在關鍵路徑添加採樣點
class PerformanceTracer {
public:
    // 使用編譯時開關，生產環境可完全移除
    #ifdef ENABLE_TRACING
    #define TRACE_POINT(name) tracer.mark(name)
    #else
    #define TRACE_POINT(name) ((void)0)
    #endif
    
    void mark(const char* point) {
        // 寫入低延遲的環形緩衝區
        // 避免系統調用
        ring_buffer.write(rdtsc(), point);
    }
};

// 使用範例
void processOrder(Order& order) {
    TRACE_POINT("order_received");
    validateOrder(order);
    
    TRACE_POINT("risk_check_start");
    if (!riskCheck(order)) return;
    
    TRACE_POINT("send_to_exchange");
    exchange.send(order);
}
```

---

## 七、常見問題解析

### 7.1 為什麼火焰圖是平的？

```yaml
可能原因:
  1. 採樣頻率太低: 增加到 999 Hz
  2. 程式太簡單: 沒有深度調用棧
  3. 內聯優化: 編譯器內聯了函數
  4. 符號資訊缺失: 需要 -g 編譯選項
  
解決方案:
  - 使用 -fno-omit-frame-pointer 編譯
  - 確保有調試符號
  - 增加採樣時間
```

### 7.2 火焰圖太複雜看不懂

```bash
# 簡化技巧
# 1. 按模組過濾
grep -E "strategy|trading" out.folded | ./flamegraph.pl > simplified.svg

# 2. 設定最小寬度閾值
./flamegraph.pl --minwidth=1 out.folded > cleaner.svg

# 3. 限制棧深度
awk -F';' 'NF<=10' out.folded | ./flamegraph.pl > shallow.svg
```

### 7.3 如何比較優化前後？

```bash
# 生成差異火焰圖
# 1. 收集優化前數據
perf record -o before.data -p $PID -g -- sleep 60
perf script -i before.data | ./stackcollapse-perf.pl > before.folded

# 2. 部署優化後收集
perf record -o after.data -p $PID -g -- sleep 60
perf script -i after.data | ./stackcollapse-perf.pl > after.folded

# 3. 生成差異圖
./difffolded.pl before.folded after.folded | \
    ./flamegraph.pl --title="Optimization Diff" --colors=java > diff.svg
```

---

## 八、實戰案例

### 8.1 發現記憶體分配熱點

```cpp
// 問題代碼 - 火焰圖顯示 malloc 佔 30% CPU
void processTickData(const Tick& tick) {
    // 每次都分配新 vector - 性能問題！
    std::vector<double> prices;  
    prices.push_back(tick.bid);
    prices.push_back(tick.ask);
    calculate(prices);
}

// 優化後 - 重用記憶體
class TickProcessor {
    std::vector<double> prices_buffer;  // 預分配
public:
    void processTickData(const Tick& tick) {
        prices_buffer.clear();  // 只清空，不釋放
        prices_buffer.push_back(tick.bid);
        prices_buffer.push_back(tick.ask);
        calculate(prices_buffer);
    }
};
```

### 8.2 識別鎖競爭

```bash
# Off-CPU 火焰圖能顯示鎖等待時間
# 如果看到大量 futex_wait，表示鎖競爭嚴重

# 採集 off-CPU 數據
bpftrace -e '
tracepoint:sched:sched_switch {
    if (args->prev_state == TASK_INTERRUPTIBLE) {
        @lock_wait[kstack] = sum(nsecs);
    }
}'
```

---

## 九、整合到 CI/CD

### 9.1 自動性能回歸測試

```yaml
# .github/workflows/performance.yml
name: Performance Regression Test

on: [push, pull_request]

jobs:
  perf-test:
    steps:
      - name: Run Performance Test
        run: |
          ./run_load_test.sh
          perf record -F 99 -g ./trading_engine_test
          
      - name: Generate Flamegraph
        run: |
          perf script | ./stackcollapse-perf.pl > out.folded
          ./flamegraph.pl out.folded > flamegraph.svg
          
      - name: Upload Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: flamegraph
          path: flamegraph.svg
          
      - name: Check Performance Regression
        run: |
          python check_performance.py --baseline main.folded \
                                     --current out.folded \
                                     --threshold 5
```

### 9.2 性能儀錶板整合

```javascript
// 將火焰圖嵌入 Grafana
const FlameGraphPanel = {
  type: 'html',
  targets: [{
    format: 'table',
    rawSql: `
      SELECT 
        timestamp,
        flamegraph_url
      FROM performance_tests
      ORDER BY timestamp DESC
      LIMIT 1
    `
  }],
  content: '<iframe src="{{flamegraph_url}}" width="100%" height="600"/>'
};
```

---

## 十、簡單程式範例

### 10.1 CPU 密集型程式範例

```cpp
// cpu_intensive.cpp - 用來練習生成 CPU 火焰圖
#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>

// 故意寫效率差的質數判斷（教學用）
bool is_prime_slow(int n) {
    if (n <= 1) return false;
    for (int i = 2; i < n; i++) {  // 故意不優化到 sqrt(n)
        if (n % i == 0) return false;
    }
    return true;
}

// 稍微優化的版本
bool is_prime_better(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }
    return true;
}

// 計算費波那契數列（遞迴版本 - 效率差）
long fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

// 矩陣運算（會顯示在火焰圖中）
void matrix_multiply(std::vector<std::vector<int>>& A,
                     std::vector<std::vector<int>>& B,
                     std::vector<std::vector<int>>& C) {
    int n = A.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
            for (int k = 0; k < n; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    std::cout << "Starting CPU intensive tasks...\n";
    
    // 任務 1: 找質數（預期佔 40% CPU）
    std::cout << "Task 1: Finding primes...\n";
    int prime_count = 0;
    for (int i = 1; i <= 50000; i++) {
        if (is_prime_slow(i)) prime_count++;
    }
    std::cout << "Found " << prime_count << " primes\n";
    
    // 任務 2: 費波那契（預期佔 30% CPU）
    std::cout << "Task 2: Computing Fibonacci...\n";
    for (int i = 1; i <= 35; i++) {
        fibonacci_recursive(i);
    }
    
    // 任務 3: 矩陣運算（預期佔 30% CPU）
    std::cout << "Task 3: Matrix multiplication...\n";
    int size = 200;
    std::vector<std::vector<int>> A(size, std::vector<int>(size, 1));
    std::vector<std::vector<int>> B(size, std::vector<int>(size, 2));
    std::vector<std::vector<int>> C(size, std::vector<int>(size, 0));
    
    for (int i = 0; i < 10; i++) {
        matrix_multiply(A, B, C);
    }
    
    std::cout << "All tasks completed!\n";
    return 0;
}
```

**編譯和生成火焰圖：**

```bash
# 編譯（保留符號資訊和框架指標）
g++ -g -O2 -fno-omit-frame-pointer cpu_intensive.cpp -o cpu_intensive

# 執行並收集性能數據
./cpu_intensive &
PID=$!
sleep 1  # 等程式開始
perf record -F 99 -p $PID -g -- sleep 10

# 生成火焰圖
perf script | ./stackcollapse-perf.pl | ./flamegraph.pl > cpu_intensive.svg

# 預期結果：
# - is_prime_slow() 佔約 40% 寬度
# - fibonacci_recursive() 佔約 30% 寬度（且調用棧很深）
# - matrix_multiply() 佔約 30% 寬度
```

### 10.2 記憶體分配範例

```cpp
// memory_allocation.cpp - 用來練習生成 Memory 火焰圖
#include <iostream>
#include <vector>
#include <list>
#include <memory>
#include <cstring>

// 問題 1：頻繁的小記憶體分配
void frequent_small_allocations() {
    for (int i = 0; i < 100000; i++) {
        // 每次都 new 一個小物件（反面教材）
        int* p = new int(i);
        // 做一些計算
        *p = *p * 2;
        delete p;
    }
}

// 問題 2：vector 不當使用導致多次重新分配
void vector_reallocation_problem() {
    std::vector<int> vec;
    // 沒有 reserve，導致多次重新分配
    for (int i = 0; i < 100000; i++) {
        vec.push_back(i);  // 可能觸發重新分配
    }
}

// 問題 3：字串拼接的記憶體問題
void string_concatenation_problem() {
    std::string result;
    for (int i = 0; i < 10000; i++) {
        // 每次 += 可能導致重新分配
        result += "Hello World ";
    }
}

// 優化版本：使用物件池
class ObjectPool {
    std::vector<int*> pool;
    std::vector<int*> available;
    
public:
    ObjectPool(size_t size) {
        for (size_t i = 0; i < size; i++) {
            int* obj = new int(0);
            pool.push_back(obj);
            available.push_back(obj);
        }
    }
    
    int* acquire() {
        if (available.empty()) {
            return new int(0);
        }
        int* obj = available.back();
        available.pop_back();
        return obj;
    }
    
    void release(int* obj) {
        available.push_back(obj);
    }
    
    ~ObjectPool() {
        for (auto* obj : pool) {
            delete obj;
        }
    }
};

void optimized_with_pool() {
    ObjectPool pool(1000);
    
    for (int i = 0; i < 100000; i++) {
        int* p = pool.acquire();
        *p = i * 2;
        pool.release(p);
    }
}

int main() {
    std::cout << "Starting memory allocation tests...\n";
    
    // 執行有問題的版本
    std::cout << "Running problematic versions...\n";
    frequent_small_allocations();
    vector_reallocation_problem();
    string_concatenation_problem();
    
    // 執行優化版本
    std::cout << "Running optimized version...\n";
    optimized_with_pool();
    
    std::cout << "Completed!\n";
    return 0;
}
```

**追蹤記憶體分配：**

```bash
# 使用 heaptrack（更適合記憶體分析）
heaptrack ./memory_allocation
heaptrack --analyze heaptrack.memory_allocation.*.gz

# 或使用 perf
perf record -e kmem:kmalloc -g ./memory_allocation
perf script | ./stackcollapse-perf.pl | ./flamegraph.pl > memory.svg
```

### 10.3 多執行緒與鎖競爭範例

```cpp
// lock_contention.cpp - 用來練習生成 Off-CPU 火焰圖
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <atomic>
#include <chrono>

std::mutex global_mutex;
std::atomic<long> shared_counter(0);

// 問題：過度使用全域鎖
void bad_locking_thread(int thread_id) {
    for (int i = 0; i < 100000; i++) {
        // 鎖的粒度太大
        std::lock_guard<std::mutex> lock(global_mutex);
        
        // 在鎖裡面做太多事情
        int local_computation = 0;
        for (int j = 0; j < 100; j++) {
            local_computation += j * thread_id;
        }
        shared_counter += local_computation;
    }
}

// 優化：減少鎖的粒度
void better_locking_thread(int thread_id) {
    for (int i = 0; i < 100000; i++) {
        // 先在鎖外面計算
        int local_computation = 0;
        for (int j = 0; j < 100; j++) {
            local_computation += j * thread_id;
        }
        
        // 只在必要時加鎖
        std::lock_guard<std::mutex> lock(global_mutex);
        shared_counter += local_computation;
    }
}

// 最優：使用原子操作
void atomic_thread(int thread_id) {
    for (int i = 0; i < 100000; i++) {
        int local_computation = 0;
        for (int j = 0; j < 100; j++) {
            local_computation += j * thread_id;
        }
        
        // 使用原子操作代替鎖
        shared_counter.fetch_add(local_computation, std::memory_order_relaxed);
    }
}

int main(int argc, char* argv[]) {
    const int num_threads = 8;
    std::vector<std::thread> threads;
    
    std::string mode = (argc > 1) ? argv[1] : "bad";
    
    auto start = std::chrono::high_resolution_clock::now();
    
    if (mode == "bad") {
        std::cout << "Running with bad locking...\n";
        for (int i = 0; i < num_threads; i++) {
            threads.emplace_back(bad_locking_thread, i);
        }
    } else if (mode == "better") {
        std::cout << "Running with better locking...\n";
        for (int i = 0; i < num_threads; i++) {
            threads.emplace_back(better_locking_thread, i);
        }
    } else {
        std::cout << "Running with atomic operations...\n";
        for (int i = 0; i < num_threads; i++) {
            threads.emplace_back(atomic_thread, i);
        }
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Result: " << shared_counter << std::endl;
    std::cout << "Time: " << duration.count() << " ms" << std::endl;
    
    return 0;
}
```

**生成 Off-CPU 火焰圖查看鎖等待：**

```bash
# 編譯
g++ -g -O2 -pthread -fno-omit-frame-pointer lock_contention.cpp -o lock_contention

# 使用 bpftrace 追蹤 off-CPU 時間
sudo bpftrace -e '
tracepoint:sched:sched_switch {
    @start[tid] = nsecs;
}

tracepoint:sched:sched_switch {
    $duration = nsecs - @start[tid];
    @offcpu[kstack, ustack, comm] = sum($duration);
    delete(@start[tid]);
}

END {
    clear(@start);
}' > offcpu.txt

# 運行三種模式比較
./lock_contention bad    # 會看到大量 mutex 等待
./lock_contention better # mutex 等待減少
./lock_contention atomic # 幾乎沒有等待
```

### 10.4 高頻交易模擬範例

```cpp
// hft_simulation.cpp - 模擬高頻交易系統的關鍵路徑
#include <iostream>
#include <vector>
#include <deque>
#include <algorithm>
#include <random>
#include <chrono>
#include <cstring>

struct MarketData {
    double bid;
    double ask;
    long timestamp;
    int volume;
};

struct Order {
    enum Type { BUY, SELL };
    Type type;
    double price;
    int quantity;
    long timestamp;
};

class OrderBook {
private:
    std::deque<Order> bids;
    std::deque<Order> asks;
    
public:
    // 這個函數會在火焰圖中顯示為熱點
    void update(const MarketData& data) {
        // 模擬訂單簿更新（簡化版）
        Order bid_order = {Order::BUY, data.bid, data.volume, data.timestamp};
        Order ask_order = {Order::SELL, data.ask, data.volume, data.timestamp};
        
        // 插入排序（實際系統會用更高效的資料結構）
        bids.push_back(bid_order);
        std::sort(bids.begin(), bids.end(), 
                  [](const Order& a, const Order& b) { 
                      return a.price > b.price; 
                  });
        
        asks.push_back(ask_order);
        std::sort(asks.begin(), asks.end(),
                  [](const Order& a, const Order& b) { 
                      return a.price < b.price; 
                  });
        
        // 限制深度
        if (bids.size() > 100) bids.resize(100);
        if (asks.size() > 100) asks.resize(100);
    }
    
    double get_mid_price() const {
        if (bids.empty() || asks.empty()) return 0;
        return (bids.front().price + asks.front().price) / 2.0;
    }
};

class TradingStrategy {
private:
    std::vector<double> price_history;
    const size_t window_size = 20;
    
public:
    // 簡單的均值回歸策略（會佔用 CPU）
    Order* generate_signal(const OrderBook& book) {
        double mid_price = book.get_mid_price();
        price_history.push_back(mid_price);
        
        if (price_history.size() < window_size) {
            return nullptr;
        }
        
        // 計算移動平均（這裡會顯示在火焰圖中）
        double sum = 0;
        for (size_t i = price_history.size() - window_size; 
             i < price_history.size(); i++) {
            sum += price_history[i];
        }
        double ma = sum / window_size;
        
        // 計算標準差（另一個熱點）
        double variance = 0;
        for (size_t i = price_history.size() - window_size; 
             i < price_history.size(); i++) {
            double diff = price_history[i] - ma;
            variance += diff * diff;
        }
        double std_dev = std::sqrt(variance / window_size);
        
        // 簡單的交易信號
        if (mid_price < ma - 2 * std_dev) {
            return new Order{Order::BUY, mid_price, 100, 0};
        } else if (mid_price > ma + 2 * std_dev) {
            return new Order{Order::SELL, mid_price, 100, 0};
        }
        
        return nullptr;
    }
};

class RiskManager {
private:
    double max_position = 10000;
    double current_position = 0;
    double max_loss = -1000;
    double current_pnl = 0;
    
public:
    // 風控檢查（關鍵路徑，需要極快）
    bool check_order(const Order* order) {
        if (!order) return true;
        
        // 檢查持倉限制
        double position_change = (order->type == Order::BUY) ? 
                                order->quantity : -order->quantity;
        
        if (std::abs(current_position + position_change) > max_position) {
            return false;
        }
        
        // 檢查損失限制
        if (current_pnl < max_loss) {
            return false;
        }
        
        return true;
    }
    
    void update_position(const Order* order) {
        if (!order) return;
        
        double position_change = (order->type == Order::BUY) ? 
                                order->quantity : -order->quantity;
        current_position += position_change;
    }
};

// 主要的交易循環
void trading_loop(int num_ticks) {
    OrderBook book;
    TradingStrategy strategy;
    RiskManager risk;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> price_dist(99.0, 101.0);
    std::uniform_int_distribution<> volume_dist(100, 1000);
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_ticks; i++) {
        // 生成模擬市場數據
        MarketData data;
        data.bid = price_dist(gen);
        data.ask = data.bid + 0.01;
        data.volume = volume_dist(gen);
        data.timestamp = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now().time_since_epoch()).count();
        
        // 關鍵路徑開始 >>>
        
        // 1. 更新訂單簿（預期 30% CPU）
        book.update(data);
        
        // 2. 生成交易信號（預期 40% CPU）
        Order* signal = strategy.generate_signal(book);
        
        // 3. 風控檢查（預期 10% CPU）
        if (risk.check_order(signal)) {
            // 4. 發送訂單（預期 20% CPU）
            risk.update_position(signal);
            // 實際系統這裡會發送到交易所
        }
        
        delete signal;
        
        // <<< 關鍵路徑結束
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    double latency_per_tick = static_cast<double>(duration.count()) / num_ticks;
    std::cout << "Processed " << num_ticks << " ticks\n";
    std::cout << "Average latency: " << latency_per_tick << " microseconds/tick\n";
}

int main() {
    std::cout << "Starting HFT simulation...\n";
    
    // 預熱
    trading_loop(1000);
    
    // 主要測試
    std::cout << "Running main test...\n";
    trading_loop(1000000);
    
    return 0;
}
```

**生成高頻交易系統的火焰圖：**

```bash
# 編譯（開啟優化但保留調試資訊）
g++ -g -O3 -march=native -fno-omit-frame-pointer hft_simulation.cpp -o hft_sim

# 運行並收集數據
./hft_sim &
PID=$!

# 等待程式進入主循環
sleep 2

# 收集 30 秒的性能數據（高採樣率）
sudo perf record -F 999 -p $PID -g -- sleep 30

# 生成火焰圖
sudo perf script | ./stackcollapse-perf.pl | \
    ./flamegraph.pl --title="HFT System Flame Graph" \
                    --subtitle="1000 Hz sampling" \
                    --width=1800 > hft_flame.svg

# 預期在火焰圖中看到：
# - OrderBook::update() 約 30% 寬度
# - TradingStrategy::generate_signal() 約 40% 寬度
#   - 其中計算移動平均和標準差是主要熱點
# - RiskManager::check_order() 約 10% 寬度
# - 其他（包括記憶體操作等）約 20% 寬度
```

### 10.5 生成對比火焰圖的腳本

```bash
#!/bin/bash
# compare_performance.sh - 對比優化前後的性能

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Performance Comparison Script${NC}"

# 編譯兩個版本
echo "Compiling baseline version..."
g++ -g -O2 -fno-omit-frame-pointer -DBASELINE cpu_intensive.cpp -o baseline

echo "Compiling optimized version..."
g++ -g -O3 -march=native -fno-omit-frame-pointer cpu_intensive.cpp -o optimized

# 收集基準版本數據
echo -e "${RED}Collecting baseline performance data...${NC}"
./baseline &
PID=$!
sleep 1
perf record -F 99 -p $PID -g -o baseline.data -- sleep 10
wait $PID

# 收集優化版本數據
echo -e "${GREEN}Collecting optimized performance data...${NC}"
./optimized &
PID=$!
sleep 1
perf record -F 99 -p $PID -g -o optimized.data -- sleep 10
wait $PID

# 生成火焰圖
echo "Generating flame graphs..."
perf script -i baseline.data | ./stackcollapse-perf.pl > baseline.folded
perf script -i optimized.data | ./stackcollapse-perf.pl > optimized.folded

# 生成單獨的火焰圖
./flamegraph.pl baseline.folded > baseline.svg
./flamegraph.pl optimized.folded > optimized.svg

# 生成對比火焰圖
./difffolded.pl baseline.folded optimized.folded | \
    ./flamegraph.pl --title="Optimization Comparison" \
                    --subtitle="Red = Slower, Blue = Faster" \
                    --colors=java > diff.svg

echo "Generated files:"
echo "  - baseline.svg (baseline performance)"
echo "  - optimized.svg (optimized performance)"
echo "  - diff.svg (performance difference)"

# 簡單的性能統計
echo -e "\n${GREEN}Performance Summary:${NC}"
echo -n "Baseline samples: "
awk '{sum+=$NF} END {print sum}' baseline.folded
echo -n "Optimized samples: "
awk '{sum+=$NF} END {print sum}' optimized.folded

# 找出最大的改進
echo -e "\n${GREEN}Top improvements:${NC}"
./difffolded.pl baseline.folded optimized.folded | \
    sort -t' ' -k2 -nr | head -5
```

這些範例程式涵蓋了：
- **CPU 密集型**：質數計算、遞迴、矩陣運算
- **記憶體問題**：頻繁分配、vector 重分配、物件池優化
- **多執行緒**：鎖競爭、原子操作優化
- **高頻交易模擬**：完整的交易路徑
- **自動化對比**：優化前後的性能比較腳本

每個範例都有詳細的編譯和執行指令，以及預期在火焰圖中看到的結果。

## 十一、總結與最佳實踐

### 關鍵要點

1. **火焰圖是性能優化的 X 光片** - 能快速定位熱點
2. **寬度比高度重要** - 寬的函數才是優化目標
3. **不同類型解決不同問題** - CPU/Memory/Off-CPU 各有用途
4. **採樣要有代表性** - 確保覆蓋典型工作負載
5. **結合其他工具使用** - perf、BPF、VTune 等

### 高頻交易場景注意事項

- 使用硬體時間戳（TSC）提高精度
- 區分熱路徑和冷路徑的優化優先級
- 關注尾延遲（P99.9）而非平均值
- 定期生成火焰圖，追蹤性能變化趨勢
- 在測試環境模擬生產負載

### 進一步學習資源

- [Brendan Gregg's Blog](http://www.brendangregg.com/flamegraphs.html)
- [Linux Perf Examples](http://www.brendangregg.com/perf.html)
- [BPF Performance Tools](https://github.com/iovisor/bcc)
- [Intel VTune Profiler](https://software.intel.com/content/www/us/en/develop/tools/vtune-profiler.html)