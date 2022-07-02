## 學習順序

Rust 是一個學習曲線比較陡峭的語言，即使有其他語言基礎，如果沒有先讀書，而是直接上，那在 compile 階段就會有很多挫折並且無法理解。以下是我覺得對已經有其他語言基礎的人，用這樣的學習順序是不錯的

1. [Rust 語言之旅](https://tourofrust.com/TOC_zh-tw.html)：1 - 3 天就可以走完，並且因為是使用 playground，可以同時改改他的範例額外觀察一些自己有興趣的行為。走完之後大概會對於 Rust 與其他語言的差別有些感覺
2. [Rust book](https://doc.rust-lang.org/book/)：Offical 的教學文，雖然寫的不算瑣碎，但若一開始就看這個可能還是會讓人失去耐心，畢竟一次會累績接收太多新東西。如果已經有了步驟 1，對於 Rust 跟其他語言的異同有感覺，那很多部分就可以參照其他本來就會的語言，因此有一個立足點，比較不會太挫折並失去耐心。不一定要一行一行看的很仔細，因為其實畢竟光看也會真的懂，所以就只是大概知道有哪些東西有個印象就行。可能會花到一週以上的時間，取決於看得多仔細以及多久失去耐心… 和下一步的 [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html) 順序可能可以調換，看你的習慣是比較喜歡讀書還是看 code…，如果很不愛讀文字的話甚至也可以跳過 Rust book，直接從 [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html) 開始也可以，如果有 Example 看不懂的地方再來翻翻看 Rust book
3. [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)：一些基礎 pattern 的範例，可以熟悉 Rust 語法和他的一些特別設計，尤其如 [Enum](https://doc.rust-lang.org/stable/rust-by-example/custom_types/enum/testcase_linked_list.html)、`match`、[Closure](https://doc.rust-lang.org/stable/rust-by-example/fn/closures.html)… 等等其他語言可能也有，但 Rust 卻在其上花更多功夫的部分。全部大概 3 天以內可以看完。如果有無法理解的地方，可能還是要回去翻 [Rust book](https://doc.rust-lang.org/book/)

到這裡就結束了讀書階段，總共花了 1~2 週的時間，往下就是練習了

1. [Chest sheet](https://cheats.rs/)：可以開始上工了，學習語言這種東西是沒辦法只用看的，開始著手寫 project 才能真的學會，寫的過程就可以快速用這個 Chest sheet 查看語法，大部分在 [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html) 介紹到的 pattern 都有被以一行簡潔的收錄在 Chest sheet，反過來說，若看了 Chest sheet 還是有疑惑，可以回去翻 [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)
2. [rustlings](https://github.com/rust-lang/rustlings/)：Rust 官方提供的練習，可以開始練習小程式，範圍有可能是單一 [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)，也有可能是複合。其實 rustlings 基本上就是 [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)，只是之前 Rust by Example 你可能就只是光看，透過 rustlings 你可以真的動手寫一次，過程中 [Chest sheet](https://cheats.rs/) 就是好幫手
3. [Rust Algorithm Club](https://rust-algo.club/index.html)：基礎演衣料結構和算法的實作
4. [Rust cookbook](https://rust-lang-nursery.github.io/rust-cookbook/)：完成之前的步驟之後，你基本上已經可以用 Rust 完成大部分的需求，但可以進一步再讀這個 Rust cookbook。他是官方收集了常用的情境，示範最專業的寫法。在往後你的實際專案中，你的程式的需求一定都用得到這些東西，也就是說當成為一個職業 Rust developer，[Chest sheet](https://cheats.rs/)、[Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)、[Rust cookbook](https://rust-lang-nursery.github.io/rust-cookbook/) 就是三個開在旁邊隨時參考的東西。其實，如果是其他語言，當想找什麼語法我們可能都會選擇直接 Google，然後就會看到吐出 Stack Overflow 的結果可以直接參考，不過可能 Rust 是一個相對新的語言，加上他的學習曲線比較陡峭，所以 Stack Overflow 的回答可能會出現不太正確或者過於模糊的狀況，所以才建議從官方資源出發，扎實一點的學，往後就可以更有能力判斷別人的回答是對是錯。也不用全看啦，瀏覽一下他有哪些範例，然後挑幾個有興趣看一下就可以，之後真的開始寫專案，要來複製貼上的時候，再來把他看懂就可以
5. 另外也有非官方的練習如 [Exercism](https://exercism.io/my/tracks/rust) 提供更進階的題目。LeetCode 也有 Rust 啦，不過他畢竟主要是 for 面試情境，所以是以思考演算法為主要導向的，因此用高階一點的語言去刷比如 Python, Java 還是比較適合的。Rust 作為一個 system programming language，直接用它來開始寫 system application 就很好
6. 可以開始寫完整的 project 了，如果沒有主題的話，可以從 [Rust book 建議的](https://doc.rust-lang.org/book/ch20-00-final-project-a-web-server.html) 開始

------

## Chest sheet

[Chest sheet](https://cheats.rs/)

### Reference

- [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)
- [Rust cookbook](https://rust-lang-nursery.github.io/rust-cookbook/)
- [Rust Algorithm Club](https://rust-algo.club/index.html)
- [Official std](https://doc.rust-lang.org/std/)

### Data Type

#### Basic

- integer

  > Length Signed Unsigned
  > 8-bit `i8` `u8`
  > 16-bit `i16` `u16`
  > 32-bit `i32`(default) `u32`
  > 64-bit `i64` `u64`
  > 128-bit `i128` `u128`
  > arch `isize` `usize`

- float: `f32`, `f64`(default)

- `bool`

- `char`: Fixed 4 bytes in size and represents a Unicode Scalar Value

#### Advanced

- **Tuple**: `()` Fixed length. Group different types.

```rust
fn main() {
    let tup: (i32, f64, u8) = (500, 6.4, 1);
}
```



```rust
let tup = (500, 6.4, 1);
let (x, y, z) = tup; // it's copying, not moving because it's on stack
```



```rust
let x: (i32, f64, u8) = (500, 6.4, 1);
let five_hundred = x.0;
let six_point_four = x.1;
```

- **Array**: `[]` Same type. Fixed length

```rust
let a = [1, 2, 3, 4, 5];

let a: [i32; 5] = [1, 2, 3, 4, 5];
let a = [3; 5]; //[3 ,3 ,3, 3, ,3]

let a = [1, 2, 3, 4, 5];
let first = a[0];
let second = a[1];
```

- [Vector](https://chungchris.github.io/2021/06/30/software/language/rust-note/#toc-heading-18)
- [string](https://chungchris.github.io/2021/06/30/software/language/rust-note/#toc-heading-12)
- [HashMap](https://chungchris.github.io/2021/06/30/software/language/rust-note/#toc-heading-19)

------

> 往下是我自己補充 Chest sheet 中沒有的，或者一些比較難懂的概念

## Borrowing

Rust 的 `*` 和 `&` 在一開始不建議直接用 C 的方式來理解，而建議理解為 `&` 表達的是 `借用`，而不是 `取址`。
雖然其實基礎上就都是 reference，所以以底層來說實際上跟 C 差異不大，只是語法上如果直接想成跟 C 一樣，那會有好些 compile error 無法順利理解。



```rust
struct Foo {
    x: i32,
}

fn do_something(f: Foo) {
    println!("{}", f.x);
    // f is dropped here
}

fn main() {
    let mut foo = Foo { x: 42 };
    let f = &mut foo;

    // FAILURE: do_something(foo) would fail because
    // foo cannot be moved while mutably borrowed

    // FAILURE: foo.x = 13; would fail here because
    // foo is not modifiable while mutably borrowed

    f.x = 13;
    // f is dropped here because it's no longer used after this point
    
    println!("{}", foo.x);
    
    // this works now because all mutable references were dropped
    foo.x = 7;
    
    // move foo's ownership to a function
    do_something(foo);
}
```

- Rust 只允許 一個 mut reference 或者 多個 unmut reference，但不會同時發生
- 一個 reference 絕對不能活得比它的擁有者還長

對於借用而來的變數，操作時會使用到 `*`，雖然也叫做 `dereferencing`，但在 rust 來說一樣是要用 ownership 的概念來準確理解。

```rust
fn main() {
    let mut foo = 42;
    let f = &mut foo;
    let bar = *f; // get a copy of the owner's value
    *f = 13;      // set the reference's owner's value
    println!("{}", bar);
    println!("{}", foo);
}
```

注意 `let bar = *f` 是讓 bar 得到 f 的值的複製品，前提是 f 的型別有 Copy 屬性。

### Example

Borrow checker 其實是個大魔王，他非常嚴格，可以寫寫這一題例子就會更有感覺
[[LeeCode\] #19 Remove Nth Node From End of List](https://chungchris.github.io/2021/07/09/software/leecode/Remove-Nth-Node-From-End-of-List/#toc-heading-5)

------

## Lifetime

Lifetime 就是為了 borrow checker 而存在，確保一個 reference 一定不會 refer 到一塊已經死掉的實體。大部分的狀況都 Elision，編譯器會幫忙補上，但編譯器無法判斷的狀況自然就要自己寫

```rust
// `print_refs` takes two references to `i32` which have different
// lifetimes `'a` and `'b`. These two lifetimes must both be at
// least as long as the function `print_refs`.
fn print_refs<'a, 'b>(x: &'a i32, y: &'b i32) {
    println!("x is {} and y is {}", x, y);
}

// A function which takes no arguments, but has a lifetime parameter `'a`.
fn failed_borrow<'a>() {
    let _x = 12;

    // ERROR: `_x` does not live long enough
    let y: &'a i32 = &_x;
    // Attempting to use the lifetime `'a` as an explicit type annotation 
    // inside the function will fail because the lifetime of `&_x` is shorter
    // than that of `y`. A short lifetime cannot be coerced into a longer one.
}

fn main() {
    // Create variables to be borrowed below.
    let (four, nine) = (4, 9);
    
    // Borrows (`&`) of both variables are passed into the function.
    print_refs(&four, &nine);
    // Any input which is borrowed must outlive the borrower. 
    // In other words, the lifetime of `four` and `nine` must 
    // be longer than that of `print_refs`.
    
    failed_borrow();
    // `failed_borrow` contains no references to force `'a` to be 
    // longer than the lifetime of the function, but `'a` is longer.
    // Because the lifetime is never constrained, it defaults to `'static`.
}
```

`fn failed_borrow<'a>()` 代表 `'a` 這個 lifetime 要 >= `failed_borrow()` 這個 funtcion 的 lifetime
但 `main()` 裡面呼叫到 `failed_borrow()` 的時候，沒有指定 `'a` 是什麼，那就預設 `'a` 就是 `'static`，而 `'static` 這個 lifetime 一定 >= `failed_borrow()` 的 lifetime

`fn print_refs<'a, 'b>(x: &'a i32, y: &'b i32)` 規範 `print_refs()` 這個 function 的 lifetime，一定要 <= `'a`,`'b` 這兩個 lifetime，也就是他的兩個參數的 lifetime

### Coercion

```rust
// Here, Rust infers a lifetime that is as short as possible.
// The two references are then coerced to that lifetime.
fn multiply<'a>(first: &'a i32, second: &'a i32) -> i32 {
    first * second
}
```

`first` `second` 兩個參數的 lifetime 不見得相同，但會取其小者，有就是 `multiply()` 這個 function 的 lifetime 一定要小於等於其兩個參數之中 lifetime 更小的那個

### static

- 一個靜態變量是在編譯時間就被產生的記憶體資源，它從程式一開始就存在，直到結束
- 一定要明確的表示型別
- 永遠不會被 `drop`
- 如果靜態生命週期資源包含了 reference，那它們必須都得是 `static`



- 修改靜態變量本質上就是危險的，因為任何人在任何地方都可以存取它們，而這有可能會造成 data racing
- Rust 允許使用 `unsafe { ... }` 操作一些編譯器無法確保的記憶體行為

------

## Collections- string

`utf-8`，有 1-4 個 bytes 的*可變長度*

```rust
fn main() {
    let a = "hi 🦀";
    println!("{}", a.len());
    let first_word = &a[0..2]; // 2 bytes => 2 Eng chars
    let second_word = &a[3..7]; // 4 bytes => 1 emoji
    // let half_crab = &a[3..5]; FAILS
    // Rust does not accept slices of invalid unicode characters
    println!("{} {}", first_word, second_word);
}
```

```bash
7
hi 🦀
```

因為可變長度的關係，查找字元時無法快速地以 `O(1)` 常數時間用索引完成，例如以 `my_text[3]` 取得第 4 個元)。取而代之的是必定得迭代整個 `utf-8` 位元序列，才有辦法知道各個 char 的開始點，所以是 `O(n)` 線性時間

### push_str, +, to_uppercase, to_lowercase, trim, replace, concat, join

```rust
fn main() {
    let mut helloworld = String::from("hello");
    helloworld.push_str(" world");
    helloworld = helloworld + "!";
    println!("{}", helloworld);
    println!("{}", helloworld.to_uppercase());
    println!("{}", helloworld.trim()); // 切除空白
    println!("{}", helloworld.replace("world", "taiwan"));

    let helloworld = ["hello", " ", "world", "!"].concat();
    let abc = ["a", "b", "c"].join(",");
    println!("{}", helloworld);
    println!("{}",abc);
}
```

```bash
hello world!
HELLO WORLD!
hello world!
hello taiwan!
hello world!
a,b,c
```

### to_string, parse

```rust
fn main() -> Result<(), std::num::ParseIntError> {
    let a = 42;
    let a_string = a.to_string();
    let b = a_string.parse::<i32>()?;
    println!("{} {}", a, b);
    Ok(())
}
```

### format!

```rust
format!("Hello");                 // => "Hello"
format!("Hello, {}!", "world");   // => "Hello, world!"
format!("The number is {}", 1);   // => "The number is 1"
format!("{:?}", (3, 4));          // => "(3, 4)"
format!("{value}", value=4);      // => "4"
format!("{} {}", 1, 2);           // => "1 2"
format!("{:04}", 42);             // => "0042" with leading zeros
format!("{:#?}", (100, 200));     // => "(
                                  //       100,
                                  //       200,
                                  //     )"
```

[more…](https://doc.rust-lang.org/std/fmt/)

### include_str

如果你有一些非常長的文字，可以考慮使用 marco `include_str!` 將 string 從 file 讀到程式裡

```rust
let hello_html = include_str!("hello.html");
```

### chars

Rust 提供了一個方法可以取得一個 `utf-8` 位元組的字元向量，它的型別是 `char`。一個 `char` 的大小永遠是 4 bytes

```rust
fn main() {
    // collect the characters as a vector of char
    let chars = "hi 🦀".chars().collect::<Vec<char>>();
    println!("{}", chars.len()); // should be 4
    // since chars are 4 bytes we can convert to u32
    println!("{}", chars[3] as u32);
}
```

`string` 的 `chars()` 方法將 string 分離為各個有意義的 character，並放入空間一律為 4 bytes 的 `char` 型別中，串成一個 `Vec` 回傳。

```rust
for c in my_str.chars() { 
    // do something with `c`
}

for (i, c) in my_str.chars().enumerate() {
    // do something with character `c` and index `i`
}
```

------

## Collections- Vector

- can only store values of the same type
- puts all the values next to each other in memory

```rust
fn main() {
    // Iterators can be collected into vectors
    let collected_iterator: Vec<i32> = (0..10).collect();
    println!("Collected (0..10) into: {:?}", collected_iterator);

    // The `vec!` macro can be used to initialize a vector
    let mut xs = vec![1 i32, 2, 3];
    println!("Initial vector: {:?}", xs);

    // Insert new element at the end of the vector
    println!("Push 4 into the vector");
    xs.push(4);
    println!("Vector: {:?}", xs);

    // Error! Immutable vectors can't grow
    collected_iterator.push(0);
    // FIXME ^ Comment out this line

    // The `len` method yields the number of elements currently stored in a vector
    println!("Vector length: {}", xs.len());

    // Indexing is done using the square brackets (indexing starts at 0)
    println!("Second element: {}", xs[1]);

    // `pop` removes the last element from the vector and returns it
    println!("Pop last element: {:?}", xs.pop());

    // Out of bounds indexing yields a panic
    println!("Fourth element: {}", xs[3]);
    // FIXME ^ Comment out this line

    // `Vector`s can be easily iterated over
    println!("Contents of xs:");
    for x in xs.iter() {
        println!("> {}", x);
    }

    // A `Vector` can also be iterated over while the iteration
    // count is enumerated in a separate variable (`i`)
    for (i, x) in xs.iter().enumerate() {
        println!("In position {} we have value {}", i, x);
    }

    // Thanks to `iter_mut`, mutable `Vector`s can also be iterated
    // over in a way that allows modifying each value
    for x in xs.iter_mut() {
        *x *= 3;
    }
    println!("Updated vector: {:?}", xs);
}
```

------

## Collections- HashMap

All of the keys must have the same type, and all of the values must have the same type. Any type that implements the `Eq` and `Hash` traits can be a key in HashMap. This includes:

- `bool` (though not very useful since there is only two possible keys)
- `int`, `uint`, and all variations thereof
- `String` and `&str`
- You can easily implement Eq and Hash for a custom type with just one line: `#[derive(PartialEq, Eq, Hash)]`

```rust
use std::collections::HashMap;

let mut scores = HashMap::new();
// `HashMap::insert()` returns `None`
// if the inserted value is new, `Some(value)` otherwise
scores.insert(String::from("Blue"), 10);
let team_name = String::from("Blue");
let score = scores.get(&team_name);

scores.entry(String::from("Yellow")).or_insert(50); // Only Inserting a Value If the Key Has No Value

for (key, value) in &scores {
    println!("{}: {}", key, value);
}

contacts.remove(&"Yellow"); 

let teams = vec![String::from("Blue"), String::from("Yellow")];
let initial_scores = vec![10, 50];
let mut scores: HashMap<_, _> =
    teams.into_iter().zip(initial_scores.into_iter()).collect();

// `HashMap::iter()` returns an iterator that yields 
// (&'a key, &'a value) pairs in arbitrary order.
for (name, &number) in teams.iter() {
    println!("Calling {}: {}", name, call(number)); 
}
```

### HashSet

Consider a HashSet as a HashMap where we just care about the keys ( `HashSet<T>` is, in actuality, just a wrapper around `HashMap<T, ()>`).
A HashSet’s unique feature is that it is guaranteed to not have duplicate elements. That’s the contract that any set collection fulfills. HashSet is just one implementation.

------

## Trait

- 可理解為其他語言（如 python）的 `Interface`
- Trait 裡面的 method 可以有 default 實作，但他無法操作 struct 的 inner fields，也就是說一個 trait 只能定義需要有哪些 method，無法定義需要有哪些成員
- trait 可以繼承另一個 trait (`Supertraits`)：`trait LoudNoiseMaker: NoiseMaker`。代表 `LoudNoiseMaker` 也要有 `NoiseMaker` 規範的所有 method

### Handling Unsized Data

When we want to store them within another struct, traits obfuscate the original struct thus it also obfuscates the original size. Unsized values being stored in structs are handled in two ways in Rust:

- generics - Using parameterized types effectively create struct/functions known types and thus known sizes. 即使用 `impl Trait`
- indirection - Putting instances on the heap gives us a level of indirection that allow us to not have to worry about the size of the actual type and just store a pointer to it. 即使用 `Box<dyn Trait>`

### Trait bound (a.k.a. impl Trait)

```rust
fn animal_talk(a: impl Animal) {
  a.talk();
}
/* same as
fn animal_talk<T>(a: T)
where
    T: Animal
{
  a.talk();
}
*/

fn main() {
  let c = Cat{};
  let d = Dog{};
 
  animal_talk(c);
  animal_talk(d);
}
```

`impl Animal` There is no `&` there. `impl` here makes the compiler determine the type at the compile time. One that takes Dog and another that takes Cat. This is called monomorphization and will not have any runtime overhead.

For example,

```rust
fn animal () -> impl Animal {
  if (is_dog_available()) {
    return Dog {};
  }
  Cat {}
}
```

It fails! because, the types here are determined at the compile time (static dispatch) .

```rust
fn animal() -> Box<dyn Animal> {
  if (is_dog_available()) {
    return Box::new(Dog {});
  } 
    
  Box::new(Cat {})
}
```

This works!

### Static vs Dynamic Dispatch (a.k.a. dyn Trait)

`&dyn NoiseMaker` is a `trait object`. It represents a pointer to the concrete type and a pointer to a vtable of function pointers. (`Box<dyn Animal>`, `Rc<dyn Animal>` are also trait Objects.) A `trait object` is what allows us to indirectly call the correct methods of an instance. A `trait object` is a struct that holds the pointer of our instance with a `list` of function pointers to our instance’s methods. This `list` of functions is known in `C++` as a `vtable`.

```rust
struct SeaCreature {
    pub name: String,
    noise: String,
}

impl SeaCreature {
    pub fn get_sound(&self) -> &str {
        &self.noise
    }
}

trait NoiseMaker {
    fn make_noise(&self);
}

impl NoiseMaker for SeaCreature {
    fn make_noise(&self) {
        println!("{}", &self.get_sound());
    }
}

fn static_make_noise(creature: &SeaCreature) {
    // we know the real type
    creature.make_noise();
}

fn dynamic_make_noise(noise_maker: &dyn NoiseMaker) {
    // we don't know the real type
    noise_maker.make_noise();
}

fn main() {
    let creature = SeaCreature {
        name: String::from("Ferris"),
        noise: String::from("blub"),
    };
    static_make_noise(&creature);
    dynamic_make_noise(&creature);
}
```

Dynamic dispatch is slightly slower because of the pointer chasing to find the real function call.

### Derive

```rust
#[derive(PartialEq, PartialOrd)]
```

讓編譯器自動幫忙補上一些基本的 trait，如下

- Comparison traits: `Eq`, `PartialEq`, `Ord`, `PartialOrd`.
- `Clone`, to create `T` from `&T` via a copy. Introduce `.clone().`
- `Copy`, to give a type ‘copy semantics’ instead of ‘move semantics’. Introct `.copy()`.
- `Hash`, to compute a hash from `&T`.
- `Default`, to create an empty instance of a data type.
- `Debug`, to format a value using the `{:?}` formatter.
- `Add`, `Sub`, inctoduce `+`, `-` operators.
- `Drop`, you can override `.drop()`
- `Iterator`

------

## Rc, Arc, Refcell, Mutex

`Rc`. Reference Count. 用來裝一個 (smart) pointer，如此便提供了 `clone()` 的能力，也就是兩個不同的 pointer 指向同一塊資料。
([為什麼叫 smart pointer 可以參考這裏](https://tourofrust.com/95_zh-tw.html))
為什麼需要這個？記得 Rust 的理念，ownership 基本上只有一個，所以不是 move 就是 borrow，如果不是 move 也不是 borrow，那只能 copy，那實際上就是兩塊獨立的資料自然可以各有各的 ownership。藉由單一擁有者，就可以透過該擁有者的作用域（scope），在正確的時間做 drop 回收記憶體。
但若牽扯到指標，就變成要確保已經沒有任何指標指到某一塊資料，才可以 drop，所以需要導入 `Rc`，只要是透過 Rc clone 的指標都會被記錄，確保在 count 歸零時才把記憶體釋放。

```rust
use std::rc::Rc;

struct Pie;

impl Pie {
    fn eat(&self) {
        println!("tastes better on the heap!")
    }
}

fn main() {
    let heap_pie = Rc::new(Pie);
    let heap_pie2 = heap_pie.clone();
    let heap_pie3 = heap_pie2.clone();

    heap_pie3.eat();
    heap_pie2.eat();
    heap_pie.eat();

    // all reference count smart pointers are dropped now
    // the heap data Pie finally deallocates
}
```

`Refcell` 用來裝一個 (smart) pointer，提供 borrow mutable/immutable references 的能力，好處是 `Refcell` 負責確保 *Only one mutable reference OR multiple immutable references, but not both!*
為什麼需要這個？因為 `Rc` 只提供了複製指標的能力，讓我們可以有複數個指標指向同一塊資料，因此也負責確保了 drop 該資料記憶體的時機。但他沒有確保 mutablility 的部分，同時有兩個活著的 mutable references 指向同一塊資料是危險的。

如下面這例子，`ferris` 和 `sarah` 的 pie 其實是指向同一塊資料，並非擁有各自的 pie

```rust
use std::cell::RefCell;
use std::rc::Rc;

struct Pie {
    slices: u8,
}

impl Pie {
    fn eat_slice(&mut self, name: &str) {
        println!("{} took a slice!", name);
        self.slices -= 1;
    }
}

struct SeaCreature {
    name: String,
    pie: Rc<RefCell<Pie>>,
}

impl SeaCreature {
    fn eat(&self) {
        // use smart pointer to pie for a mutable borrow
        let mut p = self.pie.borrow_mut();
        // take a bite!
        p.eat_slice(&self.name);
    }
}

fn main() {
    let pie = Rc::new(RefCell::new(Pie { slices: 8 }));
    // ferris and sarah are given clones of smart pointer to pie
    let ferris = SeaCreature {
        name: String::from("ferris"),
        pie: pie.clone(),
    };
    let sarah = SeaCreature {
        name: String::from("sarah"),
        pie: pie.clone(),
    };
    ferris.eat();
    sarah.eat();

    let p = pie.borrow();
    println!("{} slices left", p.slices);
}
```

如果說兩個 pointer 會由不同的 thread 擁有，`Rc` 就要換成使用 `Arc`

且如果說會跨 thread，`Refcell` 就變成要使用 `Mutex`。所以經常看到的組合就是

- within thread: `Rc<RefCell<...>>`
- across thread: `Arc<Mutex<...>>`

此時可能會產生一個疑問，在跨 thread 狀況下有 data racing 的風險這我們知道，因此需要導入 Arc 和 Mutex 合理；但若為 single thread 的狀況，需要 Rc 來知道 drop 時機可以理解，不過為何需要 Refcell？既然只有 single thread，怎麼可能會有同一時間存在兩個 mutable reference 的狀況？
會有這個疑問可能是忽略了 Rust 畢竟還是一個與 C 相同層級的語言，他是可以提供記憶體位址等級的操作的。也就是說你可以拿到一個 instance 的 address，並透過該 address 對該 instance 操作。問題是，若透過這樣的方式，這些操作就是不是 compiler 可以追蹤到並且介入規範的，自由當然是自由，但風險就要自負。這種操作在 Rust 叫做 `Unsafe`，比如 dereferencing a raw pointer 操作，只要用 `Unsafe` block 包起來，Rust compiler 就會不管你裡面的操作。因此，如果我們對於 pointer 這種透過指標去操作一塊資料的行為，都透過 `Rc`, `RefCell` 這種 wrapper，那就可以讓 compiler 介入幫我們確保我們對於指標的使用安全，順帶一提，可以想見這個 wrapper 的內部實作終究還是會有 Unsafe block，只是說他在外包了一層，加入了一些 metadata，讓編譯器可以藉由這些 metadata 此來幫助我們追蹤和確保。

## Conversion

透過 impl `From` 或 `Into` 這兩個 traits，可以讓你的 type 擁有 `::from()` 或 `::into()` 的方法來做型別轉換

```rust
use std::convert::From;

#[derive(Debug)]
struct Number {
    value: i32,
}

impl From<i32> for Number {
    fn from(item: i32) -> Self {
        Number { value: item }
    }
}

fn main() {
    let num = Number::from(30);
    println!("My number is {:?}", num);
}
```

```rust
use std::convert::From;

#[derive(Debug)]
struct Number {
    value: i32,
}

impl From<i32> for Number {
    fn from(item: i32) -> Self {
        Number { value: item }
    }
}

fn main() {
    let int = 5;
    // Try removing the type declaration
    let num: Number = int.into();
    println!("My number is {:?}", num);
}
```

`TryFrom`/`TryInto` traits are used for fallible conversions, and as such, return Results.

```rust
use std::convert::TryFrom;
use std::convert::TryInto;

#[derive(Debug, PartialEq)]
struct EvenNumber(i32);

impl TryFrom<i32> for EvenNumber {
    type Error = ();

    fn try_from(value: i32) -> Result<Self, Self::Error> {
        if value % 2 == 0 {
            Ok(EvenNumber(value))
        } else {
            Err(())
        }
    }
}

fn main() {
    // TryFrom

    assert_eq!(EvenNumber::try_from(8), Ok(EvenNumber(8)));
    assert_eq!(EvenNumber::try_from(5), Err(()));

    // TryInto

    let result: Result<EvenNumber, ()> = 8i32.try_into();
    assert_eq!(result, Ok(EvenNumber(8)));
    let result: Result<EvenNumber, ()> = 5i32.try_into();
    assert_eq!(result, Err(()));
}
```

------

## Debug

### print Display

```rust
use std::fmt; // Import the `fmt` module.

// Define a structure named `List` containing a `Vec`.
struct List(Vec<i32>);

impl fmt::Display for List {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // Extract the value using tuple indexing,
        // and create a reference to `vec`.
        let vec = &self.0;

        write!(f, "[")?;

        // Iterate over `v` in `vec` while enumerating the iteration
        // count in `count`.
        for (count, v) in vec.iter().enumerate() {
            // For every element except the first, add a comma.
            // Use the ? operator to return on errors.
            if count != 0 { write!(f, ", ")?; }
            write!(f, "{}", v)?;
        }

        // Close the opened bracket and return a fmt::Result value.
        write!(f, "]")
    }
}

fn main() {
    let v = List(vec![1, 2, 3]);
    println!("{}", v);
}
```

------

## Module

- 一個 *Program* 有一個 `main.rs`，裡面實作 `main()` 方法

- 一個 *Lib* 有一個 root module `lib.rs`，可以再包含數個 module 作為 submodule

- *Program* 或者 *Lib* 都稱為一個 *crate*，是一個 compilation unit，也可以對應到其他語言 package 的概念，是一個導入第三方函式庫的單位，透過 `use` 來導入 namespace

- 一個

   

  (Sub)Module

   

  有兩個方式，取決於 code 大小，比如創一個 submodule foo

  - `./foo.rs`：所有該 foo module 的 code 都在這個 rs file 裡
  - `./foo/mod.rs`：foo 這個資料夾底下還可以有其他 rs file，他們合起來完整 foo 這個 module

- access 一個 (sub)module 與 file path 強相關，並且有三個關鍵字可作為起點

  - `crate` - the root module of your crate
  - `super` - the parent module of your current module
  - `self` - the current module

所以一個 crate 可能就長這樣

```bash
├── lib.rs
├── main.rs
├── submod1.rs
└── submod2
    ├── file1.rs
    ├── file2.rs
    ├── mod.rs
    └── submod3
        ├── file3.rs
        └── mod.rs
```

除了 file 層級的 module 劃分，單一 rs 裡面也可以用 `mod` 定義自己的 submodule

### share lib

```bash
$ rustc --crate-type=lib rary.rs
$ ls lib*
library.rlib
```

`rary` is actuaylly refer to the whole acssociated `crate`. It does not imply only build single `rary.rs` file.

To using a Library

```rust
// extern crate rary; // May be required for Rust 2015 edition or earlier
fn main() {
    rary::public_function();
}
```

------

## Error Handling

```
Option` 和 `Result` 都有 `unwrap()` 和 `?` 可以使用，基本上一個 function 的 return 值建議就是從這兩者選其一，並且不建議 caller 直接使用 `unwarp()` 處理，因為這會造成 `panic
```

### Option

`map()` 是 `Option` 提供的方法，參數是一個 `closure`，他其實就是在這種情境中 match 語法的簡化，如下範例

```rust
// Chopping food. If there isn't any, then return `None`.
// Otherwise, return the chopped food.
fn chop(peeled: Option<Peeled>) -> Option<Chopped> {
    match peeled {
        Some(Peeled(food)) => Some(Chopped(food)),
        None               => None,
    }
}

// Cooking food. Here, we showcase `map()` instead of `match` for case handling.
fn cook(chopped: Option<Chopped>) -> Option<Cooked> {
    chopped.map(|Chopped(food)| Cooked(food))
}
/* instead of
fn cook(chopped: Option<Chopped>) -> Option<Cooked> {
    match chopped {
        Some(Chopped(food)) => Some(Cooked(food)),
        None => None
    }
}
*/
```

在串兩的都是 return Option 的 function 的時候，如果兩個 function 的 return Option<Type> 相同，那可以直接使用 `?`；若不同，則要做轉換，但應換成使用 `Option` 的 `and_then()` 方法，因為若使用 `map()`，會多一層 Option，因為 `map()` 包含一個簡化是會幫你加上 `Some()` 裝起來

下面這個範例就是串 `have_recipe()` 和 `have_ingredients()` 兩個 function

```rust
#[derive(Debug, Clone)] enum Food { CordonBleu, Steak, Sushi }
#[derive(Debug)] enum Day { Monday, Tuesday, Wednesday }

fn have_ingredients(food: Food) -> Option<Food> {
    match food {
        Food::Sushi => None,
        _           => Some(food),
    }
}

fn have_recipe(food: Food) -> Option<Food> {
    match food {
        Food::CordonBleu => None,
        _                => Some(food),
    }
}

fn cookable_v2(food: Food) -> Option<Food> {
    have_recipe(food).and_then(have_ingredients)
    // instead of have_recipe(food).map(|f| have_ingredients(f))
    //   becauset his will return Option<Option<Food>>
}
```

#### as_ref(), as_mut()

```rust
pub const fn as_ref(&self) -> Option<&T>
```

Converts from `&Option<T>` to `Option<&T>`.

這東西的重要性在於可以產生一個被包在 Option 裡面的東西的 reference 而不用 take ownership

```rust
pub fn as_mut(&mut self) -> Option<&mut T>
```

Converts from `&mut Option<T>` to `Option<&mut T>`.

```rust
let mut x = Some(2);
match x.as_mut() {
    Some(v) => *v = 42,
    None => {},
}
assert_eq!(x, Some(42));
```

注意轉換過之後都還是包在 `Option` 裡面

> `Option`, `Box`, `Result` 三種類型才有支持預設，其他要實作 `AsRef` trait

```rust
fn main() {
    let mut a = Some(Box::new(5));
    let p1 = a.as_ref(); // p 沒有 take ownership 喔. 5 的 ownership 還是在 a

    println!("{:?}", a);
    println!("{:?}", p1);
    
    let p11 = p1.unwrap();
    println!("p11:{:?}", p11); // 可以透過 p11 拿到 5
    println!("a:{:?}", a);
    
    // 以下是犯一些如果不使用 as_ref()，會遇到的 ownership 問題
    
    let p2 = &mut a;
    //let p22 = p2.unwrap(); // cannot move out of `*p2` which is behind a shared reference

    /*let p22 = match *p2 { // cannot move out of `p2.0` which is behind a mutable reference
        Some(v) => *v, // v: data moved here
        None => 0
    };*/
    
    let p22 = match *p2 {
        Some(ref v) => **v, // 處理上面錯誤的方法就是用 ref 來接
        None => 0
    };
    println!("p22:{:?} {:p}", p22, &p22);
    //println!("a:{:?}", a); // cannot borrow `a` as immutable because it is also borrowed as mutable
    // 這個時候 5 的 ownership 都還是在 a，所以當這裡要用 a 就會有這個衝突

    let p23 = match p2.take() { // 或者要把原本 a 的 ownership take 過來到 p2，p2 才有權把裡面的東西移去 v
        Some(v) => *v,
        None => 0
    };
    println!("p23:{:?} {:p}", p23, &p23);
    println!("a:{:?}", a); // 因為原本 a 的 ownership 已經被轉移去 p2，所以 a 已經變 None 自然也不再有衝突
}
```

### Result

對於一個 module 而言，最完整的 erro propagation 做法為

1. 定義自己的 error 型別，比如 `enum MyError {}`，列舉各種可能產生的 error，同時也包含當使用到其他 module 時，各個其他 moduel 的 error 歸類到 MyError 中的其中一個可能值
2. `impl fmt::Display for MyError`
3. `impl error::Error for MyError` 實作 `source()` 方法，`source()` 方法使跨抽象層的狀況讓上層 module 也能取得更多其*下下層* module 的 error 細節的可能性。也就是說，這一步可以不做，但不做的結果就是，假設 某A 使用你的 module，當你的 module 發生了 call 另一個 moduleB 時產生的該 moduleB 的 error 因此導致你的 moduel 也 report error 給 某A，某A 所能得到的唯一資訊就是你翻譯過的 error，無法進一步透過 source() 進到 moduleB 裡去提取更多資訊
4. `impl From<OtherModuleErrorType> for MyError` 讓 `?` 可用。也可以不做，若不做就變成當要 call 其他 module 時，要用 `method_provided_by_another_module().ok_or(MyError::SomeTranslatedError)?` 來做轉換。相當於 `?` 其實就是會去找 `From` 方法存不存在，若存在就會依據 From 的內容做轉換

下面範例

```rust
fn double_first(vec: Vec<&str>) -> i32 {
    let first = vec.first().unwrap(); // Generate error 1
    2 * first.parse::<i32>().unwrap() // Generate error 2
}

fn main() {
    let numbers = vec!["42", "93", "18"];
    let empty = vec![];
    let strings = vec!["tofu", "93", "18"];

    println!("The first doubled is {}", double_first(numbers));

    println!("The first doubled is {}", double_first(empty));
    // Error 1: the input vector is empty

    println!("The first doubled is {}", double_first(strings));
    // Error 2: the element doesn't parse to a number
}
```

假設這就是我們的 module，裡面用了其他兩個 moduel 的方法 `first()` 和 `parse()`，他們都會產生各自定義的 error type。下面就是依據上述的步驟改寫的結果，我們定義了自己的 error type `DoubleError` 把他們包起來並個別翻譯

```rust
use std::error;
use std::error::Error as _;
use std::num::ParseIntError;
use std::fmt;

type Result<T> = std::result::Result<T, DoubleError>;

#[derive(Debug)]
enum DoubleError {
    EmptyVec,
    // We will defer to the parse error implementation for their error.
    // Supplying extra info requires adding more data to the type.
    Parse(ParseIntError),
}

impl fmt::Display for DoubleError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match *self {
            DoubleError::EmptyVec =>
                write!(f, "please use a vector with at least one element"),
            // The wrapped error contains additional information and is available
            // via the source() method.
            DoubleError::Parse(..) =>
                write!(f, "the provided string could not be parsed as int"),
        }
    }
}

impl error::Error for DoubleError {
    fn source(&self) -> Option<&(dyn error::Error + 'static)> {
        match *self {
            DoubleError::EmptyVec => None,
            // The cause is the underlying implementation error type. Is implicitly
            // cast to the trait object `&error::Error`. This works because the
            // underlying type already implements the `Error` trait.
            DoubleError::Parse(ref e) => Some(e),
        }
    }
}

// Implement the conversion from `ParseIntError` to `DoubleError`.
// This will be automatically called by `?` if a `ParseIntError`
// needs to be converted into a `DoubleError`.
impl From<ParseIntError> for DoubleError {
    fn from(err: ParseIntError) -> DoubleError {
        DoubleError::Parse(err)
    }
}

fn double_first(vec: Vec<&str>) -> Result<i32> {
    let first = vec.first().ok_or(DoubleError::EmptyVec)?;
    // Here we implicitly use the `ParseIntError` implementation of `From` (which
    // we defined above) in order to create a `DoubleError`.
    let parsed = first.parse::<i32>()?;

    Ok(2 * parsed)
}

fn print(result: Result<i32>) {
    match result {
        Ok(n)  => println!("The first doubled is {}", n),
        Err(e) => {
            println!("Error: {}", e);
            if let Some(source) = e.source() {
                println!("  Caused by: {}", source);
            }
        },
    }
}

fn main() {
    let numbers = vec!["42", "93", "18"];
    let empty = vec![];
    let strings = vec!["tofu", "93", "18"];

    print(double_first(numbers));
    print(double_first(empty));
    print(double_first(strings));
}
```

------

## Multithreading

```rust
use std::sync::mpsc::{Sender, Receiver};
use std::sync::mpsc;
use std::thread;

static NTHREADS: i32 = 3;

fn main() {
    // Channels have two endpoints: the `Sender<T>` and the `Receiver<T>`,
    // where `T` is the type of the message to be transferred
    // (type annotation is superfluous)
    let (tx, rx): (Sender<i32>, Receiver<i32>) = mpsc::channel();
    let mut children = Vec::new();

    for id in 0..NTHREADS {
        // The sender endpoint can be copied
        let thread_tx = tx.clone();

        // Each thread will send its id via the channel
        let child = thread::spawn(move || {
            // The thread takes ownership over `thread_tx`
            // Each thread queues a message in the channel
            thread_tx.send(id).unwrap();

            // Sending is a non-blocking operation, the thread will continue
            // immediately after sending its message
            println!("thread {} finished", id);
        });

        children.push(child);
    }

    // Here, all the messages are collected
    let mut ids = Vec::with_capacity(NTHREADS as usize);
    for _ in 0..NTHREADS {
        // The `recv` method picks a message from the channel
        // `recv` will block the current thread if there are no messages available
        ids.push(rx.recv());
    }
    
    // Wait for the threads to complete any remaining work
    for child in children {
        child.join().expect("oops! the child thread panicked");
    }

    // Show the order in which the messages were sent
    println!("{:?}", ids);
}
```

------

## exec

```rust
use std::io::prelude::*;
use std::process::{Command, Stdio};

static PANGRAM: &'static str =
"the quick brown fox jumped over the lazy dog\n";

fn main() {
    // Spawn the `wc` command
    let process = match Command::new("wc")
                                .stdin(Stdio::piped())
                                .stdout(Stdio::piped())
                                .spawn() {
        Err(why) => panic!("couldn't spawn wc: {}", why),
        Ok(process) => process,
    };

    // Write a string to the `stdin` of `wc`.
    //
    // `stdin` has type `Option<ChildStdin>`, but since we know this instance
    // must have one, we can directly `unwrap` it.
    match process.stdin.unwrap().write_all(PANGRAM.as_bytes()) {
        Err(why) => panic!("couldn't write to wc stdin: {}", why),
        Ok(_) => println!("sent pangram to wc"),
    }

    // Because `stdin` does not live after the above calls, it is `drop`ed,
    // and the pipe is closed.
    //
    // This is very important, otherwise `wc` wouldn't start processing the
    // input we just sent.

    // The `stdout` field also has type `Option<ChildStdout>` so must be unwrapped.
    let mut s = String::new();
    match process.stdout.unwrap().read_to_string(&mut s) {
        Err(why) => panic!("couldn't read wc stdout: {}", why),
        Ok(_) => print!("wc responded with:\n{}", s),
    }
}
```

If you’d like to wait for a process::Child to finish, you must call Child::wait, which will return a `process::ExitStatus`.

```rust
use std::process::Command;

fn main() {
    let mut child = Command::new("sleep").arg("5").spawn().unwrap();
    let _result = child.wait().unwrap();

    println!("reached end of main");
}
```

------

## Argument parsing

```rust
use std::env;

fn increase(number: i32) {
    println!("{}", number + 1);
}

fn decrease(number: i32) {
    println!("{}", number - 1);
}

fn help() {
    println!("usage:
match_args <string>
    Check whether given string is the answer.
match_args {{increase|decrease}} <integer>
    Increase or decrease given integer by one.");
}

fn main() {
    let args: Vec<String> = env::args().collect();

    match args.len() {
        // no arguments passed
        1 => {
            println!("My name is 'match_args'. Try passing some arguments!");
        },
        // one argument passed
        2 => {
            match args[1].parse() {
                Ok(42) => println!("This is the answer!"),
                _ => println!("This is not the answer."),
            }
        },
        // one command and one argument passed
        3 => {
            let cmd = &args[1];
            let num = &args[2];
            // parse the number
            let number: i32 = match num.parse() {
                Ok(n) => {
                    n
                },
                Err(_) => {
                    eprintln!("error: second argument not an integer");
                    help();
                    return;
                },
            };
            // parse the command
            match &cmd[..] {
                "increase" => increase(number),
                "decrease" => decrease(number),
                _ => {
                    eprintln!("error: invalid command");
                    help();
                },
            }
        },
        // all the other cases
        _ => {
            // show a help message
            help();
        }
    }
}
```

------

## References

- [Rust 語言之旅](https://tourofrust.com/TOC_zh-tw.html)
- [Rust book](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/stable/rust-by-example/index.html)
- [dyn , impl and Trait Objects — Rust](https://cotigao.medium.com/dyn-impl-and-trait-objects-rust-fd7280521bea)


From: A Po
Author: Chris Chung
Link: https://chungchris.github.io/2021/06/30/software/language/rust-note/
本文章成功權歸作者所有，形式的轉載都請註明出處。