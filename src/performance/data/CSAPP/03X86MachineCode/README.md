<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [第三章：程序的機器級表示](#%E7%AC%AC%E4%B8%89%E7%AB%A0%E7%A8%8B%E5%BA%8F%E7%9A%84%E6%9C%BA%E5%99%A8%E7%BA%A7%E8%A1%A8%E7%A4%BA)
  - [3.2 程序編碼](#32-%E7%A8%8B%E5%BA%8F%E7%BC%96%E7%A0%81)
  - [3.3 數據格式](#33-%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F)
  - [3.4 訪問信息](#34-%E8%AE%BF%E9%97%AE%E4%BF%A1%E6%81%AF)
    - [操作數](#%E6%93%8D%E4%BD%9C%E6%95%B0)
    - [數據傳送指令](#%E6%95%B0%E6%8D%AE%E4%BC%A0%E9%80%81%E6%8C%87%E4%BB%A4)
    - [壓入彈出棧數據](#%E5%8E%8B%E5%85%A5%E5%BC%B9%E5%87%BA%E6%A0%88%E6%95%B0%E6%8D%AE)
  - [3.5 算術與邏輯操作](#35-%E7%AE%97%E6%9C%AF%E4%B8%8E%E9%80%BB%E8%BE%91%E6%93%8D%E4%BD%9C)
    - [加載有效地址](#%E5%8A%A0%E8%BD%BD%E6%9C%89%E6%95%88%E5%9C%B0%E5%9D%80)
    - [一元與二元操作](#%E4%B8%80%E5%85%83%E4%B8%8E%E4%BA%8C%E5%85%83%E6%93%8D%E4%BD%9C)
    - [移位操作](#%E7%A7%BB%E4%BD%8D%E6%93%8D%E4%BD%9C)
    - [特殊算術操作](#%E7%89%B9%E6%AE%8A%E7%AE%97%E6%9C%AF%E6%93%8D%E4%BD%9C)
  - [3.6 控制流](#36-%E6%8E%A7%E5%88%B6%E6%B5%81)
    - [訪問條件碼](#%E8%AE%BF%E9%97%AE%E6%9D%A1%E4%BB%B6%E7%A0%81)
    - [跳轉指令](#%E8%B7%B3%E8%BD%AC%E6%8C%87%E4%BB%A4)
    - [跳轉指令如何編碼](#%E8%B7%B3%E8%BD%AC%E6%8C%87%E4%BB%A4%E5%A6%82%E4%BD%95%E7%BC%96%E7%A0%81)
    - [用條件跳轉實現條件分支](#%E7%94%A8%E6%9D%A1%E4%BB%B6%E8%B7%B3%E8%BD%AC%E5%AE%9E%E7%8E%B0%E6%9D%A1%E4%BB%B6%E5%88%86%E6%94%AF)
    - [用條件傳送實現條件分支](#%E7%94%A8%E6%9D%A1%E4%BB%B6%E4%BC%A0%E9%80%81%E5%AE%9E%E7%8E%B0%E6%9D%A1%E4%BB%B6%E5%88%86%E6%94%AF)
    - [循環](#%E5%BE%AA%E7%8E%AF)
  - [3.7 過程](#37-%E8%BF%87%E7%A8%8B)
    - [運行時棧](#%E8%BF%90%E8%A1%8C%E6%97%B6%E6%A0%88)
    - [轉移控制](#%E8%BD%AC%E7%A7%BB%E6%8E%A7%E5%88%B6)
    - [數據傳送](#%E6%95%B0%E6%8D%AE%E4%BC%A0%E9%80%81)
    - [棧上局部存儲](#%E6%A0%88%E4%B8%8A%E5%B1%80%E9%83%A8%E5%AD%98%E5%82%A8)
    - [寄存器中的局部存儲](#%E5%AF%84%E5%AD%98%E5%99%A8%E4%B8%AD%E7%9A%84%E5%B1%80%E9%83%A8%E5%AD%98%E5%82%A8)
  - [3.8 數組分配與訪問](#38-%E6%95%B0%E7%BB%84%E5%88%86%E9%85%8D%E4%B8%8E%E8%AE%BF%E9%97%AE)
    - [多維數組](#%E5%A4%9A%E7%BB%B4%E6%95%B0%E7%BB%84)
  - [3.9 異質數據結構](#39-%E5%BC%82%E8%B4%A8%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
    - [結構](#%E7%BB%93%E6%9E%84)
    - [聯合](#%E8%81%94%E5%90%88)
    - [數據對齊](#%E6%95%B0%E6%8D%AE%E5%AF%B9%E9%BD%90)
  - [3.10 在機器程序中將控制和數據結合起來](#310-%E5%9C%A8%E6%9C%BA%E5%99%A8%E7%A8%8B%E5%BA%8F%E4%B8%AD%E5%B0%86%E6%8E%A7%E5%88%B6%E5%92%8C%E6%95%B0%E6%8D%AE%E7%BB%93%E5%90%88%E8%B5%B7%E6%9D%A5)
    - [理解指針](#%E7%90%86%E8%A7%A3%E6%8C%87%E9%92%88)
    - [使用GDB調試](#%E4%BD%BF%E7%94%A8gdb%E8%B0%83%E8%AF%95)
    - [內存越界引用和緩衝區溢出](#%E5%86%85%E5%AD%98%E8%B6%8A%E7%95%8C%E5%BC%95%E7%94%A8%E5%92%8C%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA)
    - [對抗緩衝區溢出攻擊](#%E5%AF%B9%E6%8A%97%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA%E6%94%BB%E5%87%BB)
    - [支持變長棧幀](#%E6%94%AF%E6%8C%81%E5%8F%98%E9%95%BF%E6%A0%88%E5%B8%A7)
  - [3.11 浮點代碼](#311-%E6%B5%AE%E7%82%B9%E4%BB%A3%E7%A0%81)
    - [浮點寄存器](#%E6%B5%AE%E7%82%B9%E5%AF%84%E5%AD%98%E5%99%A8)
    - [浮點傳送與轉換操作](#%E6%B5%AE%E7%82%B9%E4%BC%A0%E9%80%81%E4%B8%8E%E8%BD%AC%E6%8D%A2%E6%93%8D%E4%BD%9C)
    - [過程中的浮點代碼](#%E8%BF%87%E7%A8%8B%E4%B8%AD%E7%9A%84%E6%B5%AE%E7%82%B9%E4%BB%A3%E7%A0%81)
    - [浮點運算](#%E6%B5%AE%E7%82%B9%E8%BF%90%E7%AE%97)
    - [定義和使用浮點數常量](#%E5%AE%9A%E4%B9%89%E5%92%8C%E4%BD%BF%E7%94%A8%E6%B5%AE%E7%82%B9%E6%95%B0%E5%B8%B8%E9%87%8F)
    - [浮點數中的位級操作](#%E6%B5%AE%E7%82%B9%E6%95%B0%E4%B8%AD%E7%9A%84%E4%BD%8D%E7%BA%A7%E6%93%8D%E4%BD%9C)
    - [浮點比較操作](#%E6%B5%AE%E7%82%B9%E6%AF%94%E8%BE%83%E6%93%8D%E4%BD%9C)
  - [總結](#%E6%80%BB%E7%BB%93)
  - [補充：不同環境中編譯生成的彙編對比](#%E8%A1%A5%E5%85%85%E4%B8%8D%E5%90%8C%E7%8E%AF%E5%A2%83%E4%B8%AD%E7%BC%96%E8%AF%91%E7%94%9F%E6%88%90%E7%9A%84%E6%B1%87%E7%BC%96%E5%AF%B9%E6%AF%94)
  - [補充：C語言內聯彙編](#%E8%A1%A5%E5%85%85c%E8%AF%AD%E8%A8%80%E5%86%85%E8%81%94%E6%B1%87%E7%BC%96)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 第三章：程序的機器級表示

配置與環境：
- 環境：x86處理器，64位Linux，gcc編譯器（使用gcc 12.1.0版本），`-Og`選項生成代碼，彙編風格使用默認的AT&T風格。
- 與64位Windows環境產生的彙編可能會存在一些差異：
    - 64位Windows使用LLP64數據模型，`long`長度是32位，64位類Unix系統使用LLP64，`long`長度是64位。
    - 調用約定存在區別。
- 本章所有測試代碼都將寫在`test.c`中。
- 執行`make test.s`進行編譯生成彙編源文件。
- 執行`make test.o`生成目標文件。
- 執行`make test`生成可執行目標文件。
- 執行`objdump -d test.o`對目標文件反彙編。
- 執行`make clean`清理所有生成文件。

## 3.2 程序編碼

代碼示例：
```C
long mult2(long, long);
void multstore(long x, long y, long* dest)
{
    long t = mult2(x, y);
    *dest = t;
}
```
- 使用C語言編譯生成彙編：
```x86asm
encoding_multstore:
.LFB0:
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	movq	%rdx, %rbx
	call	encoding_mult2
	movq	%rax, (%rbx)
	popq	%rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE0:
	.size	encoding_multstore, .-encoding_multstore
	.globl	move_exchange
	.type	move_exchange, @function
```
- 精簡後：
```x86asm
encoding_multstore:
	pushq	%rbx
	movq	%rdx, %rbx
	call	encoding_mult2
	movq	%rax, (%rbx)
	popq	%rbx
	ret
```
- 對目標文件反彙編 `objdump -d test.o` 可以得到一樣的結果：
```
0000000000000000 <encoding_multstore>:
   0:   53                      push   %rbx
   1:   48 89 d3                mov    %rdx,%rbx
   4:   e8 00 00 00 00          callq  9 <encoding_multstore+0x9>
   9:   48 89 03                mov    %rax,(%rbx)
   c:   5b                      pop    %rbx
   d:   c3                      retq   
```
- X86指令是不定長指令，`.`開頭的偽指令都是指導彙編器和鏈接器工作的微指令，不影響彙編代碼的邏輯。
- 反彙編中的指令可能和彙編源文件中存在一些區別，比如指令末尾的`q`，這對指令含義並無影響。

## 3.3 數據格式

不同數據類型，使用同一指令的不同後綴形式，表示操作不同長度的數據：
- 操作字節（byte），後綴 `b`，數據長度1個字節。
- 操作字（word），後綴 `w`，數據長度2個字節。
- 操作雙字（double words），後綴 `l`，數據長度8個字節。
- 操作四字（quad words），後綴 `q`，數據長度8個字節。
- 浮點單精度操作，後綴 `s`，數據長度4字節。
- 浮點雙精度操作，後綴 `l`，數據長度8字節。
- 浮點操作和整數操作是不同指令，不會混淆。
- 例子：`movb movw movl movq`。

## 3.4 訪問信息

16個存儲64位值的通用寄存器：

|64位寄存器|32位寄存器|16位寄存器|8位寄存器|用途
|:-:|:-:|:-:|:-:|:-:|
|%rax|%eax|%ax|%al|返回值
|%rbx|%ebx|%bx|%bl|被調用者保存
|%rcx|%ecx|%cx|%cl|第4個參數
|%rdx|%edx|%dx|%dl|第3個參數
|%rsi|%esi|%si|%sil|第2個參數
|%rdi|%edi|%di|%dil|第1個參數
|%rbp|%ebp|%bp|%bpl|被調用者保存（base pointer）
|%rsp|%esp|%sp|%spl|棧指針（stack pointer）
|%r8 |%r8d |%r8w |%r8b |第5個參數
|%r9 |%r9d |%r9w |%r9b |第6個參數
|%r10|%r10d|%r10w|%r10b|調用者保存
|%r11|%r11d|%r11w|%r11b|調用者保存
|%r12|%r12d|%r12w|%r12b|被調用者保存
|%r13|%r13d|%r13w|%r13b|被調用者保存
|%r14|%r14d|%r14w|%r14b|被調用者保存
|%r15|%r15d|%r15w|%r15b|被調用者保存

- 前8個寄存器繼承自16位處理器時代（8086），那時每個寄存器只有16位，在其後加上 `l` 表示低8位。
- 到32位時代（IA32），這8個寄存器擴展為32位，前面加上 `e` 表示。
- 到了64位時代（x86-64），這8個寄存器擴展為64位，前面加上 `r` 表示。並且新增了8個寄存器，命令為`r8 ~ r16`，訪問低32位、低16位、低8位分別使用後綴`d w b`。
- 在操作寄存器的部分字節與寄存器整體時有兩條規則：
    - 生成1字節和2字節數字的指令會保持剩下的字節不變。
    - 生成4字節數字的指令會將高位4個字節置0。
- 其中比較特殊的`%rsp`，保存棧指針，其他寄存器的用法更為靈活。少量指令會使用特定寄存器。
- 有一組標準的編程規範控制著如何使用寄存器管理棧、傳遞函數參數、從函數返回值、存儲局部和臨時數據。後續會詳述這些慣例。

### 操作數

大多數的指令都有一個或者多個操作數：用於指示操作使用的源數據值或者放置結果的目的位置。操作數有三種類型：
- 立即數：表示這個數本身。使用`$`後跟一個整數，一般是`0x`開頭的十六進制整數，也可以是十進制。
- 寄存器：表示寄存器中的內容，可以是寄存器的低位1、2、4字節或者整體8字節。
- 內存引用：表示一個內存地址處保存的值，根據計算內存地址的方式，有多種尋址模式。

操作數格式：
- 對於寄存器`r`，我們用`R[r]`來表示其中存儲的值。
- 對於內存引用，我們用`M[Addr]`來表示地址`Addr`處存儲的值，至於取幾個字節的值，則由具體指令決定。
- 操作數的允許格式如下：

|類型|格式|操作數的值|名稱|
|:-:|:-:|:-:|:-:
|立即數|`$Imm`|`Imm`|立即數尋址
|寄存器尋址|`r`|`R[r]`|寄存器尋址
|存儲器|`Imm(rb, ri, s)`|`M[Imm + R[rb] + R[ri] * s`|比例變址尋址

- 在內存引用類型的操作數中，`Imm`、`rb`、`ri`和`s`、單獨的`s`可以省略，就有了以下尋址方式：
    - `Imm`，表示`M[Imm]`，絕對尋址。
    - `(rb)`，表示`M[R[rb]]`，間接尋址。
    - `Imm(rb)`，表示`M[Imm + R[rb]]`，基址偏移量尋址。
    - `(rb, ri)`和`Imm(rb, ri)`，變址尋址。
    - `(, ri, s)`和`Imm(, ri, s)`和`(rb, ri, s)`，也是比例變址尋址。
    - 其中如果`s`省略則表示為1。
    - `rb`省略則空出來，後面的逗號也必須要寫。

### 數據傳送指令

我們將許多僅僅是源和目的的操作數類型、大小有不同的同類指令成為**指令類**。

數據傳送指令是將數據從一個位置複製到另一個位置的指令，其中最簡單的一類是MOV類指令。

**MOV類指令**：
- 簡單的數據傳送指令：`MOV S D`，將S數據傳送到D。
- 源操作數可以是立即數、寄存器或者內存中的數，目的操作數只能是內存地址或者寄存器。
- x86-64加了限制，不能兩個操作數都是內存位置。將一個操作數從內存位置複製到另一內存位置需要兩條指令，需要先複製到寄存器。
- `movb movw movl movq`傳送字節、字、雙字、四字。
- `movabsq I R`傳送絕對的四字，從I到R，I只能是64位立即數，R只能是寄存器。
- 前面說過`movl`會將高4字節置0。
- 常規的`movq`只能將表示為32位補碼數字的立即數作為源操作數，然後符號擴展為64位後放到目的位置。

在將較小的源值複製到較大的目的位置時，則需要使用 **MOVZ和MOVS類指令**：
- 他們都從源複製到寄存器：`MOVZ/MOVS S R`。
- `MOVZ`類是零擴展數據傳送指令：`movzbw movzbl movzwl movzbq movzwq`。
- `MOVS`類是符號擴展傳送指令：`movsbw movsbl movswl movsbq movswq movslq cltq`。
- 從雙字到四字則已經有了`movl`零擴展傳送，所以沒有`movzlq`。
- 其中`cltq`是將`%eax`符號擴展後`%rax`，僅用於這一個寄存器。效果與`movslq %eax, %rax`完全一致，不過編碼更緊湊。

區別：
- 對於低位（1字節、2字節）傳送而言，MOV類指令不修改高位，MOVZ類則會零擴展，高位會被修改為0，MOVS會符號擴展。

例子：
```C
long move_exchange(long* xp, long y)
{
    long x = *xp;
    *xp = y;
    return x;
}
```
彙編：
```x86asm
; xp in %rdi, y in %rci, return value in %rax
; long is 8 bytes
move_exchange:
	movq	(%rdi), %rax
	movq	%rsi, (%rdi)
	ret
```
- 其中臨時變量被分配到了寄存器`%rax`中，並同時作為返回值。

### 壓入彈出棧數據

程序棧：
- 棧指針保存在`%rsp`中，指向棧頂首個數據的首地址。
- 棧從高地址向低地址生長。
- `pushq S`壓入數據，等價於：
```x86asm
subq %8, %rsp
movq S, (%rsp)
```
- `popq D`彈出數據，等價於：
```x86asm
movq (%rsp), D
addq $8, %rsp
```

## 3.5 算術與邏輯操作

整數與邏輯操作有很多類：
- 其中只有`leaq`沒有其他大小變種，其他都有`b w l q`四個變種：

|指令|效果|描述
|:-:|:-:|:-:
|`leaq S D`| D = &S|加載有效地址，目標只能是寄存器
|`INC D`| D = D+1|自增
|`DEC D`| D = D-1|自減
|`NEG D`| D = -D|取負
|`NOT D`| D = ~D|取反
|`ADD S, D`|D = D+S|加
|`SUB S, D`|D = D-S|減
|`IMUL S, D`|D = D*S|乘
|`XOR S, D`|D = D^S|異或
|`OR S, D`|D = D\|S|或
|`AND S, D`|D = D&S|與
|`SAL k, D`|D = D << k|左移
|`SHL k, D`|D = D << k|左移(等同於SAL)
|`SAR k, D`|D = D >>(A) k|算術右移
|`SHR k, D`|D = D >>(L) k|邏輯右移

### 加載有效地址

- 目的操作數只能是寄存器。
- 很像MOV類指令，不過直接將源操作數的地址計算之後不去內存中取值，而是直接將值存入寄存器。
- 很多時候會被用來進行算術運算：可以用來執行加法和有限形式的乘法（乘以1,2,4,8）。
```C
long p129_leaq_scale(long x, long y, long z)
{
    // x in %rdi, y in %rsi, z in %rdx
    return x + 4*y + 12*z;
}
```
- 彙編：
```x86asm
p129_leaq_scale:
	leaq	(%rdi,%rsi,4), %rax ; x + 4*y
	leaq	(%rdx,%rdx,2), %rdx ; z + 2*z = 3*z
	leaq	(%rax,%rdx,4), %rax ; x + 4*y + 4*(3*z) = x + 4*y + 12*z
	ret
```

### 一元與二元操作

- 一元操作：只有一個操作數，即是源也是目的。很類似於C語言中的`++ -- - ~`運算符。
- 二元操作：第二個操作數是目的操作數，同時作為其中一個源。很類似於C語言中的複合賦值運算。
    - 第一個操作數可以是立即數、寄存器、內存位置，第二個操作數可以是寄存器或者內存位置。
- AT&T表示中，所有既有源又有目的的指令都是源在前，目的在後。

### 移位操作

- `SAL SHL`含義一致。
- `SAR`是算術右移，填充符號位。
- `SHR`是邏輯右移，填充0。
- 位移量可以是立即數，或者放在單字節寄存器`%cl`中（比較特殊只能是這個寄存器）。
- 目的操作數可以是寄存器或者內存位置。
- 例子：
```C
long p131_exercise_3_9_shift_left4_rightn(long x, long n)
{
    x <<= 4;
    x >>= n;
    return x;
}
```
- 彙編
```x86asm
p131_exercise_3_9_shift_left4_rightn:
	movq	%rdi, %rax ; get x
	salq	$4, %rax   ; x <<= 4
	movl	%esi, %ecx ; get n(in 4 bytes)
	sarq	%cl, %rax  ; x >>= n
	ret
```

### 特殊算術操作

64位有符號數或者無符號數相乘需要128位來保存結果才能保證不會溢出，x86-64對128位整數操作提供了有限支持。
- 128位整數成為8字（oct word）。

|指令|效果|描述
|:-:|:-:|:-:|
|`imulq S`|`R[%rdx] : R[%rax] = S * R[%rax]`|有符號乘法
|`mulq S`|`R[%rdx] : R[%rax] = S * R[%rax]`|無符號乘法
|`cqto`|`R[%rdx] : R[%rax] = signed-extend(R[%rax])`|4字轉換為8字
|`idivq S`|`R[%rdx] = R[%rdx] : R[%rax] mod S`</p>`R[%rax] = R[%rdx] : R[rax] / S`|有符號除法
|`divq S`|`R[%rdx] = R[%rdx] : R[%rax] mod S`</p>`R[%rax] = R[%rdx] : R[rax] / S`|無符號除法

- 前面的雙操作數的`imulq`指令是適用於有符號和無符號乘法，結果是64位。
- 此外，x86-64提供了兩條單操作數，但是結果是128位的整數乘法，其中`imulq`是有符號乘法，`mulq`是無符號乘法，結果被保存到`R[%rdx]:R[%rax]`組合而成的128整數中。
- 這兩條指令要求一個操作數給出，一個操作數位於`%rax`中，結果的低位存在`%rax`中，高位存在`%rdx`中。
- 當用到128位整數相關運算時，會使用到這些指令。標準C語言不提供128位整數類型，不過可以使用GCC擴展中的`__int128`類型，需要去掉`-pedantic-errors`選項以使用非標準的特性。
- 例子：
```C
// Note: GCC extension, non-standard type __int128
typedef unsigned __int128 uint128_t;
// section 3.5.5, P124, 128bit integer arithmetics
void p134_special_arith_inst_mul(uint128_t *dest, uint64_t x, uint64_t y)
{
    *dest = x * (uint128_t)y;
}
```
- 彙編：
```x86asm
p134_special_arith_inst_mul:
	movq	%rsi, %rax      ; save x to %rax
	mulq	%rdx            ; R[%rdx] : R[%rax] = y * R[%rax]
	movq	%rax, (%rdi)    ; save low 64 bits of result
	movq	%rdx, 8(%rdi)   ; save high 64 bits of result, little endian
	ret
```
- 64位整數的除法也是通過`idvq divq`實現的。
    - 如果是有符號數，則需要先通過`cqto`將64位整數符號擴展到128位。
    - 如果是無符號數，則直接零擴展，將高位(`%rdx`)設置為0。
- 有符號數例子：
```C
void P134_special_airth_inst_remdiv(long x, long y, long *qp, long *rp)
{
    long q = x / y;
    long r = x % y;
    *qp = q;
    *rp = r;
}
```
- 彙編：
```x86asm
;  x in %rdi, y in %rsi, qp in %rdx, %rp in %rcx
P134_special_airth_inst_remdiv:
	movq	%rdi, %rax      ; copy x to %rax
	movq	%rdx, %r8       ; copy qp to %r8
	cqto                    ; signed extend %rax(x) to %rdx:%rax
	idivq	%rsi            ; x/y to %rdx, x%y to %rax
	movq	%rax, (%r8)     ; *qp = x/y
	movq	%rdx, (%rcx)    ; *rp = x%y
	ret
```
- 無符號數：
```C
void p124_sepcial_arith_inst_remdiv_unsigned(unsigned long x, unsigned long y,
    unsigned long* qp, unsigned long* rp)
{
    unsigned long q = x / y;
    unsigned long r = x % y;
    *qp = q;
    *rp = r;
}
```
- 彙編：符號擴展改為零擴展，直接清零即可，有符號除法改為無符號除法。
```x86asm
; x in %rdi, y in %rsi, qp in %rdx, %rp in %rcx
p124_sepcial_arith_inst_remdiv_unsigned:
	movq	%rdi, %rax      ; copy x to %rax
	movq	%rdx, %r8       ; copy qp to %r8
	movl	$0, %edx        ; zero extend %rax(x) to %rdx:%rax / just clear %rdx
	divq	%rsi            ; x/y to %rdx, x%y to %rax
	movq	%rax, (%r8)     ; *qp = x/y
	movq	%rdx, (%rcx)    ; *rp = x%y
	ret
```

## 3.6 控制流

標誌寄存器：
- `CF`：進位標誌。
- `ZF`：零標誌。
- `SF`：符號標誌。負數則為1。
- `OF`：溢出標誌，補碼溢出，正溢出或者負溢出。
- 所有除了`leaq`之外的指令都會根據結果改變標誌寄存器。
- 一般來說，一條指令只會設置一部分標誌寄存器，而不是所有。比如位運算就不會設置溢出標誌，因為不會溢出。

比較和測試指令：
- 比較指令`CMP S1, S2`：基於`S2-S1`，僅設置標誌寄存器，行為類似於`SUB`，不過不更新目的寄存器。有`cmpb cmpw cmpl cmpq`不同版本。
- 測試指令`TEST S1, S2`：基於`S1 & S2`，僅設置標誌寄存器，行為類似AND，不過不更新目的寄存器，有`testb testw testl testq`不同版本。

### 訪問條件碼

條件碼的使用：
- 條件寄存器的值通常不會直接讀取，而是使用它們的組合來表示各種不同的含義。
- 三種常用使用條件碼的方法：
    - **根據條件碼的某種組合設置一個字節為0或者1**。
    - **條件跳轉到程序其他部分**。
    - **條件傳送數據**。

條件設置指令：
- 目標必須是一字節寄存器。
- 他們的效果是去上面四個標誌的組合來表示特定的含義，具體的組合則略（比如`setl`是`SF ^ OF`時設置）。

|指令|含義|
|:-:|:-:|
|`sete/setz D`|相等/零
|`setne/setnz D`|不等/非零
|`sets D`|負數
|`setns D`|非負數
|`setg/setnle D`|有符號>
|`setge/setnl D`|有符號>=
|`setl/setnge D`|有符號<
|`setle/setng D`|有符號<=
|`seta/setnbe D`|無符號>
|`setae/setnb D`|無符號>=
|`setb/setnae D`|無符號<
|`setbe/setna D`|無符號<=

- 其中對有符號數使用`less greater`的縮寫，表示大於、小於。
- 對無符號數使用`above below`的縮寫，表示超過、低於。
- 末尾的後綴不表示操作數長度，而是表示具體測試什麼。
- 大多數情況下，機器代碼對於有符號和無符號運算使用相同的指令，編譯器根據源碼中的數據類型選擇是使用無符號還是有符號條件設置指令來得到不用含義的比較結果。
- 某些機器指令有多個名字，稱之為同義名（synonym）。

- 例子：`a < b`。
```C
int p137_control_flow_less(long a, long b)
{
    return a < b;
}
```
- 彙編：
```x86asm
; a in %rdi, b in %rsi
p137_control_flow_less:
	cmpq	%rsi, %rdi ; compare a : b
	setl	%al        ; singed integer less
	movzbl	%al, %eax  ; return
	ret
```
- 有符號整數的情況：
```C
int p127_control_flow_less_unsinged(unsigned long a, unsigned long b)
{
    return a < b;
}
```
- 彙編：
```x86asm
p127_control_flow_less_unsinged:
	cmpq	%rsi, %rdi  ; compare a : b
	setb	%al         ; unsigned interger below
	movzbl	%al, %eax   ; return
	ret
```
- 需要注意的是比較指令的比較順序，`cmpq`中`a`在`b`後面，但是其實是比較`a`和`b`。

### 跳轉指令

不同於順序執行時一條一條指令的執行過程，跳轉指令可以跳轉到一個特定位置開始執行：
- 在彙編中，跳轉的目的地通常用一個標號指明（lebel，形式如`.LABEL`）。
- 在鏈接後這些標號會被替換為這個標號的虛擬地址。

無條件跳轉：
- `jmp D`指令。
- 目標可以是一個標號：`.LABEL`。稱之為直接跳轉。
- 也可以是從寄存器或者內存位置中讀出的地址，稱之為間接跳轉。
- 彙編中，直接跳轉是使用`.`開始的標號，間接跳轉是`*`後跟寄存器或者內存位置。
```x86asm
jmp .L1     ; jump to .L1
jmp *%rax   ; jump to R[%rax]
jmp *(%rax) ; jump to M[R[%rax]]
```

條件跳轉：
- 只能是直接跳轉。
- 與`SET`類指令的設置條件相匹配。

|指令|含義|
|:-:|:-:
|`je/jz Label`|相等/零
|`jne/jnz Label`|不等/非零
|`js Label`|負數
|`jns Label`|非負數
|`jg/jnle Label`|有符號>
|`jge/jnl Label`|有符號>=
|`jl/jnge Label`|有符號<
|`jle/jng Label`|有符號<=
|`ja/jnbe Label`|無符號>
|`jae/jnb Label`|無符號>=
|`jb/jnae Label`|無符號<
|`jbe/jna Label`|無符號<=

### 跳轉指令如何編碼

跳轉指令的編碼：
- 前面的指令的二進制編碼對非編譯期作者來說並不重要，他們幾乎是和彙編一一對應的關係。
- 但是跳轉指令則比較特別，跳轉指令中的間接跳轉也具有確定的編碼，但是直接跳轉是跳轉到標號，而標號在最終的機器碼中是不存在的。
- 所以如何表示標號就很重要：
    - 標號有幾種不同的編碼，其中最常用的是**PC相對編碼**。也就是將標號的地址與緊跟在跳轉指令後的那條指令地址（這是一種慣例，不是基於當前指令地址）之間的差（也就是偏移量）作為編碼。這些地址偏移量可以編碼為1、2、4個字節，可正可負。只需要在彙編時確定偏移量，鏈接時不需要進行修改。
    - 第二種編碼是給出絕對地址，由四個字節直接指令目標。有彙編器和鏈接器選擇適當的跳轉目標。

例子：
```C++
int p141_encoding_of_jump_inst(int a)
{
    if (a > 0)
    {
        return a + 1;
    }
    return a - 1;
}

```
- 彙編：
```x86asm
p141_encoding_of_jump_inst:
	testl	%edi, %edi
	jg	.L16
	leal	-1(%rdi), %eax
	ret
.L16:
	leal	1(%rdi), %eax
	ret
```

- 目標文件反彙編：
```x86asm
0000000000000093 <p141_encoding_of_jump_inst>:
  93:   85 ff                   test   %edi,%edi
  95:   7f 04                   jg     9b <p141_encoding_of_jump_inst+0x8>
  97:   8d 47 ff                lea    -0x1(%rdi),%eax
  9a:   c3                      retq   
  9b:   8d 47 01                lea    0x1(%rdi),%eax
  9e:   c3                      retq 
```
- 反彙編中，跳轉地址使用一個字節`04`的PC相對編碼，也就是下一條指令其實地址`97`後移動四個字節，即`9b`。
- 偏移量可正可負，使用補碼錶示。
- 需要注意當`ret`語句作為跳轉語句的目標時，處理器不能正確預測`ret`指令的目的，所以需要在前面加一條`rep`指令，看起來就像這樣`rep; ret`，在反彙編中看起來可能像`retz retq`，他們是同義的。這裡的`rep`類似於一個佔位用的空指令，可以忽略。

### 用條件跳轉實現條件分支

條件分支可以用條件跳轉要可以用條件傳送指令實現，通常的方法是條件跳轉：
- 例子：
```C
long lt_cnt = 0;
long ge_cnt = 0;
long p142_absdiff_se(long x, long y)
{
    long result;
    if (x < y)
    {
        lt_cnt ++;
        result = y - x;
    }
    else
    {
        ge_cnt ++;
        result = x - y;
    }
    return result;
}
```
- 彙編：
```x86asm
p142_absdiff_se:
.LFB27:
	cmpq	%rsi, %rdi          ; compare x : y
	jge	.L18                    ; x >= y --> to .L18
	addq	$1, lt_cnt(%rip)    ; lt_cnt ++
	movq	%rsi, %rax
	subq	%rdi, %rax          ; result = y - x
	ret                         ; return result
.L18:
	addq	$1, ge_cnt(%rip)    ; ge_cnt ++
	movq	%rdi, %rax
	subq	%rsi, %rax          ; result = x - y
	ret                         ; return result
```
- 彙編代碼幾乎可以等價翻譯為同樣結構的`goto`風格代碼：
```C
long p142_gotodiff_se(long x, long y)
{
    long result;
    if (x >= y)
    {
        goto x_ge_y;
    }
    lt_cnt++;
    result = y - x;
    return result;
x_ge_y:
    ge_cnt++;
    result = x - y;
    return result;
}
```
- 其彙編：
```x86asm
p142_gotodiff_se:
	cmpq	%rsi, %rdi
	jge	.L23
	addq	$1, lt_cnt(%rip)
	movq	%rsi, %rax
	subq	%rdi, %rax
	ret
.L23:
	addq	$1, ge_cnt(%rip)
	movq	%rdi, %rax
	subq	%rsi, %rax
	ret
```

對於通用的`if-else`語句：
```
if (test-expr)
    then-statement
else
    else-statement
```
- 可以將其等價翻譯為：
```
    t = test-expr;
    if (!t)
    {
        goto false;
    }
    then-statement
    goto done;
false:
    else-statement
done:
```
- 然後將這種C語言結構翻譯為相同結構的彙編。當然也可以是條件成立跳轉，可以有另一種等等價結構。

### 用條件傳送實現條件分支

使用條件跳轉可以實現任何種類的分支指令，但是某些特定情況下，可以使用條件傳送指令（conditional move）來代替條件跳轉以獲得更高的性能。

例子：
```C
long p145_absdiff(long x, long y)
{
    long result;
    if (x < y)
    {
        result = y - x;
    }
    else
    {
        result = x - y;
    }
    return result;
}
```
- 彙編（在`-Og`選項編譯時不會使用條件選擇指令）：
```x86asm
p145_absdiff:
	cmpq	%rsi, %rdi
	jge	.L25
	movq	%rsi, %rax
	subq	%rdi, %rax
	ret
.L25:
	movq	%rdi, %rax
	subq	%rsi, %rax
	ret
```
- 在開啟`-O2`優化時的彙編：
```x86asm
p145_absdiff:
	movq	%rsi, %rdx  ; y
	movq	%rdi, %rax  ; x
	subq	%rdi, %rdx  ; y - x in %rdx
	subq	%rsi, %rax  ; x - y in %rax
	cmpq	%rsi, %rdi  ; compare x : y
	cmovl	%rdx, %rax  ; if x < y, move %rdx(y-x) to %rax
	ret                 ; return
```
- 其中的`cmovl`指令在`%rdi > %rsi`時才會將`%rdx`的內容傳送`%rax`，否則什麼事情也不做。

條件傳送指令：

|指令|含義|
|:-:|:-:
|`cmove/cmovz S,R`|相等/零
|`cmovne/cmovnz S,R`|不等/非零
|`cmovs S,R`|負數
|`cmovns S,R`|非負數
|`cmovg/cmovnle S,R`|有符號>
|`cmovge/cmovnl S,R`|有符號>=
|`cmovl/cmovnge S,R`|有符號<
|`cmovle/cmovng S,R`|有符號<=
|`cmova/cmovnbe S,R`|無符號>
|`cmovae/cmovnb S,R`|無符號>=
|`cmovb/cmovnae S,R`|無符號<
|`cmovbe/cmovna S,R`|無符號<=

- 條件傳送指令目的地只能是寄存器，可以是16位、32位、64位，彙編器會從目標寄存器名字推斷出條件傳送的操作數長度。對所有長度都可以使用同一個指令名。
- 通常編譯器編譯時生成的指令在條件傳送前都要對條件進行測試。但是條件傳送指令併不併不依賴於前面的測試指令才能工作。條件傳送指令僅僅是讀取值，然後檢查條件碼，然後要麼更新目的寄存器，要麼保持不變。

條件傳送指令為什麼性能更好：
- 因為現代處理器都通過流水線（pipeline）做到指令級並行，來獲得高性能。
- 現代處理器都配備有精密的分支預測邏輯來猜測哪個分支更可能執行，然後在測試指令執行結束前，就已經將該分支的邏輯加載進流水線。如果預測成功則會不受影響地繼續執行，如果預測失敗則需要丟掉所有已經加載到流水線中的後續指令。從其他分支重新加載指令。
- 預測失敗通常會導致15到30個時鐘週期的浪費，導致程序性能下降。
- 雖然現代處理器的分支預測有高的準確率了（如果條件非常可預測，幾乎所有情況都是某個分支，那麼可能能夠達到90%以上，如果條件本身不可預測，那麼可能就五五開），但是並不是100%。
- 而條件傳送指令的使用能夠直接消除掉分支，消除分支預測失敗的可能性，達到性能最大化。

使用條件傳送指令實現分支：
- 考慮條件表達式：`v = test-expr ? then-expr : else-expr`。
- 用條件控制實現：
```C
    if (!test-expr)
        goto false;
    v = then-expr;
    goto done;
false:
    v = else-expr;
done:
```
- 如果使用條件傳送實現：
```C
v = then-expr;
ve = else-expr;
t = test-expr;
if (!t) v = ve;
```
- 不是所有條件表達式都可以用條件傳送編譯的，因為我們可以看到條件傳送實現時對兩個表達式都進行了求值，但是C語言中條件表達式的語義是隻有一個表達式會被求值。
- 如果這兩個表達式存在副作用，那麼行為就變了，所以只能在內置類型這種編譯器能夠確定無副作用的情況下才能使用。
- 比如`p ? *p : 0`這種表達式就是有副作用的，就必須用條件跳轉來編譯。
- 使用條件傳送也並不一定都能有性能提升，如果多出來的整個表達式計算代價非常大，超過了分支預測失敗的性能懲罰，那麼最好還是使用條件轉移。
- 總體來說，條件傳送提供了一種非常受限的情況下的分支優化手段。

### 循環

首先**do-while循環**：
```C
do
    body-statement;
while(test-expr);
```
- 可以等價為：
```C
loop:
    body-statement;
    t = test-expr;
    if (t)
        goto loop;
```
- 例子：
```C
long p150_factorial_dowhile(long n)
{
    long result = 1;
    do
    {
        result *= n;
        n = n-1;
    } while (n > 1);
    return result;
}
```
- 彙編：
```x86asm
p150_factorial_dowhile:
	movl	$1, %eax    ; result = 1
.L30:                   ; loop:
	imulq	%rdi, %rax  ; result *= n
	subq	$1, %rdi    ; n--
	cmpq	$1, %rdi    ; compare n : 1
	jg	.L30
	ret
```

如何逆向彙編代碼：
- 關鍵是找到程序值和寄存器之間的映射關係。
- 對於複雜的任務，編譯器會嘗試合併多個操作、對計算進行重組和變形、試圖將多個變量映射到一個寄存器上，這都會給逆向工作帶來難度。

**while循環**：
- 對於：
```C
while (test-expr)
    body-statement;
```
- 第一種編譯策略可以是：
```C
    goto test;
loop:
    body-statement;
test:
    t = test-expr;
    if (t)
        goto loop;
```
- 第二種翻譯策略：最開始做一次測試，如果不成立直接結束，然後就是一個do-while模式。這種策略成為`guarded-do`。
```C
t = test-expr
if (!t)
    goto done;
loop:
    body-statement;
    t = test-expr;
    if (t)
        goto loop;
done:
```
- 例子：
```C
long p154_factorial_while(long n)
{
    long result = 1;
    while (n > 1)
    {
        result *= n;
        n--;
    }
    return result;
}
```
- `-Og`選項生成彙編，使用第一種翻譯策略：
```x86asm
p154_factorial_while:
	movl	$1, %eax    ; result = 1
	jmp	.L32            ; goto test
.L33:                   ; loop:
	imulq	%rdi, %rax  ; result *= n
	subq	$1, %rdi    ; n--
.L32:                   ; test:
	cmpq	$1, %rdi    ; compare n : 1
	jg	.L33            ; if n > 1, goto loop:
	ret
```
- `-O2`生成彙編，使用第二種翻譯策略：
```x86asm
p154_factorial_while:
	movl	$1, %eax    ; result = 1
	cmpq	$1, %rdi    ; compare n : 1
	jle	.L35            ; if n <= 1, goto done
.L34:                   ; loop:
	imulq	%rdi, %rax  ; result *= n
	subq	$1, %rdi    ; n--
	cmpq	$1, %rdi    ; compare n : 1
	jne	.L34            ; if n != 1, goto loop
	ret                 ; return result
.L35:                   ; done:
	ret                 ; return result
```

- 可以看到當優化等級較高時，編譯器會選擇第二種。利用第二種策略，編譯器可以優化初始時的測試，比如認為測試條件總是滿足。
- 注意彙編中不一定與C源代碼一一對應，某些地方可能是等價的，但是並不一一對應，比如`-O2`優化時有兩個`ret`，但是源碼中只有一次`return`。

**for循環**：
- 通用形式：
```C
for (init-expr; test-expr; update-expr)
    body-statement;
```
- 等價的`while`循環：
```C
init-expr;
while (test-expr)
{
    body-statement;
    update-expr;
}
```
- 對應的第一種翻譯策略：
```C
    init-expr;
    goto test:
loop:
    body-statement;
    update-expr;
test:
    t = test-expr;
    if (t)
        goto loop;
```
- 第二種翻譯策略：
```C
    init-expr;
    t = test-expr;
    if (!t)
        goto done;
loop:
    body-statement;
    update-expr;
    if (t)
        goto loop;
done:
```
- 例子：
```C
long p157_factorial_for(long n)
{
    long i;
    long result = 1;
    for (i = 2; i <= n; i++)
    {
        result *= n;
    }
    return result;
}
```
- 第一種翻譯策略，`-Og`：
```x86asm
p157_factorial_for:
	movl	$1, %edx    ; result = 1
	movl	$2, %eax    ; i = 2
	jmp	.L35            ; goto test
.L36:                   ; loop:
	imulq	%rdi, %rdx  ; result *= n
	addq	$1, %rax    ; i++
.L35:                   ; test:
	cmpq	%rdi, %rax  ; compare i : n
	jle	.L36            ; if i <= n, goto loop:
	movq	%rdx, %rax
	ret                 ; return result
```
- 第二種翻譯策略，`-O2`（某些轉換確實令人迷惑）：
```x86asm
p157_factorial_for:
	cmpq	$1, %rdi        ; compare n : 1
	jle	.L40                ; if n <= 1, goto done
	leaq	1(%rdi), %rcx   ; tmp = n + 1
	movl	$1, %edx        ; result = 1
	movl	$2, %eax        ; i = 2
.L39:                       ; loop:
	addq	$1, %rax        ; i++
	imulq	%rdi, %rdx      ; result *= n
	cmpq	%rcx, %rax      ; compare i : tmp(n+1)
	jne	.L39                ; if i != tmp(n+1), goto loop
	movq	%rdx, %rax
	ret                     ; return result
.L40:                       ; done:
	movl	$1, %edx
	movq	%rdx, %rax      ; result = 1
	ret                     ; return result
```

**switch語句**：
- `switch`的翻譯可以使用跳轉表優化，當開關索引值較多且比較接近時，就可能被翻譯為跳轉表（jump table）。跳轉表的執行速度與開關項的多少無關。
- 跳錶的實現原理就是將多個跳轉地址存在一個數組中，通過其開關值經過一種統一的處理後得到數組索引，從而取出地址。
- 跳轉表存在程序的只讀數據區域（`.rodata`，Read-Only Data）。
- 例子：
```C
void p160_switch_example(long x, long n, long* dest)
{
    long val = x;
    switch (n)
    {
    case 100:
        val *= 13;
        break;
    case 101:
        val += 10;
        // fall through
    case 102:
        val += 11;
        break;
    case 103:
    case 104:
        val *= val;
        break;
    default:
        val = 0;
    }
    *dest = val;
}
```
- `-Og`彙編，沒有使用跳錶優化：
```x86asm
p160_switch_example:
	cmpq	$102, %rsi
	je	.L38
	cmpq	$103, %rsi
	je	.L39
	cmpq	$100, %rsi
	je	.L42
	movl	$0, %edi
.L40:
	movq	%rdi, (%rdx)
	ret
.L42:
	leaq	(%rdi,%rdi,2), %rax
	leaq	(%rdi,%rax,4), %rdi
	jmp	.L40
.L38:
	addq	$10, %rdi
.L39:
	addq	$11, %rdi
	jmp	.L40
```
- 很遺憾，在這個版本，我嘗試了`-O1 -O2 -O3 -Os`都沒有優化成跳錶。
- 但總體來說，優化的原理就是在只讀區域創建一個保存標號對應地址的數組，然後在跳轉時通過索引找到數組項後使用間接跳轉。
- 最終只讀數據區域的彙編會像是這樣（其中不存在`case`標籤的會保存默認標籤的標號）：
```x86asm
.Lxxx
    .quad .L30
    .quad .LDef
    .quad .L32
    .quad .L33
    ...
```
- 然後`switch`語句的選擇會像是這樣：`jmp *.Lxxx(, %rsi, 8)`，其中`%rsi`中保存計算好的下標。
- 每一個`break`語句會生成一個`jmp .Label`的語句跳轉到`switch`邏輯外。

## 3.7 過程

也就是函數，所有指令級都在機器指令級對過程提供支持：
- 為了支持過程，需要提供下列機制：
    - 傳遞控制：進入過程和從過程返回時恰當的PC修改。
    - 傳遞數據：向過程傳遞一個或者多個參數，從過程返回值。
    - 分配和釋放內存：為過程內的局部變量分配空間，返回前釋放這些空間。
- 如何傳遞數據和分配釋放內存作為函數調用約定的一部分，在不同平臺不同編譯器間存在區別。
- x86-64的過程實現包括一組特殊的指令和一些對機器資源（寄存器和棧內存）使用的約定規則。

### 運行時棧

棧是一個LIFO的數據結構，每個進程擁有一個獨立的棧：
- 通過`pushq popq`向棧中存入數據、彈出數據。
- 當x86-64過程需要的存儲空間超過寄存器能夠存放的大小時，就會在棧上分配空間，這部分被稱為過程的棧幀（stack frame）。
- 當過程P調用Q時棧中有什麼東西：
```
[高地址]
P的數據
...
返回地址
保存的寄存器
局部變量
參數構造區  <--- %rsp
[低地址]
```
- 返回地址算作P的棧幀，然後直到棧頂都算Q的棧幀。
- 通過寄存器可以最多傳遞6個參數（`%rdi %rsi %rdx %rsx %r8 %r9`），但是其他的參數需要通過棧來傳遞。

### 轉移控制

控制轉義指令：

|指令|功能|
|:-:|:-:|
|`call label`|過程調用
|`call *Operand`|過程調用
|`ret`|從過程返回

- `callq retq`在x86-64中是他們的同義詞。
- 其中`call`負責將`call`指令的下一條指令的地址（也就是返回地址）壓入棧中，然後將PC設置為過程的地址。和跳轉一樣，調用也可以是直接或者間接的。
- `ret`負責從棧中彈出返回地址，並把PC設置為這個返回地址。

### 數據傳送

除了轉移控制之外，過程調用時還需要進行數據的傳遞：
- 即參數的傳遞，和從過程返回一個值。
- x86-64中，大部分過程間的數據傳送是通過寄存器實現的。
- 前六個參數的默認寄存器是：`%rdi %rsi %rdx %rcx %r8 %r9`，剩下的在棧中傳遞。
- 例子：
```C++
void p169_passing_parameter(long a1, long *a1p,
                            int a2, int *a2p,
                            short a3, short *a3p,
                            char a4, char * a4p)
{
    // a1 in %rdi, a1p in %rsi
    // a2 in %edx, a2p in %rcx
    // a3 in %r8w, a3p in %r9
    // a4 in (%rsp+8), a4p in (%rsp+16)
    *a1p += a1;
    *a2p += a2;
    *a3p += a3;
    *a4p += a4;
}
```
- 彙編：
```x86asm
p169_passing_parameter:
	movq	16(%rsp), %rax      ; a4p to %rax
	addq	%rdi, (%rsi)        ; *a1p += a1
	addl	%edx, (%rcx)        ; *a2p += a2
	addw	%r8w, (%r9)         ; *a3p += a3
	movl	8(%rsp), %edx       ; a4 to %edx
	addb	%dl, (%rax)         ; *a4p += a4
	ret
```
- 調用方：
```C
void p169_passing_parameter_caller()
{
    long a = 1;
    int b = 2;
    short c = 3;
    char d = 4;
    p169_passing_parameter(1, &a, 2, &b, 3, &c, 4, &d);
    a++;
}
```
- 彙編：
```x86asm
p169_passing_parameter_caller:
	subq	$16, %rsp           ; local storage allocation
	movq	$1, 8(%rsp)         ; a
	movl	$2, 4(%rsp)         ; b
	movw	$3, 2(%rsp)         ; c
	movb	$4, 1(%rsp)         ; d
	leaq	1(%rsp), %rax       ; &d
	pushq	%rax                ; push &d to stack
	pushq	$4                  ; push 4 to stack
	leaq	18(%rsp), %r9       ; &c
	movl	$3, %r8d            ; 3
	leaq	20(%rsp), %rcx      ; &b
	movl	$2, %edx            ; 2
	leaq	24(%rsp), %rsi      ; &a
	movl	$1, %edi            ; a
	call	p169_passing_parameter
	addq	$32, %rsp           ; release allocation of parameters(16 bytes) and local storage(16 bytes)
	ret
```
- 從上面例子可以看出：調用方在調用前需要先傳參，如果參數超過6個則從後往前壓倒棧中，前6個參數則存放到寄存器，然後才開始調用。執行完成後棧中的參數被釋放（通過移動棧指針`addq %32, %rsp`），這裡的釋放是連同棧中的局部變量存儲一起釋放的。
- 局部作用域聲明變量也是在棧中分配的。
- 通過棧傳遞參數時，所有的參數大小都向8對齊，即使參數長度小於8。多出來的部分是填充，不會被使用。

### 棧上局部存儲

這從上面的例子已經可以看出來了，局部變量會在棧上分配，也會進行字節對齊：
- 不是所有時候局部變量都會在棧上分配，會在棧上分配的常見情況包括：
    - 寄存器不足夠存放所有局部變量。
    - 對一個局部變量進行了取地址運算，因此必須要能夠產生一個地址（寄存器沒有地址）。
    - 局部變量是數據或者結構，此時不能在寄存器中分配。後續討論這個問題。
- 通過減少棧指針來分配空間，分配的結果將作為當前過程的棧幀的一部分。
- 例子：
```C
long p171_swap_add(long *xp, long *yp)
{
    long x = *xp;
    long y = *yp;
    *xp = y;
    *yp = x;
    return x + y;
}
long p171_caller()
{
    long arg1 = 534;
    long arg2 = 1057;
    long sum = p171_swap_add(&arg1, &arg2);
    long diff = arg1 - arg2;
    return sum * diff;
}
```
- 彙編：
```x86asm
p171_swap_add:
	movq	(%rdi), %rax    ; x in %rax
	movq	(%rsi), %rdx    ; y in %rdx
	movq	%rdx, (%rdi)
	movq	%rax, (%rsi)
	addq	%rdx, %rax
	ret
p171_caller:
	subq	$16, %rsp       ; local storage for arg1 and arg2
	movq	$534, 8(%rsp)   ; arg1 = 534
	movq	$1057, (%rsp)   ; arg2 = 1057
	movq	%rsp, %rsi      ; &arg2
	leaq	8(%rsp), %rdi   ; &arg1
	call	p171_swap_add
	movq	8(%rsp), %rdx
	subq	(%rsp), %rdx    ; diff = arg1 - arg2
	imulq	%rdx, %rax      ; sum * diff
	addq	$16, %rsp       ; release local storage
	ret
```
- 棧上的多個變量相互之間的順序可能會被重排以提高空間利用率，但初始化順序不會變。

### 寄存器中的局部存儲

寄存器組是所有過程共享的資源，給定時刻只有一個過程是活動的，但我們仍然需要取保當一個過程調用另一個過程時，被調不會覆蓋主調正在使用的寄存器值：
- 為此，x86-64採用一組統一的寄存器使用慣例：
    - `%rbx %rbp`和`%r12 ~ %r15`劃分為**被調用者保存寄存器**（callee-saved registers）。
    - 也就是說當過程P調用過程Q時，被調Q必須保證他們的值在調用時和返回時是一樣的。
    - 如果被調要使用這些寄存器，那麼需要將他們先壓棧，並在返回前將其原樣彈出。
    - 所有其他寄存器，除了棧指針`%rsp`，都分類為**調用者保存寄存器**（caller-saved registers）。
    - 也就是說如果使用了這些寄存器，那麼他們需要由調用者在調用其他函數前保存，調用任何函數都有可能修改這些寄存器中的值。被調會假定這些寄存器都已經被妥善保存，可以向其寫入數據覆蓋。
- 例子：
```C
long p173_Q(long x)
{
    return x;
}
long p173_P(long x, long y)
{
    long u = p173_Q(y);
    long v = p173_Q(x);
    return u + v;
}
```
- 彙編：
```x86asm
p173_P:
	pushq	%rbp        ; save %rbp
	pushq	%rbx        ; save %rbx
	movq	%rdi, %rbp  ; save x
	movq	%rsi, %rdi  ; move y to first argument
	call	p173_Q
	movq	%rax, %rbx  ; save result
	movq	%rbp, %rdi  ; move x to first argument
	call	p173_Q
	addq	%rbx, %rax  ; add saved Q(y) to Q(x)
	popq	%rbx        ; restore %rbx
	popq	%rbp        ; restore %rbp
	ret
```
- 函數中用到了被調用者保存寄存器`%rbx %rbp`，所以需要由調用者保存和恢復。
- 而如果要用進行函數，但用於傳參的寄存器卻被佔用，也需要先保存到其他寄存器。
- 例子2：
```C
void p174_inner();
long p174_outter(long a, long b, long c, long d, long e, long f)
{
    p174_inner(1, 2);
    return a + b + c + d + e + f;
}
```
- 彙編：
```x86asm
p174_outter:
	pushq	%r13        ; save registers
	pushq	%r12
	pushq	%rbp
	pushq	%rbx
	subq	$8, %rsp
	movq	%rdi, %rbx  ; save parameters a, b, c, d
	movq	%rsi, %r13
	movq	%rdx, %r12
	movq	%rcx, %rbp
	movl	$2, %esi
	movl	$1, %edi
	movl	$0, %eax
	call	p174_inner
	leaq	(%rbx,%r13), %rax
	addq	%r12, %rax
	addq	%rbp, %rax
	addq	$8, %rsp
	popq	%rbx
	popq	%rbp
	popq	%r12
	popq	%r13
	ret
```
- 從上面的例子看出，6個保存參數的寄存器同樣是調用者保存寄存器，如果函數中調用了函數，那麼這個函數就可能發生任何事，必須假定函數中會修改所有調用者保存寄存器。這些調用者保存寄存器就必須在調用前得到妥善保存。
- 而為了保存這些調用者保存寄存器，最好的方式就是將其保存到被調用者保存寄存器中。而保存到被調用者保存寄存器中前，當前函數同樣作為被調，所以需要先將被調用者保存寄存器先妥善保存，然後將調用者保存寄存器保存到這些被調用者保存寄存器中。
- 參數寄存器保存後，在函數調用完成後是沒有必要將其還原到原來的參數寄存器中的，無論在那個寄存器中，都可以參與運算。
- 如果某個參數在函數調用後沒有被使用，那麼就可以不用保存（`p174_outter`的`e f`參數）。

總結：
- 一個函數調用另一個函數前，需要保存所有在函數調用後還會使用到的調用者保存寄存器（包括參數寄存器）。通常方式是將這些寄存器保存到被調用者保存寄存器中（但不一定都能存下，也可能保存到棧中），在函數調用返回後一般不需要恢復，值直接被移動了。
- 一個函數中如果用到了被調用者保存寄存器，那麼進入函數後需要先將其保存，從函數返回前需要將其恢復。保存方式通常來說都是壓入棧中。
- 調用者保存寄存器`%rax %rcx %rdx %rsi %rdi %r8 %r9 %r10 %r11`，共9個。

## 3.8 數組分配與訪問

- 對於數組：`T A[N]`。
- x86-64的內存引用指令可以用來簡化數組訪問，伸縮引子1、2、4、8覆蓋了所有簡單數據類型的大小：
- 訪問元素`A[i]`可以使用`movq (A, i, sizeof(T)), target`實現。
- 取元素`A[i]`地址則可以用`leaq (A, i, sizeof(T)), target`實現。

### 多維數組

對於數組：`T D[R][C]`。
- 元素`D[i][j]`的地址是`D + sizeof(T)*(C * i + j)`。
- 通過計算這個式子即可得到元素地址。


## 3.9 異質數據結構

C語言支持兩種將不同類型對象組合到一起的方法：結構（struct）和聯合（union）。

### 結構

結構通過結構首地址，也就是第一個成員地址，加上該字段偏移即可得到成員地址，然後正常手法取值即可。
- 例子：
```C
struct rec
{
    int i;      // offset 0
    int j;      // offset 4
    int a[2];   // offset 8
    int *p;     // offset 16
};
void p185_test_struct(struct rec* r)
{
    r->p = &r->a[r->i + r->j];
}
```
- 彙編：
```x86asm
; r in %rdi
p185_test_struct:
	movl	4(%rdi), %eax           ; r->j
	addl	(%rdi), %eax            ; r->i + r->j
	cltq                            ; signed extend %eax to 8 bytes(%rax)
	leaq	8(%rdi,%rax,4), %rax    ; &r->a[r->i + r->j]
	movq	%rax, 16(%rdi)          ; save to r->p
	ret
```

### 聯合

聯合使用不同字段引用相同內存塊，所有字段的地址都等於首地址：
- 聯合在某些地方會很有用，它繞過了類型系統的檢查。
- 但大多數時候使用聯合都不是一個好選擇。

### 數據對齊

大多數計算機系統都對基本數據類型的合法地址做了限制，要求必須是類型的整數倍：
- 這給硬件接口的實現帶來了好處。
- x86-64無論是否對齊都能工作，但還是推薦對齊，對齊數據可以獲得更高的性能。
- 對齊原則就是任何基本數據類型地址都必須是其大小的整數倍。
- 對於包含結構的代碼，或者多個不同大小數據放一起（比如放在棧中的局部多個局部變量），編譯器會在其中加入必要的填充（padding）以保證每個數據的對齊。通過少量的空間損失獲得更好的性能。
- 彙編指令`.align 8`可以指定對齊要求。
- MSVC編譯器中允許使用`#pragma pack()`指定對齊大小。
- C11開始可以使用關鍵字`_Alignas`顯示指定對齊大小，C++中有`alignas`關鍵字。
- x86-64的某些超標量指令擴展（比如AVX、SSE）對對齊有強制要求，需要對齊才能正確計算。
- 結構的對齊規則是每個成員都按照其對齊大小對齊，並且結構大小能夠整除最大的成員對齊大小，結構的對齊大小就是最大的成員對齊大小。

## 3.10 在機器程序中將控制和數據結合起來

### 理解指針

就是地址，不用過多介紹。

### 使用GDB調試

使用`-g`編譯，`gdb prog`開始調試。略，現在我們都使用圖形化調試工具。

### 內存越界引用和緩衝區溢出

例子：
```C
void p195_do_something(char* buf);
void p195_buffer_overflow()
{
    char buf[8];
    p195_do_something(buf);
}
```
- 彙編：
```x86asm
p195_buffer_overflow:
	subq	$24, %rsp           ; allocate memory
	leaq	8(%rsp), %rdi       ; buf is at 8%(rsp)
	call	p195_do_something
	addq	$24, %rsp           ; release
	ret
```
- C語言中並沒有內建的數組下標越界檢查，所有檢查都需要程序員來做。
- 如果數組在棧上分配，比如上面的例子，那麼越界寫入就會導致棧破壞，輕則程序宕掉，重則數據破壞。
- 這一點還可能被黑客利用，將惡意代碼編碼為字符串，覆蓋掉函數返回地址，函數返回時就會跳轉到攻擊者想要執行的位置。然後攻擊者執行完指令後再返回到原來的調用者，看起來無事發生，其實已經受到了攻擊。
- 任何外部接口都應該避免可能的緩衝區溢出攻擊。

### 對抗緩衝區溢出攻擊

有一些手段可以避免通過緩衝區溢出的攻擊：

棧隨機化：
- 為了避免攻擊者製作出對多臺機器都有效的病毒。可以將棧隨機化，而不是所有機器的棧都擁有相同的地址。
- 棧隨機化的思想是使棧的位置在程序每次運行期間都有變化。讓攻擊者找不到真正的棧在什麼位置，需要在什麼位置進行攻擊。
- 典型實現手段可以是在棧上分配一個隨機數量的空間，但不使用這個空間，而是跳過。
- Linux系統中，棧隨機化已經是標準行為。
- 但執著的攻擊者可能會使用暴力克服隨機化，即反覆對不同的地址進行嘗試攻擊。

棧破壞檢測：
- 可以通過在任何局部緩衝區和其他數據之間存儲一個特殊的金絲雀（canary）值作為哨兵，在函數調用返回前進行檢查，如果這個值被更改，說明緩衝區溢出了。
- 這個值是程序每個運行時隨機產生的，攻擊者無法獲取。
- GCC`-fstack-protector`選項即可插入棧保護代碼，上面的`p195_buffer_overflow`加入棧保護後的結果：
```x86asm
p195_buffer_overflow:
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$16, %rsp
	movq	%fs:40, %rax        ; read a value from memory
	movq	%rax, -8(%rbp)      ; and store it to stack
	xorl	%eax, %eax
	leaq	-16(%rbp), %rax
	movq	%rax, %rdi
	call	p195_do_something
	nop
	movq	-8(%rbp), %rax
	subq	%fs:40, %rax
	je	.L69
	call	__stack_chk_fail    ; check the value stored in stack
.L69:
	leave
	ret
```

限制可執行代碼區域：
- 通過限制哪些內存區域才能夠存放可執行代碼，可以消除攻擊者向系統中插入可執行代碼的能力。
- 比如內存分頁的標誌（讀、寫、執行等）。
- 通過同時使用多種方式，可以顯著降低被攻擊的可能。
- 更好的方式還是在所有對外接口中對可寫入緩衝區的數據大小做限制。

### 支持變長棧幀

C99引入變長數組VLA，數組長度需要在執行時才能知道，此時就需要有支持變長棧幀的能力：
- 前面的棧內存分配都是固定大小，大小都是硬編碼到機器碼中作為立即數的。
- 為了支持變長棧幀，就需要將大小存到一個寄存器中，分配時通過訪問寄存器值來確定棧指針偏移多少，釋放時也是同樣。

## 3.11 浮點代碼

處理器的浮點體系結構包含多個方面：
- 如果存儲和訪問浮點數，通常是通過某種寄存器。
- 浮點數據操作指令。
- 向函數傳遞浮點參數以及從函數返回浮點數的規則。
- 函數調用過程中保存寄存器的規則，例如調用者和被調用者保存寄存器。

Intel x86-64的浮點指令集發展歷史：
- 最早是1980年發佈的[8087](https://zh.wikipedia.org/wiki/Intel_8087)浮點協處理器，用來協助8086處理器（只支持整數計算）處理浮點計算。由此建立了x86系列的浮點模型，稱之為x87。後續還有80287、80387等。
- 直到1993年[奔騰](https://zh.wikipedia.org/wiki/%E5%A5%94%E9%A8%B0)時代，浮點協處理器被集成到了CPU內部。
- 1996年後，奔騰處理器中增加了一類處理整數和浮點的向量指令，稱之為[MMX](https://zh.wikipedia.org/wiki/MMX)，MultiMedia eXtensions，多媒體擴展。
- 1999年奔騰-III處理器上推出[SSE](https://zh.wikipedia.org/wiki/SSE)指令，Streaming SIMD Extensions，流式單指令多數據擴展。還有後來的SSE2等升級，直到SSE5。
- 2008年，Intel提出[AVX](https://zh.wikipedia.org/wiki/AVX%E6%8C%87%E4%BB%A4%E9%9B%86)指令集，高級向量擴展指令集，Advanced Vector Extensions。經過AVX1.1，AVX2，現已發展到了AVX-512。

這裡討論x86-64指令集，現代的x64位處理上幾乎都支持AVX2，所以這裡將基於AVX-2：
- 並且主要是標量指令。
- 如果需要了解浮點向量指令或者其他浮點指令擴展，可以自行查詢資料。
- GCC編譯器中編譯時加入選項`-mavx2`可以生成AVX-2的代碼。

### 浮點寄存器

SSE寄存器`%xmm0 ~ %xmm15`是128位的，AVX寄存器`%ymm0 ~ %ymm15`是256位的，其中其中就是後者的低位。

|256位AVX寄存器|128位SSE寄存器|用途
|:-:|:-:|:-:
|`%ymm0`|`%xmm0`|第1個浮點參數
|`%ymm1`|`%xmm1`|第2個浮點參數
|`%ymm2`|`%xmm2`|第3個浮點參數
|`%ymm3`|`%xmm3`|第4個浮點參數
|`%ymm4`|`%xmm4`|第5個浮點參數
|`%ymm5`|`%xmm5`|第6個浮點參數
|`%ymm6`|`%xmm6`|第7個浮點參數
|`%ymm7`|`%xmm7`|第8個浮點參數
|`%ymm8`|`%xmm8`|調用者保存
|`%ymm9`|`%xmm9`|調用者保存
|`%ymm10`|`%xmm10`|調用者保存
|`%ymm11`|`%xmm11`|調用者保存
|`%ymm12`|`%xmm12`|調用者保存
|`%ymm13`|`%xmm13`|調用者保存
|`%ymm14`|`%xmm14`|調用者保存
|`%ymm15`|`%xmm15`|調用者保存

如果只使用低32位或者64位，可以使用`%xmm0 ~ %xmm15`來訪問，具體數據大小則通過指令區分。

### 浮點傳送與轉換操作

浮點傳送指令：

|指令|源|目的|描述
|:-:|:-:|:-:|:-
|`vmovss`|M32|X|傳送單精度浮點數
|`vmovss`|X|M32|傳送單精度浮點數
|`vmovsd`|M64|X|傳送雙精度浮點數
|`vmovsd`|X|M64|傳送雙精度浮點數
|`vmovaps`|X|X|傳送對齊的封裝好的單精度浮點數
|`vmovapd`|X|X|傳送對齊的封裝好的雙精度浮點數

- 無論對齊與否，這些指令都能工作，但是建議32位數據按照4字節對齊，64位數據按照8字節對齊，能夠避免性能損失。
- `a`表示aligned對齊的意思。
- 例子：
```C
float p206_floating_point_passing(float v1, float *src, float *dest)
{
    float v2 = *src;
    *dest = v1;
    return v2;
}
```
- 彙編：
```x86asm
; v1 in %xmm0, src in %rdi, dest in %rsi
p206_floating_point_passing:
	vmovaps	%xmm0, %xmm1        ; copy v1
	vmovss	(%rdi), %xmm0       ; read v2 from src
	vmovss	%xmm1, (%rsi)       ; write v1 to dest
	ret                         ; return v2 in %xmm0
```

浮點數與整數間的轉換指令：

- 雙操作數浮點轉換：浮點數到整數。

|指令|源|目的|描述
|:-:|:-:|:-:|:-
|`vcvttss2si`|X/M32|R32|用截斷的方法把單精度浮點數轉換為32位整數
|`vcvttsd2si`|X/M64|R32|用截斷的方法把雙精度浮點數轉換為32位整數
|`vcvttss2siq`|X/M32|R64|用截斷的方法把單精度浮點數轉換為64位（四字）整數
|`vcvttsd2siq`|X/M64|R64|用截斷的方法把雙精度浮點數轉換為64位（四字）整數

- 三操作數浮點轉換：整數到浮點數。

|指令|源1|源2|目的|描述
|:-:|:-:|:-:|:-:|:-
|`vcvtsi2ss`|M32/R32|X|X|32位整數轉單精度浮點數
|`vcvtsi2sd`|M32/R32|X|X|32位整數轉雙精度浮點數
|`vcvtsi2ssq`|M64/R64|X|X|64位（四字）整數轉單精度浮點數
|`vcvtsi2sdq`|M64/R64|X|X|64位（四字）整數轉雙精度浮點數

- 其中整數轉浮點數是不太常見的三操作數格式，有兩個源和一個目的，第一個操作數讀自一個通用寄存器或者內存，第二個操作數只會影響高位字節，這裡可以忽略。
- 在最常見的使用場景中，第二個源和目的是一樣的：
```x86asm
vcvtsi2sdq %rax, %xmm1, %xmm1
```
- 例子：
```C
void p207_floating_integer_conversion(int a, long b, float *fp, double *dp, int *ip, long *lp)
{
    *fp = a; // int to float
    *fp = b; // long to float
    *dp = a; // int to double
    *dp = b; // long to double
    *ip = *fp; // float to int
    *lp = *fp; // float to long
    *ip = *dp; // double to int
    *lp = *dp; // double to long
}
```
- 彙編：
```x86asm
; a int %edi, b in %rsi, fp in %rdx, dp in %rcx, ip in %r8, lp in %r9
p207_floating_integer_conversion:
	vxorps	%xmm0, %xmm0, %xmm0
	movq	%rcx, %rax              ; dp in %rax
	vcvtsi2ssl	%edi, %xmm0, %xmm1  ; a to float in %xmm1
	vmovss	%xmm1, (%rdx)           ; *fp = a
	vcvtsi2ssq	%rsi, %xmm0, %xmm1  ; b to float in %xmm1
	vmovss	%xmm1, (%rdx)           ; *fp = b
	vcvtsi2sdl	%edi, %xmm0, %xmm1  ; a to double in %xmm1
	vmovsd	%xmm1, (%rcx)           ; *dp = a
	vcvtsi2sdq	%rsi, %xmm0, %xmm0  ; b to double in %xmm0
	vmovsd	%xmm0, (%rcx)           ; *dp = b
	vcvttss2sil	(%rdx), %ecx        ; *fp to int in %ecx
	movl	%ecx, (%r8)             ; *ip = *fp
	vcvttss2siq	(%rdx), %rdx        ; *fp to long in %rdx
	movq	%rdx, (%r9)             ; *lp = *fp
	vcvttsd2sil	(%rax), %edx        ; *dp to int in %edx
	movl	%edx, (%r8)             ; *ip = *dp
	vcvttsd2siq	(%rax), %rax        ; *dp to long in %rax
	movq	%rax, (%r9)             ; *lp = *dp
	ret
```

浮點類型之間的轉換指令：
- 同理其實還有三操作數的`vcvtss2sd vcvtsd2ss`來進行單精度和雙精度浮點數之間的轉換。
- 例子：
```C
double p207_float_double_conversion(float *fp, double *dp)
{
    *fp = *dp;
    *dp = *fp;
    return *dp;
}
```
- 彙編：
```x86asm
; fp in %rdi, dp in %rsi
p207_float_double_conversion:
	vxorps	%xmm0, %xmm0, %xmm0
	vcvtsd2ss	(%rsi), %xmm0, %xmm0    ; *dp to float in %xmm0
	vmovss	%xmm0, (%rdi)               ; *fp = *dp
	vcvtss2sd	%xmm0, %xmm0, %xmm0     ; *fp to double in %xmm0
	vmovsd	%xmm0, (%rsi)               ; *dp = *fp
	ret                                 ; return value is in %xmm0
```

### 過程中的浮點代碼

XMM寄存器可以用來向函數傳遞浮點參數，以及從函數返回浮點值：
- XMM寄存器可以通過`%xmm0 ~ %xmm7`最多傳遞8個寄存器，按照參數列出順序使用這些寄存器。超過8個後，會使用棧來傳遞。
- 使用寄存器`%xmm0`來返回浮點數。
- 所有XMM寄存器都是調用者保存的，被調用者不用保存覆蓋這些寄存器就可以使用。
- 所有參數中除去浮點數之外的參數仍舊按照整數參數的參數傳遞順序使用寄存器或者棧傳遞。

例子：
```C
void p210_passing_floating_parameters(float a, double b, float c, long d, double *p,
    float e, double f, float g, double h, double i, double j, double k);
void p210_passing_floating_caller()
{
    p210_passing_floating_parameters(1.0f, 2.0, 3.1f, 10L, 0,
        4.2f, 5.3, 6.4f, 7.5, 8.6, 9.7, 10.8);
}
```
- 彙編：
```x86asm
; d in %rdi, p in %rsi
; a - i in %xmm0 ~ %xmm7
; j, k in stack
p210_passing_floating_caller:
	subq	$8, %rsp
	pushq	$-1717986918
	movl	$1076205977, 4(%rsp)
	pushq	$1717986918
	movl	$1076061798, 4(%rsp)
	vmovsd	.LC0(%rip), %xmm7
	vmovsd	.LC1(%rip), %xmm6
	vmovss	.LC6(%rip), %xmm5
	vmovsd	.LC2(%rip), %xmm4
	vmovss	.LC7(%rip), %xmm3
	movl	$0, %esi
	movl	$10, %edi
	vmovss	.LC8(%rip), %xmm2
	vmovsd	.LC3(%rip), %xmm1
	vmovss	.LC9(%rip), %xmm0
	call	p210_passing_floating_parameters
	addq	$24, %rsp
	ret
.LC0:
	.long	858993459
	.long	1075917619
	.align 8
.LC1:
	.long	0
	.long	1075707904
	.align 8
.LC2:
	.long	858993459
	.long	1075131187
	.align 8
.LC3:
	.long	0
	.long	1073741824
	.section	.rodata.cst4,"aM",@progbits,4
	.align 4
.LC6:
	.long	1087163597
	.align 4
.LC7:
	.long	1082549862
	.align 4
.LC8:
	.long	1078355558
	.align 4
.LC9:
	.long	1065353216
	.ident	"GCC: (GNU) 12.1.0"
	.section	.note.GNU-stack,"",@progbits
```
- 編譯時，浮點數常量被編譯為了對應二進制位對應的整數，以加載到棧中或者寄存器中。看彙編時會比較難以理解。

### 浮點運算

浮點運算指令有一個或兩個操作數，一個目的：

|單精度|雙精度|效果|描述
|:-:|:-:|:-:|:-
|`vaddss`|`vaddsd`|`D = S1 + S2`|浮點數加法
|`vsubss`|`vsubsd`|`D = S1 - S2`|浮點數減法
|`vmulss`|`vmulsd`|`D = S1 * S2`|浮點數乘法
|`vdivss`|`vdivsd`|`D = S1 / S2`|浮點數除法
|`vmaxss`|`vmaxsd`|`D = max(S1, S2)`|浮點數最大值
|`vminss`|`vminsd`|`D = min(S1, S2)`|浮點數最小值
|`sqrtss`|`sqrtsd`|`D = sqrt(S1)`|浮點數平方根

- 其中第一個源操作數可以是XMM寄存器或者內存位置，第二個操作數和目的操作數都只能是XMM寄存器。
- 例子：
```C
double p210_floating_point_airthmetics(double a, float x, double b, int i)
{
    return a*x - b/i;
}
```
- 彙編：
```x86asm
; a in %xmm0, x in %xmm1, b in %xmm2, i in %edi
p210_floating_point_airthmetics:
	vcvtss2sd	%xmm1, %xmm1, %xmm1     ; x to double
	vmulsd	%xmm0, %xmm1, %xmm1         ; a*x to %xmm1
	vxorps	%xmm0, %xmm0, %xmm0
	vcvtsi2sdl	%edi, %xmm0, %xmm0      ; i to double in %xmm0
	vdivsd	%xmm0, %xmm2, %xmm2         ; b/i in %xmm2
	vsubsd	%xmm2, %xmm1, %xmm0         ; a*x - b/i to %xmm0
	ret
```

### 定義和使用浮點數常量

與整數運算不同，沒有浮點立即數這種東西，浮點數常量會按照其二進制位編譯為等價的整數，並按照浮點數來解釋二進制位：
- 並且浮點數常量會被放到常量區，而不是直接編碼到指令中。
- 例子：
```C
double p210_floating_point_constant(double temp)
{
    return 1.8 * temp + 32.1;
}
```
- 彙編：
```x86asm
p210_floating_point_constant:
	vmulsd	.LC10(%rip), %xmm0, %xmm0
	vaddsd	.LC11(%rip), %xmm0, %xmm0
	ret
	.align 8
.LC10:  ; 1.8, little endian
	.long	-858993459  ; low order 4 bytes of 1.8
	.long	1073532108  ; high order 4 bytes of 1.8
	.align 8
.LC11:  ; 32.1
	.long	-858993459
    .long	1077939404
```

### 浮點數中的位級操作

浮點數也可以進行按位運算，雖然可能沒有什麼意義，不過前面也出現過，可能會用來對一個寄存器進行清零操作等：

|單精度|雙精度|效果|描述
|:-:|:-:|:-:|:-
|`vxorps`|`xorpd`|`D = S2 ^ S1`|按位異或（XOR）
|`vandps`|`andpd`|`D = S2 & S1`|按位與（AND）

### 浮點比較操作

AVX2提供了兩條浮點數比較指令：

|指令|基於|描述
|:-:|:-:|:-
|`vucomiss S1, S2`|`S2 - S1`|單精度浮點數比較
|`vucomisd S1, S2`|`S2 - S1`|雙精度浮點數比較

浮點數比較會設置三個條件碼：零標誌ZF，進位標誌CF，奇偶標誌PF。

|順序S2:S1|CF|ZF|PF
|:-:|:-:|:-:|:-:
|無序（其中一個是NaN）|1|1|1
|`S2 < S1`|1|0|0
|`S2 = S1`|0|1|0
|`S2 > S1`|0|0|0

除了無序結果以外，比較結果的標誌和無符號數一致，所以需要使用無符號數的條件跳轉指令：`ja je jb`，無需結果在C語言中只能通過`else`得到：
- 例子：
```C
int p214_floating_point_comparison(double x)
{
    int result;
    if (x > 0)
    {
        result = 0;
    }
    else if (x == 0)
    {
        result = 1;
    }
    else if (x < 0)
    {
        result = 2;
    }
    else
    {
        result = 3;
    }
    return result;
}
```
- 彙編：
```x86asm
p214_floating_point_comparison:
	vxorpd	%xmm1, %xmm1, %xmm1
	vcomisd	%xmm1, %xmm0
	jbe	.L74
	movl	$0, %eax
	ret
.L74:
	vucomisd	%xmm1, %xmm0
	jp	.L71
	jne	.L71
	movl	$1, %eax
	ret
.L71:
	vxorpd	%xmm1, %xmm1, %xmm1
	vcomisd	%xmm0, %xmm1
	ja	.L75
	movl	$3, %eax
	ret
.L75:
	movl	$2, %eax
	ret
```

## 總結

- C語言到彙編的映射相對來說是簡單直接的。
- 但在高優化等級下，生成的彙編可能非常不易讀，因為進行了很多代碼轉換和優化。
- C++的編譯也是同理，不過C++中會有名稱修飾，ABI會比較不一樣，會複雜很多。比如對象的拷貝是通過調用拷貝構造函數，而不是直接能用一條指令完成，並且編譯器會自動插入非平凡析構類型對象的析構調用，還有許多C++特性會增加彙編的複雜性，比如虛表等。
- 一般來說沒有比較瞭解太深，除非要寫編譯器。

## 補充：不同環境中編譯生成的彙編對比

環境：64位Windows環境下的MinGW-W64（GCC 12.1.0）以及64位Linux環境下的原生GCC 12.1.0。
- 分析調用約定：
    - 各種調用約定下，誰負責清理堆棧。
    - 參數放在哪些寄存器，參數順序之類。
    - 數據長度差異。
- 例子：
```C
void test_of_parameters(char a, short b, int c, long d,
    char* pa, short *pb, int *pc, long* pd)
{
    *pa = a;
    *pb = b;
    *pc = c;
    *pd = d;
}
```
- Linux彙編：
```x86asm
; a in %dil, b in %si, c in %edx, d in %rcx
; pa in %r8, pb in %r9, pc in 8(%rsp), pd in 16(%rsp)
; note: (%rsp) is return address
test_of_parameters:
	movb	%dil, (%r8)
	movw	%si, (%r9)
	movq	8(%rsp), %rax
	movl	%edx, (%rax)
	movq	16(%rsp), %rax
	movq	%rcx, (%rax)
	ret
```
- Windows彙編：
```x86asm
; a in %cl, b in %dx, c in %r8d, d in %r9d
; pa in 40(%rsp), pb in 48(%rsp), pc in 56(%rsp), pd in 64(%rsp)
test_of_parameters:
	movq	40(%rsp), %rax
	movb	%cl, (%rax)
	movq	48(%rsp), %rax
	movw	%dx, (%rax)
	movq	56(%rsp), %rax
	movl	%r8d, (%rax)
	movq	64(%rsp), %rax
	movl	%r9d, (%rax)
	ret
```

結論：
- 不同系統，不同編譯器上調用約定不同，怎樣傳參的約定也就不一樣，本章的所有東西都是基於Linux的，Windows上會有區別，但是道理是相同的。
- 至於具體的調用約定則有需要再探討。

## 補充：C語言內聯彙編

C語言中可以通過`asm`關鍵字引入內聯彙編，在C源程序中嵌入內聯彙編，不過內聯彙編沒有固定標準，在C中被當做擴展，可以不支持：
- GCC中可以通過`__asm__`關鍵字引入，而不是`asm`。而MSVC的關鍵字是`__asm`。
- 例子：應當使用在64位Linux環境中的GCC編譯。
```C
int inline_assembly_test(int x, int y)
{
    // 64bit Linux: x in %edi, y in %esi
    __asm__(
        "movl %esi, %eax\n\t"
        "imull %edi, %eax\n\t"
        "ret"
    );
    return 0;
}
```
- 內聯彙編僅能運行在特定的架構上，是和調用約定、ABI高度綁定的，通常不具有跨指令集、操作系統、編譯器的可移植性。
- 一般來說很少使用，可以用在必須用匯編才能實現的場景中。當然這種場景其實還是添加彙編源文件編譯為目標文件後鏈接到程序中來更好一些，耦合也更松，跨平臺則直接編寫多份即可。
