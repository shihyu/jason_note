# 程式分析工具完整指南 - 多語言版

## 目錄
- [C/C++ 分析工具](#cc-分析工具)
- [Python 分析工具](#python-分析工具)
- [Java 分析工具](#java-分析工具)
- [Go 分析工具](#go-分析工具)
- [Rust 分析工具](#rust-分析工具)
- [JavaScript/Node.js 分析工具](#javascriptnodejs-分析工具)
- [.NET/C# 分析工具](#netc-分析工具)
- [跨語言通用工具](#跨語言通用工具)
- [視覺化工具](#視覺化工具)

---

## C/C++ 分析工具

### 記憶體分析

#### Valgrind (Linux/macOS)
```bash
valgrind --leak-check=full --show-leak-kinds=all ./program
valgrind --tool=massif ./program  # heap profiling
```

#### AddressSanitizer (ASan)
```bash
g++ -fsanitize=address -g program.cpp
clang++ -fsanitize=address -g program.cpp
```

#### Memory Sanitizer (MSan)
```bash
clang++ -fsanitize=memory -fPIE -pie -g program.cpp
```

#### Dr. Memory (跨平台)
```bash
drmemory -- ./program
```

### 效能分析

#### perf (Linux)
```bash
perf record -g ./program
perf report
perf stat ./program
```

#### gprof
```bash
g++ -pg program.cpp -o program
./program
gprof program gmon.out > analysis.txt
```

#### Intel VTune Profiler
- CPU Hotspots
- Memory Access
- Threading Analysis
- Microarchitecture Analysis

#### gperftools
```bash
LD_PRELOAD=/usr/lib/libprofiler.so CPUPROFILE=prof.out ./program
google-pprof --pdf program prof.out > profile.pdf
```

---

## Python 分析工具

### 記憶體分析

#### memory_profiler
```python
# 安裝: pip install memory-profiler
# 使用裝飾器
@profile
def my_func():
    pass

# 執行
python -m memory_profiler script.py
```

#### tracemalloc (內建)
```python
import tracemalloc
tracemalloc.start()
# ... code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
```

#### objgraph
```python
# 視覺化物件引用
import objgraph
objgraph.show_most_common_types()
objgraph.show_refs(obj, filename='refs.png')
```

#### pympler
```python
from pympler import tracker
tr = tracker.SummaryTracker()
tr.print_diff()
```

### 效能分析

#### cProfile (內建)
```python
python -m cProfile -s cumulative script.py
python -m cProfile -o output.prof script.py
```

#### line_profiler
```python
# 安裝: pip install line_profiler
@profile
def slow_function():
    pass

# 執行
kernprof -l -v script.py
```

#### py-spy
```bash
# 不需修改程式碼的 profiler
py-spy record -o profile.svg -- python script.py
py-spy top -- python script.py
py-spy dump --pid $PID
```

#### Pyflame (已停止維護)
```bash
pyflame -s 3600 -r 0.01 -o profile.svg $PID
```

#### Austin
```bash
austin python script.py
austin -i 100 python script.py  # 100 微秒採樣間隔
```

#### Scalene
```bash
# 高效能 CPU+GPU+記憶體 profiler
scalene script.py
```

---

## Java 分析工具

### 記憶體分析

#### Eclipse Memory Analyzer (MAT)
- Heap dump 分析
- Memory leak 偵測
- Dominator tree 分析

#### jmap (JDK 內建)
```bash
jmap -heap $PID
jmap -dump:format=b,file=heap.bin $PID
```

#### jhat (JDK 內建)
```bash
jhat heap.bin
```

#### VisualVM
- GUI 工具
- Heap/Thread dump
- Memory/CPU profiling

### 效能分析

#### JProfiler
- 商業工具
- CPU/Memory/Thread profiling
- Database/Web 請求分析

#### YourKit Java Profiler
- 商業工具
- 低開銷
- 生產環境可用

#### Java Flight Recorder (JFR)
```bash
# JDK 11+ 免費
java -XX:StartFlightRecording=duration=60s,filename=recording.jfr MyApp
jcmd $PID JFR.start duration=60s filename=recording.jfr
```

#### async-profiler
```bash
# 低開銷的採樣 profiler
./profiler.sh -d 30 -f flamegraph.html $PID
```

#### jstack (JDK 內建)
```bash
jstack $PID > thread_dump.txt
```

---

## Go 分析工具

### 內建 pprof

#### CPU Profiling
```go
import _ "net/http/pprof"
go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof -http=:8080 profile.pb.gz
```

#### Memory Profiling
```bash
go tool pprof http://localhost:6060/debug/pprof/heap
go tool pprof -alloc_space profile.pb.gz
```

#### Goroutine Analysis
```bash
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

### trace
```go
import "runtime/trace"
trace.Start(os.Stderr)
defer trace.Stop()
```

```bash
go tool trace trace.out
```

### go-torch (已整合到 pprof)
```bash
go-torch -u http://localhost:6060/debug/pprof/profile
```

### goleak
```go
// Goroutine leak 檢測
defer goleak.VerifyNone(t)
```

---

## Rust 分析工具

### 記憶體分析

#### Valgrind
```bash
cargo build --release
valgrind --leak-check=full target/release/program
```

#### heaptrack
```bash
heaptrack target/release/program
heaptrack_gui heaptrack.program.*.gz
```

#### dhat
```rust
// Rust 的 heap profiler
#[global_allocator]
static ALLOC: dhat::Alloc = dhat::Alloc;
```

### 效能分析

#### cargo-flamegraph
```bash
cargo install flamegraph
cargo flamegraph
```

#### perf + flamegraph
```bash
perf record --call-graph=dwarf target/release/program
perf script | flamegraph.pl > flame.svg
```

#### criterion
```rust
// Benchmark 框架
use criterion::{black_box, criterion_group, criterion_main, Criterion};
```

#### pprof-rs
```rust
// CPU/Memory profiling
use pprof::protos::Message;
```

#### cargo-profiling
```bash
cargo install cargo-profiling
cargo profiling callgrind
cargo profiling cachegrind
```

---

## JavaScript/Node.js 分析工具

### 記憶體分析

#### Chrome DevTools
- Heap Snapshot
- Allocation Timeline
- Memory Profiler

#### heapdump
```javascript
const heapdump = require('heapdump');
heapdump.writeSnapshot((err, filename) => {
    console.log('Heap dump written to', filename);
});
```

#### memwatch-next
```javascript
const memwatch = require('memwatch-next');
memwatch.on('leak', (info) => {
    console.error('Memory leak detected:', info);
});
```

### 效能分析

#### Node.js 內建 profiler
```bash
node --prof app.js
node --prof-process isolate-*.log > processed.txt
```

#### clinic.js
```bash
npm install -g clinic
clinic doctor -- node app.js
clinic flame -- node app.js
clinic bubbleprof -- node app.js
```

#### 0x
```bash
npm install -g 0x
0x app.js
```

#### Chrome DevTools
```bash
node --inspect app.js
node --inspect-brk app.js
```

---

## .NET/C# 分析工具

### 記憶體分析

#### dotMemory (JetBrains)
- Memory snapshots
- Memory traffic 分析
- 自動 leak 偵測

#### PerfView
```bash
PerfView collect /MaxCollectSec:30 MyApp.exe
PerfView HeapDump MyApp.exe
```

#### Visual Studio Diagnostic Tools
- 整合在 IDE
- Memory Usage
- CPU Usage

### 效能分析

#### BenchmarkDotNet
```csharp
[Benchmark]
public void MyMethod() { }
```

#### dotTrace (JetBrains)
- Performance profiler
- Timeline profiling
- SQL query 分析

#### Application Insights
- 生產環境監控
- 自動效能追蹤

---

## 跨語言通用工具

### 系統層級分析

#### DTrace (macOS/Solaris/BSD)
```bash
sudo dtrace -n 'syscall:::entry { @[execname] = count(); }'
```

#### SystemTap (Linux)
```bash
stap -e 'probe timer.s(1) { print("Hello\n") }'
```

#### eBPF/bpftrace (Linux)
```bash
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[comm] = count(); }'
```

#### strace/ltrace (Linux)
```bash
strace -c ./program
ltrace -c ./program
```

#### Process Monitor (Windows)
- GUI 工具
- File/Registry/Network 活動

### APM (Application Performance Monitoring)

#### New Relic
- 支援多語言
- 自動儀表化
- 分散式追蹤

#### Datadog APM
- 全棧監控
- 自動追蹤
- 即時分析

#### AppDynamics
- 企業級 APM
- 業務交易追蹤
- AI 根因分析

#### Elastic APM
- 開源方案
- 整合 ELK Stack
- 分散式追蹤

---

## 視覺化工具

### 火焰圖 (Flame Graphs)

#### FlameGraph
```bash
git clone https://github.com/brendangregg/FlameGraph
perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > flame.svg
```

#### Speedscope
- Web-based viewer
- 支援多種格式
- https://www.speedscope.app/

### 通用視覺化

#### Grafana + Prometheus
- 時序資料視覺化
- 監控 Dashboard

#### kcachegrind/qcachegrind
```bash
# Callgrind 資料視覺化
kcachegrind callgrind.out.*
```

#### Google Perftools
```bash
google-pprof --web program profile.pb.gz
```

---

## 最佳實踐矩陣

| 語言 | 開發時期 | 測試時期 | 生產環境 |
|------|----------|----------|----------|
| **C/C++** | ASan + UBSan | Valgrind + perf | gperftools |
| **Python** | line_profiler | memory_profiler + cProfile | py-spy |
| **Java** | VisualVM | JProfiler | JFR + async-profiler |
| **Go** | pprof + race | pprof + trace | pprof (低採樣率) |
| **Rust** | cargo flamegraph | valgrind + criterion | perf |
| **Node.js** | Chrome DevTools | clinic.js | APM tools |
| **.NET** | VS Diagnostics | dotMemory + dotTrace | PerfView + App Insights |

---

## 選擇指南

### 依問題類型選擇

**Memory Leak**
- C/C++: Valgrind, ASan
- Python: tracemalloc, memory_profiler
- Java: MAT, VisualVM
- Go: pprof heap
- JavaScript: Chrome DevTools

**CPU Hotspot**
- C/C++: perf, VTune
- Python: py-spy, cProfile
- Java: async-profiler, JProfiler
- Go: pprof profile
- Rust: flamegraph

**Concurrency Issues**
- C/C++: ThreadSanitizer
- Java: jstack, thread dumps
- Go: race detector, trace
- .NET: Concurrency Visualizer

### 依環境選擇

**開發環境**
- 使用整合工具 (IDE profilers)
- 可接受高開銷工具

**CI/CD**
- 自動化工具
- 靜態分析
- Benchmark 套件

**生產環境**
- 低開銷工具
- APM 解決方案
- 採樣式 profiler

---

## 參考資源

- [Brendan Gregg's Performance Tools](http://www.brendangregg.com/linuxperf.html)
- [Julia Evans' Profiling Zines](https://wizardzines.com/)
- [Awesome Performance Tools](https://github.com/pditommaso/awesome-performance)
- [Google Performance Tools](https://github.com/gperftools/gperftools)
- [Linux Performance](http://www.brendangregg.com/linuxperf.html)