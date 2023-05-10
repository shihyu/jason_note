# 為函數新增enter和exit級trace

日常開發中，我們為了輔助程序偵錯常常在每個函數的出入口(entry/exit)增加Trace，一般我們多用宏來實現這些Trace語句，例如：

```c
#ifdef XX_DEBUG_
#define TRACE_ENTER() printf("Enter %s\n", __FUNCTION__)
#define TRACE_EXIT() printf("Exit %s\n", __FUNCTION__)
#else
#define TRACE_ENTER()
#define TRACE_EXIT()
#endif

// 有了TRACE_ENTER和TRACE_EXIT後，你就可以在你的函數中使用它們了。例如：
void foo(…)
{
    TRACE_ENTER();
    … …
    TRACE_EXIT();
}

```

這樣你就可以很容易看到函數的呼叫關係。不過這種手法用起來卻不輕鬆。首先你需要在每個函數中手工加入TRACE_ENTER和TRACE_EXIT，然後再利用XX_DEBUG_宏控制其是否生效。特別是對於初期未新增函數級Enter/Exit Trace的項目，後期加入工作量很大。

另外一種方便的手法：使用GCC的-finstrument-functions選項。-finstrument-functions使得GCC在生成程式碼時自動為每個函數在入口和出口生成__cyg_profile_func_enter和__cyg_profile_func_exit兩個函數呼叫。我們要做的就是給出一份兩個函數的實現即可。最簡單的實現莫過於列印出被呼叫函數的地址了：

```c
/* func_trace.c */
__attribute__((no_instrument_function))
void __cyg_profile_func_enter(void* this_fn, void* call_site)
{
    printf("enter func => %p\n", this_fn);
}

__attribute__((no_instrument_function))
void __cyg_profile_func_exit(void* this_fn, void* call_site)
{
    printf("exit func <= %p\n", this_fn);
}
```

我們將這兩個函數放入libfunc_trace.so：

```sh
gcc -fPIC -shared -o libfunc_trace.so func_trace.c
```

我們為下面例子新增enter/exit級Trace：

```c
#include <unistd.h>
/* example.c */
static void foo2()
{

}

void foo1()
{
    foo2();
}

void foo()
{
    chdir("/home/tonybai");
    foo1();
}

int main(int argc, const char* argv[])
{
    foo();
    return 0;
}
```

```sh
$ gcc -g example.c -o example -finstrument-functions -no-pie
$ LD_PRELOAD=libfunc_trace.so example
enter func => 0×8048524
enter func => 0x80484e5
enter func => 0x80484b2
enter func => 0×8048484
exit func <= 0×8048484
exit func <= 0x80484b2
exit func <= 0x80484e5
exit func <= 0×8048524
```

不過只輸出函數地址很難讓人滿意，根據這些地址我們無法得知到底對應的是哪個函數。那我們就嘗試一下將地址轉換為函數名後再輸出，這方面GNU依舊給我們提供了工具，它就是addr2line。addr2line是[binutils](http://www.gnu.org/s/binutils)包中的一個工具，它可以根據提供的地址在可執行檔案中找出對應的函數名、對應的原始碼檔案名稱以及行數。我們改造一下func_trace.c中的兩個函數的實現：

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#define PATH_MAX 1024
#define gettid() syscall(SYS_gettid)
#define DUMP(func, call) printf("%s: func = %p, called by = %p/n", __FUNCTION__, func, call)

static char path[PATH_MAX];

__attribute__((constructor))
static void executable_path_init()
{
    char    buf[PATH_MAX];

    memset(buf, 0, sizeof(buf));
    memset(path, 0, sizeof(path));

#ifdef _SOLARIS_TRACE
    getcwd(buf, PATH_MAX);
    sprintf(path, "%s/%s", buf, getexecname());
#elif _LINUX_TRACE
    readlink("/proc/self/exe", path, PATH_MAX);
#else
#endif
}

#ifdef __cplusplus
extern "C" {
#endif
__attribute__((no_instrument_function))
void __cyg_profile_func_enter(void* this_fn, void* call_site)
{
    char buf[PATH_MAX];
    char cmd[PATH_MAX];

    memset(buf, 0, sizeof(buf));
    memset(cmd, 0, sizeof(cmd));

    sprintf(cmd, "addr2line %p -e %s -f|head -1", this_fn, path);
    printf("\n%s\n", cmd);

    FILE* ptr = NULL;
    memset(buf, 0, sizeof(buf));

    if ((ptr = popen(cmd, "r")) != NULL) {
        fgets(buf, PATH_MAX, ptr);
        printf("enter func => %p:%s", this_fn, buf);
    }

    (void) pclose(ptr);
}

__attribute__((no_instrument_function))
void __cyg_profile_func_exit(void* this_fn, void* call_site)
{
    char buf[PATH_MAX];
    char cmd[PATH_MAX];

    memset(buf, 0, sizeof(buf));
    memset(cmd, 0, sizeof(cmd));

    sprintf(cmd, "addr2line %p -e %s -f|head -1", this_fn, path);
    printf("\n%s\n", cmd);

    FILE* ptr = NULL;
    memset(buf, 0, sizeof(buf));

    if ((ptr = popen(cmd, "r")) != NULL) {
        fgets(buf, PATH_MAX, ptr);
        printf("exit func <= %p:%s", this_fn, buf);
    }

    (void) pclose(ptr);
}
#ifdef __cplusplus
}
#endif
```

```sh
gcc -D_LINUX_TRACE -fPIC -shared -o libfunc_trace.so func_trace.c
$ gcc -g example.c -o example -finstrument-functions -no-pie 
$ LD_PRELOAD=./libfunc_trace.so ./example
enter func => 0×8048524:main
enter func => 0x80484e5:foo
enter func => 0x80484b2:foo1
enter func => 0×8048484:foo2
exit func <= 0×8048484:foo2
exit func <= 0x80484b2:foo1
exit func <= 0x80484e5:foo
exit func <= 0×8048524:main
```



關於這個實現，還有幾點要說道說道：
首先libfunc_trace.so是[動態連結](http://tonybai.com/2008/02/03/symbol-linkage-in-shared-library/)到你的可執行程序中的，那麼如何獲取addr2line所需要的檔案名稱是一個問題；另外考慮到可執行程序中可能會呼叫chdir這樣的介面更換當前工作路徑，所以我們需要在初始化時就得到可執行檔案的絕對路徑供addr2line使用，否則會出現無法找到可執行檔案的錯誤。在這裡我們利用了GCC的__attribute__擴展：
__attribute__((constructor))

這樣我們就可以在main之前就將可執行檔案的絕對路徑獲取到，並在__cyg_profile_func_enter和__cyg_profile_func_exit中直接引用這個路徑。

在不同平臺下獲取可執行檔案的絕對路徑的方法有不同，像Linux下可以利用"readlink /proc/self/exe"獲得可執行檔案的絕對路徑，而Solaris下則用getcwd和getexecname拼接。

再總結一下，如果你想使用上面的libfunc_trace.so，你需要做的事情有：
1、將編譯好的libfunc_trace.so放在某路徑下，並export LD_PRELOAD=PATH_TO_libfunc_trace.so/libfunc_trace.so
2、你的環境下需要安裝binutils的addr2line
3、你的應用在編譯時增加-finstrument_functions選項。

我已經將這個小工具包放到了Google Code上，有興趣的朋友可以在[這裡](http://code.google.com/p/bigwhite-code/)下載完整原始碼包（20110715更新：支援輸出函數所在原始檔路徑以及所在行號，前提編譯你的程序時務必加上-g選項）
