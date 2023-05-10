# Rust 生命週期 (Lifetime)

## 介紹(幹話)

- 變數 從出生到死亡的時間段

```rust
fn main () {
    let x = Box::new(5); // x 出生
    println!("{:?}", x);
    {
        let y = Box::new(1); // y 出生
        println!("{:?}", y);
    } // y 死亡
    // cannot find value `y` in this scope
    // y 死掉了，所以你存取不到他
    println!("{:?}", y);
} // x 死亡
```

## Borrow checker

- 編譯器的機制
- 會檢查借用者的生命週期會不會活的比擁有者久
- 為了避免 null pointer 發生，就是擁有者已經死了，Value 已經被銷毀了，但借用者還活著，就會存取到不存在的東西

```rust
#[allow(unused_variables, unused_assignments)]
fn main () {
    let x; // x 出生
    {
        let y = Box::new(1); // y 出生
        x = &y; // x 借用 y 的所有權
        println!("{:?}", y);
    } // y 死亡
    // `y` does not live long enough
    // y 死掉了，所以 x 存取不到他 (1編譯器：可憐的 y 他活的不夠久 owo)
    println!("{:?}", x);
} // x 死亡
```

## 生命週期標示

- 在名字前面加個 `'` ，就是生命週期的標示
- 以剛剛的例子來說

```rust
fn main () {
    test();
}

// 生命週期標示，必須像泛型一樣，在 function 簽名中先被宣告
fn test<'a, 'b> () {
    let x: &'a i32 = &5; // 'a 開始
    println!("{:?}", x);
    {
        let y: &'b i32 = &2; // 'b 開始
        println!("{:?}", y);
    } // 'b 結束
} // 'a 結束
```

- 不必要標生命週期的情況

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
// 因為 傳入值 與 回傳值 只有一個
// 不會造成編譯器需要檢查生命週期的問題
// 所以沒有必要標示生命週期
fn life_again_gun (y: &mut Person) -> &mut Person {
    y.age = 0;
    y
}
fn main () {
    let mut x = Person { age: 16 };
    let y = life_again_gun(&mut x);
    println!("{:?}", y);
}
```

- 必須要標生命週期的情況

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
// missing lifetime specifier
// 因為編譯器看不出回傳的 借用者 是不是會超過 擁有者 的 lifetime
// 所以要求你編上 lifetime
fn the_older (x: &Person, y: &Person) -> &Person {
    if x.age > y.age { x } else { y }
}
fn main () {
    
}
#[derive(Debug)]
struct Person {
    age: i32
}
// 我們預期這裡只會有一種生命週期
fn the_older<'a> (x: &'a Person, y: &'a Person) -> &'a Person {
    if x.age > y.age { x } else { y }
}
fn main () {
    let x = Person { age: 16 };
    let y = Person { age: 17 };
    let res = the_older(&x, &y);
    println!("{:?}", res)
}
```

- 指定多個生命週期，並標示哪個生命週期比較長

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
// 我們有兩個生命週期 'a 與 'b，其中 'b 活的比 'a 久
fn the_older<'a, 'b: 'a> (x: &'a Person, y: &'b Person) -> &'a Person {
    if x.age > y.age { x } else { y }
}
fn main () {
    let x = Person { age: 16 };
    let res;
    {
        let y = Person { age: 17 };
        res = the_older(&x, &y);
        println!("{:?}", res);
    }
}
```

## NLL (Non-Lexical-Lifetime)

### Lexical-Lifetime

- 是指說生命週期與變數的作用域是綁定在一起的
- 舉個例子

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
fn birthday (y: &mut Person) {
    y.age = y.age + 1;
}
fn life_again_gun (y: &mut Person) -> &mut Person {
    y.age = 0;
    y
}
fn main () {
    let mut x = Person { age: 16 };
    let y = life_again_gun(&mut x);
    // 在 Lexical-Lifetime 的情況，y 的生命週期沒有結束
    // 所以 y 還在進行可變借用
    // 那理論上 x 就不可以再度可變出借
    // (NLL 好像已經是標準了，所以我無法實現 LL 的編譯錯誤)
    birthday(&mut x);
    println!("{:?}", x);
}
```

### Non-Lexical-Lifetime

- borrow checker 的分析結構方式從 AST 轉向 MIR
  - AST 是抽象語法樹，它會以樹狀的形式表現程式語言的語法結構，因為舊的 borrow checker 用 AST 做分析，所以會造成生命週期與作用域掛鉤
  - MIR 是中間表達式，他在編譯器內部會有像是流程圖的資料結構，用流程控制的方式去分析生命週期
  - 只要變數在後面的程式碼中，沒有機會被使用到，就會提早被結束生命週期
- NLL 將作用域與生命週期拆開來看了
- NLL 縮短了過長的生命週期 (縮減了變數的生命)，讓程式不會充滿一堆 block 去迴避 LL 造成的問題
- 舉例來說

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
fn birthday (y: &mut Person) {
    y.age = y.age + 1;
}
fn life_again_gun (y: &mut Person) -> &mut Person {
    y.age = 0;
    y
}
fn main () {
    let mut x = Person { age: 16 };
    let y = life_again_gun(&mut x);
    // 在 Non-Lexical-Lifetime 的情況
    // y 在這段程式碼的後面都沒有被使用到
    // y 的生命週期就結束了
    // 那這裡就不會有問題
    birthday(&mut x);
    println!("{:?}", x);
}
```

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
fn birthday (y: &mut Person) {
    y.age = y.age + 1;
}
fn life_again_gun (y: &mut Person) -> &mut Person {
    y.age = 0;
    y
}
fn main () {
    let mut x = Person { age: 16 };
    let y = life_again_gun(&mut x);
    // cannot borrow `x` as mutable more than once at a time
    // 但如果 y 在後面有機會被使用到
    // 就代表 y 的生命週期還沒有結束
    // 所以 x 不可以再度進行可變出借
    birthday(&mut x);
    y.age = 16;
    println!("{:?}", x);
}
```

---

## Borrow 的存活時間

出處: https://ithelp.ithome.com.tw/articles/10200106

Rust 有個重要的功能叫 borrow checker ，它除了檢查在上一篇提到的規則外，還檢查使用者會不會使用到懸空參照 (dangling reference) ，懸空參照是在電腦世界中一種現象： 如果你今天把一個變數借給別人，實際上借走的人只是知道我可以去哪裡找到這個別人借我的東西而已，那個東西的擁有者還是你本人，以現實世界做比喻的話，這像是借別人東西只是把放那個東西的儲物櫃位置，以及鑰匙暫時的交給別人而已，送別人東西則是直接把儲物櫃的擁有者變成他。

所以如果今天發生了一種情況，你把東西借給別人後，管理每個儲物櫃擁有者的系統馬上把你的使用權收回去呢？會發生什麼事，這沒人說的準，可能儲物櫃還沒被清空，你還是可以拿到借來的東西，或是馬上又換了主人，你已經不是拿到原本的東西了，就像以下的程式碼：

```rust
fn foo() ->&i32 {
  // 這個變數在離開這個範圍後就消失了
  let a = 42;
  // 但是這邊卻回傳了 borrow
  &a
}
```

上面這段 code 是無法編譯的。

為瞭解決這樣的一個問題， Rust 提出來的就是 lifetime 的觀念，只要函式的參數或回傳值有 borrow 出現，使用者就要幫 borrow 標上 lifetime ，標記後讓編譯器可以去追蹤每個變數借出去與釋放掉的情況，確保不會有釋放掉已經出借的變數的可能性。

Rust 使用 `'a` 一個單引號加上一個識別字當作 lifetime 的標記，所以這些都是可以的 `'b`, `'foo`, `'_bar` ，此外有兩個保留用作特殊用途的 lifetime: `'static` 和 `'_`：

- `'static`： 這代表這是個整個程式都有效的 borrow 比如字串常數 `"foo"` 它的 lifetime 就是 `'static`
- `'_`：這是保留給 Rust 2018 使用的，這裡先不提它的功能

這邊是個加上 lifetime 標記後的範例：

```rust
fn foo<'a>(a: &'a i32) -> &'a i32 {
  a
}
```

其中我們必須在函式名稱後加上 `<>` 並在其中宣告我們的 lifetime ，接著把 borrow 的 `&` 後都加上我們的 lifetime 標記，但事實上在上一篇文章中，我們完全沒用使用到 lifetime ， Rust 可以在某些情況下自動推導出正確的 lifetime ，使得實際上需要手動標註的情況並不多，最有可能遇到的情況是一個函式同時使用了兩個 borrow ：

```rust
fn max<'a>(a: &'a i32, b: &'a i32) -> &'a i32 {
  if a > b {
    a
  } else {
    b
  }
}

fn main() {
  let a = 3;
  let m = &a;
  {
    let b = 2;
    let n = &b;
    // 對於 max 來說， m 與 n 同時存活的這個範圍就是 'a ，
    // 而回傳值也可以在這個範圍內使用
    println!("{}", max(m, n));
  } // b 與 n 會在這邊消失
} // a 與 m 會在這邊消失
```

這種情況編譯器因為看到了兩個 borrow ，於是沒辦法猜出來回傳的值應該要跟哪個 lifetime 一樣，這邊的作法就是全部都標記一樣的 lifetime ，讓 Rust 知道說我們的變數都會存活在同一個範圍內，同時回傳值也可以在同樣的範圍存活。

大部份的情況下編譯器都能自動的推導，所以需要手動標註的情況其實不多，通常是先嘗試讓編譯器做推導，如果編譯器報錯了才來想辦法標註。

lifetime 還有個用途是用來限制使用者傳入的參數必須是常數：

```rust
fn print_message(message: &'static str) {
  println!("{}", message);
}
```

這個函式就只能接受如 `"Hello"` 這樣的常數了，雖說只是偶爾會有這樣的需求。

## Lifetime Elision (Lifetime 省略規則) (進階)

這部份大概的瞭解一下就好了

1. 所有的 borrow 都會自動的分配一個 lifetime

```rust
fn foo(a: &i32, b: &i32);
fn foo<'a, 'b>(a: &'a i32, b: &'b i32); // 推導結果
```

1. **如果函式只有一個 borrow 的參數，則它的 lifetime 會自動被應用到回傳值上**

```rust
fn foo(a: &i32);
fn foo<'a>(a: &'a i32) -> &'a i32; // 推導結果
```

1. 如果有多個 borrow ，但其中一個是 `self` ，則 `self` 的 lifetime 會被應用在回傳值

```rust
impl Foo {
  fn method(&self, a: &i32) -> &Self {
  }
}

// 推導結果
impl Foo {
  fn method<'a, 'b>(&'a self, b: &'b i32) -> &'a Self {
  }
}
```

若不符合上面任一條規則，則必須要標註型態。

如果我們把以上的規則套用在上面的範例 `max` 上：

```rust
fn max(a: &i32, b: &i32) -> &i32 {
  if a > b {
    a
  } else {
    b
  }
}
```

套用規則 1 ：

```rust
fn max<'a, 'b>(a: &'a, i32, b: &'b i32) -> &i32 {
  if a > b {
    a
  } else {
    b
  }
}
```

到這邊結束，編譯器已經沒有可用的規則了，但是回傳值的 lifetime 依然是未知，於是就編譯失敗。
