thread & tls
============

這篇來談談執行緒 (thread) 與 thread local storage (TLS) ，雖說是這樣，但事實上主要是想來看看 TLS 是怎麼運作的，不過在那之前先來講一下執行緒是什麼吧

執行緒
------

執行緒是作業系統執行排程的最小單位，通常會包含在處理序中，並且會跟同一個處理序中的其它執行緒共用大多的系統資源，比如記憶體空間等等，但它會有自己的暫存器與堆疊，以上摘要自[維基百科][wiki-thread]

[wiki-thread]: https://zh.wikipedia.org/zh-tw/線程

不過如果只寫這樣那就太偷懶了，說來上一篇介紹到了系統呼叫， Linux 下是用什麼系統呼叫建立執行緒的呢？在解答之前先來介紹一個工具 - `strace` ，它的功能是讓你可以追蹤一個程式呼叫了哪些系統呼叫，用法像這樣：

```shell
$ strace -o <檔名> <執行檔>
$
```

這樣就會追蹤執行檔執行了哪些系統呼叫了，至於加上 `-o` 是為了讓它把紀錄輸出到檔案中，這樣比較方便等下來比對，只要準備個程式，並且記錄有呼叫 `std::thread::spawn` 與不呼叫的結果就能大概知道是呼叫了哪個系統呼叫了，在比較後多出來的呼叫是這樣的：

```plain
futex(0x7fc415a810c8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
mmap(NULL, 2101248, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_STACK, -1, 0) = 0x7fc414c4d000
mprotect(0x7fc414c4e000, 2097152, PROT_READ|PROT_WRITE) = 0
clone(child_stack=0x7fc414e4cf30, flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS|CLONE_PARENT_SETTID|CLONE_CHILD_CLEARTID, parent_tidptr=0x7fc414e4d9d0, tls=0x7fc414e4d700, child_tidptr=0x7fc414e4d9d0) = 17258
futex(0x7fc414e4d9d0, FUTEX_WAIT, 17258, NULL) = 0
```

從輸出中不只可以看到呼叫了哪個系統呼叫，連參數傳了什麼還有回傳值都知道，可以看出這個工具真的很方便，不過這邊也不只一個呼叫，但至少範圍小很多，實際只有 4 個而已而且 mprotect 與 mmap 其實在之前就用過了，剩下兩個稍微的看一下 man 的說明就知道是哪一個了，答案是 `clone`

如果說自己用 `clone` 來建立執行緒的話：

```rust
use nix::{
    sched::{clone, CloneFlags},
    sys::{
        signal::Signal,
        wait::{waitpid, WaitStatus},
    },
};
use std::{thread, time::Duration};

fn child() -> isize {
    println!("Hello from thread");
    thread::sleep(Duration::from_secs(1));
    println!("thread is going to exit");
    0
}

fn main() {
    let mut stack = Box::new([0; 1024 * 1024]);
    let tid = clone(
        Box::new(child),
        &mut *stack,
        CloneFlags::empty(),
        Some(Signal::SIGCHLD as i32),
    )
    .unwrap();
    thread::sleep(Duration::from_millis(500));
    println!("at main");
    match waitpid(tid, None).unwrap() {
        WaitStatus::Exited(..) => {
            println!("thread exit");
        }
        _ => unreachable!(),
    }
}
```

如果執行你應該可以看到子執行緒與主執行緒都是有執行的，不過這跟一般的執行緒概念實在是不太一樣就是了，因為這邊我沒有使用 `CLONE_VM` ，這個是讓兩個執行緒用同一個記憶體空間，至於不使用的原因是因為程式中間似乎存取到了什麼東西導致一直發生 segmentation fault ，然後似乎因為 `gdb` 與 `valgrind` 都對這種情況的支援不太好，我就沒去除錯了

另外這邊傳入了 `SIGCHLD` 讓執行緒結束時會產生 `SIGCHLD` 這個 signal 這樣才能用 `waitpid` 的方式去等待，一般的執行緒其實是不會產生 signal 的，而一般的 join 則是利用類似 mutex 的方式等待執行緒結束

> 具體而言是用了 `futex` 這個系統呼叫，這部份有興趣可以去看一下 `glibc` 的實作

TLS
---

TLS 是個讓每個執行緒都可以有一份自己的資料的機制，在 Rust 中是這樣使用的：

```rust
use std::{cell::Cell, thread};

thread_local! {
  static FOO: Cell<i32> = Cell::new(42);
}

fn main() {
  FOO.with(|n| {
    println!("{:p}", n as *const _);
  });
  thread::spawn(|| {
    FOO.with(|n| {
      println!("{:p}", n as *const _);
    });
  })
  .join()
  .unwrap();
}
```

這邊用 Rust 提供的 `thread_local!` 這個 macro 來宣告一個 thread local 的變數，如果執行這個程式就可以看到在不同的執行緒中實際存的位置是不同的，如果修改的話也不會影響到另一個執行緒中的值

```plain
$ ./demo
0x7efdf54db764
0x7efdf44b7664
```

而對有使用到 TLS 的程式使用 `readelf` 讀取 section 的表的話可以看到像這樣的資料段：

```plain
  [21] .tdata            PROGBITS         000000000023ca60  0003ca60
       0000000000000030  0000000000000000 WAT       0     0     32
  [22] .tbss             NOBITS           000000000023caa0  0003ca90
       00000000000000a0  0000000000000000 WAT       0     0     32
...
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
```

再搭配底下的說明可以看到這兩個段有著 `TLS` 這個屬性， Linux 系統就是在建立執行緒時也把這兩個段的內容複製一份來實現 TLS 的功能的，不過在程式裡面又是怎麼存取的呢？我們來看反組譯過的程式碼：

```plain
0000000000006380 <tls::FOO::__getit>:
    6380:	50                   	push   rax
    6381:	64 48 8b 04 25 00 00 	mov    rax,QWORD PTR fs:0x0
    6388:	00 00
    638a:	48 8d b8 60 ff ff ff 	lea    rdi,[rax-0xa0]
    6391:	e8 ea f9 ff ff       	call   5d80 <std::thread::local::fast::Key<T>::get>
    6396:	48 89 04 24          	mov    QWORD PTR [rsp],rax
    639a:	48 8b 04 24          	mov    rax,QWORD PTR [rsp]
    639e:	59                   	pop    rcx
    639f:	c3                   	ret
```

> 這段程式碼是由 [`libstd/thread/local.rs`][std-thread-local] 這邊編譯出來的，用途是設定變數的初始值，有興趣可以去看看，這邊會根據作業系統的類型去選擇一個比較快的實作

[std-thread-local]: https://github.com/rust-lang/rust/blob/master/src/libstd/thread/local.rs#L151-L189

這邊的第二行組語，後面有個比較特別的位置，在 `0x0` 的前面還多了個 `fs` ，這個是段選擇器，這在以前 16 位元的時代是個很重要的東西，以前 16 位元時電腦能存取的記憶體大小是 1 MB ，不過如果你的指標只有 16 位元，那實際上能表達的範圍最大隻有到 64 KB ( 2 的 16 次方 ) 而已，如果要完整的表達 1 MB 空間的任何一個位置你至少需要 20 位元才夠，而那時的解決方法就是用段選擇器，在 16 位元的系統下段選擇器也是 16 位元的，它會被左移 4 個位元再加上後面的偏移位置來表達完整的記憶體位置，不過現在的暫存器本身就有 64 位元的大小，能表達的範圍早就超過了 1 MB 了，所以段選擇器其實已經沒什麼用了，但這邊作業系統就拿了 `fs` 來代表 TLS 的起始位置，讓執行緒知道自己該使用的空間在哪

> 段選擇器有 cs, ds, ss 這些在以前分別代表程式碼段，資料段與堆疊段，另外還有一個 es 也是資料段，不過是用來代表要大量搬移資料時的資料來源，不過這些現在因為只需要暫存器就能完整的表達記憶體位置了，所以一般都被作業系統設定為 0 ，讓暫存器的值被作為指標來使用時，直接對應到虛擬記憶體的位置，而上面出現的 fs 另外還有個 gs 是在 64 位元後才加入的通用的段選擇器，另外在現在的作業系統所運作的保護模式下其實你沒辦法直接設定段選擇器的值，所以使用者其實並不需要關心它的值到底是什麼，至於保護模式是什麼東西，因為本系列應該是不會講到作業系統的運作，所以有興趣自己找一下資料吧

不過這邊有點可惜的是，你沒辦法用 gdb 去取得加上段選擇器的位置，如果你去查上面那個 `mov` 指令的機器碼的話，其實你會發現有使用段選擇器與沒有使用的根本是不同的指令，所以可惜沒辦法直接在 `gdb` 中透過 `fs` 來看看 TLS 中存了什麼，雖說這邊也有個很簡單的方法就是在程式中把變數的位置印出來你就知道實際的位置放在哪邊了

`fork` 也能造成死結
-------------------

不知道你相不相信， `fork` 這個系統呼叫也能造成死結：

```rust
use std::{
  os::unix::process::CommandExt,
  process::Command,
  sync::{Arc, Mutex},
  thread,
  time::Duration,
};

fn main() {
  let mutex = Arc::new(Mutex::new(()));
  let handle = {
    let mutex = mutex.clone();
    thread::spawn(move || {
      let _guard = mutex.lock();
      thread::sleep(Duration::from_secs(1));
      println!("thread end");
    })
  };
  thread::sleep(Duration::from_millis(300));
  let mut child = unsafe {
    let mutex = mutex.clone();
    Command::new("true")
      .pre_exec(move || {
        let _guard = mutex.lock();
        Ok(())
      })
      .spawn()
      .unwrap()
  };
  handle.join().unwrap();
  println!("mutex unlock");
  child.wait().unwrap();
  println!("child stop");
}
```

這邊用 `pre_exec` 來在 `fork` 之後，但是在執行其它程式之前執行一些程式碼，程式乍看之下挺合理的，只要過 1 秒鐘，執行緒就會把鎖釋放掉，然後 `pre_exec` 中的程式就可以拿到鎖了對吧，**假如**執行緒還在執行的話啦，事實上這個程式不只那個 `child stop` 不會印出來，就連 `mutex unlock` 也不會出現，不過那個 `mutex unlock` 是 Rust 的 `Command` 內部的機製造成的結果就是了

雖然準確來說並不是 `fork` 這個系統呼叫本身的問題，而是在呼叫 `fork` 之後，程式的執行緒只會剩下呼叫了 `fork` 的那一個，其它都會直接被結束掉，所以如果你在呼叫了 `fork` 之後要去存取比如像互斥鎖之類的資源，你就麻煩大了，因為能夠釋放掉鎖的執行緒早就不存在了，至於那個 `mutex unlock` 印不出來是因為 Rust 的 `Command` 在 `spawn` 中如果到 `exec` 前，或是 `exec` 本身發生了什麼錯誤它會用 pipe 通知父處理序，讓 `spawn` 可以回傳錯誤，只是因為 `pre_exec` 中的程式已經 deadlock 了，所以就連成功執行的通知也不會送到了

另外一個有趣的事實： 如果你有注意過 chromimn 延伸出來的瀏覽器所打開的處理序的參數，應該會有一個處理序的參數是 `--type=zygote` ，這個處理序可是寫 chromimn 的工程師們為瞭解決上面提到的這個問題的法寶，如果你注意看應該會發現大部份的 chromimn 的處理序都會開好幾個執行緒，但偏偏就是有一個參數是 `--type=zygote` 沒有任何執行緒，這個處理序把必須要的資源事先開好，並且刻意的維持在除了主執行緒外沒有其它執行緒的狀態，如果 chromimn 需要一個新的處理序就會從這個處理序 `fork` 出來，在沒有其它執行緒的情況下就不用擔心上面提到的因為 `fork` 與執行緒所造成的問題了，至於官方對於這個方法的介紹可以看[這邊][zygote]

[zygote]: https://chromium.googlesource.com/chromium/src.git/+/master/docs/linux_zygote.md

這次距離上次更新比較久，原本想說就算中斷了還是盡量一天一篇的把它更新完的，不過最近偷懶了一下，但我可以保證我會把它給更新完的
