# C++ 和 Rust 函數追蹤技術完整指南

## 目錄
- [概述](#概述)
- [GCC 編譯器內建追蹤](#gcc-編譯器內建追蹤)
- [專業函數追蹤工具](#專業函數追蹤工具)
- [Rust 追蹤解決方案](#rust-追蹤解決方案)
- [GDB 自動化追蹤](#gdb-自動化追蹤)
- [系統級追蹤工具](#系統級追蹤工具)
- [進階追蹤技術](#進階追蹤技術)
- [視覺化工具](#視覺化工具)
- [實用建議與最佳實踐](#實用建議與最佳實踐)
- [常見問題與解決方案](#常見問題與解決方案)

## 概述

函數追蹤是理解程式執行流程、診斷問題和優化效能的關鍵技術。本指南涵蓋從基礎到進階的各種追蹤方法，適用於 C++、Rust 等系統程式語言。

### 為什麼需要函數追蹤？
- **程式碼理解**: 快速掌握大型專案的架構和執行邏輯
- **效能優化**: 識別熱點函數和效能瓶頸
- **除錯診斷**: 追蹤難以重現的錯誤和異常行為
- **記憶體分析**: 發現記憶體洩漏和不當使用
- **並發分析**: 理解多執行緒程式的執行順序

## GCC 編譯器內建追蹤

### finstrument-functions 方法

GCC 內建函數插樁是最直接的方法：

```bash
# 編譯時加入 -finstrument-functions
gcc -finstrument-functions -g your_program.cpp -o your_program

# 排除特定函數不被插樁
gcc -finstrument-functions -finstrument-functions-exclude-function-list=main,foo -g your_program.cpp

# 排除特定檔案
gcc -finstrument-functions -finstrument-functions-exclude-file-list=/usr/include -g your_program.cpp
```

#### 基礎實現
```cpp
#include <stdio.h>
#include <execinfo.h>
#include <dlfcn.h>

extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_enter(void *callee, void *caller) {
    Dl_info info;
    if (dladdr(callee, &info)) {
        printf(">>> 進入函數: %s [%p]\n", 
               info.dli_sname ? info.dli_sname : "unknown", callee);
    }
}

extern "C" __attribute__((no_instrument_function))  
void __cyg_profile_func_exit(void *callee, void *caller) {
    Dl_info info;
    if (dladdr(callee, &info)) {
        printf("<<< 離開函數: %s [%p]\n", 
               info.dli_sname ? info.dli_sname : "unknown", callee);
    }
}
```

#### 進階實現：帶時間戳和調用深度
```cpp
#include <chrono>
#include <stack>
#include <unordered_map>
#include <mutex>

class FunctionTracer {
private:
    static thread_local int depth_;
    static thread_local std::stack<std::chrono::high_resolution_clock::time_point> time_stack_;
    static std::mutex output_mutex_;
    
public:
    static void enter(void* func, void* caller) {
        auto now = std::chrono::high_resolution_clock::now();
        time_stack_.push(now);
        
        std::lock_guard<std::mutex> lock(output_mutex_);
        for (int i = 0; i < depth_; ++i) printf("  ");
        printf("→ %p\n", func);
        depth_++;
    }
    
    static void exit(void* func, void* caller) {
        auto now = std::chrono::high_resolution_clock::now();
        auto duration = now - time_stack_.top();
        time_stack_.pop();
        depth_--;
        
        std::lock_guard<std::mutex> lock(output_mutex_);
        for (int i = 0; i < depth_; ++i) printf("  ");
        printf("← %p [%lld µs]\n", func, 
               std::chrono::duration_cast<std::chrono::microseconds>(duration).count());
    }
};

extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_enter(void *callee, void *caller) {
    FunctionTracer::enter(callee, caller);
}

extern "C" __attribute__((no_instrument_function))
void __cyg_profile_func_exit(void *callee, void *caller) {
    FunctionTracer::exit(callee, caller);
}
```

### Call Stack Logger 專案
- **GitHub**: [TomaszAugustyn/call-stack-logger](https://github.com/TomaszAugustyn/call-stack-logger)
- **功能特色**:
  - 自動函數名稱解析和記憶體地址轉換
  - 帶縮進的調用樹狀結構輸出
  - 時間戳記錄和調用深度追蹤
  - 支援多執行緒程式的完整追蹤
  - 輸出到檔案或標準輸出

### Clang 編譯器支援

Clang 也支援類似的功能：
```bash
# Clang 使用相同的選項
clang++ -finstrument-functions -g program.cpp -o program

# Clang 特有的 XRay 追蹤
clang++ -fxray-instrument -g program.cpp -o program
XRAY_OPTIONS="patch_premain=true xray_mode=xray-basic" ./program
```

## 專業函數追蹤工具

### uftrace - 強大的使用者空間追蹤工具

- **GitHub**: [namhyung/uftrace](https://github.com/namhyung/uftrace)
- **安裝**:
```bash
# Ubuntu/Debian
sudo apt-get install uftrace

# Fedora/RHEL
sudo dnf install uftrace

# 從原始碼編譯
git clone https://github.com/namhyung/uftrace.git
cd uftrace
./configure
make
sudo make install
```

#### 基本使用
```bash
# 編譯程式時加入追蹤選項
gcc -pg -g program.c -o program
# 或者
gcc -finstrument-functions -g program.c -o program

# 追蹤執行
uftrace record ./program
uftrace replay

# 即時追蹤並顯示
uftrace ./program

# 只顯示執行時間超過 1ms 的函數
uftrace -t 1ms ./program

# 追蹤特定函數
uftrace -F main -F process_data ./program

# 生成調用圖
uftrace graph
```

#### 進階功能
```bash
# 記錄函數參數和返回值
uftrace record -A . -R . ./program

# 生成火焰圖
uftrace record ./program
uftrace dump --flame-graph | flamegraph.pl > flame.svg

# 生成 Chrome tracing 格式
uftrace dump --chrome > trace.json
# 在 Chrome 中開啟 chrome://tracing 並載入 trace.json

# 統計函數執行時間
uftrace report --stats

# 追蹤 Python 程式
uftrace record -t 1ms python3 script.py
```

### 其他追蹤工具專案

#### funtrace
- **GitHub**: [yosefk/funtrace](https://github.com/yosefk/funtrace)
- **特色**: 快速、小型函數調用追蹤器，適合嵌入式系統
```bash
# 使用範例
gcc -finstrument-functions program.c funtrace.c -ldl -o program
./program
```

#### ftracer
- **GitHub**: [finaldie/ftracer](https://github.com/finaldie/ftracer)
- **特色**: 生成時間軸調用圖的工具包
```bash
# 編譯時連結 ftracer
gcc -finstrument-functions program.c -lftracer -o program
FTRACER_OUTPUT=trace.log ./program
ftracer_plot trace.log > timeline.html
```

#### tracer
- **GitHub**: [mohsenmahroos/tracer](https://github.com/mohsenmahroos/tracer)
- **特色**: 簡單的 C++ 追蹤類別，使用 RAII 模式
```cpp
#include "tracer.h"

void function() {
    TRACE_FUNC();  // 自動追蹤函數進入和離開
    // 函數邏輯
}
```

### Valgrind Callgrind

```bash
# 編譯程式（需要調試符號）
gcc -g program.c -o program

# 使用 callgrind 追蹤
valgrind --tool=callgrind ./program

# 生成調用圖
callgrind_annotate callgrind.out.*

# 使用 KCachegrind 視覺化
kcachegrind callgrind.out.*
```

## Rust 追蹤解決方案

### tracing crate - Rust 官方推薦

#### 基本設置
```toml
# Cargo.toml
[dependencies]
tracing = "0.1"
tracing-subscriber = "0.3"
tokio = { version = "1", features = ["full"] }
```

#### 使用範例
```rust
use tracing::{instrument, info, warn, error, span, Level};
use tracing_subscriber;

// 自動為函數添加追蹤
#[instrument(level = "info", ret, err)]
async fn process_data(data: &str) -> Result<String, Error> {
    info!("Processing data: {}", data);
    
    // 創建子 span
    let span = span!(Level::DEBUG, "validation");
    let _enter = span.enter();
    
    if data.is_empty() {
        warn!("Empty data received");
        return Err(Error::EmptyData);
    }
    
    Ok(data.to_uppercase())
}

// 追蹤異步函數
#[instrument(skip(db), fields(user_id = %user_id))]
async fn fetch_user(db: &Database, user_id: u64) -> Result<User, Error> {
    let user = db.get_user(user_id).await?;
    info!("Found user: {}", user.name);
    Ok(user)
}

fn main() {
    // 初始化追蹤訂閱器
    tracing_subscriber::fmt()
        .with_max_level(Level::TRACE)
        .with_thread_ids(true)
        .with_thread_names(true)
        .with_file(true)
        .with_line_number(true)
        .init();
    
    // 程式邏輯
}
```

#### 進階配置
```rust
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

fn init_tracing() {
    let fmt_layer = tracing_subscriber::fmt::layer()
        .with_target(false)
        .with_timer(tracing_subscriber::fmt::time::uptime())
        .with_level(true)
        .with_thread_ids(true)
        .with_thread_names(true);
    
    // 添加過濾器
    let filter_layer = tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| "info,my_app=debug".into());
    
    tracing_subscriber::registry()
        .with(filter_layer)
        .with(fmt_layer)
        .init();
}
```

### rftrace - Rust 函數追蹤器
- **GitHub**: [hermit-os/rftrace](https://github.com/hermit-os/rftrace)
- **功能**: 專為 Rust 設計的函數追蹤器，支援內核和使用者空間的完整追蹤

### cargo-flamegraph

```bash
# 安裝
cargo install flamegraph

# 生成火焰圖
cargo flamegraph --bin my_program

# 使用 release 模式並保留調試符號
cargo flamegraph --release -- my_arg1 my_arg2
```

## GDB 自動化追蹤

### GDB 腳本自動記錄

#### 基礎腳本
```gdb
# trace_all.gdb
set pagination off
set logging file trace.log
set logging on
set height 0

# 為所有函數設置斷點
rbreak .*

# 定義自動執行的命令
commands
silent
printf ">>> %s\n", $rip
backtrace 1
continue
end

# 執行程式
run
```

執行方式：
```bash
gdb -x trace_all.gdb ./program
```

#### 進階腳本：選擇性追蹤
```gdb
# selective_trace.gdb
set pagination off
set logging file trace.log
set logging on

# 只追蹤特定模組的函數
rbreak MyClass::.*
rbreak process_.*

# 記錄函數參數
commands
silent
printf "Function: "
x/i $pc
info args
info locals
continue
end

run
```

#### Python 擴展 GDB 腳本
```python
# trace_with_time.py
import gdb
import time

class FunctionTracer(gdb.Command):
    def __init__(self):
        super().__init__("trace-functions", gdb.COMMAND_USER)
        self.start_time = time.time()
        
    def invoke(self, arg, from_tty):
        # 設置所有函數斷點
        gdb.execute("rbreak .*")
        
        # 定義斷點處理
        def on_breakpoint(event):
            if isinstance(event, gdb.BreakpointEvent):
                frame = gdb.selected_frame()
                elapsed = time.time() - self.start_time
                print(f"[{elapsed:.6f}] {frame.name()}")
                gdb.execute("continue")
        
        gdb.events.stop.connect(on_breakpoint)
        gdb.execute("run")

FunctionTracer()
```

## 系統級追蹤工具

### ltrace 和 strace

#### ltrace - 庫函數追蹤
```bash
# 基本使用
ltrace ./program

# 追蹤特定庫函數
ltrace -e malloc+free+strcpy ./program

# 顯示時間戳
ltrace -t ./program

# 追蹤子進程
ltrace -f ./program

# 統計函數調用
ltrace -c ./program

# 追蹤已執行的進程
ltrace -p $(pidof program)
```

#### strace - 系統調用追蹤
```bash
# 基本使用
strace ./program

# 只追蹤特定系統調用
strace -e open,read,write ./program

# 追蹤網路相關調用
strace -e trace=network ./program

# 顯示調用時間
strace -T ./program

# 統計系統調用
strace -c ./program

# 追蹤所有子進程
strace -ff -o trace ./program
```

### SystemTap

```bash
# 安裝
sudo apt-get install systemtap systemtap-runtime

# 簡單的函數追蹤腳本
# trace_functions.stp
probe process("./program").function("*") {
    printf("%s -> %s\n", thread_indent(1), probefunc())
}

probe process("./program").function("*").return {
    printf("%s <- %s\n", thread_indent(-1), probefunc())
}

# 執行
sudo stap trace_functions.stp -c ./program
```

### eBPF/BCC 工具

```python
#!/usr/bin/python
# trace_functions.py
from bcc import BPF

# BPF 程式
bpf_text = """
#include <uapi/linux/ptrace.h>

int trace_func_entry(struct pt_regs *ctx) {
    u64 pid = bpf_get_current_pid_tgid();
    bpf_trace_printk("PID %d entered function\\n", pid >> 32);
    return 0;
}
"""

# 載入 BPF 程式
b = BPF(text=bpf_text)
b.attach_uprobe(name="./program", sym="main", fn_name="trace_func_entry")

# 讀取輸出
b.trace_print()
```

## 進階追蹤技術

### Intel VTune Profiler

```bash
# 收集數據
vtune -collect hotspots ./program

# 分析結果
vtune -report summary -r r000hs

# GUI 模式
vtune-gui r000hs
```

### AMD uProf

```bash
# 收集效能數據
AMDuProfCLI collect --config tbp ./program

# 生成報告
AMDuProfCLI report -i AMDuProf-program/
```

### Linux Perf

```bash
# 記錄函數調用
perf record -g ./program

# 查看報告
perf report

# 生成火焰圖
perf record -F 99 -g ./program
perf script | stackcollapse-perf.pl | flamegraph.pl > perf.svg

# 即時監控
perf top -g
```

### DTrace (macOS/FreeBSD/Solaris)

```d
/* trace_functions.d */
pid$target::*:entry
{
    printf("%*s-> %s\n", ++indent * 2, "", probefunc);
}

pid$target::*:return
{
    printf("%*s<- %s\n", indent-- * 2, "", probefunc);
}
```

執行：
```bash
sudo dtrace -s trace_functions.d -c ./program
```

## 視覺化工具

### 火焰圖 (Flame Graphs)

```bash
# 安裝 FlameGraph 工具
git clone https://github.com/brendangregg/FlameGraph
cd FlameGraph

# 使用 perf 生成火焰圖
perf record -F 99 -ag -- ./program
perf script | ./stackcollapse-perf.pl | ./flamegraph.pl > flame.svg

# 使用 uftrace 生成火焰圖
uftrace record ./program
uftrace dump --flame-graph | ./flamegraph.pl > flame.svg
```

### Perfetto UI

```bash
# 生成 Perfetto 格式追蹤
uftrace record ./program
uftrace dump --chrome > trace.json

# 開啟 https://ui.perfetto.dev/ 並載入 trace.json
```

### KCachegrind

```bash
# 生成 callgrind 數據
valgrind --tool=callgrind ./program

# 視覺化
kcachegrind callgrind.out.*
```

### Graphviz 調用圖

```bash
# 使用 uftrace 生成 dot 檔案
uftrace record ./program
uftrace graph -f dot > call_graph.dot

# 轉換為圖片
dot -Tpng call_graph.dot -o call_graph.png
dot -Tsvg call_graph.dot -o call_graph.svg
```

## 實用建議與最佳實踐

### 快速開始方案

#### C++ 專案
1. **輕量級追蹤**: 使用 `-finstrument-functions` 配合簡單的追蹤函數
2. **完整分析**: 使用 uftrace 配合 `-pg` 編譯選項
3. **效能分析**: 使用 perf 或 VTune
4. **記憶體分析**: 使用 Valgrind 配合 Callgrind

#### Rust 專案
1. **開發階段**: 使用 tracing crate 的 `#[instrument]` 宏
2. **效能分析**: 使用 cargo-flamegraph
3. **系統級追蹤**: 使用 uftrace 或 perf

#### 無法重編譯的程式
1. **動態追蹤**: 使用 GDB 自動化腳本
2. **系統調用**: 使用 strace
3. **庫函數**: 使用 ltrace
4. **進階追蹤**: 使用 SystemTap 或 eBPF

### 效能考量

#### 降低追蹤開銷
```cpp
// 使用條件編譯
#ifdef ENABLE_TRACING
    #define TRACE_FUNC() FunctionTracer tracer(__FUNCTION__)
#else
    #define TRACE_FUNC()
#endif

// 採樣追蹤
static std::atomic<int> sample_counter{0};
extern "C" void __cyg_profile_func_enter(void *callee, void *caller) {
    if (++sample_counter % 100 == 0) {  // 只追蹤 1% 的調用
        // 執行追蹤
    }
}
```

#### 過濾策略
```bash
# uftrace: 時間過濾
uftrace -t 10us ./program  # 只顯示超過 10 微秒的函數

# uftrace: 深度過濾
uftrace -D 3 ./program  # 只追蹤 3 層深度

# uftrace: 函數過濾
uftrace -F main -F 'process_*' ./program  # 只追蹤特定函數
uftrace -N 'std::*' ./program  # 排除 std 命名空間
```

### 多執行緒追蹤

```cpp
// 執行緒安全的追蹤實現
#include <thread>
#include <mutex>
#include <unordered_map>

class ThreadSafeTracer {
private:
    static std::mutex mutex_;
    static std::unordered_map<std::thread::id, int> depth_map_;
    
public:
    static void enter(void* func) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto tid = std::this_thread::get_id();
        auto& depth = depth_map_[tid];
        
        std::cout << "[" << tid << "] ";
        for (int i = 0; i < depth; ++i) std::cout << "  ";
        std::cout << "→ " << func << std::endl;
        depth++;
    }
};
```

### 分散式追蹤

#### OpenTelemetry 整合
```rust
// Rust with OpenTelemetry
use opentelemetry::{global, sdk::propagation::TraceContextPropagator};
use tracing_subscriber::layer::SubscriberExt;

fn init_telemetry() {
    global::set_text_map_propagator(TraceContextPropagator::new());
    
    let tracer = opentelemetry_jaeger::new_pipeline()
        .with_service_name("my_service")
        .install_simple()
        .unwrap();
    
    let telemetry = tracing_opentelemetry::layer().with_tracer(tracer);
    
    tracing_subscriber::registry()
        .with(telemetry)
        .init();
}
```

## 常見問題與解決方案

### 問題 1：符號解析失敗

**症狀**: 只看到記憶體地址，沒有函數名稱

**解決方案**:
```bash
# 確保編譯時包含調試符號
gcc -g -O0 program.c -o program

# 保留符號表（即使在 strip 後）
gcc -g program.c -o program
objcopy --only-keep-debug program program.debug
strip program
objcopy --add-gnu-debuglink=program.debug program

# 使用 addr2line 解析地址
addr2line -e program 0x401234
```

### 問題 2：追蹤開銷過大

**症狀**: 程式執行速度明顯變慢

**解決方案**:
```cpp
// 1. 使用編譯時開關
#ifdef DEBUG_TRACE
    // 追蹤程式碼
#endif

// 2. 動態開關
bool g_tracing_enabled = false;
extern "C" void __cyg_profile_func_enter(void *callee, void *caller) {
    if (!g_tracing_enabled) return;
    // 追蹤邏輯
}

// 3. 選擇性追蹤
// 只追蹤特定模組
gcc -finstrument-functions src/core/*.c -c
gcc src/other/*.c -c  # 不加追蹤選項
```

### 問題 3：輸出過多難以分析

**症狀**: 追蹤日誌檔案過大，難以找到關鍵資訊

**解決方案**:
```bash
# 1. 使用過濾器
uftrace -F main -D 3 ./program  # 只看 main 函數 3 層深度

# 2. 後處理過濾
grep "error\|warning" trace.log

# 3. 使用結構化日誌
# 輸出 JSON 格式，便於程式化處理
uftrace dump --format=json > trace.json
jq '.[] | select(.name | contains("process"))' trace.json
```

### 問題 4：靜態連結程式無法追蹤

**症狀**: ltrace 無輸出，uftrace 無法工作

**解決方案**:
```bash
# 1. 使用 strace（系統調用仍可追蹤）
strace ./static_program

# 2. 重新編譯為動態連結
gcc -dynamic program.c -o program

# 3. 使用 GDB 或 SystemTap
gdb ./static_program
systemtap -e 'probe process("static_program").function("*") { println(probefunc()) }'
```

### 問題 5：即時系統的追蹤

**症狀**: 追蹤影響即時性能

**解決方案**:
```cpp
// 使用無鎖資料結構
#include <atomic>
#include <array>

class LockFreeTracer {
    struct TraceEntry {
        void* func;
        uint64_t timestamp;
    };
    
    static std::array<TraceEntry, 10000> buffer_;
    static std::atomic<size_t> index_;
    
public:
    static void trace(void* func) {
        size_t idx = index_.fetch_add(1) % buffer_.size();
        buffer_[idx] = {func, get_timestamp()};
    }
};
```

### 使用場景建議

| 場景 | 推薦工具 | 理由 |
|------|---------|------|
| 理解新專案結構 | uftrace + 視覺化 | 快速生成調用圖 |
| 效能瓶頸分析 | perf + 火焰圖 | 低開銷，準確採樣 |
| 記憶體問題診斷 | Valgrind + GDB | 完整的記憶體追蹤 |
| 生產環境診斷 | eBPF/SystemTap | 動態追蹤，無需重啟 |
| 單元測試覆蓋 | gcov + lcov | 程式碼覆蓋率分析 |
| 分散式系統 | OpenTelemetry | 跨服務追蹤 |
| 嵌入式系統 | 自定義輕量級追蹤 | 資源受限環境 |

## 總結

函數追蹤是強大的程式分析技術，選擇合適的工具和方法能夠大幅提升開發和除錯效率。從簡單的編譯器插樁到複雜的動態追蹤，每種方法都有其適用場景。關鍵是根據具體需求選擇最合適的解決方案，並在追蹤開銷和資訊價值之間找到平衡。

### 快速決策樹

1. **能否重新編譯？**
   - 是 → 使用 `-finstrument-functions` 或 `-pg`
   - 否 → 使用 GDB/ltrace/strace

2. **需要視覺化？**
   - 是 → uftrace + Chrome tracing 或火焰圖
   - 否 → 簡單文字輸出即可

3. **效能敏感？**
   - 是 → 使用採樣式追蹤（perf）或 eBPF
   - 否 → 完整插樁追蹤

4. **多執行緒程式？**
   - 是 → 確保追蹤工具支援執行緒安全
   - 否 → 任何工具皆可

記住：好的追蹤策略應該是漸進式的，從簡單開始，根據需要逐步增加複雜度。
