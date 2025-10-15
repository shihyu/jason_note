# 裸指針

**Rust**通過限制智能指針的行為保障了編譯時安全，不過仍需要對指針做一些額外的操作。

`*const T`和`*mut T`在**Rust**中被稱為“裸指針”。它允許別名，允許用來寫共享所有權的類型，甚至是內存安全的共享內存類型如：`Rc<T>`和`Arc<T>`，但是賦予你更多權利的同時意味著你需要擔當更多的責任：

* 不能保證指向有效的內存，甚至不能保證是非空的
* 沒有任何自動清除，所以需要手動管理資源
* 是普通舊式類型，也就是說，它不移動所有權，因此**Rust**編譯器不能保證不出像釋放後使用這種bug
* 缺少任何形式的生命週期，不像`&`，因此編譯器不能判斷出懸垂指針
* 除了不允許直接通過`*const T`改變外，沒有別名或可變性的保障

## 使用

創建一個裸指針：

```rust
let a = 1;
let b = &a as *const i32;

let mut x = 2;
let y = &mut x as *mut i32;
```

解引用需要在`unsafe`中進行：

```rust
let a = 1;
let b = &a as *const i32;
let c = unsafe { *b };
println!("{}", c);
```

`Box<T>`的`into_raw`：

```rust
let a: Box<i32> = Box::new(10);
// 我們需要先解引用a，再隱式把 & 轉換成 *
let b: *const i32 = &*a;
// 使用 into_raw 方法
let c: *const i32 = Box::into_raw(a);
```

如上說所，引用和裸指針之間可以隱式轉換，但隱式轉換後再解引用需要使用`unsafe`：

```rust
// 顯式
let a = 1;
let b: *const i32 = &a as *const i32; //或者let b = &a as *const i32；
// 隱式
let c: *const i32 = &a;
unsafe {
	println!("{}", *c);
}

```
