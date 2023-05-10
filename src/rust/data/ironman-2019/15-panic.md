panic
=====

Rust 的 `panic` 其實是個有趣的機制，怎麼說呢，我們來看個範例程式，請試著自己先在腦中模擬一下這段程式會印出什麼：

```rust
use std::panic;

struct NeedDrop(&'static str);

impl Drop for NeedDrop {
  fn drop(&mut self) {
    println!("drop by {}", self.0)
  }
}

fn foo() {
  let need_drop = NeedDrop("foo");
  println!("before foo");
  panic!("in foo");
  println!("after foo");
}

fn bar() {
  println!("before bar");
  foo();
  let need_drop = NeedDrop("bar");
  println!("after bar");
}

fn baz() {
  let need_drop = NeedDrop("baz");
  println!("before baz");
  bar();
  println!("after baz");
}

fn main() {
  // 讓 panic 的訊息不會印出來
  panic::set_hook(Box::new(|_| ()));
  println!("before main");
  let _ = panic::catch_unwind(baz);
  println!("after main");
}
```

來公佈答案：

```shell
$ ./demo
before main
before baz
before bar
before foo
drop by foo
drop by baz
after main
```

不知道你有沒有看懂這段範例程式想要表達什麼呢？

1. 首先， `panic` 之後的 `after ...` 的訊息並沒有印出來，除了 `main` 的以外
2. 當宣告的變數有需要 drop 的 struct 時都有好好的被 drop

程式居然可以這樣子直接跳去處理清理資源的部份，不覺得很神奇嗎？另外還有那個 `catch_unwind` ，看名字大概可以猜到它是幹麻的，它是用來接住 `panic` 用的，如果看它的文件的話可以看到它會回傳一個 `Result`，假如傳進去的函式並沒有 `panic` 而正常結束的話就會回傳 `Ok` ，但如果有 `panic` 的話就會回傳 `Err` 並帶有傳給 `panic` 的資訊，所以那個 `after main` 才能被印出來

說到這邊不覺得這個機制很像什麼嗎？應該有不少程式語言都有這種機制才對，就是「例外處理」，底下用 C++ 來舉例：

```cpp
#include <iostream>

using namespace std;

struct NeedDrop {
  ~NeedDrop() { cout << "drop by " << name << endl; }

  const char *name;
};

int main() {
  try {
    NeedDrop need_drop{"main"};
    throw 42;
  } catch (int n) {
  }
  cout << "after main" << endl;
  return 0;
}
```

執行看看應該會發現它們的行為挺類似的，不過跟 C++ 的例外處理相比， Rust 的比較像是個簡化版的例外處理：

- Rust 的 `panic!` -> C++ 的 `throw`
- Rust 的 `std::panic::catch_unwind` -> C++ 的 `catch`

所以它到底是怎麼做到的呢？這篇就會講個概念瞭解一下，下一篇我們再來讀程式碼，這個機制有兩種實作， SjLj 與目前使用的 Dwarf ， SjLj 是之前實作的機制，它必須要由編譯器插入紀錄必要資訊的結構與利用 `setjmp` 與 `longjmp` 來達成例外發生時的處理，於是相對的它在執行時的成本較高

至於現在使用的 Dwarf 則是使用了除錯資訊用的 `frame` 資料來紀錄每個函式會發生例外的範圍在哪，堆疊的狀態又該是如何，清理資源或是處理程式又在哪邊，並在例外發生時透過這些資訊跳到處理程式的位置讓這段程式來處理，好處是如果例外沒發生則在執行時幾乎沒成本，但缺點是在發生例外時就必須讀取 `frame`的資訊來進行回復，相較已經把資訊準備好的 SjLj 要來的麻煩點，另外 Dwarf 的實作內還有個看網路上說是圖靈完備的 bytecode ，這必須在例外發生時執行 (說不定之後可以試著用這個 bytecode 來寫個什麼東西看看)

這邊可以用 `readelf -Wwf` 來印出 `.eh_frame` ，也就是 `frame` 資訊的內容：

```shell
❯ readelf -Wwf demo.o
Contents of the .eh_frame section:


00000000 0000000000000014 00000000 CIE
  Version:               1
  Augmentation:          "zR"
  Code alignment factor: 1
  Data alignment factor: -8
  Return address column: 16
  Augmentation data:     1b
  DW_CFA_def_cfa: r7 (rsp) ofs 8
  DW_CFA_offset: r16 (rip) at cfa-8
  DW_CFA_nop
  DW_CFA_nop

00000018 0000000000000014 0000001c FDE cie=00000000 pc=0000000000000000..000000000000003b
  DW_CFA_advance_loc: 4 to 0000000000000004
  DW_CFA_def_cfa_offset: 48
  DW_CFA_advance_loc: 54 to 000000000000003a
  DW_CFA_def_cfa_offset: 8
  DW_CFA_nop
...
```

因為內容很長，我只有節錄一些，上面的資訊其實看不懂沒關係，因為還有其它的資訊我們在下一篇看到程式碼時才會一起提到，如果對上面的內容有興趣的話可以看一下參考資料的第一篇

參考資料
--------

- https://refspecs.linuxfoundation.org/LSB_3.0.0/LSB-PDA/LSB-PDA/ehframechpt.html
- https://docs.microsoft.com/zh-tw/cpp/cpp/exceptions-and-stack-unwinding-in-cpp?view=vs-2019
