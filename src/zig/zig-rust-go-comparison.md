## Zig vs Rust vs Go 深度比較

這三個語言代表了系統程式設計的三種不同哲學：Zig 追求簡潔與控制、Rust 強調安全與正確性、Go 專注於生產力與併發。

> 💡 本文提供配套的程式碼範例專案，涵蓋記憶體管理、併發模型、HTTP 伺服器、跨平台編譯和錯誤處理。
> 詳見: [Zig-Rust-Go-Comparison](./Zig-Rust-Go-Comparison/)

### 設計哲學與記憶體管理

**Zig** 採用手動記憶體管理，沒有垃圾回收也沒有執行時環境。它被視為「更好的 C」，提供顯式控制和可預測性，通過 `defer` 語句簡化資源清理。Zig 的設計強調沒有隱藏的控制流，所有記憶體操作都需要明確指定。[^1][^2][^3]

**程式碼範例**: Zig 使用 `GeneralPurposeAllocator` 和 `defer` 進行記憶體管理：
```zig
var gpa = std.heap.GeneralPurposeAllocator(.{}){};
defer _ = gpa.deinit();  // 自動檢測記憶體洩漏

const allocator = gpa.allocator();
const data = try allocator.alloc(u8, 10);
defer allocator.free(data);  // defer 確保釋放
```

完整範例請參考: [examples/01-memory-management/zig/](./Zig-Rust-Go-Comparison/examples/01-memory-management/zig/main.zig)

**Rust** 透過獨特的所有權系統（ownership）和借用檢查器（borrow checker）在編譯時保證記憶體安全。這套系統能防止資料競爭、緩衝區溢位和釋放後使用等錯誤，但代價是陡峭的學習曲線。許多新手開發者會經歷「與借用檢查器搏鬥」的階段。[^4][^5][^6][^7][^1]

**程式碼範例**: Rust 的所有權系統防止資料競爭：
```rust
let s1 = String::from("Hello");
let s2 = s1;  // 所有權轉移
// println!("{}", s1);  // ❌ 編譯錯誤：s1 已失效

// 使用借用而非轉移所有權
let s3 = String::from("World");
let len = calculate_length(&s3);  // 借用
println!("{}", s3);  // ✓ s3 仍然有效
```

完整範例請參考: [examples/01-memory-management/rust/](./Zig-Rust-Go-Comparison/examples/01-memory-management/rust/src/main.rs)

**Go** 使用自動垃圾回收（GC），採用併發的三色標記清除演算法。Go 的 GC 持續改進，最新版本進一步提升了多核心系統的擴展性。雖然 GC 會帶來短暫的停頓（通常小於 100 微秒），但大幅簡化了開發流程。[^8][^9][^10][^11]

**程式碼範例**: Go 的 GC 自動管理記憶體：
```go
func main() {
    // 自動分配
    data := make([]int, 1000)

    // 無需手動釋放，GC 自動回收
    processData(data)

    // 可查看 GC 統計
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    fmt.Printf("GC 次數: %d\n", m.NumGC)
}
```

完整範例請參考: [examples/01-memory-management/go/](./Zig-Rust-Go-Comparison/examples/01-memory-management/go/main.go)

### 效能表現

> ⚠️ **注意**: 效能測試結果受硬體、負載模式、實作細節影響。以下數據僅供參考。

在高負載 HTTP 基準測試中，**Zig 展現最佳吞吐量**，達到約 118,000 請求/秒，Rust 緊隨其後為 113,000 請求/秒，Go 則約為 70,000 請求/秒。Zig 的記憶體使用也最低，閒置時不到 1 MB，而 Rust 約 25 MB。[^12][^13]

在 CPU 使用效率方面，Go 從一開始就顯示較高的 CPU 使用率和延遲。當負載達到 33,000 請求/秒時，Go 的延遲顯著增加；而 Rust 和 Zig 能維持穩定到更高的負載水準。[^13][^12]

**實作差異影響**:
- **Zig**: 手動 TCP + HTTP 協議實作，最小開銷
- **Rust**: Axum 框架 + Tokio，提供豐富功能
- **Go**: net/http 標準庫，易用性高

我們的簡化 HTTP 伺服器範例可在此查看: [examples/03-http-server/](./Zig-Rust-Go-Comparison/examples/03-http-server/)

### 編譯與跨平台支援

**Zig** 的跨平台編譯能力極為出色。它內建支援所有主要平台的 libc 實作，能在單一機器上為所有目標平台建構執行檔。Zig 甚至能為 Apple Silicon 進行交叉簽名，這是目前其他 C/C++ 編譯器做不到的。[^14][^15]

**實際範例**:
```bash
# 編譯到 Linux x86_64
zig build-exe main.zig -target x86_64-linux

# 編譯到 Windows x86_64
zig build-exe main.zig -target x86_64-windows

# 編譯到 Linux ARM64
zig build-exe main.zig -target aarch64-linux

# 無需安裝額外工具鏈！
```

**Rust** 的跨平台編譯需要透過工具鏈配置，某些相依套件不支援 WebAssembly 或需要額外處理。不過 Rust 擁有強大的建構系統 Cargo，能自動處理相依性管理。[^16][^17][^18]

```bash
# 安裝目標工具鏈
rustup target add x86_64-pc-windows-gnu

# 編譯到目標平台
cargo build --target x86_64-pc-windows-gnu
```

**Go** 的跨平台編譯相對直觀，透過設定 `GOOS` 和 `GOARCH` 環境變數即可。使用 Zig 作為 C 編譯器可以讓 Go 的 CGO 專案輕鬆實現跨平台編譯。[^15]

```bash
# Linux AMD64
GOOS=linux GOARCH=amd64 go build

# Windows AMD64
GOOS=windows GOARCH=amd64 go build

# macOS ARM64
GOOS=darwin GOARCH=arm64 go build
```

跨平台編譯測試腳本: [tests/test_cross_compilation.sh](./Zig-Rust-Go-Comparison/tests/test_cross_compilation.sh)

### 併發模型

**Go** 的併發模型最為成熟且易用。Goroutines 是輕量級執行緒（初始堆疊僅 2KB），配合 channels 提供「通過通訊來共享記憶體」的並行模式。Go 標準函式庫內建豐富的併發原語，如 `sync.WaitGroup`、`sync.Mutex` 等。常見模式包括 worker pools、fan-out/fan-in、pipelines 等。[^19][^20][^21][^22]

**Worker Pool 範例**:
```go
jobs := make(chan int, 100)
results := make(chan int, 100)

// 啟動 workers
for w := 1; w <= 3; w++ {
    go worker(w, jobs, results)
}

// 發送 jobs
for j := 1; j <= 10; j++ {
    jobs <- j
}
close(jobs)
```

完整併發範例: [examples/02-concurrency/go/](./Zig-Rust-Go-Comparison/examples/02-concurrency/go/main.go)

**Rust** 透過 `async/await` 語法和 Tokio 執行時環境提供非同步程式設計。Tokio 提供多執行緒的工作竊取排程器，能以最小開銷處理每秒數十萬個請求。不過非同步 Rust 的學習曲線較陡，需要理解 `Future`、`Pin` 等複雜概念。[^23][^24][^25][^26]

**Async/Await 範例**:
```rust
#[tokio::main]
async fn main() {
    let task1 = tokio::spawn(async_work(1));
    let task2 = tokio::spawn(async_work(2));

    // 等待所有任務
    let _ = tokio::join!(task1, task2);
}

async fn async_work(id: u32) {
    println!("Task {} starting", id);
    tokio::time::sleep(Duration::from_millis(100)).await;
    println!("Task {} done", id);
}
```

完整併發範例: [examples/02-concurrency/rust/](./Zig-Rust-Go-Comparison/examples/02-concurrency/rust/src/main.rs)

**Zig** 提供基本的執行緒和同步原語，但沒有內建高階併發抽象。開發者需要手動管理執行緒同步，這給予更多控制權但也增加了複雜度。[^4]

**Thread + Mutex 範例**:
```zig
var counter: i32 = 0;
var mutex: std.Thread.Mutex = .{};

fn worker() void {
    mutex.lock();
    defer mutex.unlock();
    counter += 1;
}

// 創建執行緒
const thread = try std.Thread.spawn(.{}, worker, .{});
thread.join();
```

完整併發範例: [examples/02-concurrency/zig/](./Zig-Rust-Go-Comparison/examples/02-concurrency/zig/main.zig)

### 錯誤處理機制

三種語言採用不同的錯誤處理哲學：

**Zig - Error Unions**

使用 `error{...}!T` 類型明確標記可能失敗的函數：
```zig
fn divide(a: i32, b: i32) error{DivisionByZero}!i32 {
    if (b == 0) return error.DivisionByZero;
    return @divTrunc(a, b);
}

// 使用 try 傳播錯誤
const result = try divide(10, 2);

// 使用 catch 處理錯誤
const result2 = divide(10, 0) catch |err| {
    std.debug.print("Error: {any}\n", .{err});
    return;
};
```

**Rust - Result<T, E>**

使用 `Result` enum 強制顯式錯誤處理：
```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// 使用 ? 運算符傳播錯誤
let result = divide(10, 2)?;

// 使用 match 或 unwrap_or 處理
let result2 = divide(10, 0).unwrap_or(0);
```

**Go - error interface**

使用 `error` interface 和多返回值：
```go
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 顯式錯誤檢查
result, err := divide(10, 2)
if err != nil {
    log.Fatal(err)
}
```

**對比總結**:
- **Zig**: 編譯期強制處理，明確的錯誤傳播
- **Rust**: 編譯期強制處理，函數式錯誤處理
- **Go**: 運行時檢查，冗長但清晰

完整錯誤處理範例: [examples/05-error-handling/](./Zig-Rust-Go-Comparison/examples/05-error-handling/)

### 生態系統與成熟度

**Rust** 擁有最成熟的生態系統。Crates.io 上有超過數萬個套件，涵蓋網路、遊戲開發、加密、Web 框架等領域。Cargo 提供完整的專案管理、測試、文件生成和發布功能。[^27][^17][^4]

**Go** 的標準函式庫極為豐富，包含 `net/http`、`encoding/json`、`os`、`fmt` 等常用套件。這使得許多專案無需外部相依就能完成。Go 社群活躍，有大量第三方套件支援。[^28][^29]

**Zig** 的生態系統較小但快速成長中。標準函式庫提供基礎功能如記憶體管理、I/O、資料結構、網路和併發原語。由於語言尚未穩定（目前版本 0.x），API 可能會有變動。[^30][^31][^32][^33][^4]

### 學習曲線與開發體驗

**Go** 的學習曲線最平緩。語法簡潔清晰，工具鏈完善（`go build`、`go test`、`go fmt` 等），適合快速開發和團隊協作。許多開發者能在短時間內達到生產力。[^34][^35][^36]

**學習建議**:
- 初學者: 從 [Go by Example](https://gobyexample.com/) 開始
- 本專案範例: 從簡單的錯誤處理開始學習 → [examples/05-error-handling/go/](./Zig-Rust-Go-Comparison/examples/05-error-handling/go/main.go)

**Zig** 的語法類似 C，學習曲線適中。它的 `comptime` 特性提供強大的編譯期元程式設計能力，能在編譯時執行任意程式碼。這讓 Zig 無需引入泛型、巨集等複雜機制就能實現多型。[^37][^38][^39][^30][^4]

**學習建議**:
- 有 C 背景: 可直接從記憶體管理開始 → [examples/01-memory-management/zig/](./Zig-Rust-Go-Comparison/examples/01-memory-management/zig/main.zig)
- 理解 `comptime` 的威力

**Rust** 的學習曲線最陡峭。所有權、生命週期、借用規則需要時間掌握。但經驗豐富的 Rust 開發者表示，一旦理解這些概念，與借用檢查器的「搏鬥」會大幅減少。[^5][^7][^40]

**學習建議**:
- 必讀: [The Rust Book](https://doc.rust-lang.org/book/)
- 本專案範例: 理解所有權基礎 → [examples/01-memory-management/rust/](./Zig-Rust-Go-Comparison/examples/01-memory-management/rust/src/main.rs)
- 進階: Result 錯誤處理 → [examples/05-error-handling/rust/](./Zig-Rust-Go-Comparison/examples/05-error-handling/rust/src/main.rs)

### 產業應用與薪資

根據 2024 年 Stack Overflow 調查，**Zig 開發者的平均年薪最高**，達到 \$103,000，但僅 0.83% 的受訪者精通 Zig。這反映了人才稀缺性和市場需求的增長。[^41][^42]

**Rust 開發者薪資**因領域差異較大，Web3 領域可達 \$148,000-\$225,000，一般系統程式設計約 \$120,000-\$160,000，英國中位數為 £105,000。Rust 在系統程式設計、區塊鏈、雲端基礎設施等領域廣泛應用。[^43][^44][^45][^1]

**Go 開發者薪資**平均約 \$122,000。Go 在雲端服務、微服務架構、DevOps 工具等領域佔據主導地位。[^35][^46][^34]

### 生產環境採用

**Rust** 已被 Mozilla、Amazon、Microsoft、Meta 等科技巨頭廣泛採用。Rust 基金會獲得主要科技公司的支持。[^36]

**Go** 在 Google、Uber、Netflix 等公司的後端系統中扮演關鍵角色。其在雲端原生應用和容器技術（如 Docker、Kubernetes）中的地位無可替代。[^34]

**Zig** 的生產環境採用正在增長，預計未來三年將看到更廣泛的應用。有團隊在面對 Zig vs Rust 選擇時，基於學習曲線、工具鏈體驗和跨平台需求選擇了 Zig。[^47][^48][^36]

### 適用場景建議

**選擇 Zig**：
- ✓ 需要細粒度記憶體控制
- ✓ 跨平台編譯簡便性
- ✓ 類 C 的簡潔性
- ✓ 不需要自動記憶體安全保證

**適合領域**: 嵌入式系統、作業系統開發、遊戲引擎、效能關鍵系統

**實際案例**: [Bun](https://bun.sh/) JavaScript runtime 的部分核心使用 Zig

[^49][^1][^30][^34]

---

**選擇 Rust**：
- ✓ 需要編譯期記憶體安全保證
- ✓ 高效能且安全的併發
- ✓ 成熟生態系統
- ✓ 願意投入時間學習

**適合領域**: 系統程式設計、網路服務、密碼學、WebAssembly、區塊鏈

**實際案例**: Discord、Cloudflare Workers、Figma 後端

[^1][^49][^35][^4]

---

**選擇 Go**：
- ✓ 優先考慮開發速度
- ✓ 團隊協作
- ✓ 網路服務開發
- ✓ 能接受 GC 帶來的些微效能損失

**適合領域**: 微服務、API、雲端基礎設施、CLI 工具、DevOps 工具

**實際案例**: Docker、Kubernetes、Terraform、Prometheus

[^35][^28][^34]

這三個語言各有優勢，選擇取決於專案需求、團隊技能和效能要求。對於追求極致效能和控制的專案，Zig 和 Rust 更適合；對於需要快速迭代和大規模團隊協作的網路服務，Go 是理想選擇。

---

## 附錄：程式碼範例索引

本文檔提供配套的程式碼範例專案，所有範例均可編譯執行並通過測試。

| 主題 | Zig | Rust | Go | 測試腳本 |
|------|-----|------|-----|---------|
| 記憶體管理 | [zig/main.zig](./Zig-Rust-Go-Comparison/examples/01-memory-management/zig/main.zig) | [rust/src/main.rs](./Zig-Rust-Go-Comparison/examples/01-memory-management/rust/src/main.rs) | [go/main.go](./Zig-Rust-Go-Comparison/examples/01-memory-management/go/main.go) | [test_memory_management.sh](./Zig-Rust-Go-Comparison/tests/test_memory_management.sh) |
| 併發模型 | [zig/main.zig](./Zig-Rust-Go-Comparison/examples/02-concurrency/zig/main.zig) | [rust/src/main.rs](./Zig-Rust-Go-Comparison/examples/02-concurrency/rust/src/main.rs) | [go/main.go](./Zig-Rust-Go-Comparison/examples/02-concurrency/go/main.go) | [test_concurrency.sh](./Zig-Rust-Go-Comparison/tests/test_concurrency.sh) |
| HTTP 伺服器 | [zig/main.zig](./Zig-Rust-Go-Comparison/examples/03-http-server/zig/main.zig) | [rust/src/main.rs](./Zig-Rust-Go-Comparison/examples/03-http-server/rust/src/main.rs) | [go/main.go](./Zig-Rust-Go-Comparison/examples/03-http-server/go/main.go) | [test_http_server.sh](./Zig-Rust-Go-Comparison/tests/test_http_server.sh) |
| 跨平台編譯 | [zig/main.zig](./Zig-Rust-Go-Comparison/examples/04-cross-compilation/zig/main.zig) | [rust/src/main.rs](./Zig-Rust-Go-Comparison/examples/04-cross-compilation/rust/src/main.rs) | [go/main.go](./Zig-Rust-Go-Comparison/examples/04-cross-compilation/go/main.go) | [test_cross_compilation.sh](./Zig-Rust-Go-Comparison/tests/test_cross_compilation.sh) |
| 錯誤處理 | [zig/main.zig](./Zig-Rust-Go-Comparison/examples/05-error-handling/zig/main.zig) | [rust/src/main.rs](./Zig-Rust-Go-Comparison/examples/05-error-handling/rust/src/main.rs) | [go/main.go](./Zig-Rust-Go-Comparison/examples/05-error-handling/go/main.go) | [test_error_handling.sh](./Zig-Rust-Go-Comparison/tests/test_error_handling.sh) |

**執行所有測試**:
```bash
cd Zig-Rust-Go-Comparison
./tests/test_memory_management.sh
./tests/test_concurrency.sh
./tests/test_http_server.sh
./tests/test_cross_compilation.sh
./tests/test_error_handling.sh
```
