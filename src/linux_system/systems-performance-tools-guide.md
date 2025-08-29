# Systems Performance 2/e - 實用工具完整指南

## 📚 書籍簡介
《Systems Performance: Enterprise and the Cloud, 2nd Edition》(2020) 是 Brendan Gregg 的經典系統性能分析著作，涵蓋了現代系統性能優化的完整方法論和工具集。

## 🎯 性能分析方法論

### USE 方法論
- **Utilization (使用率)**: 資源用了多少？
- **Saturation (飽和度)**: 有多少在排隊等待？  
- **Errors (錯誤)**: 有錯誤發生嗎？

### 60秒快速診斷法
```bash
# 60秒內快速了解系統狀態
uptime                  # 系統負載
dmesg | tail           # 系統訊息
vmstat 1               # 虛擬記憶體統計
mpstat -P ALL 1        # CPU統計
pidstat 1              # 進程統計
iostat -xz 1           # I/O統計
free -m                # 記憶體使用
sar -n DEV 1           # 網路設備統計
sar -n TCP,ETCP 1      # TCP統計
top                    # 進程總覽
```

## 🔧 系統層級工具

### 1. 基礎觀察工具

#### **vmstat - 虛擬記憶體統計**
```bash
vmstat 1
# 輸出說明：
# r: 等待CPU的進程數（runnable）
# b: 被阻塞的進程數（blocked）
# free: 空閒記憶體
# si/so: swap in/out
```
💡 **白話說明**：就像看汽車儀表板，一眼就知道系統忙不忙

#### **iostat - I/O 統計**
```bash
iostat -x 1
# 關鍵指標：
# %util: 磁碟忙碌程度（100%表示滿載）
# await: 平均等待時間
# r/s, w/s: 每秒讀寫次數
```
💡 **白話說明**：監控硬碟的"心跳"，看是否有I/O瓶頸

#### **top/htop - 進程監控**
```bash
htop
# 互動式操作：
# F6: 排序
# F4: 過濾
# F9: 殺進程
```
💡 **白話說明**：Linux版的任務管理器，即時查看資源消耗

### 2. 進階診斷工具

#### **perf - Linux 性能分析框架**
```bash
# CPU採樣分析
perf record -F 99 -g ./your_program
perf report

# 即時統計
perf stat ./your_program

# 系統調用追蹤
perf trace ./your_program
```
💡 **白話說明**：像X光機，能看到程式內部的執行熱點

#### **strace/ltrace - 系統調用追蹤**
```bash
# 追蹤系統調用
strace -c ./program    # 統計模式
strace -T ./program    # 顯示時間

# 追蹤函式庫調用
ltrace ./program
```
💡 **白話說明**：偷看程式和系統的"對話記錄"

### 3. BPF 新世代工具

#### **bpftrace - 動態追蹤語言**
```bash
# 追蹤檔案開啟
bpftrace -e 'tracepoint:syscalls:sys_enter_open { 
    printf("%s opened %s\n", comm, str(args->filename)); 
}'

# 追蹤進程創建
bpftrace -e 'tracepoint:sched:sched_process_fork { 
    printf("PID %d created PID %d\n", pid, args->child_pid); 
}'

# 分析系統調用延遲
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { 
    @start[tid] = nsecs; 
} 
tracepoint:raw_syscalls:sys_exit /@start[tid]/ { 
    @ns = hist(nsecs - @start[tid]); delete(@start[tid]); 
}'
```
💡 **白話說明**：在系統裡裝"探針"，想監控什麼就監控什麼

#### **bcc 工具集**
```bash
# TCP 連線生命週期
tcplife

# 檔案 I/O 延遲分析
ext4slower

# 執行緒阻塞分析
offcputime -p PID

# 記憶體分配追蹤
memleak -p PID
```

## 🔥 火焰圖 (Flame Graphs)

### CPU 火焰圖
```bash
# 1. 收集數據（30秒）
perf record -F 99 -ag -- sleep 30

# 2. 生成火焰圖
perf script | stackcollapse-perf.pl | flamegraph.pl > cpu-flame.svg

# 3. 針對特定進程
perf record -F 99 -p PID -g -- sleep 30
```

### Off-CPU 火焰圖
```bash
# 分析程式在等待什麼
bpftrace -e 'kprobe:finish_task_switch { 
    @[kstack, ustack, comm] = count(); 
}' > out.stacks
cat out.stacks | flamegraph.pl > offcpu-flame.svg
```

💡 **白話說明**：火焰圖把執行時間視覺化，寬度代表時間佔比，一眼看出瓶頸

## 💻 C++ 性能分析工具

### 1. Valgrind 套件
```bash
# 記憶體洩漏檢測
valgrind --leak-check=full --show-leak-kinds=all ./cpp_program

# CPU 分析（callgrind）
valgrind --tool=callgrind ./cpp_program
kcachegrind callgrind.out.*  # 視覺化檢視

# 快取分析
valgrind --tool=cachegrind ./cpp_program
```

### 2. Google Performance Tools (gperftools)
```cpp
// 在程式碼中使用
#include <gperftools/profiler.h>

int main() {
    ProfilerStart("cpu_profile.prof");
    // 你的程式碼
    ProfilerStop();
}
```
```bash
# 編譯連結
g++ -o program program.cpp -lprofiler

# 分析結果
pprof --text ./program cpu_profile.prof
pprof --pdf ./program cpu_profile.prof > profile.pdf
```

### 3. AddressSanitizer (ASan)
```bash
# 編譯時啟用
g++ -fsanitize=address -g -O1 program.cpp -o program

# 執行時會自動檢測：
# - 緩衝區溢出
# - Use-after-free
# - 記憶體洩漏
```

### 4. C++ 專用 perf 分析
```bash
# 編譯優化但保留符號
g++ -O2 -g -fno-omit-frame-pointer program.cpp

# 收集性能數據
perf record -g ./program
perf report

# 產生註解的原始碼
perf annotate --stdio
```

## 🦀 Rust 性能分析工具

### 1. Cargo 內建工具
```bash
# 編譯優化版本
cargo build --release

# 執行基準測試
cargo bench

# 使用 flamegraph
cargo install flamegraph
cargo flamegraph --bin your_program
```

### 2. Rust 專用分析工具
```toml
# Cargo.toml 加入依賴
[profile.release]
debug = true  # 保留除錯符號

[dev-dependencies]
criterion = "0.5"  # 基準測試框架
```

```rust
// 使用 criterion 基準測試
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 1,
        1 => 1,
        n => fibonacci(n-1) + fibonacci(n-2),
    }
}

fn bench_fibonacci(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

criterion_group!(benches, bench_fibonacci);
criterion_main!(benches);
```

### 3. Tokio Console (非同步程式)
```toml
# 用於非同步 Rust 程式
[dependencies]
console-subscriber = "0.2"
tokio = { version = "1", features = ["full", "tracing"] }
```

```rust
#[tokio::main]
async fn main() {
    console_subscriber::init();
    // 你的非同步程式碼
}
```

```bash
# 安裝並執行 console
cargo install --locked tokio-console
tokio-console
```

### 4. Miri (記憶體安全檢查)
```bash
# 安裝 Miri
rustup +nightly component add miri

# 執行記憶體安全檢查
cargo +nightly miri run
cargo +nightly miri test
```

## 📊 實戰場景範例

### 場景 1：C++ 程式記憶體洩漏
```bash
# 快速診斷流程
1. valgrind --leak-check=full ./program
2. 如果太慢，使用 AddressSanitizer：
   g++ -fsanitize=address program.cpp && ./a.out
3. 使用 heaptrack 視覺化：
   heaptrack ./program
   heaptrack_gui heaptrack.program.*
```

### 場景 2：Rust 程式效能優化
```bash
# 完整優化流程
1. cargo build --release
2. cargo flamegraph --bin program
3. 檢視火焰圖，找出熱點
4. cargo bench  # 優化前基準
5. 優化程式碼
6. cargo bench  # 優化後對比
```

### 場景 3：高並發服務診斷
```bash
# 系統層面
1. ss -s                    # 查看連線統計
2. netstat -nat | awk '{print $6}' | sort | uniq -c  # 連線狀態分布

# 應用層面（C++）
perf record -g -p `pidof server` -- sleep 30
perf report

# 應用層面（Rust + Tokio）
tokio-console  # 即時查看非同步任務
```

### 場景 4：延遲分析
```bash
# BPF 追蹤系統調用延遲
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @start[tid] = nsecs; }
             tracepoint:syscalls:sys_exit_read /@start[tid]/ {
                 @ms = hist((nsecs - @start[tid]) / 1000000); 
                 delete(@start[tid]);
             }'

# C++ 程式分析
strace -T -p PID  # 顯示每個系統調用的時間

# Rust 程式分析
RUST_LOG=trace cargo run  # 啟用詳細日誌
```

## 🎓 最佳實踐總結

### 通用原則
1. **先測量，別猜測** - 使用工具驗證假設
2. **從全局到局部** - 先看系統整體，再深入細節
3. **建立基準線** - 保存正常狀態的性能數據
4. **持續監控** - 使用 Prometheus + Grafana 等工具

### C++ 優化建議
- 編譯時保留符號：`-g -fno-omit-frame-pointer`
- 使用 PGO (Profile-Guided Optimization)
- 善用 `perf` 和 `valgrind` 工具鏈
- 考慮使用 `jemalloc` 或 `tcmalloc`

### Rust 優化建議
- 使用 `cargo flamegraph` 找熱點
- 善用 `criterion` 做基準測試
- 注意 `Box`、`Arc`、`Rc` 的使用開銷
- 非同步程式使用 `tokio-console` 診斷

### 火焰圖解讀技巧
- **寬度** = 時間佔比
- **高度** = 調用棧深度
- **顏色** = 通常隨機，用於區分
- 找最寬的"平頂山" = 優化目標

## 📚 延伸資源
- [Brendan Gregg's Blog](http://www.brendangregg.com/)
- [Flame Graphs](http://www.brendangregg.com/flamegraphs.html)
- [BPF Performance Tools (書籍)](http://www.brendangregg.com/bpf-performance-tools-book.html)
- [Linux Performance](http://www.brendangregg.com/linuxperf.html)

---

💡 **記住**：性能優化是一門實證科學，永遠要基於數據做決定，而不是直覺！
