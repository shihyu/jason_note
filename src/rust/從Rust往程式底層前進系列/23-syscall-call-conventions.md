syscall & call conventions
==========================

這篇要來聊系統呼叫 syscall ，實際上程式執行的環境是處處受到限制的，很多東西需要由作業系統幫忙完成，比如寫檔案，寫檔案這個動作牽涉到了讀寫檔案系統中的資訊，檔案應該寫在硬碟的哪個位置上等等，這些看似簡單的操作，作業系統在背後都不知道做了多少處理， Linux 系統下提供了很多的系統呼叫，在 Ubuntu 系統下的 `/usr/include/x86_64-linux-gnu/asm/unistd_64.h` 你可以看到很長的一串列表在定義系統呼叫的代號，另外這邊也有個可以搜尋的[網頁列表][syscall-table]

[syscall-table]: https://filippo.io/linux-syscall-table/

大部份的系統呼叫都有提供一個 C 的包裝，不過也有一小部份沒有，比如 `gettid` 這個是用來取得執行緒的識別碼用的系統呼叫，因為沒有包裝的函式，如果要呼叫就只能直接用 `syscall` 這個函式來呼叫了：

```rust
libc::syscall(libc::SYS_gettid)
```

而在組言中 syscall 就是一個叫 `syscall` 的指令，雖說在以前並不是這樣一個指令就可以解決的，在 32 位元的時候還有一些其它的方式，但因為一些歷史的因素，到了 64 位元系統基本上就剩下一種了

> 32 位元的時候原先使用的是軟體中斷 `int 0x80` ，不過因為它處理的東西比較多導致它的速度較慢，後來 Intel 與 AMD 各自推出了能快速的呼叫系統呼叫的指令 `sysenter` 與 `syscall` ，到了 64 位元的時代時， Intel 推出了新的 CPU 指令集，但…它不相容 32 位元時的 x86 指令集，於是它沒能活下來，使得 `sysenter` 指令跟著消失了

> 中斷是比如像按下鍵盤的動作，硬體會產生一個中斷來通知 CPU 發生了按下鍵盤的事件，作業系統會預先註冊中斷該如何處理，於是 CPU 就會中斷目前執行的東西跳去處理中斷的程式，這也是為什麼這個東西會叫中斷，另外也能用 `int` 這個指令來產生中斷，當然它跟硬體產生的中斷不太一樣就是了

如果用組語印出 `Hello world` 的話：

```asm
bits 64
section .rodata
  msg db "Hello world", 10
section .text
  mov rdx, 12
  lea rsi, [rel msg]
  mov rdi, 1
  mov rax, 1
  syscall
```

呼叫了 `syscall` 就會進到作業系統的程式碼中，這邊並不像一般呼叫函式一樣可以用 `call` 或 `jmp` 之類的單純跳轉過去就行了，因為作業系統跟一般使用者的程式碼實際上是執行在不同的 protection ring 之下，簡單來說它們所擁有的權限是不一樣的，而 x86 與現在的 x64 的 CPU 將這個等級分為 4 等，從 ring0 到 ring3 ，但事實上用到的只有 ring0 與 ring3 而已，作業系統執行在 ring0 之下，而使用者的程式則是在 ring3 下，在 ring3 下的程式受到了限制，比如不能直接存取硬體，不能直接改變自己的等級

但在呼叫 `syscall` 時 CPU 會保存幾個值來確保能回復程式的狀態，之後切換到 ring0 並跳到預先註冊好的處理程式的位置，接下來就是由作業系統根據暫存器的值來決定要怎麼處理這次的系統呼叫了

在上面的程式碼中可以看到我們把幾個值填到暫存器中，為什麼是這幾個暫存器其實有個重要的東西叫呼叫慣例 (call conventions)，簡單來說就是參數應該要怎麼傳，平常呼叫函式時可能就只是在括號中將參數填入而已，但在底層，這些參數總是要放在某個位置，

在現在類 Unix 系統下 64 位元的程式中用的基本上都是同一套叫 `System V AMD64 ABI` 這個其實可以在維基上找到，如果是一般函式呼叫的話參數是依序放在 `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9`，另外 `rax` 被用來放回傳值，在系統呼叫時則是把 `rcx` 換成 `r10` ，順帶一提，系統呼叫時 `rcx` 被拿去存返回位置了，呼叫慣例中還約定了如果使用到了哪些暫存器必須把它的值回復，哪些則不用

參考資料
--------

- https://en.wikipedia.org/wiki/X86_calling_conventions
- https://stackoverflow.com/questions/15168822/intel-x86-vs-x64-system-call
- https://en.wikipedia.org/wiki/Protection_ring
- https://stackoverflow.com/questions/18717016/what-are-ring-0-and-ring-3-in-the-context-of-operating-systems
