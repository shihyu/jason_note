ELF
===

所以我們平常在執行的程式檔案裡放了些什麼，又是怎麼存的呢？這就要講到執行檔的格式 `ELF` 了， `ELF` 的全名是 Executable and Linkable Format ，對就是可執行又可連結的格式，這名字取的超直白的，不過根據 wiki ，這個格式在 1999 年就成為 Unix 下的執行檔標準格式了，它大致可以分成幾個部份：

1. 記錄基本資料的表頭 (ELF header)
2. 記錄程式該怎麼載入記憶體的 program header table
3. 記錄檔案內的分段的 section header table
4. 數個分段 (section)

不過開始介紹這些東西之前，先來介紹讀取這些資料的工具 `readelf` 吧，比如要讀取 ELF header 的話就找個執行檔，然後輸入：

```shell
$ readelf -h <path/to/executable>
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              DYN (Shared object file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x650
  Start of program headers:          64 (bytes into file)
  Start of section headers:          4384 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         8
  Size of section headers:           64 (bytes)
  Number of section headers:         26
  Section header string table index: 25
```

ELF header
----------

在上面已經有由 `readelf` 所讀出來的內容了，在表頭中有的資料有：

1. Magic Number： 這固定是在開頭的 `\x7fELF` ，可以簡單的用這個來判斷是不是 ELF 執行檔
2. 程式的位元數、類型 (動態函式庫或是一般執行檔)、指令集資訊
3. 程式開始的位置
4. program header 與 section header 開始的位置與大小

這些資料標註了這個執行檔的基本資訊，與如何找到其它必要的資訊，另外在檔案型態的部份，為了要支援 ALSR ，所以現在的程式大多編譯成位置無關程式碼 (PIE, Position Independent Executable) ，這也導致程式的類型變的跟動態函式庫一樣了，另外 Gnome 下預設的檔案管理器 nautilus 也因此把執行檔都判斷為函式庫而無法執行，這點老實說很麻煩

Program header
--------------

先用 `readelf` 看看吧

```shell
$ readelf -l c

Elf file type is DYN (Shared object file)
Entry point 0x650
There are 8 program headers, starting at offset 64

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  PHDR           0x0000000000000040 0x0000000000000040 0x0000000000000040
                 0x00000000000001c0 0x00000000000001c0  R      0x8
  INTERP         0x0000000000000238 0x0000000000000238 0x0000000000000238
                 0x000000000000001c 0x000000000000001c  R      0x1
      [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
  LOAD           0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000a70 0x0000000000000a70  R E    0x200000
  LOAD           0x0000000000000d98 0x0000000000200d98 0x0000000000200d98
                 0x0000000000000278 0x0000000000000280  RW     0x200000
  DYNAMIC        0x0000000000000da8 0x0000000000200da8 0x0000000000200da8
                 0x00000000000001f0 0x00000000000001f0  RW     0x8
  NOTE           0x0000000000000274 0x0000000000000274 0x0000000000000274
                 0x0000000000000024 0x0000000000000024  R      0x4
  GNU_EH_FRAME   0x00000000000008d4 0x00000000000008d4 0x00000000000008d4
                 0x0000000000000054 0x0000000000000054  R      0x4
  GNU_STACK      0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000000 0x0000000000000000  RW     0x8

 Section to Segment mapping:
  Segment Sections...
   00
   01     .interp
   02     .interp .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt .init .plt .plt.got .text .fini .rodata .eh_frame_hdr .eh_frame
   03     .init_array .fini_array .dynamic .got .data .bss
   04     .dynamic
   05     .note.gnu.build-id
   06     .eh_frame_hdr
   07
```

這個表記錄的是要如何把這個執行檔載入，以及每個段的可讀可寫可執行的屬性該如何設定，這個輸出分成兩個部份，先講上面的部份，第一個 `Type` 的欄位就是標記這個記憶體區段的類型，這邊也正好是幾個比較常見的類型：

1. PHDR： 就是這張表本身啦
2. INTERP： 紀錄使用的動態連結器 (Dynamic Linker) ，在 Linux 下基本上會稱為 `ld.so`，它是做什麼的之後再說明吧
3. LOAD： 必須要載入的區段，程式碼本身與資料都是這種類型
4. DYNAMIC： 與動態連結有關的資訊
5. NOTE： 類似註解的資訊，通常是可有可無的區段，不用的話用 `strip` 這個程式移除掉也沒關係
6. GNU_EH_FRAME： 這個先賣個關子
7. GNU_STACK： 用來紀錄 stack 的屬性用的

每個段都會紀錄它在檔案的哪個位置，它的大小與它應該被載入到的相對位置，有這些資訊就可以載入程式了，之後再根據屬性的欄位設定好是要可讀還是可寫就行了

下面的那部份是每個記憶體的區段 (segment) 與程式內的區段 (section) 對應的關係，像 `02` 這個段裡實際就包含了 `init` 與 `finit`，另外還有程式本體的 `text` 與唯讀資料的 `rodata` 的部份

Section header
--------------

```shell
$ readelf -S c
There are 26 section headers, starting at offset 0x1120:

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .interp           PROGBITS         0000000000000238  00000238
       000000000000001c  0000000000000000   A       0     0     1
  ...
  [10] .init             PROGBITS         00000000000005d8  000005d8
       0000000000000017  0000000000000000  AX       0     0     4
  ...
  [13] .text             PROGBITS         0000000000000650  00000650
       000000000000026e  0000000000000000  AX       0     0     16
  [14] .fini             PROGBITS         00000000000008c0  000008c0
       0000000000000009  0000000000000000  AX       0     0     4
  [15] .rodata           PROGBITS         00000000000008cc  000008cc
       0000000000000008  0000000000000000   A       0     0     4
  ...
  [22] .data             PROGBITS         0000000000201000  00001000
       0000000000000010  0000000000000000  WA       0     0     8
  [23] .bss              NOBITS           0000000000201010  00001010
       0000000000000008  0000000000000000  WA       0     0     4
  [24] .comment          PROGBITS         0000000000000000  00001010
       000000000000002b  0000000000000001  MS       0     0     1
  [25] .shstrtab         STRTAB           0000000000000000  0000103b
       00000000000000e0  0000000000000000           0     0     1
```

上面的輸出有省略一部份，這張表其實是給連結器 (linker) 看的，程式最後必須經過連結的步驟，將靜態函式庫，以 Rust 來說可以說是 crate 吧，連結在一起，而連結器的工具就是根據這張表與預先定義好的規則將各個檔案組合成一個執行檔，此外，這張表其實在完成連結後對於程式如何載入是沒有影響的，理論上可以用工具把它移除掉

> Rust 的 crate 也不一定是靜態函式庫，可能會編譯成動態函式庫，或是本身有連結到動態函式庫

上面有些常用的區段名稱：

1. `text`: 程式碼本身
2. `rodata`: 唯讀資料，這段在 program header 的地方其實可以看到被併入 `text` 一起載入了呢
3. `data`: 可寫的資料，同時有初始值的
4. `bss`: 同樣是可寫的資料，只是這張表內使用的值都是 `0`，於是這邊的資料就可以不用存在檔案中，只要紀錄大小就好了

這些名稱算是一個約定好的名稱，連結器的規則基本上也是根據這些名稱編寫的，不過其實可以自己加新的區段也是沒問題的，只是如果不去修改連結規則可能就不會載入了

另外先介紹一個 crate - [`goblin`][goblin] ，對，就是那個哥布林 (不知道你想到的是哪個)，它是個執行檔的 parser ，不只支援 ELF ，連 windows 的 PE 與 Mac 用的 Mach-o 都能解析，之後會再用它做些有趣的東西出來，今天就先試用一下就好：

[goblin]: https://github.com/m4b/goblin

```rust
use goblin::elf::Elf;
use std::{env, fs};

fn main() {
    let buf = fs::read(env::args().nth(1).unwrap()).unwrap();
    let elf = Elf::parse(&buf).unwrap();
    println!("{:#?}", elf.program_headers);
}
```

像這樣就可以印出程式的 program header 了：

```plain
[
    ProgramHeader {
        p_type: "PT_PHDR",
        p_flags: 0x4,
        p_offset: 0x40,
        p_vaddr: 0x40,
        p_paddr: 0x40,
        p_filesz: 0x1c0,
        p_memsz: 0x1c0,
        p_align: 8,
    },
    ProgramHeader {
        p_type: "PT_INTERP",
        p_flags: 0x4,
        p_offset: 0x238,
        p_vaddr: 0x238,
        p_paddr: 0x238,
        p_filesz: 0x1c,
        p_memsz: 0x1c,
        p_align: 1,
    },
    ProgramHeader {
        p_type: "PT_LOAD",
        p_flags: 0x5,
        p_offset: 0x0,
        p_vaddr: 0x0,
        p_paddr: 0x0,
        p_filesz: 0xa70,
        p_memsz: 0xa70,
        p_align: 2097152,
    },
    ...
]
```

> 另外這邊有件事情要講一下，因為我昨天不小心忘記發文的原因導致連續發文中斷了，因此接下來的內容將不一定會每天更新，我會盡量將內容弄到比較完整後才更新
