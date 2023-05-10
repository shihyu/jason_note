## jemalloc源碼分析之分析工具



### 簡介

jemalloc同malloc一樣, 是一種內存管理的實現.

如果使用gcc編譯軟件, 默認使用的是glic實現的ptmalloc算法. 而同樣的算法有google的C++實現tcmalloc算法, 而今天我們分析的是facebook使用C語言實現的jemalloc算法.

tcmalloc同jemalloc一樣都是對多線程多核友好的分配算法, 被各種語言借鑑來實現自身的內存管理.

### 實現原理

如果使用C語言進行內存分配, 我們會調用malloc函數, 而jemalloc就是通過malloc的hook機制實現的.

[如何實現自定義的malloc函數](http://stackoverflow.com/questions/262439/create-a-wrapper-function-for-malloc-and-free-in-c) 這篇文章有介紹如何覆蓋或重寫默認的malloc函數.

[GNU基於hook機制實現自定義的的malloc函數](http://www.gnu.org/savannah-checkouts/gnu/libc/manual/html_node/Hooks-for-Malloc.html), 具體就是通過覆蓋__malloc_hook 函數指標來實現的.

在jemalloc中我們能找到類似的代碼:

jemalloc.c:1830

```c
/*
 * Begin non-standard override functions.
 */

#ifdef JEMALLOC_OVERRIDE_MEMALIGN
JEMALLOC_EXPORT JEMALLOC_ALLOCATOR JEMALLOC_RESTRICT_RETURN
void JEMALLOC_NOTHROW*
JEMALLOC_ATTR(malloc)
je_memalign(size_t alignment, size_t size)
{
    void* ret JEMALLOC_CC_SILENCE_INIT(NULL);

    if (unlikely(imemalign(&ret, alignment, size, 1) != 0)) {
        ret = NULL;
    }

    return (ret);
}
#endif

#ifdef JEMALLOC_OVERRIDE_VALLOC
JEMALLOC_EXPORT JEMALLOC_ALLOCATOR JEMALLOC_RESTRICT_RETURN
void JEMALLOC_NOTHROW*
JEMALLOC_ATTR(malloc)
je_valloc(size_t size)
{
    void* ret JEMALLOC_CC_SILENCE_INIT(NULL);

    if (unlikely(imemalign(&ret, PAGE, size, 1) != 0)) {
        ret = NULL;
    }

    return (ret);
}
#endif

/*
 * is_malloc(je_malloc) is some macro magic to detect if jemalloc_defs.h has
 * #define je_malloc malloc
 */
#define malloc_is_malloc 1
#define is_malloc_(a) malloc_is_ ## a
#define is_malloc(a) is_malloc_(a)

#if ((is_malloc(je_malloc) == 1) && defined(JEMALLOC_GLIBC_MALLOC_HOOK))
/*
 * glibc provides the RTLD_DEEPBIND flag for dlopen which can make it possible
 * to inconsistently reference libc's malloc(3)-compatible functions
 * (https://bugzilla.mozilla.org/show_bug.cgi?id=493541).
 *
 * These definitions interpose hooks in glibc.  The functions are actually
 * passed an extra argument for the caller return address, which will be
 * ignored.
 */
JEMALLOC_EXPORT void (*__free_hook)(void* ptr) = je_free;
JEMALLOC_EXPORT void* (*__malloc_hook)(size_t size) = je_malloc;
JEMALLOC_EXPORT void* (*__realloc_hook)(void* ptr, size_t size) = je_realloc;
# ifdef JEMALLOC_GLIBC_MEMALIGN_HOOK
JEMALLOC_EXPORT void* (*__memalign_hook)(size_t alignment, size_t size) =
    je_memalign;
# endif
#endif

/*
 * End non-standard override functions.
 */
```

如果我們在自己的函數調用malloc就會被je_malloc攔截. 例如下面的例子:

```c
int main()
{
    void* ptr = malloc(10);
    free(ptr);
    return 0;
}
```

整個過程是

```
-> main
-> malloc -> je_malloc(mmap等系統調用分配內存) -> malloc結束
-> free -> jeje_free(munmap等系統調用釋放內存) -> free結束
-> main結束
```

上面是當我們程序調用malloc函數時執行的過程, 實際上在jemalloc載入的時候, 就已經進行了一些初始化操作.

具體是在jemalloc_constructor函數.

jemalloc.c:2576

```c
#ifndef JEMALLOC_JET
JEMALLOC_ATTR(constructor)
static void
jemalloc_constructor(void)
{

    malloc_init();
}
#endif

jemalloc_macros.h.in:67
#  define JEMALLOC_ATTR(s) __attribute__((s))
```

通過這篇文章 [如何在共享庫載入時進行初始化操作](http://stackoverflow.com/questions/1681145/how-to-initialize-a-shared-library-on-linux) 知道這是gcc的一個特性.

後面我們將結合"call graph"調用圖分別分析這兩個過程.

### 開始調試

這節主要介紹下載編譯jemalloc, 編寫測試代碼, 使用callgrind生成調用圖, 使用gdb調試jemalloc.

jemalloc當前託管在github上

```
git clone git@github.com:jemalloc/jemalloc.git
./autogen.sh
./configure --enable-debug
make dist
make
make install
```

然後使用ide添加jemalloc項目, 主要作用是方便查看源代碼, 在gdb中查看源代碼實在不太方便, 而且gdb-tui雖然提供了可視化界面, 但是偶爾會出現花屏的情況.

這中間可能因為doc文檔找不到的原因安裝失敗, 根據[issue231](https://github.com/jemalloc/jemalloc/issues/231), 將最後兩步換成

```
make && make install_bin install_include install_lib
```

即可.

然後編寫我們的調試代碼:

a.c文件:

```c
#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>

int func_long_name_a();
int func_long_name_b();
int func_long_name_c();

int func_long_name_a()
{
    printf("func_long_name_a called\n");
    func_long_name_b();
    return 0;
}

int func_long_name_b()
{
    printf("func_long_name_b called\n");
    func_long_name_c();
    return 0;
}

int func_long_name_c()
{
    printf("func_long_name_c called\n");
    int sizeArr[] = {1, 4095, 4096, 8192, 8193, 4 * 1024 * 1024, 10 * 1024 * 1024};
    int i;

    for (i = 0; i < 7; ++i) {
        void* p = malloc(sizeArr[i]);
        free(p);
    }

    return 0;
}

int main(int argc, char** argv)
{
    printf("main called\n");
    func_long_name_a();
    func_long_name_c();
    printf("main exit\n");
    return 0;
}
```

然後編寫一個腳本來實現編譯及調用圖的生成

gen.sh文件

```shell
#!/bin/bash

JEMALLOC_PATH=/home/shihyu/github/jemalloc
gcc -g -ljemalloc -o a -I${JEMALLOC_PATH}/include -L${JEMALLOC_PATH}/lib a.c
valgrind --tool=callgrind ./a
gprof2dot -f callgrind -n 0 callgrind.out.* | dot -Tsvg -o a.svg
date=`date '+%Y%m%d%H%i%s'`
mv a.svg "$(date '+%Y-%m-%d_%H:%M:%S').svg"
#rm -f callgrind.out.* .DS_Store a a.out
rm -f callgrind.out.* .DS_Store a.out
echo
ls -al .
```

中間需要安裝一些特別的軟件, 比如valgrind, gprof2dot, dot等, 這些都可以在網上找到相應的安裝方法.

最後生成我們的[jemalloc_call_graph.svg](https://yaoguais.github.io/images/jemalloc_call_graph.svg)調用圖文件.

在gen.sh中我們並沒有刪除可執行文件"a", 下面我就使用gdb來調試該文件.

```gdb
# gdb a
# b jemalloc_constructor
# b src/jemalloc.c:1443
# b src/jemalloc.c:1811
# r
```

其中jemalloc_constructor是jemalloc共享庫載入時的入口.

src/jemalloc.c:1443是je_malloc函數實現的地方.

src/jemalloc.c:1811是je_free函數實現的地方.

可根據自己的jemalloc版本找到兩個函數的行數做出調整.

執行r後, gdb就停在了jemalloc_constructor函數處.

關於gdb的使用, 也很多, 這裡也有[關於gdb可視化界面gdb-tui的使用](http://mingxinglai.com/cn/2013/07/gdbtui/).

其中在tui模式和傳統模式切換的快捷鍵是ctrl+x接ctrl+a.

### 總結

這篇文章主要介紹瞭如何調試jemalloc, 是分析jemalloc的準備工作, 也是分析其他開源c程序的普遍方法.

首先使用valgrind+dot打印函數調用圖, 找到函數執行的流程. 然後分析基礎的數據結構與其附屬的操作, 快速明白各種變量會有怎樣的轉換. 最後順著調用圖, 分析各個函數的實現, 以及各種結構體之間的關系. 至此, 所有的源代碼幾乎查看完畢, 一個軟件也分析完畢.



---

## 使用jemalloc來對c，c++程序進行內存管理



```sh
git clone https://github.com/jemalloc/jemalloc

cd jemalloc

注意：這一步確定要把jemalloc的函數編譯成哪種形式，比如下面的配置就會把分配內存的函數編譯成je_malloc的形式，把calloc編譯成je_calloc等等。這樣就不會和系統的libc的分配函數malloc沖突，因為若不指定該選項默認編譯的分配函數是malloc。

 ./configure --enable-debug --with-jemalloc-prefix=je_

make -j8
```

## 使用jemalloc

```sh
mkdir jem_test
```

```c
#include <stdio.h>
#include <jemalloc/jemalloc.h>
//define to jemalloc
#define malloc(size) je_malloc(size)
#define calloc(count,size) je_calloc(count,size)
#define realloc(ptr,size) je_realloc(ptr,size)
#define free(ptr) je_free(ptr)

int main(void)
{
    char* pcon;

    pcon = malloc(10 * sizeof(char));

    if (!pcon) {
        fprintf(stderr, "malloc failed!\n");
    }

    if (pcon != NULL) {
        free(pcon);
        pcon = NULL;
    }

    fprintf(stderr, "main end!\n");
    return 0;
}
```

```makefile
CC=gcc
CFLAGS=-Wall -g
INCLUDES=-I /home/shihyu/github/jemalloc/include
ALLOC_DEP=/home/shihyu/github/jemalloc/lib/libjemalloc.a
ALLOC_LINK=$(ALLOC_DEP) -lpthread -ldl

dtest: dtest.o
	$(CC) $(INCLUDES) $(CFLAGS) -o dtest dtest.o $(ALLOC_LINK)

dtest.o: dtest.c $(ALLOC_DEP)
	$(CC) -c $(INCLUDES) $(CFLAGS) dtest.c

clean:
	rm -f dtest dtest.o
```

```sh
cgdb dtest 
b je_malloc
r
```

http://www.web-lovers.com/c-jemalloc-address-problem.html