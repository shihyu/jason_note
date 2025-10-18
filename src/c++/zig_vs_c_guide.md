# Zig vs C 語言完整比較指南

## 目錄
1. [簡介](#簡介)
2. [語法比較](#語法比較)
3. [特性比較](#特性比較)
4. [Zig 優勢詳解](#zig-優勢詳解)
5. [記憶體管理](#記憶體管理)
6. [錯誤處理](#錯誤處理)
7. [Ubuntu 安裝指南](#ubuntu-安裝指南)
8. [Hello World 完整範例](#hello-world-完整範例)

---

## 簡介

**Zig** 是一個現代的系統程式語言，目標是成為「更好的 C」。它保留了 C 的簡潔性和性能，同時增加了現代語言的安全性和便利性。

**設計理念：**
- 沒有隱藏的控制流
- 沒有隱藏的記憶體分配
- 沒有預處理器
- 編譯時程式設計能力強大

---

## 語法比較

### 變數宣告

```c
// C 語言
int x = 10;
const int y = 20;
float pi = 3.14;
```

```zig
// Zig 語言
var x: i32 = 10;      // 可變變數
const y: i32 = 20;    // 不可變常數
const pi: f32 = 3.14; // 浮點數
```

### 函數定義

```c
// C 語言
int add(int a, int b) {
    return a + b;
}

void print_hello() {
    printf("Hello\n");
}
```

```zig
// Zig 語言
fn add(a: i32, b: i32) i32 {
    return a + b;
}

fn printHello() void {
    std.debug.print("Hello\n", .{});
}
```

### 結構體

```c
// C 語言
struct Point {
    int x;
    int y;
};

struct Point p = {10, 20};
p.x = 30;
```

```zig
// Zig 語言
const Point = struct {
    x: i32,
    y: i32,
};

var p = Point{ .x = 10, .y = 20 };
p.x = 30;
```

### 陣列

```c
// C 語言
int arr[5] = {1, 2, 3, 4, 5};
int len = sizeof(arr) / sizeof(arr[0]);  // 容易出錯
```

```zig
// Zig 語言
const arr = [_]i32{1, 2, 3, 4, 5};
const len = arr.len;  // 內建長度屬性
```

### 指標

```c
// C 語言
int x = 10;
int *ptr = &x;
*ptr = 20;

int *null_ptr = NULL;
```

```zig
// Zig 語言
var x: i32 = 10;
var ptr: *i32 = &x;
ptr.* = 20;

var null_ptr: ?*i32 = null;  // 可選指標
```

### 條件判斷

```c
// C 語言
if (x > 0) {
    printf("positive\n");
} else if (x < 0) {
    printf("negative\n");
} else {
    printf("zero\n");
}
```

```zig
// Zig 語言
if (x > 0) {
    std.debug.print("positive\n", .{});
} else if (x < 0) {
    std.debug.print("negative\n", .{});
} else {
    std.debug.print("zero\n", .{});
}
```

### 迴圈

```c
// C 語言
for (int i = 0; i < 10; i++) {
    printf("%d\n", i);
}

while (condition) {
    // ...
}
```

```zig
// Zig 語言
for (0..10) |i| {
    std.debug.print("{}\n", .{i});
}

while (condition) {
    // ...
}
```

### Switch 語句

```c
// C 語言
switch (x) {
    case 1:
        printf("one\n");
        break;  // 需要 break
    case 2:
        printf("two\n");
        break;
    default:
        printf("other\n");
}
```

```zig
// Zig 語言
switch (x) {
    1 => std.debug.print("one\n", .{}),
    2 => std.debug.print("two\n", .{}),
    else => std.debug.print("other\n", .{}),
}  // 不需要 break，不會 fall-through
```

---

## 特性比較

| 特性 | C 語言 | Zig 語言 |
|------|--------|----------|
| **預處理器** | 有 (#define, #ifdef) | 無，用 comptime 取代 |
| **標頭檔** | 需要 .h 檔案 | 不需要，直接 import |
| **記憶體安全** | 無檢查 | Debug 模式有運行時檢查 |
| **空指標檢查** | 無 | 可選類型 (?*T) |
| **錯誤處理** | errno 或返回值 | 內建錯誤類型 (!) |
| **泛型** | 無（用宏模擬） | 編譯時泛型 (comptime) |
| **包管理** | 無官方工具 | 內建包管理 |
| **跨平台編譯** | 需要額外工具鏈 | 內建支援 |
| **未定義行為** | 很多 UB | 編譯時/運行時檢查 |
| **整數溢位** | 未定義 | 可檢測或環繞 |
| **測試框架** | 需要外部工具 | 內建測試 |
| **LLVM IR** | 無 | 可生成和操作 |

---

## Zig 優勢詳解

### 1. 沒有隱藏的記憶體分配

**C/C++ 的隱藏分配：**
```cpp
// C++ - 隱藏的分配
std::vector<int> vec;
vec.push_back(42);  // 內部自動 malloc，你看不到

std::string str = "Hello";
str += " World";  // 又一次隱藏的分配
```

**Zig 的顯式分配：**
```zig
// Zig - 所有分配都需要明確的 allocator
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    // 必須明確傳入 allocator
    var list = std.ArrayList(i32).init(allocator);
    defer list.deinit();
    try list.append(42);  // 你知道這裡可能分配記憶體

    // 字串處理也要明確
    const text = try std.fmt.allocPrint(allocator, "Hello {s}", .{"World"});
    defer allocator.free(text);
}
```

**好處：**
- 記憶體使用清晰可見
- 可以選擇不同的分配策略（arena、pool、fixed buffer）
- 容易追蹤和調試記憶體問題
- 適合嵌入式和即時系統

### 2. 編譯時程式設計 (comptime)

**C 語言的限制：**
```c
// C - 需要用宏
#define MAX(a, b) ((a) > (b) ? (a) : (b))  // 可能多次求值

// 或使用內聯函數，但無法編譯時計算
```

**Zig 的 comptime：**
```zig
// 編譯時計算
fn fibonacci(comptime n: u32) u32 {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

const fib_10 = fibonacci(10);  // 在編譯時計算出 55

// 編譯時泛型
fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}

const result1 = max(i32, 10, 20);
const result2 = max(f64, 3.14, 2.71);
```

### 3. 內建錯誤處理

**C 語言：**
```c
// C - 多種錯誤處理方式，不統一
FILE* file = fopen("test.txt", "r");
if (file == NULL) {
    perror("Error opening file");
    return -1;
}

// 或使用 errno
int result = some_function();
if (result < 0) {
    fprintf(stderr, "Error: %s\n", strerror(errno));
}
```

**Zig 語言：**
```zig
// Zig - 統一的錯誤處理
const std = @import("std");

const MyError = error{
    FileNotFound,
    PermissionDenied,
};

fn openFile(path: []const u8) !std.fs.File {
    return std.fs.cwd().openFile(path, .{}) catch |err| {
        return err;
    };
}

pub fn main() !void {
    const file = try openFile("test.txt");
    defer file.close();
    
    // 或使用 catch 自訂處理
    const file2 = openFile("test.txt") catch |err| {
        std.debug.print("Error: {}\n", .{err});
        return err;
    };
}
```

### 4. defer 和 errdefer

**C 語言的清理問題：**
```c
// C - 容易遺漏清理
void process() {
    FILE* f1 = fopen("file1.txt", "r");
    if (!f1) return;
    
    char* buffer = malloc(1024);
    if (!buffer) {
        fclose(f1);  // 容易忘記
        return;
    }
    
    FILE* f2 = fopen("file2.txt", "r");
    if (!f2) {
        free(buffer);  // 要記得清理
        fclose(f1);    // 要記得關閉
        return;
    }
    
    // ... 處理
    
    fclose(f2);
    free(buffer);
    fclose(f1);
}
```

**Zig 的 defer：**
```zig
// Zig - 自動清理，不會遺漏
fn process() !void {
    const f1 = try std.fs.cwd().openFile("file1.txt", .{});
    defer f1.close();  // 保證執行
    
    const buffer = try allocator.alloc(u8, 1024);
    defer allocator.free(buffer);
    
    const f2 = try std.fs.cwd().openFile("file2.txt", .{});
    defer f2.close();
    
    // ... 處理
    
    // defer 自動按相反順序清理：f2 -> buffer -> f1
}
```

**defer 執行規則：**
- 在當前作用域結束時執行
- 執行順序：後進先出 (LIFO)
- 即使有 error return 也會執行

**errdefer：**
```zig
fn createResources() !void {
    const r1 = try allocateResource1();
    errdefer freeResource1(r1);  // 只在錯誤時執行
    
    const r2 = try allocateResource2();  // 如果這裡失敗
    errdefer freeResource2(r2);
    
    // 如果成功，errdefer 不執行
    // 如果失敗，自動清理已分配的資源
}
```

### 5. 可選類型 (Optional Types)

**C 語言的空指標問題：**
```c
// C - 空指標容易造成崩潰
int* find_value(int key) {
    // ...
    return NULL;  // 可能返回 NULL
}

int* result = find_value(42);
*result = 10;  // 💥 如果 result 是 NULL，程式崩潰
```

**Zig 的可選類型：**
```zig
// Zig - 強制檢查 null
fn findValue(key: i32) ?*i32 {
    // ...
    return null;
}

const result = findValue(42);
if (result) |value| {
    value.* = 10;  // 安全，已經解包
} else {
    std.debug.print("Not found\n", .{});
}

// 或使用 orelse
const value = findValue(42) orelse return error.NotFound;
```

### 6. 更精確的整數類型

**C 語言：**
```c
// C - 平台相依
int x;        // 可能是 16/32/64 位元
long y;       // 可能是 32/64 位元
size_t z;     // 平台相依

// 需要 stdint.h
int32_t a;
uint64_t b;
```

**Zig 語言：**
```zig
// Zig - 明確且一致
const x: i32 = 0;   // 32 位元有符號整數
const y: u64 = 0;   // 64 位元無符號整數
const z: i8 = 0;    // 8 位元有符號整數
const w: u1 = 0;    // 1 位元（bool）

// 甚至支援任意位元寬度
const a: i7 = 0;    // 7 位元整數
const b: u24 = 0;   // 24 位元整數
```

### 7. 內建測試

**C 語言：**
```c
// C - 需要外部測試框架（如 CUnit, Check）
#include <assert.h>

void test_add() {
    assert(add(2, 3) == 5);
}

int main() {
    test_add();
    return 0;
}
```

**Zig 語言：**
```zig
// Zig - 內建測試
const std = @import("std");

fn add(a: i32, b: i32) i32 {
    return a + b;
}

test "basic addition" {
    try std.testing.expect(add(2, 3) == 5);
    try std.testing.expectEqual(@as(i32, 10), add(7, 3));
}

test "negative numbers" {
    try std.testing.expect(add(-5, 3) == -2);
}

// 執行: zig test myfile.zig
```

### 8. C 互操作性

**Zig 可以直接使用 C 程式庫：**
```zig
// 直接引入 C 標頭檔
const c = @cImport({
    @cInclude("stdio.h");
    @cInclude("stdlib.h");
});

pub fn main() void {
    c.printf("Hello from C!\n");
    
    const ptr = c.malloc(100);
    defer c.free(ptr);
}

// 也可以匯出給 C 使用
export fn zigAdd(a: i32, b: i32) i32 {
    return a + b;
}
```

### 9. 跨平台編譯

**C 語言：**
```bash
# C - 需要安裝不同平台的工具鏈
sudo apt install gcc-mingw-w64  # Windows
sudo apt install gcc-arm-linux-gnueabihf  # ARM
```

**Zig 語言：**
```bash
# Zig - 內建跨平台編譯
zig build-exe main.zig -target x86_64-windows
zig build-exe main.zig -target x86_64-linux
zig build-exe main.zig -target aarch64-macos
zig build-exe main.zig -target wasm32-freestanding

# 支援超過 30 個目標平台
```

### 10. 更安全的預設行為

| 行為 | C 語言 | Zig 語言 |
|------|--------|----------|
| 整數溢位 | 未定義行為 | Debug: panic, Release: 可選 |
| 陣列越界 | 未定義行為 | Debug: panic, Release: 可選 |
| 空指標解引用 | 未定義行為 | 編譯錯誤（可選類型） |
| 未初始化變數 | 未定義行為 | 編譯錯誤 |
| Switch 未處理 | 警告 | 編譯錯誤（需要 else） |

---

## 記憶體管理

### C 語言的記憶體管理

```c
#include <stdlib.h>
#include <string.h>

void example() {
    // 分配
    int* arr = (int*)malloc(10 * sizeof(int));
    if (!arr) {
        // 處理錯誤
        return;
    }
    
    // 使用
    for (int i = 0; i < 10; i++) {
        arr[i] = i;
    }
    
    // 重新分配
    int* new_arr = (int*)realloc(arr, 20 * sizeof(int));
    if (!new_arr) {
        free(arr);
        return;
    }
    arr = new_arr;
    
    // 釋放
    free(arr);
}
```

### Zig 的記憶體管理

```zig
const std = @import("std");

fn example() !void {
    // 建立 allocator
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    // 分配
    const arr = try allocator.alloc(i32, 10);
    defer allocator.free(arr);
    
    // 使用
    for (arr, 0..) |*item, i| {
        item.* = @intCast(i);
    }
    
    // 重新分配
    const new_arr = try allocator.realloc(arr, 20);
    defer allocator.free(new_arr);
}
```

### Zig 的不同 Allocator

```zig
const std = @import("std");

pub fn main() !void {
    // 1. GeneralPurposeAllocator - 通用分配器，有安全檢查
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    
    // 2. ArenaAllocator - 一次性釋放所有
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();  // 一次釋放全部
    const arena_allocator = arena.allocator();
    
    const item1 = try arena_allocator.create(i32);
    const item2 = try arena_allocator.create(i32);
    // 不需要逐個 free
    
    // 3. FixedBufferAllocator - 固定緩衝區（嵌入式）
    var buffer: [1024]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    const fba_allocator = fba.allocator();
    
    // 4. page_allocator - 直接從 OS
    const page_mem = try std.heap.page_allocator.alloc(u8, 4096);
    defer std.heap.page_allocator.free(page_mem);
}
```

---

## 錯誤處理

### 完整的錯誤處理範例

```zig
const std = @import("std");

// 定義錯誤集合
const FileError = error{
    FileNotFound,
    PermissionDenied,
    OutOfMemory,
};

// 函數可能返回錯誤
fn readConfig(path: []const u8) ![]u8 {
    const file = try std.fs.cwd().openFile(path, .{});
    defer file.close();
    
    const size = (try file.stat()).size;
    const allocator = std.heap.page_allocator;
    
    const content = try allocator.alloc(u8, size);
    errdefer allocator.free(content);  // 錯誤時釋放
    
    _ = try file.readAll(content);
    return content;
}

pub fn main() !void {
    // 方法 1: 使用 try（錯誤會向上傳遞）
    const config = try readConfig("config.txt");
    defer std.heap.page_allocator.free(config);
    
    // 方法 2: 使用 catch（自訂錯誤處理）
    const config2 = readConfig("config.txt") catch |err| {
        std.debug.print("Failed to read config: {}\n", .{err});
        return;
    };
    defer std.heap.page_allocator.free(config2);
    
    // 方法 3: 使用 if
    if (readConfig("config.txt")) |config3| {
        defer std.heap.page_allocator.free(config3);
        std.debug.print("Success!\n", .{});
    } else |err| {
        std.debug.print("Error: {}\n", .{err});
    }
}
```

---

## Ubuntu 安裝指南

### 方法 1: 下載官方二進位檔（推薦）

```bash
# 1. 下載最新版本
cd ~/Downloads
wget https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz

# 2. 解壓縮
tar -xf zig-linux-x86_64-0.13.0.tar.xz

# 3. 移動到系統目錄
sudo mv zig-linux-x86_64-0.13.0 /opt/zig

# 4. 建立符號連結
sudo ln -s /opt/zig/zig /usr/local/bin/zig

# 5. 驗證安裝
zig version
```

### 方法 2: 使用 Snap

```bash
# 安裝
sudo snap install zig --classic --beta

# 驗證
zig version
```

### 方法 3: 從原始碼編譯

```bash
# 安裝依賴
sudo apt update
sudo apt install -y git cmake llvm-14 clang-14 lld-14

# 下載原始碼
git clone https://github.com/ziglang/zig.git
cd zig

# 編譯
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make install

# 驗證
zig version
```

---

## Hello World 完整範例

### 建立專案

```bash
# 建立專案目錄
mkdir zig-hello
cd zig-hello

# 建立 main.zig 檔案
touch main.zig
```

### Hello World 程式碼

建立 `main.zig` 檔案，內容如下：

```zig
const std = @import("std");

pub fn main() !void {
    // 使用標準輸出
    const stdout = std.io.getStdOut().writer();
    
    // 方法 1: 簡單輸出
    try stdout.print("Hello, World!\n", .{});
    
    // 方法 2: 格式化輸出
    const name = "Zig";
    const version = "0.13.0";
    try stdout.print("Hello from {s} {s}!\n", .{name, version});
    
    // 方法 3: Debug 輸出
    std.debug.print("Debug: Hello, World!\n", .{});
}
```

### 編譯和執行

```bash
# 編譯並執行（一步完成）
zig run main.zig

# 輸出：
# Hello, World!
# Hello from Zig 0.13.0!
# Debug: Hello, World!
```

### 編譯為可執行檔

```bash
# Debug 模式編譯
zig build-exe main.zig

# Release 模式編譯（優化）
zig build-exe main.zig -O ReleaseFast

# Release 模式（小體積）
zig build-exe main.zig -O ReleaseSmall

# Release 模式（安全檢查）
zig build-exe main.zig -O ReleaseSafe

# 執行
./main
```

### 進階範例：帶參數的 Hello World

```zig
const std = @import("std");

pub fn main() !void {
    // 取得 allocator
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    // 取得命令列參數
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);
    
    const stdout = std.io.getStdOut().writer();
    
    if (args.len > 1) {
        try stdout.print("Hello, {s}!\n", .{args[1]});
    } else {
        try stdout.print("Hello, World!\n", .{});
    }
}
```

執行：
```bash
zig build-exe hello.zig
./hello           # 輸出: Hello, World!
./hello Alice     # 輸出: Hello, Alice!
```

### 使用 Build System

建立 `build.zig`：

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "hello",
        .root_source_file = b.path("main.zig"),
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());

    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);
}
```

使用 build system：
```bash
# 編譯
zig build

# 編譯並執行
zig build run

# 可執行檔在 zig-out/bin/ 目錄
./zig-out/bin/hello
```

---

## 實用程式範例

### 檔案讀寫

```zig
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    // 寫入檔案
    const file = try std.fs.cwd().createFile("test.txt", .{});
    defer file.close();
    
    try file.writeAll("Hello from Zig!\n");
    
    // 讀取檔案
    const content = try std.fs.cwd().readFileAlloc(
        allocator,
        "test.txt",
        1024 * 1024,  // 最大 1MB
    );
    defer allocator.free(content);
    
    std.debug.print("File content: {s}\n", .{content});
}
```

### HTTP 請求（使用標準庫）

```zig
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var client = std.http.Client{ .allocator = allocator };
    defer client.deinit();

    const uri = try std.Uri.parse("http://example.com");
    
    var buf: [4096]u8 = undefined;
    var req = try client.open(.GET, uri, .{ .server_header_buffer = &buf });
    defer req.deinit();

    try req.send();
    try req.wait();

    const body = try req.reader().readAllAlloc(allocator, 1024 * 1024);
    defer allocator.free(body);

    std.debug.print("Response: {s}\n", .{body});
}
```

---

## 總結對照表

| 項目 | C 語言 | Zig 語言 |
|------|--------|----------|
| **學習曲線** | 低 | 中等 |
| **記憶體安全** | 手動，易出錯 | 更安全，有檢查 |
| **編譯速度** | 快 | 非常快 |
| **執行效能** | 極快 | 極快（相當） |
| **工具鏈** | 成熟，多樣 | 現代，整合 |
| **生態系統** | 龐大 | 成長中 |
| **適用場景** | 系統、嵌入式 | 系統、嵌入式 |
| **維護性** | 中等 | 較好 |

## 何時選擇 Zig？

✅ **選擇 Zig：**
- 新專案，想要現代語言特性
- 需要更好的錯誤處理
- 重視編譯時安全檢查
- 需要跨平台編譯
- 想要更好的 C 互操作

⚠️ **選擇 C：**
- 需要極度成熟的生態系統
- 團隊已熟悉 C
- 需要大量現成的函式庫
- 專案已經用 C 開發

---

## 參考資源

- **官方網站**: https://ziglang.org/
- **文檔**: https://ziglang.org/documentation/master/
- **學習資源**: https://ziglearn.org/
- **標準庫文檔**: https://ziglang.org/documentation/master/std/
- **GitHub**: https://github.com/ziglang/zig

---

**最後更新**: 2025-10-18
