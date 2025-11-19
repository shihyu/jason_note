# Rust 靜態與動態編譯完整指南

## 目錄
1. [基本概念](#基本概念)
2. [動態連結](#動態連結)
3. [靜態編譯](#靜態編譯)
4. [跨平臺編譯](#跨平臺編譯)
5. [實戰範例](#實戰範例)
6. [疑難排解](#疑難排解)
7. [最佳實踐](#最佳實踐)

## 基本概念

### 動態連結 vs 靜態連結

| 特性 | 動態連結 | 靜態連結 |
|------|---------|---------|
| **檔案大小** | 較小 | 較大 |
| **執行速度** | 啟動稍慢 | 啟動較快 |
| **記憶體使用** | 共享函式庫，較省記憶體 | 每個程式獨立，較耗記憶體 |
| **相依性** | 需要系統有對應函式庫 | 無外部相依 |
| **可攜性** | 較差 | 極佳 |
| **更新函式庫** | 可獨立更新 | 需重新編譯 |

### 查看執行檔資訊

```bash
# 檢查檔案類型
file ./myapp

# 查看動態連結庫依賴
ldd ./myapp

# 查看符號表
nm ./myapp

# 查看 ELF 資訊
readelf -d ./myapp

# 查看檔案大小
ls -lh ./myapp
```

## 動態連結

### 預設編譯（動態連結）

```bash
# 標準編譯（預設使用 glibc）
cargo build --release

# 產生的執行檔依賴系統函式庫
ldd target/release/myapp
# 輸出範例：
#   linux-vdso.so.1
#   libgcc_s.so.1
#   libpthread.so.0
#   libc.so.6
```

### 常見問題

#### GLIBC 版本不相容
```bash
# 錯誤訊息
./myapp: /lib64/libc.so.6: version `GLIBC_2.34' not found

# 解決方法：
# 1. 在目標系統上編譯
# 2. 使用較舊的系統編譯
# 3. 改用靜態編譯
```

#### 缺少動態函式庫
```bash
# 錯誤訊息
error while loading shared libraries: libssl.so.1.1: cannot open shared object file

# 解決方法：
# Ubuntu/Debian
sudo apt-get install libssl1.1

# CentOS/RHEL
sudo yum install openssl-libs
```

## 靜態編譯

### 方法 1：使用 musl（推薦）

```bash
# 安裝 musl target
rustup target add x86_64-unknown-linux-musl

# Ubuntu/Debian 安裝 musl 工具
sudo apt-get install musl-tools

# macOS 安裝 musl cross
brew install FiloSottile/musl-cross/musl-cross

# 編譯
cargo build --release --target x86_64-unknown-linux-musl

# 驗證是否為靜態連結
ldd target/x86_64-unknown-linux-musl/release/myapp
# 應顯示：not a dynamic executable
```

### 方法 2：靜態連結 glibc（部分靜態）

```bash
# 在 .cargo/config.toml 添加
[target.x86_64-unknown-linux-gnu]
rustflags = [
    "-C", "target-feature=+crt-static",
    "-C", "link-arg=-static"
]

# 編譯
cargo build --release
```

### 方法 3：使用 cargo-zigbuild

```bash
# 安裝 zigbuild
cargo install cargo-zigbuild

# 安裝 zig
brew install zig  # macOS
# 或參考 https://ziglang.org/download/

# 編譯
cargo zigbuild --release --target x86_64-unknown-linux-musl
```

## 跨平臺編譯

### 使用 cross 工具

```bash
# 安裝 cross
cargo install cross

# 編譯不同目標
cross build --target x86_64-unknown-linux-musl --release
cross build --target aarch64-unknown-linux-musl --release
cross build --target armv7-unknown-linux-musleabihf --release
```

### Docker 多階段建構

```dockerfile
# Dockerfile.static
# 階段 1：建構
FROM rust:1.75-alpine as builder

# 安裝必要的建構工具
RUN apk add --no-cache musl-dev

WORKDIR /usr/src/app
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# 靜態編譯
RUN cargo build --release --target x86_64-unknown-linux-musl

# 階段 2：最小執行環境
FROM scratch

COPY --from=builder /usr/src/app/target/x86_64-unknown-linux-musl/release/myapp /myapp

ENTRYPOINT ["/myapp"]
```

### GitHub Actions CI/CD

```yaml
name: Build Static Binary

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
        target: x86_64-unknown-linux-musl
        override: true
    
    - name: Install musl-tools
      run: sudo apt-get install -y musl-tools
    
    - name: Build
      run: cargo build --release --target x86_64-unknown-linux-musl
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: binary
        path: target/x86_64-unknown-linux-musl/release/myapp
```

## 實戰範例

### 範例 1：Web 服務靜態編譯

```toml
# Cargo.toml
[package]
name = "web-service"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

[profile.release]
lto = true          # 連結時間優化
codegen-units = 1   # 單一編譯單元
strip = true        # 移除符號
opt-level = "z"     # 優化大小
```

```bash
# 編譯命令
cargo build --release --target x86_64-unknown-linux-musl

# 使用 UPX 進一步壓縮（可選）
upx --best --lzma target/x86_64-unknown-linux-musl/release/web-service
```

### 範例 2：CLI 工具跨平臺發布

```bash
#!/bin/bash
# build-all.sh

TARGETS=(
    "x86_64-unknown-linux-musl"
    "aarch64-unknown-linux-musl"
    "x86_64-pc-windows-gnu"
    "x86_64-apple-darwin"
)

for target in "${TARGETS[@]}"; do
    echo "Building for $target..."
    cross build --release --target "$target"
done

# 打包
mkdir -p dist
for target in "${TARGETS[@]}"; do
    cp "target/$target/release/myapp" "dist/myapp-$target" 2>/dev/null || \
    cp "target/$target/release/myapp.exe" "dist/myapp-$target.exe" 2>/dev/null
done
```

### 範例 3：處理 OpenSSL 依賴

```toml
# Cargo.toml
[dependencies]
# 使用 rustls 取代 OpenSSL
reqwest = { version = "0.11", features = ["rustls-tls"], default-features = false }

# 或使用 vendored OpenSSL
# openssl = { version = "0.10", features = ["vendored"] }
```

## 疑難排解

### 問題 1：musl 編譯失敗

```bash
# 錯誤：linking with `cc` failed
# 解決：
export CC_x86_64_unknown_linux_musl=musl-gcc
export CARGO_TARGET_X86_64_UNKNOWN_LINUX_MUSL_LINKER=musl-gcc
cargo build --release --target x86_64-unknown-linux-musl
```

### 問題 2：找不到 pkg-config

```bash
# 錯誤：Could not find `pkg-config`
# 解決：
# Ubuntu/Debian
sudo apt-get install pkg-config

# macOS
brew install pkg-config
```

### 問題 3：C 函式庫依賴

```toml
# 使用純 Rust 替代品
[dependencies]
# 替換 OpenSSL
ring = "0.16"        # 加密
rustls = "0.21"      # TLS

# 替換 libpq
tokio-postgres = "0.7"

# 替換 sqlite3
rusqlite = { version = "0.29", features = ["bundled"] }
```

### 問題 4：執行檔過大

```toml
# Cargo.toml 優化設定
[profile.release]
lto = true
codegen-units = 1
panic = "abort"
strip = true
opt-level = "z"  # 或 "s"
```

```bash
# 額外壓縮
strip target/release/myapp
upx --best target/release/myapp
```

## 最佳實踐

### 1. 開發流程

```yaml
# docker-compose.yml
version: '3'
services:
  dev:
    image: rust:latest
    volumes:
      - .:/app
    working_dir: /app
    command: cargo watch -x run
  
  build-static:
    image: rust:alpine
    volumes:
      - .:/app
    working_dir: /app
    command: cargo build --release --target x86_64-unknown-linux-musl
```

### 2. 測試矩陣

```bash
#!/bin/bash
# test-compatibility.sh

DISTROS=(
    "ubuntu:20.04"
    "ubuntu:22.04"
    "debian:11"
    "centos:7"
    "alpine:latest"
)

for distro in "${DISTROS[@]}"; do
    echo "Testing on $distro..."
    docker run --rm -v $(pwd):/app "$distro" /app/myapp --version
done
```

### 3. 版本相容性檢查

```rust
// build.rs
fn main() {
    // 檢查 glibc 版本
    println!("cargo:rerun-if-changed=build.rs");
    
    #[cfg(target_env = "gnu")]
    {
        println!("cargo:rustc-link-arg=-Wl,--wrap=memcpy");
        println!("cargo:rustc-link-arg=-Wl,--wrap=__memcpy_chk");
    }
}
```

### 4. 選擇策略

| 場景 | 建議方案 |
|------|---------|
| **單一目標系統** | 動態連結 |
| **多個 Linux 發行版** | musl 靜態編譯 |
| **嵌入式系統** | musl + strip + upx |
| **容器化部署** | 動態連結 + FROM scratch |
| **桌面應用分發** | 靜態編譯或 AppImage |
| **CI/CD 產物** | 靜態編譯 |

## 效能比較

```bash
# 測試腳本
#!/bin/bash

echo "動態連結版本："
time ./myapp-dynamic

echo "靜態連結版本："
time ./myapp-static

echo "檔案大小比較："
ls -lh myapp-*

echo "記憶體使用："
/usr/bin/time -v ./myapp-dynamic 2>&1 | grep "Maximum resident"
/usr/bin/time -v ./myapp-static 2>&1 | grep "Maximum resident"
```

## 跨發行版執行的效能分析

### 靜態編譯跨發行版效能影響

**結論：Ubuntu 編譯的靜態執行檔在 CentOS 運行，一般不會變慢**

#### 理論分析

| 效能面向 | 影響程度 | 說明 |
|---------|---------|------|
| **啟動時間** | ✅ 可能更快 5-15% | 無需動態連結載入 |
| **執行效能** | ✅ 幾乎無差異 < 1% | CPU 指令執行相同 |
| **記憶體使用** | ⚠️ 稍高 | 函式庫內嵌在執行檔 |
| **CPU 快取** | ✅ 可能更好 | 程式碼局部性更佳 |

#### 效能優勢來源

1. **無動態連結開銷**
   - 省略載入共享函式庫時間
   - 省略符號解析過程
   - 省略地址重定位

2. **更好的編譯器優化**
   ```toml
   [profile.release]
   lto = "fat"           # Link Time Optimization
   codegen-units = 1     # 允許跨模組優化
   ```

3. **更好的程式碼局部性**
   - 減少記憶體分頁錯誤
   - 提高 CPU 快取命中率

#### 實測數據範例

```bash
# 測試環境：計算密集型任務
# Ubuntu 20.04 編譯 → CentOS 7 執行
```

| 版本 | 啟動時間 (100次平均) | 執行時間 | 記憶體峰值 |
|------|-------------------|----------|-----------|
| 動態連結 (原生) | 12ms | 1.52s | 45MB |
| 靜態連結 (musl) | 10ms | 1.54s | 48MB |
| 靜態連結 (glibc) | 10ms | 1.51s | 47MB |

### musl vs glibc 效能比較

#### 效能差異場景

| 場景 | musl | glibc | 建議 |
|------|------|-------|------|
| **一般應用** | 基準 | +0-2% | musl (可攜性佳) |
| **記憶體分配密集** | 基準 | +10-20% | glibc |
| **多執行緒** | 基準 | +5-15% | glibc |
| **數學運算** | 基準 | +0-1% | 無明顯差異 |
| **網路 I/O** | 基準 | +0-2% | 無明顯差異 |

#### 選擇建議

```rust
// 記憶體分配密集型 - 建議用 glibc
let mut data = Vec::new();
for _ in 0..10_000_000 {
    data.push(vec![0u8; 1024]);
}

// 一般 Web 服務 - musl 即可
async fn handle_request(req: Request) -> Response {
    // 業務邏輯
}
```

### 效能測試與監控

#### 基準測試工具

```bash
# 1. hyperfine - 命令列程式基準測試
hyperfine --warmup 3 './app-static' './app-dynamic'

# 2. perf - Linux 效能分析
perf stat -r 10 ./app-static
perf record ./app-static
perf report

# 3. flamegraph - 火焰圖分析
cargo install flamegraph
cargo flamegraph --release
```

#### Criterion 基準測試

```toml
# Cargo.toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_benchmark"
harness = false
```

```rust
// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 1,
        1 => 1,
        n => fibonacci(n-1) + fibonacci(n-2),
    }
}

fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
```

### 跨平臺優化策略

#### CPU 指令集優化

```bash
# 保守策略 - 最大相容性
RUSTFLAGS="-C target-cpu=x86-64" cargo build --release

# 平衡策略 - 2013年後的 CPU
RUSTFLAGS="-C target-cpu=x86-64-v2" cargo build --release

# 現代策略 - 2015年後的 CPU (AVX2)
RUSTFLAGS="-C target-cpu=x86-64-v3" cargo build --release

# 激進策略 - 只針對編譯機器
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

#### 條件編譯優化

```rust
// 根據目標平臺優化
#[cfg(target_os = "linux")]
fn platform_specific_optimization() {
    // Linux 特定優化
}

#[cfg(target_arch = "x86_64")]
fn arch_specific_optimization() {
    // x86_64 特定優化
}

// 執行時檢測 CPU 功能
fn main() {
    if is_x86_feature_detected!("avx2") {
        // 使用 AVX2 優化版本
    } else {
        // 使用通用版本
    }
}
```

### 實務決策指南

#### 何時使用靜態編譯

✅ **適合場景**：
- 需要跨多個 Linux 發行版
- 部署環境不可控
- 容器 FROM scratch 最小化映像
- 嵌入式系統
- CLI 工具分發

⚠️ **需謹慎評估**：
- 極度效能敏感的應用
- 大量記憶體分配的應用
- 需要熱更新函式庫

❌ **不建議場景**：
- 只在單一受控環境執行
- 需要動態載入插件

#### 效能檢查清單

- [ ] 使用 release 編譯模式
- [ ] 啟用 LTO 優化
- [ ] 設定適當的 codegen-units
- [ ] 選擇合適的 target-cpu
- [ ] 進行實際環境基準測試
- [ ] 監控生產環境效能指標

## 總結

- **動態連結**：適合受控環境、容器部署
- **靜態連結**：適合分發、跨發行版、嵌入式
- **musl**：最佳跨平臺相容性，一般應用效能損失 < 5%
- **跨發行版效能**：靜態編譯幾乎無效能損失，某些情況還更快
- **優化**：LTO + strip + UPX 可大幅減少檔案大小
- **測試**：務必在目標環境測試

記住：
1. 「在最舊的目標系統上編譯，在最新的系統上執行」通常是最安全的策略
2. 跨發行版執行的效能影響微乎其微，優先考慮可攜性和部署便利性
3. 真實效能問題通常來自演算法和架構，而非編譯方式