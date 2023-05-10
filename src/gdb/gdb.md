# GDB

```sh
sudo apt-get install libgmp-dev libmpfr-dev

git clone https://github.com/bminor/binutils-gdb

../configure --enable-targets=all \
--prefix=/home/shihyu/.mybin/gdb

make -j8 && make
```



---

## 編譯 gdb-7.9 build gdbserver and gdb

建議： 給特定用戶安裝 GDB 的 pretty-printer 打印出可讀性更好的 stdc++ 的 STL 容器 在編譯 GDB 之前，先安裝 ncurses 庫和 Python 庫（用於在 GDB 中 開啟 Python 支持，編譯 GDB 時必須添加 --with-python 選項）。

```sh
sudo apt-get install texinfo libncurses-dev libreadline-dev python-dev
gdb 編譯新版修改  // 因為 gdb 會出現  'g' packet reply is too long:
修改gdb/remote.c文件，屏蔽process_g_packet函數中的下列兩行：
if (buf_len > 2 * rsa->sizeof_g_packet)
error (_(“Remote ‘g’ packet reply is too long: %s”), rs->buf);
在其後添加：
if (buf_len > 2 * rsa->sizeof_g_packet) {
    rsa->sizeof_g_packet = buf_len ;
    for (i = 0; i < gdbarch_num_regs (gdbarch); i++)
    {
        if (rsa->regs[i].pnum == -1)
            continue;

        if (rsa->regs[i].offset >= rsa->sizeof_g_packet)
            rsa->regs[i].in_g_packet = 0;
        else
            rsa->regs[i].in_g_packet = 1;
    }
}
```

#### 找到python可執行程序的位置

```sh
which python

/home/shihyu/anaconda2/bin/python
```

#### 若為 Anaconda，則使用 Anaconda/lib

```sh
設置環境變量

export LDFLAGS="-Wl,-rpath,/home/shihyu/anaconda3/lib -L/home/shihyu/anaconda3/lib"

../configure --enable-targets=all \
             --enable-64-bit-bfd  \
             --with-python=python3.7 \
             --with-system-readline \
             --prefix=/home/shihyu/.mybin/gdb8.3_python3
設置環境變量

export LDFLAGS="-Wl,-rpath,/home/shihyu/anaconda2/lib -L/home/shihyu/anaconda2/lib"

./configure --enable-targets=all \
            --enable-64-bit-bfd \
            --with-python="/home/shihyu/anaconda2/bin/" \
            --with-system-readline \
            --prefix=/home/shihyu/.mybin/gdb_8.1
mkdir build ; cd build

export LDFLAGS="-Wl,-rpath,/home/shihyu/anaconda3/lib -L/home/shihyu/anaconda3/lib"

../configure --enable-targets=all \
             --enable-64-bit-bfd  \
             --with-python=python3.6 \
             --with-system-readline \
             --prefix=/home/shihyu/.mybin/gdb_python3
../configure --enable-targets=all \
             --enable-64-bit-bfd  \
             --with-python=python3 \
             --with-system-readline \
             --prefix=/home/shihyu/.mybin/gdb_python3
./configure --enable-targets=all \
            --enable-64-bit-bfd \
            --with-python \
            --with-system-readline \
            --prefix=/home/shihyu/.mybin/gdb_8.1




# --target=arm-linux表示生成的gdb調試的目標是在arm核心Linux系統中運行的程序
# --enable-targets=all  gdb可以用同一個版本支持x86，ppc等多種體系結構。
# 比較新的bfd中，當設置的target是64位或者打開--enable-targets=all的時候，不需要設置會自動打開這個選項，不過保險起見還是打開。這樣編譯出的GDB就能支持GDB支持的全部體系結構了。
make
sudo make install
```

把[GCC源碼目錄]/libstdc++-v3/python 複製到任意一個目錄（比如 ~/.mybin/gdb_8.1 目錄下）， 如果源碼目錄下沒有上述 python 目錄，也可以用如下方式從遠程庫拉取之後再放到 ~/.mybin/gdb_8.1 目錄下：

```sh
svn co svn://gcc.gnu.org/svn/gcc/trunk/libstdc++-v3/python
```

然後，編輯 ~/.gdbinit，添加如下內容

```sh
python
import sys
import os
p = os.path.expanduser('~/.gdb/python') 
print p
if os.path.exists(p):
    sys.path.insert(0, p)
    from libstdcxx.v6.printers import register_libstdcxx_printers
    register_libstdcxx_printers(None)
end
(gdb) set architecture
Display all 204 possibilities? (y or n)
alpha                          m68k:isa-c:nodiv:mac
alpha:ev4                      m88k:88100
alpha:ev5                      mep
alpha:ev6                      mips
am33                           mips:10000
am33-2                         mips:12000
arm                            mips:16
armv2                          mips:3000
armv2a                         mips:3900
armv3                          mips:4000
armv3m                         mips:4010
armv4                          mips:4100
armv4t                         mips:4111
armv5                          mips:4120
armv5t                         mips:4300
armv5te                        mips:4400
auto                           mips:4600
avr                            mips:4650
avr:1                          mips:5000
avr:2                          mips:5400
avr:3                          mips:5500
avr:4                          mips:6000
avr:5                          mips:7000
avr:6                          mips:8000
cris                           mips:9000
cris:common_v10_v32            mips:isa32
crisv32                        mips:isa32r2
ep9312                         mips:isa64
fr300                          mips:isa64r2
fr400                          mips:loongson_2e
fr450                          mips:loongson_2f
fr500                          mips:mips5
fr550                          mips:octeon
frv                            mips:sb1
h1                             mn10300
h8300                          ms1
h8300h                         ms1-003
h8300hn                        ms2
h8300s                         powerpc:403
h8300sn                        powerpc:601
h8300sx                        powerpc:603
h8300sxn                       powerpc:604
hppa1.0                        powerpc:620
i386                           powerpc:630
i386:intel                     powerpc:7400
i386:x86-64                    powerpc:750
i386:x86-64:intel              powerpc:EC603e
i8086                          powerpc:MPC8XX
ia64-elf32                     powerpc:a35
ia64-elf64                     powerpc:common
iq10                           powerpc:common64
iq2000                         powerpc:e500
iwmmxt                         powerpc:rs64ii
iwmmxt2                        powerpc:rs64iii
m16c                           rs6000:6000
m32c                           rs6000:rs1
m32r                           rs6000:rs2
m32r2                          rs6000:rsc
m32rx                          s390:31-bit
m68hc11                        s390:64-bit
m68hc12                        score
m68k                           sh
m68k:5200                      sh-dsp
m68k:5206e                     sh2
m68k:521x                      sh2a
m68k:5249                      sh2a-nofpu
m68k:528x                      sh2a-nofpu-or-sh3-nommu
m68k:5307                      sh2a-nofpu-or-sh4-nommu-nofpu
m68k:5407                      sh2a-or-sh3e
m68k:547x                      sh2a-or-sh4
m68k:548x                      sh2e
m68k:68000                     sh3
m68k:68008                     sh3-dsp
m68k:68010                     sh3-nommu
m68k:68020                     sh3e
m68k:68030                     sh4
m68k:68040                     sh4-nofpu
m68k:68060                     sh4-nommu-nofpu
m68k:cfv4e                     sh4a
m68k:cpu32                     sh4a-nofpu
m68k:fido                      sh4al-dsp
m68k:isa-a                     sh5
m68k:isa-a:emac                simple
m68k:isa-a:mac                 sparc
m68k:isa-a:nodiv               sparc:sparclet
m68k:isa-aplus                 sparc:sparclite
m68k:isa-aplus:emac            sparc:sparclite_le
m68k:isa-aplus:mac             sparc:v8plus
m68k:isa-b                     sparc:v8plusa
m68k:isa-b:emac                sparc:v8plusb
m68k:isa-b:float               sparc:v9
m68k:isa-b:float:emac          sparc:v9a
m68k:isa-b:float:mac           sparc:v9b
m68k:isa-b:mac                 spu:256K
m68k:isa-b:nousp               tomcat
m68k:isa-b:nousp:emac          v850
m68k:isa-b:nousp:mac           v850e
m68k:isa-c                     v850e1
m68k:isa-c:emac                vax
m68k:isa-c:mac                 xscale
m68k:isa-c:nodiv               xstormy16
m68k:isa-c:nodiv:emac          xtensa
set architecture arm:指定arm硬體
```

- Toolchain 無法使用 android 的 arm 編譯器目前原因不清楚

```
https://launchpad.net/linaro-toolchain-binaries/trunk/2013.10/+download/gcc-linaro-arm-linux-gnueabihf-4.8-2013.10_linux.tar.bz2
```

- build.env

```
# -*- shell-script -*-
TOOLCHAIN=gcc-linaro-arm-linux-gnueabihf-4.8-2013.10_linux
DIR=$(pushd $(dirname $BASH_SOURCE) > /dev/null; pwd; popd > /dev/null)
echo $DIR
export PATH=${PATH}:${DIR}/${TOOLCHAIN}/bin
export CC=arm-linux-gnueabihf-gcc
```

## gdbserver , 要注意gdb和gdbserver版本一致

```
source build.env
./configure --target=arm-linux --host=arm-linux LDFLAGS="-static"
# 這裡的--host指定這個程序的目標平臺。這一步中會檢查系統中是否有交叉編譯器的。
# We must add the above LDFLAGS to let gdb statically linked, otherwise it cannot
run on Android.

time make -j8 2>&1 | tee build.log
file ./gdbserver

./gdbserver: ELF 32-bit LSB  executable, ARM, EABI5 version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 3.1.1, BuildID[sha1]=4eec8a5a6893ed8ce65eea5d0741a55cc621236a, not stripped
```

------

## cgdb

安裝 cgdb

cgdb 是一個開源的 gdb 前端，可以提供實時的代碼預覽，極大的方便了調試。

獲取源碼

```sh
$ git clone git://github.com/cgdb/cgdb.git
```

依賴

```sh
flex( gettext )，autoconf, aclocal, automake, help2man
```

安裝依賴 （1） flex

```sh
$ sudo apt-get install flex
```

（2） aclocal, automake, autoconf, autoheader 這些 utilities 都在 automake 包中，因此安裝automake 就夠了。

```sh
$ sudo apt-get install automake
$ sudo apt-get install autotools-dev
```

(3) makeinfo，這個 utility 在 texinfo 包中

```sh
$ sudo apt-get install texinfo
```

（3）help2man

```sh
$ sudo apt-get install help2man
```

## 編譯和安裝

```sh
$ cd cgdb
$ ./autogen.sh
$ ./configure --prefix=/usr/local
$ make
$ sudo make install
```

------

- ~/.gdbinit

```sh
#    ``                                                                                                    
#   STL GDB evaluators/views/utilities - 1.03
#
#   The new GDB commands:                                                         
#         are entirely non instrumental                                             
#         do not depend on any "inline"(s) - e.g. size(), [], etc
#       are extremely tolerant to debugger settings
#                                                                                 
#   This file should be "included" in .gdbinit as following:
#   source stl-views.gdb or just paste it into your .gdbinit file
#
#   The following STL containers are currently supported:
#
#       std::vector<T> -- via pvector command
#       std::list<T> -- via plist or plist_member command
#       std::map<T,T> -- via pmap or pmap_member command
#       std::multimap<T,T> -- via pmap or pmap_member command
#       std::set<T> -- via pset command
#       std::multiset<T> -- via pset command
#       std::deque<T> -- via pdequeue command
#       std::stack<T> -- via pstack command
#       std::queue<T> -- via pqueue command
#       std::priority_queue<T> -- via ppqueue command
#       std::bitset<n> -- via pbitset command
#       std::string -- via pstring command
#       std::widestring -- via pwstring command
#
#   The end of this file contains (optional) C++ beautifiers
#   Make sure your debugger supports $argc
#
#   Simple GDB Macros writen by Dan Marinescu (H-PhD) - License GPL
#   Inspired by intial work of Tom Malnar, 
#     Tony Novac (PhD) / Cornell / Stanford,
#     Gilad Mishne (PhD) and Many Many Others.
#   Contact: dan_c_marinescu@yahoo.com (Subject: STL)
#
#   Modified to work with g++ 4.3 by Anders Elton
#   Also added _member functions, that instead of printing the entire class in map, prints a member.



#
# std::vector<>
#

define pvector
    if $argc == 0
        help pvector
    else
        set $size = $arg0._M_impl._M_finish - $arg0._M_impl._M_start
        set $capacity = $arg0._M_impl._M_end_of_storage - $arg0._M_impl._M_start
        set $size_max = $size - 1
    end
    if $argc == 1
        set $i = 0
        while $i < $size
            printf "elem[%u]: ", $i
            p *($arg0._M_impl._M_start + $i)
            set $i++
        end
    end
    if $argc == 2
        set $idx = $arg1
        if $idx < 0 || $idx > $size_max
            printf "idx1, idx2 are not in acceptable range: [0..%u].\n", $size_max
        else
            printf "elem[%u]: ", $idx
            p *($arg0._M_impl._M_start + $idx)
        end
    end
    if $argc == 3
      set $start_idx = $arg1
      set $stop_idx = $arg2
      if $start_idx > $stop_idx
        set $tmp_idx = $start_idx
        set $start_idx = $stop_idx
        set $stop_idx = $tmp_idx
      end
      if $start_idx < 0 || $stop_idx < 0 || $start_idx > $size_max || $stop_idx > $size_max
        printf "idx1, idx2 are not in acceptable range: [0..%u].\n", $size_max
      else
        set $i = $start_idx
        while $i <= $stop_idx
            printf "elem[%u]: ", $i
            p *($arg0._M_impl._M_start + $i)
            set $i++
        end
      end
    end
    if $argc > 0
        printf "Vector size = %u\n", $size
        printf "Vector capacity = %u\n", $capacity
        printf "Element "
        whatis $arg0._M_impl._M_start
    end
end

document pvector
    Prints std::vector<T> information.
    Syntax: pvector <vector> <idx1> <idx2>
    Note: idx, idx1 and idx2 must be in acceptable range [0..<vector>.size()-1].
    Examples:
    pvector v - Prints vector content, size, capacity and T typedef
    pvector v 0 - Prints element[idx] from vector
    pvector v 1 2 - Prints elements in range [idx1..idx2] from vector
end 

#
# std::list<>
#

define plist
    if $argc == 0
        help plist
    else
        set $head = &$arg0._M_impl._M_node
        set $current = $arg0._M_impl._M_node._M_next
        set $size = 0
        while $current != $head
            if $argc == 2
                printf "elem[%u]: ", $size
                p *($arg1*)($current + 1)
            end
            if $argc == 3
                if $size == $arg2
                    printf "elem[%u]: ", $size
                    p *($arg1*)($current + 1)
                end
            end
            set $current = $current._M_next
            set $size++
        end
        printf "List size = %u \n", $size
        if $argc == 1
            printf "List "
            whatis $arg0
            printf "Use plist <variable_name> <element_type> to see the elements in the list.\n"
        end
    end
end

document plist
    Prints std::list<T> information.
    Syntax: plist <list> <T> <idx>: Prints list size, if T defined all elements or just element at idx
    Examples:
    plist l - prints list size and definition
    plist l int - prints all elements and list size
    plist l int 2 - prints the third element in the list (if exists) and list size
end

define plist_member
    if $argc == 0
        help plist_member
    else
        set $head = &$arg0._M_impl._M_node
        set $current = $arg0._M_impl._M_node._M_next
        set $size = 0
        while $current != $head
            if $argc == 3
                printf "elem[%u]: ", $size
                p (*($arg1*)($current + 1)).$arg2
            end
            if $argc == 4
                if $size == $arg3
                    printf "elem[%u]: ", $size
                    p (*($arg1*)($current + 1)).$arg2
                end
            end
            set $current = $current._M_next
            set $size++
        end
        printf "List size = %u \n", $size
        if $argc == 1
            printf "List "
            whatis $arg0
            printf "Use plist_member <variable_name> <element_type> <member> to see the elements in the list.\n"
        end
    end
end

document plist_member
    Prints std::list<T> information.
    Syntax: plist <list> <T> <idx>: Prints list size, if T defined all elements or just element at idx
    Examples:
    plist_member l int member - prints all elements and list size
    plist_member l int member 2 - prints the third element in the list (if exists) and list size
end


#
# std::map and std::multimap
#

define pmap
    if $argc == 0
        help pmap
    else
        set $tree = $arg0
        set $i = 0
        set $node = $tree._M_t._M_impl._M_header._M_left
        set $end = $tree._M_t._M_impl._M_header
        set $tree_size = $tree._M_t._M_impl._M_node_count
        if $argc == 1
            printf "Map "
            whatis $tree
            printf "Use pmap <variable_name> <left_element_type> <right_element_type> to see the elements in the map.\n"
        end
        if $argc == 3
            while $i < $tree_size
                set $value = (void *)($node + 1)
                printf "elem[%u].left: ", $i
                p *($arg1*)$value
                set $value = $value + sizeof($arg1)
                printf "elem[%u].right: ", $i
                p *($arg2*)$value
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
        end
        if $argc == 4
            set $idx = $arg3
            set $ElementsFound = 0
            while $i < $tree_size
                set $value = (void *)($node + 1)
                if *($arg1*)$value == $idx
                    printf "elem[%u].left: ", $i
                    p *($arg1*)$value
                    set $value = $value + sizeof($arg1)
                    printf "elem[%u].right: ", $i
                    p *($arg2*)$value
                    set $ElementsFound++
                end
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
            printf "Number of elements found = %u\n", $ElementsFound
        end
        if $argc == 5
            set $idx1 = $arg3
            set $idx2 = $arg4
            set $ElementsFound = 0
            while $i < $tree_size
                set $value = (void *)($node + 1)
                set $valueLeft = *($arg1*)$value
                set $valueRight = *($arg2*)($value + sizeof($arg1))
                if $valueLeft == $idx1 && $valueRight == $idx2
                    printf "elem[%u].left: ", $i
                    p $valueLeft
                    printf "elem[%u].right: ", $i
                    p $valueRight
                    set $ElementsFound++
                end
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
            printf "Number of elements found = %u\n", $ElementsFound
        end
        printf "Map size = %u\n", $tree_size
    end
end

document pmap
    Prints std::map<TLeft and TRight> or std::multimap<TLeft and TRight> information. Works for std::multimap as well.
    Syntax: pmap <map> <TtypeLeft> <TypeRight> <valLeft> <valRight>: Prints map size, if T defined all elements or just element(s) with val(s)
    Examples:
    pmap m - prints map size and definition
    pmap m int int - prints all elements and map size
    pmap m int int 20 - prints the element(s) with left-value = 20 (if any) and map size
    pmap m int int 20 200 - prints the element(s) with left-value = 20 and right-value = 200 (if any) and map size
end


define pmap_member
    if $argc == 0
        help pmap_member
    else
        set $tree = $arg0
        set $i = 0
        set $node = $tree._M_t._M_impl._M_header._M_left
        set $end = $tree._M_t._M_impl._M_header
        set $tree_size = $tree._M_t._M_impl._M_node_count
        if $argc == 1
            printf "Map "
            whatis $tree
            printf "Use pmap <variable_name> <left_element_type> <right_element_type> to see the elements in the map.\n"
        end
        if $argc == 5
            while $i < $tree_size
                set $value = (void *)($node + 1)
                printf "elem[%u].left: ", $i
                p (*($arg1*)$value).$arg2
                set $value = $value + sizeof($arg1)
                printf "elem[%u].right: ", $i
                p (*($arg3*)$value).$arg4
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
        end
        if $argc == 6
            set $idx = $arg5
            set $ElementsFound = 0
            while $i < $tree_size
                set $value = (void *)($node + 1)
                if *($arg1*)$value == $idx
                    printf "elem[%u].left: ", $i
                    p (*($arg1*)$value).$arg2
                    set $value = $value + sizeof($arg1)
                    printf "elem[%u].right: ", $i
                    p (*($arg3*)$value).$arg4
                    set $ElementsFound++
                end
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
            printf "Number of elements found = %u\n", $ElementsFound
        end
        printf "Map size = %u\n", $tree_size
    end
end

document pmap_member
    Prints std::map<TLeft and TRight> or std::multimap<TLeft and TRight> information. Works for std::multimap as well.
    Syntax: pmap <map> <TtypeLeft> <TypeRight> <valLeft> <valRight>: Prints map size, if T defined all elements or just element(s) with val(s)
    Examples:
    pmap_member m class1 member1 class2 member2 - prints class1.member1 : class2.member2
    pmap_member m class1 member1 class2 member2 lvalue - prints class1.member1 : class2.member2 where class1 == lvalue
end


#
# std::set and std::multiset
#

define pset
    if $argc == 0
        help pset
    else
        set $tree = $arg0
        set $i = 0
        set $node = $tree._M_t._M_impl._M_header._M_left
        set $end = $tree._M_t._M_impl._M_header
        set $tree_size = $tree._M_t._M_impl._M_node_count
        if $argc == 1
            printf "Set "
            whatis $tree
            printf "Use pset <variable_name> <element_type> to see the elements in the set.\n"
        end
        if $argc == 2
            while $i < $tree_size
                set $value = (void *)($node + 1)
                printf "elem[%u]: ", $i
                p *($arg1*)$value
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
        end
        if $argc == 3
            set $idx = $arg2
            set $ElementsFound = 0
            while $i < $tree_size
                set $value = (void *)($node + 1)
                if *($arg1*)$value == $idx
                    printf "elem[%u]: ", $i
                    p *($arg1*)$value
                    set $ElementsFound++
                end
                if $node._M_right != 0
                    set $node = $node._M_right
                    while $node._M_left != 0
                        set $node = $node._M_left
                    end
                else
                    set $tmp_node = $node._M_parent
                    while $node == $tmp_node._M_right
                        set $node = $tmp_node
                        set $tmp_node = $tmp_node._M_parent
                    end
                    if $node._M_right != $tmp_node
                        set $node = $tmp_node
                    end
                end
                set $i++
            end
            printf "Number of elements found = %u\n", $ElementsFound
        end
        printf "Set size = %u\n", $tree_size
    end
end

document pset
    Prints std::set<T> or std::multiset<T> information. Works for std::multiset as well.
    Syntax: pset <set> <T> <val>: Prints set size, if T defined all elements or just element(s) having val
    Examples:
    pset s - prints set size and definition
    pset s int - prints all elements and the size of s
    pset s int 20 - prints the element(s) with value = 20 (if any) and the size of s
end



#
# std::dequeue
#

define pdequeue
    if $argc == 0
        help pdequeue
    else
        set $size = 0
        set $start_cur = $arg0._M_impl._M_start._M_cur
        set $start_last = $arg0._M_impl._M_start._M_last
        set $start_stop = $start_last
        while $start_cur != $start_stop
            p *$start_cur
            set $start_cur++
            set $size++
        end
        set $finish_first = $arg0._M_impl._M_finish._M_first
        set $finish_cur = $arg0._M_impl._M_finish._M_cur
        set $finish_last = $arg0._M_impl._M_finish._M_last
        if $finish_cur < $finish_last
            set $finish_stop = $finish_cur
        else
            set $finish_stop = $finish_last
        end
        while $finish_first != $finish_stop
            p *$finish_first
            set $finish_first++
            set $size++
        end
        printf "Dequeue size = %u\n", $size
    end
end

document pdequeue
    Prints std::dequeue<T> information.
    Syntax: pdequeue <dequeue>: Prints dequeue size, if T defined all elements
    Deque elements are listed "left to right" (left-most stands for front and right-most stands for back)
    Example:
    pdequeue d - prints all elements and size of d
end



#
# std::stack
#

define pstack
    if $argc == 0
        help pstack
    else
        set $start_cur = $arg0.c._M_impl._M_start._M_cur
        set $finish_cur = $arg0.c._M_impl._M_finish._M_cur
        set $size = $finish_cur - $start_cur
        set $i = $size - 1
        while $i >= 0
            p *($start_cur + $i)
            set $i--
        end
        printf "Stack size = %u\n", $size
    end
end

document pstack
    Prints std::stack<T> information.
    Syntax: pstack <stack>: Prints all elements and size of the stack
    Stack elements are listed "top to buttom" (top-most element is the first to come on pop)
    Example:
    pstack s - prints all elements and the size of s
end



#
# std::queue
#

define pqueue
    if $argc == 0
        help pqueue
    else
        set $start_cur = $arg0.c._M_impl._M_start._M_cur
        set $finish_cur = $arg0.c._M_impl._M_finish._M_cur
        set $size = $finish_cur - $start_cur
        set $i = 0
        while $i < $size
            p *($start_cur + $i)
            set $i++
        end
        printf "Queue size = %u\n", $size
    end
end

document pqueue
    Prints std::queue<T> information.
    Syntax: pqueue <queue>: Prints all elements and the size of the queue
    Queue elements are listed "top to bottom" (top-most element is the first to come on pop)
    Example:
    pqueue q - prints all elements and the size of q
end



#
# std::priority_queue
#

define ppqueue
    if $argc == 0
        help ppqueue
    else
        set $size = $arg0.c._M_impl._M_finish - $arg0.c._M_impl._M_start
        set $capacity = $arg0.c._M_impl._M_end_of_storage - $arg0.c._M_impl._M_start
        set $i = $size - 1
        while $i >= 0
            p *($arg0.c._M_impl._M_start + $i)
            set $i--
        end
        printf "Priority queue size = %u\n", $size
        printf "Priority queue capacity = %u\n", $capacity
    end
end

document ppqueue
    Prints std::priority_queue<T> information.
    Syntax: ppqueue <priority_queue>: Prints all elements, size and capacity of the priority_queue
    Priority_queue elements are listed "top to buttom" (top-most element is the first to come on pop)
    Example:
    ppqueue pq - prints all elements, size and capacity of pq
end



#
# std::bitset
#

define pbitset
    if $argc == 0
        help pbitset
    else
        p /t $arg0._M_w
    end
end

document pbitset
    Prints std::bitset<n> information.
    Syntax: pbitset <bitset>: Prints all bits in bitset
    Example:
    pbitset b - prints all bits in b
end



#
# std::string
#

define pstring
    if $argc == 0
        help pstring
    else
        printf "String \t\t\t= \"%s\"\n", $arg0._M_data()
        printf "String size/length \t= %u\n", $arg0._M_rep()._M_length
        printf "String capacity \t= %u\n", $arg0._M_rep()._M_capacity
        printf "String ref-count \t= %d\n", $arg0._M_rep()._M_refcount
    end
end

document pstring
    Prints std::string information.
    Syntax: pstring <string>
    Example:
    pstring s - Prints content, size/length, capacity and ref-count of string s
end 

#
# std::wstring
#

define pwstring
    if $argc == 0
        help pwstring
    else
        call printf("WString \t\t= \"%ls\"\n", $arg0._M_data())
        printf "WString size/length \t= %u\n", $arg0._M_rep()._M_length
        printf "WString capacity \t= %u\n", $arg0._M_rep()._M_capacity
        printf "WString ref-count \t= %d\n", $arg0._M_rep()._M_refcount
    end
end

document pwstring
    Prints std::wstring information.
    Syntax: pwstring <wstring>
    Example:
    pwstring s - Prints content, size/length, capacity and ref-count of wstring s
end 

#
# C++ related beautifiers (optional)
#

set height 0
set history size 10000
set history filename ~/.gdb_history
set history save on

#退出時不顯示提示信息
set confirm off

#按照派生類型打印對象
set print object on

#打印數組的索引下標
set print array-indexes on

#每行打印一個結構體成員
set print pretty on

set print union on

set print address on 

set print static-members on
set print vtbl on
set print demangle on
set demangle-style gnu-v3
set print sevenbit-strings off
set step-mode on

shell rm -f ./gdb.log
set logging off
set logging file ./gdb.log
set logging on

python
import sys
import os
p = os.path.expanduser('/home/shihyu/.mybin/gdb_8.1/python') 
print(p)
if os.path.exists(p):
    sys.path.insert(0, p)
    from libstdcxx.v6.printers import register_libstdcxx_printers
    register_libstdcxx_printers(None)
end
```



## 100個gdb小技巧

- https://github.com/hellogcc/100-gdb-tips