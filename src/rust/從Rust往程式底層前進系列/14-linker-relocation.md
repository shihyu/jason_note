linker - relocation
===================

在上一篇中有提到 section header 是給連結器看的資訊，那連結器又是什麼呢？連結器主要有兩個功能：

1. 合併靜態函式庫與目的檔 (object file) 成一個執行檔
2. 讀取重定址的資訊對檔案進行重定址

這篇要來講的就是重定址這回事，我們先來看個簡單的程式吧：

```c
#include <stdio.h>

int main() {
  const char *s = "Hello world";
  puts(s);
  return 0;
}
```

原本我是想用 Rust 的程式的，不過我試著讓 Rust 的編譯器輸出目的檔後發現，似乎已經完成重定址了，所以我就用 C 的程式了，這次要編譯成目的檔，也就是隻要再經過連結的步驟就能變成執行檔的檔案：

```shell
$ gcc -fno-pie -c -g demo.c
$
```

> 為了接下來解說的方便，這邊用 `-fno-pie` 強制關掉預設開啟的編譯成 PIE 程式的功能，但這樣在預設有開啟這個功能的系統上就無法連結成執行檔了

於是同一個目錄下應該會出現同名但副檔名為 `.o` 的目的檔，實際上它的格式跟執行檔一樣都是 ELF ，不過它還沒有經過連結的步驟，所以在那之前的檔案是什麼情況呢，我們用 `objdump` 來看看：

```shell
$ objdump -M intel -S demo.o
demo.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <main>:
#include <stdio.h>

int main() {
   0:   55                      push   rbp
   1:   48 89 e5                mov    rbp,rsp
   4:   48 83 ec 10             sub    rsp,0x10
  const char *s = "Hello world";
   8:   48 c7 45 f8 00 00 00    mov    QWORD PTR [rbp-0x8],0x0
   f:   00
  puts(s);
  10:   48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
  14:   48 89 c7                mov    rdi,rax
  17:   e8 00 00 00 00          call   1c <main+0x1c>
  return 0;
  1c:   b8 00 00 00 00          mov    eax,0x0
}
  21:   c9                      leave
  22:   c3                      ret
```

這邊改用 `-S` 讓它把原始碼也印出來對照，如果你把這邊的輸出與完整的執行檔比較，你會發現目的檔中的東西真的少了很多，只有我們寫好的 `main` 而已，不過最主要的是我們看到指定字串的那行的組語 `mov    QWORD PTR [rbp-0x8],0x0` ，這邊是把字串的位置存進堆疊裡，但好像哪邊不太對，字串的位置居然是 `0x0` ，這位置就是 `NULL` ，這當然不可能，我們先再來看另一個東西，重定址表：

```shell
$ readelf -rW demo.o

Relocation section '.rela.text' at offset 0xa38 contains 2 entries:
    Offset             Info             Type               Symbol's Value  Symbol's Name + Addend
000000000000000c  000000050000000b R_X86_64_32S           0000000000000000 .rodata + 0
0000000000000018  0000000f00000002 R_X86_64_PC32          0000000000000000 puts - 4
...
```

上面的輸出我只有節錄重點部份，你可以看到它這邊顯示兩筆資料，最後一個欄位是這個重定址資訊應該要指向哪邊，第一筆是 `.rodata` 開頭的位置，我們再用一次 `readelf`

```shell
$ readelf -p .rodata demo.o

String dump of section '.rodata':
  [     0]  Hello world
```

開頭的位置正是我們的字串，而上面重定址的資訊就是指向我們的字串，或許看到這邊你會覺得奇怪，明明編譯器都把字串也放進目的檔裡了，為什麼程式中字串的位置會是 0 這個奇怪的位置呢？你還記得嗎，連結器會把目的檔們合併變成一個執行檔喔，如果有多個目的檔中都有像這樣的唯讀資料的話，這些資料都會被併到一個 `.rodata` 中的，字串的位置也可能會隨之改變，所以編譯器根本不知道最後字串的位置會在哪裡，只好先填 0 ，然後紀錄一筆資料告訴連結器要來修正這個位置，這個修正的過程就叫重定址

接下來我們稍微看一下這個重定址表的內容吧，第一個 offset 是需要重定址的位置，第一筆是 16 進位的 c 換算成十進位就是 12 ，你可以在更上面的反組譯結果的中間那個用 16 進位表示每個指令的欄位數一下， `mov` 指令後的那個連續的 0 是不是正好從第 12 個開始的 (記得一開始的位置是 0 喔，這跟陣列下標的起始位置是一樣的) ， `Type` 則是描述這個位置應該要用什麼方式填進去，比如填相對位置或是絕對位置，相對位置又是相對於哪邊之類的，至於每個代表的意思是什麼，正好在前一篇提到的 [`goblin` 的文件][goblin-reloc] 中有一張表寫出了大部份常用的類型

[goblin-reloc]: https://docs.rs/goblin/0.0.24/goblin/elf/reloc/index.html

只要根據這些資料，連結器就可以在組合完執行檔後對檔案中的位置進行修正了

參考資料
--------

- https://stackoverflow.com/questions/48942103/how-to-understand-fields-of-relocation-section-rela-plt
- https://stackoverflow.com/questions/6093547/what-do-r-x86-64-32s-and-r-x86-64-64-relocation-mean
