Trait Object
============

這功能或許平常比較不常用一點，它長這樣子

```rust
trait Name {
  fn name(&self);
}

struct Foo;

impl Name for Foo {
  fn name(&self) {
    println!("This is Foo")
  }
}

fn print_name(x: &dyn Name) {
  x.name();
}

fn main() {
  let foo = Foo;
  print_name(&foo);
}
```

像這樣把傳入實作了某個 trait 的參考，就能使用該 trait 的方法，這跟範型有什麼不同，有什麼好處，又有什麼缺點呢？

這次我們改來看 llvm ir 吧，因為在 ir 裡還會留著型態的資訊，編譯成 asm 就沒那麼方便了，編譯成 ir 後找到這兩行：

```llvm-ir
@vtable.1 = private unnamed_addr constant { void (%Foo*)*, i64, i64, void (%Foo*)* } { void (%Foo*)* @_ZN4core3ptr18real_drop_in_place17h953817d878c40c2bE, i64 0, i64 1, void (%Foo*)* @"_ZN40_$LT$demo..Foo$u20$as$u20$demo..Name$GT$4name17hcb2e78ca8ebcdfdcE" }, align 8

; call demo::print_name
  call void @_ZN4demo10print_name17he7efac073c093a6aE({}* nonnull align 1 %0, [3 x i64]* noalias readonly align 8 dereferenceable(24) bitcast ({ void (%Foo*)*, i64, i64, void (%Foo*)* }* @vtable.1 to [3 x i64]*))
```

第一行是個叫 `vtable.1` 的常數，它就是一般說的 [Virtual method table](https://en.wikipedia.org/wiki/Virtual_method_table) ，裡面存的是一個函式，再來兩個數字，最後再一個函式，最重要的是最後的那個函式，那個函式就是我們幫 `Foo` 實作的 `Name::name` 方法

而在呼叫時，Rust 就把我們的資料與這個 `vtable.1` 一起傳給了 `print_name` 這個函式，事實上這邊我有點訝異，這邊的 `print_name` 實際上被改成了有兩個參數的函式，第一個用來接收資料，第二個則是 vtable ，而在 `print_name` 的函式裡則是從第二個參數找出了 `name` 的函式並且呼叫了

像這樣子把資料的 pointer 與它的 vtable 一起傳遞的作法有個稱呼叫 fat pointer ，如果看到它怎麼傳的應該會覺得這稱呼挺適合的，畢竟實際上它是傳了兩個 pointer ，使得它的大小有一般 pointer 的兩倍

那這樣子的做法跟範型又有什麼差別，如果我們同時準備範型與 trait object 的版本，再用兩個實作了 `Name` 的型態去呼叫它的話：

```rust
fn print_name_dyn(x: &dyn Name) {
  x.name();
}

fn print_name_generic(x: &impl Name) {
  x.name();
}
```

接著我們用 Linux 下的 `nm -C <exe file>` 去觀察輸出的執行檔，應該會發現 `print_name_generic` 出現了兩次，但 `print_name_dyn` 只有一次而已

```plain
00000000000041e0 t demo::print_name_dyn
00000000000041f0 t demo::print_name_generic
0000000000004200 t demo::print_name_generic
```

因為 generic 的版本幫每個實作產生了一份程式碼，而用 trait object 的都是用同一份，但透過產生個別的 vtable 使得程式可以在執行時找到正確的實作，這功能雖然會影響到一點執行時的速度，但在某些情況下卻比範型要來的好用，比如需要將實作了同樣 trait 的物件保存在同一個 vec 中，或是需要遞迴呼叫 trait 的方法時，例如 `Debug` 的實作

另外也因為範型需要複製程式碼，在使用範型的情況下也容易發生產生的執行檔較大的問題，視情況可以選用 dyn 來解決，另外這也有個小技巧可以用

```rust
fn print_str<S: AsRef<str>>(s: S) {
  let s = s.as_ref();
  inner(s);

  fn inner(s: &str) {
    println!("{}", s);
  }
}
```

像這樣子減少範型所要複製的程式碼的量，可以減少產生的執行檔的大小

參考資料
--------

- [Peeking inside trait object](https://huonw.github.io/blog/2015/01/peeking-inside-trait-objects/)
- [The book first edition - trait object](https://doc.rust-lang.org/1.30.0/book/first-edition/trait-objects.html)
