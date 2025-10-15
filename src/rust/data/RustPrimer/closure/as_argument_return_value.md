# 閉包作為參數和返回值
## 閉包作為參數（Taking closures as arguments）

現在我們知道了閉包是 trait，我們已經知道了如何接受和返回閉包；就像任何其它的 trait！

這也意味著我們也可以選擇靜態或動態分發。首先，讓我們寫一個獲取可調用結構的函數，調用它，然後返回結果：

```rust
fn call_with_one<F>(some_closure: F) -> i32
    where F : Fn(i32) -> i32 {

    some_closure(1)
}

let answer = call_with_one(|x| x + 2);

assert_eq!(3, answer);
```

我們傳遞我們的閉包，`|x| x + 2`，給`call_with_one`。它正做了我們說的：它調用了閉包，`1`作為參數。

讓我們更深層的解析`call_with_one`的簽名：

```rust
fn call_with_one<F>(some_closure: F) -> i32
#    where F : Fn(i32) -> i32 {
#    some_closure(1) }
```

我們獲取一個參數，而它有類型`F`。我們也返回一個`i32`。這一部分並不有趣。下一部分是：

```rust
# fn call_with_one<F>(some_closure: F) -> i32
    where F : Fn(i32) -> i32 {
#   some_closure(1) }
```

因為`Fn`是一個trait，我們可以用它限制我們的泛型。在這個例子中，我們的閉包取得一個`i32`作為參數並返回`i32`，所以我們用泛型限制是`Fn(i32) -> i32`。

還有一個關鍵點在於：因為我們用一個trait限制泛型，它會是單態的，並且因此，我們在閉包中使用靜態分發。這是非常簡單的。在很多語言中，閉包固定在heap上分配，所以總是進行動態分發。在Rust中，我們可以在stack上分配我們閉包的環境，並靜態分發調用。這經常發生在迭代器和它們的適配器上，它們經常取得閉包作為參數。

當然，如果我們想要動態分發，我們也可以做到。trait對象處理這種情況，通常：

```rust
fn call_with_one(some_closure: &Fn(i32) -> i32) -> i32 {
    some_closure(1)
}

let answer = call_with_one(&|x| x + 2);

assert_eq!(3, answer);
```

現在我們取得一個trait對象，一個`&Fn`。並且當我們將我們的閉包傳遞給`call_with_one`時我們必須獲取一個引用，所以我們使用`&||`。

## 函數指針和閉包

一個函數指針有點像一個沒有環境的閉包。因此，你可以傳遞一個函數指針給任何函數除了作為閉包參數，下面的代碼可以工作：

```rust
fn call_with_one(some_closure: &Fn(i32) -> i32) -> i32 {
    some_closure(1)
}

fn add_one(i: i32) -> i32 {
    i + 1
}

let f = add_one;

let answer = call_with_one(&f);

assert_eq!(2, answer);
```

在這個例子中，我們並不是嚴格的需要這個中間變量`f`，函數的名字就可以了：

```rust
let answer = call_with_one(&add_one);
```

## 返回閉包（Returning closures）

對於函數式風格代碼來說在各種情況返回閉包是非常常見的。如果你嘗試返回一個閉包，你可能會得到一個錯誤。在剛接觸的時候，這看起來有點奇怪，不過我們會搞清楚。當你嘗試從函數返回一個閉包的時候，你可能會寫出類似這樣的代碼：

```rust
fn factory() -> (Fn(i32) -> i32) {
    let num = 5;

    |x| x + num
}

let f = factory();

let answer = f(1);
assert_eq!(6, answer);
```

編譯的時候會給出這一長串相關錯誤：

```text
error: the trait `core::marker::Sized` is not implemented for the type
`core::ops::Fn(i32) -> i32` [E0277]
fn factory() -> (Fn(i32) -> i32) {
                ^~~~~~~~~~~~~~~~
note: `core::ops::Fn(i32) -> i32` does not have a constant size known at compile-time
fn factory() -> (Fn(i32) -> i32) {
                ^~~~~~~~~~~~~~~~
error: the trait `core::marker::Sized` is not implemented for the type `core::ops::Fn(i32) -> i32` [E0277]
let f = factory();
    ^
note: `core::ops::Fn(i32) -> i32` does not have a constant size known at compile-time
let f = factory();
    ^
```

為了從函數返回一些東西，Rust 需要知道返回類型的大小。不過`Fn`是一個 trait，它可以是各種大小(size)的任何東西。比如說，返回值可以是實現了`Fn`的任意類型。一個簡單的解決方法是：返回一個引用。因為引用的大小(size)是固定的，因此返回值的大小就固定了。因此我們可以這樣寫：

```rust
fn factory() -> &(Fn(i32) -> i32) {
    let num = 5;

    |x| x + num
}

let f = factory();

let answer = f(1);
assert_eq!(6, answer);
```

不過這樣會出現另外一個錯誤：

```text
error: missing lifetime specifier [E0106]
fn factory() -> &(Fn(i32) -> i32) {
                ^~~~~~~~~~~~~~~~~
```

對。因為我們有一個引用，我們需要給它一個生命週期。不過我們的`factory()`函數不接收參數，所以省略不能用在這。我們可以使用什麼生命週期呢？`'static`：

```rust
fn factory() -> &'static (Fn(i32) -> i32) {
    let num = 5;

    |x| x + num
}

let f = factory();

let answer = f(1);
assert_eq!(6, answer);
```

不過這樣又會出現另一個錯誤：

```text
error: mismatched types:
 expected `&'static core::ops::Fn(i32) -> i32`,
    found `[closure@<anon>:7:9: 7:20]`
(expected &-ptr,
    found closure) [E0308]
         |x| x + num
         ^~~~~~~~~~~

```

這個錯誤讓我們知道我們並沒有返回一個`&'static Fn(i32) -> i32`，而是返回了一個`[closure <anon>:7:9: 7:20]`。等等，什麼？

因為每個閉包生成了它自己的環境`struct`並實現了`Fn`和其它一些東西，這些類型是匿名的。它們只在這個閉包中存在。所以Rust把它們顯示為`closure <anon>`，而不是一些自動生成的名字。

這個錯誤也指出了返回值類型期望是一個引用，不過我們嘗試返回的不是。更進一步，我們並不能直接給一個對象`'static`聲明週期。所以我們換一個方法並通過`Box`裝箱`Fn`來返回一個 trait 對象。這個*幾乎*可以成功運行：

```rust
fn factory() -> Box<Fn(i32) -> i32> {
    let num = 5;

    Box::new(|x| x + num)
}
# fn main() {
let f = factory();

let answer = f(1);
assert_eq!(6, answer);
# }
```

這還有最後一個問題：

```text
error: closure may outlive the current function, but it borrows `num`,
which is owned by the current function [E0373]
Box::new(|x| x + num)
         ^~~~~~~~~~~
```

好吧，正如我們上面討論的，閉包借用他們的環境。而且在這個例子中。我們的環境基於一個stack分配的`5`，`num`變量綁定。所以這個借用有這個stack幀的生命週期。所以如果我們返回了這個閉包，這個函數調用將會結束，stack幀也將消失，那麼我們的閉包指向了被釋放的內存環境！再有最後一個修改，我們就可以讓它運行了：

```rust
fn factory() -> Box<Fn(i32) -> i32> {
    let num = 5;

    Box::new(move |x| x + num)
}
# fn main() {
let f = factory();

let answer = f(1);
assert_eq!(6, answer);
# }
```

通過把內部閉包添加`move`關鍵字，我們強制閉包使用 move 的方式捕獲環境變量。因為這裡的 num 類型是 i32，實際上這裡的 move 執行的是 copy, 這樣一來，閉包就不再擁有指向環境的指針，而是完整擁有了被捕獲的變量。並允許它離開我們的stack幀。

> ### 這部分引用自[The Rust Programming Language中文版](https://github.com/KaiserY/rust-book-chinese/blob/master/content/Closures%20%E9%97%AD%E5%8C%85.md)
