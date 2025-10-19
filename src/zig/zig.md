# Zig

Zig 是一個通用程式語言和工具鏈，專注於穩健性、最佳化和可維護性。

---

## 簡介

### Zig 是什麼？

Zig 是一門現代系統程式語言，由 Andrew Kelley 於 2015 年開始開發。它定位為「更好的 C」，提供手動記憶體管理的同時，大幅改善開發體驗和安全性。

**核心目標：**
- ⚡ 最佳化執行速度
- 🛡️ 防止錯誤（compile-time guarantees）
- 🔧 簡單易懂的程式碼
- 🌍 跨平台編譯支援

---

### 核心特性

```zig
// 簡潔、明確的語法
const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, {s}!\n", .{"Zig"});
}
```

**關鍵特性：**

1. **無隱藏控制流** - 所有控制流都明確可見
2. **無隱藏記憶體分配** - 必須明確使用 allocator
3. **無預處理器** - 用 `comptime` 取代巨集
4. **無異常** - 使用 Error Union (`!`) 處理錯誤
5. **手動記憶體管理** - 完全控制，無 GC
6. **編譯期執行** - 強大的 `comptime` 功能

---

### 設計理念

```zig
// Zig 的設計哲學：簡單勝於複雜

// ✅ 明確的記憶體分配
const allocator = std.heap.page_allocator;
const memory = try allocator.alloc(u8, 100);
defer allocator.free(memory);

// ✅ 明確的錯誤處理
fn readFile(path: []const u8) ![]u8 {
    // 錯誤會被強制處理
    return error.FileNotFound;
}

// ✅ 編譯期執行（取代複雜的泛型系統）
fn max(comptime T: type) type {
    return struct {
        pub fn get(a: T, b: T) T {
            return if (a > b) a else b;
        }
    };
}
```

**設計原則：**
- 只有一種明確的做事方法
- 與 C 無縫互操作
- 編譯期執行優於複雜的型別系統
- 實用性優於純粹性

---

### 與其他語言比較

| 特性 | Zig | C | C++ | Rust |
|------|-----|---|-----|------|
| 記憶體安全 | 編譯期檢查 | ❌ | ❌ | ✅ Borrow Checker |
| 學習曲線 | 中等 | 簡單 | 陡峭 | 陡峭 |
| 編譯速度 | 快 | 最快 | 慢 | 慢 |
| C 互操作 | 原生支援 | - | 良好 | FFI |
| 錯誤處理 | Error Union | 返回碼 | 異常 | Result<T, E> |
| 泛型 | Comptime | ❌ | Template | Trait |
| 包管理 | 內建 | ❌ | ❌ | Cargo |
| 跨平台編譯 | 內建 | 需工具鏈 | 需工具鏈 | Rustup |

**Zig vs C：**
```zig
// Zig: 現代化的 C，保留手動控制
const allocator = std.heap.page_allocator;
const data = try allocator.alloc(i32, 10);
defer allocator.free(data);
```

```c
// C: 傳統手動管理
int* data = malloc(10 * sizeof(int));
// 容易忘記 free，造成記憶體洩漏
free(data);
```

**Zig vs Rust：**
- Zig：簡單直接，手動記憶體管理，編譯快
- Rust：複雜型別系統，自動記憶體安全（Borrow Checker），編譯慢

**Zig vs C++：**
- Zig：無隱藏功能，無異常，無運算子重載
- C++：功能豐富但複雜，有歷史包袱

---

## 主要特色

### 1. 無隱藏控制流

```zig
// ✅ 沒有異常，所有錯誤都明確處理
fn divide(a: i32, b: i32) !i32 {
    if (b == 0) return error.DivisionByZero;
    return @divTrunc(a, b);
}

// 使用時必須處理錯誤
const result = divide(10, 0) catch |err| {
    std.debug.print("Error: {}\n", .{err});
    return;
};
```

### 2. 無隱式記憶體分配

```zig
// ❌ 不會像 C++ 一樣隱式分配記憶體
// std::vector<int> v = {1, 2, 3}; // C++ 隱式 heap allocation

// ✅ Zig 必須明確指定 allocator
const allocator = std.heap.page_allocator;
var list = std.ArrayList(i32).init(allocator);
defer list.deinit();

try list.append(1);
try list.append(2);
```

### 3. Comptime（編譯期執行）

```zig
// 在編譯期執行程式碼
fn fibonacci(comptime n: i32) i32 {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// 編譯期計算，零執行期成本
const fib10 = comptime fibonacci(10); // 55

// 編譯期生成型別
fn Vec(comptime T: type, comptime size: usize) type {
    return struct {
        data: [size]T,

        pub fn init() @This() {
            return .{ .data = undefined };
        }
    };
}

const Vec3f = Vec(f32, 3); // 編譯期生成型別
```

### 4. 錯誤處理（Error Union）

```zig
// 定義錯誤集合
const FileError = error{
    NotFound,
    PermissionDenied,
    OutOfMemory,
};

// 函數返回值或錯誤
fn openFile(path: []const u8) FileError!File {
    // ...
    return error.NotFound;
}

// 錯誤處理方式
const file = openFile("data.txt") catch |err| {
    std.debug.print("Failed: {}\n", .{err});
    return;
};

// 或者用 try（錯誤會向上傳播）
const file2 = try openFile("data.txt");
```

### 5. 跨平台編譯

```bash
# 一個命令編譯到任何平台
zig build-exe main.zig -target x86_64-windows
zig build-exe main.zig -target aarch64-linux
zig build-exe main.zig -target wasm32-freestanding

# Zig 也是 C/C++ 編譯器
zig cc main.c -o main
zig c++ main.cpp -o main
```

### 6. C 互操作性

```zig
// 直接使用 C 標頭檔
const c = @cImport({
    @cInclude("stdio.h");
    @cInclude("stdlib.h");
});

pub fn main() void {
    c.printf("Hello from C!\n");
}

// 匯出函數給 C 使用
export fn add(a: i32, b: i32) i32 {
    return a + b;
}
```

---

## 學習資源

### 官方資源

- **官方網站**: [https://ziglang.org/](https://ziglang.org/)
- **語言文檔**: [https://ziglang.org/documentation/master/](https://ziglang.org/documentation/master/)
- **標準庫文檔**: [https://ziglang.org/documentation/master/std/](https://ziglang.org/documentation/master/std/)
- **學習指南**: [https://ziglang.org/learn/](https://ziglang.org/learn/)

### 線上教學

- **Zig Learn**: [https://ziglearn.org/](https://ziglearn.org/) - 互動式教學
- **Zig by Example**: [https://zig-by-example.com/](https://zig-by-example.com/)
- **Ziglings**: [https://github.com/ratfactor/ziglings](https://github.com/ratfactor/ziglings) - 透過練習學 Zig

### 書籍

- **Zig Language Reference** (官方文檔)
- 社群正在撰寫更多書籍中

### 影片資源

- **Andrew Kelley's Talks** - Zig 作者的演講
  - "The Road to Zig 1.0"
  - "Zig: A programming language designed for robustness"
- **YouTube Zig 頻道**: 搜尋 "Zig programming"

### 社群資源

- **GitHub**: [https://github.com/ziglang/zig](https://github.com/ziglang/zig)
- **Discord**: Zig 官方 Discord 社群
- **Reddit**: [r/Zig](https://www.reddit.com/r/Zig/)
- **中文資源**:
  - Zig 中文社區正在成長中
  - 翻譯文檔陸續推出

### 工具與生態系統

- **包管理器**: 內建於 Zig (zig build system)
- **編輯器支援**:
  - VS Code: `zig-language-server`
  - Vim/Neovim: `zls` (Zig Language Server)
  - JetBrains: Zig 插件
- **測試框架**: 內建 `zig test`
- **性能分析**: 支援多種 profiler

### 實用套件

- **網路**: `zig-network`
- **HTTP**: `http.zig`
- **JSON**: 標準庫內建
- **圖形**: `mach-glfw`, `raylib-zig`

---

## 相關文章

- [為什麼 Zig 編譯器程式碼那麼小？](zig_compiler_size.md)
- [Zig vs C 語言完整比較指南](zig_vs_c_complete_guide.md)

---

## 快速開始

### 安裝

```bash
# Linux/macOS
curl https://ziglang.org/download/0.11.0/zig-linux-x86_64-0.11.0.tar.xz | tar -xJ
export PATH=$PATH:$PWD/zig-linux-x86_64-0.11.0

# 或使用套件管理器
# Ubuntu/Debian
sudo apt install zig

# macOS
brew install zig
```

### Hello World

```zig
// hello.zig
const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, World!\n", .{});
}
```

```bash
# 編譯並執行
zig run hello.zig

# 或編譯成執行檔
zig build-exe hello.zig
./hello
```

### 建立專案

```bash
# 初始化專案
zig init-exe
# 或
zig init-lib

# 編譯專案
zig build

# 執行測試
zig build test

# 執行程式
zig build run
```

---

## 總結

Zig 是一門**簡單、快速、可靠**的系統程式語言：

✅ **優點：**
- 簡潔明確，學習曲線平緩
- 編譯速度快
- 優秀的 C 互操作性
- 強大的編譯期執行能力
- 內建跨平台編譯

⚠️ **注意：**
- 語言仍在發展中（未到 1.0）
- 生態系統較小
- 手動記憶體管理需要謹慎

**適合場景：**
- 系統程式開發
- 嵌入式開發
- 高性能應用
- 取代 C/C++ 的現代化選擇
- 需要與 C 程式碼互操作的專案

---

*Zig：一門讓系統程式設計變得簡單的語言。*
