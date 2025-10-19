# Zig vs C 語言完整比較指南

## 目錄
1. [簡介](#簡介)
2. [語言概述](#語言概述)
3. [核心特性比較](#核心特性比較)
4. [語法比較](#語法比較)
5. [Zig 優勢詳解](#zig-優勢詳解)
6. [記憶體管理](#記憶體管理)
7. [錯誤處理](#錯誤處理)
8. [編譯時特性](#編譯時特性)
9. [標準函式庫](#標準函式庫)
10. [實際範例對比](#實際範例對比)
11. [實用程式範例](#實用程式範例)
12. [Ubuntu 安裝指南](#ubuntu-安裝指南)
13. [Hello World 完整範例](#hello-world-完整範例)
14. [優缺點總結](#優缺點總結)
15. [遷移建議](#遷移建議)

---

## 簡介

**Zig** 是一個現代的系統程式語言,目標是成為「更好的 C」。它保留了 C 的簡潔性和性能，同時增加了現代語言的安全性和便利性。

**設計理念：**
- 沒有隱藏的控制流
- 沒有隱藏的記憶體分配
- 沒有預處理器
- 編譯時程式設計能力強大

---

## 語言概述

### C 語言
- **發布年份**: 1972年
- **設計者**: Dennis Ritchie
- **設計理念**: 系統程式設計、可移植性、效率
- **主要用途**: 作業系統、嵌入式系統、系統軟體

### Zig 語言
- **發布年份**: 2016年
- **設計者**: Andrew Kelley
- **設計理念**: 取代 C 的現代系統程式語言，更安全、更簡單
- **主要用途**: 系統程式設計、嵌入式開發、WebAssembly

---

## 核心特性比較

| 特性 | C 語言 | Zig 語言 |
|------|--------|----------|
| **記憶體安全** | 手動管理，容易出錯 | 手動管理但有更多安全檢查 |
| **空指標** | 允許，常見錯誤來源 | 可選類型（Optional Types） |
| **錯誤處理** | 返回錯誤碼或 errno | 內建錯誤處理機制 (!) |
| **預處理器** | 有（#define, #include） | 無，使用編譯時執行 |
| **標頭檔** | 需要 .h 檔案 | 不需要標頭檔 |
| **泛型程式設計** | 透過巨集或 void* | 編譯時泛型 (comptime) |
| **編譯時執行** | 有限（巨集） | 完整的編譯時執行 |
| **未定義行為** | 大量存在 | 明確定義所有行為 |
| **交叉編譯** | 需要工具鏈 | 內建交叉編譯支援 |
| **C 相容性** | N/A | 可直接導入 C 程式碼 |
| **包管理** | 無官方工具 | 內建包管理 |
| **測試框架** | 需要外部工具 | 內建測試 |
| **整數溢位** | 未定義 | 可檢測或環繞 |

---

## 語法比較

### 1. 基本程式結構

**C 語言：**
```c
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

**Zig 語言：**
```zig
const std = @import("std");

pub fn main() void {
    std.debug.print("Hello, World!\n", .{});
}
```

### 2. 變數宣告

**C 語言：**
```c
int x = 10;           // 可變變數
const int y = 20;     // 常數
int *ptr = &x;        // 指標
float pi = 3.14;
```

**Zig 語言：**
```zig
var x: i32 = 10;      // 可變變數
const y: i32 = 20;    // 編譯時常數
var ptr: *i32 = &x;   // 指標
const pi: f32 = 3.14; // 浮點數
```

### 3. 資料型別

| C 型別 | Zig 型別 | 說明 |
|--------|----------|------|
| `char` | `u8` 或 `i8` | 8位元整數 |
| `short` | `i16` | 16位元有號整數 |
| `int` | `c_int` 或 `i32` | 32位元有號整數 |
| `long` | `c_long` 或 `i64` | 64位元有號整數 |
| `float` | `f32` | 32位元浮點數 |
| `double` | `f64` | 64位元浮點數 |
| `void*` | `*anyopaque` | 不透明指標 |
| `NULL` | `null` | 空值 |

### 4. 函式定義

**C 語言：**
```c
int add(int a, int b) {
    return a + b;
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void print_hello() {
    printf("Hello\n");
}
```

**Zig 語言：**
```zig
fn add(a: i32, b: i32) i32 {
    return a + b;
}

fn swap(a: *i32, b: *i32) void {
    const temp = a.*;
    a.* = b.*;
    b.* = temp;
}

fn printHello() void {
    std.debug.print("Hello\n", .{});
}
```

### 5. 結構體

**C 語言：**
```c
struct Point {
    int x;
    int y;
};

struct Point p = {10, 20};
p.x = 30;

typedef struct {
    char name[50];
    int age;
} Person;
```

**Zig 語言：**
```zig
const Point = struct {
    x: i32,
    y: i32,
};

var p = Point{ .x = 10, .y = 20 };
p.x = 30;

const Person = struct {
    name: [50]u8,
    age: i32,

    // 可以包含方法
    pub fn greet(self: Person) void {
        std.debug.print("Hello, {s}\n", .{self.name});
    }
};
```

### 6. 陣列

**C 語言：**
```c
int arr[5] = {1, 2, 3, 4, 5};
int len = sizeof(arr) / sizeof(arr[0]);  // 容易出錯
```

**Zig 語言：**
```zig
const arr = [_]i32{1, 2, 3, 4, 5};
const len = arr.len;  // 內建長度屬性
```

### 7. 指標

**C 語言：**
```c
int x = 10;
int *ptr = &x;
*ptr = 20;

int *null_ptr = NULL;
```

**Zig 語言：**
```zig
var x: i32 = 10;
var ptr: *i32 = &x;
ptr.* = 20;

var null_ptr: ?*i32 = null;  // 可選指標
```

### 8. 條件判斷

**C 語言：**
```c
if (x > 0) {
    printf("Positive\n");
} else if (x < 0) {
    printf("Negative\n");
} else {
    printf("Zero\n");
}

// 三元運算子
int result = (x > 0) ? 1 : -1;

// Switch
switch (x) {
    case 1:
        printf("One\n");
        break;  // 需要 break
    case 2:
        printf("Two\n");
        break;
    default:
        printf("Other\n");
}
```

**Zig 語言：**
```zig
if (x > 0) {
    std.debug.print("Positive\n", .{});
} else if (x < 0) {
    std.debug.print("Negative\n", .{});
} else {
    std.debug.print("Zero\n", .{});
}

// if 表達式
const result = if (x > 0) 1 else -1;

// Switch
switch (x) {
    1 => std.debug.print("One\n", .{}),
    2 => std.debug.print("Two\n", .{}),
    else => std.debug.print("Other\n", .{}),
}  // 不需要 break，不會 fall-through
```

### 9. 迴圈

**C 語言：**
```c
// for 迴圈
for (int i = 0; i < 10; i++) {
    printf("%d ", i);
}

// while 迴圈
int i = 0;
while (i < 10) {
    printf("%d ", i);
    i++;
}

// do-while 迴圈
do {
    printf("%d ", i);
    i++;
} while (i < 10);
```

**Zig 語言：**
```zig
// for 迴圈（範圍）
for (0..10) |i| {
    std.debug.print("{} ", .{i});
}

// for 迴圈（陣列）
const array = [_]i32{1, 2, 3, 4, 5};
for (array) |item| {
    std.debug.print("{} ", .{item});
}

// while 迴圈
var i: usize = 0;
while (i < 10) : (i += 1) {
    std.debug.print("{} ", .{i});
}
```

### 10. 列舉

**C 語言：**
```c
enum Color {
    RED,
    GREEN,
    BLUE
};

enum Color c = RED;
```

**Zig 語言：**
```zig
const Color = enum {
    red,
    green,
    blue,
};

var c = Color.red;

// 標籤聯合（Tagged Union）
const Value = union(enum) {
    int: i32,
    float: f32,
    string: []const u8,
};
```

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

### 動態記憶體分配比較

**C 語言：**
```c
#include <stdlib.h>

int *arr = (int*)malloc(10 * sizeof(int));
if (arr == NULL) {
    // 處理錯誤
}

// 使用陣列
arr[0] = 42;

free(arr);  // 必須記得釋放
```

**Zig 語言：**
```zig
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const arr = try allocator.alloc(i32, 10);
    defer allocator.free(arr);  // defer 確保釋放

    arr[0] = 42;
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

### C 語言的錯誤處理

```c
FILE *file = fopen("test.txt", "r");
if (file == NULL) {
    perror("Error opening file");
    return -1;
}

// 或使用 errno
if (some_function() == -1) {
    if (errno == ENOENT) {
        printf("File not found\n");
    }
}
```

### Zig 語言的錯誤處理

```zig
const file = std.fs.cwd().openFile("test.txt", .{}) catch |err| {
    std.debug.print("Error opening file: {}\n", .{err});
    return err;
};
defer file.close();

// 錯誤聯合類型
fn divide(a: f32, b: f32) !f32 {
    if (b == 0) {
        return error.DivisionByZero;
    }
    return a / b;
}

// 使用 try
const result = try divide(10, 2);
```

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

## 編譯時特性

### C 語言的預處理器

```c
#define MAX_SIZE 100
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#ifdef DEBUG
    #define LOG(x) printf("%s\n", x)
#else
    #define LOG(x)
#endif
```

### Zig 語言的編譯時執行

```zig
const max_size = 100;  // 編譯時常數

fn min(comptime T: type, a: T, b: T) T {
    return if (a < b) a else b;
}

// 編譯時執行
const fibonacci = comptime blk: {
    var fib: [10]i32 = undefined;
    fib[0] = 0;
    fib[1] = 1;
    var i: usize = 2;
    while (i < 10) : (i += 1) {
        fib[i] = fib[i-1] + fib[i-2];
    }
    break :blk fib;
};

// 條件編譯
const debug = @import("builtin").mode == .Debug;
fn log(msg: []const u8) void {
    if (debug) {
        std.debug.print("{s}\n", .{msg});
    }
}
```

---

## 標準函式庫

### 字串操作

**C 語言：**
```c
#include <string.h>

char str1[100] = "Hello";
char str2[] = " World";

strcat(str1, str2);        // 串接
int len = strlen(str1);     // 長度
int cmp = strcmp(str1, str2); // 比較
char *copy = strcpy(dest, src); // 複製
```

**Zig 語言：**
```zig
const std = @import("std");

var buffer: [100]u8 = undefined;
const str1 = "Hello";
const str2 = " World";

// 使用 fmt 格式化
const result = try std.fmt.bufPrint(&buffer, "{s}{s}", .{str1, str2});

// 長度
const len = str1.len;

// 比較
const equal = std.mem.eql(u8, str1, str2);

// 複製
std.mem.copy(u8, &buffer, str1);
```

---

## 實際範例對比

### 範例 1：陣列操作

**C 語言：**
```c
#include <stdio.h>

void print_array(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

int main() {
    int numbers[] = {1, 2, 3, 4, 5};
    int size = sizeof(numbers) / sizeof(numbers[0]);

    print_array(numbers, size);
    printf("Sum: %d\n", sum_array(numbers, size));

    return 0;
}
```

**Zig 語言：**
```zig
const std = @import("std");

fn printArray(arr: []const i32) void {
    for (arr) |item| {
        std.debug.print("{} ", .{item});
    }
    std.debug.print("\n", .{});
}

fn sumArray(arr: []const i32) i32 {
    var sum: i32 = 0;
    for (arr) |item| {
        sum += item;
    }
    return sum;
}

pub fn main() void {
    const numbers = [_]i32{ 1, 2, 3, 4, 5 };

    printArray(&numbers);
    std.debug.print("Sum: {}\n", .{sumArray(&numbers)});
}
```

### 範例 2：鏈結串列

**C 語言：**
```c
#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node* next;
};

struct Node* create_node(int data) {
    struct Node* node = (struct Node*)malloc(sizeof(struct Node));
    if (node == NULL) return NULL;
    node->data = data;
    node->next = NULL;
    return node;
}

void free_list(struct Node* head) {
    struct Node* temp;
    while (head != NULL) {
        temp = head;
        head = head->next;
        free(temp);
    }
}
```

**Zig 語言：**
```zig
const std = @import("std");

const Node = struct {
    data: i32,
    next: ?*Node,

    fn create(allocator: std.mem.Allocator, data: i32) !*Node {
        const node = try allocator.create(Node);
        node.* = Node{
            .data = data,
            .next = null,
        };
        return node;
    }

    fn destroyList(self: *Node, allocator: std.mem.Allocator) void {
        var current: ?*Node = self;
        while (current) |node| {
            const next = node.next;
            allocator.destroy(node);
            current = next;
        }
    }
};
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

### 方法 3: 使用 APT（Ubuntu 22.04+）

```bash
# 更新套件列表
sudo apt update

# 安裝 Zig
sudo apt install zig
```

### 方法 4: 從原始碼編譯

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

### 基本使用指令

```bash
# 建立專案目錄
mkdir hello-zig
cd hello-zig

# 建立主程式檔案
cat > main.zig << 'EOF'
const std = @import("std");

pub fn main() void {
    std.debug.print("Hello, Zig!\n", .{});
}
EOF

# 直接執行（開發時使用）
zig run main.zig

# 編譯成執行檔
zig build-exe main.zig

# 執行編譯後的程式
./main
```

### 編譯選項詳解

```bash
# 基本編譯
zig build-exe main.zig

# 指定輸出檔名
zig build-exe main.zig -femit-bin=myapp

# 優化等級
zig build-exe main.zig -O ReleaseFast    # 最佳效能
zig build-exe main.zig -O ReleaseSafe    # 平衡效能與安全
zig build-exe main.zig -O ReleaseSmall   # 最小體積
zig build-exe main.zig -O Debug          # 偵錯模式（預設）

# 靜態連結（預設）
zig build-exe main.zig

# 動態連結
zig build-exe main.zig -dynamic

# 交叉編譯（編譯給其他平台）
zig build-exe main.zig -target x86_64-windows
zig build-exe main.zig -target aarch64-linux
zig build-exe main.zig -target wasm32-wasi
```

### 使用 Zig 專案建構系統

```bash
# 建立新專案
mkdir myproject
cd myproject

# 初始化 Zig 專案
zig init-exe  # 建立執行檔專案
# 或
zig init-lib  # 建立函式庫專案

# 專案結構
tree
# .
# ├── build.zig       # 建構腳本
# ├── src
# │   └── main.zig    # 主程式
# └── zig-cache/      # 快取目錄（自動生成）
```

### 整合 C 程式碼

```zig
// math_wrapper.zig
const c = @cImport({
    @cInclude("math.h");
    @cInclude("stdio.h");
});

pub fn main() void {
    const result = c.sqrt(16.0);
    _ = c.printf("Square root of 16 is: %f\n", result);
}
```

編譯：
```bash
# 編譯包含 C 程式碼的 Zig 程式
zig build-exe math_wrapper.zig -lc
./math_wrapper
```

### 開發環境設定

#### VSCode 設定

```bash
# 安裝 VSCode
sudo snap install code --classic

# 安裝 Zig 擴充套件
code --install-extension ziglang.vscode-zig

# 建立 VSCode 設定檔 (.vscode/settings.json)
mkdir .vscode
cat > .vscode/settings.json << 'EOF'
{
    "zig.buildOnSave": true,
    "zig.formattingProvider": "zls",
    "zig.zls.enableAutofix": true
}
EOF
```

#### 安裝 ZLS (Zig Language Server)

```bash
# 方法 1: 使用預編譯版本
wget https://github.com/zigtools/zls/releases/download/0.11.0/zls-x86_64-linux.tar.gz
tar -xf zls-x86_64-linux.tar.gz
sudo mv zls /usr/local/bin/

# 方法 2: 從原始碼編譯
git clone https://github.com/zigtools/zls
cd zls
zig build -Doptimize=ReleaseSafe
sudo cp zig-out/bin/zls /usr/local/bin/
```

### 常用開發指令

```bash
# 格式化程式碼
zig fmt src/

# 產生文件
zig build-docs

# 執行內建測試
zig test src/main.zig

# 檢查程式碼
zig ast-check src/main.zig

# 顯示建構快取
zig build --verbose-cc

# 清理快取
rm -rf zig-cache zig-out

# 查看 Zig 內建函式
zig builtin

# 查看支援的目標平台
zig targets

# C 程式碼轉換為 Zig
zig translate-c helper.c > helper.zig
```

### 偵錯 Zig 程式

#### 使用 GDB

```bash
# 編譯時加入偵錯資訊
zig build-exe main.zig -O Debug

# 使用 GDB 偵錯
gdb ./main

# GDB 指令
# (gdb) break main           # 設定中斷點
# (gdb) run                  # 執行程式
# (gdb) step                 # 單步執行
# (gdb) print variable_name  # 印出變數
# (gdb) backtrace           # 顯示呼叫堆疊
# (gdb) quit                # 離開
```

#### 使用 LLDB

```bash
# 安裝 LLDB
sudo apt install lldb

# 偵錯
lldb ./main

# LLDB 指令
# (lldb) b main             # 設定中斷點
# (lldb) r                  # 執行
# (lldb) s                  # 單步執行
# (lldb) p variable_name    # 印出變數
# (lldb) bt                 # 顯示呼叫堆疊
```

### 效能分析

```bash
# 使用 Valgrind 檢查記憶體洩漏
sudo apt install valgrind
zig build-exe main.zig -O Debug
valgrind --leak-check=full ./main

# 使用 perf 進行效能分析
sudo apt install linux-tools-generic
zig build-exe main.zig -O ReleaseFast
perf record ./main
perf report
```

### 常見問題解決

#### 1. 版本相容性問題

```bash
# 檢查 Zig 版本
zig version

# 使用特定版本的 Zig
# 下載並管理多個版本，使用符號連結切換
ls -la /opt/zig-*
sudo ln -sf /opt/zig-0.11.0 /opt/zig
```

#### 2. 編譯錯誤除錯

```bash
# 顯示詳細編譯資訊
zig build-exe main.zig --verbose-cc

# 顯示 AST（抽象語法樹）
zig ast-check --ast main.zig
```

#### 3. 記憶體問題除錯

```zig
// 使用 GeneralPurposeAllocator 的除錯模式
const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{
        .safety = true,  // 啟用安全檢查
    }){};
    defer {
        const leaked = gpa.deinit();
        if (leaked) {
            std.debug.print("Memory leak detected!\n", .{});
        }
    }

    const allocator = gpa.allocator();
    // 使用 allocator...
}
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

## 優缺點總結

### C 語言優點
1. 成熟穩定，生態系統龐大
2. 幾乎所有平台都支援
3. 大量的函式庫和工具
4. 豐富的學習資源
5. 簡單直接的語法

### C 語言缺點
1. 大量未定義行為
2. 手動記憶體管理容易出錯
3. 缺乏現代語言特性
4. 預處理器系統複雜且容易出錯
5. 沒有內建的錯誤處理機制

### Zig 語言優點
1. 沒有未定義行為
2. 優秀的編譯時執行能力
3. 內建錯誤處理機制
4. 更好的型別安全
5. 內建交叉編譯支援
6. 可直接使用 C 程式碼
7. 不需要標頭檔
8. defer 語句確保資源清理

### Zig 語言缺點
1. 相對較新，生態系統較小
2. 文件和學習資源較少
3. 語言仍在發展中（尚未到 1.0 版）
4. IDE 支援不如 C 成熟
5. 社群相對較小

---

## 遷移建議

### 從 C 遷移到 Zig 的步驟

1. **漸進式遷移**：Zig 可以直接導入和使用 C 程式碼，可以逐步遷移
2. **學習新概念**：重點學習錯誤處理、可選類型、編譯時執行
3. **利用 Zig 的優勢**：使用 defer、錯誤聯合、編譯時驗證
4. **保持 C 相容性**：可以繼續使用現有的 C 函式庫

### 適合使用 Zig 的場景
- 新的系統程式專案
- 需要更好的安全性保證
- 嵌入式系統開發
- WebAssembly 目標
- 需要交叉編譯的專案

### 適合繼續使用 C 的場景
- 維護現有的大型 C 程式碼庫
- 需要最廣泛的平台支援
- 團隊已經熟悉 C
- 依賴特定的 C 工具鏈

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

**最後更新**: 2025-10-19

---

*Zig 是一個現代化的系統程式語言，旨在解決 C 語言的許多問題，同時保持 C 的簡單性和效能。雖然 Zig 還在發展中，但它提供了許多吸引人的特性，特別是在安全性和開發體驗方面。對於新專案，Zig 是一個值得考慮的選擇；對於現有的 C 專案，可以考慮漸進式地引入 Zig。*

*選擇使用哪種語言應該基於專案需求、團隊經驗和長期維護考量。兩種語言都有其適用的場景，了解它們的差異有助於做出明智的技術決策。*
