# Copy trait的std文件

Copy trait的std文件

https://doc.rust-lang.org/std/marker/trait.Copy.html

```rust
pub trait Copy: Clone { }
```

只需複製位即可複製其值的類型。

默認情況下，變數繫結具有 `move語義`。換句話說:

```rust
#[derive(Debug)]
struct Foo;

let x = Foo;

let y = x;

// `x` 已移至 `y`，因此無法使用

// println!("{:?}", x); // error: use of moved value
```

但是，如果類型實現 `Copy`，則它具有複製語義:

```rust
// 我們可以派生一個 `Copy` 實現。
// `Clone` 也是必需的，因為它是 `Copy` 的父特徵。
#[derive(Debug, Copy, Clone)]
struct Foo;

let x = Foo;

let y = x;

// `y` 是 `x` 的副本

println!("{:?}", x); // A-OK!
```

重要的是要注意，在這兩個示例中，唯一的區別是分配後是否允許您訪問 `x`。 在後台，複製(copy)和移動(move)都可能導致將位複製到記憶體中，儘管有時會對其進行最佳化。

### 如何實現 `Copy`?

有兩種方法可以在您的類型上實現 `Copy`。最簡單的是使用 `derive`:

```rust
#[derive(Copy, Clone)]
struct MyStruct;
```

您還可以手動實現 `Copy` 和 `Clone`:

```rust
struct MyStruct;

impl Copy for MyStruct { }

impl Clone for MyStruct {
    fn clone(&self) -> MyStruct {
        *self
    }
}
```

兩者之間的區別很小: `derive` 策略還將 `Copy` 繫結在類型參數上，這並不總是需要的。

### `Copy` 和 `Clone` 有什麼區別？

複製是隱式發生的，例如作為分配 `y = x` 的一部分。`Copy` 的行為不可多載; 它始終是簡單的按位複製。

克隆是一個明確的動作 `x.clone()`。`Clone` 的實現可以提供安全複製值所需的任何特定於類型的行為。 例如，用於 `String`的 `Clone` 的實現需要在堆中複製指向字串的緩衝區。 `String` 值的簡單按位副本將僅複製指針，從而導致該行向下雙重釋放。 因此，`String`是 `Clone`，但不是 `Copy`。

`Clone` 是 `Copy` 的父特徵，因此 `Copy` 的所有類型也必須實現 `Clone`。 如果類型為 `Copy`，則其 `Clone` 實現僅需要返回 `*self` (請參見上面的示例)。

### 類型何時可以是 `Copy`?

如果類型的所有元件都實現 `Copy`，則它可以實現 `Copy`。例如，此結構體可以是 `Copy`:

```rust
#[derive(Copy, Clone)]
struct Point {
   x: i32,
   y: i32,
}
```

一個結構體可以是 `Copy`，而 `i32` 是 `Copy`，因此 `Point` 有資格成為 `Copy`。 相比之下，考慮

```rust
struct PointList {
    points: Vec<Point>,
}
```

結構體 `PointList` 無法實現 `Copy`，因為 `Vec` 不是 `Copy`。如果嘗試派生 `Copy` 實現，則會收到錯誤消息:

```bash
the trait `Copy` may not be implemented for this type; field `points` does not implement `Copy`
```

共享引用 (`&T`) 也是 `Copy`，因此，即使類型中包含不是 *`Copy` 類型的共享引用 `T`，也可以是 `Copy`。 考慮下面的結構體，它可以實現 `Copy`，因為它從上方僅對我們的非 Copy 類型 `PointList` 持有一個 *shared 引用*:

```rust
#[derive(Copy, Clone)]
struct PointListWrapper<'a> {
    point_list_ref: &'a PointList,
}
```

### 什麼時候類型不能為 `Copy`?

某些類型無法安全複製。例如，複製 `&mut T` 將建立一個別名可變引用。 複製 `String` 將重複管理 `String` 緩衝區，從而導致雙重釋放。

概括後一種情況，任何實現 `Drop` 的類型都不能是 `Copy`，因為它除了管理自己的 `size_of::` 位元組外還管理一些資源。

果您嘗試在包含非 `Copy` 資料的結構或列舉上實現 `Copy`，則會收到 [E0204](https://skyao.io/learning-rust/std/marker/error-index.html#E0204) 錯誤。

### 什麼時候類型應該是 `Copy`?

一般來說，如果您的類型可以實現 `Copy`，則應該這樣做。 但是請記住，實現 `Copy` 是您類型的公共 API 的一部分。 如果該類型將來可能變為非 `Copy`，則最好現在省略 `Copy` 實現，以避免 API 發生重大更改。

### 其他實現者

除下面列出的實現者外，以下類型還實現 `Copy`:

- 函數項類型 (即，為每個函數定義的不同類型)
- 函數指針類型 (例如 `fn() -> i32`)
- 如果項類型也實現 `Copy` (例如 `[i32; 123456]`)，則所有大小的陣列類型
- 如果每個元件還實現 `Copy` (例如 `()`，`(i32, bool)`)，則為元組類型
- 閉包類型，如果它們沒有從環境中捕獲任何值，或者所有此類捕獲的值本身都實現了 `Copy`。 請注意，由共享引用捕獲的變數始終實現 `Copy` (即使引用對象沒有實現)，而由變數引用捕獲的變數從不實現 `Copy`。


---

```rust
#[derive(Debug)]
struct MyStruct;

impl Copy for MyStruct {
}

impl Clone for MyStruct {
    fn clone(&self) -> MyStruct {
        println!("Cloning MyStruct");
        *self
    }
}

fn main() {
    let original = MyStruct;
    let copied = original;
    let cloned = original.clone();

    println!("Original: {:?}", original);
    println!("Copied: {:?}", copied);
    println!("Cloned: {:?}", cloned);
}
```
