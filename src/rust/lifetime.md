# Rust 生命周期 (Lifetime)

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
- 會檢查借用者的生命周期會不會活的比擁有者久
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

## 生命周期標示

- 在名字前面加個 `'` ，就是生命周期的標示
- 以剛剛的例子來說

```rust
fn main () {
    test();
}

// 生命周期標示，必須像泛型一樣，在 function 簽名中先被宣告
fn test<'a, 'b> () {
    let x: &'a i32 = &5; // 'a 開始
    println!("{:?}", x);
    {
        let y: &'b i32 = &2; // 'b 開始
        println!("{:?}", y);
    } // 'b 結束
} // 'a 結束
```

- 不必要標生命周期的情況

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
// 因為 傳入值 與 回傳值 只有一個
// 不會造成編譯器需要檢查生命周期的問題
// 所以沒有必要標示生命周期
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

- 必須要標生命周期的情況

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
// 我們預期這裡只會有一種生命周期
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

- 指定多個生命周期，並標示哪個生命周期比較長

```rust
#[derive(Debug)]
struct Person {
    age: i32
}
// 我們有兩個生命周期 'a 與 'b，其中 'b 活的比 'a 久
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

- 是指說生命周期與變數的作用域是綁定在一起的
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
    // 在 Lexical-Lifetime 的情況，y 的生命周期沒有結束
    // 所以 y 還在進行可變借用
    // 那理論上 x 就不可以再度可變出借
    // (NLL 好像已經是標準了，所以我無法實現 LL 的編譯錯誤)
    birthday(&mut x);
    println!("{:?}", x);
}
```

### Non-Lexical-Lifetime

- borrow checker 的分析結構方式從 AST 轉向 MIR
  - AST 是抽象語法樹，它會以樹狀的形式表現程式語言的語法結構，因為舊的 borrow checker 用 AST 做分析，所以會造成生命周期與作用域掛鉤
  - MIR 是中間表達式，他在編譯器內部會有像是流程圖的資料結構，用流程控制的方式去分析生命周期
  - 只要變數在後面的程式碼中，沒有機會被使用到，就會提早被結束生命周期
- NLL 將作用域與生命周期拆開來看了
- NLL 縮短了過長的生命周期 (縮減了變數的生命)，讓程式不會充滿一堆 block 去迴避 LL 造成的問題
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
    // y 的生命周期就結束了
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
    // 就代表 y 的生命周期還沒有結束
    // 所以 x 不可以再度進行可變出借
    birthday(&mut x);
    y.age = 16;
    println!("{:?}", x);
}
```

