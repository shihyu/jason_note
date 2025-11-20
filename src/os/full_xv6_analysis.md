# 讀書心得 : 操作系統原型 - xv6 分析與實踐 羅秋明 著 - HackMD

###### [](#tags-202211-unixv6-xv6 "tags-202211-unixv6-xv6")tags: 
```
2022/11
```
 
```
unixv6
```
 
```
xv6
```

(2022/11/20) 發現這本難得的好書, 對 Unix/Linux kernel 的實作了解大有幫助. 該作者目前已經發行四本(實體)書, 分別是

1.  "Linux GNU C 程序(程式)觀察" : C 語言程式設計, 數據結構
2.  "操作系統之編程觀察" : 操作系統原理, /proc 儀錶板, 將操作系統從黑盒變白盒
3.  "操作系統原型 - xv6 分析與實踐" : 在裸硬件上, 設計與實現操作系統核心機制的能力
4.  "Linux 技術內幕" : 鑽研真實操作系統代碼(程式碼)

For English documentation related to 
```
xv6
```
, I found two articles valueable, they are official [xv6 book (pdf) - xv6 a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf), and [Lions' Commentary on UNIX' 6th Edition, John Lions (pdf version)](http://www.lemis.com/grog/Documentation/Lions/book.pdf)

latest update on 2023/02/27

---

**Table of Contents**

-   [讀書心得 : 操作系統原型 - xv6 分析與實踐 羅秋明 著](#讀書心得--操作系統原型---xv6-分析與實踐-羅秋明-著 "讀書心得 : 操作系統原型 - xv6 分析與實踐 羅秋明 著")  -   [Chapter 0 How to read this article / 建議閱讀順序](#Chapter-0-How-to-read-this-article--建議閱讀順序 "Chapter 0 How to read this article / 建議閱讀順序")
      -   [Chapter 1 xv6 installation](#Chapter-1-xv6-installation "Chapter 1 xv6 installation")    -   [What is xv6](#What-is-xv6 "What is xv6")
              -   [Install xv6 and run xv6 on QEMU / gdb](#Install-xv6-and-run-xv6-on-QEMU--gdb "Install xv6 and run xv6 on QEMU / gdb")
              -   [xv6 shell command introduction](#xv6-shell-command-introduction "xv6 shell command introduction")
          
      -   [Chapter 2 - xv6 Experiements, Level One](#Chapter-2---xv6-Experiements-Level-One "Chapter 2 - xv6 Experiements, Level One")    -   [How xv6 Makefile generates the disk image](#How-xv6-Makefile-generates-the-disk-image "How xv6 Makefile generates the disk image")
              -   [Experiment 1-0 : Modify xv6 greetings](#Experiment-1-0--Modify-xv6-greetings "Experiment 1-0 : Modify xv6 greetings")
              -   [Experiment 1-1 : Adding one user application (new shell command) on xv6](#Experiment-1-1--Adding-one-user-application-new-shell-command-on-xv6 "Experiment 1-1 : Adding one user application (new shell command) on xv6")
              -   [Experiment 1-2 : Adding one kernel System Call in xv6](#Experiment-1-2--Adding-one-kernel-System-Call-in-xv6 "Experiment 1-2 : Adding one kernel System Call in xv6")
              -   [Deep dive into how the System Call example works - 1 : more descriptions](#Deep-dive-into-how-the-System-Call-example-works---1--more-descriptions "Deep dive into how the System Call example works - 1 : more descriptions")
              -   [Deep dive into how the System Call example works - 2 : trace by gdb](#Deep-dive-into-how-the-System-Call-example-works---2--trace-by-gdb "Deep dive into how the System Call example works - 2 : trace by gdb")
              -   [Deep dive into how the System Call example works - 3 : another example getpid](#Deep-dive-into-how-the-System-Call-example-works---3--another-example-getpid "Deep dive into how the System Call example works - 3 : another example getpid")
              -   [xv6 binary and image](#xv6-binary-and-image "xv6 binary and image")
              -   [File Descriptors](#File-Descriptors "File Descriptors")
              -   [Testing multiple cores and fork](#Testing-multiple-cores-and-fork "Testing multiple cores and fork")
    
-   [讀書心得 - xv6 a simple, Unix-like teaching operating system](#讀書心得---xv6-a-simple-Unix-like-teaching-operating-system "讀書心得 - xv6 a simple, Unix-like teaching operating system")  -   [Appendix A - Source code in boot sequence](#Appendix-A---Source-code-in-boot-sequence "Appendix A - Source code in boot sequence")
      -   [Appendix B - xv6 Bootstrap](#Appendix-B---xv6-Bootstrap "Appendix B - xv6 Bootstrap")
      -   [References](#References "References")
---

## [](#Chapter-0-How-to-read-this-article--建議閱讀順序 "Chapter-0-How-to-read-this-article--建議閱讀順序")Chapter 0 How to read this article / 建議閱讀順序

本文主要參考 2 本書的心得 "操作系統原型 - xv6 分析與實踐 羅秋明 著" 跟 "xv6 a simple, Unix-like teaching operating system".

喜歡實作的人, 可以從 ["Chapter 1 xv6 installation"](#Chapter-1-xv6-installation) 開始操作, 下載 xv6 原始碼, 進行編譯及修改, 再進入 xv6 的原理, 介紹 bootstrap 到 kernel 的實踐.

如果是喜歡先理解原理的人, 可以先從 [xv6 a simple Unix like teaching operating system](#%E8%AE%80%E6%9B%B8%E5%BF%83%E5%BE%97---xv6-a-simple-Unix-like-teaching-operating-system) 的 Appendix A & B 開始讀起.

---

## [](#Chapter-1-xv6-installation "Chapter-1-xv6-installation")Chapter 1 xv6 installation

### [](#What-is-xv6 "What-is-xv6")What is xv6

A : xv6 是個教學用的操作系統, 是 Unix Version 6 (v6) 的簡單實現, 但是並不嚴格遵守 v6 的結構與風格. 2020/8/11 後已不再維護, 而轉向 RISC-V 版本.

xv6 is a re-implementation of Dennis Ritchie's and Ken Thompson's Unix Version 6 (v6). xv6 loosely follows the structure and style of v6,  
but is implemented for a modern x86-based multiprocessor using ANSI C.

xv6 is inspired by John Lions's Commentary on UNIX 6th Edition (Peer  
to Peer Communications; ISBN: 1-57398-013-7; 1st edition (June 14,  
2000)). See also [https://pdos.csail.mit.edu/6.828/](https://pdos.csail.mit.edu/6.828/), which  
provides pointers to on-line resources for v6.

xv6 borrows code from the following sources:

-   JOS (asm.h, elf.h, mmu.h, bootasm.S, ide.c, console.c, and others)
-   Plan 9 (entryother.S, mp.h, mp.c, lapic.c)
-   FreeBSD (ioapic.c)
-   NetBSD (console.c)
---

### [](#Install-xv6-and-run-xv6-on-QEMU--gdb "Install-xv6-and-run-xv6-on-QEMU--gdb")Install xv6 and run xv6 on QEMU / gdb

從 [https://github.com/mit-pdos/xv6-public/tags](https://github.com/mit-pdos/xv6-public/tags) 下載 rev9 版本 [xv6-rev9.tar.gz](https://github.com/mit-pdos/xv6-public/archive/refs/tags/xv6-rev9.tar.gz) 後就可以在 QEMU 上執行, 或在 QEMU / gdb 執行.

```


# Download and make
wget https://github.com/mit-pdos/xv6-public/archive/refs/tags/xv6-rev9.tar.gz
tar -xvf xv6-rev9.tar.gz
cd xv6-public-xv6-rev9
make
# Different ways of execution
# 1.1 Running xv6 on QEMU in a separate screen
make qemu
# 1.2 Running xv6 on QEMU from the same terminal screen
make qemu-nox
# 2. Running xv6 on QEMU with four (4) CPU cores
CPUS=4 make qemu-nox
# 3.1 Running xv6 on QEMU+gdb
#    It is required to open another terminal to run gdb. See 3.2-x
make qemu-gdb
# 3.2-1 open another terminal screen and run gdb 
gdb -q kernel
(gdb) target remote localhost:26000
(gdb) continue
# or 3.2-2 use .gdbinit under the current working directory
#    /home/kernel-dev/myworks/xv6-public
gdb -q kernel -iex "set auto-load safe-path /home/kernel-dev/myworks/xv6-public"
(gdb) continue
# or 3.2-3 set up ~/.gdbinit with current working directory
#    then launch gdb
echo "set auto-load safe-path /home/kernel-dev/myworks/xv6-public" > ~/.gdbinit
gdb -q kernel
(gdb) continue





```

#### [](#A-note-about-xv6-gdb-environment "A-note-about-xv6-gdb-environment")**A note about xv6 gdb environment**

In above 3.2-1 example, we will find below message after launching 
```
gdb
```
, and learn that there is a 
```
.gdbinit
```
 file in xv6 directory which set up the environment for 
```
gdb
```
 client. However, 
```
gdb
```
 does not execute that 
```
.gdinit
```
 for security concern. We need to enable it manually. In 3.2-2, we specify the working directory of xv6 and 
```
.gdbinit
```
 in command line option 
```
gdb -iex
```
. Or in 3.2-3, we create a file 
```
.gdbinit
```
 under 
```
~/
```
 directory with the content of 
```
"set auto-load safe-path /home/kernel-dev/myworks/xv6-public"
```
 so 
```
gdb
```
 will execute xv6 
```
.gdbinit
```
 to set up environments. Either way can work.

```


Reading symbols from kernel...done.
warning: File "/home/kernel-dev/myworks/xv6-public/.gdbinit" auto-loading has been declined by your `auto-load safe-path' set to "$debugdir:$datadir/auto-load".
To enable execution of this file add
	add-auto-load-safe-path /home/kernel-dev/myworks/xv6-public/.gdbinit
line to your configuration file "/home/kernel-dev/.gdbinit".
To completely disable this security protection add
	set auto-load safe-path /
line to your configuration file "/home/kernel-dev/.gdbinit".
For more information about this security protection see the
"Auto-loading safe path" section in the GDB manual.  E.g., run from the shell:
	info "(gdb)Auto-loading safe path"





```

#### [](#Notes-about-QEMU-and-gdb-commands-to-exit "Notes-about-QEMU-and-gdb-commands-to-exit")**Notes about QEMU and gdb commands to exit**

For those who are not familiar with QEMU and gdb, you might need to know the commands how to exit. Without knowing those commands, you will be annoyed by how to exit QEMU and gdb.

-   CTRL+a then x (not CTRL-x) : Exit from QEMU (if using 
    ```
    qemu-nox
    ```
     command)
-   CTRL+ALT or CTRL+ALT+g : Escape mouse and keyboard from QEMU screen, back to host (if using 
    ```
    qemu
    ```
     command)
-   CTRL+d : Exit from gdb

Please look for more QEMU and gdb commands in respective manuals.

---

### [](#xv6-shell-command-introduction "xv6-shell-command-introduction")xv6 shell command introduction

After launching xv6 
```
CPUS=4 make qemu-nox
```
, it shows shell command prompt 
```
$
```
. (One strange thing is, xv6 system becomes very slow when I set CPUS to 8 or 16. Could be an interesting topic to dive into details)

```
SeaBIOS (version rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org)


iPXE (http://ipxe.org) 00:03.0 CA00 PCI2.10 PnP PMM+1FF908D0+1FEF08D0 CA00
                                                                               


Booting from Hard Disk..xv6...
cpu1: starting xv6 on cpu1
cpu2: starting xv6 on cpu2
cpu3: starting xv6 on cpu3
cpu0: starting xv6 on cpu0
sb: size 1000 nblocks 941 ninodes 200 nlog 30 logstart 2 inodestart 32 bmap sta8
init: starting sh
$ 

```

After entering xv6 system, we can issue 
```
ls
```
 command to check what else commands available, as in left column of below table. Also list the files in xv6 source code with 
```
*.c
```
 as reference. There are quite some differences beween both, as the 
```
xv6
```
 column shows the commands in user space, and 
```
host Linux
```
 shows commands/API's for both user and kernel space.

<table><tbody><tr><td>host Linux</td><td>qemu - xv6</td></tr><tr><td><div data-position="6358" data-infoprefix-length="6" data-endline="203" data-startline="155" class="part code-block-wrapper code-block-toolbar-handled"><pre class="click-event-handled"><code class="shell hljs"><div class="wrapper"><p><span class="hljs-meta">$ </span><span class="language-bash"><span class="hljs-built_in">ls</span> *.c</span>                       
bio.c
bootmain.c
cat.c
console.c
echo.c
exec.c
file.c
forktest.c
fs.c
grep.c
ide.c
init.c
ioapic.c
kalloc.c
kbd.c
kill.c
lapic.c
ln.c
log.c
ls.c
main.c
memide.c
mkdir.c
mkfs.c
mp.c
picirq.c
pipe.c
printf.c
proc.c
rm.c
sh.c
sleeplock.c
spinlock.c
stressfs.c
string.c
syscall.c
sysfile.c
sysproc.c
trap.c
uart.c
ulib.c
umalloc.c
usertests.c
vm.c
wc.c
zombie.c
</p></div></code></pre></div></td><td><div data-position="6775" data-infoprefix-length="6" data-endline="229" data-startline="208" class="part code-block-wrapper code-block-toolbar-handled"><pre class="click-event-handled"><code class="shell hljs"><div class="wrapper"><p><span class="hljs-meta">$ </span><span class="language-bash"><span class="hljs-built_in">ls</span></span>
.              1 1 512
..             1 1 512
README         2 2 2286
cat            2 3 13412
echo           2 4 12488
forktest       2 5 8204
grep           2 6 15240
init           2 7 13080
kill           2 8 12528
ln             2 9 12436
ls             2 10 14652
mkdir          2 11 12552
rm             2 12 12528
sh             2 13 23168
stressfs       2 14 13208
usertests      2 15 56088
wc             2 16 14064
zombie         2 17 12260
console        3 22 0
</p></div></code></pre></div></td></tr></tbody></table>

#### [](#xv6-special-command-CTRLp "xv6-special-command-CTRLp")**xv6 special command CTRL+p**

People familiar with Linux know the command 
```
ps
```
 to list the active processes running (in foreground and background). In xv6, there is a special command, or should be called key strokes, of CTRL+p, to print out the active processes. Below is the example when CTRL+p were pressed at vx6 prompt.

```


$ 1 sleep  init 80103db7 80103e59 80104857 801058e9 8010564e
2 sleep  sh 80103d7c 801002c2 80100f8c 80104b52 80104857 801058e9 8010564e





```

#### [](#Check-xv6-source-code-of-the-active-processes-on-host-Linux "Check-xv6-source-code-of-the-active-processes-on-host-Linux")**Check xv6 source code of the active processes on host Linux**

Then we switch back to the host Linux environment, to check what those numbers mean in xv6 source code.

```


# now we switch back to host Linux environment
cd xv6-public
# print out the source code of running process `init`
addr2line -e kernel 80103db7 80103e59 80104857 801058e9 8010564e
# /home/kernel-dev/myworks/xv6-public/proc.c:445
# /home/kernel-dev/myworks/xv6-public/proc.c:311
# /home/kernel-dev/myworks/xv6-public/syscall.c:141
# /home/kernel-dev/myworks/xv6-public/trap.c:44
# /home/kernel-dev/myworks/xv6-public/trapasm.S:21
# print out the source code of running process `sh`
addr2line -e kernel 80103d7c 801002c2 80100f8c 80104b52 80104857 801058e9 8010564e
# /home/kernel-dev/myworks/xv6-public/proc.c:445
# /home/kernel-dev/myworks/xv6-public/console.c:245
# /home/kernel-dev/myworks/xv6-public/file.c:107
# /home/kernel-dev/myworks/xv6-public/sysfile.c:78
# /home/kernel-dev/myworks/xv6-public/syscall.c:141
# /home/kernel-dev/myworks/xv6-public/trap.c:44
# /home/kernel-dev/myworks/xv6-public/trapasm.S:21





```

---

## [](#Chapter-2---xv6-Experiements-Level-One "Chapter-2---xv6-Experiements-Level-One")Chapter 2 - xv6 Experiements, Level One

### [](#How-xv6-Makefile-generates-the-disk-image "How-xv6-Makefile-generates-the-disk-image")How xv6 Makefile generates the disk image

This section can be skipped if you are not (yet) intestered in using 
```
Makefile
```
 to build xv6 (or other Linux) image. There are 2 steps to generate the xv6 disk file system.

-   Generate all applications
-   Generate File System image from those applications.
1.  Generate all applications : Below is the 
    ```
    Makefile
    ```
     snippet to build all applicaions.

Each 
```
%.o
```
 file will link 
```
$(LD)
```
 with 
```
$(ULIB)
```
 to produce its executable file named 
```
_%
```
. (
```
%
```
 will be replaced by 
```
cat
```
, 
```
echo
```
, or other user applications)

```
-Ttext 0
```
 to assign the code to start from address 
```
0
```
.

```
-e main
```
 indicates to use 
```
main
```
 function as the first instruction.

```
-N
```
 is to specify the 
```
data
```
 and 
```
text
```
 sections allows 
```
read
```
 and 
```
write
```
, and no need to align with page boundary.

```


ULIB = ulib.o usys.o printf.o umalloc.o

_%: %.o $(ULIB)
        $(LD) $(LDFLAGS) -N -e main -Ttext 0 -o $@ $^
        $(OBJDUMP) -S $@ > $*.asm
        $(OBJDUMP) -t $@ | sed '1,/SYMBOL TABLE/d; s/ .* / /; /^$$/d' > $*.sym






```

2.  Generate File System image from those applications : 
    ```
    UPROGS
    ```
     parameter includes all the related executable file names. Then generate 
    ```
    fs.img
    ```
     by 
    ```
    mkfs
    ```
     with README and 
    ```
    UPROGS
    ```
     files.

```


UPROGS=\
        _cat\
        _echo\
        _forktest\
        _grep\
        _init\
        _kill\
        _ln\
        _ls\
        _mkdir\
        _rm\
        _sh\
        _stressfs\
        _usertests\
        _wc\
        _zombie\
        _my-app-1\
        _my-app-print-pid\
        _my-app-pcpuid\
        _my-app-fork\

fs.img: mkfs README $(UPROGS)
        ./mkfs fs.img README $(UPROGS)





```

---

### [](#Experiment-1-0--Modify-xv6-greetings "Experiment-1-0--Modify-xv6-greetings")Experiment 1-0 : Modify xv6 greetings

Find the file 
```
main.c
```
 under 
```
xv6
```
 source code, find below code snippet.

```


mpmain(void)
{
  cprintf("cpu%d: starting %d\n", cpuid(), cpuid());
  idtinit();       // load idt register
  xchg(&(mycpu()->started), 1); // tell startothers() we're up
  scheduler();     // start running processes
}





```

Modify the 
```
cprintf
```
 line by adding 
```
xv6
```
. Then run 
```
make qemu-nox
```
 to see the greeting has changed with your modification.

```


cprintf("cpu%d: starting xv6 %d\n", cpuid(), cpuid());





```

---

### [](#Experiment-1-1--Adding-one-user-application-new-shell-command-on-xv6 "Experiment-1-1--Adding-one-user-application-new-shell-command-on-xv6")Experiment 1-1 : Adding one user application (new shell command) on xv6

To add one shell command/application in user space of xv6 requires two actions:

1.  Create the file 
    ```
    my-app.c
    ```
     (or other file name you prefer), under the directory of 
    ```
    xv6-public
    ```
    , same with 
    ```
    Makefile
    ```
     and other applications.
2.  In 
    ```
    Makefile
    ```
    , add 
    ```
    _my-app
    ```
     (or other file name you pick) to the parameter 
    ```
    UPROGS
    ```
    .

```
my-app.c
```
 file content

```


#include "types.h"
#include "stat.h"
#include "user.h"

int main(int argc, char *argv[])
{
    printf(1, "This is Marconi's app.\n");
    exit();
}





```

Add one line of 
```
_my-app
```
 to the 
```
UPROGS
```
 parameter in 
```
Makefile
```
.

```


UPROGS=\
        _cat\
        _echo\
        _forktest\
        _grep\
        _init\
        _kill\
        _ln\
        _ls\
        _mkdir\
        _rm\
        _sh\
        _stressfs\
        _usertests\
        _wc\
        _zombie\
        _my-app\





```

Let's check the result.

<table><tbody><tr><td>host Linux</td><td>qemu - xv6</td></tr><tr><td><div data-position="12172" data-infoprefix-length="6" data-endline="412" data-startline="401" class="part code-block-wrapper code-block-toolbar-handled"><pre class="click-event-handled"><code class="shell hljs"><div class="wrapper"><p><span class="hljs-meta">$ </span><span class="language-bash">make</span>
<span class="hljs-meta"># </span><span class="language-bash">output of make is omitted</span>
<span class="hljs-meta">$ </span><span class="language-bash"><span class="hljs-built_in">ls</span> -l my-app*</span>
-rw-rw-r-- 1 kernel-dev kernel-dev 43517 十一 20 15:44 my-app.asm
-rw-rw-r-- 1 kernel-dev kernel-dev   151 十一 15 08:10 my-app.c
-rw-rw-r-- 1 kernel-dev kernel-dev    72 十一 20 15:44 my-app.d
-rw-rw-r-- 1 kernel-dev kernel-dev  2696 十一 20 15:44 my-app.o
-rw-rw-r-- 1 kernel-dev kernel-dev   950 十一 20 15:44 my-app.sym
<span class="hljs-meta">$ </span><span class="language-bash">make qemu</span>
<span class="hljs-meta"># </span><span class="language-bash">Check the screen to the right of qemu <span class="hljs-keyword">for</span> xv6</span> 
</p></div></code></pre></div></td><td><div data-position="12625" data-infoprefix-length="6" data-endline="422" data-startline="417" class="part code-block-wrapper code-block-toolbar-handled"><pre class="click-event-handled"><code class="shell hljs"><div class="wrapper"><p><span class="hljs-meta">$ </span><span class="language-bash"><span class="hljs-built_in">ls</span> my-app-1</span>
my-app-1       2 18 12316
<span class="hljs-meta">$ </span><span class="language-bash">my-app-1</span>
This is Marconi's app.
</p></div></code></pre></div></td></tr></tbody></table>

---

### [](#Experiment-1-2--Adding-one-kernel-System-Call-in-xv6 "Experiment-1-2--Adding-one-kernel-System-Call-in-xv6")Experiment 1-2 : Adding one kernel System Call in xv6

Unlike adding an application in user space, it take much more procedures to add a system call in kernel space (all applications are in user space, not in kernel space. In kernel space, it is called system call).

To create a system call in kernel, it requires the following steps:

1.  Modify 
    ```
    syscall.h
    ```
    
2.  Modify 
    ```
    user.h
    ```
    
3.  Modify 
    ```
    usys.S
    ```
    
4.  Modify 
    ```
    syscall.c
    ```
    
5.  Modify 
    ```
    sysproc.c
    ```
    
6.  Modify 
    ```
    proc.c
    ```
    
7.  Modify 
    ```
    defs.h
    ```
    
8.  Create a user space application 
    ```
    pcpuid.c
    ```
    
9.  Update 
    ```
    Makefile
    ```
    
10.  Execute 
    ```
    make qemu
    ```

```


// Add one line to the end of syscall.h
#define SYS_getcpuid 22

// Add one line to the end of user.h
int getcpuid(void);

// Add one line to the end of usys.S
SYSCALL(getcpuid)
	
// Add one line between line 100 and 101 of syscall.c
ext int sys_getcpuid(void);
// Add one line between line 123 and 124 of syscall.c
[SYS_getcpuid] sys_getcpuid,

// Add the following lines to the end of sysproc.c
int
sys_getcpuid(void)
{
  return getcpuid();
}

// Add the following lines to the end of proc.c
int getcpuid(void)
{
  int cpuidnum;
  cli();
  cpuidnum = cpuid();
  sti(); 
  return cpuidnum;
}

// Add one line after proc.c section of file defs.h
// proc.c
int             getcpuid(void);

// Now we have already completed the implementation in kernel space, Next is to call getcpuid() from user application, let's call it pcpuid.c
// Create a new file name of pcpuid.c, with the following contents
#include "types.h"
#include "stat.h"
#include "user.h"

int main(int argc, char *argv[])
{
    printf(1, "my pid is : %d\n", getcpuid());
    exit();
}

// And add _pcpuid to parameter UPROGS in Makefile
UPROGS=\
        _pcpuid\





```

Now, execute 
```
make qemu
```
 to run into 
```
xv6 shell
```
, and run 
```
pcpuid
```
. (with 
```
CPUS=4 make qemu
```
 might get different 
```
pcpuid
```
 results.)

```


$ pcpuid
My CPU id is :0





```

You make it

---

### [](#Deep-dive-into-how-the-System-Call-example-works---1--more-descriptions "Deep-dive-into-how-the-System-Call-example-works---1--more-descriptions")Deep dive into how the System Call example works - 1 : more descriptions

The book explains in a little bit more details on how those files work.

1.  **Modify 
    ```
    syscall.h
    ```
    5.* : In xv6, each System Call has one unique ID, so adding 
    ```
    SYS_getcpuid
    ```
     with ID of 
    ```
    22
    ```
    .

```


#define SYS_getcpuid 22





```

2.  **Modify 
    ```
    user.h
    ```
    6.* : Declare user state entry function 
    ```
    getcpuid
    ```
     to the header file of 
    ```
    user.h
    ```
     14. 
    ```
    int getcpuid(void);
    ```
    . Then it can be called by user application program.

```


int getcpuid(void);





```

3.  **Modify 
    ```
    usys.S
    ```
    7.* : 
    ```
    usys.S
    ```
     defines a macro 
    ```
    SYSCALL(getcpuid)
    ```
     to move 
    ```
    SYS_getcpuid=22
    ```
     to register 
    ```
    eax
    ```
    , then issue interrupt command 
    ```
    int $T_SYSCALL
    ```

```


#define SYSCALL(name) \
  .globl name; \
  name: \
    movl $SYS_ ## name, %eax; \
    int $T_SYSCALL; \
    ret





```

Add one line in 
```
usys.S
```

```


SYSCALL(getcpuid)





```

4.  **Modify 
    ```
    syscall.c
    ```
    8.* : Define the entry for syscall 
    ```
    sys_getcpuid()
    ```
     when issueing 
    ```
    int $T_SYSCALL
    ```
     and 
    ```
    eax
    ```
     = 22.

```


extern int sys_getcpuid(void);





```

```


[SYS_getcpuid] sys_getcpuid,





```

Below is the 
```
syscall()
```
 snippet

```


void
syscall(void)
{
  int num;
  struct proc *curproc = myproc();

  num = curproc->tf->eax;
  if(num > 0 && num < NELEM(syscalls) && syscalls[num]) {
    curproc->tf->eax = syscalls[num]();
  } else {
    cprintf("%d %s: unknown sys call %d\n",
            curproc->pid, curproc->name, num);
    curproc->tf->eax = -1;
  }
}





```

Until now, the set up is ready for both 
```
getcpuid()
```
 and 
```
sys_getcpuid()
```
. We are going to implement the code for both. 
```
sys_getcpuid()
```
 is defined in the source file 
```
sysproc.c
```
, and 
```
getcpuid()
```
 defined in 
```
proc.c
```
.  
5\. **Modify 
```
sysproc.c
```
** : Implement 
```
sys_getcpuid()
```
 function. It just calls 
```
getcpuid()
```
 directly.

```


int
sys_getcpuid(void)
{
  return getcpuid();
}





```

6.  **Modify 
    ```
    proc.c
    ```
    10.* : Implement 
    ```
    getcpuid()
    ```
     in 
    ```
    proc.c
    ```
    . It is quite straight forward to call 
    ```
    cpuid()
    ```
    . However, it needs to disable interrupt first before calling it, so 
    ```
    cli()
    ```
     is added before and 
    ```
    sti()
    ```
     after.

```


int getcpuid(void)
{
  int cpuidnum;
  cli();
  cpuidnum = cpuid();
  sti();
  return cpuidnum;
}





```

7.  **Modify 
    ```
    defs.h
    ```
    11.* : 
    ```
    defs.h
    ```
     defines (almost) all the 
    ```
    xv6
    ```
     kernal data structure and functions. In order to get 
    ```
    sys_getcpuid()
    ```
     within 
    ```
    sysproc.c
    ```
     to be able to call 
    ```
    getcpuid()
    ```
    , we need to add 
    ```
    int getcpuid(void);
    ```
     in 
    ```
    defs.h
    ```
    .

```


int             getcpuid(void);





```

8.  **Create a user space application 
    ```
    pcpuid.c
    ```
    12.* : Relatively easy as other regular user applications.
---

### [](#Deep-dive-into-how-the-System-Call-example-works---2--trace-by-gdb "Deep-dive-into-how-the-System-Call-example-works---2--trace-by-gdb")Deep dive into how the System Call example works - 2 : trace by 
```
gdb
```

Now I understand better the design, but still not clear exactly how the program will flow among all those functional calls. So use 
```
gbd
```
 to trace the process flow.

```
qemu
```
 terminal screen

```


$ CPUS=1 make qemu-gdb





```

```
gdb
```
 terminal screen

```


$ gdb kernel
(gdb) c
# wait for qemu terminal screen ready and showing $ prompt
(gdb) CTRL+c
(gdb) layout next
(gdb) br syscall.c:141 if num==22
Breakpoint 1 at 0x80104830: file syscall.c, line 135.
(gdb) br sysproc.c:sys_getcpuid
Breakpoint 2 at 0x80105630: file sysproc.c, line 96.
(gdb) br proc.c:getcpuid
Breakpoint 3 at 0x80104080: file proc.c, line 537.
(gdb) c





```

Back to 
```
qemu
```
 screen

```


$ pcpuid <Enter>





```

We will see 
```
gdb
```
 screen pops up with Breakpint like below

```


Breakpoint 1, syscall () at syscall.c:141
(gdb) print num
$1 = 22
(gdb) n
=> 0x80105630 <sys_getcpuid>:   push   %ebp

Breakpoint 2, sys_getcpuid () at sysproc.c:96
(gdb) n
=> 0x80105633 <sys_getcpuid+3>: pop    %ebp
(gdb) n
=> 0x80105634 <sys_getcpuid+4>: jmp    0x80104080 <getcpuid>
sys_getcpuid () at sysproc.c:97
(gdb) n
=> 0x80105634 <sys_getcpuid+4>: jmp    0x80104080 <getcpuid>
sys_getcpuid () at sysproc.c:97
(gdb) n
=> 0x80104080 <getcpuid>:       push   %ebp

Breakpoint 3, getcpuid () at proc.c:537
(gdb) n 5
=> 0x80104092 <getcpuid+18>:    leave

(gdb) n
=> 0x80104093 <getcpuid+19>:    sar    $0x4,%eax
getcpuid () at proc.c:542
(gdb) n
=> 0x8010409c <getcpuid+28>:    ret
(gbd) n
=> 0x8010485a <syscall+42>:     lea    -0x8(%ebp),%esp
syscall () at syscall.c:147
(gdb) n
=> 0x801058e9 <trap+441>:       call   0x80103770 <myproc>
trap (tf=0x8df4bfb4) at trap.c:44
(gdb) n        
=> 0x8010581f <trap+239>:       lea    -0xc(%ebp),%esp
(gdb) n
=> 0x8010564e <alltraps+21>:    add    $0x4,%esp
alltraps () at trapasm.S:21






```

Based on above 
```
gdb
```
 findings and previous coding, I try to imagine the process flow like below. Though it needs to be validated. Advise is welcome, and more works to do

---

### [](#Deep-dive-into-how-the-System-Call-example-works---3--another-example-getpid "Deep-dive-into-how-the-System-Call-example-works---3--another-example-getpid")Deep dive into how the System Call example works - 3 : another example 
```
getpid
```

Try to understand the other (simple) System Call - 
```
getpid
```
, to see if 
```
getpid
```
 shows up at exactly the same source files.

```


$ grep -n "getpid" *.[ch]
syscall.c:92:extern int sys_getpid(void);
syscall.c:119:[SYS_getpid]  sys_getpid,
syscall.h:12:#define SYS_getpid 11
sysproc.c:40:sys_getpid(void)
user.h:22:int getpid(void);
usertests.c:434:  ppid = getpid();
usertests.c:1498:    ppid = getpid();





```

```
getpid
```
 only shows up in above 1,2,4,5 files (
```
syscall.h
```
, 
```
user.h
```
, 
```
syscall.c
```
, 
```
sysproc.c
```
) modified for 
```
gcpuid
```
, plus user application 
```
usertests.c
```
, but not in 
```
usys.S
```
, 
```
proc.c
```
, 
```
defs.h
```
.

---

### [](#xv6-binary-and-image "xv6-binary-and-image")xv6 binary and image

xv6 binary consists of 2 sections :

-   boot loader - 
    ```
    bootblock
    ```
    
-   kernel  
    Both are built by GNU GCC, and in ELF format. So it can be viewed and analyzed by 
    ```
    binutils
    ```
     tool. For those (including me) who are not familiar with ELF format, bootloader and 
    ```
    binutils
    ```
     tool can refer to Chap 4 of another book <<Linux GNU C 程式观察>> by the same author.

**Simplify the boot loader by putting kernel on the same disk image with boot loader**  
Reference from appendix B of [xv6 a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf), or translation in Mandarin [xv6代码阅读：系统引导](http://ybin.cc/os/xv6-boot/). There is a [draft version from Cox, Kaashoek, Morris released in 2010](https://www.cs.columbia.edu/~junfeng/11sp-w4118/lectures/boot.pdf), which explains in more details about bootstrap than later version in 2012.

The boot loader compiles to around 470 byes (definitely needs to be less than 510bytes, to fit into one sector, plus magic words of 0x55aa.) of machine code, depending on the optimizations used when compiling C code. **In order to fit in that small amout of space, the xv6 boot loader makes a major simpifying assumption, that the kernel has been written to the boot disk contiguously starting at sector 1. (Boot loader was stored at sector 0 of the boot disk).** We know that from the 
```
Makefile
```
 of 
```
xv6
```
. It is unlike modern PC uses a two-step boot process.

So 
```
xv6
```
 boot loader relies on the less space constraint BIOS for disk access rather than trying to drive the disk itself.

```


xv6.img: bootblock kernel fs.img
	dd if=/dev/zero of=xv6.img count=10000
	dd if=bootblock of=xv6.img conv=notrunc # bootblock部分放置到第一个扇区(该部分必须保证自己的size小于512bytes)
	dd if=kernel of=xv6.img seek=1 conv=notrunc # kernel代码放置到第二个以及以后的扇区





```

---

#### [](#xv6-binary-and-image---bootblock-description "xv6-binary-and-image---bootblock-description")xv6 binary and image - 
```
bootblock
```
 description

To understand how PC works from scratch, it might require some computer architecture and hardware/firmware/software, and some PC development history. Can refer to articles [MBR 載入位址 0x7C00 的來源與意義的調查結果](https://gist.github.com/letoh/2790559), or [From the bootloader to the kernel](https://0xax.gitbooks.io/linux-insides/content/Booting/linux-bootstrap-1.html).

x86 system BIOS (after checking hardware, or called POST, Power On Self Test) or 
```
qemu
```
 will load the first 512 byts boot code (or MBR from HDD) to RAM memory address 0x7c00, and jump to 0x7c00 to execute the boot code, it is 
```
bootblock
```
 used in 
```
xv6
```
. This 512 byte boot code will further load the kernel from HDD, then transfer the control to kernel.

```
bootblock
```
 file size is 512 bytes, and 
```
MBR boot sector
```
 when checked by 
```
file
```
 instruction.

```


$ ls -l bootblock
-rwxr-xr-x 1 ubuntu ubuntu 512 Nov 29 22:17 bootblock
$ file bootblock
bootblock: DOS/MBR boot sector





```

---

#### [](#xv6-binary-and-image---How-bootblock-is-generated-with-starting-address-from-7c00 "xv6-binary-and-image---How-bootblock-is-generated-with-starting-address-from-7c00")**xv6 binary and image - How 
```
bootblock
```
 is generated, with starting address from $7c00**

**A :** [Appendix B - The boot loader of "xv6 a simple, Unix-like teaching operating system"](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf) provides a clear view on boot sequence. It explains how 
```
bootasm.S
```
 and 
```
bootmain.c
```
 works.

Below chart is referred from the book "操作系統原型 - xv6 分析與實踐 羅秋明 著".

**1\. About which one is first between 
```
bootasm.S
```
 and 
```
bootmain.c
```
? :** Even I know the BIOS entry is $7c00, but I was not sure which one will 
```
bootblock
```
 start first? 
```
bootasm.S
```
 or 
```
bootmain.c
```
. (Normally, I would expect the program shall start from main(), haha, which is **not in this case**.) Finally, I learned from [Compiling & Linking](https://people.cs.pitt.edu/~xianeizhang/notes/Linking.html) that the linker scans the relocatable obj files and archives left to right in the same sequential order that they appear on the compiler driver's command line. (The driver automatically translates any .c files on the cmd line into .o files.) And in 
```
xv6 Makefile
```
, the 
```
bootasm.o
```
 is in front of 
```
bootmain.o
```
. So when BIOS completes the hardware setup, load the 'bootloader' 512 bytes into the memory address of $7c00, 
```
xv6
```
 will start from 
```
bootasm.S
```
.

```


bootblock: bootasm.S bootmain.c
        $(CC) $(CFLAGS) -fno-pic -O -nostdinc -I. -c bootmain.c
        $(CC) $(CFLAGS) -fno-pic -nostdinc -I. -c bootasm.S
        $(LD) $(LDFLAGS) -N -e start -Ttext 0x7C00 -o bootblock.o bootasm.o bootmain.o
        $(OBJDUMP) -S bootblock.o > bootblock.asm
        $(OBJCOPY) -S -O binary -j .text bootblock.o bootblock
        ./sign.pl bootblock





```

Also, we can cross check with the first few line of 
```
bootblock.asm
```
, which is exactly the same as the beginning of 
```
bootasm.S
```
.

```


bootblock.o:     file format elf32-i386


Disassembly of section .text:

00007c00 <start>:
# with %cs=0 %ip=7c00.

.code16                       # Assemble for 16-bit mode
.globl start
start:
  cli                         # BIOS enabled interrupts; disable
    7c00:       fa                      cli

  # Zero data segment registers DS, ES, and SS.
  xorw    %ax,%ax             # Set %ax to zero
    7c01:       31 c0                   xor    %eax,%eax
  movw    %ax,%ds             # -> Data Segment
    7c03:       8e d8                   mov    %eax,%ds
  movw    %ax,%es             # -> Extra Segment
    7c05:       8e c0                   mov    %eax,%es
  movw    %ax,%ss             # -> Stack Segment
    7c07:       8e d0                   mov    %eax,%ss






```

**2\. 
```
bootasm.S
```
 Code - Assembly bootstrap :**

Reference from appendix B of [xv6 a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf), or translation in Mandarin [xv6代码阅读：系统引导](http://ybin.cc/os/xv6-boot/)

**The main functions of xv6 bootasm.S is to initiates the CPU and the system**

2.1 Clear interrup - cli  
2.2 Zero data segment registers DS, ES and SS  
2.3 Enable A20 line to enable address capability beyond 1MB. (More info from [A20 - a pain from the past](https://www.win.tue.nl/~aeb/linux/kbd/A20.html))  
2.4 Switch from real to protected mode by loading GDT, and enable CR0\_PE bit  
2.5 Complete the transition to 32-bit protected mode to reload %cs and %eip by using a long jmp instruction  
2.6 Tell assembler to generate 32 bit code from now on. Then, set up the protected-mode data segment registers. Select Data Segement for DS, ES, and SS, null Segment for FS, and GS.  
2.7 Set up Stack Pointer and call into 
```
bootmain.c
```
  
2.8 If 
```
bootmain.c
```
 returns (it shouldn't but it would happen with error), trigger a Boch kind of emulator, then hangs by an infinite loop.

**2.1 
```
bootasm.S
```
 Code - 
```
80286/80386 protected mode
```
 and legacy 
```
8086 real mode
```
**

Before diving into how 
```
bootasm.S
```
 works, let's understand how it is defined in the Segment Descriptor, and some lagecy from 8086 to 80286, then 80386, and lately 64 bit. xv6 (and Linux) starts from 80386 design, however, x86 CPU always boots up in 8086 real mode first, so is the reason to under the lagacy.

-   Find below table from [x86-64处理器的几种运行模式](https://zhuanlan.zhihu.com/p/69334474)

![](images/v2-c2f06a68a48172453878ff804d956d27_1440w.jpg?source=172ae18b)

One thing worthwhile noticing is mentioned earlier that 
```
bootmain()
```
, the xv6 boot loader, makes a major simpifying assumption, that the kernel has been written to the boot disk contiguously starting at sector 1. And it uses BIOS API to read the kernel images into memory.

This [article - 2.1. Internal Microprocessor Architecture](https://www.byclb.com/TR/Tutorials/microprocessors/ch2_1.htm) describes the evolution from 
```
8086 real mode
```
 to 
```
80286 (16bit)/80386(32bit) protected mode
```
.

-   2.2. Real Mode Memory Addressing
-   2.3. Introduction to Protected Mode Memory Addressing  
    For the 80286 microprocessor, the base address is a 24-bit address, so segments begin at any location in its 16M bytes of memory. Note that the paragraph boundary limitation is re­moved in these microprocessors when operated in the protected mode. The 80386 and above use a 32-bit base address that allows segments to begin at any location in its 4G bytes of memory. Notice how the 80286 descriptor’s base address is upward-compatible to the 80386 through the Pentium II descriptor because its most-significant 16 bits are 0000H.

Figure below shows the format of a descriptor for the 80286 through the Pentium II. Note that each descriptor is 8 bytes in length, so the global and local descriptor tables are each a maximum of 64K bytes in length. Descriptors for the 80286 and the 80386 through the Pentium II differ slightly, but the 80286 descriptor is upward-compatible (with reserved 2 bytes). Though we can see the 'ugly' structure of descriptor in 80386 to be backward compatible with 80286.

![Descriptor difference between 80286 and 80386](images/image006.gif)

**2.2 
```
bootasm.S
```
 Code - Implementation of Global Descriptor Table (GDT)**

Segment Descriptor entry has a complex structure. (Reference from [osdev - GDT](https://wiki.osdev.org/Global_Descriptor_Table))

```
Segment Descriptor (contains 8bytes)
    
 +-------------+------+------+
 |<-  Byte7  ->|<-  Byte6  ->|
 |Base         |Flags |Limit |
 |63         56|55  52|51  48|
7+-------------+------+------+6
 +-------------+-------------+
 |<-  Byte5  ->|<-  Byte4  ->| 
 |Access Byte  |Base         |
 |47         40|39         32| 
5+-------------+-------------+4
 +-------------+-------------+
 |<-  Byte3  ->|<-  Byte2  ->|
 |Base                       |
 |31                       16|
3+---------------------------+2
 +-------------+-------------+
 |<-  Byte1  ->|<-  Byte0  ->|
 |Limit                      |
 |15                        0|
1+---------------------------+0

```

Below are code snippet related to GDP in 
```
xv6/x86.h
```
 and 
```
bootasm.S
```
.

```
xv6/x86.h
```

```
0650 //
0651 // assembler macros to create x86 segments
0652 //
0653 
0654 #define SEG_NULLASM \
0655 .word 0, 0; \
0656 .byte 0, 0, 0, 0
0657 
0658 // The 0xC0 means the limit is in 4096−byte units
0659 // and (for executable segments) 32−bit mode.
0660 #define SEG_ASM(type,base,lim) \
0661 .word (((lim) >> 12) & 0xffff), ((base) & 0xffff); \
0662 .byte (((base) >> 16) & 0xff), (0x90 | (type)), \
0663 (0xC0 | (((lim) >> 28) & 0xf)), (((base) >> 24) & 0xff)
0664 
0665 #define STA_X 0x8 // Executable segment
0666 #define STA_E 0x4 // Expand down (non−executable segments)
0667 #define STA_C 0x4 // Conforming code segment (executable only)
0668 #define STA_W 0x2 // Writeable (non−executable segments)
0669 #define STA_R 0x2 // Readable (executable segments)
0670 #define STA_A 0x1 // Accessed

```

```
xv6/bootasm.S
```

```
8438 # Switch from real to protected mode. Use a bootstrap GDT that makes
8439 # virtual addresses map directly to physical addresses so that the
8440 # effective memory map doesn’t change during the transition.
8441 lgdt gdtdesc
...
 # Bootstrap GDT
8481 .p2align 2 # force 4 byte alignment
8482 gdt:
8483 SEG_NULLASM # null seg
8484 SEG_ASM(STA_X|STA_R, 0x0, 0xffffffff) # code seg
8485 SEG_ASM(STA_W, 0x0, 0xffffffff) # data seg
8486 
8487 gdtdesc:
8488 .word (gdtdesc − gdt − 1) # sizeof(gdt) − 1
8489 .long gdt # address gdt

```

```
xv6
```
 code 
```
lines 0660-0663
```
 
```
SEG_ASM(type,base,lim)
```
 does the job of converting the values of 
```
type
```
, 
```
base
```
 and 
```
limit
```
 to the structure required by the _Segment Descriptor_.

line 
```
8484
```
 sets up for code segment, and line 8485 sets up for data segment.

```
8484 SEG_ASM(STA_X|STA_R, 0x0, 0xffffffff) # code seg
8485 SEG_ASM(STA_W, 0x0, 0xffffffff) # data seg

```

So, the Segment Descript of 
```
code segment
```
 in 
```
xv6 bootloader
```
 looks like this

```
Segment Descriptor (contains 8bytes)
    
 +-------------+------+------+
 |<-  Byte7  ->|<-  Byte6  ->|
 |Base         |Flags |Limit |
 |63         56|55  52|51  48|
7+-------------+------+------+6
 +-------------+-------------+
 |<-  Byte5  ->|<-  Byte4  ->| 
 |Access Byte  |Base         |
 |47         40|39         32| 
5+-------------+-------------+4
 +-------------+-------------+
 |<-  Byte3  ->|<-  Byte2  ->|
 |Base                       |
 |31                       16|
3+---------------------------+2
 +-------------+-------------+
 |<-  Byte1  ->|<-  Byte0  ->|
 |Limit                      |
 |15                        0|
1+---------------------------+0

```

And 
```
data segment
```
 looks like this

```
Segment Descriptor (contains 8bytes)
    
 +-------------+------+------+
 |<-  Byte7  ->|<-  Byte6  ->|
 |Base         |Flags |Limit |
 |63         56|55  52|51  48|
7+-------------+------+------+6
 +-------------+-------------+
 |<-  Byte5  ->|<-  Byte4  ->| 
 |Access Byte  |Base         |
 |47         40|39         32| 
5+-------------+-------------+4
 +-------------+-------------+
 |<-  Byte3  ->|<-  Byte2  ->|
 |Base                       |
 |31                       16|
3+---------------------------+2
 +-------------+-------------+
 |<-  Byte1  ->|<-  Byte0  ->|
 |Limit                      |
 |15                        0|
1+---------------------------+0

```

---

**3\. 
```
bootmain.c
```
 Code - C bootstrap:**

As described in 
```
bootmain.c
```
, 
```
bootmain()
```
 loads an ELF kernel image from the disk starting at sector 1 and then jumps to the kernel entry routine. That is the only task of what 
```
bootmain.c
```
 does.

**3.1 
```
bootmain.c
```
 C bootstrap memory map:**

```
xv6
```
 Memory map with reference from [xv6代码阅读：系统引导](http://ybin.cc/os/xv6-boot/).

**3.1.1 Memory map loading 512 bytes from disc sector 0**

The CPU is in 
```
real
```
 mode, in which it simulates an Intel 8088. In real mode, there are eight 16-bit general registers, but the processor sends 20 bits of address to memory. The segment registers %cs, %ds, %es, and %ss provide the additional bits necessary to generate 20-bit memory address from 16-bit registers. That gives x86 CPU with addressing capability of maximum 
```
1MBytes
```
 in real mode. We will call the **_segment:offset_** as **virtual memory** reference in real mode, and processor chip sends to memory 20-bit **physical addresses**.

Quote from [Cox, Kaashoek, Morris - Bootstrap](https://www.cs.columbia.edu/~junfeng/11sp-w4118/lectures/boot.pdf)

Real mode’s 16-bit general-purpose and segment registers make it awkward for a program to use more than 65,536 bytes of memory, and impossible to use more than a megabyte. Modern x86 processors have a **"protected mode"** which allows physical addresses to have many more bits, and a **"32-bit" mode** that causes registers, virtual addresses, and most integer arithmetic to be carried out with 32 bits rather than 16. The xv6 boot sequence enables both modes.

(x86 default) BIOS loads the first 512 bytes from disk, load it to 0x7C00 memory address, and jump to 0x7C00 to start boot sequence.

```
(not in scale)

CPU working in real mode

  0x100000(1MB) -> +-------------------+ <-   1MB (0x100000)
                   |                   | <- 512KB  (0x80000)
                   |                   | <- 256KB  (0x40000)
                   |                   | <- 128KB  (0x20000)
                   |                   | <-  64KB  (0x10000)
                   |                   |
         0x7E00 -> +-------------------+
   boot magic word |      0x55 0xAA    |
         0x7DFE -> +-------------------+
                   |filled with zero(0)|
                   |                   |
.gdtdesc+6bytes -> +-------------------+
                   |                   |
       .gdtdesc -> +-----+-------------+
                   |     |  seg null   |
                   | GDT |  seg code   |
                   |     |  seg data   |
         .gdt   -> +-----+-------------+ <- gdtr(GDT Register)
                   |                   |
                   |                   |
    bootmain()  -> |                   |
                   |        code       |
                   |                   |
      .start32  -> |                   |
                   |                   |
(0x7c00).start  -> +---------+---------+ <- esp
                   |         |         |
                   |         v         | 
                   |       stack       |
                   |                   |
                   |                   |
                   +-------------------+ <- 0MB

```

\*\*3.1.2 Memory map after 
```
bootasm.S
```
 and 
```
bootmain.c
```
 \*\*

```
bootasm.S
```

```
/*
读取kernel数据到内存0x10000处，读取之后内存的样子如下:
0x10000(64KB)这个地方的内容只是暂时存放kernel img(elf文件)的hdr内容的，
根据elf header的内容进一步读取kernel img的内容，实际的内容将会存在在
1MB地址处，这个1MB地址是在kernel.ld中定义的(AT(0x100000))，这恰好跟
kernel memlayout吻合起来，见memlayout.h。

                   +-------------------+  4GB
                   |                   |
                   |                   |
                   |                   |
                   |                   |
                   |                   |
                   |                   |
                   |                   |
                   |                   |
                   +-------------------+
                   |                   |
 (main.c)main() -> |      kernel       |
       Entry.S? -> |                   |
  0x100000(1MB) -> +-------------------+
                   |                   |
  0x10000(64KB) -> +elf hdr of kern img+    (tmp use. elf header content)                    
                   |                   |
   0x7c00 + 512 -> |      0x55 0xAA    |
   0x7c00 + 510 -> |                   |
                   |                   |
       .gdtdesc -> +-------------------+
                   |                   |
           .gdt -> +-----+-------------+ <- gdtr(GDT Register)
                   |     |  seg null   |
                   | GDT |  seg code   |
                   |     |  seg data   |
                   +-----+-------------+
                   |                   |
                   |                   |
    bootmain()  -> |                   |
                   |        code       |
                   |                   |
      .start32  -> |                   |
                   |                   |
(0x7c00).start  -> +---------+---------+ <- esp
                   |         |         |
                   |         v         |
                   |       stack       |
                   |                   |
                   |                   |
                   +-------------------+  0GB

 */

```

Check [x86 inline assembly](https://hackmd.io/@MarconiJiang/x86assembly#Assembly-Language--Inline-Assembly-in-C-Language-Example---insl) for detail explanation on inline aseembly in 
```
bootmain.c
```
 line 8573 
```
insl(0x1F0, dst, SECTSIZE/4);
```

---

### [](#File-Descriptors "File-Descriptors")**File Descriptors**

**A :** [簡介 file descriptor (檔案描述符)](https://www.hy-star.com.tw/tech/linux/fd/fd.html)

 fd Number | Name | Function |
| --- | --- | --- |
 0 | stdin | 標準輸入 |
 1 | stdout | 標準輸出 |
 2 | stderr | 標準錯誤 |

---

### [](#Testing-multiple-cores-and-fork "Testing-multiple-cores-and-fork")**Testing multiple cores and 
```
fork
```
**

Page 10, section 1.2.3  
Page 23, section 2.3

---

## [](#讀書心得---xv6-a-simple-Unix-like-teaching-operating-system "讀書心得---xv6-a-simple-Unix-like-teaching-operating-system")讀書心得 - xv6 a simple, Unix-like teaching operating system

To those who are interested in boot sequences of xv6, suggest to read below _["Appendix A - Source code boot sequence"](#Appendix-A---Source-code-in-boot-sequence)_ and _["Appendix B - xv6 Bootstrap"](#Appendix-B---xv6-Bootstrap)_, from which [draft version from Cox, Kaashoek, Morris released in 2010](https://www.cs.columbia.edu/~junfeng/11sp-w4118/lectures/boot.pdf) explains in more details of boot sequence, before reading this book [xv6 book (pdf) - xv6 a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf). It also contains this topic in its _"Appendix B The boot loader"_, though with less details.

---

## [](#Appendix-A---Source-code-in-boot-sequence "Appendix-A---Source-code-in-boot-sequence")Appendix A - Source code in boot sequence

 Item | Source code /  
Function Entry | Line no. <sup>\[1\]</sup> | Description | Memory address/  
Entry point | Call from | x86 mode | user/kernel mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
 1. | 
```
bootasm.S
```
 /  
```
start:
```
 | 9100  
9111 | Start of bootloader sequence.
BIOS loads this code from first sector (0) of HDD into memory address 
```
0x7c00 - 0x7e00
```
 and starts execution in real mode with 
```
%cs=0 %ip=0x7c00
```

```
bootasm.S
```
 sets up A20 line, switches from real mode to 80286 protected mode, then to 32bit 80386 protected mode.

 | 
```
0x7c00 - 0x7e00
```
 (just below 32KB)  
Entry: 
```
0x7c00
```
 | BIOS | Real -> Protected (16bit) -> Protected (32bit) |  |
 2. | 
```
bootmain.c
```
 /  
```
bootmain(void)
```
 | 9200  
9216 | Part of Bootblock, along with 
```
bootasm.S
```
.

The function 
```
bootmain()
```
 loads ELF image _(contains 
```
elf header
```
 and 
```
program header
```
)_ from HDD sector 1 _(right after the bootloader of HDD sector 0)_, and store in scratch memory address 
```
0x10000 (64KB)
```
 for temporary usage.

Follow the contents of 
```
elf header / program header
```
, and read again from HDD to the memory address specified.

Then jump to and execute kernel 
```
entry.S entry:
```
 routine

 | 
```
0x7c00 - 0x7e00 (just below 32KB)
```
  
Entry: 
```
0x7cxx
```
 _(following bootasm.S, real address depending on xv6 compiled result)_ | 
```
bootasm.S
```
 | Protected (32bit) |  |
 3. | 
```
entry.S
```
 /  
```
_start
```
  
```
entry:
```
 | 1100  
1139  
1144 | The xv6 kernel starts executing in this fie.

Entering xv6 on boot processor, turn on page size extention, set up stack pointer, jump to 
```
main()
```


 | 
```
0x100000 - 0x1063ca
```
 & 
```
0x1073e0 - 0x107b7e
```
<sup>\[2\]</sup>  
Entry point : 
```
0x10000c(1MB)
```
<sup>\[3\]</sup> | 
```
bootmain.c
```
 | Protected (32bit) |  |
 4. | 
```
main.c
```
 /  
```
main(void)
```
 | 1300  
1316 | Bootstrap processor starts running C code here.

Allocate a real stack and switch to it, first doing some setup required for memory allocator to work. Tasks are listed in <sup>\[4\]</sup>

 | 
```
0x100000 - 0x1063ca
```
 & 
```
0x1073e0 - 0x107b7e
```
<sup>\[2\]</sup>  
Entry point : 
```
0x10xxxx
```
 _(following 
```
entry.S
```
, real address depending on xv6 compiled result)_ | 
```
entry.S
```
 | Protected (32bit) |  |

\[1\]: Line no. of xv6 rev9 source code  
\[2\]: Check page 6 of [draft version from Cox, Kaashoek, Morris released in 2010](https://www.cs.columbia.edu/~junfeng/11sp-w4118/lectures/boot.pdf)

```
# objdump -p kernel
kernel: file format elf32-i386
Program Header:
LOAD off 0x00001000 vaddr 0x00100000 paddr 0x00100000 align 2**12
filesz 0x000063ca memsz 0x000063ca flags r-x
LOAD off 0x000073e0 vaddr 0x001073e0 paddr 0x001073e0 align 2**12
filesz 0x0000079e memsz 0x000067e4 flags rwSTACK off 0x00000000 vaddr 0x00000000 paddr 0x00000000 align 2**2
filesz 0x00000000 memsz 0x00000000 flags rwx

```

\[3\]: Check [xv6启动源码阅读 - csdn](https://blog.csdn.net/vally1989/article/details/71796482)  
\[4\]: 
```
main()
```
 function does the following tasks

```
1316 int
1317 main(void)
1318 {
1319   kinit1(end, P2V(4*1024*1024)); // phys page allocator
1320   kvmalloc();    // kernel page table
1321   mpinit();      // detect other processors
1322   lapicinit();   // interrupt controller
1323   seginit();     // segment descriptors
1324   cprintf("\ncpu%d: starting xv6\n\n", cpunum());
1325   picinit();     // another interrupt controller
1326   ioapicinit();  // another interrupt controller
1327   consoleinit(); // console hardware
1328   uartinit();    // serial port
1329   pinit();       // process table
1330   tvinit();      // trap vectors
1331   binit();       // buffer cache
1332   fileinit();    // file table
1333   ideinit();     // disk
1334   if(!ismp)
1335     timerinit(); // uniprocessor timer
1336   startothers(); // start other processors
1337   kinit2(P2V(4*1024*1024), P2V(PHYSTOP)); // must come after startothers()
1338   userinit();    // first user process
1339   mpmain();      // finish this processor’s setup
1340 }

```

---

## [](#Appendix-B---xv6-Bootstrap "Appendix-B---xv6-Bootstrap")Appendix B - xv6 Bootstrap

There is a [draft version from Cox, Kaashoek, Morris released in 2010](https://www.cs.columbia.edu/~junfeng/11sp-w4118/lectures/boot.pdf), which explains in more details about bootstrap than later version in 2016. It uses [xv6 rev4](https://www.cs.columbia.edu/~junfeng/11sp-w4118/xv6/xv6-rev4.pdf) as reference source code, which is different from [xv6 rev9 source code pdf](https://pdos.csail.mit.edu/6.828/2016/xv6/xv6-rev9.pdf) used in xv6 book. (we use the rev9 as the reference throughout this note for consistance)

---

#### [](#Line-9111-bootasmS "Line-9111-bootasmS")Line 9111 
```
bootasm.S
```

Below is the complete list of 
```
bootasm.S
```
 source code.

```
9100 #include "asm.h"
9101 #include "memlayout.h"
9102 #include "mmu.h"
9103	
9104 # Start the first CPU: switch to 32−bit protected mode, jump into C.
9105 # The BIOS loads this code from the first sector of the hard disk into
9106 # memory at physical address 0x7c00 and starts executing in real mode
9107 # with %cs=0 %ip=7c00.
9108	
9109 .code16	# Assemble for 16−bit mode
9110 .globl start
9111 start:
9112    cli  	# BIOS enabled interrupts; disable
9113	
9114	# Zero data segment registers DS, ES, and SS.
9115	xorw	%ax,%ax	    # Set %ax to zero
9116	movw	%ax,%ds	    # −> Data Segment
9117	movw	%ax,%es	    # −> Extra Segment
9118	movw	%ax,%ss	    # −> Stack Segment
9119	
9120	# Physical address line A20 is tied to zero so that the first PCs
9121	# with 2 MB would run software that assumed 1 MB. Undo that.
9122 seta20.1:		
9123	inb	$0x64,%al	# Wait for not busy
9124	testb	$0x2,%al	
9125	jnz	seta20.1	
9126			
9127	movb	$0xd1,%al	# 0xd1 −> port 0x64
9128	outb	%al,$0x64	
9129			
9130	seta20.2:		
9131	inb	$0x64,%al	# Wait for not busy
9132	testb	$0x2,%al	
9133	jnz	seta20.2	
9134			
9135	movb	$0xdf,%al	# 0xdf −> port 0x60
9136	outb	%al,$0x60	
9137
9138	# Switch from real to protected mode. Use a bootstrap GDT that makes 
9139	# virtual addresses map directly to physical addresses so that the 
9140	# effective memory map doesn’t change during the transition.
9141	lgdt	gdtdesc 
9142	movl	%cr0, %eax
9143	orl	$CR0_PE, %eax 
9144	movl	%eax, %cr0 
9150	# Complete the transition to 32−bit protected mode by using a long jmp
9151	# to reload %cs and %eip. The segment descriptors are set up with no
9152	# translation, so that the mapping is still the identity mapping.
9153	ljmp	$(SEG_KCODE<<3), $start32
9154	
9155 .code32 # Tell assembler to generate 32−bit code now.
9156 start32:
9157	# Set up the protected−mode data segment registers
9158	movw	$(SEG_KDATA<<3), %ax	# Our data segment selector
9159	movw	%ax, %ds	# −> DS: Data Segment
9160	movw	%ax, %es	# −> ES: Extra Segment
9161	movw	%ax, %ss	# −> SS: Stack Segment
9162	movw	$0, %ax	# Zero segments not ready for use
9163	movw	%ax, %fs	# −> FS
9164	movw	%ax, %gs	# −> GS
9165	
9166	# Set up the stack pointer and call into C.
9167	movl	$start, %esp
9168	call	bootmain
9169	
9170	# If bootmain returns (it shouldn’t), trigger a Bochs
9171	# breakpoint if running under Bochs, then loop.
9172	movw	$0x8a00, %ax	# 0x8a00 −> port 0x8a00
9173	movw	%ax, %dx	
9174	outw	%ax, %dx	
9175	movw	$0x8ae0, %ax	# 0x8ae0 −> port 0x8a00
9176	outw	%ax, %dx	
9177 spin:		
9178 jmp	spin	
9179			
9180 # Bootstrap GDT		
9181 .p2align 2		# force 4 byte alignment
9182 gdt:		
9183	SEG_NULLASM		# null seg
9184	SEG_ASM(STA_X|STA_R, 0x0, 0xffffffff)	# code seg
9185	SEG_ASM(STA_W, 0x0, 0xffffffff)	# data seg
9186		
9187 gdtdesc:
9188	.word	(gdtdesc − gdt − 1)	# sizeof(gdt) − 1
9189	.long	gdt	# address gdt 

```

---

#### [](#Line-9216-bootmainc "Line-9216-bootmainc")Line 9216 
```
bootmain.c
```

```
9200 // Boot loader.
9201 //
9202 // Part of the boot block, along with bootasm.S, which calls bootmain().
9203 // bootasm.S has put the processor into protected 32−bit mode.
9204 // bootmain() loads an ELF kernel image from the disk starting at
9205 // sector 1 and then jumps to the kernel entry routine.
9206	
9207 #include "types.h"
9208 #include "elf.h"
9209 #include "x86.h"
9210 #include "memlayout.h"
9211	
9212 #define SECTSIZE 512
9213	
9214 void readseg(uchar*, uint, uint);
9215	
9216 void
9217 bootmain(void)
9218 {
9219   struct elfhdr *elf;
9220   struct proghdr *ph, *eph;
9221   void (*entry)(void);
9222   uchar* pa;
9223 
9224   elf = (struct elfhdr*)0x10000; // scratch space
9225 
9226   // Read 1st page off disk
9227   readseg((uchar*)elf, 4096, 0);
9228 
9229   // Is this an ELF executable?
9230   if(elf−>magic != ELF_MAGIC)
9231     return; // let bootasm.S handle error
9232 
9233   // Load each program segment (ignores ph flags).
9234   ph = (struct proghdr*)((uchar*)elf + elf−>phoff);
9235   eph = ph + elf−>phnum;
9236   for(; ph < eph; ph++){
9237     pa = (uchar*)ph−>paddr;
9238     readseg(pa, ph−>filesz, ph−>off);
9239     if(ph−>memsz > ph−>filesz)
9240       stosb(pa + ph−>filesz, 0, ph−>memsz − ph−>filesz);
9241   }
9242 
9243   // Call the entry point from the ELF header.
9244   // Does not return!
9245   entry = (void(*)(void))(elf−>entry);
9246   entry();
9247 }
9248
9249
9250 void
9251 waitdisk(void)
9252 {
9253	// Wait for disk ready.
9254	while((inb(0x1F7) & 0xC0) != 0x40)
9255	 ;
9256 }
9257	
9258 // Read a single sector at offset into dst.
9259 void
9260 readsect(void *dst, uint offset)
9261 {
9262	// Issue command.
9263	waitdisk();
9264	outb(0x1F2, 1);	// count = 1
9265	outb(0x1F3, offset);
9266	outb(0x1F4, offset >> 8);
9267	outb(0x1F5, offset >> 16);
9268	outb(0x1F6, (offset >> 24) | 0xE0);
9269	outb(0x1F7, 0x20); // cmd 0x20 − read sectors
9270	
9271	// Read data.
9272	waitdisk();
9273	insl(0x1F0, dst, SECTSIZE/4);
9274 }
9275	
9276 // Read ’count’ bytes at ’offset’ from kernel into physical address ’pa’.
9277 // Might copy more than asked.
9278 void
9279 readseg(uchar* pa, uint count, uint offset)
9280 {
9281	uchar* epa;
9282	
9283	epa = pa + count;
9284	
9285	// Round down to sector boundary.
9286	pa −= offset % SECTSIZE;
9287	
9288	// Translate from bytes to sectors; kernel starts at sector 1.
9289	offset = (offset / SECTSIZE) + 1;
9290	
9291	// If this is too slow, we could read lots of sectors at a time.
9292	// We’d write more to memory than asked, but it doesn’t matter −−
9293	// we load in increasing order.
9294	for(; pa < epa; pa += SECTSIZE, offset++)
9295	  readsect(pa, offset);
9296 }

```

---

#### [](#Line-9234-ph--struct-proghdrucharelf--elf−gtphoff "Line-9234-ph--struct-proghdrucharelf--elf−gtphoff")Line 9234 ph = (struct proghdr\*)((uchar\*)elf + elf−>phoff);

Check [wiki - Executable and Linkable Format (ELF)](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) about [File header](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format#File_header) and [Program header](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format#Program_header) for both 32 and 64 bit format, which xv6 uses 32 bit format. xv6 defines in 
```
 xv6/elf.h
```
 about 
```
elfhdr
```
 and 
```
proghdr
```
.

```
1004 // File header
1005 struct elfhdr {
1006   uint magic; // must equal ELF_MAGIC
1007   uchar elf[12];
1008   ushort type;
1009   ushort machine;
1010   uint version;
1011   uint entry;
1012   uint phoff;
1013   uint shoff;
1014   uint flags;
1015   ushort ehsize;
1016   ushort phentsize;
1017   ushort phnum;
1018   ushort shentsize;
1019   ushort shnum;
1020   ushort shstrndx;
1021 };
1022 
1023 // Program section header
1024 struct proghdr {
1025   uint type;
1026   uint off;
1027   uint vaddr;
1028   uint paddr;
1029   uint filesz;
1030   uint memsz;
1031   uint flags;
1032   uint align;
1033 };

```

---

#### [](#Line-9245-entry--voidvoidelf−gtentry "Line-9245-entry--voidvoidelf−gtentry")Line 9245 entry = (void(\*)(void))(elf−>entry);

Check [Stackoverflow - Casting an address to a function: using "void(\*)(void)"](https://stackoverflow.com/questions/21081156/casting-an-address-to-a-function-using-void-void).

```
((void (*)(void))
```
  
It's casting the expression  
```
(ELFHDR->e_entry)
```
  
to be a pointer to a function that takes no arguments and returns nothing.

or another explaination

The tool you want is [cdecl](http://cdecl.org/), which translates C types into English. In this case, it translates:

```
(void (*)(void))
```

into:

```
cast unknown_name into pointer to function (void) returning void
```

---

#### [](#Line-1144-entryS "Line-1144-entryS")Line 1144 
```
entry.S
```

```
1100 # The xv6 kernel starts executing in this file. This file is linked with 1101 # the kernel C code, so it can refer to kernel symbols such as main(). 1102 # The boot block (bootasm.S and bootmain.c) jumps to entry below.
1103
1104 # Multiboot header, for multiboot boot loaders like GNU Grub. 1105 # http://www.gnu.org/software/grub/manual/multiboot/multiboot.html
1106 #
1107 # Using GRUB 2, you can boot xv6 from a file stored in a
1108 # Linux file system by copying kernel or kernelmemfs to /boot 1109 # and then adding this menu entry:
1110 #
1111 # menuentry "xv6" { 1112 # insmod ext2
1113 # set root=’(hd0,msdos1)’ 1114 # set kernel=’/boot/kernel’ 1115 # echo "Loading ${kernel}..."
1116 # multiboot ${kernel} ${kernel} 1117 # boot
1118 # }
1119
1120 #include "asm.h"
1121 #include "memlayout.h"
1122 #include "mmu.h"
1123 #include "param.h"
1124
1125 # Multiboot header. Data to direct multiboot loader. 1126 .p2align 2
1127 .text
1128 .globl multiboot_header
1129 multiboot_header:
1130	#define magic 0x1badb002 1131	#define flags 0
1132	.long magic
1133	.long flags
1134	.long (−magic−flags)
1135
1136 # By convention, the _start symbol specifies the ELF entry point. 1137 # Since we haven’t set up virtual memory yet, our entry point is 1138 # the physical address of ’entry’.
1139 .globl _start
1140 _start = V2P_WO(entry) 1141
1142 # Entering xv6 on boot processor, with paging off. 1143 .globl entry
1144 entry:
1145	# Turn on page size extension for 4Mbyte pages 1146	movl	%cr4, %eax
1147	orl	$(CR4_PSE), %eax 1148	movl	%eax, %cr4
1149	# Set page directory
1150	movl	$(V2P_WO(entrypgdir)), %eax 1151	movl	%eax, %cr3
1152	# Turn on paging. 1153	movl	%cr0, %eax
1154	orl	$(CR0_PG|CR0_WP), %eax 1155	movl	%eax, %cr0
1156
1157	# Set up the stack pointer.
1158	movl $(stack + KSTACKSIZE), %esp 1159
1160	# Jump to main(), and switch to executing at
1161	# high addresses. The indirect call is needed because 1162	# the assembler produces a PC−relative instruction 1163	# for a direct jump.
1164	mov $main, %eax 1165	jmp *%eax
1166
1167 .comm stack, KSTACKSIZE 

```

---

#### [](#Line-1316-mainc "Line-1316-mainc")Line 1316 
```
main.c
```

```
1300	#include "types.h"
1301	#include "defs.h"
1302	#include "param.h"
1303	#include "memlayout.h"
1304	#include "mmu.h"
1305	#include "proc.h"
1306	#include "x86.h"
1307	
1308	static void startothers(void);
1309	static void mpmain(void) attribute ((noreturn));
1310	extern pde_t *kpgdir;
1311	extern char end[]; // first address after kernel loaded from ELF file
1312	
1313	// Bootstrap processor starts running C code here.
1314	// Allocate a real stack and switch to it, first
1315	// doing some setup required for memory allocator to work.
1316 int
1317 main(void)
1318 {
1319	kinit1(end, P2V(4*1024*1024)); // phys page allocator
1320	kvmalloc();	// kernel page table
1321	mpinit();	// detect other processors
1322	lapicinit();	// interrupt controller
1323	seginit();	// segment descriptors
1324	cprintf("\ncpu%d: starting xv6\n\n", cpunum());
1325	picinit();	// another interrupt controller
1326	ioapicinit();	// another interrupt controller
1327	consoleinit();	// console hardware
1328	uartinit();	// serial port
1329	pinit();	// process table
1330	tvinit();	// trap vectors
1331	binit();	// buffer cache
1332	fileinit();	// file table
1333	ideinit();	// disk
1334	if(!ismp)
1335	timerinit();	// uniprocessor timer
1336	startothers();	// start other processors
1337	kinit2(P2V(4*1024*1024), P2V(PHYSTOP)); // must come after startothers()
1338	userinit();	// first user process
1339	mpmain();	// finish this processor’s setup
1340 }
...
...
1350 // Other CPUs jump here from entryother.S.
1351 static void
1352 mpenter(void)
1353 {
1354	switchkvm();
1355	seginit();
1356	lapicinit();
1357	mpmain();
1358 }
1359	
1360 // Common CPU setup code.
1361 static void
1362 mpmain(void)
1363 {
1364	cprintf("cpu%d: starting\n", cpunum());
1365	idtinit();	// load idt register
1366	xchg(&cpu−>started, 1); // tell startothers() we’re up
1367	scheduler();	// start running processes
1368 }
1369	
1370 pde_t entrypgdir[]; // For entry.S
1371	
1372 // Start the non−boot (AP) processors.
1373 static void
1374 startothers(void)
1375 {
1376	extern uchar _binary_entryother_start[], _binary_entryother_size[];
1377	uchar *code;
1378	struct cpu *c;
1379	char *stack;
1380	
1381	// Write entry code to unused memory at 0x7000.
1382	// The linker has placed the image of entryother.S in
1383	// _binary_entryother_start.
1384	code = P2V(0x7000);
1385	memmove(code, _binary_entryother_start, (uint)_binary_entryother_size);
1386	
1387	for(c = cpus; c < cpus+ncpu; c++){
1388	if(c == cpus+cpunum()) // We’ve started already.
1389	continue;
1390	
1391	// Tell entryother.S what stack to use, where to enter, and what
1392	// pgdir to use. We cannot use kpgdir yet, because the AP processor
1393	// is running in low memory, so we use entrypgdir for the APs too.
1394	stack = kalloc();
1395	*(void**)(code−4) = stack + KSTACKSIZE;
1396	*(void**)(code−8) = mpenter;
1397	*(int**)(code−12) = (void *) V2P(entrypgdir);
1398	
1399	lapicstartap(c−>apicid, V2P(code));
1400	// wait for cpu to finish mpmain() 
1401	while(c−>started == 0)
1402	  ;
1403	}
1404 }
1405
1406 // The boot page table used in entry.S and entryother.S.
1407 // Page directories (and page tables) must start on page boundaries, 1408 // hence the aligned attribute.
1409 // PTE_PS in a page directory entry enables 4Mbyte pages. 1410
1411 attribute (( aligned (PGSIZE))) 
1412 pde_t entrypgdir[NPDENTRIES] = {
1413	// Map VA’s [0, 4MB) to PA’s [0, 4MB)
1414	[0] = (0) | PTE_P | PTE_W | PTE_PS,
1415	// Map VA’s [KERNBASE, KERNBASE+4MB) to PA’s [0, 4MB)
1416	[KERNBASE>>PDXSHIFT] = (0) | PTE_P | PTE_W | PTE_PS,
1417 };

```

---

#### [](#xv6-Compile-amp-Make---xv6-Makefile-LD--b-binary-initcode-entryother "xv6-Compile-amp-Make---xv6-Makefile-LD--b-binary-initcode-entryother")xv6 Compile & Make - 
```
xv6 Makefile $(LD) -b binary initcode entryother
```

[Stackoverflow article $(LD) -b binary](https://stackoverflow.com/questions/29034840/binutils-kernel-binary-meaning) explains 
```
xv6
```
 how linker work to generate the kernel, with command line below:

```
$(LD) $(LDFLAGS) -T kernel.ld -o kernel entry.o $(OBJS) -b binary initcode entryother

```

As you can see, it uses -b binary to embed the files initcode and entryother, so the above symbols will be defined during this process.

---

## [](#References "References")References

-   **xv6 officials**  -   [MIT PDOS (Parallel and Distributed Operating Systems group at MIT CSAIL) xv6 source code github](https://github.com/mit-pdos/xv6-public)    -   [xv6 revisions](https://github.com/mit-pdos/xv6-public/tags)
              -   [xv6 book (html) - xv6 a simple, Unix-like teaching operating system](https://pekopeko11.sakura.ne.jp/unix_v6/xv6-book/en/index.html)
              -   [xv6 book (pdf) - xv6 a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf)      -   [xv6 rev9 source code pdf - the version used in xv6 book](https://pdos.csail.mit.edu/6.828/2016/xv6/xv6-rev9.pdf)
                  
              -   There is a [draft version from Cox, Kaashoek, Morris released in 2010](https://www.cs.columbia.edu/~junfeng/11sp-w4118/lectures/boot.pdf), which explains in more details about bootstrap than later version in 2016.      -   Use [xv6 rev4](https://www.cs.columbia.edu/~junfeng/11sp-w4118/xv6/xv6-rev4.pdf) as reference
          
      -   [Lions' Commentary on UNIX' 6th Edition, John Lions](http://www.lemis.com/grog/Documentation/Lions/)    -   [Lions' Commentary on UNIX' 6th Edition, John Lions (pdf version)](http://www.lemis.com/grog/Documentation/Lions/book.pdf)
          
      -   [Washington Univ. CSE451 course](https://courses.cs.washington.edu/courses/cse451/15au/schedule.html)
      -   [OSDev wiki](https://wiki.osdev.org/)
---
-   **xv6 English article collections**  -   [xv6 explained by YehudaShapira  
          ](https://github.com/YehudaShapira/xv6-explained)    -   [xv6 code explained](https://github.com/YehudaShapira/xv6-explained/blob/master/xv6%20Code%20Explained.md) : though not sure about what the entry point means
          
      -   [CTRL + P : Repository contains the code developed for Xv6 Operating system to implement Ctrl + P functionality](https://github.com/anandankit95/Ctrl-P)    -   The Ctrl + P, or Ctrl + p key combination gives the following details in the following given format:-
              -   Process ID, Process Name, Uptime ,Process Status
          
      -   [Intro to xv6 - write a System Call ny Tyler Allen/](https://tnallen.people.clemson.edu/2019/03/04/intro-to-xv6.html)
      -   Principles of Operating Systems by Anton Burtsev    -   [Lecture 7: System boot (2018 fall - 143A)](https://www.ics.uci.edu/~aburtsev/143A/2018fall/lectures/lecture06-system-boot/lecture06-system-boot.pdf) : [https://www.ics.uci.edu/~aburtsev/143A/2018fall/lectures/lecture06-system-boot/lecture06-system-boot.pdf](https://www.ics.uci.edu/~aburtsev/143A/2018fall/lectures/lecture06-system-boot/lecture06-system-boot.pdf)
              -   [CS5460/6460: Operating Systems Lecture 9: Finishing system boot, and system init](https://www.ics.uci.edu/~aburtsev/143A/2017fall/lectures/lecture09-kernel-init/lecture09-kernel-init.pdf): [https://www.ics.uci.edu/~aburtsev/143A/2017fall/lectures/lecture09-kernel-init/lecture09-kernel-init.pdf](https://www.ics.uci.edu/~aburtsev/143A/2017fall/lectures/lecture09-kernel-init/lecture09-kernel-init.pdf)
              -   [Lecture 7: System boot (238P)](https://www.ics.uci.edu/~aburtsev/238P/lectures/lecture07-system-boot/lecture07-system-boot.pdf) : [https://www.ics.uci.edu/~aburtsev/238P/lectures/lecture07-system-boot/lecture07-system-boot.pdf](https://www.ics.uci.edu/~aburtsev/238P/lectures/lecture07-system-boot/lecture07-system-boot.pdf)
---
-   **xv6 Mandarin article collections**  -   [LuSkyWalter - xv6 based on x86](https://blog.lusw.dev/categories/XV6/)    -   [XV6 - PC Hardware 2018-08-27](https://blog.lusw.dev/posts/xv6/hardware.html)
              -   [XV6 - Memory Page Tables 2018-07-23](https://blog.lusw.dev/posts/xv6/mem.html)
              -   [XV6 - Traps and Drivers 2018-07-30](https://blog.lusw.dev/posts/xv6/trap.html)
              -   [XV6 - OS Organization 2018-07-16](https://blog.lusw.dev/posts/xv6/process.html)
              -   [XV6 - OS Interfaces 2018-07-09](https://blog.lusw.dev/posts/xv6/intro.html)
              -   [XV6 - Running 2018-08-27](https://blog.lusw.dev/posts/xv6/running.html)
              -   [XV6 - The Boot loader 2018-08-27](https://blog.lusw.dev/posts/xv6/bootloader.html)
              -   [XV6 - Starting Process 2018-08-27](https://blog.lusw.dev/posts/xv6/starting.html)
              -   [XV6 - File System 2018-08-23](https://blog.lusw.dev/posts/xv6/fs.html)
              -   [XV6 - Scheduling 2018-08-14](https://blog.lusw.dev/posts/xv6/scheduler.html)
              -   [XV6 - Locking 2018-08-07](https://blog.lusw.dev/posts/xv6/lock.html)
          
      -   [xv6启动源码阅读 - csdn](https://blog.csdn.net/vally1989/article/details/71796482) or [codeantenna link](https://codeantenna.com/a/xcCMl54eeQ) : 最近在学习MIT的6.828操作系统课程，课程地址: [https://pdos.csail.mit.edu/6.828/2016/](https://pdos.csail.mit.edu/6.828/2016/) 。6.828的课程自带了一个简单的基于unix的操作系统。打算写几篇阅读这个操作系统源码的文章。这是第一篇，主要讲解启动时候的主要操作。
      -   [淺談特權模式與模式切換 - xv6 RISC-V](https://ithelp.ithome.com.tw/articles/10279502?sc=hot) : 恐龍書上的 User Mode 與 Kernel Mode. 在恐龍書中有提到，作業系統一般會在 User Mode 與 Kernel Mode 之間切換，Kernel Mode 具有更高的系統控制權且掌管了多數的硬體資源。而 User Mode 通常用於執行 User Application，如果 User Application 呼叫了 System call，系統便會切換到 Kernel Mode 進行處理，並在處理完成後退回 User Mode。恐龍本沒有教的事:特權指令.
      -   [xv6 Trap (user mode): Trace Trap - 2022 iThome 鐵人賽](https://ithelp.ithome.com.tw/m/articles/10302200)
      -   [Google search result - how to judge kernel mode or user mode xv6](https://www.google.com/search?q=how+to+judge+kernel+mode+or+user+mode+xv6&oq=how+to+judge+kernel+mode+or+user+mode+xv6&aqs=edge..69i57.50387j0j1&sourceid=chrome&ie=UTF-8)
---
-   **Youtube collections**  -   [xv6 Kernel by hhp3](https://www.youtube.com/watch?v=fWUJKH0RNFE&list=PLbtzT1TYeoMhTPzyTZboW_j7TPAnjv9XB) : 38 videos
---

[![:arrow_left:](images/arrow_left.png)Previous article - Q&A for Linux](https://hackmd.io/@MarconiJiang/QnA_Linux)  
[![:arrow_right:](images/arrow_right.png)Next article - x86 RISC-C Implementation](https://hackmd.io/@MarconiJiang/xv6-riscv-implementation)  
[![:arrow_up:](images/arrow_up.png)back to marconi's blog](https://marconi1964.github.io/)
