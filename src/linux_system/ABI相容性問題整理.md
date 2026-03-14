# ABI 相容性問題完整整理

## 什麼是 ABI？

ABI（Application Binary Interface，應用程式二進位介面）定義了編譯後的二進位程式碼如何在執行時期互動，包含結構體記憶體佈局、函數呼叫慣例、符號命名規則等。ABI 相容性問題通常發生在軟體元件（庫、驅動程式）的編譯環境不一致時。

---

## 一、根本原因

### 1. 結構體與資料佈局差異

若庫升版修改了結構體成員、調整了成員順序或變更了資料類型，編譯後的記憶體位移量（Offset）會改變。舊版主程式依據錯誤的 offset 讀取記憶體，導致資料損毀。

```
舊版庫 struct Foo          新版庫 struct Foo
┌──────────────┐           ┌──────────────┐
│ offset 0: a  │  (int)    │ offset 0: b  │  (double)
├──────────────┤           ├──────────────┤
│ offset 4: b  │ (double)  │ offset 8: a  │  (int)
└──────────────┘           └──────────────┘
     主程式以舊 offset 讀 → 讀到垃圾值
```

### 2. 函數簽名變更

函數名稱改變（Name Mangling）或參數類型變更，導致連結期（Link-time）或執行期（Run-time）無法找到對應的函數符號。

### 3. 編譯器／編譯選項不一致

使用不同版本的編譯器（如 GCC vs. Clang，或不同版本 GCC），或設定不同的結構體對齊方式，導致即使程式碼相同，產生的機器碼指令和資料結構也不相容。

### 4. 硬體架構／模式衝突

庫與應用程式針對不同 ABI 模式編譯（如 ARM32 與 ARM64，或 32-bit 與 64-bit），或軟體庫與運行的 CUDA／作業系統版本衝突。

---

## 二、問題表現

| 症狀 | 說明 |
|------|------|
| Segmentation Fault | 存取虛擬函數表或錯誤記憶體位址時崩潰 |
| 未定義行為（UB） | 變數存取錯誤導致邏輯錯誤、資料損毀 |
| Linker Error | 符號未找到（undefined reference） |
| 載入失敗 | Runtime `dlopen` 錯誤，.so 無法載入 |

---

## 三、跨語言 ABI 風險比較

| 語言 | 預設 ABI 穩定性 | 主要陷阱 | 安全做法 |
|------|----------------|----------|----------|
| C | 高（佈局可預測） | `#pragma pack`、不同 `sizeof` | 固定標頭版本 |
| C++ | 低（Mangling + vtable） | 跨編譯器、跨版本 vtable 錯位 | `extern "C"` 包裝 |
| Go | 高（純 Go 內部） | `cgo` 邊界 struct 佈局 | 顯式建立 C 型別 |
| Rust | 低（`repr(Rust)` 可重排） | FFI 傳遞 struct | `#[repr(C)]` |

---

## 四、實際程式碼範例

### C / C++ — 結構體 offset 錯位

**問題：** 庫升版時調換欄位順序，主程式沿用舊標頭。

```c
// libfoo_v1.h（舊版，主程式用這個編譯）
typedef struct {
    int    id;     // offset 0
    double value;  // offset 8
} Foo;

// libfoo_v2.c（新版庫，成員順序對調）
typedef struct {
    double value;  // offset 0  ← 順序換了！
    int    id;     // offset 8
} Foo;

void print_foo(Foo *f) {
    printf("id=%d value=%f\n", f->id, f->value);
    // 主程式傳來的 f->id 實際上是 double 的位元 → 垃圾值
}
```

**修法：** 用不透明指標（opaque pointer）固定對外介面，內部實作隨意改：

```c
// stable_api.h ← 對外穩定介面
typedef struct FooHandle FooHandle;  // 不透明指標，外部看不到成員

FooHandle* foo_create(int id, double value);
int        foo_get_id(FooHandle*);
double     foo_get_value(FooHandle*);
void       foo_destroy(FooHandle*);
```

---

### C++ — Name Mangling 與 vtable 問題

**問題：** 在 vtable 中間插入新的 virtual function，導致 slot 全部錯位。

```cpp
// 庫用 GCC 12 編譯
class Animal {
public:
    virtual void speak();    // vtable slot 0
};

// 升版後插入新 virtual，vtable slot 全錯位
class Animal {
public:
    virtual void breathe();  // 新增！slot 0
    virtual void speak();    // 現在是 slot 1
};

// 主程式呼叫 speak() → 實際跳到 breathe() → UB / crash
```

**修法：** 在 ABI 邊界加 `extern "C"` 包裝，新 virtual 只能加在尾端：

```cpp
// stable_wrapper.h
#ifdef __cplusplus
extern "C" {
#endif

void* animal_create();
void  animal_speak(void* handle);   // C 介面，不受 Name Mangling 影響
void  animal_destroy(void* handle);

#ifdef __cplusplus
}
#endif
```

---

### Go — cgo 邊界的 ABI 問題

Go 純 Go 呼叫沒有 ABI 相容問題，但透過 `cgo` 呼叫 C 庫時需注意 struct 佈局。

**問題：** Go struct 與 C struct 佈局不一致，直接強轉 `unsafe.Pointer`。

```go
package main

/*
#include <stdint.h>
typedef struct {
    double  value;   // C: 8 bytes, offset 0
    int32_t id;      // C: 4 bytes, offset 8
} CFoo;
void print_foo(CFoo* f);
*/
import "C"
import "unsafe"

type GoFoo struct {
    ID    int32   // Go: 4 bytes, offset 0  ← 順序和 C 不同！
    Value float64 // Go: 8 bytes, offset 8
}

func main() {
    gf := GoFoo{ID: 1, Value: 3.14}
    // 直接強轉 unsafe.Pointer → C 會讀到錯誤欄位
    C.print_foo((*C.CFoo)(unsafe.Pointer(&gf))) // BUG！
}
```

**修法：** 一律建立 `C.CFoo`，不靠 `unsafe.Pointer` 強轉：

```go
func main() {
    cf := C.CFoo{
        value: C.double(3.14),
        id:    C.int32_t(1),
    }
    C.print_foo(&cf)  // 欄位名稱對應，Go cgo 自動處理佈局
}
```

---

### Rust — `repr(Rust)` vs `repr(C)`

Rust 預設編譯器可隨意重排欄位（`repr(Rust)`），跨 FFI 邊界必須用 `repr(C)`。

**問題：** 使用預設 `repr(Rust)`，欄位順序由編譯器決定，傳給 C 函式是 UB。

```rust
// 問題：預設 repr(Rust)，欄位順序編譯器決定
struct Foo {
    id: i32,
    value: f64,
}

extern "C" {
    fn c_print_foo(f: *const Foo);
}

unsafe { c_print_foo(&foo); }  // UB！佈局未定義
```

**修法：** 加上 `#[repr(C)]` 保證與 C struct 佈局相同：

```rust
#[repr(C)]          // ← 保證與 C struct 佈局相同
struct Foo {
    id:    i32,     // offset 0
    value: f64,     // offset 8（自動 padding）
}

unsafe { c_print_foo(&foo); }  // OK，佈局有保證
```

---

## 五、常見場景與對應解法

| 場景 | 症狀 | 對應做法 |
|------|------|----------|
| Android 驅動 | `insmod` 失敗 / kernel panic | 核對 `Module.symvers`，更新 `EXPORT_SYMBOL` 符號清單 |
| PyTorch C++ 擴展 | `import` 時 `.so` 載入報錯 | 加 `_GLIBCXX_USE_CXX11_ABI=0/1` 旗標重編 |
| 跨版本升級 | 執行期隨機崩潰 | 版本化標頭 + `soname` 機制分隔新舊 ABI |
| 混用編譯器 | 連結期符號找不到 | 統一 compiler 版本與 flags |

---

## 六、通用排查步驟

```
① 確認編譯器版本
   gcc --version / clang --version / rustc --version

② 比對編譯選項
   CFLAGS / CXXFLAGS / ABI flag (-D_GLIBCXX_USE_CXX11_ABI)

③ 檢查符號表
   nm -D libfoo.so | grep foo_func
   readelf -d libfoo.so | grep SONAME

④ 重新編譯全部元件
   統一工具鏈後全量重編，避免混用舊產物
```

---

## 七、解決核心原則

1. **統一工具鏈** — 所有元件使用相同 compiler 版本與 flags
2. **版本化介面** — soname / symbol versioning 分隔新舊 ABI
3. **穩定邊界** — C ABI 包裝（`extern "C"`）或 FFI 層隔離 C++ 細節
4. **靜態連結** — 消除動態庫 ABI 差異（犧牲體積換穩定性）
5. **不透明指標** — 對外只暴露 handle，內部結構不外露

---

*整理日期：2026-03-15*
