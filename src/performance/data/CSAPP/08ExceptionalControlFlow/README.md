<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [第八章：異常控制流](#%E7%AC%AC%E5%85%AB%E7%AB%A0%E5%BC%82%E5%B8%B8%E6%8E%A7%E5%88%B6%E6%B5%81)
  - [8.1 異常](#81-%E5%BC%82%E5%B8%B8)
    - [異常處理](#%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86)
    - [異常類別](#%E5%BC%82%E5%B8%B8%E7%B1%BB%E5%88%AB)
    - [Linux/x86-64系統中的異常](#linuxx86-64%E7%B3%BB%E7%BB%9F%E4%B8%AD%E7%9A%84%E5%BC%82%E5%B8%B8)
  - [8.2 進程](#82-%E8%BF%9B%E7%A8%8B)
    - [邏輯控制流](#%E9%80%BB%E8%BE%91%E6%8E%A7%E5%88%B6%E6%B5%81)
    - [併發流](#%E5%B9%B6%E5%8F%91%E6%B5%81)
    - [私有地址空間](#%E7%A7%81%E6%9C%89%E5%9C%B0%E5%9D%80%E7%A9%BA%E9%97%B4)
    - [用戶模式和內核模式](#%E7%94%A8%E6%88%B7%E6%A8%A1%E5%BC%8F%E5%92%8C%E5%86%85%E6%A0%B8%E6%A8%A1%E5%BC%8F)
    - [上下文切換](#%E4%B8%8A%E4%B8%8B%E6%96%87%E5%88%87%E6%8D%A2)
  - [8.3 系統調用錯誤處理](#83-%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8%E9%94%99%E8%AF%AF%E5%A4%84%E7%90%86)
  - [8.4 進程控制](#84-%E8%BF%9B%E7%A8%8B%E6%8E%A7%E5%88%B6)
    - [進程ID](#%E8%BF%9B%E7%A8%8Bid)
    - [創建終止進程](#%E5%88%9B%E5%BB%BA%E7%BB%88%E6%AD%A2%E8%BF%9B%E7%A8%8B)
    - [回收子進程](#%E5%9B%9E%E6%94%B6%E5%AD%90%E8%BF%9B%E7%A8%8B)
    - [讓進程休眠](#%E8%AE%A9%E8%BF%9B%E7%A8%8B%E4%BC%91%E7%9C%A0)
    - [加載並運行程序](#%E5%8A%A0%E8%BD%BD%E5%B9%B6%E8%BF%90%E8%A1%8C%E7%A8%8B%E5%BA%8F)
    - [利用fork和execve運行程序](#%E5%88%A9%E7%94%A8fork%E5%92%8Cexecve%E8%BF%90%E8%A1%8C%E7%A8%8B%E5%BA%8F)
  - [8.5 信號](#85-%E4%BF%A1%E5%8F%B7)
    - [信號術語](#%E4%BF%A1%E5%8F%B7%E6%9C%AF%E8%AF%AD)
    - [發送信號](#%E5%8F%91%E9%80%81%E4%BF%A1%E5%8F%B7)
    - [接收信號](#%E6%8E%A5%E6%94%B6%E4%BF%A1%E5%8F%B7)
    - [阻塞和解除阻塞信號](#%E9%98%BB%E5%A1%9E%E5%92%8C%E8%A7%A3%E9%99%A4%E9%98%BB%E5%A1%9E%E4%BF%A1%E5%8F%B7)
    - [編寫信號處理程序](#%E7%BC%96%E5%86%99%E4%BF%A1%E5%8F%B7%E5%A4%84%E7%90%86%E7%A8%8B%E5%BA%8F)
    - [同步流以避免討厭的併發錯誤](#%E5%90%8C%E6%AD%A5%E6%B5%81%E4%BB%A5%E9%81%BF%E5%85%8D%E8%AE%A8%E5%8E%8C%E7%9A%84%E5%B9%B6%E5%8F%91%E9%94%99%E8%AF%AF)
    - [顯式等待信號](#%E6%98%BE%E5%BC%8F%E7%AD%89%E5%BE%85%E4%BF%A1%E5%8F%B7)
  - [8.6 非本地跳轉](#86-%E9%9D%9E%E6%9C%AC%E5%9C%B0%E8%B7%B3%E8%BD%AC)
  - [8.7 操作進程的工具](#87-%E6%93%8D%E4%BD%9C%E8%BF%9B%E7%A8%8B%E7%9A%84%E5%B7%A5%E5%85%B7)
  - [補充資料](#%E8%A1%A5%E5%85%85%E8%B5%84%E6%96%99)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 第八章：異常控制流

通常一個系統中除了順序的指令流之外還有跳轉、函數調用返回這種突變流，這些控制流都是程序的內部變化。但是系統中應當還有其他類型的控制流，也就是程序響應外部環境發生變化的控制流：
- 這些控制流不是被內部程序變量捕獲的，而且不一定要和程序執行相關。
- 比如：
    - 一個硬件定時器定期產生的信號，這個事件必須得到處理。
    - 包到達網絡適配器後，必須被存放到主存中。
    - 程序向磁盤請求數據，然後休眠，數據就緒後收到的通知。
    - 子進程終止時，父進程得到通知。
- 現代系統通過使控制流發生突變來對這些情況作出反應，我們把這些突變稱之為**異常控制流**（Exceptional Control Flow，ECF）。
- 異常控制流發生在系統的各個層次：
    - 硬件層：硬件檢測到的事件觸發控制轉移到異常處理程序。
    - 操作系統層：內核通過上下文切換控制一個用戶進程轉移到另一個用戶進程。
    - 應用層：一個進程發送信號到另一個進程，接受者會突然將控制轉移到一個信號處理程序。
    - 一個程序可以通過迴避通常的棧規則，並執行到其他函數中任意位置的非本地跳轉來對錯誤做出反應。
- ECF非常重要：
    - ECF是操作系統用來實現I/O、進程和虛擬內存的基本機制。
    - 應用程序通過一個叫做陷阱（trap）或者系統調用（system call）的ECF形式，向操作系統請求服務。ECF是應用程序和內核交互的基本方式，比如磁盤寫數據、從網絡讀數據、創建新進程、終止進程等。
    - 操作系統為應用程序提供了強大的ECF機制，瞭解這些機制才能編寫如Unix Shell和Web服務器之類的程序。
    - ECF是計算機系統中實現併發的基本機制，理解ECF是理解併發的第一步。
    - ECF是實現軟件異常的基本機制，理解ECF才能理解異常機制是如何實現的。
- 本章介紹的是應用如何和操作系統交互的東西，這些交互都是圍繞ECF的。
- 本章內容：
    - 異常：位於硬件和操作系統的交界。
    - 系統調用：為應用程序提供到操作系統入口點的異常。
    - 進程和信號：應用和操作系統的交界。
    - 非本地跳轉：ECF的一種應用層形式。

## 8.1 異常

異常是異常控制流的一種形式，一部分由硬件實現，一部分由操作系統實現。因為有一部分由硬件實現，所以具體系統隨系統不同而不同。但基本思想是一致的。
- 異常就是控制流中的突變，用來響應處理器狀態的某些變化。
- 狀態的變化被稱為事件，事件可能和當前指令的執行直接相關，比如缺頁、算術溢出、除零等，也可能沒有關係，比如系統定時器信號、一個I/O請求完成。
- 發生異常時會跳轉到異常處理程序，處理完後再跳轉回來繼續執行。
```
    |
    |
    | Icurr ---------------->| 異常處理程序
event occurs here            |
    | Inext <----------------|
    |
    |
    v
```
- 任何情況下，當處理器檢測到事件發生，它會通過一張叫做**異常表**（exception table）的跳轉表，進行一個間接過程調用，跳轉到專門設計用來處理這類事件的操作系統子程序（異常處理程序，exception handler）。異常處理程序處理完後，根據引起異常的事件的類型，會發生以下三種情況中的一種：
    - 處理程序將控制返回給當前指令Icurr，即發生事件時正在執行的指令。
    - 處理程序將事件返回給下一個指令Inext，即沒有發生異常將會執行的下一條指令。
    - 處理程序終止被中斷的程序。

注意：本章所述的異常是ECF中統稱的異常，而編程語言中的異常則只是其中一種應用級ECF實現，大多數時候異常都是指前者，從上下文可以區分到底在說硬件級異常還是軟件異常。

### 異常處理

異常是由硬件和軟件配合實現的，需要搞清楚他們分別負責哪個部分：
- 系統中每種可能的異常都分配了一個唯一的非負整數的**異常號**（exception number）。
- 其中一些號碼是由處理器設計者分配，其他號碼是由操作系統內核的設計者分配。前者包括除零、缺頁、內存訪問違例、斷點、算術運算溢出等，後者包括系統調用、外部I/O設備信號等。
- 系統啟動時，操作系統會分配或者初始化一張稱為異常表的跳轉表。通過異常號k作為索引就可以從異常表中查找出對應的異常處理程序。
- 異常表的起始地址放在一個叫做**異常表基址寄存器**（exception table base register）的寄存器中，通過異常號乘以異常表條目大小就能得到異常處理程序地址。在x86-64架構中，通過一次比例變址尋址就能找到。
- 在運行時，處理器檢測到發生了一個事件，並確定了異常號k之後。處理器會通過執行間接過程調用觸發異常，通過異常表條目k，轉到對應的處理程序。
- 異常類似於過程調用，但有一些不同之處：
    - 過程調用時，跳轉到處理程序前，處理器將返回地址壓入棧中。然而根據異常類型，返回地址要麼是當前指令，要麼是下一條指令。
    - 處理器還會將一些額外狀態壓入棧中，在異常處理返回後再恢復這些狀態。
    - 如果控制從用戶程序轉移到內核，那麼所有項目都被壓入內核棧，而不是壓入用戶棧。
    - 異常處理程序運行在內核態下，也就是說他們對所有的系統資源都有完全的訪問權限。
- 一旦硬件觸發了異常，轉入異常處理程序中後，剩下的工作都由異常處理程序完成。在處理結束後，通過一條特殊的“從中斷返回”指令，可選地返回到被中斷的程序。該指令將適當的狀態彈出到處理器的控制和數據寄存器中。如果異常中斷的是一個用戶程序，就將狀態恢復到用戶態，然後將控制返回給被中斷程序。

### 異常類別

異常分為四類：中斷（interrupt）、陷阱（trap）、故障（fault）、終止（abort）。這些異常有不同的屬性：

|類別|原因|異步發生/同步發生|返回行為|
|:-:|:-|:-:|:-|
|中斷|來自I/O設備信號|異步|總是返回下一條指令
|陷阱|有意的異常|同步|總是返回到下一條指令
|故障|潛在可恢復的錯誤|同步|可能返回到當前指令
|終止|不可恢復的錯誤|同步|不會返回

**中斷**：
- 中斷是**異步發生**的，是來自於處理器外部的I/O設備信號的結果。也就是說它不是由任何一條專門的指令造成的，而是隨機的來自外圍設備的信號。
- 硬件中斷的處理程序常稱為中斷處理程序。
- 發起中斷的設備通過向處理器芯片的引腳發送信號，並將異常放到系統總線上，來觸發中斷，這個異常號標識了引起中斷的設備。
- 當每一條指令執行完成後，處理器如果注意到中斷引腳電壓變高了，就會從系統總線上讀取異常號，然後調用適當的中斷處理程序。
- 當處理程序返回時，將控制返回給下一條指令，程序繼續執行，好像沒有中斷過一樣。
- 剩下的類型都是同步發生的，是執行當前指令的結果，將這些指令統稱為故障指令（faulting instruction）。

**陷阱和系統調用**：
- 陷阱是有意的異常，是執行一條指令的結果，陷阱處理程序將返回到下一條指令。
- 陷阱最重要的用途是在用戶程序和內核之間提供像過程調用一樣的接口，稱之為系統調用（system call）。
- 用戶程序經常需要向系統請求服務，這些服務只能有系統調用在內核態下完成，所以需要一個陷阱，以從用戶態切換到內核態。這些服務很多，比如讀一個文件（read）、創建一個新線程（fork）、加載一個新程序（execve）、終止當前進程（exit）等。
- 為了支持這類服務，系統提供了一條特殊的`syscall n`指令，用戶程序請求服務`n`時就可以執行這條指令，執行`syscall1`指令會將控制傳遞到陷阱處理程序，這個處理程序解析參數，並調用適當的內核程序。
- 普通用戶程序運行在用戶態，只有使用系統調用進入內核態才能調用一些特權指令和訪問內核棧。操作系統通過系統調用的方式向用戶提供一系列功能，用戶要使用這些功能就必須調用系統調用（直接或者間接）。

**故障**：
- 故障由錯誤情況引起，可能能夠被故障處理程序修正。
- 故障發生時，處理器將控制權轉移給故障處理程序，如果故障處理程序能夠修正這個情況，那麼它就將控制返回到引起故障的指令，從而重新執行它。否則，處理程序調用內核中的`abort`例程，`abort`例程會終止引起故障的應用程序。
- 一個典型的故障例子是**缺頁異常**，當指令引用一個虛擬地址，而這個虛擬地址對應的物理頁面不再內存中，那麼就必須將其從磁盤換出到內存中，就會發生故障。當缺頁處理程序返回時，重新執行引起缺頁的指令，對應物理頁面已經在內存中，就不會再發生缺頁了。

**終止**：
- 終止是不可恢復錯誤造成的結果，通常是一些硬件錯誤。
- 終止處理程序不會將控制返回給應用程序，而是將控制返回給一個`abort`例程，它將終止程序運行。

### Linux/x86-64系統中的異常

x86-64中系統中定義的異常，有256中異常類型，0~31為Intel架構師定義，對任何x86-64系統都一樣，32~256對應操作系統定義的中斷和陷阱：
- 例子：

|異常號|描述|異常類別|
|:-:|:-|:-
|0|除法錯誤|故障
|13|一般保護故障|故障
|14|缺頁|故障
|18|機器檢查|終止
|32~255|操作系統定義異常|中斷或陷阱

- 除法錯誤：整數除零時會導致除零故障，Unix系統不會視圖從除法錯誤中恢復，而是選擇終止程序，Linux Shell通常會將除法錯誤報告為`Floating point exception`。
- 一般保護故障：很多原因可能會導致，比如訪問一個未分配的虛擬內存區域，或者寫一個只讀頁面中的內存，Linux不會嘗試恢復這類故障，Linux Shell通常將這類保護故障報告為**段錯誤**（segmentation fault）。
- 段錯誤例子：
```C
int main()
{
    char* s = "hello"; // "hello" is in .rodata section
    s[0] = 'y'; // write read-only data
    return 0;
}
```
- 缺頁：如前所述，第九章有具體細節。
- 機器檢查：在導致故障的指令執行過程中檢測到指明硬件錯誤時發生，機器檢查處理程序不會返回控制給應用程序，而知直接終止。

Linux/X86-64系統調用：
- Linux系統提供幾百種系統調用，當應用程序想要請求內核服務時可以使用，比如讀寫文件、創建新進程等。
- 每個系統調用都有一個唯一的整數號，對應到內核中一個跳轉表的偏移量。（注意這個跳轉表和異常表不一樣，這個編號也不是異常號）。
- C程序用`syscall`函數可以直接調用任何系統調用，然而實際中幾乎沒有必要這麼做，對於大多數系統調用，操作系統都提供了標準C函數封裝。這些包裝函數將參數打包到一起，以適當系統調用指令陷入內核，然後將系統調用的狀態返回給調用程序。
- 系統調用的調用慣例，和普通函數不一樣：
    - 寄存器`%rax`包含系統調用號。
    - 所有系統調用參數都使用寄存器傳遞。
    - 使用寄存器`%rdi %rsi %rdx %r10 %r8 %r9`傳遞最多6個參數。
    - 從系統調用返回時，`%rcx %r11`會被破壞，`%rax`包含返回值。
    - 返回值在`-4095 ~ -1`表明發生了錯誤，對應於付的errno。
- Linux系統常見系統調用示例：

|編號|名字|描述、
|:-:|:-:|:-
|0|read|讀文件|
|1|write|寫文件
|2|open|打開文件
|3|close|關閉文件
|4|stat|獲得文件信息
|9|mmap|將內存映射到文件
|12|brk|重置堆頂
|32|dup2|複製文件描述符


使用示例：
- 用`syscall`直接進行系統調用：
```
SYSCALL(2)

NAME
       syscall - indirect system call

SYNOPSIS
       #include <unistd.h>
       #include <sys/syscall.h>   /* For SYS_xxx definitions */

       long syscall(long number, ...);
```
- `write`包裝：
```
WRITE(2)

NAME
       write - write to a file descriptor

SYNOPSIS
       #include <unistd.h>

       ssize_t write(int fd, const void *buf, size_t count);
```
- `write`例子：
```C
#include <unistd.h>

char* s = "yes\n";

int main()
{
    syscall(1, STDOUT_FILENO, "hello\n", 6);
    write(STDOUT_FILENO, "world\n", 6);
    // GCC inline assembly
    __asm__(
        "movq $1, %rax\n\t" // syscall number: 1
        "movq $1, %rdi\n\t" // STDOUT_FILENO is 1
        "movq s, %rsi\n\t" // value of s
        "movq $4, %rdx\n\t" // size: 4
        "syscall"
    );
    write(STDOUT_FILENO, "no\n", 3);
    return 0;
}
```
- 輸出結果：
```
hello
world
yes
no
```
- 使用`syscall`和調用C包裝是一樣的，最終都是通過`syscall`指令來陷入內核，進行系統調用。

## 8.2 進程

進程（process）是計算機科學中最深刻、最成功的概念之一，異常是實現進程概念的基本構造塊：
- 進程給我們提供了一個假象：我們的程序好像是系統中當前唯一運行的程序一樣，我們的程序好像是獨佔處理器和內存，處理器好像是無間斷一條接一條執行程序中指令。
- 進程的經典定義是一個執行中程序的實例。系統中每個程序都運行在某個進程的上下文（context）中。上下文是由程序正確運行所需的狀態組成的，這個狀態包括存放在內存中的程序和數據、棧、通用目的寄存器內容、程序計數器、環境變量、打開文件描述符、頁表等的集合。
- 在Shell中執行一個程序時，Shell就會創建一個新進程，然後在這個新進程的上下文中運行這個可執行目標文件。
- 進程提供給應用程序的關鍵抽象：
    - 一個獨立的邏輯控制流：提供程序在獨佔使用處理器的假象。
    - 一個私有的地址空間：提供程序獨佔使用內存系統的假象。

### 邏輯控制流

每個程序的PC的序列稱之為邏輯控制流，或者邏輯流，
- 操作系統向我們提供獨佔處理器的假象，實際上卻是每個進程運行一段時間後掛起，輪到其他進程執行。
- 不過由於切換過程中並不改變程序狀態，所以進程的切換對我們來說並不會有感知。邏輯流看起來是連續的。

### 併發流

- 一個邏輯流在時間上與另一個流重疊，稱之為併發流（concurrent flow），這兩個流被稱為併發地運行，準確地說，他們互相併發。
- 多個流併發執行的現象稱之為併發（concurrency）。
- 一個進程和其他進程輪流運行的概念稱之為多任務（multitasking）。
- 一個進程執行它的控制流的一部分的每一時間段叫做時間片（time slice）。多任務也叫做時間分片（time slicing）。一個進程的流由多個時間片組成。
- 併發流的思想與流運行的處理器核心數量或者計算機數量無關，如果兩個流在時間上重疊，它們就是併發的，即使是運行在同一處理器上。
- 如果在同一個時刻，兩個流同時在運行，他們就稱之為並行流（parallel stream），它們是併發流的真子集。並行流是實現併發流的其中一個手段。

### 私有地址空間

進程也為每個程序提供了它們在獨佔地址空間的假象，進程為每個程序提供他們自己的私有地址空間。
- 一般而言，一個進程的私有地址空間內存中的字節是不會被其他進程讀取的。
- 這樣的地址空間都有通用的結構，細節見第九章。
- 私有地址空間是通過虛擬內存實現的，細節見第九章。

### 用戶模式和內核模式

為了更好地實現進程，操作系統應該提供一種機制，限制一個應用可以執行的指令以及它可以訪問的地址空間範圍：
- 現代處理器通常通過某個控制寄存器中的模式位來提供這種功能，這個寄存器描述了進程當前所擁有的特權。
- 模式位可以有兩種狀態：內核態和用戶態。運行在內核態中的進程可以執行任何指令，並且可以訪問系統中的任何內存位置，而運行在用戶態的進程則只能訪問自己的地址空間，並且只能執行特權指令。
- 普通程序都是運行在用戶態的，用戶態下不能執行特權指令，比如停止處理器、改變模式位、發起I/O操作等，也不允許進程直接修改地址空間中內核區的數據和代碼。任何這種嘗試都會導致故障發生。
- 操作系統通過系統調用提供這些功能，執行系統調用將進入內核態。
- 一般地來說，將控制從用戶態轉換為內核態的唯一方式是通過中斷、故障或者陷阱這樣的異常。
- 異常發生時，控制傳遞到異常處理程序，執行異常處理程序時，處理器模式將從用戶態變為內核態。返回應用程序時，又從內核態切換回用戶態。

Linux提供`/proc`文件系統，允許用戶模式進程訪問內核數據結構內容：
- `/proc`文件系統將許多內核數據結構的內容輸出為一個用戶程序可以讀取的文本文件的層次結構。
- 比如可以通過`cat /proc/cpuinfo`查看CPU信息。

### 上下文切換

操作系統內核使用一種叫做**上下文切換**（context switch）的高級形式的異常控制流來實現多任務。
- 上下文切換機制建立在底層異常機制之上。
- 內核為每個進程維護一個上下文（context），上下文就是內核重新啟動一個被搶佔的進程所需的狀態。包括：通用目的寄存器、浮點寄存器、程序計數器、用戶棧、狀態寄存器、內核棧和各種內核數據結構，比如頁表、進程表、打開文件表等。
- 進行執行中，內核可以決定搶佔當前線程，並重新開始一個先前被搶佔的線程。這種決策叫做調度（scheduling），由內核中的**調度器**（scheduler）的代碼處理。
- 內核通過上下文切換的方式調度進程，上下文切換的步驟：
    - 保存當前進程上下文。
    - 恢復某個先前被搶佔的進程被保存的上下文。
    - 將控制傳遞給新恢復的進程。
- 當內核代表用戶執行系統調用時，可能會發生上下文切換。如果一個進程發生阻塞（等待IO或者等待鎖釋放條件變量通知等）或者睡眠，那麼內核會將其切換到其他進程。即使系統調用沒有阻塞，分配的時間片執行完之後，系統也會選擇切換上下文調度到其他線程。
- 中斷也可能引發上下文切換，比如這個中斷可能是由定時器發送表示當前進程時間片已經執行完了，或者磁盤DMA傳輸完成發送來的中斷信號。

## 8.3 系統調用錯誤處理

UNIX系統級函數遇到錯誤時，通常會返回`-1`，並設置全局變量`errno`，可以使用`strerror`將`errno`的值轉化為一個字符串。使用每個可能出錯的系統級函數時，總是應該檢查其返回值，可以將檢查返回值的工作包裝到一個函數中，以簡化重複代碼。

## 8.4 進程控制

UNIX提供了大量操作進程的系統調用，這一節描述這些函數並說明如何使用。

### 進程ID

每個進程都有一個唯一的正整數進程ID（PID）：
- `getid`獲取調用進程的PID。
- `getppid`獲取父進程PID。
```C
#include <sys/types.h>
#include <unistd.h>
pid_t getpid(void);
pid_t getppid(void);
```

### 創建終止進程

從程序員角度，可以說程序總是處於下面三種狀態之一：
- 運行：要麼在CPU上運行，要麼在等待執行最終會被內核調度。
- 停止：進程被掛起，且不會被調度。當收到`SIGSTOP SIGTSTP STGTTIN STGTTOUT`信號時，進程被掛起，知道收到`SIGCONT`信號。信號是軟中斷的一種形式，下一節詳述。
- 終止：運行結束。三種終止原因：收到終止信號，從主程序返回，調用`exit`函數。
```C
#include <stdlib.h>
void exit(int status);
```

相關UNIX系統調用接口：
- 父進程通過`fork`函數創建新的子進程：
```C
#include <sys/types.h>
#include <unistd.h>
pid_t fork(void);
```
- 新創建的子進程幾乎但不完全和父進程完全相同，子進程得到與父進程用戶級虛擬地址空間相同但獨立的一份副本（會使用COW機制降低不必要的開銷），父進程與子進程最大區別在於它們有不同的PID。
- `fork`會返回兩次，子進程中返回0，父進程中返回子進程PID，以此區分子進程和父進程。
- 子進程和父進程是併發執行的獨立進程。
- 子進程和父進程擁有相同但是獨立的虛擬地址空間。
- 子進程父進程共享打開的文件，比如`stdout`標準輸出。

### 回收子進程

- 當一個子進程由於某種原因終止時，內核並不是立刻將其從系統中清除。
- 相反，進程會保持在已終止的狀態中，直到被它的父進程回收（reaped）。
- 當父進程回收已終止子進程時，內核將子進程狀態傳遞給父進程，然後拋棄終止的進程，從此刻開始，該子進程就不存了。
- 一個終止了但是還未被回收的進程稱為僵死進程（zombie）。
- 如果一個父進程終止了，內核會安排`init`進程稱為它的孤兒進程的養父進程。
- `init`進程的PID為1，是內核啟動時就創建的，不會終止。
- 如果父進程沒有回收它的僵死子進程就終止了，內核會安排`init`進程回收這些僵死的子進程。
- 長時間運行的程序，總是應該回收它們的僵死子進程，即是僵死子進程沒有運行，他們依然在消耗內存資源。

回收子進程：
- 一個進程可以通過使用`waitpid`函數等待它的子進程終止或者結束：
```C
#include <sys/types.h>
#include <sys/wait.h>
pid_t wait(int *wstatus);
pid_t waitpid(pid_t pid, int *wstatus, int options);
```
- 等待集合：
    - 如果`pid > 0`，那麼就是等待該PID的單獨子進程。
    - 如果`pid == -1`，那麼等待集合就是父進程的所有子進程。
- `options`參數可以選擇`WNOHANG WUNTRACED WCONTINUED`是在子進程仍在執行時直接返回還是掛起父進程。
- `wstatus`可以用來保存返回子進程的狀態信息：是`exit return`正常返回，還是因為信號返回，可以通過這個參數得到進程終止的相關信息。
- 更多細節查看`man waitpid`。
- `wait`是`waitpid`的簡化版本，等價於`waitpid(-1, wstatus, 0)`。

### 讓進程休眠

`sleep`函數讓進程掛起指定時間：
```C
#include <unistd.h>
unsigned int sleep(unsigned int seconds);
```
- 查看`man 3 sleep`。
- 可以被信號中斷。

`pause`函數讓進程休眠，直到進程受到一個信號：
```C
#include <unistd.h>
int pause(void);
```
- `man 2 pause`。

### 加載並運行程序

```C
#include <unistd.h>
int execve(const char *pathname, char *const argv[],
                  char *const envp[]);
```
- 執行文件`pathname`，如果找不到，立即返回。
- 如果找到，以參數列表`argv`，環境變量列表`envp`執行，此時從不返回。
- `argv`第一個參數是可執行文件名，環境變量為`name=value`形式的字符串列表，都以NULL作為列表末尾標誌。
- 加載了文件之後，轉到啟動代碼，設置棧，並將控制交給新程序主函數。
- Linux提供幾個函數來操作環境變量：
```C
#include <stdlib.h>
char *getenv(const char *name);
int setenv(const char *name, const char *value, int overwrite);
int unsetenv(const char *name);
```

### 利用fork和execve運行程序

像Unix Shell和Web服務器這樣的程序大量使用`fork`和`execve函數來執行程序：
- shell是一個交互型應用程序，代表用戶運行其他程序。
- shell是一個Read-Eval-Loop，讀取用戶輸入，執行，終止，並繼續循環這個過程。
- 書上P526編寫了一個簡單的shell，實現了讀取-求值循環，可以參考。

更多細節參考APUE。

## 8.5 信號

前面說了硬件和軟件如何配合實現底層異常機制，這裡將研究一種更高層的軟件形式的異常，成為Linux信號，它允許進程和內核中斷其他進程。
- 一個信號就是一條小消息，它通知進程系統中發生了一個某種類型的事件。
```
Linux supports the standard signals listed below.  The second column of the table indicates which standard (if any) specified the signal: "P1990" indicates that the signal is described
in the original POSIX.1-1990 standard; "P2001" indicates that the signal was added in SUSv2 and POSIX.1-2001.

Signal      Standard   Action   Comment
────────────────────────────────────────────────────────────────────────
SIGABRT      P1990      Core    Abort signal from abort(3)
SIGALRM      P1990      Term    Timer signal from alarm(2)
SIGBUS       P2001      Core    Bus error (bad memory access)
SIGCHLD      P1990      Ign     Child stopped or terminated
SIGCLD         -        Ign     A synonym for SIGCHLD
SIGCONT      P1990      Cont    Continue if stopped
SIGEMT         -        Term    Emulator trap
SIGFPE       P1990      Core    Floating-point exception
SIGHUP       P1990      Term    Hangup detected on controlling terminal
                                or death of controlling process
SIGILL       P1990      Core    Illegal Instruction
SIGINFO        -                A synonym for SIGPWR
SIGINT       P1990      Term    Interrupt from keyboard
SIGIO          -        Term    I/O now possible (4.2BSD)
SIGIOT         -        Core    IOT trap. A synonym for SIGABRT
SIGKILL      P1990      Term    Kill signal
SIGLOST        -        Term    File lock lost (unused)
SIGPIPE      P1990      Term    Broken pipe: write to pipe with no
                                readers; see pipe(7)
SIGPOLL      P2001      Term    Pollable event (Sys V).
                                Synonym for SIGIO
SIGPROF      P2001      Term    Profiling timer expired
SIGPWR         -        Term    Power failure (System V)
SIGQUIT      P1990      Core    Quit from keyboard
SIGSEGV      P1990      Core    Invalid memory reference
SIGSTKFLT      -        Term    Stack fault on coprocessor (unused)
SIGSTOP      P1990      Stop    Stop process
SIGTSTP      P1990      Stop    Stop typed at terminal
SIGSYS       P2001      Core    Bad system call (SVr4);
                                see also seccomp(2)
SIGTERM      P1990      Term    Termination signal
SIGTRAP      P2001      Core    Trace/breakpoint trap
SIGTTIN      P1990      Stop    Terminal input for background process

SIGTTOU      P1990      Stop    Terminal output for background process
SIGUNUSED      -        Core    Synonymous with SIGSYS
SIGURG       P2001      Ign     Urgent condition on socket (4.2BSD)
SIGUSR1      P1990      Term    User-defined signal 1
SIGUSR2      P1990      Term    User-defined signal 2
SIGVTALRM    P2001      Term    Virtual alarm clock (4.2BSD)
SIGXCPU      P2001      Core    CPU time limit exceeded (4.2BSD);
                                see setrlimit(2)
SIGXFSZ      P2001      Core    File size limit exceeded (4.2BSD);
                                see setrlimit(2)
SIGWINCH       -        Ign     Window resize signal (4.3BSD, Sun)
```
- 其中比較常見的有：`SIGSEGV`段錯誤、除零`SIGFPE`、鍵盤輸入Ctrl+C則會觸發`SIGINT`、執行非法指令`SIGILL`、一個進程可以向另一個進程發送`SIGKILL`來終止它、一個子進程終止或者停止時，內核會發送`SIGCHILD`給父進程。
- 行為一欄有幾種：終止Term，終止並轉儲Core，停止Stop，忽略Ign。
- 每種信號類型都對應於某種系統事件，低層的硬件異常是由內核異常處理程序處理的。正常情況下，對用於進程是不可見的。信號提供了一種機制，通知用戶進程發生了這些異常。

### 信號術語

發送信號給目的進程由兩個步驟組成：
- 發送信號：內核通過更新目的進程的上下文中的某個狀態，發送一個信號給目的進程。
    - 發送信號可能有兩種原因：
    - 內核檢測到一個系統事件，比如除零錯或者子進程終止。
    - 一個進程調用了`kill`函數，顯式要求內核發送一個信號個目的進程。
- 當目的進程被內核強迫以某種方式對信號的發送做出反應時，它就接收了信號，
    - 進程可以忽略這個信號，終止，或者通過執行一個稱為信號處理程序的（signal handler）的用戶層函數捕獲這個信號。

### 發送信號

UNIX系統提供了大量向進程發送信號的機制，這些機制都基於進程組（process group）這個概念。

**進程組**：
- 每個進程只屬於一個進程組，進程組由一個正整數進程組ID標識，`getpgrp`函數返回當前進程的進程組ID。
```
NAME
       setpgid, getpgid, setpgrp, getpgrp - set/get process group

SYNOPSIS
       #include <sys/types.h>
       #include <unistd.h>

       int setpgid(pid_t pid, pid_t pgid);
       pid_t getpgid(pid_t pid);

       pid_t getpgrp(void);                 /* POSIX.1 version */
       pid_t getpgrp(pid_t pid);            /* BSD version */

       int setpgrp(void);                   /* System V version */
       int setpgrp(pid_t pid, pid_t pgid);  /* BSD version */

   Feature Test Macro Requirements for glibc (see feature_test_macros(7)):
```
- 默認一個進程和它的父進程同屬於一個進程組，可以通過`setpgrp`改變自己或其他進程進程組。

**用`/bin/kill`程序發送信號**：
- `/bin/kill`可以向另外程序發送任意信號：
```shell
/bin/kill -9 15213
```
- 將向進程`15213`發送信號`SIGKILL`（9）。
- 負的PID將導致向進程組中所有進程發送信號。

**從鍵盤發送信號**：
- Unix Shell使用作業（job）這個抽象概念表示對一條命令行求值而創建的進程。
- 在任何時刻，至多隻有一個前臺作業和0個或多個後臺作業（鍵入命令後跟`&`將會後臺運行）。
- Shell為每個作業創建一個獨立進程組，進程組ID通常取自作業中父進程的那一個。
- 鍵盤輸入Ctrl+C會導致內核發送`SIGINT`給前臺進程組中每個進程，默認情況下，結果是終止前臺作業。
- 類似地，輸入Ctrl+Z，會發送`SIGTSTP`給前臺進程組中每個進程，默認情況下，結果是掛起前臺作業。

**用`kill`函數發送信號**：
```
KILL(2)

NAME
       kill - send signal to a process

SYNOPSIS
       #include <sys/types.h>
       #include <signal.h>

       int kill(pid_t pid, int sig);
```
- 如果`pid > 0`，那麼發送信號給該進程。
- 如果`pid == 0`，那麼發送給調用進程所在進程組所有進程。
- 如果`pid < 0`，那麼發送給絕對值表示進程所在進程組所有進程。
- `man 2 kill`。

**用alarm函數發送信號**：
```
ALARM(2)

NAME
       alarm - set an alarm clock for delivery of a signal

SYNOPSIS
       #include <unistd.h>

       unsigned int alarm(unsigned int seconds);
```
- `man 2 alarm`。
- 內核安排在`seconds`秒後發送`SIGALRM`給調用進程。

### 接收信號

信號的接收：
- 當內核吧進程從內核態切換到用戶態時，會檢查進程上下文中未被阻塞的進程上下文信號結集合，如果為空，那麼將控制轉到下一條指令。如果不為空，則會選擇一個信號進行處理（通常是最小的）。
- 每個信號都有一個預定義的默認行為，是下面一種：
    - 終止。
    - 終止並轉儲內存。
    - 掛起/停止直到被`SIGCONT`信號重啟。
    - 忽略該信號。
- 進程可以通過`signal`函數修改和信號關聯的默認行為：
```
SIGNAL(2)

NAME
       signal - ANSI C signal handling

SYNOPSIS
       #include <signal.h>

       typedef void (*sighandler_t)(int);

       sighandler_t signal(int signum, sighandler_t handler);

DESCRIPTION
       The  behavior  of  signal() varies across UNIX versions, and has also varied historically across different versions of Linux.  Avoid its use: use sigaction(2) instead.  See Portability
       below.

       signal() sets the disposition of the signal signum to handler, which is either SIG_IGN, SIG_DFL, or the address of a programmer-defined function (a "signal handler").

       If the signal signum is delivered to the process, then one of the following happens:

       *  If the disposition is set to SIG_IGN, then the signal is ignored.

       *  If the disposition is set to SIG_DFL, then the default action associated with the signal (see signal(7)) occurs.

       *  If the disposition is set to a function, then first either the disposition is reset to SIG_DFL, or the signal is blocked (see Portability below), and then handler is called with ar‐
          gument signum.  If invocation of the handler caused the signal to be blocked, then the signal is unblocked upon return from the handler.

       The signals SIGKILL and SIGSTOP cannot be caught or ignored.

RETURN VALUE
       signal() returns the previous value of the signal handler, or SIG_ERR on error.  In the event of an error, errno is set to indicate the cause.
```
- 設置的這個函數稱為信號處理函數，調用信號處理程序稱為捕獲信號，執行信號處理程序稱為處理信號。
- 信號處理程序有一個參數就是信號整數值，這個參數允許同一個函數處理不同類型的信號。
- 當信號處理程序執行`return`後，控制（通常）會傳遞迴控制流中進程被信號中斷位置處的指令。

### 阻塞和解除阻塞信號

Linux提供阻塞信號的機制：
- 隱式阻塞：內核默認阻塞任何當前處理程序正在處理信號類型的待處理信號。也就是說在處理信號s過程中，不會在被此時受到的信號s中斷。
- 顯式阻塞：應用程序可以用`sigprocmask`函數和它的輔助函數，明確地阻塞和解除阻塞選定的信號。
- 見`man 2 sigprocmask`。

### 編寫信號處理程序

編寫信號處理程序通常很棘手，有幾個原因：
- 處理程序和主程序併發運行，共享同樣的全局變量，因此可能會互相干擾。
- 如何以及何時接受信號常常未被直覺。
- 不同系統由不同的信號處理語義。

安全的信號處理：
- 處理程序儘可能簡單。
- 在處理程序中只調用異步信號安全的函數，列表見`man 7 signal`，這些函數要麼是可重入的，要麼不能被信號處理程序中斷。
    - 信號處理程序中產生輸出的安全方式是`write`。
- 保存和恢復errno。
- 主程序中阻塞所有信號以保護對共享全局數據結構的訪問。
- 用`volatile`聲明全局變量，防止優化，並在訪問全局變量時阻塞信號。
- 用`sig_atomic_t`聲明全局標誌以原子讀寫。
- 上面的要求並不是任何時刻都全部必須。

正確的信號處理：
- 信號的一個與直覺不符的方面是未處理信號是不排隊的，如果有一個信號還未處理，那麼第二個到達的會被直接丟棄。這基於一個思想：如果存在未處理信號表明至少一個信號到達了。
- 舉個例子，我們可能希望父進程在等待子進程結束回收子進程前去做自己的事情，而不是等待子進程結束。那麼可以用`SIGCHLD`信號處理函數來回收子進程，但是如果有多個子進程，在收到信號但還未處理時又收到同一個信號，信號處理的次數可能就會和僵死的子進程數量不一樣，導致某些僵死子進程未被回收。那代碼中就需要解決信號不會排隊這個問題。
- **不可以用信號來對其他進程中發生的事件計數**。
- 我們可以通過在`SIGCHLD`處理程序中每次回收僵死的所有子進程解決這個問題。

可移植的信號處理：
- Unix信號處理存在一些缺陷：
    - signal函數在不同系統中語義各有不同。
    - 系統調用可以中斷。某些慢速系統調用比如`read write`可以被信號中斷，在這時，程序必須手動檢測`errno`並在被中斷時重啟系統調用代碼。
- Posix標準定義了`sigaction`函數，允許用戶設置信號處理函數時，明確指定他們想要的語義：
```C
#include <signal.h>
int sigaction(int signum, const struct sigaction *act,
                     struct sigaction *oldact);
```

### 同步流以避免討厭的併發錯誤

喜好處理是異步的，顯式的同步操作是必要的，可能需要異步編程所需要的所有措施。

### 顯式等待信號

使用循環等待顯然不是一個好主意，合適的解決方式是使用`sugsyspend`：
```
SIGSUSPEND(2)

NAME
       sigsuspend, rt_sigsuspend - wait for a signal

SYNOPSIS
       #include <signal.h>

       int sigsuspend(const sigset_t *mask);

   Feature Test Macro Requirements for glibc (see feature_test_macros(7)):

       sigsuspend(): _POSIX_C_SOURCE

DESCRIPTION
       sigsuspend()  temporarily replaces the signal mask of the calling thread with the mask given by mask and then suspends the thread until delivery of a signal whose action is to invoke a
       signal handler or to terminate a process.

       If the signal terminates the process, then sigsuspend() does not return.  If the signal is caught, then sigsuspend() returns after the signal handler returns, and the  signal  mask  is
       restored to the state before the call to sigsuspend().

       It is not possible to block SIGKILL or SIGSTOP; specifying these signals in mask, has no effect on the thread's signal mask.

RETURN VALUE
       sigsuspend() always returns -1, with errno set to indicate the error (normally, EINTR).
```

## 8.6 非本地跳轉

C語言提供了一種用戶級異常控制流形式，稱之為**非本地跳轉（nonlocal jump）**：
- 它將控制直接從一個函數轉移到另一個當前正在執行的函數，而不需要經過正常的調用-返回序列。
- 非本地跳轉通過`setjmp longjmp`實現：
```
SETJMP(3)

NAME
       setjmp, sigsetjmp, longjmp, siglongjmp  - performing a nonlocal goto

SYNOPSIS
       #include <setjmp.h>

       int setjmp(jmp_buf env);
       int sigsetjmp(sigjmp_buf env, int savesigs);

       void longjmp(jmp_buf env, int val);
       void siglongjmp(sigjmp_buf env, int val);

   Feature Test Macro Requirements for glibc (see feature_test_macros(7)):

       setjmp(): see NOTES.

       sigsetjmp(): _POSIX_C_SOURCE

DESCRIPTION
       The  functions  described on this page are used for performing "nonlocal gotos": transferring execution from one function to a predetermined location in another function.  The setjmp()
       function dynamically establishes the target to which control will later be transferred, and longjmp() performs the transfer of execution.

       The setjmp() function saves various information about the calling environment (typically, the stack pointer, the instruction pointer, possibly the values of  other  registers  and  the
       signal mask) in the buffer env for later use by longjmp().  In this case, setjmp() returns 0.

       The longjmp() function uses the information saved in env to transfer control back to the point where setjmp() was called and to restore ("rewind") the stack to its state at the time of
       the setjmp() call.  In addition, and depending on the implementation (see NOTES), the values of some other registers and the process signal mask may be restored to their state  at  the
       time of the setjmp() call.

       Following  a  successful  longjmp(),  execution  continues as if setjmp() had returned for a second time.  This "fake" return can be distinguished from a true setjmp() call because the
       "fake" return returns the value provided in val.  If the programmer mistakenly passes the value 0 in val, the "fake" return will instead return 1.

   sigsetjmp() and siglongjmp()
       sigsetjmp() and siglongjmp() also perform nonlocal gotos, but provide predictable handling of the process signal mask.

       If, and only if, the savesigs argument provided to sigsetjmp() is nonzero, the process's current signal mask is saved in env and will be restored if a siglongjmp() is  later  performed
       with this env.

RETURN VALUE
       setjmp() and sigsetjmp() return 0 when called directly; on the "fake" return that occurs after longjmp() or siglongjmp(), the nonzero value specified in val is returned.

       The longjmp() or siglongjmp() functions do not return.
```
- `setjmp`函數在`env`緩衝區中保存當前調用環境，以供後面的`longjmp`使用，並返回0。調用環境包括程序計數器、棧指針、通用目的寄存器。`setjmp`返回值不能被賦給變量。
- `longjmp`函數從`env`緩衝區中恢復調用環境，然後觸發一個從最近一次初始化`env`的`setjmp`的調用的返回。然後`setjmp`返回，並帶有非零的返回值`retval`。
- 說明：
    - `setjmp`調用一次但返回多次，第一次調用保存調用環境，然後每次`longjmp`都將返回到`setjmp`中來。
    - `longjmp`調用一次，但從不返回。
- 一個重要應用就是從深層嵌套的函數調用中立即返回，通常是檢測到某個錯誤引起，C++的異常就可以使用`setjmp longjmp`實現。
- `longjmp`允許跳過所有中間調用的特性可能產生意味後果，比如內存洩漏。
- 非本地跳轉的另一個重要應用是使一個信號處理程序分支到一個特殊的代碼位置，而不是返回被信號到達中斷了的指令的位置。
- `sigsetjmp siglongjmp`是`setjmp longjmp`的可以被信號處理程序使用的版本。
- 使用`setjmp longjmp`實現的異常機制中，`catch`類似於`setjmp`，`throw`類似於`longjmp`。

## 8.7 操作進程的工具

- `strace`：打印一個正在運行的程序和它的子進程調用的每個系統調用軌跡。
- `ps`：列出系統中的進程，包括僵死進程。
- `top`：打印出關於當前進程資源使用的信息。
- `pmap`：顯式進程的內存映射。
- `/proc`：一個虛擬文件系統，以ASCII形式輸出大量內核數據結構的內容。用戶程序可以讀取這些內容，比如`cat /proc/cpuinfo`顯式CPU信息。

## 補充資料

- 系統編程：
    - [UNIX環境高級編程](https://book.douban.com/subject/25900403/)
    - [Linux系統編程手冊](https://book.douban.com/subject/25809330/)
- 操作系統書籍：
    - [操作系統概念](https://book.douban.com/subject/30297919/)
    - [現代操作系統](https://book.douban.com/subject/27096665/)
    - [深入理解Linux內核](https://book.douban.com/subject/1230516/)
    - [操作系統——精髓與設計原理](https://book.douban.com/subject/26993995/)
- [Intel® 64 and IA-32 Architectures Software Developer’s Manual](https://cdrdv2-public.intel.com/671200/325462-sdm-vol-1-2abcd-3abcd.pdf), CHAPTER 6 PROCEDURE CALLS, INTERRUPTS, AND EXCEPTIONS。
