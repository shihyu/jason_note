<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [第七章：鏈接](#%E7%AC%AC%E4%B8%83%E7%AB%A0%E9%93%BE%E6%8E%A5)
  - [7.1 編譯器驅動程序](#71-%E7%BC%96%E8%AF%91%E5%99%A8%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8F)
  - [7.2 靜態鏈接](#72-%E9%9D%99%E6%80%81%E9%93%BE%E6%8E%A5)
  - [7.3 目標文件](#73-%E7%9B%AE%E6%A0%87%E6%96%87%E4%BB%B6)
  - [7.4 可重定位目標文件](#74-%E5%8F%AF%E9%87%8D%E5%AE%9A%E4%BD%8D%E7%9B%AE%E6%A0%87%E6%96%87%E4%BB%B6)
  - [7.5 符號和符號表](#75-%E7%AC%A6%E5%8F%B7%E5%92%8C%E7%AC%A6%E5%8F%B7%E8%A1%A8)
  - [7.6 符號解析](#76-%E7%AC%A6%E5%8F%B7%E8%A7%A3%E6%9E%90)
    - [鏈接器如何解析多重定義的全局符號](#%E9%93%BE%E6%8E%A5%E5%99%A8%E5%A6%82%E4%BD%95%E8%A7%A3%E6%9E%90%E5%A4%9A%E9%87%8D%E5%AE%9A%E4%B9%89%E7%9A%84%E5%85%A8%E5%B1%80%E7%AC%A6%E5%8F%B7)
    - [與靜態庫鏈接](#%E4%B8%8E%E9%9D%99%E6%80%81%E5%BA%93%E9%93%BE%E6%8E%A5)
    - [鏈接器如何使用靜態庫來解析引用](#%E9%93%BE%E6%8E%A5%E5%99%A8%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8%E9%9D%99%E6%80%81%E5%BA%93%E6%9D%A5%E8%A7%A3%E6%9E%90%E5%BC%95%E7%94%A8)
  - [7.7 重定位](#77-%E9%87%8D%E5%AE%9A%E4%BD%8D)
    - [重定位條目（relocation entry）](#%E9%87%8D%E5%AE%9A%E4%BD%8D%E6%9D%A1%E7%9B%AErelocation-entry)
    - [重定位符號引用](#%E9%87%8D%E5%AE%9A%E4%BD%8D%E7%AC%A6%E5%8F%B7%E5%BC%95%E7%94%A8)
  - [7.8 可執行目標文件](#78-%E5%8F%AF%E6%89%A7%E8%A1%8C%E7%9B%AE%E6%A0%87%E6%96%87%E4%BB%B6)
  - [7.9 加載可執行目標文件](#79-%E5%8A%A0%E8%BD%BD%E5%8F%AF%E6%89%A7%E8%A1%8C%E7%9B%AE%E6%A0%87%E6%96%87%E4%BB%B6)
  - [7.10 動態鏈接共享庫](#710-%E5%8A%A8%E6%80%81%E9%93%BE%E6%8E%A5%E5%85%B1%E4%BA%AB%E5%BA%93)
  - [7.11 從應用程序中加載和鏈接共享庫](#711-%E4%BB%8E%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E4%B8%AD%E5%8A%A0%E8%BD%BD%E5%92%8C%E9%93%BE%E6%8E%A5%E5%85%B1%E4%BA%AB%E5%BA%93)
  - [7.12 位置無關代碼](#712-%E4%BD%8D%E7%BD%AE%E6%97%A0%E5%85%B3%E4%BB%A3%E7%A0%81)
  - [7.13 庫打樁機制](#713-%E5%BA%93%E6%89%93%E6%A1%A9%E6%9C%BA%E5%88%B6)
    - [編譯期打樁](#%E7%BC%96%E8%AF%91%E6%9C%9F%E6%89%93%E6%A1%A9)
    - [鏈接時打樁](#%E9%93%BE%E6%8E%A5%E6%97%B6%E6%89%93%E6%A1%A9)
    - [運行時打樁](#%E8%BF%90%E8%A1%8C%E6%97%B6%E6%89%93%E6%A1%A9)
  - [7.14 處理目標文件的工具](#714-%E5%A4%84%E7%90%86%E7%9B%AE%E6%A0%87%E6%96%87%E4%BB%B6%E7%9A%84%E5%B7%A5%E5%85%B7)
  - [7.15 小結](#715-%E5%B0%8F%E7%BB%93)
  - [補充材料](#%E8%A1%A5%E5%85%85%E6%9D%90%E6%96%99)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 第七章：鏈接

## 7.1 編譯器驅動程序

大多數編譯系統提供編譯器驅動程序，在用戶需要時調用預處理器、編譯器、彙編器和鏈接器。
- 比如GCC：
```shell
gcc -Og -o prog main.c sum.c
```
- 這個步驟會調用預處理器`cpp`、C編譯器`ccl`、彙編器`as`、鏈接器`ld`。
- 執行：
```shell
./prog
```
- 執行時會調用加載器（loader），將可執行目標文件的代碼和數據複製到內存，然後將控制轉移到這個程序開頭。

## 7.2 靜態鏈接

像ld這樣的靜態鏈接器（static linker）以一組可重定位目標文件和命令行參數作為輸入，生成一個完全鏈接的、可以加載和運行的可執行目標文件作為輸出。鏈接器主要完成兩個任務：
- 符號解析（symbol resolution）：目標文件會定義和引用符號，每個符號對應與一個函數、一個全局變量、或者一個靜態變量。符號解析的目的是將每個符號引用正好和一個符號定義聯繫起來。
- 重定位（relocation）：編譯器和彙編器生成地址從0開始的代碼和數據節。鏈接器通過把每個符號定義與一個內存位置關聯起來，從而重定位這些節（section）。然後修改所有對這些符號的引用，使他們指向這個內存位置。鏈接器使用匯編器產生的重定位條目（relocation entry）的詳細指令，不加甄別地執行這樣的重定位。

基本事實：目標文件是字節塊的集合。
- 這些塊中，有的包含數據，有的包含代碼，其他的則包含引導鏈接器和加載器的數據結構。
- 鏈接器將這些塊連接起來，確定被連接塊的運行時位置，並且修改代碼和數據塊的各種位置。

## 7.3 目標文件

目標文件有三種形式：
- 可重定位目標文件：包含二進制代碼和數據，其形式可以在編譯時與其他可重定位目標文件鏈接起來，創建一個可執行目標文件。
- 可執行目標文件：包含二進制代碼和數據，可以直接複製到內存中執行。
- 共享目標文件：一種特殊的可重定位目標文件，可以在加載或者運行時被動態加載進內存並鏈接。

編譯器和彙編器生成可重定位目標文件（包括共享目標文件），鏈接器生成可執行目標文件。

目標文件是按照特定文件格式組織的，各個系統中的目標文件都不相同：
- Windows使用可移植可執行文件（Portable Executable，PE）。
- MaxOS-X使用Mach-O格式。
- 現代x86-64 Linux和Unix使用可執行可連接格式（Executable and Linkable Format，ELF）。
- 這裡集中於ELF文件格式，其他文件格式在概念上也是類似的。

## 7.4 可重定位目標文件

ELF可重定位目標文件典型格式：

![](ELF_relocable_object_file.JPG)

- ELF頭以一個16字節的序列開始，在本地64位Linux上是`7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00`。
- 這個序列描述了生成該文件的系統的字的大小和字節序，以及幫助鏈接器語法分析和解析目標文件的信息：ELF頭大小、目標文件類型、機器類型、節頭部表的文件偏移以及節頭部表中條目的大小和數量。不同節的位置和大小是由節頭部表描述的，其中目標文件中每個節都有一個固定大小的條目。
- 其中包含的信息可以通過`readelf -h`得到：
```
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              REL (Relocatable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x0
  Start of program headers:          0 (bytes into file)
  Start of section headers:          504 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           0 (bytes)
  Number of program headers:         0
  Size of section headers:           64 (bytes)
  Number of section headers:         11
  Section header string table index: 10
```
- 在ELF頭和節頭部表之間的都是節，一般典型的ELF可重定位文件包含下列幾個節：
    - `.text`：已編譯程序的機器代碼。
    - `.rodata`：只讀數據，比如字符串字面量，跳錶等。
    - `.data`：已初始化的全局和靜態C變量。
    - `.bss`：未初始化的全局和靜態C變量，以及所有被初始化為0的全局或靜態變量。目標文件中這個節不佔據實際空間，僅僅是一個佔位符，區分已初始化和未初始化是為了提供空間效率：未初始化變量不佔據目標文件中的任何磁盤空間。在內存中分配時，初始化為0（通過內存映射到匿名文件初始化，見第九章）。
    - `.symtab`：符號表，存放程序中定義和引用的全局變量的信息。與編譯器的符號表不同，`.symtab`不包含任何局部變量的條目。
    - `.rel.text`：一個`.text`節中位置的列表，當鏈接器把這個目標文件和其他文件組合時，需要修改這些設置。一般而言，任何調用外部函數或者引用全局變量的指令都需要修改。調用本地函數的指令則不需要修改。注意的是可執行目標文件並不需要重定位信息，因此通常省略。
    - `.rel.data`：被模塊引用或者定義的所有全局變量的重定位信息。一般而言，任何已初始化的全局變量，如果它的初始值是一個全局變量地址或者外部定義函數的地址，都需要修改。
    - `.debug`：符號調試表，條目是程序中定義的局部變量和類型定義、程序中定義和引用的全局變量、以及原始C源文件。只有`-g`選項編譯才會生成。
    - `.line`：原始C源程序中的行號與`.text`節中機器指令之間的映射。`-g`選項編譯才會生成。
    - `.strtab`：一個字符串表，內容包括`.symtab .debug`節中的符號表，以及節頭部中的節名字，字符串表是以null結尾的字符串序列。
- `.bss`命名起源於IBM 704彙編語言中的塊存儲開始（Block Storage Start）指令的首字母縮寫，沿用至今。現在的話原始含義基本不具備含義，可以簡記為Better Save Space。

## 7.5 符號和符號表

每個可重定位目標文件都有一個符號表，包含了其中定義和引用的符號的信息。在鏈接器上下文中，有三種符號：
- 該模塊中定義能在其他模塊定義的**全局符號**：對應於非靜態的C函數和全局變量。
- 由其他模塊定義並在該模塊中被引用的全局符號：稱為**外部符號**，對應於在其他模塊定義的非靜態C函數和全局變量。
- 只在該模塊內部定義和引用的**局部符號**：對應於靜態C函數和靜態全局變量。

靜態變量（static，不管是局部還是全局）不是在棧中分配而是在`.data .bss`中分配的，在符號表中會創建一個唯一的局部名稱：
```C
int* p1468_f()
{
    static int x = 0;
    return &x;
}
int* p468_g()
{
    static int x = 0;
    return &x;
}
int x;
```
- 彙編：
```x86asm
p1468_f:
	movl	$x.1, %eax
	ret
p468_g:
	movl	$x.0, %eax
	ret

	.local	x.0
	.comm	x.0,4,4
	.local	x.1
	.comm	x.1,4,4
	.globl	x
	.bss
	.align 4
	.type	x, @object
	.size	x, 4
x:
	.zero	4
```
- 在不同作用域內的同名靜態變量在編譯後會生成不同名字的局部鏈接器符號`x.0 x.1`。

符號表條目中包含的信息包括：
- 符號名稱：保存為在字符串表中的偏移，指向一個null結尾的字符串。
- 符號的地址：節中的相對偏移（可重定位文件中）或者絕對地址（可執行目標文件）。
- 符號類型：函數還是變量。
- 符號在哪個節：比如函數在`.text`，而變量在`.data`。
- 綁定：本地還是全局。
- 數據長度。

每個符號都被分到目標文件中的某個節：
- 有三個特殊的偽節在節頭部表中沒有條目：ABS表示不該被重定位的符號，UNDEF表示未定義符號，COMMON表示還未分配位置的未初始化的條目（比如`int a[]`這種嗎？）。
- 可重定位目標文件才有這些偽節，可執行目標文件中沒有。
- 現代版本的GCC的分配規則：
    - 未初始化的全局變量分配在`COMMON`節中，而未初始化的靜態變量、初始化為0的全局或靜態變量則放在`.bss`中。
- 使用`readelf -s test.o`可以讀取目標文件的符號表，上面的例子中的符號表：
```
Symbol table '.symtab' contains 13 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS test.c
     2: 0000000000000000     0 SECTION LOCAL  DEFAULT    1 
     3: 0000000000000000     0 SECTION LOCAL  DEFAULT    3 
     4: 0000000000000000     0 SECTION LOCAL  DEFAULT    4 
     5: 0000000000000008     4 OBJECT  LOCAL  DEFAULT    4 x.1
     6: 0000000000000004     4 OBJECT  LOCAL  DEFAULT    4 x.0
     7: 0000000000000000     0 SECTION LOCAL  DEFAULT    6 
     8: 0000000000000000     0 SECTION LOCAL  DEFAULT    7 
     9: 0000000000000000     0 SECTION LOCAL  DEFAULT    5 
    10: 0000000000000000     6 FUNC    GLOBAL DEFAULT    1 p1468_f
    11: 0000000000000006     6 FUNC    GLOBAL DEFAULT    1 p468_g
    12: 0000000000000000     4 OBJECT  GLOBAL DEFAULT    4 x
```
- 其中`Ndx`通過索引來表示位於哪個節，只有上面的三個偽節是顯式的字符串。
- `readelf -S`顯式節頭部表：
```
There are 12 section headers, starting at offset 0x2c0:

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .text             PROGBITS         0000000000000000  00000040
       000000000000000c  0000000000000000  AX       0     0     1
  [ 2] .rela.text        RELA             0000000000000000  00000200
       0000000000000030  0000000000000018   I       9     1     8
  [ 3] .data             PROGBITS         0000000000000000  0000004c
       0000000000000000  0000000000000000  WA       0     0     1
  [ 4] .bss              NOBITS           0000000000000000  0000004c
       000000000000000c  0000000000000000  WA       0     0     4
  [ 5] .comment          PROGBITS         0000000000000000  0000004c
       0000000000000013  0000000000000001  MS       0     0     1
  [ 6] .note.GNU-stack   PROGBITS         0000000000000000  0000005f
       0000000000000000  0000000000000000           0     0     1
  [ 7] .eh_frame         PROGBITS         0000000000000000  00000060
       0000000000000040  0000000000000000   A       0     0     8
  [ 8] .rela.eh_frame    RELA             0000000000000000  00000230
       0000000000000030  0000000000000018   I       9     7     8
  [ 9] .symtab           SYMTAB           0000000000000000  000000a0
       0000000000000138  0000000000000018          10    10     8
  [10] .strtab           STRTAB           0000000000000000  000001d8
       0000000000000021  0000000000000000           0     0     1
  [11] .shstrtab         STRTAB           0000000000000000  00000260
       0000000000000059  0000000000000000           0     0     1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  l (large), p (processor specific)
```

## 7.6 符號解析

局部符號：
- 鏈接器解析符號引用的方法就是將每個引用與他們輸入的可重定位目標文件的符號表中的一個確定符號關聯起來。
- 局部符號的解析相對來說比較簡單，每個模塊中每個局部符號只能有一個定義。
- 靜態局部變量也會有本地鏈接符號，編譯器會確保他們擁有唯一的名字。

全局符號：
- 全局符號的解析相對來說棘手很多。
- 當編譯器遇到一個非當前模塊定義的符號時，會假設該符號在其他模塊定義，並生成一個鏈接器符號表條目，並把它交給鏈接器處理。
- 如果鏈接器在任何輸入條目中都找不到這個符號，就輸出一條錯誤信息並終止。
- 比如沒有定義`main`函數鏈接器就會輸出：
```
gcc test.c -o test -Wall -Wextra -pedantic-errors -Wshadow -Wno-unused-parameter -Og -DNDEBUG
/usr/bin/ld: /lib/x86_64-linux-gnu/crt1.o: in function `_start':
(.text+0x24): undefined reference to `main'
collect2: error: ld returned 1 exit status
make: [Makefile:55: test] Error 1 (ignored)
```
- 對全局符號的解析需要注意，如果多個目標文件都定義了某個符號，那麼鏈接器可能會報錯或者說選擇其中一個定義拋棄其他定義，這取決於場景。

符號重整：
- C++中允許函數重載，需要將參數列表整合進函數符號名稱中才能避免重名。
- 這個過程叫做符號重整（name mangling），相反的過程叫做demangling。

### 鏈接器如何解析多重定義的全局符號

鏈接器的輸入是一組可重定位目標文件，每個模塊定義一組符號，有些是局部的（僅對模塊內可見），有些是全局的（其他模塊也可見），如果多個模塊中多個符號同名，那麼需要特殊處理：
- 編譯時，編譯器向彙編器輸出每個全局符號，或者是強符號（strong）或者弱符號（weak）。這個信息被編碼到可重定位目標文件的符號表中。
- **函數和已初始化的全局變量是強符號，未初始化的全局變量是弱符號**。
- 根據符號強弱關係，Linux使用如下規則來處理：
    - 不允許多個同名強符號。
    - 如果有一個強符號，多個弱符號，選擇強符號。
    - 如果有多個弱符號同名，選擇其中任意一個。
- 這非常好理解，全局變量默認`extern`，如果初始化就成為強符號，一個全局變量不能有多個初始值，所以最多隻能有一個同名強符號。不初始化就是弱符號，所有模塊中都未初始化，那麼隨便選擇一個就好，分配空間後零初始化，所有該符號都引用這個位置。
- 如果重複定義的符號類型不同，那麼就是絕對的錯誤，可能產生很晦澀難以察覺的問題。
- 弱符號未被分配到`COMMON`段中，把決定權留給鏈接器。強符號則會直接分配到`.bss`中。

### 與靜態庫鏈接

現代編譯器都提供機制將一組目標文件打包成一個單獨的文件，稱之為靜態庫（static library），它可以用作鏈接器的輸入。
- 當鏈接器構造一個輸出可執行文件時，它只複製靜態庫中被應用程序引用的目標模塊。
- 靜態庫的缺點：
    - 每個可執行文件中都會重複包含靜態庫中的內容，浪費磁盤空間以及運行時浪費內存空間。
    - 庫發生任何更改都需要更新靜態庫，無論改變多麼小。
- 優點：
    - 相比起單獨鏈接庫中所有需要的目標文件，鏈接到庫更加方便。
    - 鏈接時，程序只複製引用到的目標模塊，不會把庫中所有內容鏈接進來。
- Linux系統中，靜態庫是以存檔（archive）的特殊文件格式存放在磁盤中的，存檔文件是一組可以連接起來的可重定位目標文件的集合。有一個頭部描述所有目標文件大小的大小和位置，存檔文件由後綴`.a`標識。

Linux中創建靜態庫：
```shell
gcc -c file1.c file2.c
ar rcs libtarget.a file1.o file2.o
```
- 編譯時鏈接靜態庫：
```shell
gcc -static -o exe_target filexxx.o ./libtarget.a
gcc -static -o exe_target filexxx.o -L. -ltarget
```
- 其中`-ltarget`與`./libtarget.a`等價，不過前者通過`-L`選項將庫的路徑顯式添加到庫目錄，後者直接通過文件方式指定庫。

### 鏈接器如何使用靜態庫來解析引用

靜態庫很有用，但同時可能令人迷惑。需要特別注意Linux鏈接器使用他們解析外部引用的方式：
- 在符號解析階段，鏈接器從左到右按照他們在編譯器驅動程序中出現的順序來掃描可重定位目標文件和存檔文件（靜態庫）。
- 在這期間，編譯器會自動將`.c`翻譯為`.o`文件。
- 掃描期間，鏈接器維護一個可重定位目標文件集合E，這個集合會合並起來形成可執行目標文件。一個未解析的符號引用（即引用了但未定義的）集合U，以及一個前面輸入文件中定義的符號集合D。
- 初始時，E、U、D均為空。
- 處理過程如下：
     - 對於命令行上的每個輸入文件f，鏈接器會判斷這是一個目標文件還是存檔文件。如果f是目標文件，那麼鏈接器把f添加到E，並同時根據f修改E和D，並繼續下一個文件。
     - 如果f是一個存檔文件，那麼鏈接器嘗試匹配U中未解析的符號和存檔文件成員定義的符號。如果某個存檔文件成員m，定義了一個符號來解析U中的一個引用，就講這個成員加入E。對存檔文件所有成員執行這個過程，任何不包含在E中的目標文件成員將被簡單地丟棄。並繼續處理下一個文件。
     - 鏈接器完成命令行中對文件的掃描後，如果U非空，就會輸出錯誤並終止。否則，就會合並和重定位E中的目標文件，構造輸出的可執行目標文件。
- 以上的過程就導致了一個問題，如果將庫放到前面就會導致無法解析庫中的引用。所以關於庫的一般準則是**將庫放到命令行末尾**。
- 如果各個庫相互獨立（也就是說相互之間沒有任何符號引用），那麼他們不需要對他們進行排序。
- 如果庫之間存在依賴關係，那麼必須將他們按照依賴關係進行拓撲排序後，將被依賴的放在後面，依賴其他庫的放在前面。
- 如果庫之間存在環形依賴關係，那麼可以在不同熟悉怒兩次添加同一個庫解決。
- 例子，如果`libx.a liby.a`相互依賴（當然這通常來說並不是好的編程習慣），那麼可以這樣鏈接：
```shell
gcc xxx.o ./libx.a ./liby.a ./libx.a
```

## 7.7 重定位

一旦鏈接器完成了符號解析這一步，就把代碼中的每個符號引用和正好一個符號定義關聯起來了。此時鏈接器已經知道了目標模塊中的代碼節和數據節的確切大小，就可以開始重定位步驟了：
- 重定位節和符號定義：
     - 首先，鏈接器將所有相同類型的節合併為同一類型的新的聚合節。
     - 然後鏈接器將運行時內存賦給聚合節，賦給輸入模塊定義的每個節，賦給輸入模塊定義的每個模塊，這一步完成時，程序中每條指令和全局變量都有了唯一的運行時內存地址。
- 重定位節中的符號引用：
     - 這一步中，鏈接器修改代碼節和數據節中對每一個符號的引用，使他們指向正確的運行時地址。
     - 執行這一步時，鏈接器依賴可重定位目標模塊中的稱為**重定位條目**（relocation entry）的數據結構。

### 重定位條目（relocation entry）

當彙編器引用一個目標模塊時，它並不知道數據和代碼最終放在內存什麼位置。也不知道這個模塊引用的任何外部定義的函數或者全局變量的位置，所以無論何時，彙編器遇到對最終位置的位置的目標引用，就會生成一個重定位條目，告訴鏈接器在將目標文件合併成可執行文件時如何修改這個引用。
- 代碼的重定位條目放在`.rel.text`，已初始化數據的重定位條目放在`.rel.data`。
- ELF重定位條目格式：
```C
typedef struct
{
  Elf64_Addr	r_offset;		/* Address */
  Elf64_Xword	r_info;			/* Relocation type and symbol index */
  Elf64_Sxword	r_addend;		/* Addend */
} Elf64_Rela;
```
- 其中`offset`是要修改引用的節偏移，`info`被分為兩個32位信息：重定位類型和用來表示符號的符號表索引，`addend`是一個符號常數，一些類型的重定位要使用它對被修改引用的值做偏移調整。
- ELF定義了32種不同的重定位類型，我們只需要關心兩種：
- `R_X86_64_PC32`：重定位一個使用32位PC相對地址的引用。PC相對地址就是距PC當前運行值的偏移量。運行PC相對尋址指令時，將指令中編碼的32位值加上PC當前值，得到有效地址。PC的值通常是下一條指令在內存中的地址。
- `R_X86_64_32`：重定位一個使用32位絕對地址的引用。通過絕對尋址，CPU直接使用在指令中編碼的32位值作為有效地址，不需要進一步修改。
- 這兩種重定位類型支持x86-64小代碼模型（small code model），該模型假設可執行目標文件中的代碼和數據總體大小小於2GB，可以使用32位PC相對尋址來訪問。GCC默認使用小代碼模型，如果要使用中代碼或者大代碼模型可以用`-mcmodel=medium -mcmodel=large`選項編譯。

### 重定位符號引用

例子：
```C
int sum(int *a, int n);
int array[2] = {1, 2};

int main()
{
    int val = sum(array, 2);
    return val;
}
```
- 生成可重定位目標文件後反彙編：
```
Disassembly of section .text:

0000000000000000 <main>:
   0:   48 83 ec 08             sub    $0x8,%rsp
   4:   be 02 00 00 00          mov    $0x2,%esi
   9:   bf 00 00 00 00          mov    $0x0,%edi
                        a: R_X86_64_32  array
   e:   e8 00 00 00 00          callq  13 <main+0x13>
                        f: R_X86_64_PLT32       sum-0x4
  13:   48 83 c4 08             add    $0x8,%rsp
  17:   c3                      retq
```
- 關於重定位的具體細節這裡不贅述。

## 7.8 可執行目標文件

ELF可執行文件結構：

![](ELF_executable_object_file.JPG)

- 其結構類似於可重定位目標文件，還包括了程序入口點，也就是程序運行時要執行的第一條指令。
- `.text .rodata .data`可可重定位目標文件類似，不過在可執行目標文件中，這些節已經被重定位他們最終的運行時內存地址。
- `.init`節定義了一個小函數，叫做`_init`，程序的初始化代碼會調用它。
- 可執行文件是完全鏈接的，不再需要`rel`節。
- ELF可執行文件被設計得很容易加載到內存，可執行文件的連續的片（chunk）被映射到連續的內存段，程序頭部表描述了這種關係。由`objdump -dx`得到上面的例子程序的節頭部表：
```
Program Header:
    PHDR off    0x0000000000000040 vaddr 0x0000000000400040 paddr 0x0000000000400040 align 2**3
         filesz 0x0000000000000268 memsz 0x0000000000000268 flags r--
  INTERP off    0x00000000000002a8 vaddr 0x00000000004002a8 paddr 0x00000000004002a8 align 2**0
         filesz 0x000000000000001c memsz 0x000000000000001c flags r--
    LOAD off    0x0000000000000000 vaddr 0x0000000000400000 paddr 0x0000000000400000 align 2**12
         filesz 0x00000000000003f8 memsz 0x00000000000003f8 flags r--
    LOAD off    0x0000000000001000 vaddr 0x0000000000401000 paddr 0x0000000000401000 align 2**12
         filesz 0x00000000000001c5 memsz 0x00000000000001c5 flags r-x
    LOAD off    0x0000000000002000 vaddr 0x0000000000402000 paddr 0x0000000000402000 align 2**12
         filesz 0x0000000000000108 memsz 0x0000000000000108 flags r--
    LOAD off    0x0000000000002e40 vaddr 0x0000000000403e40 paddr 0x0000000000403e40 align 2**12
         filesz 0x00000000000001f0 memsz 0x00000000000001f8 flags rw-
 DYNAMIC off    0x0000000000002e50 vaddr 0x0000000000403e50 paddr 0x0000000000403e50 align 2**3
         filesz 0x00000000000001a0 memsz 0x00000000000001a0 flags rw-
    NOTE off    0x00000000000002c4 vaddr 0x00000000004002c4 paddr 0x00000000004002c4 align 2**2
         filesz 0x0000000000000020 memsz 0x0000000000000020 flags r--
EH_FRAME off    0x0000000000002004 vaddr 0x0000000000402004 paddr 0x0000000000402004 align 2**2
         filesz 0x000000000000003c memsz 0x000000000000003c flags r--
   STACK off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**4
         filesz 0x0000000000000000 memsz 0x0000000000000000 flags rw-
   RELRO off    0x0000000000002e40 vaddr 0x0000000000403e40 paddr 0x0000000000403e40 align 2**0
         filesz 0x00000000000001c0 memsz 0x00000000000001c0 flags r--
```
- 包含信息：
    - `off`：目標文件中的偏移。
    - `vaddr/paddr`：內存地址。
    - `align`：對齊要求。
    - `filesz`：目標文件中段大小。
    - `memsz`：內存中段大小。
    - `flags`：運行時訪問權限。

## 7.9 加載可執行目標文件

要運行可執行目標文件，可以直接在Linux Shell中輸入可執行目標文件名稱：
```shell
./prog
```
- 通過調用某個駐留在內存中的成為加載器的操作系統代碼來運行它。
- 任何Linux程序都可以通過調用`execve`函數來調用加載器，下一章會詳細介紹這個函數。
- 加載器將可執行目標文件中的代碼和數據從磁盤複製到內存中，然後跳轉到程序的第一條指令或者叫入口點來運行該程序。這個複製到內存並運行的過程稱之為**加載**。
- 在Linux x86-64中，代碼段總是從`0x400000`處開始的，後面是數據段，堆在數據段後，通過調用`malloc`向高地址生長。對後面是為共享模塊保留的，用戶棧從最大合法地址開始，從高地址向低地址生長。

![](LinuxX86-64_Program_memory_image.JPG)

- 棧地址從`2^48`開始，更高地址的部分是為內核代碼和數據保留的，對用戶代碼不可見。所謂內核就是操作系統駐留在內存的部分。
- 這裡為了簡潔，將各個區域畫得彼此相鄰。實際上由於`.data`段對齊要求，代碼段數據段之間是有間隙的。在分配棧、共享庫、堆段內存運行時地址時，鏈接器還會使用地址空間佈局隨機化（ASLR，第三章有介紹）。
- 程序每次運行時這些區域地址都會變，但他們的相對地址是不變的。
- 執行過程：
    - 加載器將可執行文件的片（chunk）賦值到代碼段和數據段之後，跳轉到程序入口點，魚就是`_start`函數地址：
    - 這個函數是系統目標文件`ctrl.o`中定義的，對所有C程序都一樣。
    - 其中調用系統啟動函數`__libc_start_main`，定義在`libc.so`中，它初始化執行環境，調用用戶層的`main`函數，處理`main`函數返回值，然後在需要時把控制返回給內核。
- 加載過程其實是有進程、虛擬內存和內存映射的工作參與其中，見第九章。這裡簡要概述：
    - 簡單來說，shell啟動一個程序時，會啟動一個子進程（`fork`），它是父進程的一個複製（COW機制），子進程通過`execve`系統調用啟動加載器。
    - 加載器刪除子進程現有的虛擬內存段，通過內存映射加載可執行文件的各個段（比如`.bss`、棧、堆這種就映射到匿名文件，初始化為0，其他則映射到可執行文件的具體位置）。
    - 然後跳轉到`_start`。
    - 這個過程除去一些頭部信息，沒有顯式的數據複製，直到CPU引用一個未被緩存到主存的頁面中的數據時才會將頁面從磁盤換入主存，才執行真正的數據或者代碼複製。

## 7.10 動態鏈接共享庫

前面接受的靜態庫解決了如何讓大量相關函數對應用程序可用的問題，但是靜態庫仍然存在一些缺點。
- 靜態庫需要定期維護與更新，即使只更改了實現而沒有更改接口，都需要重新與庫進行鏈接。
- 而另一個問題是某些所有程序都會用到的庫設施，沒有必要在每個文件中保留一份，也沒有必要在運行時在內存中保留多份。
- 動態庫則可以解決這些問題。

共享庫（shared library）是致力於解決靜態庫問題的現代產物：
- 共享庫是一個目標模塊，在運行或加載時可以加載到任意的內存地址，並和內存中的程序鏈接起來，這個過程稱為動態鏈接（dynamic linking），由一個叫做動態鏈接器（dynamic linker）的程序來執行。
- 共享庫也成為共享目標文件（shared object），Linux中常用`.so`後綴，在Winodws操作系統中則使用`.dll`（dynamic linked library，動態鏈接庫）後綴。
- 共享庫以兩種不同方式來共享：
    - 對於一個庫只有一個`.so`文件，所有引用該庫的可執行目標文件共享這個`.so`中的代碼和數據，而不是像靜態庫的內容那樣被複制和嵌入引用他們的可執行文件中。
    - 其次，在內存中，一個共享庫的`.text`節的一個副本被不同正在運行的進程共享，這是通過將共享庫的物理內存同時映射到不同進程的不同虛擬內存做到的。第九章有更多細節。
- 動態鏈接共享庫的過程：

![](Link_Shared_Library.JPG)

- 鏈接共享庫之前需要先生成共享庫：
```shell
gcc -shared -fpic -o libtarget.so file1.o file2.o
```
- `-fpic`指示生成位置無關代碼（position independent code），`-shared`指示鏈接器創建共享的目標文件。
- 鏈接到共享庫：
```shell
gcc -o prog file1.c file2.o ./libtarget.so
```
- 動態鏈接時，引用的動態庫中的代碼不會被複制可執行目標文件中，所以在運行時就必須動態地講動態庫加載進來。者通過加載器調用動態鏈接器（在Linux中是`ld-linux.so`庫做到這件事情）將動態庫動態鏈接。
- 鏈接了動態庫的可執行目標文件會將需要的動態庫編碼在文件中，靜態執行一些鏈接，然後程序加載時，動態完成鏈接過程，沒有動態庫的內容真正被複制到可執行文件中。
- 動態鏈接的信息被保存在`.interp`節，這一節包含了動態鏈接器的路徑名，動態鏈接器本身就是一個共享目標（Linux上的`ld-linux.so`）。
- 加載器不會像通常那樣直接將控制傳遞給應用，而是加載和執行這個動態鏈接器，然後動態鏈接器執行下列的重定位完成鏈接任務：
    - 重定位`libc.so`（C標準庫）和其他動態庫的文本和數據到某個內存段（通過內存映射將動態庫映射到堆和棧之間的內存區域）。
    - 重定位可執行目標文件中對所有動態庫中定義的符號的引用。
- 完成後才將控制傳遞給應用程序，從這個時刻開始，共享庫位置就固定了，在程序執行過程中不會變。

## 7.11 從應用程序中加載和鏈接共享庫

上面介紹了的自動進行的動態鏈接過程，要求在鏈接時將動態庫作為輸入。但是應用程序還可以在運行過程中動態加載和鏈接某個共享庫，而不需要在編譯時將動態庫鏈接進來：
- 這非常有用，舉個例子：
    - 用戶可以通過替換共享庫的新版本的方式更新軟件，不需要重新進行鏈接，不需要更新可執行目標文件。
    - 用戶可以動態的加載需要的庫，調用其中的函數，而不需要再`fork`和`execve`創建子進程在子進程的上下文中運行。函數會一直緩存在地址空間中，不需要創建新的上下文就可以執行特定代碼，開銷會降低很多，很快便能夠執行。而且不需要停下機器，就可以動態添加新的功能，新的動態庫。
- Linux提供的運行時動態鏈接接口：
```C
#include <dlfcn.h>

void *dlopen(const char *filename, int flags);

int dlclose(void *handle);

#define _GNU_SOURCE
#include <dlfcn.h>

void *dlmopen (Lmid_t lmid, const char *filename, int flags);
```
- 可通過`man dlopen`查看更詳細信息。
- `dlopen`函數加載並鏈接動態庫`filename`。
- 標誌：
    - `RTLD_GLOBAL`打開將解析`filename`中的外部符號。
    - 如果當前可執行文件是`-rdynamic`編譯的，那麼對於符號解析而言，它的全局符號也可用。
    - 還可以包括`RTLD_NOW`和`RTLD_LAZY`其中一者，可以與到標誌中，表示加載時解析對外部符號引用或者推遲直到引用庫中代碼時才解析符號。
- 返回一個句柄指針，加載失敗則返回NULL。
- `dlsym`可以去到動態庫中符號的地址：
```
NAME
       dlsym, dlvsym - obtain address of a symbol in a shared object or executable

SYNOPSIS
       #include <dlfcn.h>

       void *dlsym(void *handle, const char *symbol);

       #define _GNU_SOURCE
       #include <dlfcn.h>

       void *dlvsym(void *handle, char *symbol, char *version);
```
- `dlclose`卸載動態庫。
- `dlerror`則得到最近的`dlopen dlsym dlopen`的錯誤信息。
```
NAME
       dlerror - obtain error diagnostic for functions in the dlopen API

SYNOPSIS
       #include <dlfcn.h>

       char *dlerror(void);
```
- 最後如果程序中使用`dlopen dlsym dlclose dlerror`加載動態庫，需要添加鏈接選項`-ldl`，也就是說這些函數都在`libdl.so`中，需要鏈接進來。
- `-rdynamic`主要用於導出全局符號給動態庫用，如果動態庫用了可執行文件中的全局符號，那麼就必須要加這個選項。不加會導致`dlopen`失敗，通過`dlerror`可以獲取到這個信息。
- 通過`dlopen`加載的動態庫不需要特殊編譯。
- 有沒有部分導出符號的機制？這個導出機制和普通動態庫還不一樣，在編譯時就鏈接到動態庫是不需要用`-rdynamic`的。
- Windows中有一套類似機制，如`LoadLibrary`接口等。
- 例子見：[./SharedObject](./SharedObject)，執行`make run`。

Java程序中的JNI（Java Native Interface）允許Java程序調用本地的C或者C++代碼，也是通過這種機制實現的。

## 7.12 位置無關代碼

因為多個進程可以使用同一個庫，所以必須要提供這種機制，為了避免各種問題，現代系統以這樣一種方式編譯共享模塊的代碼段，使得他們可以加載到內存中的任何位置而無須鏈接器修改。使用這種方法，無限多個線程可以共享一個共享模塊的代碼塊的一個副本：
- 可以加載而無需重定位的代碼稱之為位置無關代碼（Position-Independent Code，PIC）。
- 添加`-fpic`選項可以使GCC生成位置無關代碼，共享庫編譯時必須總是指定該選項。
- 在x86-64系統中，對同一個模塊內符號的引用是不需要特殊處理使之成為PIC的，可以用PC相對尋址來編譯這些引用，構造目標文件時由靜態鏈接器重定位。
- 然而共享模塊定義的外部過程和對全局變量的引用需要一些特殊技巧。

PIC數據引用：
- 通過全局偏移量表（Global Offset Table，GOT）實現。關鍵思想是對全局偏移量表中條目的PC相對引用中的偏移量是一個運行時常量。

PIC函數調用：
- 通過GOT和過程鏈接表（Procedure Linkage Table，PLT）實現。使用延遲綁定機制，在第一次函數調用時才解析動態庫中函數的地址，代價相對較大，其後的每次調用都不會再進行解析。這有效地減小了解析庫中用不到的函數的開銷。細節略。

## 7.13 庫打樁機制

Linux鏈接器支持一個機制，成為庫打樁（library interpositioning），允許你截獲對共享庫函數的調用，替換為自己的代碼。
- 通過使用打樁機制，可以追蹤一個特殊庫函數的調用次數，驗證和追蹤它的輸入輸出值，甚至把它替換為一個完全不同的實現。
- 它的基本思想是：給定一個需要打樁的目標函數，創建一個包裝函數，它的原型和目標函數完全一致。使用某種特殊的打樁機制，你可以欺騙系統調用包裝函數而不是目標函數。包裝函數執行自己的邏輯然後調用目標函數，並將目標函數返回值傳遞給調用者。
- 打樁可以發生在編譯時、鏈接時或者程序被加載和執行的運行時。
- 以下例子對`malloc free`進行打樁。

### 編譯期打樁

- 主要通過宏完成：
- 例子：
```C
// malloc.h
#define malloc(size) mymalloc(size)
#define free(p) myfree(p)
void* mymalloc(size_t size);
void myfree(void* p);
// mymalloc.c
#ifdef COMPILETIME
// implementaion of mymalloc and myfree ...
#endif

// main.c
#include <stdio.h>
#include <malloc.h>
int main()
{
    int *p = malloc(10);
    free(p);
    return 0;
}
```
- 編譯：
```shell
gcc -DCOMPLETIME -c mymalloc.c
gcc -I. -o main main.c mymalloc.o
```
- 添加選項`-I.`則會進行打樁，去掉就就取消打樁。
- 就是一個簡單的條件編譯機制。
- 也可以使用宏作為開關，定義宏則打樁，不定義則不打樁，最後通過編譯選項中的`-DXXX`作為控制。

### 鏈接時打樁

Linux靜態鏈接器支持用`--wrap f`標誌進行連接時打樁：
- 它把對符號`f`的引用解析為`__wrap_f`，把對符號`__real_f`的引用解析為`f`。
- 通過`-Wl,option`將選項傳遞給鏈接器，比如`-Wl,--wrap,f`。
- 例子：
```C
// myalloc.c
#ifdef LINKTIME
void* __real_malloc(size_t size);
void __real_free(void* p);
void* __wrap_malloc(size_t size)
{
    // implementation ...
}
void __wrap_free(void* p)
{
    // implementation ...
}
#endif
```
- 編譯：
```shell
gcc -DLINKTIME -c myalloc.c
gcc -c main.c
gcc -Wl,--wrap,malloc -Wl,--wrap,free -o main main.o mymalloc.o
```
- 通過鏈接選項控制是否進行打樁，還定義了宏來控制。

### 運行時打樁

編譯期打樁需要能夠訪問程序源代碼，鏈接時打樁則需要能夠訪問程序的可重定位目標文件。不過，有這樣一種打樁機制，可以在運行時打樁，只需要能夠訪問可執行目標文件：
- 這個機制基於動態鏈接器的`LD_PRELOAD`環境變量。
- 如果`LD_PRELOAD`被設置為一個共享路徑名列表（以空格或者分號分隔），那麼當加載和執行一個程序時，需要解析未定義引用時，動態鏈接器先搜索`PRE_LOAD`庫，然後才搜索其他任何函庫。
- 有了這個機制，當加載執行任意可執行文件時，可以對任何共享庫中的任何函數打樁，包括`libc.so`。
- 例子：
```c
// mymalloc.c
#ifdef RUNTIME
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

// wrapper
void* malloc(size_t size)
{
    void* (*mallocp)(size_t size);
    mallocp = dlsym(RTLD_NEXT, "malloc"); // get malloc in libc.so
    if (!mallocp)
    {
        printf(dlerror());
        exit(1);
    }
    char* ptr = mallocp(size);
    printf("malloc(%d) = %p\n", size, ptr);
    return ptr;
}
void free(void* ptr)
{
    void (*freep)(void*) = NULL;
    if (!ptr)
        return;
    freep = dlsym(RTLD_NEXT, "free"); // get free in libc.so
    if (!freep)
    {
        printf(dlerror());
        exit(1);
    }
    free(ptr);
    printf("free(%p)\n", ptr);
}
#endif
```
```c
// main.c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char const *argv[])
{
    int *p = malloc(32);
    free(p);
    return 0;
}
```
- 編譯運行：
```shell
gcc -DRUNTIME -shared -fpic -o mymalloc.so mymalloc.c -ldl
gcc -o main main.c
LD_PRELOAD="./mymalloc.so" ./main
```

## 7.14 處理目標文件的工具

Linux系統中有大量可用工具幫助理解和處理目標文件，特比是GNU binutils包中：
- `ar`：創建靜態庫，插入、刪除、列出、提取成員。
- `strings`：列出目標文件中所有可打印字符串。
- `strip`：從目標文件中刪除符號表信息。
- `mm`：列出目標文件符號表中定義的符號。
- `size`：列出目標文件中節的名稱和大小。
- `readelf`：顯式一個目標文件的完整結構，包括ELF頭中編碼的所有信息。
    - `-a`：所有。
    - `-h`：ELF頭。
    - `-l`：程序頭/段頭部表。
    - `-S`：節頭部表。
    - `-e`：`-h -l -S`，所有頭。
    - `-s`：符號表。
    - `-r`：重定位表。
    - 更多見幫助。
- `objdump`：顯式一個目標文件中的所有信息，最大作用是反彙編。
    - `-a`：歸檔文件頭信息。
    - `-f`：全面的文件頭信息。
    - `-h`：節頭部表內容。
    - `-x`：所有頭。
    - `-d`：反彙編可執行的節。
    - `-D`：反彙編所有節內容。
    - `-S`：在反彙編時混合插入源碼。
    - `-s`：所有節的的全部內容。
    - `-g`：對象文件中的調試信息。
    - `-t`：符號表內容。
    - `-r`：重定位信息。
- `ldd`：列出一個可執行文件在運行時所需要的共享庫。

## 補充材料

- [程序員的自我修養——鏈接、裝載與庫](https://book.douban.com/subject/3652388/)，可以作為本章的更詳細的補充。
