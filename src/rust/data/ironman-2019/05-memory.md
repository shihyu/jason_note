Memory
======

資料在記憶體中長什麼樣呢？我們宣告的變數，不管是區域變數或是全域變數都存在記憶體中，甚至是程式碼也是，不過我們先把程式碼的部份留著，先來試著看看變數在記憶體中是怎麼回事吧

```rust
static N: i32 = 42;

fn main() {
    let num = 1;
    let boxed_num = Box::new(2);
    dbg!(&N as *const _);
    dbg!(&num as *const _);
    dbg!(&*boxed_num as *const _);
}
```

這邊宣告了三種不同的變數，並把它們轉換成指標，並印出它的位置看看，比較特別的是 `Box` 的部份，因為如果直接取它的位置的話會是它本身的位置，而不是它內部分配的空間的位置

```plain
[demo.rs:6] &N as *const _ = 0x000055ea7c3dd7e0
[demo.rs:7] &num as *const _ = 0x00007fff7e05ad7c
[demo.rs:8] &*boxed_num as *const _ = 0x000055ea7d2cfa40
```

首先，我們可以觀察到，區域變數很顯然被分配到了距離另外兩個很遠的空間去，是說剛剛提到了 `Box` 內部分配的空間，如果你去看 [`Box` 的文件][box-doc]，你會發現上面寫了句 `A pointer type for heap allocation`「給從 heap 分配的空間的指標」，底下也有提到 `Move a value from the stack to the heap` 「把一個指從 stack 移到 heap」上，這就是今天最主要要講的兩個東西了 stack 與 heap

[box-doc]: https://doc.rust-lang.org/stable/std/boxed/index.html

stack
-----

所以 stack 是什麼，並不是資料結構的那個 stack 喔，不知道你有沒有想過，我們平常宣告區域變數，這些變數總是要佔空間的吧，憑什麼這些空間都自動的在函式結束時還給系統了呢，說自動還回去好像也不太對，因為對於 C 與 Rust 來說確實像是自動還回去的，如果往更底層去看的話實際上還是要自己來處理就是了

stack 的中文叫堆疊，一般是指先進先出的資料結構，不過程式中也有個 stack ，是由系統提供給程式暫存區域變數等等用的，至於為什麼這個東西也叫 stack 呢，我們實際來看看：

```rust
fn foo() {
    let x = 2;
    dbg!(&x as *const _);
}

fn main() {
    let x = 1;
    dbg!(&x as *const _);
    foo();
}
```

```plain
[demo.rs:8] &x as *const _ = 0x00007ffe795a6f44
[demo.rs:3] &x as *const _ = 0x00007ffe795a6e14
```

因為它的空間會隨著函式的呼叫不斷的由高位置往低位置儲存資料，也同樣的是 FIFO 的結構，在 CPU 中有個負責儲存堆疊頂端位置的堆疊指標的暫存器，編譯完後的程式會透過減少堆疊指標的值在上面分配需要的空間來暫存區域變數，並在函式結束時將指標回復原狀

heap
----

heap 則是又是另一種資料結構的名字，不過同樣的在這邊並不是指資料結構，而是一塊記憶體的空間，在 Rust 中則是由像 `Box` 這樣的 API 來分配與管理的，因為不像 stack 一樣，在函式結束後必須把空間還回去，而可以傳遞在不同函式間，由使用者決定何時要還回去，但 Rust 實際上會由編譯器自動在 `Box` 離開作用域時將空間還回去就是了

Rust 中大多的 API 如果有分配資源 (記憶體、檔案等等)，都會在物件離開作用域時自動把資源還回去，這叫 [RAII][RAII] ，也就是資源的取得與初始化在你拿到物件時就完成了，而資源的釋放則由解構子處理，在 Rust 中也就是 `Drop` ，我們只好用 C 來體驗一下自己分配與釋放記憶體了：

[RAII]: https://zh.wikipedia.org/zh-tw/RAII

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
  // 分配一個 int 大小的記憶體
  int *n = malloc(sizeof(int));
  // 寫入值 42
  *n = 42;
  // 印出 n 指向的位置
  printf("%p\n", n);
  // 釋放記憶體
  free(n);
}
```

全域變數
--------

雖說叫全域變數，不過因為 Rust 有模組機制的關係，實際上可以決定要不要給外部使用，相較之下比較不會造成像 C 一樣因為未預期的修改而造成問題，上面提到了全域變數儲存的位置跟 heap 的變數很接近，這個原因之後會再詳細說明，這邊就先帶過吧
