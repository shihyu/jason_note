# 現代程式語言的靜態連結策略分析

## 為什麼 Rust、Zig、Go 編譯出來的執行檔比 C/C++ 大？

簡單答案：**預設靜態連結 (Static Linking)**

## 各語言的編譯策略比較

| 語言 | 預設行為 | 執行檔大小 (Hello World) | 特點 |
|------|---------|------------------------|------|
| **C/C++** | 動態連結 | ~16 KB | 依賴系統函式庫 |
| **Go** | 完全靜態 | ~1-2 MB | 包含 runtime、GC |
| **Rust** | 靜態連結 std | ~300-400 KB | 包含 panic handler |
| **Zig** | 靜態連結 | ~10-50 KB | 更精簡的 std |

## 靜態連結的主要原因

### 1. 內建 Runtime 功能

Rust 和 Zig 的執行檔會包含：
- Panic/錯誤處理機制
- Stack unwinding
- 格式化輸出功能
- 記憶體分配器

即使是簡單的 Hello World 也會帶入這些功能。

### 2. 標準函式庫的差異

```bash
# C (動態連結 glibc)
gcc hello.c -o hello    # ~16 KB

# Rust (靜態連結 libstd)
cargo build --release   # ~300-400 KB

# Go (包含完整 runtime)
go build hello.go       # ~1-2 MB
```

### 3. 部署需求的改變

傳統方式（動態連結）：
```bash
./myapp
# 需要系統有：
# - libc.so.6
# - libstdc++.so.6
# - libpthread.so.0
# ...
```

現代方式（靜態連結）：
```bash
./myapp  # 單一檔案，直接執行 ✅
```

## 為什麼選擇靜態連結作為預設？

### 1. 部署極度簡化

```bash
# 單一執行檔，複製即可
scp myapp user@server:/usr/local/bin/

# 不用擔心：
# ❌ 目標系統缺少 libstdc++
# ❌ glibc 版本不相容  
# ❌ 動態函式庫路徑問題
# ❌ Linux 發行版差異
```

### 2. 容器化時代的完美選擇

```dockerfile
# Go/Rust 可以用空映像檔
FROM scratch
COPY myapp /
CMD ["/myapp"]
# 最終 Docker image 只有幾 MB！

# C++ 需要基礎映像檔
FROM ubuntu:22.04
RUN apt-get install -y libstdc++6 ...
COPY myapp /
# image 大了 100+ MB
```

### 3. 避免依賴地獄

動態連結的痛點：
- 不同 Linux 發行版的 glibc 版本衝突
- Windows DLL Hell
- macOS 系統更新破壞相容性
- 版本管理複雜

### 4. 語言設計哲學

- **Go**: "Build once, run anywhere" - 極致的部署簡化
- **Rust**: 零成本抽象 + 可預測行為
- **Zig**: 完全控制，minimal runtime

## 優缺點分析

### ✅ 優點

#### 1. 部署超級簡單
```bash
# 只需一個檔案
./myapp  ✅

# vs C++ 需要確認依賴
ldd myapp
# libstdc++.so.6 => not found ❌
```

#### 2. 跨平台編譯容易
```bash
# Go 交叉編譯
GOOS=linux GOARCH=amd64 go build      # Linux
GOOS=windows GOARCH=amd64 go build    # Windows  
GOOS=darwin GOARCH=arm64 go build     # macOS M1

# Rust 交叉編譯
cargo build --target x86_64-unknown-linux-musl
```

#### 3. 版本管理清晰
- 不會因系統更新 libstdc++ 導致程式壞掉
- 每個執行檔自帶所需函式庫版本
- 行為可預測、可重現

#### 4. 安全隔離
- 避免惡意程式替換系統共享函式庫
- 執行環境完全可控

### ❌ 缺點

#### 1. 執行檔巨大

實際案例：
```bash
du -h myapp

# Go:     2.1 MB (Hello World)
# Rust:   400 KB
# C:      16 KB
```

多個程式時的差異：
```
10 個 Go 程式    = 20 MB
10 個 C 程式     = 160 KB + 共享的 libc (~2 MB)
10 個 Rust 程式  = 4 MB
```

#### 2. 記憶體使用增加

動態連結的優勢：
```
Process A ──┐
            ├──→ [libc.so] (記憶體只載入一份)
Process B ──┘
```

靜態連結的情況：
```
Process A → [內建 libc] (2 MB)
Process B → [內建 libc] (2 MB)  # 重複載入！
```

#### 3. 安全性更新麻煩

動態連結：
```bash
# 修一次函式庫，所有程式受益
apt-get update libc6
# 所有使用 libc 的程式自動更新 ✅
```

靜態連結：
```bash
# 每個程式都要重新編譯部署
./app1  # 包含舊版 OpenSSL (CVE-2024-xxxx) ⚠️
./app2  # 包含舊版 OpenSSL (CVE-2024-xxxx) ⚠️
./app3  # 包含舊版 OpenSSL (CVE-2024-xxxx) ⚠️
# 需要分別重新編譯和部署
```

#### 4. 編譯時間較長
- 需要連結整個標準函式庫
- LTO (Link Time Optimization) 很慢
- 不過 Go 編譯速度仍然很快

## 減少執行檔大小的方法

### Rust 優化

在 `Cargo.toml` 中：
```toml
[profile.release]
opt-level = "z"       # 優化體積而非速度
lto = true            # Link Time Optimization
codegen-units = 1     # 單一編譯單元，更好優化
strip = true          # 自動移除符號表
panic = "abort"       # 不使用 unwinding，減少代碼
```

使用 no_std（極致精簡）：
```rust
#![no_std]
#![no_main]
// 完全不用標準函式庫，可到幾 KB
```

手動 strip：
```bash
cargo build --release
strip target/release/myapp
# 可再減少 ~100 KB
```

### Go 優化

```bash
# 使用 UPX 壓縮（可能影響啟動速度）
go build -ldflags="-s -w" myapp
upx --best myapp

# -s: 移除符號表
# -w: 移除 DWARF 除錯資訊
```

### Zig 優化

Zig 預設就很小，進一步優化：
```bash
zig build-exe -O ReleaseSmall main.zig
```

## Go 的特殊之處

Go 更激進的原因：
```
Go 執行檔包含：
├── 你的代碼
├── 標準函式庫
├── 垃圾回收器 (GC)
├── Goroutine 排程器
├── 完整的 runtime
└── 連 C runtime 都不依賴！
```

優勢：
- 編譯超快（即使靜態連結）
- 部署體驗極佳
- 天生適合微服務架構
- 單一執行檔包含一切

## 實際選擇建議

### 適合靜態連結的場景 (Go/Rust/Zig)

✅ 雲端部署、容器化應用  
✅ 微服務架構  
✅ CLI 工具（如 kubectl, cargo）  
✅ 嵌入式系統  
✅ 需要分發給用戶的軟體  
✅ DevOps 工具  
✅ 無伺服器 (Serverless) 函數

### 適合動態連結的場景 (C/C++)

✅ 系統程式（桌面應用）  
✅ 記憶體極度受限環境  
✅ 大量小程式共存（如系統工具）  
✅ 需要快速安全性更新的場景  
✅ 傳統企業環境  
✅ 與系統深度整合的程式

## 總結

現代語言（Go、Rust、Zig）選擇靜態連結是**以空間換便利性**的策略：

| 犧牲 | 換取 |
|------|------|
| 磁碟空間 (幾 MB) | 部署極度簡化 |
| 記憶體 (重複載入) | 無依賴問題 |
| 更新較麻煩 | 版本完全可控 |
| 編譯時間 | 執行環境可預測 |

### 時代背景的改變

**過去 (1990s-2000s)**
- 磁碟空間貴（MB 級）
- 記憶體貴（幾十 MB）
- 工程師時間便宜
- 👉 動態連結省資源

**現在 (2020s)**
- 磁碟空間便宜（TB 級）
- 記憶體便宜（GB 級）
- 工程師時間很貴
- 雲端/容器化普及
- 👉 靜態連結省時間、減少問題

在雲端時代，**開發和部署效率** > **幾 MB 的空間**，這就是為什麼現代語言都選擇預設靜態連結！

---

## 參考資料

- [Rust Binary Size Optimization](https://github.com/johnthagen/min-sized-rust)
- [Go Executable Size](https://golang.org/doc/faq#Why_is_my_trivial_program_such_a_large_binary)
- [Zig Documentation](https://ziglang.org/documentation/master/)
- [Static vs Dynamic Linking](https://en.wikipedia.org/wiki/Static_library)