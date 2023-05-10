閉包 (closure)
==============

Rust 中有閉包這種東西

```rust
let x = 42;
let f = || println!("x: {}", x);

f(); // 會印出 `x: 42`
```

它似乎是個函式，卻又跟一般的函式不太一樣，是的，它還包含了建立它的環境，如同將環境也一起包含進來了，在 Rust 中閉包還又細分成三種 `Fn`, `FnMut`, `FnOnce`，它們又有什麼不同呢

在 C 中並沒有 closure 這種東西，我們稍為再往比較複雜一點的語言， C++ 去找，事實上 C++11 中就有了 lambda ，不過我想提的是另一個東西，在 C++ 中的物件都會有個叫 `this` 的指向自己的指標，而物件中的方法可以透過這個指標存取存在物件上的屬性與方法等等，另外在 Rust 中 struct 的 method 也有 self 這個參數，當你用 `.` 呼叫方法時，你的 struct 實際上就是被當成第一個參數傳進來，這也在之前的系列有提過，所以在 Rust 中 method 可以有兩種方式呼叫：

```rust
struct Person {
  name: &'static str,
}

impl Person {
  fn greet(&self) {
    println!("Hello {}", self.name);
  }
}

let john = Person { name: "John" };
// 用 `.` 呼叫方法
john.greet();

// 自己把 reference 傳進去呼叫
Person::greet(&john);
```

於是這跟 closure 有什麼關係呢？如果像這樣：

```rust
struct Closure {
  x: i32
}

impl Closure {
  fn call(&self) {
    println!("x: {}", self.x)
  }
}
```

然後這個 struct 與 `call` 的實作都由編譯器幫你產生，也讓你在直接呼叫時自動轉成對 `call` 的呼叫，咦， closure 不就完成了嗎

```rust
let x = 42;
// 如果這邊自動產生上面的 struct 並轉換成 let f = Closure { x: 42 };
let f = || println!("x: {}", x);

// 如果這邊自動轉換成 f.call()
f();
```

我們來驗證一下是不是真的是這樣，同樣的編譯成組語來看看吧：

```asm
movl  $42, 4(%rsp)
leaq  4(%rsp), %rax
movq  %rax, 8(%rsp)
leaq  8(%rsp), %rdi
callq _ZN4demo4main28_$u7b$$u7b$closure$u7d$$u7d$17hc91dcf7758881cc0E
```

其實還是有點不一樣，上面的組語先把 `42` 存到堆疊裡後再把那個記憶體位置再存到記憶體裡，然後才又把那個記憶體位置傳給底下的函式當第一個參數，簡單來說底下那個函式拿到的是 `&&i32` ，對照一下上面我們想像的實作，差別在 `x` 實際上是存了 reference ，所以經過修正後應該是：

```rust
struct Closure<'a> {
  x: &'a i32,
}
```

事實上也有個很簡單的方法可以確定 closure 裡的 `x` 使用的是 reference：

```rust
fn check_is_reference() -> impl Fn() {
  let x = 42;
  || println!("x: {}", x)
}

fn main() {
  check_is_reference()();
}
```

上面這段程式碼拿去編譯，如預期的跳出了 `not live long enough` 的訊息了

Fn, FnMut, FnOnce
-----------------

在之前的系列有講過，不過這邊還是提一下這三個 trait 的用途

- `FnOnce`: 這個代表它可能會消耗掉它取得的區域變數，所以它可能只能呼叫一次
- `FnMut`： 這代表它會修改到它的環境
- `Fn`： 這是不會動到環境的閉包

另外因為 trait 之間的繼承關係， `Fn` 可以當作 `FnMut` 與 `FnOnce` ，而 `FnMut` 也能當作 `FnOnce`

所以這三個的差別在哪，不過除了這三個 trait ，事實上還有另一個也能直接呼叫的東西叫 `fn`，對，就是平常用的函式，它也能當指標傳給其它函式來用，比如像在用 `Option` 的 `unwrap_or_else` 時：

```rust
let x = None::<String>;
let x = x.unwrap_or_else(String::new);
```

這邊就把 `String::new` 傳給了 `unwrap_or_else` 來建立預設值了，總之我們先來想個方法來分辦這些函式到底是實作了哪個 trait 吧：

```rust
fn is_fn(_f: fn()) {}
fn is_Fn(_f: impl Fn()) {}
fn is_FnMut(_f: impl FnMut()) {}
fn is_FnOnce(_f: impl FnOnce()) {}
```

像這樣定義幾個函式，分別接收不同類型的參數，我們就可以用這些函式來幫助我們判斷我們的 closure 實際上是實作了哪個 trait 了

```rust
fn main() {
  let x = 42;
  let mut y = 123;
  let s = "foo".to_owned();

  let f = || println!("no capture");
  let g = || println!("capture x: {}", x);
  let mut h = || {
    y += 1;
    println!("mutate y: {}", y);
  };
  let i = move || {
    println!("move s: {}", s);
    // 如果沒有這個 drop 結果又會有所不同喔
    drop(s);
  };

  // f 是 fn
  is_fn(f);
  is_Fn(f);
  is_FnMut(f);
  is_FnOnce(&f);

  // g 是 Fn
  // is_fn(g);
  is_Fn(g);
  is_FnMut(g);
  is_FnOnce(&g);

  // h 是 FnMut
  // is_fn(h);
  // is_Fn(h);
  is_FnMut(&mut h);
  is_FnOnce(&mut h);

  // i 是 FnOnce
  // is_fn(i);
  // is_Fn(i);
  // is_FnMut(i);
  is_FnOnce(i);
}
```

上面任何一個註解的程式碼取消註解都會造成編譯錯誤，不過像上面的 `drop` 拿掉又會造成不同的結果，讓 `i` 可以用 reference 的形式傳給 `is_Fn` ，事實上 closure 實際由編譯器實作了哪個 trait 是根據 closure 內對 capture 的值做了什麼而決定的，而不是由定義 closure 時的寫法決定的

另外有個 [RFC 2132][rfc_2132]，在 1.26 後讓 closure 在 capture 的值能被 Copy 或 Clone 時也實作 Copy 或 Clone ，於是再考慮到可複製，實際的情況又變的更複雜了呢，不過實際上平常不會特別注意自己的 closure 到底被實作成了什麼形態

[rfc_2132]: https://github.com/frol/rust-rfcs/blob/master/text/2132-copy-closures.md

參考資料
--------

- [rust reference - closure](https://doc.rust-lang.org/reference/types/closure.html)
