# GDB 除錯技巧完整指南

> 本文件整合自 100-gdb-tips 專案，包含 100+ 個 GDB 使用技巧。
> 
> 原始專案: https://github.com/hellogcc/100-gdb-tips
> 
> **注意**: 本文件已轉換為繁體中文，並統一專業術語。

---

## 目錄

- [資訊顯示](#資訊顯示)
- [函式](#函式)
- [斷點](#斷點)
- [觀察點](#觀察點)
- [Catchpoint](#Catchpoint)
- [列印](#列印)
- [多程序/執行緒](#多程序-執行緒)
- [core dump檔案](#core-dump檔案)
- [組合語言](#組合語言)
- [改變程式的執行](#改變程式的執行)
- [訊號](#訊號)
- [共享庫](#共享庫)
- [指令碼](#指令碼)
- [原始檔](#原始檔)
- [圖形化介面](#圖形化介面)
- [其它](#其它)

---

## 資訊顯示

### 顯示gdb版本資訊

## 技巧
使用gdb時，如果想檢視gdb版本資訊，可以使用“`show version`”命令:  

	(gdb) show version
	GNU gdb (GDB) 7.7.1
	Copyright (C) 2014 Free Software Foundation, Inc.
	License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
	This is free software: you are free to change and redistribute it.
	There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
	and "show warranty" for details.
	This GDB was configured as "x86_64-pc-solaris2.10".
	Type "show configuration" for configuration details.
	For bug reporting instructions, please see:
	<http://www.gnu.org/software/gdb/bugs/>.
	Find the GDB manual and other documentation resources online at:
	<http://www.gnu.org/software/gdb/documentation/>.
	For help, type "help".
	Type "apropos word" to search for commands related to "word".

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Help.html#index-GDB-version-number)。

---

### 顯示gdb版權相關資訊

## 技巧
使用gdb時，如果想檢視gdb版權相關資訊，可以使用“`show copying`”命令:  

	(gdb) show copying
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

	 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
	 Everyone is permitted to copy and distribute verbatim copies
	 of this license document, but changing it is not allowed.
	
	                            Preamble
	
	  The GNU General Public License is a free, copyleft license for
	software and other kinds of works.
	
	  The licenses for most software and other practical works are designed
	to take away your freedom to share and change the works.  By contrast,
	the GNU General Public License is intended to guarantee your freedom to
	share and change all versions of a program--to make sure it remains free
	software for all its use
	......

或者“`show warranty`”命令：

	(gdb) show warranty
	  15. Disclaimer of Warranty.
	
	  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
	APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
	HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
	OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
	THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
	PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
	IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
	ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
	
	  16. Limitation of Liability.
	
	  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
	WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
	THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
	GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
	USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
	DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
	PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
	EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
	SUCH DAMAGES.
	
	  17. Interpretation of Sections 15 and 16.
	
	  If the disclaimer of warranty and limitation of liability provided
	above cannot be given local legal effect according to their terms,
	reviewing courts shall apply local law that most closely approximates
	an absolute waiver of all civil liability in connection with the
	Program, unless a warranty or assumption of liability accompanies a
	copy of the Program in return for a fee.

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Help.html#index-GDB-version-number)。

---

### 啟動時不顯示提示資訊

## 例子

	$ gdb
	GNU gdb (GDB) 7.7.50.20140228-cvs
	Copyright (C) 2014 Free Software Foundation, Inc.
	License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
	This is free software: you are free to change and redistribute it.
	There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
	and "show warranty" for details.
	This GDB was configured as "x86_64-unknown-linux-gnu".
	Type "show configuration" for configuration details.
	For bug reporting instructions, please see:
	<http://www.gnu.org/software/gdb/bugs/>.
	Find the GDB manual and other documentation resources online at:
	<http://www.gnu.org/software/gdb/documentation/>.
	For help, type "help".
	Type "apropos word" to search for commands related to "word".

## 技巧
gdb在啟動時會顯示如上類似的提示資訊。

如果不想顯示這個資訊，則可以使用`-q`選項把提示資訊關掉:

	$ gdb -q
	(gdb)

你可以在~/.bashrc中，為gdb設定一個別名：

	alias gdb="gdb -q"

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Invoking-GDB.html#Invoking-GDB)

---

### 退出時不顯示提示資訊

## 技巧
gdb在退出時會提示:  

	A debugging session is active.

        Inferior 1 [process 29686    ] will be killed.

    Quit anyway? (y or n) n


如果不想顯示這個資訊，則可以在gdb中使用如下命令把提示資訊關掉:

	(gdb) set confirm off

也可以把這個命令加到.gdbinit檔案裡。

---

### 輸出資訊多時不會暫停輸出

## 技巧
有時當gdb輸出資訊較多時，gdb會暫停輸出，並會列印“`---Type <return> to continue, or q <return> to quit---`”這樣的提示資訊，如下面所示：  

	 81 process 2639102      0xff04af84 in __lwp_park () from /usr/lib/libc.so.1
	 80 process 2573566      0xff04af84 in __lwp_park () from /usr/lib/libc.so.1
	---Type <return> to continue, or q <return> to quit---Quit



解決辦法是使用“`set pagination off`”或者“`set height 0`”命令。這樣gdb就會全部輸出，中間不會暫停。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Screen-Size.html).

---

## 函式

### 列出函式的名字

## 例子

	#include <stdio.h>
	#include <pthread.h>
	void *thread_func(void *p_arg)
	{
	        while (1)
	        {
	                sleep(10);
	        }
	}
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread_func, "Thread 1");
	        pthread_create(&t2, NULL, thread_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}




## 技巧

使用gdb除錯時，使用“`info functions`”命令可以列出可執行檔案的所有函式名稱。以上面程式碼為例：

	(gdb) info functions
	All defined functions:
	
	File a.c:
	int main(void);
	void *thread_func(void *);
	
	Non-debugging symbols:
	0x0805079c  _PROCEDURE_LINKAGE_TABLE_
	0x080507ac  _cleanup@plt
	0x080507bc  atexit
	0x080507bc  atexit@plt
	0x080507cc  __fpstart
	0x080507cc  __fpstart@plt
	0x080507dc  exit@plt
	0x080507ec  __deregister_frame_info_bases@plt
	0x080507fc  __register_frame_info_bases@plt
	0x0805080c  _Jv_RegisterClasses@plt
	0x0805081c  sleep
	0x0805081c  sleep@plt
	0x0805082c  pthread_create@plt
	0x0805083c  _start
	0x080508b4  _mcount
	0x080508b8  __do_global_dtors_aux
	0x08050914  frame_dummy
	0x080509f4  __do_global_ctors_aux
	0x08050a24  _init
	0x08050a31  _fini

	
可以看到會列出函式原型以及不帶除錯資訊的函式。

另外這個命令也支援正則表示式：“`info functions regex`”，這樣只會列出符合正則表示式的函式名稱，例如：

	(gdb) info functions thre*
	All functions matching regular expression "thre*":
	
	File a.c:
	void *thread_func(void *);
	
	Non-debugging symbols:
	0x0805082c  pthread_create@plt




可以看到gdb只會列出名字裡包含“`thre`”的函式。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Symbols.html)

---

### 是否進入帶除錯資訊的函式

## 例子

	#include <stdio.h>

	int func(void)
	{
		return 3;
	}
	
	int main(void)
	{
		int a = 0;
		
		a = func();
		printf("%d\n", a);
		return 0;
	}



## 技巧

使用gdb除錯遇到函式時，使用step命令（縮寫為s）可以進入函式（函式必須有除錯資訊）。以上面程式碼為例：

	(gdb) n
	12              a = func();
	(gdb) s
	func () at a.c:5
	5               return 3;
	(gdb) n
	6       }
	(gdb)
	main () at a.c:13
	13              printf("%d\n", a);

	
可以看到gdb進入了func函式。

可以使用next命令（縮寫為n）不進入函式，gdb會等函式執行完，再顯示下一行要執行的程式程式碼：

	(gdb) n
	12              a = func();
	(gdb) n
	13              printf("%d\n", a);
	(gdb) n
	3
	14              return 0;



可以看到gdb沒有進入func函式。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Continuing-and-Stepping.html)

---

### 進入不帶除錯資訊的函式

## 例子

	#include <stdio.h>
	#include <pthread.h>
	
	typedef struct
	{
	        int a;
	        int b;
	        int c;
	        int d;
	        pthread_mutex_t mutex;
	}ex_st;
	
	int main(void) {
	        ex_st st = {1, 2, 3, 4, PTHREAD_MUTEX_INITIALIZER};
	        printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	        return 0;
	}



## 技巧

預設情況下，gdb不會進入不帶除錯資訊的函式。以上面程式碼為例：

	(gdb) n
	15              printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	(gdb) s
	1,2,3,4
	16              return 0;

	
可以看到由於printf函式不帶除錯資訊，所以“s”命令（s是“step”縮寫）無法進入printf函式。

可以執行“set step-mode on”命令，這樣gdb就不會跳過沒有除錯資訊的函式：

	(gdb) set step-mode on
	(gdb) n
	15              printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	(gdb) s
	0x00007ffff7a993b0 in printf () from /lib64/libc.so.6
	(gdb) s
	0x00007ffff7a993b7 in printf () from /lib64/libc.so.6


可以看到gdb進入了printf函式，接下來可以使用除錯組合語言程式的辦法去除錯函式。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Continuing-and-Stepping.html)

---

### 退出正在除錯的函式

## 例子

	#include <stdio.h>

	int func(void)
	{
	    int i = 0;
	
	    i += 2;
	    i *= 10;
	
	    return i;
	}
	
	int main(void)
	{
	    int a = 0;
	
	    a = func();
	    printf("%d\n", a);
	    return 0;
	}



## 技巧

當單步除錯一個函式時，如果不想繼續跟蹤下去了，可以有兩種方式退出。

第一種用“`finish`”命令，這樣函式會繼續執行完，並且列印返回值，然後等待輸入接下來的命令。以上面程式碼為例：

	(gdb) n
	17          a = func();
	(gdb) s
	func () at a.c:5
	5               int i = 0;
	(gdb) n
	7               i += 2;
	(gdb) fin
	find    finish
	(gdb) finish
	Run till exit from #0  func () at a.c:7
	0x08050978 in main () at a.c:17
	17          a = func();
	Value returned is $1 = 20

	
可以看到當不想再繼續跟蹤`func`函式時，執行完“`finish`”命令，gdb會列印結果：“`20`”，然後停在那裡。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Continuing-and-Stepping.html)

第二種用“`return`”命令，這樣函式不會繼續執行下面的語句，而是直接返回。也可以用“`return expression`”命令指定函式的返回值。仍以上面程式碼為例：

	(gdb) n
	17          a = func();
	(gdb) s
	func () at a.c:5
	5               int i = 0;
	(gdb) n
	7               i += 2;
	(gdb) n
	8               i *= 10;
	(gdb) re
	record              remove-inferiors    return              reverse-next        reverse-step
	refresh             remove-symbol-file  reverse-continue    reverse-nexti       reverse-stepi
	remote              restore             reverse-finish      reverse-search
	(gdb) return 40
	Make func return now? (y or n) y
	#0  0x08050978 in main () at a.c:17
	17          a = func();
	(gdb) n
	18          printf("%d\n", a);
	(gdb)
	40
	19          return 0;



可以看到“`return`”命令退出了函式並且修改了函式的返回值。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Returning.html#Returning)

---

### 直接執行函式

## 例子
	#include <stdio.h>

	int global = 1;
	
	int func(void) 
	{
		return (++global);
	}
	
	int main(void)
	{
		printf("%d\n", global);
		return 0;
	}



## 技巧
使用gdb除錯程式時，可以使用“`call`”或“`print`”命令直接呼叫函式執行。以上面程式為例：  
 
	(gdb) start
	Temporary breakpoint 1 at 0x4004e3: file a.c, line 12.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:12
	12              printf("%d\n", global);
	(gdb) call func()
	$1 = 2
	(gdb) print func()
	$2 = 3
	(gdb) n
	3
	13              return 0;

可以看到執行兩次`func`函式後，`global`的值變成`3`。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Calling.html).

---

### 列印函式堆疊幀資訊

## 例子
	#include <stdio.h>
	int func(int a, int b)
	{
		int c = a * b;
		printf("c is %d\n", c);
	}
	
	int main(void) 
	{
		func(1, 2);
		return 0;
	}



## 技巧
使用gdb除錯程式時，可以使用“`i frame`”命令（`i`是`info`命令縮寫）顯示函式堆疊幀資訊。以上面程式為例：  
 
	Breakpoint 1, func (a=1, b=2) at a.c:5
	5               printf("c is %d\n", c);
	(gdb) i frame
	Stack level 0, frame at 0x7fffffffe590:
	 rip = 0x40054e in func (a.c:5); saved rip = 0x400577
	 called by frame at 0x7fffffffe5a0
	 source language c.
	 Arglist at 0x7fffffffe580, args: a=1, b=2
	 Locals at 0x7fffffffe580, Previous frame's sp is 0x7fffffffe590
	 Saved registers:
	  rbp at 0x7fffffffe580, rip at 0x7fffffffe588
	(gdb) i registers
	rax            0x2      2
	rbx            0x0      0
	rcx            0x0      0
	rdx            0x7fffffffe688   140737488348808
	rsi            0x2      2
	rdi            0x1      1
	rbp            0x7fffffffe580   0x7fffffffe580
	rsp            0x7fffffffe560   0x7fffffffe560
	r8             0x7ffff7dd4e80   140737351863936
	r9             0x7ffff7dea560   140737351951712
	r10            0x7fffffffe420   140737488348192
	r11            0x7ffff7a35dd0   140737348066768
	r12            0x400440 4195392
	r13            0x7fffffffe670   140737488348784
	r14            0x0      0
	r15            0x0      0
	rip            0x40054e 0x40054e <func+24>
	eflags         0x202    [ IF ]
	cs             0x33     51
	ss             0x2b     43
	ds             0x0      0
	es             0x0      0
	fs             0x0      0
	gs             0x0      0
	(gdb) disassemble func
	Dump of assembler code for function func:
	   0x0000000000400536 <+0>:     push   %rbp
	   0x0000000000400537 <+1>:     mov    %rsp,%rbp
	   0x000000000040053a <+4>:     sub    $0x20,%rsp
	   0x000000000040053e <+8>:     mov    %edi,-0x14(%rbp)
	   0x0000000000400541 <+11>:    mov    %esi,-0x18(%rbp)
	   0x0000000000400544 <+14>:    mov    -0x14(%rbp),%eax
	   0x0000000000400547 <+17>:    imul   -0x18(%rbp),%eax
	   0x000000000040054b <+21>:    mov    %eax,-0x4(%rbp)
	=> 0x000000000040054e <+24>:    mov    -0x4(%rbp),%eax
	   0x0000000000400551 <+27>:    mov    %eax,%esi
	   0x0000000000400553 <+29>:    mov    $0x400604,%edi
	   0x0000000000400558 <+34>:    mov    $0x0,%eax
	   0x000000000040055d <+39>:    callq  0x400410 <printf@plt>
	   0x0000000000400562 <+44>:    leaveq
	   0x0000000000400563 <+45>:    retq
	End of assembler dump.

可以看到執行“`i frame`”命令後，輸出了當前函式堆疊幀的地址，指令暫存器的值，區域性變數地址及值等資訊，可以對照當前暫存器的值和函式的組合語言指令看一下。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Frame-Info.html).

---

### 列印尾呼叫堆疊幀資訊

## 例子
	#include<stdio.h>
	void a(void)
	{
	        printf("Tail call frame\n");
	}
	
	void b(void)
	{
	        a();
	}
	
	void c(void)
	{
	        b();
	}
	
	int main(void)
	{
	        c();
	        return 0;
	}

## 技巧
當一個函式最後一條指令是呼叫另外一個函式時，開啟最佳化選項的編譯器常常以最後被呼叫的函式返回值作為呼叫者的返回值，這稱之為“尾呼叫（Tail call）”。以上面程式為例，編譯程式（使用‘-O’）：  

    gcc -g -O -o test test.c
檢視`main`函式組合語言程式碼：

	(gdb) disassemble main
    Dump of assembler code for function main:
    0x0000000000400565 <+0>:     sub    $0x8,%rsp
    0x0000000000400569 <+4>:     callq  0x400536 <a>
    0x000000000040056e <+9>:     mov    $0x0,%eax
    0x0000000000400573 <+14>:    add    $0x8,%rsp
    0x0000000000400577 <+18>:    retq
可以看到`main`函式直接呼叫了函式`a`，根本看不到函式`b`和函式`c`的影子。
  
在函式`a`入口處打上斷點，程式停止後，列印堆疊幀資訊：  

	(gdb) i frame
	Stack level 0, frame at 0x7fffffffe590:
	 rip = 0x400536 in a (test.c:4); saved rip = 0x40056e
	 called by frame at 0x7fffffffe5a0
	 source language c.
	 Arglist at 0x7fffffffe580, args:
	 Locals at 0x7fffffffe580, Previous frame's sp is 0x7fffffffe590
	 Saved registers:
	  rip at 0x7fffffffe588
看不到尾呼叫的相關資訊。  

可以設定“`debug entry-values`”選項為非0的值，這樣除了輸出正常的函式堆疊幀資訊以外，還可以輸出尾呼叫的相關資訊：  

	(gdb) set debug entry-values 1
	(gdb) b test.c:4
	Breakpoint 1 at 0x400536: file test.c, line 4.
	(gdb) r
	Starting program: /home/nanxiao/test
	
	Breakpoint 1, a () at test.c:4
	4       {
	(gdb) i frame
	tailcall: initial:
	Stack level 0, frame at 0x7fffffffe590:
	 rip = 0x400536 in a (test.c:4); saved rip = 0x40056e
	 called by frame at 0x7fffffffe5a0
	 source language c.
	 Arglist at 0x7fffffffe580, args:
	 Locals at 0x7fffffffe580, Previous frame's sp is 0x7fffffffe590
	 Saved registers:
	  rip at 0x7fffffffe588

可以看到輸出了“`tailcall: initial:`”資訊。  

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Tail-Call-Frames.html).

---

### 選擇函式堆疊幀

## 例子
	#include <stdio.h>

	int func1(int a)
	{
	        return 2 * a;
	}
	
	int func2(int a)
	{
	        int c = 0;
	        c = 2 * func1(a);
	        return c;
	}
	
	int func3(int a)
	{
	        int c = 0;
	        c = 2 * func2(a);
	        return c;
	}
	
	int main(void)
	{
	        printf("%d\n", func3(10));
	        return 0;
	}

## 技巧
用gdb除錯程式時，當程式暫停後，可以用“`frame n`”命令選擇函式堆疊幀，其中`n`是層數。以上面程式為例：  

    (gdb) b test.c:5
	Breakpoint 1 at 0x40053d: file test.c, line 5.
	(gdb) r
	Starting program: /home/nanxiao/test
	
	Breakpoint 1, func1 (a=10) at test.c:5
	5               return 2 * a;
	(gdb) bt
	#0  func1 (a=10) at test.c:5
	#1  0x0000000000400560 in func2 (a=10) at test.c:11
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	#3  0x000000000040059e in main () at test.c:24
	(gdb) frame 2
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	18              c = 2 * func2(a);

可以看到程式斷住後，最內層的函式幀為第`0`幀。執行`frame 2`命令後，當前的堆疊幀變成了`fun3`的函式幀。

也可以用“`frame addr`”命令選擇函式堆疊幀，其中`addr`是堆疊地址。仍以上面程式為例：  

    (gdb) frame 2
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	18              c = 2 * func2(a);
	(gdb) i frame
	Stack level 2, frame at 0x7fffffffe590:
	 rip = 0x400586 in func3 (test.c:18); saved rip = 0x40059e
	 called by frame at 0x7fffffffe5a0, caller of frame at 0x7fffffffe568
	 source language c.
	 Arglist at 0x7fffffffe580, args: a=10
	 Locals at 0x7fffffffe580, Previous frame's sp is 0x7fffffffe590
	 Saved registers:
	  rbp at 0x7fffffffe580, rip at 0x7fffffffe588
	(gdb) frame 0x7fffffffe568
	#1  0x0000000000400560 in func2 (a=10) at test.c:11
	11              c = 2 * func1(a);
使用“`i frame`”命令可以知道`0x7fffffffe568`是`func2`的函式堆疊幀地址，使用“`frame 0x7fffffffe568`”可以切換到`func2`的函式堆疊幀。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Selection.html#Selection).

---

### 向上或向下切換函式堆疊幀

## 例子
	#include <stdio.h>

	int func1(int a)
	{
	        return 2 * a;
	}
	
	int func2(int a)
	{
	        int c = 0;
	        c = 2 * func1(a);
	        return c;
	}
	
	int func3(int a)
	{
	        int c = 0;
	        c = 2 * func2(a);
	        return c;
	}
	
	int main(void)
	{
	        printf("%d\n", func3(10));
	        return 0;
	}

## 技巧
用gdb除錯程式時，當程式暫停後，可以用“`up n`”或“`down n`”命令向上或向下選擇函式堆疊幀，其中`n`是層數。以上面程式為例：  

    (gdb) b test.c:5
	Breakpoint 1 at 0x40053d: file test.c, line 5.
	(gdb) r
	Starting program: /home/nanxiao/test
	
	Breakpoint 1, func1 (a=10) at test.c:5
	5               return 2 * a;
	(gdb) bt
	#0  func1 (a=10) at test.c:5
	#1  0x0000000000400560 in func2 (a=10) at test.c:11
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	#3  0x000000000040059e in main () at test.c:24
	(gdb) frame 2
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	18              c = 2 * func2(a);
	(gdb) up 1
	#3  0x000000000040059e in main () at test.c:24
	24              printf("%d\n", func3(10));
	(gdb) down 2
	#1  0x0000000000400560 in func2 (a=10) at test.c:11
	11              c = 2 * func1(a);


可以看到程式斷住後，先執行“`frame 2`”命令，切換到`fun3`函式。接著執行“`up 1`”命令，此時會切換到`main`函式，也就是會往外層的堆疊幀移動一層。反之，當執行“`down 2`”命令後，又會向內層堆疊幀移動二層。如果不指定`n`，則`n`預設為`1`.

還有“`up-silently n`”和“`down-silently n`”這兩個命令，與“`up n`”和“`down n`”命令區別在於，切換堆疊幀後，不會列印資訊，仍以上面程式為例：  

    (gdb) up
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	18              c = 2 * func2(a);
	(gdb) bt
	#0  func1 (a=10) at test.c:5
	#1  0x0000000000400560 in func2 (a=10) at test.c:11
	#2  0x0000000000400586 in func3 (a=10) at test.c:18
	#3  0x000000000040059e in main () at test.c:24
	(gdb) up-silently
	(gdb) i frame
	Stack level 3, frame at 0x7fffffffe5a0:
	 rip = 0x40059e in main (test.c:24); saved rip = 0x7ffff7a35ec5
	 caller of frame at 0x7fffffffe590
	 source language c.
	 Arglist at 0x7fffffffe590, args:
	 Locals at 0x7fffffffe590, Previous frame's sp is 0x7fffffffe5a0
	 Saved registers:
	  rbp at 0x7fffffffe590, rip at 0x7fffffffe598

可以看到從`func3`切換到`main`函式堆疊幀時，並沒有打印出相關資訊。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Selection.html#Selection).

---

## 斷點

### 在匿名空間設定斷點

## 例子
	namespace Foo
	{
	  void foo()
	  {
	  }
	}

	namespace
	{
	  void bar()
	  {
	  }
	}

## 技巧

可以先使用檢視所有函式資訊，這樣便於理解，使用如下命令：

	(gdb) info functions                                                                                                                   
	All defined functions:                                                                                                                 

	File test.cpp:
	3:      void Foo::foo();
	10:     static void (anonymous namespace)::bar();

在gdb中，如果要對namespace Foo中的foo函式設定斷點，可以使用如下命令：

	(gdb) b Foo::foo

如果要對匿名空間中的bar函式設定斷點，可以使用如下命令：

	(gdb) b (anonymous namespace)::bar

---

### 在程式地址上打斷點

## 例子

	0000000000400522 <main>:
	  400522:       55                      push   %rbp
	  400523:       48 89 e5                mov    %rsp,%rbp
	  400526:       8b 05 00 1b 00 00       mov    0x1b00(%rip),%eax        # 40202c <he+0xc>
	  40052c:       85 c0                   test   %eax,%eax
	  40052e:       75 07                   jne    400537 <main+0x15>
	  400530:       b8 7c 06 40 00          mov    $0x40067c,%eax
	  400535:       eb 05                   jmp    40053c <main+0x1a>

## 技巧

當除錯組合語言程式，或者沒有除錯資訊的程式時，經常需要在程式地址上打斷點，方法為`b *address`。例如：

	(gdb) b *0x400522

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Specify-Location.html#Specify-Location)

---

### 在程式入口處打斷點

## 獲取程式入口

### 方法一：

	$ strip a.out
	$ readelf -h a.out 
	ELF Header:
	  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
	  Class:                             ELF64
	  Data:                              2's complement, little endian
	  Version:                           1 (current)
	  OS/ABI:                            UNIX - System V
	  ABI Version:                       0
	  Type:                              EXEC (Executable file)
	  Machine:                           Advanced Micro Devices X86-64
	  Version:                           0x1
	  Entry point address:               0x400440
	  Start of program headers:          64 (bytes into file)
	  Start of section headers:          4496 (bytes into file)
	  Flags:                             0x0
	  Size of this header:               64 (bytes)
	  Size of program headers:           56 (bytes)
	  Number of program headers:         9
	  Size of section headers:           64 (bytes)
	  Number of section headers:         29
	  Section header string table index: 28

### 方法二：

    $ gdb a.out 
    >>> info files
    Symbols from "/home/me/a.out".
    Local exec file:
    	`/home/me/a.out', file type elf64-x86-64.
    	Entry point: 0x400440
    	0x0000000000400238 - 0x0000000000400254 is .interp
    	0x0000000000400254 - 0x0000000000400274 is .note.ABI-tag
    	0x0000000000400274 - 0x0000000000400298 is .note.gnu.build-id
    	0x0000000000400298 - 0x00000000004002b4 is .gnu.hash
    	0x00000000004002b8 - 0x0000000000400318 is .dynsym
    	0x0000000000400318 - 0x0000000000400355 is .dynstr
    	0x0000000000400356 - 0x000000000040035e is .gnu.version
    	0x0000000000400360 - 0x0000000000400380 is .gnu.version_r
    	0x0000000000400380 - 0x0000000000400398 is .rela.dyn
    	0x0000000000400398 - 0x00000000004003e0 is .rela.plt
    	0x00000000004003e0 - 0x00000000004003fa is .init
    	0x0000000000400400 - 0x0000000000400440 is .plt
    	0x0000000000400440 - 0x00000000004005c2 is .text
    	0x00000000004005c4 - 0x00000000004005cd is .fini
    	0x00000000004005d0 - 0x00000000004005e0 is .rodata
    	0x00000000004005e0 - 0x0000000000400614 is .eh_frame_hdr
    	0x0000000000400618 - 0x000000000040070c is .eh_frame
    	0x0000000000600e10 - 0x0000000000600e18 is .init_array
    	0x0000000000600e18 - 0x0000000000600e20 is .fini_array
    	0x0000000000600e20 - 0x0000000000600e28 is .jcr
    	0x0000000000600e28 - 0x0000000000600ff8 is .dynamic
    	0x0000000000600ff8 - 0x0000000000601000 is .got
    	0x0000000000601000 - 0x0000000000601030 is .got.plt
    	0x0000000000601030 - 0x0000000000601040 is .data
    	0x0000000000601040 - 0x0000000000601048 is .bss

## 技巧

當除錯沒有除錯資訊的程式時，直接執行`start`命令是沒有效果的：

	(gdb) start
	Function "main" not defined.

如果不知道main在何處，那麼可以在程式入口處打斷點。先透過`readelf`或者進入gdb，執行`info files`獲得入口地址，然後：

	(gdb) b *0x400440
	(gdb) r

---

### 在檔案行號上打斷點

## 例子

	/* a/file.c */
	#include <stdio.h>
	
	void print_a (void)
	{
	  puts ("a");
	}
	
	/* b/file.c */
	#include <stdio.h>
	
	void print_b (void)
	{
	  puts ("b");
	}
	
	/* main.c */
	extern void print_a(void);
	extern void print_b(void);
	
	int main(void)
	{
	  print_a();
	  print_b();
	  return 0;
	}

## 技巧

這個比較簡單，如果要在當前檔案中的某一行打斷點，直接`b linenum`即可，例如：

	(gdb) b 7

也可以顯式指定檔案，`b file:linenum`例如：

	(gdb) b file.c:6
	Breakpoint 1 at 0x40053b: file.c:6. (2 locations)
	(gdb) i breakpoints 
	Num     Type           Disp Enb Address            What
	1       breakpoint     keep y   <MULTIPLE>         
	1.1                         y     0x000000000040053b in print_a at a/file.c:6
	1.2                         y     0x000000000040054b in print_b at b/file.c:6

可以看出，gdb會對所有匹配的檔案設定斷點。你可以透過指定（部分）路徑，來區分相同的檔名：

	(gdb) b a/file.c:6

注意：透過行號進行設定斷點的一個弊端是，如果你更改了源程式，那麼之前設定的斷點就可能不是你想要的了。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Specify-Location.html#Specify-Location)

---

### 儲存已經設定的斷點

## 例子

	$ gdb -q `which gdb`
	Reading symbols from /home/xmj/install/binutils-trunk/bin/gdb...done.
	(gdb) b gdb_main
	Breakpoint 1 at 0x5a7af0: file /home/xmj/project/binutils-trunk/gdb/main.c, line 1061.
	(gdb) b captured_main
	Breakpoint 2 at 0x5a6bd0: file /home/xmj/project/binutils-trunk/gdb/main.c, line 310.
	(gdb) b captured_command_loop
	Breakpoint 3 at 0x5a68b0: file /home/xmj/project/binutils-trunk/gdb/main.c, line 261.

## 技巧

在gdb中，可以使用如下命令將設定的斷點儲存下來：

<pre><code>(gdb) save breakpoints <i>file-name-to-save</i></code></pre>

下此除錯時，可以使用如下命令批次設定儲存的斷點：

<pre><code>(gdb) source <i>file-name-to-save</i></code></pre>

	(gdb) info breakpoints 
	Num     Type           Disp Enb Address            What
	1       breakpoint     keep y   0x00000000005a7af0 in gdb_main at /home/xmj/project/binutils-trunk/gdb/main.c:1061
	2       breakpoint     keep y   0x00000000005a6bd0 in captured_main at /home/xmj/project/binutils-trunk/gdb/main.c:310
	3       breakpoint     keep y   0x00000000005a68b0 in captured_command_loop at /home/xmj/project/binutils-trunk/gdb/main.c:261

詳情參見[gdb手冊](https://sourceware.org/gdb/download/onlinedocs/gdb/Save-Breakpoints.html#Save-Breakpoints)

---

### 設定臨時斷點

## 例子

	#include <stdio.h>
	#include <pthread.h>
	
	typedef struct
	{
	        int a;
	        int b;
	        int c;
	        int d;
	        pthread_mutex_t mutex;
	}ex_st;
	
	int main(void) {
	        ex_st st = {1, 2, 3, 4, PTHREAD_MUTEX_INITIALIZER};
	        printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	        return 0;
	}



## 技巧

在使用gdb時，如果想讓斷點只生效一次，可以使用“tbreak”命令（縮寫為：tb）。以上面程式為例：

	(gdb) tb a.c:15
	Temporary breakpoint 1 at 0x400500: file a.c, line 15.
	(gdb) i b
	Num     Type           Disp Enb Address            What
	1       breakpoint     del  y   0x0000000000400500 in main at a.c:15
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:15
	15              printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	(gdb) i b
	No breakpoints or watchpoints.

	


首先在檔案的第15行設定臨時斷點，當程式斷住後，用“i b”（"info breakpoints"縮寫）命令檢視斷點，發現斷點沒有了。也就是斷點命中一次後，就被刪掉了。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Breaks.html)

---

### 設定條件斷點

## 例子

	#include <stdio.h>
		
	int main(void)
	{
	        int i = 0;
			int sum = 0;

			for (i = 1; i <= 200; i++)
			{
				sum += i;
			}
		
			printf("%d\n", sum);
	        return 0;
	}



## 技巧

gdb可以設定條件斷點，也就是隻有在條件滿足時，斷點才會被觸發，命令是“`break … if cond`”。以上面程式為例：

	(gdb) start
	Temporary breakpoint 1 at 0x4004cc: file a.c, line 5.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:5
	5                       int i = 0;
	(gdb) b 10 if i==101
	Breakpoint 2 at 0x4004e3: file a.c, line 10.
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	
	Breakpoint 2, main () at a.c:10
	10                                      sum += i;
	(gdb) p sum
	$1 = 5050

可以看到設定斷點只在`i`的值為`101`時觸發，此時列印`sum`的值為`5050`。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Breaks.html)

---

### 忽略斷點

## 例子

	#include <stdio.h>
		
	int main(void)
	{
	        int i = 0;
			int sum = 0;

			for (i = 1; i <= 200; i++)
			{
				sum += i;
			}
		
			printf("%d\n", sum);
	        return 0;
	}



## 技巧

在設定斷點以後，可以忽略斷點，命令是“`ignore bnum count`”：意思是接下來`count`次編號為`bnum`的斷點觸發都不會讓程式中斷，只有第`count + 1`次斷點觸發才會讓程式中斷。以上面程式為例：

	(gdb) b 10
	Breakpoint 1 at 0x4004e3: file a.c, line 10.
	(gdb) ignore 1 5
	Will ignore next 5 crossings of breakpoint 1.
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	
	Breakpoint 1, main () at a.c:10
	10                                      sum += i;
	(gdb) p i
	$1 = 6


可以看到設定忽略斷點前`5`次觸發後，第一次斷點斷住時，列印`i`的值是`6`。如果想讓斷點下次就生效，可以將`count`置為`0`：“`ignore 1 0`”。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Conditions.html)

---

## 觀察點

### 設定觀察點

## 例子
	#include <stdio.h>
	#include <pthread.h>
	#include <unistd.h>
	int a = 0;

	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}

	int main(int argc, char* argv[])
	{
	        pthread_t t1;
	        pthread_create(&t1, NULL, thread1_func, NULL);

	        sleep(1000);
	        return 0;
	}

## 技巧
gdb可以使用“`watch`”命令設定觀察點，也就是當一個變數值發生變化時，程式會停下來。以上面程式為例:

	(gdb) start
	Temporary breakpoint 1 at 0x4005a8: file a.c, line 19.
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".

	Temporary breakpoint 1, main () at a.c:19
	19              pthread_create(&t1, NULL, thread1_func, "Thread 1");
	(gdb) watch a
	Hardware watchpoint 2: a
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	[New Thread 0x7ffff782c700 (LWP 8813)]
	[Switching to Thread 0x7ffff782c700 (LWP 8813)]
	Hardware watchpoint 2: a

	Old value = 0
	New value = 1
	thread1_func (p_arg=0x4006d8) at a.c:11
	11                      sleep(10);
	(gdb) c
	Continuing.
	Hardware watchpoint 2: a

	Old value = 1
	New value = 2
	thread1_func (p_arg=0x4006d8) at a.c:11
	11                      sleep(10);

可以看到，使用“`watch a`”命令以後，當`a`的值變化：由`0`變成`1`，由`1`變成`2`，程式都會停下來。
此外也可以使用“`watch *(data type*)address`”這樣的命令，仍以上面程式為例:

	(gdb) p &a
	$1 = (int *) 0x6009c8 <a>
	(gdb) watch *(int*)0x6009c8
	Hardware watchpoint 2: *(int*)0x6009c8
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	[New Thread 0x7ffff782c700 (LWP 15431)]
	[Switching to Thread 0x7ffff782c700 (LWP 15431)]
	Hardware watchpoint 2: *(int*)0x6009c8

	Old value = 0
	New value = 1
	thread1_func (p_arg=0x4006d8) at a.c:11
	11                      sleep(10);
	(gdb) c
	Continuing.
	Hardware watchpoint 2: *(int*)0x6009c8

	Old value = 1
	New value = 2
	thread1_func (p_arg=0x4006d8) at a.c:11
	11                      sleep(10);

先得到`a`的地址：`0x6009c8`，接著用“`watch *(int*)0x6009c8`”設定觀察點，可以看到同“`watch a`”命令效果一樣。
觀察點可以透過軟體或硬體的方式實現，取決於具體的系統。但是軟體實現的觀察點會導致程式執行很慢，使用時需注意。參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Watchpoints.html).

如果系統支援硬體觀測的話，當設定觀測點是會列印如下資訊：
	Hardware watchpoint num: expr

 如果不想用硬體觀測點的話可如下設定：
    set can-use-hw-watchpoints

## 檢視斷點
列出當前所設定了的所有觀察點：
info watchpoints

watch 所設定的斷點也可以用控制斷點的命令來控制。如 disable、enable、delete等

---

### 設定觀察點只針對特定執行緒生效

## 例子
	#include <stdio.h>
	#include <pthread.h>
	
	int a = 0;
	
	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}
	
	void *thread2_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}
	
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread1_func, "Thread 1");
			pthread_create(&t2, NULL, thread2_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}

## 技巧
gdb可以使用“`watch expr thread threadnum`”命令設定觀察點只針對特定執行緒生效，也就是隻有編號為`threadnum`的執行緒改變了變數的值，程式才會停下來，其它編號執行緒改變變數的值不會讓程式停住。以上面程式為例:  

	(gdb) start
	Temporary breakpoint 1 at 0x4005d4: file a.c, line 28.
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	
	Temporary breakpoint 1, main () at a.c:28
	28              pthread_create(&t1, NULL, thread1_func, "Thread 1");
	(gdb) n
	[New Thread 0x7ffff782c700 (LWP 25443)]
	29              pthread_create(&t2, NULL, thread2_func, "Thread 2");
	(gdb)
	[New Thread 0x7ffff6e2b700 (LWP 25444)]
	31              sleep(1000);
	(gdb) i threads
	  Id   Target Id         Frame
	  3    Thread 0x7ffff6e2b700 (LWP 25444) 0x00007ffff7915911 in clone () from /lib64/libc.so.6
	  2    Thread 0x7ffff782c700 (LWP 25443) 0x00007ffff78d9bcd in nanosleep () from /lib64/libc.so.6
	* 1    Thread 0x7ffff7fe9700 (LWP 25413) main () at a.c:31
	(gdb) wa a thread 2
	Hardware watchpoint 2: a
	(gdb) c
	Continuing.
	[Switching to Thread 0x7ffff782c700 (LWP 25443)]
	Hardware watchpoint 2: a
	
	Old value = 1
	New value = 3
	thread1_func (p_arg=0x400718) at a.c:11
	11                      sleep(10);
	(gdb) c
	Continuing.
	Hardware watchpoint 2: a
	
	Old value = 3
	New value = 5
	thread1_func (p_arg=0x400718) at a.c:11
	11                      sleep(10);
	(gdb) c
	Continuing.
	Hardware watchpoint 2: a
	
	Old value = 5
	New value = 7
	thread1_func (p_arg=0x400718) at a.c:11
	11                      sleep(10);


可以看到，使用“`wa a thread 2`”命令（`wa`是`watch`命令的縮寫）以後，只有`thread1_func`改變`a`的值才會讓程式停下來。  
需要注意的是這種針對特定執行緒設定觀察點方式只對硬體觀察點才生效，參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Watchpoints.html).

---

### 設定讀觀察點

## 例子
	#include <stdio.h>
	#include <pthread.h>
	
	int a = 0;
	
	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                printf("%d\n", a);
	                sleep(10);
	        }
	}
	
	int main(void)
	{
	        pthread_t t1;
	
	        pthread_create(&t1, NULL, thread1_func, "Thread 1");
	
	        sleep(1000);
	        return;
	}


## 技巧
gdb可以使用“`rwatch`”命令設定讀觀察點，也就是當發生讀取變數行為時，程式就會暫停住。以上面程式為例:  

	(gdb) start
	Temporary breakpoint 1 at 0x4005f3: file a.c, line 19.
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	
	Temporary breakpoint 1, main () at a.c:19
	19              pthread_create(&t1, NULL, thread1_func, "Thread 1");
	(gdb) rw a
	Hardware read watchpoint 2: a
	(gdb) c
	Continuing.
	[New Thread 0x7ffff782c700 (LWP 5540)]
	[Switching to Thread 0x7ffff782c700 (LWP 5540)]
	Hardware read watchpoint 2: a
	
	Value = 0
	0x00000000004005c6 in thread1_func (p_arg=0x40071c) at a.c:10
	10                      printf("%d\n", a);
	(gdb) c
	Continuing.
	0
	Hardware read watchpoint 2: a
	
	Value = 0
	0x00000000004005c6 in thread1_func (p_arg=0x40071c) at a.c:10
	10                      printf("%d\n", a);
	(gdb) c
	Continuing.
	0
	Hardware read watchpoint 2: a
	
	Value = 0
	0x00000000004005c6 in thread1_func (p_arg=0x40071c) at a.c:10
	10                      printf("%d\n", a);



可以看到，使用“`rw a`”命令（`rw`是`rwatch`命令的縮寫）以後，每次訪問`a`的值都會讓程式停下來。  
需要注意的是`rwatch`命令只對硬體觀察點才生效，參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Watchpoints.html).

---

### 設定讀寫觀察點

## 例子
	#include <stdio.h>
	#include <pthread.h>
	
	int a = 0;
	
	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}
	
	void *thread2_func(void *p_arg)
	{
	        while (1)
	        {
	                printf("%d\n", a);;
	                sleep(10);
	        }
	}
	
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread1_func, "Thread 1");
	        pthread_create(&t2, NULL, thread2_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}

## 技巧
gdb可以使用“`awatch`”命令設定讀寫觀察點，也就是當發生讀取變數或改變變數值的行為時，程式就會暫停住。以上面程式為例:  

	(gdb) aw a
	Hardware access (read/write) watchpoint 1: a
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	[New Thread 0x7ffff782c700 (LWP 16938)]
	[Switching to Thread 0x7ffff782c700 (LWP 16938)]
	Hardware access (read/write) watchpoint 1: a
	
	Value = 0
	0x00000000004005c6 in thread1_func (p_arg=0x40076c) at a.c:10
	10                      a++;
	(gdb) c
	Continuing.
	Hardware access (read/write) watchpoint 1: a
	
	Old value = 0
	New value = 1
	thread1_func (p_arg=0x40076c) at a.c:11
	11                      sleep(10);
	(gdb) c
	Continuing.
	[New Thread 0x7ffff6e2b700 (LWP 16939)]
	[Switching to Thread 0x7ffff6e2b700 (LWP 16939)]
	Hardware access (read/write) watchpoint 1: a
	
	Value = 1
	0x00000000004005f2 in thread2_func (p_arg=0x400775) at a.c:19
	19                      printf("%d\n", a);;
	(gdb) c
	Continuing.
	1
	[Switching to Thread 0x7ffff782c700 (LWP 16938)]
	Hardware access (read/write) watchpoint 1: a
	
	Value = 1
	0x00000000004005c6 in thread1_func (p_arg=0x40076c) at a.c:10
	10                      a++;

可以看到，使用“`aw a`”命令（`aw`是`awatch`命令的縮寫）以後，每次讀取或改變`a`的值都會讓程式停下來。  
需要注意的是`awatch`命令只對硬體觀察點才生效，參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Watchpoints.html).

---

## Catchpoint

### 讓catchpoint只觸發一次

## 例子
	#include <stdio.h>
	#include <stdlib.h>
	#include <sys/types.h>
	#include <unistd.h>
	
	int main(void) {
	    pid_t pid;
	    int i = 0;
	
	    for (i = 0; i < 2; i++)
	    {
		    pid = fork();
		    if (pid < 0)
		    {
		        exit(1);
		    }
		    else if (pid == 0)
		    {
		        exit(0);
		    }
	    }
	    printf("hello world\n");
	    return 0;
	}

## 技巧
使用gdb除錯程式時，可以用“`tcatch`”命令設定`catchpoint`只觸發一次，以上面程式為例：  

	(gdb) tcatch fork
	Catchpoint 1 (fork)
	(gdb) r
	Starting program: /home/nan/a
	
	Temporary catchpoint 1 (forked process 27377), 0x00000034e42acdbd in fork () from /lib64/libc.so.6
	(gdb) c
	Continuing.
	hello world
	[Inferior 1 (process 27373) exited normally]
	(gdb) q

可以看到當程式只在第一次呼叫`fork`時暫停。  

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Catchpoints.html).

---

### 為fork呼叫設定catchpoint

## 例子
	#include <stdio.h>
	#include <stdlib.h>
	#include <sys/types.h>
	#include <unistd.h>
	
	int main(void) {
	    pid_t pid;
	
	    pid = fork();
	    if (pid < 0)
	    {
	        exit(1);
	    }
	    else if (pid > 0)
	    {
	        exit(0);
	    }
	    printf("hello world\n");
	    return 0;
	}



## 技巧
使用gdb除錯程式時，可以用“`catch fork`”命令為`fork`呼叫設定`catchpoint`，以上面程式為例：  

	(gdb) catch fork
	Catchpoint 1 (fork)
	(gdb) r
	Starting program: /home/nan/a 
	
	Catchpoint 1 (forked process 33499), 0x00000034e42acdbd in fork () from /lib64/libc.so.6
	(gdb) bt
	#0  0x00000034e42acdbd in fork () from /lib64/libc.so.6
	#1  0x0000000000400561 in main () at a.c:9
可以看到當`fork`呼叫發生後，gdb會暫停程式的執行。  
注意：目前只有HP-UX和GNU/Linux支援這個功能。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Catchpoints.html).

---

### 為vfork呼叫設定catchpoint

## 例子
	#include <stdio.h>
	#include <stdlib.h>
	#include <sys/types.h>
	#include <unistd.h>
	
	int main(void) {
	    pid_t pid;
	
	    pid = vfork();
	    if (pid < 0)
	    {
	        exit(1);
	    }
	    else if (pid > 0)
	    {
	        exit(0);
	    }
	    printf("hello world\n");
	    return 0;
	}



## 技巧
使用gdb除錯程式時，可以用“`catch vfork`”命令為`vfork`呼叫設定`catchpoint`，以上面程式為例：  

	(gdb) catch vfork
	Catchpoint 1 (vfork)
	(gdb) r
	Starting program: /home/nan/a
	
	Catchpoint 1 (vforked process 27312), 0x00000034e42acfc4 in vfork ()
	   from /lib64/libc.so.6
	(gdb) bt
	#0  0x00000034e42acfc4 in vfork () from /lib64/libc.so.6
	#1  0x0000000000400561 in main () at a.c:9

可以看到當`vfork`呼叫發生後，gdb會暫停程式的執行。  
注意：目前只有HP-UX和GNU/Linux支援這個功能。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Catchpoints.html).

---

### 為exec呼叫設定catchpoint

## 例子
	#include <unistd.h>
	
	int main(void) {
	    execl("/bin/ls", "ls", NULL);
	    return 0;
	}



## 技巧
使用gdb除錯程式時，可以用“`catch exec`”命令為`exec`系列系統呼叫設定`catchpoint`，以上面程式為例：  

	(gdb) catch exec
	Catchpoint 1 (exec)
	(gdb) r
	Starting program: /home/nan/a
	process 32927 is executing new program: /bin/ls
	
	Catchpoint 1 (exec'd /bin/ls), 0x00000034e3a00b00 in _start () from /lib64/ld-linux-x86-64.so.2
	(gdb) bt
	#0  0x00000034e3a00b00 in _start () from /lib64/ld-linux-x86-64.so.2
	#1  0x0000000000000001 in ?? ()
	#2  0x00007fffffffe73d in ?? ()
	#3  0x0000000000000000 in ?? ()


可以看到當`execl`呼叫發生後，gdb會暫停程式的執行。  
注意：目前只有HP-UX和GNU/Linux支援這個功能。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Catchpoints.html).

---

### 為系統呼叫設定catchpoint

## 例子
	#include <stdio.h>

	int main(void)
	{
	    char p1[] = "Sam";
	    char *p2 = "Bob";
	
	    printf("p1 is %s, p2 is %s\n", p1, p2);
	    return 0;
	}



## 技巧
使用gdb除錯程式時，可以使用`catch syscall [name | number]`為關注的系統呼叫設定`catchpoint`，以上面程式為例：  

	(gdb) catch syscall mmap
	Catchpoint 1 (syscall 'mmap' [9])
	(gdb) r
	Starting program: /home/nan/a
	
	Catchpoint 1 (call to syscall mmap), 0x00000034e3a16f7a in mmap64 ()
	   from /lib64/ld-linux-x86-64.so.2
	(gdb) c
	Continuing.
	
	Catchpoint 1 (returned from syscall mmap), 0x00000034e3a16f7a in mmap64 ()
	   from /lib64/ld-linux-x86-64.so.2


可以看到當`mmap`呼叫發生後，gdb會暫停程式的執行。  
也可以使用系統呼叫的編號設定`catchpoint`，仍以上面程式為例：  

	(gdb) catch syscall 9
	Catchpoint 1 (syscall 'mmap' [9])
	(gdb) r
	Starting program: /home/nan/a
	
	Catchpoint 1 (call to syscall mmap), 0x00000034e3a16f7a in mmap64 ()
	   from /lib64/ld-linux-x86-64.so.2
	(gdb) c
	Continuing.
	
	Catchpoint 1 (returned from syscall mmap), 0x00000034e3a16f7a in mmap64 ()
	   from /lib64/ld-linux-x86-64.so.2
	(gdb) c
	Continuing.
	
	Catchpoint 1 (call to syscall mmap), 0x00000034e3a16f7a in mmap64 ()
	   from /lib64/ld-linux-x86-64.so.2
可以看到和使用`catch syscall mmap`效果是一樣的。（系統呼叫和編號的對映參考具體的`xml`檔案，以我的系統為例，就是在`/usr/local/share/gdb/syscalls`資料夾下的`amd64-linux.xml`。）

如果不指定具體的系統呼叫，則會為所有的系統呼叫設定`catchpoint`，仍以上面程式為例：  

	(gdb) catch syscall
	Catchpoint 1 (any syscall)
	(gdb) r
	Starting program: /home/nan/a
	
	Catchpoint 1 (call to syscall brk), 0x00000034e3a1618a in brk ()
	   from /lib64/ld-linux-x86-64.so.2
	(gdb) c
	Continuing.
	
	Catchpoint 1 (returned from syscall brk), 0x00000034e3a1618a in brk ()
	   from /lib64/ld-linux-x86-64.so.2
	(gdb)
	Continuing.
	
	Catchpoint 1 (call to syscall mmap), 0x00000034e3a16f7a in mmap64 ()
	   from /lib64/ld-linux-x86-64.so.2



參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Set-Catchpoints.html).

---

### 透過為ptrace呼叫設定catchpoint破解anti-debugging的程式

## 例子
	#include <sys/ptrace.h>
	#include <stdio.h>
	 
	int main()                                                                      
	{
	        if (ptrace(PTRACE_TRACEME, 0, 0, 0) < 0 ) {
	                printf("Gdb is debugging me, exit.\n");
	                return 1;
	        }
	        printf("No debugger, continuing\n");
	        return 0;
	}



## 技巧
有些程式不想被gdb除錯，它們就會在程式中呼叫“`ptrace`”函式，一旦返回失敗，就證明程式正在被gdb等類似的程式追蹤，所以就直接退出。以上面程式為例：  

	(gdb) start
	Temporary breakpoint 1 at 0x400508: file a.c, line 6.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:6
	6                       if (ptrace(PTRACE_TRACEME, 0, 0, 0) < 0 ) {
	(gdb) n
	7                               printf("Gdb is debugging me, exit.\n");
	(gdb)
	Gdb is debugging me, exit.
	8                               return 1;



破解這類程式的辦法就是為`ptrace`呼叫設定`catchpoint`，透過修改`ptrace`的返回值，達到目的。仍以上面程式為例：  

	(gdb) catch syscall ptrace
	Catchpoint 2 (syscall 'ptrace' [101])
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	
	Catchpoint 2 (call to syscall ptrace), 0x00007ffff7b2be9c in ptrace () from /lib64/libc.so.6
	(gdb) c
	Continuing.
	
	Catchpoint 2 (returned from syscall ptrace), 0x00007ffff7b2be9c in ptrace () from /lib64/libc.so.6
	(gdb) set $rax = 0
	(gdb) c
	Continuing.
	No debugger, continuing
	[Inferior 1 (process 11491) exited normally]

可以看到，透過修改`rax`暫存器的值，達到修改返回值的目的，從而讓gdb可以繼續除錯程式（列印“`No debugger, continuing`”）。  
詳細過程，可以參見這篇文章[避開 PTRACE_TRACME 反追蹤技巧](http://blog.linux.org.tw/~jserv/archives/2011_08.html).

---

## 列印

### 列印ASCII和寬字元字串

## 例子
	#include <stdio.h>
	#include <wchar.h>
	
	int main(void)
	{
	        char str1[] = "abcd";
	        wchar_t str2[] = L"abcd";
	        
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以使用“`x/s`”命令列印ASCII字串。以上面程式為例：  

    Temporary breakpoint 1, main () at a.c:6
	6               char str1[] = "abcd";
	(gdb) n
	7               wchar_t str2[] = L"abcd";
	(gdb) 
	9               return 0;
	(gdb) x/s str1
	0x804779f:      "abcd"

可以看到打印出了`str1`字串的值。

列印寬字元字串時，要根據寬字元的長度決定如何列印。仍以上面程式為例： 

    Temporary breakpoint 1, main () at a.c:6
	6               char str1[] = "abcd";
	(gdb) n
	7               wchar_t str2[] = L"abcd";
	(gdb) 
	9               return 0;
	(gdb) p sizeof(wchar_t)
	$1 = 4
	(gdb) x/ws str2
	0x8047788:      U"abcd"
由於當前平臺寬字元的長度為4個位元組，則用“`x/ws`”命令。如果是2個位元組，則用“`x/hs`”命令。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Memory.html).

---

### 列印STL容器中的內容

## 例子

	#include <iostream>
	#include <vector>
	
	using namespace std;
	
	int main ()
	{
	  vector<int> vec(10); // 10 zero-initialized elements
	
	  for (int i = 0; i < vec.size(); i++)
	    vec[i] = i;
	
	  cout << "vec contains:";
	  for (int i = 0; i < vec.size(); i++)
	    cout << ' ' << vec[i];
	  cout << '\n';
	
	  return 0;
	}

## 技巧一

在gdb中，如果要列印C++ STL容器的內容，預設的顯示結果可讀性很差：

	(gdb) p vec
	$1 = {<std::_Vector_base<int, std::allocator<int> >> = {
	    _M_impl = {<std::allocator<int>> = {<__gnu_cxx::new_allocator<int>> = {<No data fields>}, <No data fields>}, _M_start = 0x404010, _M_finish = 0x404038, 
              _M_end_of_storage = 0x404038}}, <No data fields>}

gdb 7.0之後，可以使用gcc提供的python指令碼，來改善顯示結果：

	(gdb) p vec
	$1 = std::vector of length 10, capacity 10 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}

某些發行版(Fedora 11+)，不需要額外的設定工作。可在gdb命令列下驗證（若沒有顯示，可按下文的方法進行設定）。

		(gdb) info pretty-printer

方法如下:

1. 獲得python指令碼，建議使用gcc預設安裝的

		sudo find / -name "*libstdcxx*"
2. 若本機查詢不到python指令碼，建議下載gcc對應版本原始碼包

    gcc git 倉庫地址：https://github.com/gcc-mirror/gcc

    python 指令碼位於 libstdc++-v3/python 目錄下
3. 將如下程式碼新增到.gdbinit檔案中（假設python指令碼位於 /home/maude/gdb_printers/ 下）

		python
		import sys
		sys.path.insert(0, '/home/maude/gdb_printers/python')
		from libstdcxx.v6.printers import register_libstdcxx_printers
		register_libstdcxx_printers (None)
		end

（源自https://sourceware.org/gdb/wiki/STLSupport）

## 技巧二

`p vec`的輸出無法閱讀，但能給我們提示，從而得到無需指令碼支援的技巧：

	(gdb) p *(vec._M_impl._M_start)@vec.size()
	$2 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
	
## 技巧三

將 [dbinit_stl_views](http://www.yolinux.com/TUTORIALS/src/dbinit_stl_views-1.03.txt ) 下載下來,，執行命令
```shell
cat dbinit_stl_views-1.03.txt >> ~/.gdbinit
```
即可
一些常用的容器及其對應的命令關係
```shell
std::vector<T>  pvector stl_variable 
std::list<T>  plist stl_variable T 
std::map<T,T>  pmap stl_variable 
std::multimap<T,T>  pmap stl_variable 
std::set<T>  pset stl_variable T 
std::multiset<T>  pset stl_variable 
std::deque<T>  pdequeue stl_variable 
std::stack<T>  pstack stl_variable 
std::queue<T>  pqueue stl_variable 
std::priority_queue<T>  ppqueue stl_variable 
std::bitset<n><td>  pbitset stl_variable 
std::string  pstring stl_variable 
std::widestring  pwstring stl_variable  
```
更多詳情，參考配置中的幫助

---

### 列印大陣列中的內容

## 例子

	int main()
	{
	  int array[201];
	  int i;
	
	  for (i = 0; i < 201; i++)
	    array[i] = i;
	
	  return 0;
	}

## 技巧

在gdb中，如果要列印大陣列的內容，預設最多會顯示200個元素：

	(gdb) p array
	$1 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
	  48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 
	  95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 
	  133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 
	  170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199...}

可以使用如下命令，設定這個最大限制數：

<pre><code>(gdb) set print elements <i>number-of-elements</i></code></pre>

也可以使用如下命令，設定為沒有限制：

	(gdb) set print elements 0

或

	(gdb) set print elements unlimited
	(gdb) p array
	$2 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 
	  48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 
	  95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 
	  133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 
	  170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200}

詳情參見[gdb手冊](https://sourceware.org/gdb/download/onlinedocs/gdb/Print-Settings.html#Print-Settings)

---

### 列印陣列中任意連續元素值

## 例子

	int main(void)
	{
	  int array[201];
	  int i;
	
	  for (i = 0; i < 201; i++)
	    array[i] = i;
	
	  return 0;
	}

## 技巧

在gdb中，如果要列印陣列中任意連續元素的值，可以使用“`p array[index]@num`”命令（`p`是`print`命令的縮寫）。其中`index`是陣列索引（從0開始計數），`num`是連續多少個元素。以上面程式碼為例：

	(gdb) p array
	$8 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
	  32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62,
	  63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,
	  94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
	  120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144,
	  145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169,
	  170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194,
	  195, 196, 197, 198, 199...}
	(gdb) p array[60]@10
	$9 = {60, 61, 62, 63, 64, 65, 66, 67, 68, 69}


可以看到列印了`array`陣列第60~69個元素的值。  
如果要列印從陣列開頭連續元素的值，也可使用這個命令：“`p *array@num`”：

	(gdb) p *array@10
	$2 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}


詳情參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Arrays.html#Arrays)

---

### 列印陣列的索引下標

## 例子

	#include <stdio.h>
	
	int num[10] = { 
	  1 << 0,
	  1 << 1,
	  1 << 2,
	  1 << 3,
	  1 << 4,
	  1 << 5,
	  1 << 6,
	  1 << 7,
	  1 << 8,
	  1 << 9
	};
	
	int main (void)
	{
	  int i;
	
	  for (i = 0; i < 10; i++)
	    printf ("num[%d] = %d\n", i, num[i]);
	
	  return 0;
	}

## 技巧

在gdb中，當列印一個數組時，預設是不列印索引下標的：

	(gdb) p num
	$1 = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512}

如果要列印索引下標，則可以透過如下命令進行設定：

	(gdb) set print array-indexes on

	(gdb) p num
	$2 = {[0] = 1, [1] = 2, [2] = 4, [3] = 8, [4] = 16, [5] = 32, [6] = 64, [7] = 128, [8] = 256, [9] = 512}

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Print-Settings.html#index-set-print)

---

### 格式化列印陣列

## 例子

利用`call`函式控制陣列的輸出格式：

```
#include <stdio.h>

int matrix[10][10];

/* 格式化輸出陣列 */
void print(int matrix[][10], int m, int n) {
    int i, j;
    for (i = 0; i < m; ++i) {
        for (j = 0; j < n; ++j)
            printf("%d ", matrix[i][j]);
        printf("\n");
    }
}

int main(int argc, char const* argv[]) {
    int i, j;
    for (i = 0; i < 10; ++i)
        for (j = 0; j < 10; ++j)
            matrix[i][j] = i*10 + j;
    return 0;
}
```

## 技巧

```
(gdb) b 20
Breakpoint 1 at 0x40065e: file test.c, line 20.
(gdb) r
Starting program: /home/zhaoyu/codelab/algorithm/a.out 

Breakpoint 1, main (argc=1, argv=0x7fffffffdc88) at test.c:20
20          return 0;
(gdb) call print(matrix, 10, 10) // 透過函式呼叫格式化輸出陣列
0 1 2 3 4 5 6 7 8 9 
10 11 12 13 14 15 16 17 18 19 
20 21 22 23 24 25 26 27 28 29 
30 31 32 33 34 35 36 37 38 39 
40 41 42 43 44 45 46 47 48 49 
50 51 52 53 54 55 56 57 58 59 
60 61 62 63 64 65 66 67 68 69 
70 71 72 73 74 75 76 77 78 79 
80 81 82 83 84 85 86 87 88 89 
90 91 92 93 94 95 96 97 98 99 
```

---

### 列印函式區域性變數的值

## 例子

	#include <stdio.h>

	void fun_a(void)
	{
		int a = 0;
		printf("%d\n", a);
	}
	
	void fun_b(void)
	{
		int b = 1;
		fun_a();
		printf("%d\n", b);
	}
	
	void fun_c(void)
	{
		int c = 2;
		fun_b();
		printf("%d\n", c);
	}
	
	void fun_d(void)
	{
		int d = 3;
		fun_c();
		printf("%d\n", d);
	}
	
	int main(void)
	{
		int var = -1;
		fun_d();
		return 0;
	}

## 技巧一

如果要列印函式區域性變數的值，可以使用“bt full”命令（bt是backtrace的縮寫）。首先我們在函式fun_a裡打上斷點，當程式斷住時，顯示呼叫棧資訊：

	(gdb) bt
	#0  fun_a () at a.c:6
	#1  0x000109b0 in fun_b () at a.c:12
	#2  0x000109e4 in fun_c () at a.c:19
	#3  0x00010a18 in fun_d () at a.c:26
	#4  0x00010a4c in main () at a.c:33


接下來，用“bt full”命令顯示各個函式的區域性變數值：

	(gdb) bt full
	#0  fun_a () at a.c:6
	        a = 0
	#1  0x000109b0 in fun_b () at a.c:12
	        b = 1
	#2  0x000109e4 in fun_c () at a.c:19
	        c = 2
	#3  0x00010a18 in fun_d () at a.c:26
	        d = 3
	#4  0x00010a4c in main () at a.c:33
	        var = -1


也可以使用如下“bt full n”，意思是從內向外顯示n個棧楨，及其區域性變數，例如：

	(gdb) bt full 2
	#0  fun_a () at a.c:6
	        a = 0
	#1  0x000109b0 in fun_b () at a.c:12
	        b = 1
	(More stack frames follow...)


而“bt full -n”，意思是從外向內顯示n個棧楨，及其區域性變數，例如：

	(gdb) bt full -2
	#3  0x00010a18 in fun_d () at a.c:26
	        d = 3
	#4  0x00010a4c in main () at a.c:33
	        var = -1


詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Backtrace.html)

## 技巧二

如果只是想列印當前函式區域性變數的值，可以使用如下命令：

	(gdb) info locals
	a = 0

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Frame-Info.html#index-info-locals)

---

### 列印程序記憶體資訊

## 技巧
用gdb除錯程式時，如果想檢視程序的記憶體對映資訊，可以使用“i proc mappings”命令（i是info命令縮寫），例如:  

	(gdb) i proc mappings
	process 27676 flags:
	PR_STOPPED Process (LWP) is stopped
	PR_ISTOP Stopped on an event of interest
	PR_RLC Run-on-last-close is in effect
	PR_MSACCT Microstate accounting enabled
	PR_PCOMPAT Micro-state accounting inherited on fork
	PR_FAULTED : Incurred a traced hardware fault FLTBPT: Breakpoint trap

	Mapped address spaces:

        Start Addr   End Addr       Size     Offset   Flags
         0x8046000  0x8047fff     0x2000 0xfffff000 -s--rwx
         0x8050000  0x8050fff     0x1000          0 ----r-x
         0x8060000  0x8060fff     0x1000          0 ----rwx
        0xfee40000 0xfef4efff   0x10f000          0 ----r-x
        0xfef50000 0xfef55fff     0x6000          0 ----rwx
        0xfef5f000 0xfef66fff     0x8000   0x10f000 ----rwx
        0xfef67000 0xfef68fff     0x2000          0 ----rwx
        0xfef70000 0xfef70fff     0x1000          0 ----rwx
        0xfef80000 0xfef80fff     0x1000          0 ---sr--
        0xfef90000 0xfef90fff     0x1000          0 ----rw-
        0xfefa0000 0xfefa0fff     0x1000          0 ----rw-
        0xfefb0000 0xfefb0fff     0x1000          0 ----rwx
        0xfefc0000 0xfefeafff    0x2b000          0 ----r-x
        0xfeff0000 0xfeff0fff     0x1000          0 ----rwx
        0xfeffb000 0xfeffcfff     0x2000    0x2b000 ----rwx
        0xfeffd000 0xfeffdfff     0x1000          0 ----rwx




首先輸出了程序的flags，接著是程序的記憶體對映資訊。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/SVR4-Process-Information.html#index-info-proc-exe).

此外，也可以用"i files"（還有一個同樣作用的命令：“i target”）命令，它可以更詳細地輸出程序的記憶體資訊，包括引用的動態連結庫等等，例如：

	(gdb) i files
	Symbols from "/data1/nan/a".
	Unix /proc child process:
        Using the running image of child Thread 1 (LWP 1) via /proc.
        While running this, GDB does not access memory from...
	Local exec file:
        `/data1/nan/a', file type elf32-i386-sol2.
        Entry point: 0x8050950
        0x080500f4 - 0x08050105 is .interp
        0x08050108 - 0x08050114 is .eh_frame_hdr
        0x08050114 - 0x08050218 is .hash
        0x08050218 - 0x08050418 is .dynsym
        0x08050418 - 0x080507e6 is .dynstr
        0x080507e8 - 0x08050818 is .SUNW_version
        0x08050818 - 0x08050858 is .SUNW_versym
        0x08050858 - 0x08050890 is .SUNW_reloc
        0x08050890 - 0x080508c8 is .rel.plt
        0x080508c8 - 0x08050948 is .plt
        ......
		0xfef5fb58 - 0xfef5fc48 is .dynamic in /usr/lib/libc.so.1
        0xfef5fc80 - 0xfef650e2 is .data in /usr/lib/libc.so.1
        0xfef650e2 - 0xfef650e2 is .bssf in /usr/lib/libc.so.1
        0xfef650e8 - 0xfef65be0 is .picdata in /usr/lib/libc.so.1
        0xfef65be0 - 0xfef666a7 is .data1 in /usr/lib/libc.so.1
        0xfef666a8 - 0xfef680dc is .bss in /usr/lib/libc.so.1




參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Files.html)

---

### 列印靜態變數的值

## 例子

	/* main.c */
	extern void print_var_1(void);
	extern void print_var_2(void);
	
	int main(void)
	{
	  print_var_1();
	  print_var_2();
	  return 0;
	}
	
	/* static-1.c */
	#include <stdio.h>
	
	static int var = 1;
	
	void print_var_1(void)
	{ 
	  printf("var = %d\n", var);
	} 
	
	/* static-2.c */
	#include <stdio.h>
	
	static int var = 2;
	
	void print_var_2(void)
	{ 
	  printf("var = %d\n", var);
	} 

## 技巧

在gdb中，如果直接列印靜態變數，則結果並不一定是你想要的：

	$ gcc -g main.c static-1.c static-2.c
	$ gdb -q ./a.out
	(gdb) start
	(gdb) p var
	$1 = 2

	$ gcc -g main.c static-2.c static-1.c
	$ gdb -q ./a.out
	(gdb) start
	(gdb) p var
	$1 = 1

你可以顯式地指定檔名（上下文）：

	(gdb) p 'static-1.c'::var
	$1 = 1
	(gdb) p 'static-2.c'::var
	$2 = 2

詳情參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Variables.html#Variables)

---

### 列印變數的型別和所在檔案

## 例子

	#include <stdio.h>
	
	struct child {
	  char name[10];
	  enum { boy, girl } gender;
	};
	
	struct child he = { "Tom", boy };
	
	int main (void)
	{
	  static struct child she = { "Jerry", girl };
	  printf ("Hello %s %s.\n", he.gender == boy ? "boy" : "girl", he.name);
	  printf ("Hello %s %s.\n", she.gender == boy ? "boy" : "girl", she.name);
	  return 0;
	}

## 技巧

在gdb中，可以使用如下命令檢視變數的型別：

	(gdb) whatis he
	type = struct child

如果想檢視詳細的型別資訊：

	(gdb) ptype he
	type = struct child {
	    char name[10];
	    enum {boy, girl} gender;
	}

如果想檢視定義該變數的檔案：

	(gdb) i variables he
	All variables matching regular expression "he":
	
	File variable.c:
	struct child he;
	
	Non-debugging symbols:
	0x0000000000402030  she
	0x00007ffff7dd3380  __check_rhosts_file

哦，gdb會顯示所有包含（匹配）該表示式的變數。如果只想檢視完全匹配給定名字的變數：

	(gdb) i variables ^he$
	All variables matching regular expression "^he$":
	
	File variable.c:
	struct child he;

注：`info variables`不會顯示區域性變數，即使是static的也沒有太多的資訊。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Symbols.html)

---

### 列印記憶體的值

## 例子
	#include <stdio.h>

	int main(void)
	{
	        int i = 0;
	        char a[100];
	
	        for (i = 0; i < sizeof(a); i++)
	        {
	                a[i] = i;
	        }
	
	        return 0;
	}


## 技巧
gdb中使用“`x`”命令來列印記憶體的值，格式為“`x/nfu addr`”。含義為以`f`格式列印從`addr`開始的`n`個長度單元為`u`的記憶體值。引數具體含義如下：  
a）n：輸出單元的個數。  
b）f：是輸出格式。比如`x`是以16進位制形式輸出，`o`是以8進位制形式輸出,等等。  
c）u：標明一個單元的長度。`b`是一個`byte`，`h`是兩個`byte`（halfword），`w`是四個`byte`（word），`g`是八個`byte`（giant word）。  

以上面程式為例：  
（1） 以16進位制格式列印陣列前`a`16個byte的值：  

	(gdb) x/16xb a
	0x7fffffffe4a0: 0x00    0x01    0x02    0x03    0x04    0x05    0x06    0x07
	0x7fffffffe4a8: 0x08    0x09    0x0a    0x0b    0x0c    0x0d    0x0e    0x0f
（2） 以無符號10進位制格式列印陣列`a`前16個byte的值：  

	(gdb) x/16ub a
	0x7fffffffe4a0: 0       1       2       3       4       5       6       7
	0x7fffffffe4a8: 8       9       10      11      12      13      14      15
（3） 以2進位制格式列印陣列前16個`a`byte的值：  

	(gdb) x/16tb a
	0x7fffffffe4a0: 00000000        00000001        00000010        00000011        00000100        00000101        00000110        00000111
	0x7fffffffe4a8: 00001000        00001001        00001010        00001011        00001100        00001101        00001110        00001111
（4）  以16進位制格式列印陣列`a`前16個word（4個byte）的值：  

	(gdb) x/16xw a
	0x7fffffffe4a0: 0x03020100      0x07060504      0x0b0a0908      0x0f0e0d0c
	0x7fffffffe4b0: 0x13121110      0x17161514      0x1b1a1918      0x1f1e1d1c
	0x7fffffffe4c0: 0x23222120      0x27262524      0x2b2a2928      0x2f2e2d2c
	0x7fffffffe4d0: 0x33323130      0x37363534      0x3b3a3938      0x3f3e3d3c



參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Memory.html).

---

### 列印原始碼行

## 例子

	$ gdb -q `which gdb`
	(gdb) l
	15	
	16	   You should have received a copy of the GNU General Public License
	17	   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */
	18	
	19	#include "defs.h"
	20	#include "main.h"
	21	#include <string.h>
	22	#include "interps.h"
	23	
	24	int

## 技巧

如上所示，在gdb中可以使用`list`（簡寫為l）命令來顯示原始碼以及行號。`list`命令可以指定行號，函式：

	(gdb) l 24
	(gdb) l main

還可以指定向前或向後列印：

	(gdb) l -
	(gdb) l +

還可以指定範圍：

	(gdb) l 1,10

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/List.html#List)

---

### 每行列印一個結構體成員

## 例子

	#include <stdio.h>
	#include <pthread.h>
	
	typedef struct
	{
	        int a;
	        int b;
	        int c;
	        int d;
	        pthread_mutex_t mutex;
	}ex_st;
	
	int main(void) {
	        ex_st st = {1, 2, 3, 4, PTHREAD_MUTEX_INITIALIZER};
	        printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	        return 0;
	}



## 技巧

預設情況下，gdb以一種“緊湊”的方式列印結構體。以上面程式碼為例：

	(gdb) n
	15              printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	(gdb) p st
	$1 = {a = 1, b = 2, c = 3, d = 4, mutex = {__data = {__lock = 0, __count = 0, __owner = 0, __nusers = 0, __kind = 0,
	      __spins = 0, __list = {__prev = 0x0, __next = 0x0}}, __size = '\000' <repeats 39 times>, __align = 0}}


	


可以看到結構體的顯示很混亂，尤其是結構體裡還巢狀著其它結構體時。

可以執行“set print pretty on”命令，這樣每行只會顯示結構體的一名成員，而且還會根據成員的定義層次進行縮排：

	(gdb) set print pretty on
	(gdb) p st
	$2 = {
	  a = 1,
	  b = 2,
	  c = 3,
	  d = 4,
	  mutex = {
	    __data = {
	      __lock = 0,
	      __count = 0,
	      __owner = 0,
	      __nusers = 0,
	      __kind = 0,
	      __spins = 0,
	      __list = {
	        __prev = 0x0,
	        __next = 0x0
	      }
	    },
	    __size = '\000' <repeats 39 times>,
	    __align = 0
	  }
	}




詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Print-Settings.html#index-print-settings)

---

### 按照派生型別列印物件

## 例子

	#include <iostream>
	using namespace std;
	
	class Shape {
	 public:
	  virtual void draw () {}
	};
	
	class Circle : public Shape {
	 int radius;
	 public:
	  Circle () { radius = 1; }
	  void draw () { cout << "drawing a circle...\n"; }
	};
	
	class Square : public Shape {
	 int height;
	 public:
	  Square () { height = 2; }
	  void draw () { cout << "drawing a square...\n"; }
	};
	
	void drawShape (class Shape &p)
	{
	  p.draw ();
	}
	
	int main (void)
	{
	  Circle a;
	  Square b;
	  drawShape (a);
	  drawShape (b);
	  return 0;
	}

## 技巧

在gdb中，當列印一個物件時，預設是按照宣告的型別進行列印：

	(gdb) frame
	#0  drawShape (p=...) at object.cxx:25
	25	  p.draw ();
	(gdb) p p
	$1 = (Shape &) @0x7fffffffde90: {_vptr.Shape = 0x400a80 <vtable for Circle+16>}

在這個例子中，p雖然宣告為class Shape，但它實際的派生型別可能為class Circle和Square。如果要預設按照派生型別進行列印，則可以透過如下命令進行設定：

	(gdb) set print object on

	(gdb) p p
	$2 = (Circle &) @0x7fffffffde90: {<Shape> = {_vptr.Shape = 0x400a80 <vtable for Circle+16>}, radius = 1}

當列印物件型別資訊時，該設定也會起作用：

	(gdb) whatis p
	type = Shape &
	(gdb) ptype p
	type = class Shape {
	  public:
	    virtual void draw(void);
	} &

	(gdb) set print object on
	(gdb) whatis p
	type = /* real type = Circle & */
	Shape &
	(gdb) ptype p
	type = /* real type = Circle & */
	class Shape {
	  public:
	    virtual void draw(void);
	} &

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Print-Settings.html#index-set-print)

---

### 指定程式的輸入輸出裝置

## 例子

	#include <stdio.h>
	
	int main(void)
	{
	  int i;
	
	  for (i = 0; i < 100; i++)
	    {
	      printf("i = %d\n", i);
	    }
	
	  return 0;
	}

## 技巧

在gdb中，預設情況下程式的輸入輸出是和gdb使用同一個終端。你也可以為程式指定一個單獨的輸入輸出終端。

首先，開啟一個新終端，使用如下命令獲得裝置檔名：

	$ tty
	/dev/pts/2

然後，透過命令列選項指定程式的輸入輸出裝置：

	$ gdb -tty /dev/pts/2 ./a.out
	(gdb) r

或者，在gdb中，使用命令進行設定：

	(gdb) tty /dev/pts/2

詳情參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Input_002fOutput.html#index-tty)

---

### 使用“$\\_”和“$\\__”變數

## 例子
	#include <stdio.h>

	int main(void)
	{
	        int i = 0;
	        char a[100];
	
	        for (i = 0; i < sizeof(a); i++)
	        {
	                a[i] = i;
	        }
	
	        return 0;
	}

## 技巧
"`x`"命令會把最後檢查的記憶體地址值存在“`$_`”這個“convenience variable”中，並且會把這個地址中的內容放在“`$__`”這個“convenience variable”，以上面程式為例:
	
	(gdb) b a.c:13
	Breakpoint 1 at 0x4004a0: file a.c, line 13.
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	
	Breakpoint 1, main () at a.c:13
	13              return 0;
	(gdb) x/16xb a
	0x7fffffffe4a0: 0x00    0x01    0x02    0x03    0x04    0x05    0x06    0x07
	0x7fffffffe4a8: 0x08    0x09    0x0a    0x0b    0x0c    0x0d    0x0e    0x0f
	(gdb) p $_
	$1 = (int8_t *) 0x7fffffffe4af
	(gdb) p $__
	$2 = 15


可以看到“`$_`”值為`0x7fffffffe4af`，正好是"`x`"命令檢查的最後的記憶體地址。而“`$__`”值為`15`。  
另外要注意有些命令（像“`info line`”和“`info breakpoint`”）會提供一個預設的地址給"`x`"命令檢查，而這些命令也會把“`$_`”的值變為那個預設地址值：

	(gdb) p $_
	$5 = (int8_t *) 0x7fffffffe4af
	(gdb) info breakpoint
	Num     Type           Disp Enb Address            What
	1       breakpoint     keep y   0x00000000004004a0 in main at a.c:13
	        breakpoint already hit 1 time
	(gdb) p $_
	$6 = (void *) 0x4004a0 <main+44>


可以看到使用“`info breakpoint`”命令後，“`$_`”值變為`0x4004a0`。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Convenience-Vars.html).

---

### 列印程式動態分配記憶體的資訊

## 例子
	#include <stdio.h>
	#include <malloc.h>
	
	int main(void)
	{
	        char *p[10];
	        int i = 0;
	
	        for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	        {
	                p[i] = malloc(100000);
	        }
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以用下面的自定義命令，列印程式動態分配記憶體的資訊：  

    define mallocinfo
      set $__f = fopen("/dev/tty", "w")
      call malloc_info(0, $__f)
      call fclose($__f)
    end

以上面程式為例：  

    Temporary breakpoint 5, main () at a.c:7
	7               int i = 0;
	(gdb) mallocinfo 
	<malloc version="1">
	<heap nr="0">
	<sizes>
	</sizes>
	<total type="fast" count="0" size="0"/>
	<total type="rest" count="0" size="0"/>
	<system type="current" size="135168"/>
	<system type="max" size="135168"/>
	<aspace type="total" size="135168"/>
	<aspace type="mprotect" size="135168"/>
	</heap>
	<total type="fast" count="0" size="0"/>
	<total type="rest" count="0" size="0"/>
	<system type="current" size="135168"/>
	<system type="max" size="135168"/>
	<aspace type="total" size="135168"/>
	<aspace type="mprotect" size="135168"/>
	</malloc>
	$20 = 0
	$21 = 0
	(gdb) n
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) mallocinfo 
	<malloc version="1">
	<heap nr="0">
	<sizes>
	</sizes>
	<total type="fast" count="0" size="0"/>
	<total type="rest" count="0" size="0"/>
	<system type="current" size="532480"/>
	<system type="max" size="532480"/>
	<aspace type="total" size="532480"/>
	<aspace type="mprotect" size="532480"/>
	</heap>
	<total type="fast" count="0" size="0"/>
	<total type="rest" count="0" size="0"/>
	<system type="current" size="532480"/>
	<system type="max" size="532480"/>
	<aspace type="total" size="532480"/>
	<aspace type="mprotect" size="532480"/>
	</malloc>
	$22 = 0
	$23 = 0
	(gdb) n
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) 
	11                      p[i] = malloc(100000);
	(gdb) 
	9               for (i = 0; i < sizeof(p)/sizeof(p[0]); i++)
	(gdb) mallocinfo 
	<malloc version="1">
	<heap nr="0">
	<sizes>
	</sizes>
	<total type="fast" count="0" size="0"/>
	<total type="rest" count="0" size="0"/>
	<system type="current" size="1134592"/>
	<system type="max" size="1134592"/>
	<aspace type="total" size="1134592"/>
	<aspace type="mprotect" size="1134592"/>
	</heap>
	<total type="fast" count="0" size="0"/>
	<total type="rest" count="0" size="0"/>
	<system type="current" size="1134592"/>
	<system type="max" size="1134592"/>
	<aspace type="total" size="1134592"/>
	<aspace type="mprotect" size="1134592"/>
	</malloc>
	$24 = 0
	$25 = 0

可以看到gdb輸出了動態分配記憶體的變化資訊。   
參見[stackoverflow](http://stackoverflow.com/questions/1471226/most-tricky-useful-commands-for-gdb-debugger).

---

### 列印呼叫棧幀中變數的值

## 例子

	#include <stdio.h>
	
	int func1(int a)
	{
	  int b = 1;
	  return b * a;
	}
	
	int func2(int a)
	{
	  int b = 2;
	  return b * func1(a);
	}
	
	int func3(int a)
	{
	  int b = 3;
	  return b * func2(a);
	}
	
	int main(void)
	{
	  printf("%d\n", func3(10));
	  return 0;
	}

## 技巧

在gdb中，如果想檢視呼叫棧幀中的變數，可以先切換到該棧幀中，然後列印：

	(gdb) b func1
	(gdb) r
	(gdb) bt
	#0  func1 (a=10) at frame.c:5
	#1  0x0000000000400560 in func2 (a=10) at frame.c:12
	#2  0x0000000000400582 in func3 (a=10) at frame.c:18
	#3  0x0000000000400596 in main () at frame.c:23
	(gdb) f 1
	(gdb) p b
	(gdb) f 2
	(gdb) p b

也可以不進行切換，直接列印：

	(gdb) p func2::b
	$1 = 2
	(gdb) p func3::b
	$2 = 3

同樣，對於C++的函式名，需要使用單引號括起來，比如：

	(gdb) p '(anonymous namespace)::SSAA::handleStore'::n->pi->inst->dump()

詳情參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Variables.html#Variables)

---

## 多程序/執行緒

### 除錯已經執行的程序

## 例子

	#include <stdio.h>
	#include <pthread.h>
	void *thread_func(void *p_arg)
	{
	        while (1)
	        {
	                printf("%s\n", (char*)p_arg);
	                sleep(10);
	        }
	}
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread_func, "Thread 1");
	        pthread_create(&t2, NULL, thread_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}



## 技巧

除錯已經執行的程序有兩種方法：一種是gdb啟動時，指定程序的ID：gdb program processID（也可以用-p或者--pid指定程序ID，例如：gdb program -p=10210）。以上面程式碼為例，用“ps”命令已經獲得程序ID為10210：

	bash-3.2# gdb -q a 10210
	Reading symbols from /data/nan/a...done.
	Attaching to program `/data/nan/a', process 10210
	[New process 10210]
	Retry #1:
	Retry #2:
	Retry #3:
	Retry #4:
	Reading symbols from /usr/lib/libc.so.1...(no debugging symbols found)...done.
	[Thread debugging using libthread_db enabled]
	[New LWP    3        ]
	[New LWP    2        ]
	[New Thread 1 (LWP 1)]
	[New Thread 2 (LWP 2)]
	[New Thread 3 (LWP 3)]
	Loaded symbols for /usr/lib/libc.so.1
	Reading symbols from /lib/ld.so.1...(no debugging symbols found)...done.
	Loaded symbols for /lib/ld.so.1
	[Switching to Thread 1 (LWP 1)]
	0xfeeeae55 in ___nanosleep () from /usr/lib/libc.so.1
	(gdb) bt
	#0  0xfeeeae55 in ___nanosleep () from /usr/lib/libc.so.1
	#1  0xfeedcae4 in sleep () from /usr/lib/libc.so.1
	#2  0x080509ef in main () at a.c:17

如果嫌每次ps檢視程序號比較麻煩，請嘗試如下指令碼

```shell
# 儲存為xgdb.sh（新增可執行許可權）
# 用法 xgdb.sh a 
prog_bin=$1
running_name=$(basename $prog_bin)
pid=$(/sbin/pidof $running_name)
gdb attach $pid
```

	
另一種是先啟動gdb，然後用“attach”命令“附著”在程序上：

	bash-3.2# gdb -q a
	Reading symbols from /data/nan/a...done.
	(gdb) attach 10210
	Attaching to program `/data/nan/a', process 10210
	[New process 10210]
	Retry #1:
	Retry #2:
	Retry #3:
	Retry #4:
	Reading symbols from /usr/lib/libc.so.1...(no debugging symbols found)...done.
	[Thread debugging using libthread_db enabled]
	[New LWP    3        ]
	[New LWP    2        ]
	[New Thread 1 (LWP 1)]
	[New Thread 2 (LWP 2)]
	[New Thread 3 (LWP 3)]
	Loaded symbols for /usr/lib/libc.so.1
	Reading symbols from /lib/ld.so.1...(no debugging symbols found)...done.
	Loaded symbols for /lib/ld.so.1
	[Switching to Thread 1 (LWP 1)]
	0xfeeeae55 in ___nanosleep () from /usr/lib/libc.so.1
	(gdb) bt
	#0  0xfeeeae55 in ___nanosleep () from /usr/lib/libc.so.1
	#1  0xfeedcae4 in sleep () from /usr/lib/libc.so.1
	#2  0x080509ef in main () at a.c:17



如果不想繼續除錯了，可以用“detach”命令“脫離”程序：

	(gdb) detach
	Detaching from program: /data/nan/a, process 10210
	(gdb) bt
	No stack.


詳情參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Attach.html#index-attach)

---

### 除錯子程序

## 例子

	#include <stdio.h>
	#include <sys/types.h>
	#include <unistd.h>
	
	int main(void) {
		pid_t pid;
	
		pid = fork();
		if (pid < 0)
		{
			exit(1);
		}
		else if (pid > 0)
		{
			exit(0);
		}
		printf("hello world\n");
		return 0;
	}


## 技巧

在除錯多程序程式時，gdb預設會追蹤父程序。例如：

	(gdb) start
	Temporary breakpoint 1 at 0x40055c: file a.c, line 8.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:8
	8               pid = fork();
	(gdb) n
	9               if (pid < 0)
	(gdb) hello world
	
	13              else if (pid > 0)
	(gdb)
	15                      exit(0);
	(gdb)
	[Inferior 1 (process 12786) exited normally]


	


可以看到程式執行到第15行：父程序退出。 

如果要除錯子程序，要使用如下命令：“set follow-fork-mode child”，例如：

	(gdb) set follow-fork-mode child
	(gdb) start
	Temporary breakpoint 1 at 0x40055c: file a.c, line 8.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:8
	8               pid = fork();
	(gdb) n
	[New process 12241]
	[Switching to process 12241]
	9               if (pid < 0)
	(gdb)
	13              else if (pid > 0)
	(gdb)
	17              printf("hello world\n");
	(gdb)
	hello world
	18              return 0;


可以看到程式執行到第17行：子程序列印“hello world”。 

這個命令目前Linux支援，其它很多作業系統都不支援，使用時請注意。參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Forks.html)

---

### 同時除錯父程序和子程序

## 例子

	#include <stdio.h>
	#include <stdlib.h>
	
	int main(void) {
	    pid_t pid;
	
	    pid = fork();
	    if (pid < 0)
	    {
	        exit(1);
	    }
	    else if (pid > 0)
	    {
	        printf("Parent\n");
	        exit(0);
	    }
	    printf("Child\n");
	    return 0;
	}



## 技巧

在除錯多程序程式時，gdb預設只會追蹤父程序的執行，而子程序會獨立執行，gdb不會控制。以上面程式為例：

	(gdb) start
	Temporary breakpoint 1 at 0x40055c: file a.c, line 7.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:7
	7           pid = fork();
	(gdb) n
	8           if (pid < 0)
	(gdb) Child
	
	12          else if (pid > 0)
	(gdb)
	14              printf("Parent\n");
	(gdb)
	Parent
	15              exit(0);

可以看到當單步執行到第8行時，程式打印出“Child” ，證明子程序已經開始獨立執行。

如果要同時除錯父程序和子程序，可以使用“`set detach-on-fork off`”（預設`detach-on-fork`是`on`）命令，這樣gdb就能同時除錯父子程序，並且在除錯一個程序時，另外一個程序處於掛起狀態。仍以上面程式為例：

	(gdb) set detach-on-fork off
	(gdb) start
	Temporary breakpoint 1 at 0x40055c: file a.c, line 7.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:7
	7           pid = fork();
	(gdb) n
	[New process 1050]
	8           if (pid < 0)
	(gdb)
	12          else if (pid > 0)
	(gdb) i inferior
	  Num  Description       Executable
	  2    process 1050      /data2/home/nanxiao/a
	* 1    process 1046      /data2/home/nanxiao/a
	(gdb) n
	14              printf("Parent\n");
	(gdb) n
	Parent
	15              exit(0);
	(gdb)
	[Inferior 1 (process 1046) exited normally]
	(gdb)
	The program is not being run.
	(gdb) i inferiors
	  Num  Description       Executable
	  2    process 1050      /data2/home/nanxiao/a
	* 1    <null>            /data2/home/nanxiao/a
	(gdb) inferior 2
	[Switching to inferior 2 [process 1050] (/data2/home/nanxiao/a)]
	[Switching to thread 2 (process 1050)]
	#0  0x00007ffff7af6cad in fork () from /lib64/libc.so.6
	(gdb) bt
	#0  0x00007ffff7af6cad in fork () from /lib64/libc.so.6
	#1  0x0000000000400561 in main () at a.c:7
	(gdb) n
	Single stepping until exit from function fork,
	which has no line number information.
	main () at a.c:8
	8           if (pid < 0)
	(gdb)
	12          else if (pid > 0)
	(gdb)
	17          printf("Child\n");
	(gdb)
	Child
	18          return 0;
	(gdb)



在使用“`set detach-on-fork off`”命令後，用“`i inferiors`”（`i`是`info`命令縮寫）檢視程序狀態，可以看到父子程序都在被gdb除錯的狀態，前面顯示“*”是正在除錯的程序。當父程序退出後，用“`inferior infno`”切換到子程序去除錯。

這個命令目前Linux支援，其它很多作業系統都不支援，使用時請注意。參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Forks.html)  

此外，如果想讓父子程序都同時執行，可以使用“`set schedule-multiple on`”（預設`schedule-multiple`是`off`）命令，仍以上述程式碼為例：  

	(gdb) set detach-on-fork off
	(gdb) set schedule-multiple on
	(gdb) start
	Temporary breakpoint 1 at 0x40059c: file a.c, line 7.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:7
	7           pid = fork();
	(gdb) n
	[New process 26597]
	Child
可以看到打印出了“Child”，證明子程序也在運行了。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/All_002dStop-Mode.html#All_002dStop-Mode)

---

### 檢視執行緒資訊

## 例子
	#include <stdio.h>
	#include <pthread.h>
	void *thread_func(void *p_arg)
	{
	        while (1)
	        {
	                printf("%s\n", (char*)p_arg);
	                sleep(10);
	        }
	}
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread_func, "Thread 1");
	        pthread_create(&t2, NULL, thread_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}

## 技巧
用gdb除錯多執行緒程式，可以用“i threads”命令（i是info命令縮寫）檢視所有執行緒的資訊，以上面程式為例（執行平臺為Linux，CPU為X86_64）:  

	  (gdb) i threads
	  Id   Target Id         Frame
	  3    Thread 0x7ffff6e2b700 (LWP 31773) 0x00007ffff7915911 in clone () from /lib64/libc.so.6
	  2    Thread 0x7ffff782c700 (LWP 31744) 0x00007ffff78d9bcd in nanosleep () from /lib64/libc.so.6
	* 1    Thread 0x7ffff7fe9700 (LWP 31738) main () at a.c:18

第一項（Id）：是gdb標示每個執行緒的唯一ID：1，2等等。  
第二項（Target Id）：是具體系統平臺用來標示每個執行緒的ID，不同平臺資訊可能會不同。 像當前Linux平臺顯示的就是： Thread 0x7ffff6e2b700 (LWP 31773)。  
第三項（Frame）：顯示的是執行緒執行到哪個函式。  
前面帶“*”表示的是“current thread”，可以理解為gdb除錯多執行緒程式時，選擇的一個“預設執行緒”。

再以Solaris平臺（CPU為X86_64）為例，可以看到顯示資訊會略有不同：

    (gdb) i threads
    [New Thread 2 (LWP 2)]
    [New Thread 3 (LWP 3)]
      Id   Target Id         Frame
      6    Thread 3 (LWP 3)  0xfeec870d in _thr_setup () from /usr/lib/libc.so.1
      5    Thread 2 (LWP 2)  0xfefc9661 in elf_find_sym () from /usr/lib/ld.so.1
      4    LWP    3          0xfeec870d in _thr_setup () from /usr/lib/libc.so.1
      3    LWP    2          0xfefc9661 in elf_find_sym () from /usr/lib/ld.so.1
    * 2    Thread 1 (LWP 1)  main () at a.c:18
      1    LWP    1          main () at a.c:18


也可以用“i threads [Id...]”指定列印某些執行緒的資訊，例如：

	  (gdb) i threads 1 2
	  Id   Target Id         Frame
	  2    Thread 0x7ffff782c700 (LWP 12248) 0x00007ffff78d9bcd in nanosleep () from /lib64/libc.so.6
	* 1    Thread 0x7ffff7fe9700 (LWP 12244) main () at a.c:18

使用"thread thread-id"實現不同執行緒之間的切換，檢視指定執行緒的堆疊資訊

```
(gdb) thread 2
[Switching to thread 2 (Thread 0x7ffff782c700 (LWP 12248))]...
```

使用"thread apply [thread-id-list] [all] args"可以在多個執行緒上執行命令，例如：`thread apply all bt`可以檢視所有執行緒的堆疊資訊。

```
(gdb) thread apply all bt
```

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Threads.html).

---

### 列印所有執行緒的堆疊資訊

## 例子
	#include <stdio.h>
	#include <pthread.h>
	#include <unistd.h>
	int a = 0;

	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}

	int main(int argc, char* argv[])
	{
	        pthread_t t1, t2;
	        pthread_create(&t1, NULL, thread1_func, NULL);
	        pthread_create(&t2, NULL, thread1_func, NULL);

	        sleep(1000);
	        return 0;
	}

## 技巧
gdb可以使用“`thread apply all bt`”命令列印所有執行緒的堆疊資訊。以上面程式為例:

    (gdb) thread apply all bt

    Thread 3 (Thread -1210868832 (LWP 26975)):
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6
    #1  0xb7dcc77f in sleep () from /lib/libc.so.6
    #2  0x08048575 in thread1_func ()
    #3  0xb7e871eb in start_thread () from /lib/libpthread.so.0
    #4  0xb7e007fe in clone () from /lib/libc.so.6

    Thread 2 (Thread -1219257440 (LWP 26976)):
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6
    #1  0xb7dcc77f in sleep () from /lib/libc.so.6
    #2  0x08048575 in thread1_func ()
    #3  0xb7e871eb in start_thread () from /lib/libpthread.so.0
    #4  0xb7e007fe in clone () from /lib/libc.so.6

    Thread 1 (Thread -1210866000 (LWP 26974)):
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6
    #1  0xb7dcc77f in sleep () from /lib/libc.so.6
    #2  0x08048547 in main ()
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6

可以看到，使用“`thread apply all bt`”命令以後，會對所有的執行緒實施backtrace命令。`thread apply [thread-id-list] [all] args` 也可以對指定的執行緒ID列表進行執行：

    (gdb) thread apply 1-2 bt

    Thread 1 (Thread -1210866000 (LWP 26974)):
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6
    #1  0xb7dcc77f in sleep () from /lib/libc.so.6
    #2  0x08048547 in main ()

    Thread 2 (Thread -1219257440 (LWP 26976)):
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6
    #1  0xb7dcc77f in sleep () from /lib/libc.so.6
    #2  0x08048575 in thread1_func ()
    #3  0xb7e871eb in start_thread () from /lib/libpthread.so.0
    #4  0xb7e007fe in clone () from /lib/libc.so.6
    #0  0xb7dcc96c in __gxx_personality_v0 () from /lib/libc.so.6

`thread apply`更多用法和`thread-id-list`的格式用法參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Threads.html).

---

### 在Solaris上使用maintenance命令檢視執行緒資訊

## 技巧
用gdb除錯多執行緒程式時，如果想檢視執行緒資訊，可以使用“i threads”命令（i是info命令縮寫），例如:  

	(gdb) i threads
    106 process 2689429      0xff04af84 in __lwp_park () from /lib/libc.so.1
    105 process 2623893      0xff04af84 in __lwp_park () from /lib/libc.so.1
    104 process 2558357      0xff04af84 in __lwp_park () from /lib/libc.so.1
    103 process 2492821      0xff04af84 in __lwp_park () from /lib/libc.so.1



在Solaris作業系統上，gdb為Solaris量身定做了一個檢視執行緒資訊的命令：“maint info sol-threads”（maint是maintenance命令縮寫），例如:

	(gdb) maint info sol-threads
	user   thread #1, lwp 1, (active)
	user   thread #2, lwp 2, (active)    startfunc: monitor_thread
	user   thread #3, lwp 3, (asleep)    startfunc: mem_db_thread
    - Sleep func: 0x000aa32c


可以看到相比於info命令，maintenance命令顯示了更多資訊。例如執行緒當前狀態（active，asleep），入口函式（startfunc）等。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Threads.html)

---

### 不顯示執行緒啟動和退出資訊

## 例子
	#include <stdio.h>
	#include <pthread.h>
	
	void *thread_func(void *p_arg)
	{
	       sleep(10);
	}
	
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread_func, "Thread 1");
	        pthread_create(&t2, NULL, thread_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}


## 技巧
預設情況下，gdb檢測到有執行緒產生和退出時，會列印提示資訊，以上面程式為例:  

	(gdb) r
	Starting program: /data/nan/a
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[New LWP    2        ]
	[New LWP    3        ]
	[LWP    2         exited]
	[New Thread 2        ]
	[LWP    3         exited]
	[New Thread 3        ]


如果不想顯示這些資訊，可以使用“`set print thread-events off`”命令，這樣當有執行緒產生和退出時，就不會列印提示資訊：

    (gdb) set print thread-events off
	(gdb) r
	Starting program: /data/nan/a
	[Thread debugging using libthread_db enabled]



可以看到不再列印相關資訊。

這個命令有些平臺不支援，使用時需注意。參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Threads.html).

---

### 只允許一個執行緒執行

## 例子
	#include <stdio.h>
	#include <pthread.h>
	int a = 0;
	int b = 0;
	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(1);
	        }
	}
	
	void *thread2_func(void *p_arg)
	{
	        while (1)
	        {
	                b++;
	                sleep(1);
	        }
	}
	
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread1_func, "Thread 1");
	        pthread_create(&t2, NULL, thread2_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}


## 技巧
用gdb除錯多執行緒程式時，一旦程式斷住，所有的執行緒都處於暫停狀態。此時當你除錯其中一個執行緒時（比如執行“`step`”，“`next`”命令），所有的執行緒都會同時執行。以上面程式為例:  

	(gdb) b a.c:9
	Breakpoint 1 at 0x400580: file a.c, line 9.
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	[New Thread 0x7ffff782c700 (LWP 17368)]
	[Switching to Thread 0x7ffff782c700 (LWP 17368)]
	
	Breakpoint 1, thread1_func (p_arg=0x400718) at a.c:9
	9                       a++;
	(gdb) p b
	$1 = 0
	(gdb) s
	10                      sleep(1);
	(gdb) s
	[New Thread 0x7ffff6e2b700 (LWP 17369)]
	11              }
	(gdb)
	
	Breakpoint 1, thread1_func (p_arg=0x400718) at a.c:9
	9                       a++;
	(gdb)
	10                      sleep(1);
	(gdb) p b
	$2 = 3

`thread1_func`更新全域性變數`a`的值，`thread2_func`更新全域性變數`b`的值。我在`thread1_func`裡`a++`語句打上斷點，當斷點第一次命中時，列印`b`的值是`0`，在單步除錯`thread1_func`幾次後，`b`的值變成`3`，證明在單步除錯`thread1_func`時，`thread2_func`也在執行。  
如果想在除錯一個執行緒時，讓其它執行緒暫停執行，可以使用“`set scheduler-locking on`”命令：

    (gdb) b a.c:9
	Breakpoint 1 at 0x400580: file a.c, line 9.
	(gdb) r
	Starting program: /data2/home/nanxiao/a
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib64/libthread_db.so.1".
	[New Thread 0x7ffff782c700 (LWP 19783)]
	[Switching to Thread 0x7ffff782c700 (LWP 19783)]
	
	Breakpoint 1, thread1_func (p_arg=0x400718) at a.c:9
	9                       a++;
	(gdb) set scheduler-locking on
	(gdb) p b
	$1 = 0
	(gdb) s
	10                      sleep(1);
	(gdb)
	11              }
	(gdb)
	
	Breakpoint 1, thread1_func (p_arg=0x400718) at a.c:9
	9                       a++;
	(gdb)
	10                      sleep(1);
	(gdb)
	11              }
	(gdb) p b
	$2 = 0

可以看到在單步除錯`thread1_func`幾次後，`b`的值仍然為`0`，證明在在單步除錯`thread1_func`時，`thread2_func`沒有執行。

此外，“`set scheduler-locking`”命令除了支援`off`和`on`模式外（預設是`off`），還有一個`step`模式。含義是：當用"`step`"命令除錯執行緒時，其它執行緒不會執行，但是用其它命令（比如"`next`"）除錯執行緒時，其它執行緒也許會執行。

這個命令依賴於具體作業系統的排程策略，使用時需注意。參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/All_002dStop-Mode.html#All_002dStop-Mode).

---

### 使用“$_thread”變數

## 例子
	#include <stdio.h>
	#include <pthread.h>
	
	int a = 0;
	
	void *thread1_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}
	
	void *thread2_func(void *p_arg)
	{
	        while (1)
	        {
	                a++;
	                sleep(10);
	        }
	}
	
	int main(void)
	{
	        pthread_t t1, t2;
	
	        pthread_create(&t1, NULL, thread1_func, "Thread 1");
			pthread_create(&t2, NULL, thread2_func, "Thread 2");
	
	        sleep(1000);
	        return;
	}

## 技巧
gdb從7.2版本引入了`$_thread`這個“`convenience variable`”，用來儲存當前正在除錯的執行緒號。這個變數在寫斷點命令或是命令指令碼時會很有用。以上面程式為例:
	
	(gdb) wa a
	Hardware watchpoint 2: a
	(gdb) command 2
	Type commands for breakpoint(s) 2, one per line.
	End with a line saying just "end".
	>printf "thread id=%d\n", $_thread
	>end

首先設定了觀察點：“wa a”（`wa`是`watch`命令縮寫），也就是當`a`的值發生變化時，程式會暫停，接下來在`commands`語句中列印執行緒號。  
然後繼續執進程式：

	(gdb) c
	Continuing.
	[New Thread 0x7ffff782c700 (LWP 20928)]
	[Switching to Thread 0x7ffff782c700 (LWP 20928)]
	Hardware watchpoint 2: a
	
	Old value = 0
	New value = 1
	thread1_func (p_arg=0x400718) at a.c:11
	11                      sleep(10);
	thread id=2
	(gdb) c
	Continuing.
	[New Thread 0x7ffff6e2b700 (LWP 20929)]
	[Switching to Thread 0x7ffff6e2b700 (LWP 20929)]
	Hardware watchpoint 2: a
	
	Old value = 1
	New value = 2
	thread2_func (p_arg=0x400721) at a.c:20
	20                      sleep(10);
	thread id=3

可以看到程式暫停時，會列印執行緒號：“`thread id=2`”或者“`thread id=3`”。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Threads.html).

---

### 一個gdb會話中同時除錯多個程式

## 例子
	a.c:
	#include <stdio.h>
	int func(int a, int b)
	{
	        int c = a * b;
	        printf("c is %d\n", c);
	}
	
	int main(void)
	{
	        func(1, 2);
	        return 0;
	}


	b.c:
	#include <stdio.h>

	int func1(int a)
	{
	        return 2 * a;
	}
	
	int func2(int a)
	{
	        int c = 0;
	        c = 2 * func1(a);
	        return c;
	}
	
	int func3(int a)
	{
	        int c = 0;
	        c = 2 * func2(a);
	        return c;
	}
	
	int main(void)
	{
	        printf("%d\n", func3(10));
	        return 0;
	}


## 技巧
gdb支援在一個會話中同時除錯多個程式。以上面程式為例，首先除錯`a`程式：  

	root@bash:~$ gdb a
	GNU gdb (Ubuntu 7.7-0ubuntu3) 7.7
	Copyright (C) 2014 Free Software Foundation, Inc.
	License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
	This is free software: you are free to change and redistribute it.
	There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
	and "show warranty" for details.
	This GDB was configured as "x86_64-linux-gnu".
	Type "show configuration" for configuration details.
	For bug reporting instructions, please see:
	<http://www.gnu.org/software/gdb/bugs/>.
	Find the GDB manual and other documentation resources online at:
	<http://www.gnu.org/software/gdb/documentation/>.
	For help, type "help".
	Type "apropos word" to search for commands related to "word"...
	Reading symbols from a...done.
	(gdb) start
	Temporary breakpoint 1 at 0x400568: file a.c, line 10.
	Starting program: /home/nanxiao/a

接著使用“`add-inferior [ -copies n ] [ -exec executable ]`”命令載入可執行檔案`b`。其中`n`預設為1：  

	(gdb) add-inferior -copies 2 -exec b
	Added inferior 2
	Reading symbols from b...done.
	Added inferior 3
	Reading symbols from b...done.
	(gdb) i inferiors
	  Num  Description       Executable
	  3    <null>            /home/nanxiao/b
	  2    <null>            /home/nanxiao/b
	* 1    process 1586      /home/nanxiao/a
	(gdb) inferior 2
	[Switching to inferior 2 [<null>] (/home/nanxiao/b)]
	(gdb) start
	Temporary breakpoint 2 at 0x400568: main. (3 locations)
	Starting program: /home/nanxiao/b
	
	Temporary breakpoint 2, main () at b.c:24
	24              printf("%d\n", func3(10));
	(gdb) i inferiors
	  Num  Description       Executable
	  3    <null>            /home/nanxiao/b
	* 2    process 1590      /home/nanxiao/b
	  1    process 1586      /home/nanxiao/a
可以看到可以除錯`b`程式了。

另外也可用“`clone-inferior [ -copies n ] [ infno ]`”克隆現有的`inferior`，其中`n`預設為1，`infno`預設為當前的`inferior`：  

	(gdb) i inferiors
	  Num  Description       Executable
	  3    <null>            /home/nanxiao/b
	* 2    process 1590      /home/nanxiao/b
	  1    process 1586      /home/nanxiao/a
	(gdb) clone-inferior -copies 1
	Added inferior 4.
	(gdb) i inferiors
	  Num  Description       Executable
	  4    <null>            /home/nanxiao/b
	  3    <null>            /home/nanxiao/b
	* 2    process 1590      /home/nanxiao/b
	  1    process 1586      /home/nanxiao/a
可以看到又多了一個`b`程式。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Inferiors-and-Programs.html).

---

### 列印程式程序空間資訊

## 例子
	a.c:
	#include <stdio.h>
	int func(int a, int b)
	{
	        int c = a * b;
	        printf("c is %d\n", c);
	}
	
	int main(void)
	{
	        func(1, 2);
	        return 0;
	}


	b.c:
	#include <stdio.h>

	int func1(int a)
	{
	        return 2 * a;
	}
	
	int func2(int a)
	{
	        int c = 0;
	        c = 2 * func1(a);
	        return c;
	}
	
	int func3(int a)
	{
	        int c = 0;
	        c = 2 * func2(a);
	        return c;
	}
	
	int main(void)
	{
	        printf("%d\n", func3(10));
	        return 0;
	}


## 技巧
使用gdb除錯多個程序時，可以使用“`maint info program-spaces`”列印當前所有被除錯的程序資訊。以上面程式為例：  

	[root@localhost nan]# gdb a
	GNU gdb (GDB) 7.8.1
	......
	Reading symbols from a...done.
	(gdb) start
	Temporary breakpoint 1 at 0x4004f9: file a.c, line 10.
	Starting program: /home/nan/a 
	
	Temporary breakpoint 1, main () at a.c:10
	10              func(1, 2);
	(gdb) add-inferior -exec b
	Added inferior 2
	Reading symbols from b...done.
	(gdb) i inferiors b
	Args must be numbers or '$' variables.
	(gdb) i inferiors
	  Num  Description       Executable        
	  2    <null>            /home/nan/b       
	* 1    process 15753     /home/nan/a       
	(gdb) inferior 2
	[Switching to inferior 2 [<null>] (/home/nan/b)]
	(gdb) start
	Temporary breakpoint 2 at 0x4004f9: main. (2 locations)
	Starting program: /home/nan/b 
	
	Temporary breakpoint 2, main () at b.c:24
	24              printf("%d\n", func3(10));
	(gdb) i inferiors
	  Num  Description       Executable        
	* 2    process 15902     /home/nan/b       
	  1    process 15753     /home/nan/a       
	(gdb) clone-inferior -copies 2
	Added inferior 3.
	Added inferior 4.
	(gdb) i inferiors
	  Num  Description       Executable        
	  4    <null>            /home/nan/b       
	  3    <null>            /home/nan/b       
	* 2    process 15902     /home/nan/b       
	  1    process 15753     /home/nan/a       
	(gdb) maint info program-spaces
	  Id   Executable        
	  4    /home/nan/b       
	        Bound inferiors: ID 4 (process 0)
	  3    /home/nan/b       
	        Bound inferiors: ID 3 (process 0)
	* 2    /home/nan/b       
	        Bound inferiors: ID 2 (process 15902)
	  1    /home/nan/a       
	        Bound inferiors: ID 1 (process 15753)
可以看到執行“`maint info program-spaces`”命令後，打印出當前有4個`program-spaces`（編號從1到4）。另外還有每個`program-spaces`對應的程式，`inferior`編號及程序號。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Inferiors-and-Programs.html).

---

### 使用“$_exitcode”變數

## 例子
	int main(void)
	{
	    return 0;
	}


## 技巧
當被除錯的程式正常退出時，gdb會使用`$_exitcode`這個“`convenience variable`”記錄程式退出時的“`exit code`”。以除錯上面程式為例:
	
	[root@localhost nan]# gdb -q a
	Reading symbols from a...done.
	(gdb) start
	Temporary breakpoint 1 at 0x400478: file a.c, line 3.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:3
	3               return 0;
	(gdb) n
	4       }
	(gdb)
	0x00000034e421ed1d in __libc_start_main () from /lib64/libc.so.6
	(gdb)
	Single stepping until exit from function __libc_start_main,
	which has no line number information.
	[Inferior 1 (process 1185) exited normally]
	(gdb) p $_exitcode
	$1 = 0

可以看到列印的`$_exitcode`的值為`0`。  
改變程式，返回值改為`1`：

	int main(void)
	{
	    return 1;
	}
接著除錯：  

	[root@localhost nan]# gdb -q a
	Reading symbols from a...done.
	(gdb) start
	Temporary breakpoint 1 at 0x400478: file a.c, line 3.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:3
	3               return 1;
	(gdb)
	(gdb) n
	4       }
	(gdb)
	0x00000034e421ed1d in __libc_start_main () from /lib64/libc.so.6
	(gdb)
	Single stepping until exit from function __libc_start_main,
	which has no line number information.
	[Inferior 1 (process 2603) exited with code 01]
	(gdb) p $_exitcode
	$1 = 1

可以看到列印的`$_exitcode`的值變為`1`。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Convenience-Vars.html).

---

## core dump檔案

### 為除錯程序產生core dump檔案

# 技巧
在用gdb除錯程式時，我們有時想讓被除錯的程序產生core dump檔案，記錄現在程序的狀態，以供以後分析。可以用“generate-core-file”命令來產生core dump檔案：

	(gdb) help generate-core-file
	Save a core file with the current state of the debugged process.
	Argument is optional filename.  Default filename is 'core.<process_id>'.
 
	(gdb) start
	Temporary breakpoint 1 at 0x8050c12: file a.c, line 9.
	Starting program: /data1/nan/a
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Temporary breakpoint 1, main () at a.c:9
	9           change_var();
	(gdb) generate-core-file
	Saved corefile core.12955

也可使用“gcore”命令：  

	(gdb) help gcore
	Save a core file with the current state of the debugged process.
	Argument is optional filename.  Default filename is 'core.<process_id>'.
	(gdb) gcore
	Saved corefile core.13256

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Core-File-Generation.html)

---

### 載入可執進程式和core dump檔案

## 例子

	#include <stdio.h>

	int main(void) {
	        int *p = NULL;
	        printf("hello world\n");
	        *p = 0;
	        return 0;
	}



## 技巧

例子程式訪問了一個空指標，所以程式會crash併產生core dump檔案。用gdb除錯core dump檔案，通常用這個命令形式：“gdb path/to/the/executable path/to/the/coredump”，然後gdb會顯示程式crash的位置：

	bash-3.2# gdb -q /data/nan/a /var/core/core.a.22268.1402638140
	Reading symbols from /data/nan/a...done.
	[New LWP 1]
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	Core was generated by `./a'.
	Program terminated with signal 11, Segmentation fault.
	#0  0x0000000000400cdb in main () at a.c:6
	6               *p = 0;

有時我們想在gdb啟動後，動態載入可執進程式和core dump檔案，這時可以用“file”和“core”（core-file命令縮寫）命令。“file”命令用來讀取可執行檔案的符號表資訊，而“core”命令則是指定core dump檔案的位置：

	bash-3.2# gdb -q
	(gdb) file /data/nan/a
	Reading symbols from /data/nan/a...done.
	(gdb) core /var/core/core.a.22268.1402638140
	[New LWP 1]
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	Core was generated by `./a'.
	Program terminated with signal 11, Segmentation fault.
	#0  0x0000000000400cdb in main () at a.c:6
	6               *p = 0;



可以看到gdb同樣顯示程式crash的位置。 

這兩個命令可參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Files.html#index-core-dump-file)

---

## 組合語言

### 設定組合語言指令格式

## 例子

	#include <stdio.h>
	int global_var;
	
	void change_var(){
	    global_var=100;
	}
	
	int main(void){
	    change_var();
	    return 0;
	}


## 技巧

在Intel x86處理器上，gdb預設顯示組合語言指令格式是AT&T格式。例如：

	(gdb) disassemble main
	Dump of assembler code for function main:
	   0x08050c0f <+0>:     push   %ebp
	   0x08050c10 <+1>:     mov    %esp,%ebp
	   0x08050c12 <+3>:     call   0x8050c00 <change_var>
	   0x08050c17 <+8>:     mov    $0x0,%eax
	   0x08050c1c <+13>:    pop    %ebp
	   0x08050c1d <+14>:    ret
	End of assembler dump.
	


可以用“set disassembly-flavor”命令將格式改為intel格式：

	(gdb) set disassembly-flavor intel
	(gdb) disassemble main
	Dump of assembler code for function main:
	   0x08050c0f <+0>:     push   ebp
	   0x08050c10 <+1>:     mov    ebp,esp
	   0x08050c12 <+3>:     call   0x8050c00 <change_var>
	   0x08050c17 <+8>:     mov    eax,0x0
	   0x08050c1c <+13>:    pop    ebp
	   0x08050c1d <+14>:    ret
	End of assembler dump.



目前“set disassembly-flavor”命令只能用在Intel x86處理器上，並且取值只有“intel”和“att”。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Machine-Code.html)

---

### 在函式的第一條組合語言指令打斷點

## 例子

	#include <stdio.h>
	int global_var;
	
	void change_var(){
	    global_var=100;
	}
	
	int main(void){
	    change_var();
	    return 0;
	}


## 技巧

通常給函式打斷點的命令：“b func”（b是break命令的縮寫），不會把斷點設定在組合語言指令層次函式的開頭，例如：

	(gdb) b main
	Breakpoint 1 at 0x8050c12: file a.c, line 9.
	(gdb) r
	Starting program: /data1/nan/a
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Breakpoint 1, main () at a.c:9
	9           change_var();
	(gdb) disassemble
	Dump of assembler code for function main:
	   0x08050c0f <+0>:     push   %ebp
	   0x08050c10 <+1>:     mov    %esp,%ebp
	=> 0x08050c12 <+3>:     call   0x8050c00 <change_var>
	   0x08050c17 <+8>:     mov    $0x0,%eax
	   0x08050c1c <+13>:    pop    %ebp
	   0x08050c1d <+14>:    ret
	End of assembler dump.

	


可以看到程式停在了第三條組合語言指令（箭頭所指位置）。如果要把斷點設定在組合語言指令層次函式的開頭，要使用如下命令：“b *func”，例如：

	(gdb) b *main
	Breakpoint 1 at 0x8050c0f: file a.c, line 8.
	(gdb) r
	Starting program: /data1/nan/a
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Breakpoint 1, main () at a.c:8
	8       int main(void){
	(gdb) disassemble
	Dump of assembler code for function main:
	=> 0x08050c0f <+0>:     push   %ebp
	   0x08050c10 <+1>:     mov    %esp,%ebp
	   0x08050c12 <+3>:     call   0x8050c00 <change_var>
	   0x08050c17 <+8>:     mov    $0x0,%eax
	   0x08050c1c <+13>:    pop    %ebp
	   0x08050c1d <+14>:    ret
	End of assembler dump.

可以看到程式停在了第一條組合語言指令（箭頭所指位置）。

---

### 自動反組合語言後面要執行的程式碼

## 例子
    (gdb) set disassemble-next-line on
    (gdb) start 
    The program being debugged has been started already.
    Start it from the beginning? (y or n) y
    Temporary breakpoint 3 at 0x400543: file 1.c, line 14.
    Starting program: /home/teawater/tmp/a.out 

    Temporary breakpoint 3, main (argc=1, argv=0x7fffffffdf38, envp=0x7fffffffdf48) at 1.c:14
    14      printf("1\n");
    => 0x0000000000400543 <main+19>:    bf f0 05 40 00  mov    $0x4005f0,%edi
       0x0000000000400548 <main+24>:    e8 c3 fe ff ff  callq  0x400410 <puts@plt>
    (gdb) si
    0x0000000000400548  14      printf("1\n");
    0x0000000000400543 <main+19>:    bf f0 05 40 00  mov    $0x4005f0,%edi
    => 0x0000000000400548 <main+24>:    e8 c3 fe ff ff  callq  0x400410 <puts@plt>
    (gdb) 
    0x0000000000400410 in puts@plt ()
    => 0x0000000000400410 <puts@plt+0>: ff 25 02 0c 20 00   jmpq   *0x200c02(%rip)        # 0x601018 <puts@got.plt>

    (gdb) set disassemble-next-line auto 
    (gdb) start 
    Temporary breakpoint 1 at 0x400543: file 1.c, line 14.
    Starting program: /home/teawater/tmp/a.out 

    Temporary breakpoint 1, main (argc=1, argv=0x7fffffffdf38, envp=0x7fffffffdf48) at 1.c:14
    14      printf("1\n");
    (gdb) si
    0x0000000000400548  14      printf("1\n");
    (gdb) 
    0x0000000000400410 in puts@plt ()
    => 0x0000000000400410 <puts@plt+0>: ff 25 02 0c 20 00   jmpq   *0x200c02(%rip)        # 0x601018 <puts@got.plt>
    (gdb) 
    0x0000000000400416 in puts@plt ()
    => 0x0000000000400416 <puts@plt+6>: 68 00 00 00 00  pushq  $0x0

## 技巧

如果要在任意情況下反組合語言後面要執行的程式碼：

    (gdb) set disassemble-next-line on

如果要在後面的程式碼沒有原始碼的情況下才反組合語言後面要執行的程式碼：

    (gdb) set disassemble-next-line auto

關閉這個功能：

    (gdb) set disassemble-next-line off

---

### 將源程式和組合語言指令對映起來

## 例子

	#include <stdio.h>

	typedef struct
	{
	        int a;
	        int b;
	        int c;
	        int d;
	}ex_st;
	
	int main(void) {
	        ex_st st = {1, 2, 3, 4};
	        printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	        return 0;
	}

## 技巧一

可以用“disas /m fun”（disas是disassemble命令縮寫）命令將函式程式碼和組合語言指令對映起來，以上面程式碼為例：

	(gdb) disas /m main
	Dump of assembler code for function main:
	11      int main(void) {
	   0x00000000004004c4 <+0>:     push   %rbp
	   0x00000000004004c5 <+1>:     mov    %rsp,%rbp
	   0x00000000004004c8 <+4>:     push   %rbx
	   0x00000000004004c9 <+5>:     sub    $0x18,%rsp
	
	12              ex_st st = {1, 2, 3, 4};
	   0x00000000004004cd <+9>:     movl   $0x1,-0x20(%rbp)
	   0x00000000004004d4 <+16>:    movl   $0x2,-0x1c(%rbp)
	   0x00000000004004db <+23>:    movl   $0x3,-0x18(%rbp)
	   0x00000000004004e2 <+30>:    movl   $0x4,-0x14(%rbp)
	
	13              printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	   0x00000000004004e9 <+37>:    mov    -0x14(%rbp),%esi
	   0x00000000004004ec <+40>:    mov    -0x18(%rbp),%ecx
	   0x00000000004004ef <+43>:    mov    -0x1c(%rbp),%edx
	   0x00000000004004f2 <+46>:    mov    -0x20(%rbp),%ebx
	   0x00000000004004f5 <+49>:    mov    $0x400618,%eax
	   0x00000000004004fa <+54>:    mov    %esi,%r8d
	   0x00000000004004fd <+57>:    mov    %ebx,%esi
	   0x00000000004004ff <+59>:    mov    %rax,%rdi
	   0x0000000000400502 <+62>:    mov    $0x0,%eax
	   0x0000000000400507 <+67>:    callq  0x4003b8 <printf@plt>
	
	14              return 0;
	   0x000000000040050c <+72>:    mov    $0x0,%eax
	
	15      }
	   0x0000000000400511 <+77>:    add    $0x18,%rsp
	   0x0000000000400515 <+81>:    pop    %rbx
	   0x0000000000400516 <+82>:    leaveq
	   0x0000000000400517 <+83>:    retq
	
	End of assembler dump.

可以看到每一條C語句下面是對應的組合語言程式碼。

## 技巧二

如果只想檢視某一行所對應的地址範圍，可以：

	(gdb) i line 13
	Line 13 of "foo.c" starts at address 0x4004e9 <main+37> and ends at 0x40050c <main+72>.	


如果只想檢視這一條語句對應的組合語言程式碼，可以使用“`disassemble [Start],[End]`”命令：  

	(gdb) disassemble 0x4004e9, 0x40050c
	Dump of assembler code from 0x4004e9 to 0x40050c:
	   0x00000000004004e9 <main+37>:        mov    -0x14(%rbp),%esi
	   0x00000000004004ec <main+40>:        mov    -0x18(%rbp),%ecx
	   0x00000000004004ef <main+43>:        mov    -0x1c(%rbp),%edx
	   0x00000000004004f2 <main+46>:        mov    -0x20(%rbp),%ebx
	   0x00000000004004f5 <main+49>:        mov    $0x400618,%eax
	   0x00000000004004fa <main+54>:        mov    %esi,%r8d
	   0x00000000004004fd <main+57>:        mov    %ebx,%esi
	   0x00000000004004ff <main+59>:        mov    %rax,%rdi
	   0x0000000000400502 <main+62>:        mov    $0x0,%eax
	   0x0000000000400507 <main+67>:        callq  0x4003b8 <printf@plt>
	End of assembler dump.

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Machine-Code.html)

---

### 顯示將要執行的組合語言指令

## 例子

	#include <stdio.h>
	int global_var;
	
	void change_var(){
	    global_var=100;
	}
	
	int main(void){
	    change_var();
	    return 0;
	}


## 技巧

使用gdb除錯組合語言程式時，可以用“`display /i $pc`”命令顯示當程式停止時，將要執行的組合語言指令。以上面程式為例：

	(gdb) start
	Temporary breakpoint 1 at 0x400488: file a.c, line 9.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:9
	9           change_var();
	(gdb) display /i $pc
	1: x/i $pc
	=> 0x400488 <main+4>:   mov    $0x0,%eax
	(gdb) si
	0x000000000040048d      9           change_var();
	1: x/i $pc
	=> 0x40048d <main+9>:   callq  0x400474 <change_var>
	(gdb)
	change_var () at a.c:4
	4       void change_var(){
	1: x/i $pc
	=> 0x400474 <change_var>:       push   %rbp

可以看到打印出了將要執行的組合語言指令。此外也可以一次顯示多條指令：

	(gdb) display /3i $pc
	2: x/3i $pc
	=> 0x400474 <change_var>:       push   %rbp
	   0x400475 <change_var+1>:     mov    %rsp,%rbp
	   0x400478 <change_var+4>:     movl   $0x64,0x2003de(%rip)        # 0x600860 <global_var>
可以看到一次顯示了`3`條指令。

取消顯示可以用`undisplay`命令。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Auto-Display.html)

---

### 列印暫存器的值

## 技巧
用gdb除錯程式時，如果想檢視暫存器的值，可以使用“i registers”命令（i是info命令縮寫），例如:  

    (gdb) i registers
    rax            0x7ffff7dd9f60   140737351884640
    rbx            0x0      0
    rcx            0x0      0
    rdx            0x7fffffffe608   140737488348680
    rsi            0x7fffffffe5f8   140737488348664
    rdi            0x1      1
    rbp            0x7fffffffe510   0x7fffffffe510
    rsp            0x7fffffffe4c0   0x7fffffffe4c0
    r8             0x7ffff7dd8300   140737351877376
    r9             0x7ffff7deb9e0   140737351956960
    r10            0x7fffffffe360   140737488348000
    r11            0x7ffff7a68be0   140737348275168
    r12            0x4003e0 4195296
    r13            0x7fffffffe5f0   140737488348656
    r14            0x0      0
    r15            0x0      0
    rip            0x4004cd 0x4004cd <main+9>
    eflags         0x206    [ PF IF ]
    cs             0x33     51
    ss             0x2b     43
    ds             0x0      0
    es             0x0      0
    fs             0x0      0
    gs             0x0      0
以上輸出不包括浮點暫存器和向量暫存器的內容。使用“i all-registers”命令，可以輸出所有暫存器的內容：
	

    (gdb) i all-registers
    	rax            0x7ffff7dd9f60   140737351884640
    	rbx            0x0      0
    	rcx            0x0      0
    	rdx            0x7fffffffe608   140737488348680
    	rsi            0x7fffffffe5f8   140737488348664
    	rdi            0x1      1
    	rbp            0x7fffffffe510   0x7fffffffe510
    	rsp            0x7fffffffe4c0   0x7fffffffe4c0
    	r8             0x7ffff7dd8300   140737351877376
    	r9             0x7ffff7deb9e0   140737351956960
    	r10            0x7fffffffe360   140737488348000
    	r11            0x7ffff7a68be0   140737348275168
    	r12            0x4003e0 4195296
    	r13            0x7fffffffe5f0   140737488348656
    	r14            0x0      0
    	r15            0x0      0
    	rip            0x4004cd 0x4004cd <main+9>
    	eflags         0x206    [ PF IF ]
    	cs             0x33     51
    	ss             0x2b     43
    	ds             0x0      0
    	es             0x0      0
    	fs             0x0      0
    	gs             0x0      0
    	st0            0        (raw 0x00000000000000000000)
    	st1            0        (raw 0x00000000000000000000)
    	st2            0        (raw 0x00000000000000000000)
    	st3            0        (raw 0x00000000000000000000)
    	st4            0        (raw 0x00000000000000000000)
    	st5            0        (raw 0x00000000000000000000)
    	st6            0        (raw 0x00000000000000000000)
    	st7            0        (raw 0x00000000000000000000)
    	......

要列印單個暫存器的值，可以使用“i registers regname”或者“p $regname”，例如：

    (gdb) i registers eax
    eax            0xf7dd9f60       -136470688
    (gdb) p $eax
    $1 = -136470688

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Registers.html).

---

### 顯示程式原始機器碼

## 例子

	#include <stdio.h>

	int main(void)
	{
	        printf("Hello, world\n");
	        return 0;
	}



## 技巧

使用“disassemble /r”命令可以用16進位制形式顯示程式的原始機器碼。以上面程式為例：

	(gdb) disassemble /r main
	Dump of assembler code for function main:
	   0x0000000000400530 <+0>:     55      push   %rbp
	   0x0000000000400531 <+1>:     48 89 e5        mov    %rsp,%rbp
	   0x0000000000400534 <+4>:     bf e0 05 40 00  mov    $0x4005e0,%edi
	   0x0000000000400539 <+9>:     e8 d2 fe ff ff  callq  0x400410 <puts@plt>
	   0x000000000040053e <+14>:    b8 00 00 00 00  mov    $0x0,%eax
	   0x0000000000400543 <+19>:    5d      pop    %rbp
	   0x0000000000400544 <+20>:    c3      retq
	End of assembler dump.
	(gdb) disassemble /r 0x0000000000400534,+4
	Dump of assembler code from 0x400534 to 0x400538:
	   0x0000000000400534 <main+4>: bf e0 05 40 00  mov    $0x4005e0,%edi
	End of assembler dump.
	

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Machine-Code.html)

---

## 改變程式的執行

### 改變字串的值

## 例子
	#include <stdio.h>

	int main(void)
	{
		char p1[] = "Sam";
		char *p2 = "Bob";
		
		printf("p1 is %s, p2 is %s\n", p1, p2);
		return 0;
	}



## 技巧
使用gdb除錯程式時，可以用“`set`”命令改變字串的值，以上面程式為例：  

	(gdb) start
	Temporary breakpoint 1 at 0x8050af0: file a.c, line 5.
	Starting program: /data1/nan/a 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Temporary breakpoint 1, main () at a.c:5
	5               char p1[] = "Sam";
	(gdb) n
	6               char *p2 = "Bob";
	(gdb) 
	8               printf("p1 is %s, p2 is %s\n", p1, p2);
	(gdb) set main::p1="Jil"
	(gdb) set main::p2="Bill"
	(gdb) n
	p1 is Jil, p2 is Bill
	9               return 0;
可以看到執行`p1`和`p2`的字串都發生了變化。也可以透過訪問記憶體地址的方法改變字串的值：  

	Starting program: /data1/nan/a 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Temporary breakpoint 2, main () at a.c:5
	5               char p1[] = "Sam";
	(gdb) n
	6               char *p2 = "Bob";
	(gdb) p p1
	$1 = "Sam"
	(gdb) p &p1
	$2 = (char (*)[4]) 0x80477a4
	(gdb) set {char [4]} 0x80477a4 = "Ace"
	(gdb) n
	8               printf("p1 is %s, p2 is %s\n", p1, p2);
	(gdb) 
	p1 is Ace, p2 is Bob
	9               return 0;

在改變字串的值時候，一定要注意記憶體越界的問題。  
參見[stackoverflow](http://stackoverflow.com/questions/19503057/in-gdb-how-can-i-write-a-string-to-memory).

---

### 設定變數的值

## 例子

	#include <stdio.h>

    int func(void)
    {
        int i = 2;

        return i;
    }

    int main(void)
    {
        int a = 0;

        a = func();
        printf("%d\n", a);
        return 0;
    }

## 技巧

在gdb中，可以用“`set var variable=expr`”命令設定變數的值，以上面程式碼為例：


	Breakpoint 2, func () at a.c:5
	5                   int i = 2;
	(gdb) n
	7                   return i;
	(gdb) set var i = 8
	(gdb) p i
	$4 = 8


	
可以看到在`func`函數里用`set`命令把`i`的值修改成為`8`。  

也可以用“`set {type}address=expr`”的方式，含義是給儲存地址在`address`，變數型別為`type`的變數賦值，仍以上面程式碼為例：  

	Breakpoint 2, func () at a.c:5
	5                   int i = 2;
	(gdb) n
	7                   return i;
	(gdb) p &i
	$5 = (int *) 0x8047a54
	(gdb) set {int}0x8047a54 = 8
	(gdb) p i
	$6 = 8

可以看到`i`的值被修改成為`8`。

另外暫存器也可以作為變數，因此同樣可以修改暫存器的值：

	Breakpoint 2, func () at a.c:5
	5                   int i = 2;
	(gdb)
	(gdb) n
	7                   return i;
	(gdb)
	8               }
	(gdb) set var $eax = 8
	(gdb) n
	main () at a.c:15
	15                  printf("%d\n", a);
	(gdb)
	8
	16                  return 0;

可以看到因為eax暫存器儲存著函式的返回值，所以當把eax暫存器的值改為`8`後，函式的返回值也變成了`8`。  

詳情參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Assignment.html#Assignment)

---

### 修改PC暫存器的值

## 例子
	#include <stdio.h>
	int main(void)
	{       
	        int a =0;               
	
	        a++;    
	        a++;    
	        printf("%d\n", a);      
	        return 0;
	}


## 技巧
PC暫存器會儲存程式下一條要執行的指令，透過修改這個暫存器的值，可以達到改變程式執行流程的目的。  
上面的程式會輸出“`a=2`”，下面介紹一下如何透過修改PC暫存器的值，改變程式執行流程。  

	4               int a =0;
	(gdb) disassemble main
	Dump of assembler code for function main:
	0x08050921 <main+0>:    push   %ebp
	0x08050922 <main+1>:    mov    %esp,%ebp
	0x08050924 <main+3>:    sub    $0x8,%esp
	0x08050927 <main+6>:    and    $0xfffffff0,%esp
	0x0805092a <main+9>:    mov    $0x0,%eax
	0x0805092f <main+14>:   add    $0xf,%eax
	0x08050932 <main+17>:   add    $0xf,%eax
	0x08050935 <main+20>:   shr    $0x4,%eax
	0x08050938 <main+23>:   shl    $0x4,%eax
	0x0805093b <main+26>:   sub    %eax,%esp
	0x0805093d <main+28>:   movl   $0x0,-0x4(%ebp)
	0x08050944 <main+35>:   lea    -0x4(%ebp),%eax
	0x08050947 <main+38>:   incl   (%eax)
	0x08050949 <main+40>:   lea    -0x4(%ebp),%eax
	0x0805094c <main+43>:   incl   (%eax)
	0x0805094e <main+45>:   sub    $0x8,%esp
	0x08050951 <main+48>:   pushl  -0x4(%ebp)
	0x08050954 <main+51>:   push   $0x80509b4
	0x08050959 <main+56>:   call   0x80507cc <printf@plt>
	0x0805095e <main+61>:   add    $0x10,%esp
	0x08050961 <main+64>:   mov    $0x0,%eax
	0x08050966 <main+69>:   leave
	0x08050967 <main+70>:   ret
	End of assembler dump.
	(gdb) info line 6
	Line 6 of "a.c" starts at address 0x8050944 <main+35> and ends at 0x8050949 <main+40>.
	(gdb) info line 7
	Line 7 of "a.c" starts at address 0x8050949 <main+40> and ends at 0x805094e <main+45>.

透過“`info line 6`”和“`info line 7`”命令可以知道兩條“`a++;`”語句的組合語言指令起始地址分別是`0x8050944`和`0x8050949`。

    (gdb) n
	6               a++;
	(gdb) p $pc
	$3 = (void (*)()) 0x8050944 <main+35>
	(gdb) set var $pc=0x08050949
當程式要執行第一條“`a++;`”語句時，列印`pc`暫存器的值，看到`pc`暫存器的值為`0x8050944`，與“`info line 6`”命令得到的一致。接下來，把`pc`暫存器的值改為`0x8050949`，也就是透過“`info line 7`”命令得到的第二條“`a++;`”語句的起始地址。

	(gdb) n
	8               printf("a=%d\n", a);
	(gdb)
	a=1
	9               return 0;

接下來執行，可以看到程式輸出“`a=1`”，也就是跳過了第一條“`a++;`”語句。

---

### 跳轉到指定位置執行

## 例子

	#include <stdio.h>
	
	void fun (int x)
	{
	  if (x < 0)
	    puts ("error");
	}
	
	int main (void)
	{
	  int i = 1;
	
	  fun (i--);
	  fun (i--);
	  fun (i--);
	
	  return 0;
	}

## 技巧

當除錯程式時，你可能不小心走過了出錯的地方：

	(gdb) n
	13	  fun (i--);
	(gdb) 
	14	  fun (i--);
	(gdb) 
	15	  fun (i--);
	(gdb) 
	error
	17	  return 0;

看起來是在15行，呼叫fun的時候出錯了。常見的辦法是在15行設定個斷點，然後從頭`run`一次。

如果你的環境支援反向執行，那麼更好了。

如果不支援，你也可以直接`jump`到15行，再執行一次：

	(gdb) b 15
	Breakpoint 2 at 0x40056a: file jump.c, line 15.
	(gdb) j 15
	Continuing at 0x40056a.
	
	Breakpoint 2, main () at jump.c:15
	15	  fun (i--);
	(gdb) s
	fun (x=-2) at jump.c:5
	5	  if (x < 0)
	(gdb) n
	6	    puts ("error");

需要注意的是：

1. `jump`命令只改變pc的值，所以改變程式執行可能會出現不同的結果，比如變數i的值
2. 透過（臨時）斷點的配合，可以讓你的程式跳到指定的位置，並停下來

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Jumping.html#Jumping)

---

### 使用斷點命令改變程式的執行

## 例子

	#include <stdio.h>
	#include <stdlib.h>
	
	void drawing (int n)
	{
	  if (n != 0)
	    puts ("Try again?\nAll you need is a dollar, and a dream.");
	  else
	    puts ("You win $3000!");
	}
	
	int main (void)
	{
	  int n;
	
	  srand (time (0));
	  n = rand () % 10;
	  printf ("Your number is %d\n", n);
	  drawing (n);
	
	  return 0;
	}

## 技巧

這個例子程式可能不太好，只是可以用來演示下斷點命令的用法：

	(gdb) b drawing
	Breakpoint 1 at 0x40064d: file win.c, line 6.
	(gdb) command 1
	Type commands for breakpoint(s) 1, one per line.
	End with a line saying just "end".
	>silent
	>set variable n = 0
	>continue
	>end
	(gdb) r
	Starting program: /home/xmj/tmp/a.out 
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
	Your number is 6
	You win $3000!
	[Inferior 1 (process 4134) exited normally]

可以看到，當程式執行到斷點處，會自動把變數n的值修改為0，然後繼續執行。

如果你在除錯一個大程式，重新編譯一次會花費很長時間，比如除錯編譯器的bug，那麼你可以用這種方式在gdb中先實驗性的修改下試試，而不需要修改原始碼，重新編譯。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Break-Commands.html#Break-Commands)

---

### 修改被除錯程式的二進位制檔案

## 例子

	#include <stdio.h>
	#include <stdlib.h>
	
	void drawing (int n)
	{
	  if (n != 0)
	    puts ("Try again?\nAll you need is a dollar, and a dream.");
	  else
	    puts ("You win $3000!");
	}
	
	int main (void)
	{
	  int n;
	
	  srand (time (0));
	  n = rand () % 10;
	  printf ("Your number is %d\n", n);
	  drawing (n);
	
	  return 0;
	}

## 技巧

gdb不僅可以用來除錯程式，還可以修改程式的二進位制程式碼。

預設情況下，gdb是以只讀方式載入程式的。可以透過命令列選項指定為可寫：

	$ gcc -write ./a.out
	(gdb) show write
	Writing into executable and core files is on.

也可以在gdb中，使用命令設定並重新載入程式：

	(gdb) set write on
	(gdb) file ./a.out

接下來，檢視反組合語言：

	(gdb) disassemble /mr drawing 
	Dump of assembler code for function drawing:
	5	{
	   0x0000000000400642 <+0>:	55	push   %rbp
	   0x0000000000400643 <+1>:	48 89 e5	mov    %rsp,%rbp
	   0x0000000000400646 <+4>:	48 83 ec 10	sub    $0x10,%rsp
	   0x000000000040064a <+8>:	89 7d fc	mov    %edi,-0x4(%rbp)
	
	6	  if (n != 0)
	   0x000000000040064d <+11>:	83 7d fc 00	cmpl   $0x0,-0x4(%rbp)
	   0x0000000000400651 <+15>:	74 0c	je     0x40065f <drawing+29>
	
	7	    puts ("Try again?\nAll you need is a dollar, and a dream.");
	   0x0000000000400653 <+17>:	bf e0 07 40 00	mov    $0x4007e0,%edi
	   0x0000000000400658 <+22>:	e8 b3 fe ff ff	callq  0x400510 <puts@plt>
	   0x000000000040065d <+27>:	eb 0a	jmp    0x400669 <drawing+39>
	
	8	  else
	9	    puts ("You win $3000!");
	   0x000000000040065f <+29>:	bf 12 08 40 00	mov    $0x400812,%edi
	   0x0000000000400664 <+34>:	e8 a7 fe ff ff	callq  0x400510 <puts@plt>
	
	10	}
	   0x0000000000400669 <+39>:	c9	leaveq 
	   0x000000000040066a <+40>:	c3	retq   
	
	End of assembler dump.

修改二進位制程式碼（注意大小端和指令長度）：

	(gdb) set variable *(short*)0x400651=0x0ceb
	(gdb) disassemble /mr drawing 
	Dump of assembler code for function drawing:
	5	{
	   0x0000000000400642 <+0>:	55	push   %rbp
	   0x0000000000400643 <+1>:	48 89 e5	mov    %rsp,%rbp
	   0x0000000000400646 <+4>:	48 83 ec 10	sub    $0x10,%rsp
	   0x000000000040064a <+8>:	89 7d fc	mov    %edi,-0x4(%rbp)
	
	6	  if (n != 0)
	   0x000000000040064d <+11>:	83 7d fc 00	cmpl   $0x0,-0x4(%rbp)
	   0x0000000000400651 <+15>:	eb 0c	jmp    0x40065f <drawing+29>
	
	7	    puts ("Try again?\nAll you need is a dollar, and a dream.");
	   0x0000000000400653 <+17>:	bf e0 07 40 00	mov    $0x4007e0,%edi
	   0x0000000000400658 <+22>:	e8 b3 fe ff ff	callq  0x400510 <puts@plt>
	   0x000000000040065d <+27>:	eb 0a	jmp    0x400669 <drawing+39>
	
	8	  else
	9	    puts ("You win $3000!");
	   0x000000000040065f <+29>:	bf 12 08 40 00	mov    $0x400812,%edi
	   0x0000000000400664 <+34>:	e8 a7 fe ff ff	callq  0x400510 <puts@plt>
	
	10	}
	   0x0000000000400669 <+39>:	c9	leaveq 
	   0x000000000040066a <+40>:	c3	retq   
	
	End of assembler dump.

可以看到，條件跳轉指令“je”已經被改為無條件跳轉“jmp”了。

退出，執行一下：

	$ ./a.out 
	Your number is 2
	You win $3000!

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Patching.html#Patching)

---

## 訊號

### 檢視訊號處理資訊

## 例子
	#include <stdio.h>
	#include <signal.h>
	
	void handler(int sig);
	
	void handler(int sig)
	{
	        signal(sig, handler);
	        printf("Receive signal: %d\n", sig);
	}
	
	int main(void) {
	        signal(SIGINT, handler);
	        signal(SIGALRM, handler);
	        
	        while (1)
	        {
	                sleep(1);
	        }
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以用“`i signals`”命令（或者“`i handle`”命令，`i`是`info`命令縮寫）檢視gdb如何處理程序收到的訊號:  

	(gdb) i signals 
	Signal        Stop      Print   Pass to program Description
	
	SIGHUP        Yes       Yes     Yes             Hangup
	SIGINT        Yes       Yes     No              Interrupt
	SIGQUIT       Yes       Yes     Yes             Quit
	......
	SIGALRM       No        No      Yes             Alarm clock
	......

第一項（`Signal`）：標示每個訊號。  
第二項（`Stop`）：表示被除錯的程式有對應的訊號發生時，gdb是否會暫停程式。  
第三項（`Print`）：表示被除錯的程式有對應的訊號發生時，gdb是否會列印相關資訊。  
第四項（`Pass to program`）：gdb是否會把這個訊號發給被除錯的程式。  
第五項（`Description`）：訊號的描述資訊。

從上面的輸出可以看到，當`SIGINT`訊號發生時，gdb會暫停被除錯的程式，並列印相關資訊，但不會把這個訊號發給被除錯的程式。而當`SIGALRM`訊號發生時，gdb不會暫停被除錯的程式，也不列印相關資訊，但會把這個訊號發給被除錯的程式。  

啟動gdb除錯上面的程式，同時另起一個終端，先後傳送`SIGINT`和`SIGALRM`訊號給被除錯的程序，輸出如下：  

	Program received signal SIGINT, Interrupt.
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) c
	Continuing.
	Receive signal: 14

可以看到收到`SIGINT`時，程式暫停了，也輸出了訊號資訊，但並沒有把`SIGINT`訊號交由程序處理（程式沒有輸出）。而收到`SIGALRM`訊號時，程式沒有暫停，也沒有輸出訊號資訊，但把`SIGALRM`訊號交由程序處理了（程式列印了輸出）。


參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Signals.html).

---

### 訊號發生時是否暫停程式

## 例子
	#include <stdio.h>
	#include <signal.h>
	
	void handler(int sig);
	
	void handler(int sig)
	{
	        signal(sig, handler);
	        printf("Receive signal: %d\n", sig);
	}
	
	int main(void) {
	        signal(SIGHUP, handler);
	        
	        while (1)
	        {
	                sleep(1);
	        }
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以用“`handle signal stop/nostop`”命令設定當訊號發生時，是否暫停程式的執行，以上面程式為例:  

	(gdb) i signals 
	Signal        Stop      Print   Pass to program Description
	
	SIGHUP        Yes       Yes     Yes             Hangup
	......

	(gdb) r
	Starting program: /data1/nan/test 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	
	Program received signal SIGHUP, Hangup.
	[Switching to Thread 1 (LWP 1)]
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) c
	Continuing.
	Receive signal: 1

可以看到，預設情況下，發生`SIGHUP`訊號時，gdb會暫停程式的執行，並列印收到訊號的資訊。此時需要執行`continue`命令繼續程式的執行。

接下來用“`handle SIGHUP nostop`”命令設定當`SIGHUP`訊號發生時，gdb不暫停程式，執行如下：

	(gdb) handle SIGHUP nostop
	Signal        Stop      Print   Pass to program Description
	SIGHUP        No        Yes     Yes             Hangup
	(gdb) c
	Continuing.
	
	Program received signal SIGHUP, Hangup.
	Receive signal: 1
可以看到，程式收到`SIGHUP`訊號發生時，沒有暫停，而是繼續執行。

如果想恢復之前的行為，用“`handle SIGHUP stop`”命令即可。需要注意的是，設定`stop`的同時，預設也會設定`print`（關於`print`，請參見[訊號發生時是否列印訊號資訊](print-signal.md)）。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Signals.html).

---

### 訊號發生時是否列印訊號資訊

## 例子
	#include <stdio.h>
	#include <signal.h>
	
	void handler(int sig);
	
	void handler(int sig)
	{
	        signal(sig, handler);
	        printf("Receive signal: %d\n", sig);
	}
	
	int main(void) {
	        signal(SIGHUP, handler);
	        
	        while (1)
	        {
	                sleep(1);
	        }
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以用“`handle signal print/noprint`”命令設定當訊號發生時，是否列印訊號資訊，以上面程式為例:  

	(gdb) i signals 
	Signal        Stop      Print   Pass to program Description
	
	SIGHUP        Yes       Yes     Yes             Hangup
	......

	(gdb) r
	Starting program: /data1/nan/test 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	
	Program received signal SIGHUP, Hangup.
	[Switching to Thread 1 (LWP 1)]
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) c
	Continuing.
	Receive signal: 1

可以看到，預設情況下，發生`SIGHUP`訊號時，gdb會暫停程式的執行，並列印收到訊號的資訊。此時需要執行`continue`命令繼續程式的執行。

接下來用“`handle SIGHUP noprint`”命令設定當`SIGHUP`訊號發生時，gdb不列印訊號資訊，執行如下：

	(gdb) handle SIGHUP noprint 
	Signal        Stop      Print   Pass to program Description
	SIGHUP        No        No      Yes             Hangup
	(gdb) r
	Starting program: /data1/nan/test 
	[Thread debugging using libthread_db enabled]
	Receive signal: 1

需要注意的是，設定`noprint`的同時，預設也會設定`nostop`。可以看到，程式收到`SIGHUP`訊號發生時，沒有暫停，也沒有列印訊號資訊。而是繼續執行。

如果想恢復之前的行為，用“`handle SIGHUP print`”命令即可。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Signals.html).

---

### 訊號發生時是否把訊號丟給程式處理

## 例子
	#include <stdio.h>
	#include <signal.h>
	
	void handler(int sig);
	
	void handler(int sig)
	{
	        signal(sig, handler);
	        printf("Receive signal: %d\n", sig);
	}
	
	int main(void) {
	        signal(SIGHUP, handler);
	        
	        while (1)
	        {
	                sleep(1);
	        }
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以用“`handle signal pass(noignore)/nopass(ignore)`”命令設定當訊號發生時，是否把訊號丟給程式處理.其中`pass`和`noignore`含義相同，`nopass`和`ignore`含義相同。以上面程式為例:  

	(gdb) i signals 
	Signal        Stop      Print   Pass to program Description
	
	SIGHUP        Yes       Yes     Yes             Hangup
	......

	(gdb) r
	Starting program: /data1/nan/test 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	
	Program received signal SIGHUP, Hangup.
	[Switching to Thread 1 (LWP 1)]
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) c
	Continuing.
	Receive signal: 1

可以看到，預設情況下，發生`SIGHUP`訊號時，gdb會把訊號丟給程式處理。

接下來用“`handle SIGHUP nopass`”命令設定當`SIGHUP`訊號發生時，gdb不把訊號丟給程式處理，執行如下：

	(gdb) handle SIGHUP nopass
	Signal        Stop      Print   Pass to program Description
	SIGHUP        Yes       Yes     No              Hangup
	(gdb) c
	Continuing.
	
	Program received signal SIGHUP, Hangup.
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) c
	Continuing.
可以看到，`SIGHUP`訊號發生時，程式沒有列印“Receive signal: 1”，說明gdb沒有把訊號丟給程式處理。

如果想恢復之前的行為，用“`handle SIGHUP pass`”命令即可。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Signals.html).

---

### 給程式傳送訊號

## 例子
	#include <stdio.h>
	#include <signal.h>
	
	void handler(int sig);
	
	void handler(int sig)
	{
	        signal(sig, handler);
	        printf("Receive signal: %d\n", sig);
	}
	
	int main(void) {
	        signal(SIGHUP, handler);
	        
	        while (1)
	        {
	                sleep(1);
	        }
	        return 0;
	}

## 技巧
用gdb除錯程式的過程中，當被除錯程式停止後，可以用“`signal signal_name`”命令讓程式繼續執行，但會立即給程式傳送訊號。以上面程式為例:  

	(gdb) r
	`/data1/nan/test' has changed; re-reading symbols.
	Starting program: /data1/nan/test 
	[Thread debugging using libthread_db enabled]
	^C[New Thread 1 (LWP 1)]
	
	Program received signal SIGINT, Interrupt.
	[Switching to Thread 1 (LWP 1)]
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) signal SIGHUP
	Continuing with signal SIGHUP.
	Receive signal: 1

可以看到，當程式暫停後，執行`signal SIGHUP`命令，gdb會發送訊號給程式處理。

可以使用“`signal 0`”命令使程式重新執行，但不傳送任何訊號給程序。仍以上面程式為例：

	Program received signal SIGHUP, Hangup.
	0xfeeeae55 in ___nanosleep () from /lib/libc.so.1
	(gdb) signal 0
	Continuing with no signal.

可以看到，`SIGHUP`訊號發生時，gdb停住了程式，但是由於執行了“`signal 0`”命令，所以程式重新執行後，並沒有收到`SIGHUP`訊號。

使用`signal`命令和在shell環境使用`kill`命令給程式傳送訊號的區別在於：在shell環境使用`kill`命令給程式傳送訊號，gdb會根據當前的設定決定是否把訊號傳送給程序，而使用`signal`命令則直接把訊號發給程序。

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Signaling.html#Signaling).

---

### 使用“$_siginfo”變數

## 例子
	#include <stdio.h>
	#include <signal.h>
	
	void handler(int sig);
	
	void handler(int sig)
	{
	        signal(sig, handler);
	        printf("Receive signal: %d\n", sig);
	}
	
	int main(void) {
	        signal(SIGHUP, handler);
	        
	        while (1)
	        {
	                sleep(1);
	        }
	        return 0;
	}

## 技巧
在某些平臺上（比如Linux）使用gdb除錯程式，當有訊號發生時，gdb在把訊號丟給程式之前，可以透過`$_siginfo`變數讀取一些額外的有關當前訊號的資訊，這些資訊是`kernel`傳給訊號處理函式的。以上面程式為例:  

	Program received signal SIGHUP, Hangup.
	0x00000034e42accc0 in __nanosleep_nocancel () from /lib64/libc.so.6
	Missing separate debuginfos, use: debuginfo-install glibc-2.12-1.132.el6.x86_64
	(gdb) ptype $_siginfo
	type = struct {
	    int si_signo;
	    int si_errno;
	    int si_code;
	    union {
	        int _pad[28];
	        struct {...} _kill;
	        struct {...} _timer;
	        struct {...} _rt;
	        struct {...} _sigchld;
	        struct {...} _sigfault;
	        struct {...} _sigpoll;
	    } _sifields;
	}
	(gdb) ptype $_siginfo._sifields._sigfault
	type = struct {
	    void *si_addr;
	}
	(gdb) p $_siginfo._sifields._sigfault.si_addr
	$1 = (void *) 0x850e

我們可以瞭解`$_siginfo`變數裡每個成員的型別，並且可以讀到成員的值。


參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Signaling.html#Signaling).

---

## 共享庫

### 顯示共享連結庫資訊

## 例子
	#include <hiredis/hiredis.h>

	int main(void)
	{
	        char a[1026] = {0};
	        redisContext *c = NULL;
	        void *reply = NULL;
	
	        memset(a, 'a', (sizeof(a) - 1));
	        c = redisConnect("127.0.0.1", 6379);
	        if (NULL != c)
	        {
	              reply = redisCommand(c, "set 1 %s", a);
	              freeReplyObject(reply);
	
	              reply = redisCommand(c, "get 1");
	              freeReplyObject(reply);
	
	              redisFree(c);
	        }
	        return 0;
	}


## 技巧
使用"`info sharedlibrary regex`"命令可以顯示程式載入的共享連結庫資訊，其中`regex`可以是正則表示式，意為顯示名字符合`regex`的共享連結庫。如果沒有`regex`，則列出所有的庫。以上面程式為例:
	
	(gdb) start
	Temporary breakpoint 1 at 0x109f0: file a.c, line 5.
	Starting program: /export/home/nan/a
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Temporary breakpoint 1, main () at a.c:5
	5                       char a[1026] = {0};
	(gdb) info sharedlibrary
	From        To          Syms Read   Shared Object Library
	0xff3b44a0  0xff3e3490  Yes (*)     /usr/lib/ld.so.1
	0xff3325f0  0xff33d4b4  Yes         /usr/local/lib/libhiredis.so.0.11
	0xff3137f0  0xff31a9f4  Yes (*)     /lib/libsocket.so.1
	0xff215fd4  0xff28545c  Yes (*)     /lib/libnsl.so.1
	0xff0a3a20  0xff14fedc  Yes (*)     /lib/libc.so.1
	0xff320400  0xff3234c8  Yes (*)     /platform/SUNW,UltraAX-i2/lib/libc_psr.so.1
	(*): Shared library is missing debugging information.

可以看到列出所有載入的共享連結庫資訊，帶“`*`”表示庫缺少除錯資訊。  

另外也可以使用正則表示式：

	(gdb) i sharedlibrary hiredi*
	From        To          Syms Read   Shared Object Library
	0xff3325f0  0xff33d4b4  Yes         /usr/local/lib/libhiredis.so.0.11

可以看到只列出了一個庫資訊。  
參見[gdb手冊](https://sourceware.org/gdb/current/onlinedocs/gdb/Files.html#index-shared-libraries).

---

## 指令碼

### 配置gdb init檔案

## 技巧

當gdb啟動時，會讀取HOME目錄和當前目錄下的的配置檔案，執行裡面的命令。這個檔案通常為“.gdbinit”。

這裡給出了本文件中介紹過的，可以放在“.gdbinit”中的一些配置：

	# 列印STL容器中的內容
	python
	import sys
	sys.path.insert(0, "/home/xmj/project/gcc-trunk/libstdc++-v3/python")
	from libstdcxx.v6.printers import register_libstdcxx_printers
	register_libstdcxx_printers (None)
	end
	
	# 儲存歷史命令
	set history filename ~/.gdb_history
	set history save on
	
	# 退出時不顯示提示資訊
	set confirm off
	
	# 按照派生型別列印物件
	set print object on
	
	# 列印陣列的索引下標
	set print array-indexes on
	
	# 每行列印一個結構體成員
	set print pretty on

歡迎補充。

---

### 按何種方式解析指令碼檔案

## 例子

	#include <stdio.h>

	typedef struct
	{
	        int a;
	        int b;
	        int c;
	        int d;
	}ex_st;
	
	int main(void) {
	        ex_st st = {1, 2, 3, 4};
	        printf("%d,%d,%d,%d\n", st.a, st.b, st.c, st.d);
	        return 0;
	}



## 技巧

gdb支援的指令碼檔案分為兩種：一種是隻包含gdb自身命令的指令碼，例如“.gdbinit”檔案，當gdb在啟動時，就會執行“.gdbinit”檔案中的命令；此外，gdb還支援其它一些語言寫的指令碼檔案（比如python）。  
gdb用“`set script-extension`”命令來決定按何種格式來解析指令碼檔案。它可以取3個值：  
a）`off`：所有的指令碼檔案都解析成gdb的命令指令碼；  
b）`soft`：根據指令碼副檔名決定如何解析指令碼。如果gdb支援解析這種指令碼語言（比如python），就按這種語言解析，否則就按命令指令碼解析；  
c）`strict`：根據指令碼副檔名決定如何解析指令碼。如果gdb支援解析這種指令碼語言（比如python），就按這種語言解析，否則不解析；  
以上面程式為例，進行除錯：

	(gdb) start
	Temporary breakpoint 1 at 0x4004cd: file a.c, line 12.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:12
	12              ex_st st = {1, 2, 3, 4};
	(gdb) q
	A debugging session is active.
	
	        Inferior 1 [process 24249] will be killed.
	
	Quit anyway? (y or n) y


可以看到gdb退出時，預設行為會提示使用者是否退出。

下面寫一個指令碼檔案（gdb.py），但內容是一個gdb命令，不是真正的python指令碼。用途是退出gdb時不提示：

	set confirm off
再次開始除錯：  

	(gdb) start
	Temporary breakpoint 1 at 0x4004cd: file a.c, line 12.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:12
	12              ex_st st = {1, 2, 3, 4};
	(gdb) show script-extension
	Script filename extension recognition is "soft".
	(gdb) source gdb.py
	  File "gdb.py", line 1
	    set confirm off
	              ^
	SyntaxError: invalid syntax


可以看到“`script-extension`”預設值是`soft`，接下來執行“`source gdb.py`”,會按照pyhton語言解析gdb.py檔案，但是由於這個檔案實質上是一個gdb命令指令碼，所以解析出錯。  
再執行一次：  

	(gdb) start
	Temporary breakpoint 1 at 0x4004cd: file a.c, line 12.
	Starting program: /data2/home/nanxiao/a
	
	Temporary breakpoint 1, main () at a.c:12
	12              ex_st st = {1, 2, 3, 4};
	(gdb) set script-extension off
	(gdb) source gdb.py
	(gdb) q
	[root@linux:~]$
這次把“`script-extension`”值改為`off`，所以指令碼會按gdb命令指令碼去解析，可以看到這次指令碼命令生效了。
  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Extending-GDB.html)

---

### 儲存歷史命令

## 技巧

在gdb中，預設是不儲存歷史命令的。你可以透過如下命令來設定成儲存歷史命令：

	(gdb) set history save on

但是，歷史命令是預設儲存在了當前目錄下的.gdb_history檔案中。可以透過如下命令來設定要儲存的檔名和路徑：

	(gdb) set history filename fname

現在，我們把這兩個命令放到$HOME/.gdbinit檔案中：

	set history filename ~/.gdb_history
	set history save on

好了，下次啟動gdb時，你就可以直接查詢使用之前的歷史命令了。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Command-History.html#Command-History)

---

## 原始檔

### 設定原始檔查詢路徑

## 例子
	#include <stdio.h>
	#include <time.h>
	
	int main(void) {
	        time_t now = time(NULL);
	        struct tm local = {0};
	        struct tm gmt = {0};
	
	        localtime_r(&now, &local);
	        gmtime_r(&now, &gmt);
	
	        return 0;
	}




## 技巧
有時gdb不能準確地定位到原始檔的位置（比如檔案被移走了，等等），此時可以用`directory`命令設定查詢原始檔的路徑。以上面程式為例：  

	(gdb) start
	Temporary breakpoint 1 at 0x400560: file a.c, line 5.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:5
	5       a.c: No such file or directory.
	(gdb) directory ../ki/
	Source directories searched: /home/nan/../ki:$cdir:$cwd
	(gdb) n
	6               struct tm local = {0};
	(gdb)
	7               struct tm gmt = {0};
	(gdb)
	9               localtime_r(&now, &local);
	(gdb)
	10              gmtime_r(&now, &gmt);
	(gdb) q

可以看到，使用`directory`（或`dir`)命令設定原始檔的查詢目錄後，gdb就可以正常地解析原始碼了。  

如果希望在gdb啟動時，載入code的位置，避免每次在gdb中再次輸入命令，可以使用gdb的`-d` 引數
```shell
gdb -q a.out -d /search/code/some 
```

參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Source-Path.html).

---

### 替換查詢原始檔的目錄

## 例子
	#include <stdio.h>
	#include <time.h>
	
	int main(void) {
	        time_t now = time(NULL);
	        struct tm local = {0};
	        struct tm gmt = {0};
	
	        localtime_r(&now, &local);
	        gmtime_r(&now, &gmt);
	
	        return 0;
	}




## 技巧
有時除錯程式時，原始碼檔案可能已經移到其它的檔案夾了。此時可以用`set substitute-path from to`命令設定新的資料夾（`to`）目錄替換舊的（`from`）。以上面程式為例：  

	(gdb) start
	Temporary breakpoint 1 at 0x400560: file a.c, line 5.
	Starting program: /home/nan/a

	Temporary breakpoint 1, main () at a.c:5
	5       a.c: No such file or directory.
	(gdb) set substitute-path /home/nan /home/ki
	(gdb) n
	6                       struct tm local = {0};
	(gdb)
	7                       struct tm gmt = {0};
	(gdb)
	9                       localtime_r(&now, &local);
	(gdb)
	10                      gmtime_r(&now, &gmt);
	(gdb)
	12                      return 0;



除錯時，因為原始檔已經移到`/home/ki`這個資料夾下了，所以gdb找不到原始檔。使用`set substitute-path /home/nan /home/ki`命令設定原始檔的查詢目錄後，gdb就可以正常地解析原始碼了。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Source-Path.html).

---

## 圖形化介面

### 進入和退出圖形化除錯介面

## 例子
	#include <stdio.h>
	
	void fun1(void)
	{
	        int i = 0;
	
	        i++;
	        i = i * 2;
	        printf("%d\n", i);
	}
	
	void fun2(void)
	{
	        int j = 0;
	
	        fun1();
	        j++;
	        j = j * 2;
	        printf("%d\n", j);
	}
	
	int main(void)
	{
	        fun2();
	        return 0;
	}


## 技巧
啟動gdb時指定“`-tui`”引數（例如：`gdb -tui program`），或者執行gdb過程中使用“`Crtl+X+A`”組合鍵，都可以進入圖形化除錯介面。以除錯上面程式為例：  

	   ┌──a.c──────────────────────────────────────────────────────────────────────────────────────────┐
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	B+>│24              fun2();                                                                        │
	   │25              return 0;                                                                      │
	   │26      }                                                                                      │
	   │27                                                                                             │
	   │28                                                                                             │
	   │29                                                                                             │
	   │30                                                                                             │
	   │31                                                                                             │
	   │32                                                                                             │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 22141 In: main                                               Line: 24   PC: 0x40052b
	Type "apropos word" to search for commands related to "word"...
	Reading symbols from a...done.
	(gdb) start
	Temporary breakpoint 1 at 0x40052b: file a.c, line 24.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:24
	(gdb)
可以看到，顯示了當前的程式的程序號，將要執行的程式碼行號，`PC`暫存器的值。  
退出圖形化除錯介面也是用“`Crtl+X+A`”組合鍵。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/TUI.html).

---

### 顯示組合語言程式碼視窗

## 例子
	#include <stdio.h>
	
	void fun1(void)
	{
	        int i = 0;
	
	        i++;
	        i = i * 2;
	        printf("%d\n", i);
	}
	
	void fun2(void)
	{
	        int j = 0;
	
	        fun1();
	        j++;
	        j = j * 2;
	        printf("%d\n", j);
	}
	
	int main(void)
	{
	        fun2();
	        return 0;
	}


## 技巧
使用gdb圖形化除錯介面時，可以使用“`layout asm`”命令顯示組合語言程式碼視窗。以除錯上面程式為例：  

		    ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
	  >│0x40052b <main+4>               callq  0x4004f3 <fun2>                                         │
	   │0x400530 <main+9>               mov    $0x0,%eax                                               │
	   │0x400535 <main+14>              leaveq                                                         │
	   │0x400536 <main+15>              retq                                                           │
	   │0x400537                        nop                                                            │
	   │0x400538                        nop                                                            │
	   │0x400539                        nop                                                            │
	   │0x40053a                        nop                                                            │
	   │0x40053b                        nop                                                            │
	   │0x40053c                        nop                                                            │
	   │0x40053d                        nop                                                            │
	   │0x40053e                        nop                                                            │
	   │0x40053f                        nop                                                            │
	   │0x400540 <__libc_csu_fini>      repz retq                                                      │
	   │0x400542                        data16 data16 data16 data16 nopw %cs:0x0(%rax,%rax,1)          │
	   │0x400550 <__libc_csu_init>      mov    %rbp,-0x28(%rsp)                                        │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 44658 In: main                                               Line: 24   PC: 0x40052b
	
	(gdb) start
	Temporary breakpoint 1 at 0x40052b: file a.c, line 24.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:24
	(gdb)

可以看到，顯示了當前的程式的組合語言程式碼。  
如果既想顯示原始碼，又想顯示組合語言程式碼，可以使用“`layout split`”命令：  

	   ┌──a.c──────────────────────────────────────────────────────────────────────────────────────────┐
	  >│24              fun2();                                                                        │
	   │25              return 0;                                                                      │
	   │26      }                                                                                      │
	   │27                                                                                             │
	   │28                                                                                             │
	   │29                                                                                             │
	   │30                                                                                             │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	  >│0x40052b <main+4>       callq  0x4004f3 <fun2>                                                 │
	   │0x400530 <main+9>       mov    $0x0,%eax                                                       │
	   │0x400535 <main+14>      leaveq                                                                 │
	   │0x400536 <main+15>      retq                                                                   │
	   │0x400537                nop                                                                    │
	   │0x400538                nop                                                                    │
	   │0x400539                nop                                                                    │
	   │0x40053a                nop                                                                    │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 44658 In: main                                               Line: 24   PC: 0x40052b
	
	(gdb) start
	Temporary breakpoint 1 at 0x40052b: file a.c, line 24.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:24
	(gdb)

可以看到上面顯示的是原始碼，下面顯示的是組合語言程式碼。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/TUI-Commands.html).

---

### 顯示暫存器視窗

## 例子
	#include <stdio.h>
	
	void fun1(void)
	{
	        int i = 0;
	
	        i++;
	        i = i * 2;
	        printf("%d\n", i);
	}
	
	void fun2(void)
	{
	        int j = 0;
	
	        fun1();
	        j++;
	        j = j * 2;
	        printf("%d\n", j);
	}
	
	int main(void)
	{
	        fun2();
	        return 0;
	}


## 技巧
使用gdb圖形化除錯介面時，可以使用“`layout regs`”命令顯示暫存器視窗。以除錯上面程式為例：  

	┌──Register group: general─────────────────────────────────────────────────────────────────────────┐
	│rax            0x34e4590f60     227169341280     rbx            0x0      0                        │
	│rcx            0x0      0                        rdx            0x7fffffffe4b8   140737488348344  │
	│rsi            0x7fffffffe4a8   140737488348328  rdi            0x1      1                        │
	│rbp            0x7fffffffe3c0   0x7fffffffe3c0   rsp            0x7fffffffe3c0   0x7fffffffe3c0   │
	│r8             0x34e458f300     227169334016     r9             0x34e3a0e9f0     227157273072     │
	│r10            0x7fffffffe210   140737488347664  r11            0x34e421ec20     227165727776     │
	│r12            0x4003e0 4195296                  r13            0x7fffffffe4a0   140737488348320  │
	└──────────────────────────────────────────────────────────────────────────────────────────────────┘
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	  >│24              fun2();                                                                        │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 12552 In: main                                               Line: 24   PC: 0x40052b
	Reading symbols from a...done.
	(gdb) start
	Temporary breakpoint 1 at 0x40052b: file a.c, line 24.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:24
	(gdb)

可以看到，顯示了通用暫存器的內容。  
如果想檢視浮點暫存器，可以使用“`tui reg float`”命令：  

	┌──Register group: float───────────────────────────────────────────────────────────────────────────┐
	│st0            0        (raw 0x00000000000000000000)                                              │
	│st1            0        (raw 0x00000000000000000000)                                              │
	│st2            0        (raw 0x00000000000000000000)                                              │
	│st3            0        (raw 0x00000000000000000000)                                              │
	│st4            0        (raw 0x00000000000000000000)                                              │
	│st5            0        (raw 0x00000000000000000000)                                              │
	│st6            0        (raw 0x00000000000000000000)                                              │
	└──────────────────────────────────────────────────────────────────────────────────────────────────┘
	   │16              fun1();                                                                        │
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 12552 In: main                                               Line: 24   PC: 0x40052b
	Temporary breakpoint 1 at 0x40052b: file a.c, line 24.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:24
	(gdb) tui reg float

“`tui reg system`”命令顯示系統暫存器：  

	┌──Register group: system──────────────────────────────────────────────────────────────────────────┐
	│orig_rax       0xffffffffffffffff       -1                                                        │
	│                                                                                                  │
	│                                                                                                  │
	│                                                                                                  │
	│                                                                                                  │
	│                                                                                                  │
	│                                                                                                  │
	└──────────────────────────────────────────────────────────────────────────────────────────────────┘
	   │16              fun1();                                                                        │
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 12552 In: main                                               Line: 24   PC: 0x40052b
	
	Temporary breakpoint 1, main () at a.c:24
	(gdb) tui reg system
	(gdb)
想切換回顯示通用暫存器內容，可以使用“`tui reg general`”命令：  

	┌──Register group: general─────────────────────────────────────────────────────────────────────────┐
	│rax            0x34e4590f60     227169341280     rbx            0x0      0                        │
	│rcx            0x0      0                        rdx            0x7fffffffe4b8   140737488348344  │
	│rsi            0x7fffffffe4a8   140737488348328  rdi            0x1      1                        │
	│rbp            0x7fffffffe3c0   0x7fffffffe3c0   rsp            0x7fffffffe3c0   0x7fffffffe3c0   │
	│r8             0x34e458f300     227169334016     r9             0x34e3a0e9f0     227157273072     │
	│r10            0x7fffffffe210   140737488347664  r11            0x34e421ec20     227165727776     │
	│r12            0x4003e0 4195296                  r13            0x7fffffffe4a0   140737488348320  │
	└──────────────────────────────────────────────────────────────────────────────────────────────────┘
	   │16              fun1();                                                                        │
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 12552 In: main                                               Line: 24   PC: 0x40052b
	(gdb) tui reg general
	(gdb)
  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/TUI-Commands.html).

---

### 調整視窗大小

## 例子
	#include <stdio.h>
	
	void fun1(void)
	{
	        int i = 0;
	
	        i++;
	        i = i * 2;
	        printf("%d\n", i);
	}
	
	void fun2(void)
	{
	        int j = 0;
	
	        fun1();
	        j++;
	        j = j * 2;
	        printf("%d\n", j);
	}
	
	int main(void)
	{
	        fun2();
	        return 0;
	}


## 技巧
使用gdb圖形化除錯介面時，可以使用“`winheight  <win_name> [+ | -]count`”命令調整視窗大小（`winheight`縮寫為`win`。`win_name`可以是`src`、`cmd`、`asm`和`regs`）。以除錯上面程式為例，這是原始的`src`視窗大小：  

	   ┌──a.c──────────────────────────────────────────────────────────────────────────────────────────┐
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21      int main(void)                                                                        22
	   │23      {                                                                                      │
	   │24              fun2();                                                                        │
	B+>│25                                                                                             │
	   │                return 0;                                                                      │
	   │26      }                                                                                      │
	   │27                                                                                            32
	   │                                                                                               │
	   │                                                                                               │
	   │                                                                                               │
	   │                                                                                               │
	   │                                                                                               │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 9667 In: main                                                Line: 24   PC: 0x40052b
	Usage: winheight <win_name> [+ | -] <#lines>
	(gdb) start
	Temporary breakpoint 1 at 0x40052b: file a.c, line 24.
	Starting program: /home/nan/a
	
	Temporary breakpoint 1, main () at a.c:24

執行“`winheight src -5`”命令後：

	   ┌──a.c──────────────────────────────────────────────────────────────────────────────────────────┐
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	  >│24              fun2();                                                                        │
	   │25              return 0;                                                                      │
	   │26      }                                                                                      │
	   │27                                                                                             │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 9667 In: main                                               Line: 24   PC: 0x40052b
	Usage: winheight <win_name> [+ | -] <#lines>
	(gdb)
可以看到視窗變小了。  
接著執行“`winheight src +5`”命令：  

	   ┌──a.c──────────────────────────────────────────────────────────────────────────────────────────┐
	   │17              j++;                                                                           │
	   │18              j = j * 2;                                                                     │
	   │19              printf("%d\n", j);                                                             │
	   │20      }                                                                                      │
	   │21                                                                                             │
	   │22      int main(void)                                                                         │
	   │23      {                                                                                      │
	  >│24              fun2();                                                                        │
	   │25              return 0;                                                                      │
	   │26      }                                                                                      │
	   │27                                                                                             │
	   │28                                                                                             │
	   │29                                                                                             │
	   │30                                                                                             │
	   │31                                                                                             │
	   │32                                                                                             │
	   └───────────────────────────────────────────────────────────────────────────────────────────────┘
	native process 9667 In: main                                               Line: 24   PC: 0x40052b
	Usage: winheight <win_name> [+ | -] <#lines>
	(gdb)
可以看到視窗恢復了原樣。  
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/TUI-Commands.html).

---

## 其它

### 命令列選項的格式

## 技巧

gdb的幫助資訊和線上文件對於長選項的形式使用了不同的風格。你可能有點迷惑，gdb的長選項究竟應該是“-”，還是“--”？

是的，這兩種方式都可以。例如：

	$ gdb -help
	$ gdb --help

	$ gdb -args ./a.out a b c
	$ gdb --args ./a.out a b c

好吧，使用短的。

---

### 支援預處理器宏資訊

## 例子

	#include <stdio.h>
	
	#define NAME "Joe"
	
	int main()
	{
	  printf ("Hello %s\n", NAME);
	  return 0;
	}

## 技巧

使用`gcc -g`編譯生成的程式，是不包含預處理器宏資訊的：

	(gdb) p NAME
	No symbol "NAME" in current context.

如果想在gdb中檢視宏資訊，可以使用`gcc -g3`進行編譯：

	(gdb) p NAME
	$1 = "Joe"

關於預處理器宏的命令，參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Macros.html#Macros)

---

### 保留未使用的型別

## 例子

	#include <stdio.h>
	
	union Type {
	  int a;
	  int *b;
	};
	
	int main()
	{
	  printf("sizeof(union Type) is %lu\n", sizeof(union Type));
	  return 0;
	}

## 技巧

使用`gcc -g`編譯生成的程式，是不包含union Type的符號資訊：

	(gdb) p sizeof(union Type)
	No union type named Type.

如果想讓gcc保留這些沒有被使用的型別資訊（猜測應該是sizeof在編譯時即被替換成常數，所以gcc認為union Type是未使用的型別），則可以使用`gcc -g -fno-eliminate-unused-debug-types`進行編譯：

	(gdb) p sizeof(union Type)
	$1 = 8

參見[gcc手冊](https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html#Debugging-Options)

---

### 使用命令的縮寫形式

## 技巧

在gdb中，你不用必須輸入完整的命令，只需命令的（前）幾個字母即可。規則是，只要這個縮寫不會和其它命令有歧義（注，是否有歧義，這個規則從文件上看不出，看起來需要檢視gdb的原始碼，或者在實際使用中進行總結）。也可以使用tab鍵進行命令補全。

其中許多常用命令只使用第一個字母就可以，比如：

	b -> break
	c -> continue
	d -> delete
	f -> frame
	i -> info
	j -> jump
	l -> list
	n -> next
	p -> print
	r -> run
	s -> step
	u -> until

也有使用兩個或幾個字母的，比如：  

	aw -> awatch
	bt -> backtrace
	dir -> directory
	disas -> disassemble
	fin -> finish
	ig -> ignore
	ni -> nexti
	rw -> rwatch
	si -> stepi
	tb -> tbreak
	wa -> watch
	win -> winheight
	
另外，如果直接按回車鍵，會重複執行上一次的命令。

---

### 在gdb中執行shell命令和make

## 技巧

你可以不離開gdb，直接執行shell命令，比如：

	(gdb) shell ls

或

	(gdb) !ls

這裡，"!"和命令之間不需要有空格（即，有也成）。

特別是當你在構建環境(build目錄)下除錯程式的時候，可以直接執行make：

	(gdb) make CFLAGS="-g -O0"

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Shell-Commands.html#Shell-Commands)

---

### 在gdb中執行cd和pwd命令

## 技巧

是的，gdb確實支援這兩個命令，雖然我沒有想到它們有什麼特別的用處。

也許，當你啟動gdb之後，發現需要切換工作目錄，但又不想退出gdb的時候：

	(gdb) pwd
	Working directory /home/xmj.
	(gdb) cd tmp
	Working directory /home/xmj/tmp.

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Working-Directory.html#Working-Directory)

---

### 設定命令提示符

## 例子

	$ gdb -q `which gdb`
	Reading symbols from /home/xmj/install/binutils-gdb-git/bin/gdb...done.
	(gdb) r -q
	Starting program: /home/xmj/install/binutils-gdb-git/bin/gdb -q
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
	(gdb)

## 技巧

當你用gdb來除錯gdb的時候，透過設定命令提示符，可以幫助你區分這兩個gdb：

	$ gdb -q `which gdb`
	Reading symbols from /home/xmj/install/binutils-gdb-git/bin/gdb...done.
	(gdb) set prompt (main gdb) 
	(main gdb) r -q
	Starting program: /home/xmj/install/binutils-gdb-git/bin/gdb -q
	[Thread debugging using libthread_db enabled]
	Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
	(gdb) 

注意，這裡`set prompt (main gdb) `結尾處是有一個空格的。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Prompt.html#Prompt)

---

### 設定被除錯程式的引數

## 技巧

可以在gdb啟動時，透過選項指定被除錯程式的引數，例如：

	$ gdb -args ./a.out a b c

也可以在gdb中，透過命令來設定，例如：

	(gdb) set args a b c
	(gdb) show args
	Argument list to give program being debugged when it is started is "a b c".

也可以在執進程式時，直接指定：

	(gdb) r a b
	Starting program: /home/xmj/tmp/a.out a b
	(gdb) show args
	Argument list to give program being debugged when it is started is "a b".
	(gdb) r
	Starting program: /home/xmj/tmp/a.out a b 

可以看出，引數已經被儲存了，下次執行時直接執行`run`命令，即可。

有意的是，如果我接下來，想讓引數為空，該怎麼辦？是的，直接：

	(gdb) set args

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Arguments.html#Arguments)

---

### 設定被除錯程式的環境變數

## 例子

	(gdb) u 309
	Warning: couldn't activate thread debugging using libthread_db: Cannot find new threads: generic error
	Warning: couldn't activate thread debugging using libthread_db: Cannot find new threads: generic error
	warning: Unable to find libthread_db matching inferior's thread library, thread debugging will not be available.

## 技巧

在gdb中，可以透過命令`set env varname=value`來設定被除錯程式的環境變數。對於上面的例子，網上可以搜到一些解決方法，其中一種方法就是設定LD_PRELOAD環境變數：

	set env LD_PRELOAD=/lib/x86_64-linux-gnu/libpthread.so.0

注意，這個實際路徑在不同的機器環境下可能不一樣。把這個命令加到~/.gdbinit檔案中，就可以了。

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Environment.html#Environment)

---

### 得到命令的幫助資訊

## 技巧

使用`help`命令可以得到gdb的命令幫助資訊：  

（1）`help`命令不加任何引數會得到命令的分類：

	(gdb) help
	List of classes of commands:
	
	aliases -- Aliases of other commands
	breakpoints -- Making program stop at certain points
	data -- Examining data
	files -- Specifying and examining files
	internals -- Maintenance commands
	obscure -- Obscure features
	running -- Running the program
	stack -- Examining the stack
	status -- Status inquiries
	support -- Support facilities
	tracepoints -- Tracing of program execution without stopping the program
	user-defined -- User-defined commands
	
	Type "help" followed by a class name for a list of commands in that class.
	Type "help all" for the list of all commands.
	Type "help" followed by command name for full documentation.
	Type "apropos word" to search for commands related to "word".
	Command name abbreviations are allowed if unambiguous.
（2）當輸入`help class`命令時，可以得到這個類別下所有命令的列表和命令功能：  

	(gdb) help data
	Examining data.
	
	List of commands:
	
	append -- Append target code/data to a local file
	append binary -- Append target code/data to a raw binary file
	append binary memory -- Append contents of memory to a raw binary file
	append binary value -- Append the value of an expression to a raw binary file
	append memory -- Append contents of memory to a raw binary file
	append value -- Append the value of an expression to a raw binary file
	call -- Call a function in the program
	disassemble -- Disassemble a specified section of memory
	display -- Print value of expression EXP each time the program stops
	dump -- Dump target code/data to a local file
	dump binary -- Write target code/data to a raw binary file
	dump binary memory -- Write contents of memory to a raw binary file
	dump binary value -- Write the value of an expression to a raw binary file
	......
（3）也可以用`help command`命令得到某一個具體命令的用法：  

	(gdb) help mem
	Define attributes for memory region or reset memory region handling totarget-based.
	Usage: mem auto
       mem <lo addr> <hi addr> [<mode> <width> <cache>],
	where <mode>  may be rw (read/write), ro (read-only) or wo (write-only),
      <width> may be 8, 16, 32, or 64, and
      <cache> may be cache or nocache

（4）用`apropos regexp`命令查詢所有符合`regexp`正則表示式的命令資訊：  

	(gdb) apropos set
	awatch -- Set a watchpoint for an expression
	b -- Set breakpoint at specified line or function
	br -- Set breakpoint at specified line or function
	bre -- Set breakpoint at specified line or function
	brea -- Set breakpoint at specified line or function
	......

詳情參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Help.html)

---

### 記錄執行gdb的過程

## 例子
	#include <stdio.h>
	#include <wchar.h>
	
	int main(void)
	{
	        char str1[] = "abcd";
	        wchar_t str2[] = L"abcd";
	        
	        return 0;
	}

## 技巧
用gdb除錯程式時，可以使用“`set logging on`”命令把執行gdb的過程記錄下來，方便以後自己參考或是別人幫忙分析。預設的日誌檔案是“`gdb.txt`”，也可以用“`set logging file file`”改成別的名字。以上面程式為例：  

    (gdb) set logging file log.txt
	(gdb) set logging on
	Copying output to log.txt.
	(gdb) start
	Temporary breakpoint 1 at 0x8050abe: file a.c, line 6.
	Starting program: /data1/nan/a 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Temporary breakpoint 1, main () at a.c:6
	6               char str1[] = "abcd";
	(gdb) n
	7               wchar_t str2[] = L"abcd";
	(gdb) x/s str1
	0x804779f:      "abcd"
	(gdb) n       
	9               return 0;
	(gdb) x/ws str2
	0x8047788:      U"abcd"
	(gdb) q
	A debugging session is active.
	
	        Inferior 1 [process 9931    ] will be killed.
	
	Quit anyway? (y or n) y

執行完後，檢視log.txt檔案：

	bash-3.2# cat log.txt 
	Temporary breakpoint 1 at 0x8050abe: file a.c, line 6.
	Starting program: /data1/nan/a 
	[Thread debugging using libthread_db enabled]
	[New Thread 1 (LWP 1)]
	[Switching to Thread 1 (LWP 1)]
	
	Temporary breakpoint 1, main () at a.c:6
	6               char str1[] = "abcd";
	7               wchar_t str2[] = L"abcd";
	0x804779f:      "abcd"
	9               return 0;
	0x8047788:      U"abcd"
	A debugging session is active.
	
	        Inferior 1 [process 9931    ] will be killed.
	
	Quit anyway? (y or n)
可以看到log.txt詳細地記錄了gdb的執行過程。

此外“`set logging overwrite on`”命令可以讓輸出覆蓋之前的日誌檔案；而 “`set logging redirect on`”命令會讓gdb的日誌不會列印在終端。    
參見[gdb手冊](https://sourceware.org/gdb/onlinedocs/gdb/Logging-Output.html).

---

### 列印C++虛表及其內容

## 例子
	#include <iostream>
 
        struct Base {
          virtual void f(){
            std::cout << "base\n";
          }
        };
 
        struct Derived : Base {
          void f() override // 'override' is optional
          {
            std::cout << "derived\n";
          }
        };
 
        int main() {
          Base b;
          Derived d;
 
          // virtual function call through reference
          Base& br = b; // the type of br is Base&
          Base& dr = d; // the type of dr is Base& as well
        }

## 技巧
  為了觀察一個物件的虛表和相應虛表的內容，可以在啟動gdb後設置如下命令
  `set print asm-demangle on`
  `set print demangle on`
  已下面程式為例子
    
     (gdb) l
	    int main() {
	    Base b;
	    Derived d;

	    // virtual function call through reference
	    Base& br = b; // the type of br is Base&
	    Base& dr = d; // the type of dr is Base& as well
    (gdb) n
    	The program is not being run.
    (gdb) r
    	Starting program: /home/qinliansong/pblearn/main
    	[Thread debugging using libthread_db enabled]
    	Using host libthread_db library "/lib64/libthread_db.so.1".

	Breakpoint 1, main () at main.cc:21
	    Base b;
	Missing separate debuginfos, use: debuginfo-install libgcc-4.8.5-39.el7.x86_64 libstdc++-4.8.5-39.el7.x86_64
    (gdb) n
	    Derived d;
    (gdb) n
	    Base& br = b; // the type of br is Base&
  
  此時設定如下兩個命令，幾個命令，更友好的觀察vtbl
  
  `set print vtbl on`
  `set print object on`
  `set print pretty on`
  
    (gdb) set print vtbl on
    (gdb) p d
	$1 = {<Base> = {_vptr.Base = 0x4009c0 <vtable for Derived+16>}, <No data fields>}
    (gdb) set print object on
    (gdb) set print pretty on
    (gdb) p d
	$2 = (Derived) {
  		<Base> = {
   		 _vptr.Base = 0x4009c0 <vtable for Derived+16>
  	}, <No data fields>}

  透過`info vtbl [expr]`觀察物件的虛擬函式
   
    (gdb) info vtbl d
    	vtable for 'Derived' @ 0x4009c0 (subobject @ 0x7fffffffde00):
	    [0]: 0x4008f2 <Derived::f()>

    (gdb) set print demangle on
    (gdb) set print asm-demangle on
    (gdb) x/28x 0x4009c0
    	0x4009c0 <vtable for Derived+16>:	0x004008f2	0x00000000	0x00000000	0x00000000
	    0x4009d0 <vtable for Base+8>:	0x00400a08	0x00000000	0x004008d4	0x00000000
    	0x4009e0 <typeinfo for Derived>:	0x00600d90	0x00000000	0x004009f8	0x00000000
    	0x4009f0 <typeinfo for Derived+16>:	0x00400a08	0x00000000	0x72654437	0x64657669
    	0x400a00 <typeinfo name for Derived+8>:	0x00000000	0x00000000	0x00600d30	0x00000000
	    0x400a10 <typeinfo for Base+8>:	0x00400a18	0x00000000	0x73614234	0x00000065
	    0x400a20:	0x3b031b01	0x00000054	0x00000009	0xfffffc80


    (gdb) info variables vtable for Derived
	    All variables matching regular expression "vtable for Derived":

	    Non-debugging symbols:
    	0x00000000004009b0  vtable for Derived
    (gdb) x /4a 0x00000000004009b0
	    0x4009b0 <vtable for Derived>:	0x0	0x4009e0 <typeinfo for Derived>
	    0x4009c0 <vtable for Derived+16>:	0x4008f2 <Derived::f()>	0x0
    (gdb) x /10a 0x4009c0
    	0x4009c0 <vtable for Derived+16>:	0x4008f2 <Derived::f()>	0x0
	    0x4009d0 <vtable for Base+8>:	0x400a08 <typeinfo for Base>	0x4008d4 <Base::f()>
	    0x4009e0 <typeinfo for Derived>:	0x600d90 <vtable for __cxxabiv1::__si_class_type_info@@CXXABI_1.3+16>	0x4009f8 <typeinfo name for Derived>
	    0x4009f0 <typeinfo for Derived+16>:	0x400a08 <typeinfo for Base>	0x6465766972654437
	    0x400a00 <typeinfo name for Derived+8>:	0x0	0x600d30 <vtable for __cxxabiv1::__class_type_info@@CXXABI_1.3+16>

## 參考
  [gdb手冊](https://docs.adacore.com/live/wave/gdb-10/html/gdb/gdb.html)
  [vtable-part1](https://shaharmike.com/cpp/vtable-part1/)

---

## 其他資源

- [GDB 線上手冊](https://sourceware.org/gdb/onlinedocs/gdb)
- [GDB 命令卡片](https://github.com/hellogcc/100-gdb-tips/blob/master/refcard.pdf)
- [GDB Dashboard](https://github.com/cyrus-and/gdb-dashboard)
- [Gdbinit for OS X, iOS and others](https://github.com/gdbinit/Gdbinit)
- [dotgdb：關於底層除錯和反向工程的 GDB 腳本集](https://github.com/dholm/dotgdb)

## 授權

本文件使用 [GNU Free Documentation License](http://www.gnu.org/licenses/fdl.html) 授權。

## 致謝

感謝所有 100-gdb-tips 專案的貢獻者。

---

*本文件由腳本自動生成，共整合 105 個 GDB 技巧。*
