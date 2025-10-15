# unsafe

**Rust**的內存安全依賴於強大的類型系統和編譯時檢測，不過它並不能適應所有的場景。
首先，所有的編程語言都需要跟外部的“不安全”接口打交道，調用外部庫等，在“安全”的Rust下是無法實現的; 其次，“安全”的Rust無法高效表示複雜的數據結構，特別是數據結構內部有各種指針互相引用的時候；再次，
事實上還存在著一些操作，這些操作是安全的，但不能通過編譯器的驗證。

因此在安全的Rust背後，還需要`unsafe`的支持。

`unsafe`塊能允許程序員做的額外事情有：

* 解引用一個裸指針`*const T`和`*mut T`
 
```rust
let x = 5;
let raw = &x as *const i32;
let points_at = unsafe { *raw };
println!("raw points at {}", points_at);
```

* 讀寫一個可變的靜態變量`static mut`

```rust
static mut N: i32 = 5;
unsafe {
    N += 1;
    println!("N: {}", N);
}
```

* 調用一個不安全函數

```rust
unsafe fn foo() {
	//實現
}
fn main() {
	unsafe {
    	foo();
    }
}
```

## 使用`unsafe`

`unsafe fn`不安全函數標示如果調用它可能會違反**Rust**的內存安全語意：

```rust
unsafe fn danger_will_robinson() {
    // 實現
}
```

`unsafe block`不安全塊可以在其中調用不安全的代碼：

```rust
unsafe {
    // 實現
}
```

`unsafe trait`不安全trait及它們的實現，所有實現它們的具體類型有可能是不安全的:

```rust
unsafe trait Scary { }
unsafe impl Scary for i32 {}
```

## safe != no bug

對於**Rust**來說禁止你做任何不安全的事是它的本職，不過有些是編寫代碼時的`bug`，它們並不屬於“內存安全”的範疇：

* 死鎖
* 內存或其他資源溢出
* 退出未調用析構函數
* 整型溢出

使用`unsafe`時需要注意一些特殊情形：

* 數據競爭
* 解引用空裸指針和懸垂裸指針
* 讀取未初始化的內存
* 使用裸指針打破指針重疊規則
* `&mut T`和`&T`遵循LLVM範圍的`noalias`模型，除了如果`&T`包含一個`UnsafeCell<U>`的話。不安全代碼必須不能違反這些重疊（aliasing）保證
* 不使用`UnsafeCell<U>`改變一個不可變值/引用
* 通過編譯器固有功能調用未定義行為：
	* 使用`std::ptr::offset`（offset功能）來索引超過對象邊界的值，除了允許的末位超出一個字節
	* 在重疊（overlapping）緩衝區上使用`std::ptr::copy_nonoverlapping_memory`（memcpy32/memcpy64功能）
* 原生類型的無效值，即使是在私有字段/本地變量中：
	* 空/懸垂引用或裝箱
	* `bool`中一個不是`false`（0）或`true`（1）的值
	* `enum`中一個並不包含在類型定義中判別式
	* `char`中一個代理字（surrogate）或超過char::MAX的值
	* `str`中非UTF-8字節序列
* 在外部代碼中使用Rust或在Rust中使用外部語言



