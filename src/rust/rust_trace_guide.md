# Rust 程式追蹤與除錯完整指南

## 1. 快速追蹤命令

### 基本追蹤
```bash
# 使用 RUST_BACKTRACE 追蹤 panic
RUST_BACKTRACE=1 cargo run

# 完整追蹤
RUST_BACKTRACE=full cargo run

# 使用 RUST_LOG 追蹤日誌
RUST_LOG=debug cargo run
RUST_LOG=trace cargo run  # 更詳細

# 使用 GDB 除錯 Rust
rust-gdb target/debug/program

# 使用 LLDB 除錯 Rust
rust-lldb target/debug/program
```

## 2. 完整範例專案結構

```
rust-trace-demo/
├── Cargo.toml
├── src/
│   ├── main.rs
│   └── lib.rs
├── examples/
│   └── trace_demo.rs
└── tests/
    └── integration_test.rs
```

## 3. Cargo.toml 設定

```toml
[package]
name = "rust-trace-demo"
version = "0.1.0"
edition = "2021"

[dependencies]
# 日誌追蹤
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "fmt", "json"] }
tracing-appender = "0.2"

# 日誌
log = "0.4"
env_logger = "0.10"

# 效能分析
pprof = { version = "0.13", features = ["flamegraph", "criterion"] }
criterion = { version = "0.5", features = ["html_reports"] }

# 記憶體分析
dhat = "0.3"

# 序列化
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# 錯誤處理
anyhow = "1.0"
thiserror = "1.0"

# 測試
mockall = "0.11"
proptest = "1.0"

[dev-dependencies]
# 基準測試
criterion = "0.5"

[profile.release]
debug = true  # 保留除錯符號

[profile.dev]
opt-level = 0
debug = true

# 效能分析專用 profile
[profile.profiling]
inherits = "release"
debug = true
```

## 4. 主程式 - 各種追蹤技術示範 (src/main.rs)

```rust
use std::time::Instant;
use tracing::{debug, error, info, instrument, trace, warn, Level};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

// 函式追蹤宏
macro_rules! trace_fn {
    ($func_name:expr) => {
        println!("→ Entering: {}", $func_name);
        let _guard = FunctionGuard::new($func_name);
    };
}

struct FunctionGuard {
    name: &'static str,
    start: Instant,
}

impl FunctionGuard {
    fn new(name: &'static str) -> Self {
        Self {
            name,
            start: Instant::now(),
        }
    }
}

impl Drop for FunctionGuard {
    fn drop(&mut self) {
        println!(
            "← Exiting: {} (took {:?})",
            self.name,
            self.start.elapsed()
        );
    }
}

// 使用 tracing 的 instrument 屬性
#[instrument]
fn fibonacci(n: u32) -> u64 {
    trace!("Computing fibonacci({})", n);
    
    if n <= 1 {
        n as u64
    } else {
        fibonacci(n - 1) + fibonacci(n - 2)
    }
}

#[instrument(level = "debug", ret)]
fn calculate(x: i32, y: i32) -> i32 {
    debug!("Starting calculation");
    let result = add(x, y) * multiply(x, y);
    info!("Calculation complete");
    result
}

#[instrument]
fn add(a: i32, b: i32) -> i32 {
    trace!("Adding {} + {}", a, b);
    a + b
}

#[instrument]
fn multiply(a: i32, b: i32) -> i32 {
    trace!("Multiplying {} * {}", a, b);
    a * b
}

// 記憶體追蹤範例
fn memory_operations() {
    trace_fn!("memory_operations");
    
    let mut vec = Vec::new();
    for i in 0..1000 {
        vec.push(i);
        if i % 100 == 0 {
            debug!("Vector size: {}", vec.len());
        }
    }
    
    info!("Final vector capacity: {}", vec.capacity());
}

// 錯誤追蹤範例
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    
    #[error("Calculation error")]
    CalculationError,
}

fn may_fail(input: i32) -> Result<i32, AppError> {
    trace_fn!("may_fail");
    
    if input < 0 {
        error!("Received negative input: {}", input);
        return Err(AppError::InvalidInput(format!("negative value: {}", input)));
    }
    
    Ok(input * 2)
}

// 效能追蹤
fn performance_test() {
    let start = Instant::now();
    info!("Starting performance test");
    
    let _result = fibonacci(30);
    
    let duration = start.elapsed();
    warn!("Performance test took: {:?}", duration);
}

fn main() {
    // 初始化 tracing
    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(EnvFilter::from_default_env()
            .add_directive(Level::TRACE.into()))
        .init();
    
    info!("=== Rust Trace Demo Started ===");
    
    // 1. 函式追蹤
    println!("\n--- Function Tracing ---");
    let result = calculate(5, 3);
    println!("Result: {}", result);
    
    // 2. 遞迴追蹤
    println!("\n--- Recursive Tracing ---");
    let fib = fibonacci(5);
    println!("Fibonacci(5) = {}", fib);
    
    // 3. 記憶體操作追蹤
    println!("\n--- Memory Operations ---");
    memory_operations();
    
    // 4. 錯誤追蹤
    println!("\n--- Error Handling ---");
    match may_fail(-5) {
        Ok(val) => println!("Success: {}", val),
        Err(e) => error!("Error occurred: {}", e),
    }
    
    // 5. 效能測試
    println!("\n--- Performance Test ---");
    performance_test();
    
    info!("=== Demo Completed ===");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
    
    #[test]
    fn test_fibonacci() {
        assert_eq!(fibonacci(10), 55);
    }
}
```

## 5. 進階追蹤工具整合 (examples/advanced_trace.rs)

```rust
use criterion::{black_box, Criterion};
use pprof::ProfilerGuard;
use std::fs::File;
use tracing::{instrument, Level};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

// CPU 效能分析
fn cpu_profiling() {
    #[cfg(not(target_os = "windows"))]
    {
        let guard = ProfilerGuard::new(100).unwrap();
        
        // 執行要分析的程式碼
        expensive_computation();
        
        // 產生火焰圖
        if let Ok(report) = guard.report().build() {
            let file = File::create("flamegraph.svg").unwrap();
            report.flamegraph(&file).unwrap();
            println!("Flamegraph saved to flamegraph.svg");
        }
    }
}

fn expensive_computation() {
    let mut sum = 0;
    for i in 0..1_000_000 {
        sum += i;
    }
    println!("Sum: {}", sum);
}

// 記憶體分析
#[global_allocator]
static ALLOC: dhat::Alloc = dhat::Alloc;

fn memory_profiling() {
    let _profiler = dhat::Profiler::new_heap();
    
    // 分配記憶體
    let mut vecs = Vec::new();
    for _ in 0..100 {
        let mut v = Vec::with_capacity(1000);
        for i in 0..1000 {
            v.push(i);
        }
        vecs.push(v);
    }
    
    println!("Allocated {} vectors", vecs.len());
}

fn main() {
    // 設定追蹤
    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(EnvFilter::from_default_env())
        .init();
    
    println!("=== Advanced Tracing Demo ===");
    
    // CPU 分析
    println!("\n--- CPU Profiling ---");
    cpu_profiling();
    
    // 記憶體分析
    println!("\n--- Memory Profiling ---");
    memory_profiling();
}
```

## 6. 自動化追蹤腳本 (trace.sh)

```bash
#!/bin/bash
# trace.sh - Rust 追蹤自動化腳本

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 基本追蹤
basic_trace() {
    echo -e "${YELLOW}=== Basic Trace ===${NC}"
    RUST_BACKTRACE=1 RUST_LOG=trace cargo run
}

# 2. 火焰圖生成
flame_graph() {
    echo -e "${YELLOW}=== Generating Flamegraph ===${NC}"
    
    # 安裝 flamegraph
    cargo install flamegraph
    
    # 生成火焰圖
    cargo flamegraph --root -- --example advanced_trace
    
    echo -e "${GREEN}Flamegraph saved to flamegraph.svg${NC}"
}

# 3. 測試覆蓋率
coverage() {
    echo -e "${YELLOW}=== Test Coverage ===${NC}"
    
    # 安裝 tarpaulin
    cargo install cargo-tarpaulin
    
    # 執行覆蓋率測試
    cargo tarpaulin --out Html --output-dir coverage
    
    echo -e "${GREEN}Coverage report saved to coverage/index.html${NC}"
}

# 4. 記憶體檢查 (使用 Valgrind)
memory_check() {
    echo -e "${YELLOW}=== Memory Check ===${NC}"
    
    cargo build
    valgrind --leak-check=full --show-leak-kinds=all \
             target/debug/rust-trace-demo
}

# 5. Miri 檢查 (未定義行為檢測)
miri_check() {
    echo -e "${YELLOW}=== Miri Check ===${NC}"
    
    # 安裝 miri
    rustup +nightly component add miri
    
    # 執行 miri
    cargo +nightly miri run
}

# 6. 效能測試
benchmark() {
    echo -e "${YELLOW}=== Benchmark ===${NC}"
    cargo bench
}

# 7. GDB 除錯
gdb_debug() {
    echo -e "${YELLOW}=== GDB Debug ===${NC}"
    
    cargo build
    rust-gdb -ex "break main" \
             -ex "run" \
             -ex "bt" \
             -ex "continue" \
             -ex "quit" \
             target/debug/rust-trace-demo
}

# 8. LLDB 除錯
lldb_debug() {
    echo -e "${YELLOW}=== LLDB Debug ===${NC}"
    
    cargo build
    rust-lldb -o "breakpoint set --name main" \
              -o "run" \
              -o "bt" \
              -o "continue" \
              -o "quit" \
              target/debug/rust-trace-demo
}

# 9. Clippy 檢查
clippy_check() {
    echo -e "${YELLOW}=== Clippy Analysis ===${NC}"
    cargo clippy -- -W clippy::all
}

# 10. 安全審計
security_audit() {
    echo -e "${YELLOW}=== Security Audit ===${NC}"
    
    # 安裝 cargo-audit
    cargo install cargo-audit
    
    # 執行審計
    cargo audit
}

# 主選單
show_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════╗"
    echo -e "║      Rust 追蹤工具選單             ║"
    echo -e "╚════════════════════════════════════╝${NC}"
    echo
    echo "1) 基本追蹤 (RUST_LOG + RUST_BACKTRACE)"
    echo "2) 火焰圖生成"
    echo "3) 測試覆蓋率"
    echo "4) 記憶體檢查 (Valgrind)"
    echo "5) Miri 檢查"
    echo "6) 效能測試"
    echo "7) GDB 除錯"
    echo "8) LLDB 除錯"
    echo "9) Clippy 檢查"
    echo "10) 安全審計"
    echo "11) 執行所有"
    echo "0) 退出"
    echo
}

# 主程式
main() {
    if [ "$1" == "--all" ]; then
        basic_trace
        flame_graph
        coverage
        benchmark
        clippy_check
        security_audit
    else
        while true; do
            show_menu
            read -p "請選擇 (0-11): " choice
            
            case $choice in
                1) basic_trace ;;
                2) flame_graph ;;
                3) coverage ;;
                4) memory_check ;;
                5) miri_check ;;
                6) benchmark ;;
                7) gdb_debug ;;
                8) lldb_debug ;;
                9) clippy_check ;;
                10) security_audit ;;
                11) 
                    basic_trace
                    flame_graph
                    coverage
                    benchmark
                    clippy_check
                    security_audit
                    ;;
                0) 
                    echo -e "${GREEN}再見！${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}無效選擇${NC}"
                    ;;
            esac
            
            read -p "按 Enter 繼續..."
        done
    fi
}

main "$@"
```

## 7. 基準測試 (benches/benchmark.rs)

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 | 1 => n,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn fibonacci_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

criterion_group!(benches, fibonacci_benchmark);
criterion_main!(benches);
```

## 8. 整合測試 (tests/integration_test.rs)

```rust
use rust_trace_demo::*;

#[test]
fn test_integration() {
    // 設定測試環境的追蹤
    let _ = tracing_subscriber::fmt()
        .with_test_writer()
        .try_init();
    
    // 執行測試
    let result = some_function();
    assert_eq!(result, expected_value);
}
```

## 9. VS Code 設定 (.vscode/launch.json)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "lldb",
            "request": "launch",
            "name": "Debug Rust",
            "cargo": {
                "args": [
                    "build",
                    "--bin=rust-trace-demo",
                    "--package=rust-trace-demo"
                ],
                "filter": {
                    "name": "rust-trace-demo",
                    "kind": "bin"
                }
            },
            "args": [],
            "cwd": "${workspaceFolder}",
            "env": {
                "RUST_BACKTRACE": "full",
                "RUST_LOG": "trace"
            }
        }
    ]
}
```

## 10. GitHub Actions CI/CD (.github/workflows/rust.yml)

```yaml
name: Rust CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  CARGO_TERM_COLOR: always

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        profile: minimal
        toolchain: stable
        override: true
        components: rustfmt, clippy
    
    - name: Build
      run: cargo build --verbose
    
    - name: Run tests
      run: RUST_BACKTRACE=1 cargo test --verbose
    
    - name: Run clippy
      run: cargo clippy -- -D warnings
    
    - name: Check formatting
      run: cargo fmt -- --check
    
    - name: Run benchmarks
      run: cargo bench
    
    - name: Generate test coverage
      run: |
        cargo install cargo-tarpaulin
        cargo tarpaulin --out Xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 11. 實用命令速查

```bash
# 快速追蹤
RUST_LOG=trace cargo run                    # 詳細日誌
RUST_BACKTRACE=full cargo run              # 完整錯誤追蹤

# 除錯
rust-gdb target/debug/program              # GDB 除錯
rust-lldb target/debug/program             # LLDB 除錯

# 效能分析
cargo flamegraph                           # 火焰圖
cargo bench                                 # 基準測試
perf record -g cargo run                   # Linux perf

# 記憶體分析
valgrind --leak-check=full cargo run       # Valgrind
cargo +nightly miri run                    # Miri

# 測試與覆蓋率
cargo test -- --nocapture                  # 顯示 println!
cargo tarpaulin                            # 測試覆蓋率

# 程式碼品質
cargo clippy                               # Lint 檢查
cargo fmt                                  # 格式化
cargo audit                                # 安全審計
```

## 12. 最佳實踐

### 開發階段
```toml
# Cargo.toml
[profile.dev]
opt-level = 0
debug = true
overflow-checks = true
```

### 追蹤設定
```rust
// 使用條件編譯
#[cfg(debug_assertions)]
println!("Debug: {}", value);

// 使用 debug_assert!
debug_assert!(condition, "Error message");

// 使用 tracing
#[instrument(skip(large_data))]
fn process(large_data: &[u8]) -> Result<()> {
    // ...
}
```

### 錯誤處理
```rust
use anyhow::{Context, Result};

fn operation() -> Result<()> {
    something()
        .context("Failed to do something")?;
    Ok(())
}
```

## 總結

Rust 的追蹤工具比 C/C++ 更現代化：

1. **內建工具**：`RUST_BACKTRACE`, `RUST_LOG`
2. **生態系統**：`tracing`, `log`, `env_logger`
3. **效能分析**：`flamegraph`, `criterion`, `perf`
4. **記憶體安全**：`miri`, `valgrind`, `dhat`
5. **程式碼品質**：`clippy`, `rustfmt`, `cargo-audit`

最大優勢是 Rust 的所有追蹤工具都整合在 Cargo 生態系統中，使用起來非常方便！