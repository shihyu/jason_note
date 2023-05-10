

# 5.7 線程崩潰了，進程也會崩潰嗎？

> 來源：公眾號@碼海
>
> 原文地址：[美團一面：線程崩潰了，進程也會崩潰嗎？](https://mp.weixin.qq.com/s/easnVQ75Rq-C07W4YWeclQ)

大家好，我是小林。

之前分享這篇文章的時候：[進程和線程基礎知識全家桶，30 張圖一套帶走](https://xiaolincoding.com/os/4_process/process_base.html)，提到說線程的一個缺點：

![](https://img-blog.csdnimg.cn/899ce21f16244826a7e2fb899484b348.png)

很多同學就好奇，**為什麼 C/C++ 語言裡，線程崩潰後，進程也會崩潰，而 Java 語言裡卻不會呢？**

剛好看到朋友（[公眾號：碼海](https://mp.weixin.qq.com/s/JnlTdUk8Jvao8L6FAtKqhQ)）寫了一篇：「**美團面試題：為什麼線程崩潰崩潰不會導致 JVM 崩潰?**」

我覺得寫的很好，所以分享給大家一起拜讀拜讀，本文分以下幾節來探討：

1. 線程崩潰，進程一定會崩潰嗎
2. 進程是如何崩潰的-信號機制簡介
3. 為什麼在 JVM 中線程崩潰不會導致 JVM 進程崩潰
4. openJDK 源碼解析

## 線程崩潰，進程一定會崩潰嗎

一般來說如果線程是因為非法訪問內存引起的崩潰，那麼進程肯定會崩潰，為什麼系統要讓進程崩潰呢，這主要是因為在進程中，**各個線程的地址空間是共享的**，既然是共享，那麼某個線程對地址的非法訪問就會導致內存的不確定性，進而可能會影響到其他線程，這種操作是危險的，操作系統會認為這很可能導致一系列嚴重的後果，於是乾脆讓整個進程崩潰

![](https://img-blog.csdnimg.cn/17be94f342ea4e49a227b195845880fd.png)


線程共享代碼段，數據段，地址空間，文件非法訪問內存有以下幾種情況，我們以 C 語言舉例來看看。

1.、針對只讀內存寫入數據

```c
   #include <stdio.h>
   #include <stdlib.h>
   
   int main() {
      char *s = "hello world";
      // 向只讀內存寫入數據，崩潰
      s[1] = 'H'; 
   }
```

2、訪問了進程沒有權限訪問的地址空間（比如內核空間）

```c
   #include <stdio.h>
   #include <stdlib.h>

   int main() {
      int *p = (int *)0xC0000fff;
      // 針對進程的內核空間寫入數據，崩潰
      *p = 10; 
   }
```

在 32 位虛擬地址空間中，p 指向的是內核空間，顯然不具有寫入權限，所以上述賦值操作會導致崩潰

3、訪問了不存在的內存，比如：

```c
   #include <stdio.h>
   #include <stdlib.h>
   
   int main() {
      int *a = NULL;
      *a = 1;     
   }
```

以上錯誤都是訪問內存時的錯誤，所以統一會報 Segment Fault 錯誤（即段錯誤），這些都會導致進程崩潰

## 進程是如何崩潰的-信號機制簡介

那麼線程崩潰後，進程是如何崩潰的呢，這背後的機制到底是怎樣的，答案是**信號**。

大家想想要幹掉一個正在運行的進程是不是經常用 kill -9 pid 這樣的命令，這裡的 kill 其實就是給指定 pid 發送終止信號的意思，其中的 9 就是信號。

其實信號有很多類型的，在 Linux 中可以通過 `kill -l`查看所有可用的信號：

![](https://img-blog.csdnimg.cn/eba4dce5e59442b8b2b24d9e171bab0d.png)


當然了發 kill 信號必須具有一定的權限，否則任意進程都可以通過發信號來終止其他進程，那顯然是不合理的，實際上 kill 執行的是系統調用，將控制權轉移給了內核（操作系統），由內核來給指定的進程發送信號

那麼發個信號進程怎麼就崩潰了呢，這背後的原理到底是怎樣的？

其背後的機制如下

1. CPU 執行正常的進程指令
2. 調用 kill 系統調用向進程發送信號
3. 進程收到操作系統發的信號，CPU 暫停當前程序運行，並將控制權轉交給操作系統
4. 調用 kill 系統調用向進程發送信號（假設為 11，即 SIGSEGV，一般非法訪問內存報的都是這個錯誤）
5. **操作系統根據情況執行相應的信號處理程序（函數），一般執行完信號處理程序邏輯後會讓進程退出**

注意上面的第五步，如果進程沒有註冊自己的信號處理函數，那麼操作系統會執行默認的信號處理程序（一般最後會讓進程退出），但如果註冊了，則會執行自己的信號處理函數，這樣的話就給了進程一個垂死掙扎的機會，它收到 kill 信號後，可以調用 exit() 來退出，**但也可以使用 sigsetjmp，siglongjmp 這兩個函數來恢復進程的執行**

```c
// 自定義信號處理函數示例

#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
// 自定義信號處理函數，處理自定義邏輯後再調用 exit 退出
void sigHandler(int sig) {
  printf("Signal %d catched!\n", sig);
  exit(sig);
}
int main(void) {
  signal(SIGSEGV, sigHandler);
  int *p = (int *)0xC0000fff;
  *p = 10; // 針對不屬於進程的內核空間寫入數據，崩潰
}

// 以上結果輸出: Signal 11 catched!
```

**如代碼所示**：註冊信號處理函數後，當收到 SIGSEGV 信號後，先執行相關的邏輯再退出

另外當進程接收信號之後也可以不定義自己的信號處理函數，而是選擇忽略信號，如下

```c
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

int main(void) {
  // 忽略信號
  signal(SIGSEGV, SIG_IGN);

  // 產生一個 SIGSEGV 信號
  raise(SIGSEGV);

  printf("正常結束");
}
```

也就是說雖然給進程發送了 kill 信號，但如果進程自己定義了信號處理函數或者無視信號就有機會逃出生天，當然了 kill -9 命令例外，不管進程是否定義了信號處理函數，都會馬上被幹掉。

說到這大家是否想起了一道經典面試題：**如何讓正在運行的 Java 工程的優雅停機？**

通過上面的介紹大家不難發現，其實是 JVM 自己定義了信號處理函數，這樣當發送 kill pid 命令（默認會傳 15 也就是 SIGTERM）後，JVM 就可以在信號處理函數中執行一些資源清理之後再調用 exit 退出。

這種場景顯然不能用 kill -9，不然一下把進程幹掉了資源就來不及清除了。

## 為什麼線程崩潰不會導致 JVM 進程崩潰

現在我們再來看看開頭這個問題，相信你多少會心中有數，想想看在 Java 中有哪些是常見的由於非法訪問內存而產生的 Exception 或 error 呢，常見的是大家熟悉的 StackoverflowError 或者 NPE（NullPointerException）,NPE 我們都瞭解，屬於是訪問了不存在的內存。

但為什麼棧溢出（Stackoverflow）也屬於非法訪問內存呢，這得簡單聊一下進程的虛擬空間，也就是前面提到的共享地址空間。

現代操作系統為了保護進程之間不受影響，所以使用了虛擬地址空間來隔離進程，進程的尋址都是針對虛擬地址，每個進程的虛擬空間都是一樣的，而線程會共用進程的地址空間。

以 32 位虛擬空間，進程的虛擬空間分佈如下：

![](https://img-blog.csdnimg.cn/8de250fcb055400c94f95c99712a1158.png)

那麼 stackoverflow 是怎麼發生的呢？

進程每調用一個函數，都會分配一個棧幀，然後在棧幀裡會分配函數裡定義的各種局部變量。

假設現在調用了一個無限遞歸的函數，那就會持續分配棧幀，但 stack 的大小是有限的（Linux 中默認為 8 M，可以通過 ulimit -a 查看），如果無限遞歸很快棧就會分配完了，此時再調用函數試圖分配超出棧的大小內存，就會發生段錯誤，也就是 stackoverflowError。

![](https://img-blog.csdnimg.cn/c54aff1660e34d8a8a83d534c3390954.png)

好了，現在我們知道了 StackoverflowError 怎麼產生的。

那問題來了，既然 StackoverflowError 或者 NPE 都屬於非法訪問內存， JVM 為什麼不會崩潰呢？

有了上一節的鋪墊，相信你不難回答，其實就是**因為 JVM 自定義了自己的信號處理函數，攔截了 SIGSEGV 信號，針對這兩者不讓它們崩潰**。

怎麼證明這個推測呢，我們來看下 JVM 的源碼來一探究竟

## openJDK 源碼解析

HotSpot 虛擬機目前使用範圍最廣的 Java 虛擬機，據 R 大所述， Oracle JDK 與 OpenJDK 裡的 JVM 都是 HotSpot VM，從源碼層面說，兩者基本上是同一個東西。

OpenJDK 是開源的，所以我們主要研究下 Java 8 的 OpenJDK 即可，地址如下：[https://github.com/AdoptOpenJDK/openjdk-jdk8u](https://github.com/AdoptOpenJDK/openjdk-jdk8u)，有興趣的可以下載來看看。

我們只要研究 Linux 下的 JVM，為了便於說明，也方便大家查閱，我把其中關於信號處理的關鍵流程整理了下（忽略其中的次要代碼）。

![](https://img-blog.csdnimg.cn/474ddf8657a0438da1822e0f6fa59af7.png)


可以看到，在啟動 JVM 的時候，也設置了信號處理函數，收到 SIGSEGV，SIGPIPE 等信號後最終會調用 JVM_handle_linux_signal 這個自定義信號處理函數，再來看下這個函數的主要邏輯。

```java
JVM_handle_linux_signal(int sig,
                        siginfo_t* info,
                        void* ucVoid,
                        int abort_if_unrecognized) {

   // Must do this before SignalHandlerMark, if crash protection installed we will longjmp away
  // 這段代碼裡會調用 siglongjmp，主要做線程恢復之用
  os::ThreadCrashProtection::check_crash_protection(sig, t);

  if (info != NULL && uc != NULL && thread != NULL) {
    pc = (address) os::Linux::ucontext_get_pc(uc);

    // Handle ALL stack overflow variations here
    if (sig == SIGSEGV) {
      // Si_addr may not be valid due to a bug in the linux-ppc64 kernel (see
      // comment below). Use get_stack_bang_address instead of si_addr.
      address addr = ((NativeInstruction*)pc)->get_stack_bang_address(uc);

      // 判斷是否棧溢出了
      if (addr < thread->stack_base() &&
          addr >= thread->stack_base() - thread->stack_size()) {
        if (thread->thread_state() == _thread_in_Java) {            // 針對棧溢出 JVM 的內部處理
            stub = SharedRuntime::continuation_for_implicit_exception(thread, pc, SharedRuntime::STACK_OVERFLOW);
        }
      }
    }
  }

  if (sig == SIGSEGV &&
               !MacroAssembler::needs_explicit_null_check((intptr_t)info->si_addr)) {
         // 此處會做空指針檢查
      stub = SharedRuntime::continuation_for_implicit_exception(thread, pc, SharedRuntime::IMPLICIT_NULL);
  }


  // 如果是棧溢出或者空指針最終會返回 true，不會走最後的 report_and_die，所以 JVM 不會退出
  if (stub != NULL) {
    // save all thread context in case we need to restore it
    if (thread != NULL) thread->set_saved_exception_pc(pc);

    uc->uc_mcontext.gregs[REG_PC] = (greg_t)stub;
    // 返回 true 代表 JVM 進程不會退出
    return true;
  }

  VMError err(t, sig, pc, info, ucVoid);
  // 生成 hs_err_pid_xxx.log 文件並退出
  err.report_and_die();

  ShouldNotReachHere();
  return true; // Mute compiler

}
```

從以上代碼我們可以知道以下信息：

1. 發生 stackoverflow 還有空指針錯誤，確實都發送了 SIGSEGV，只是虛擬機不選擇退出，而是自己內部作了額外的處理，其實是恢復了線程的執行，並拋出 StackoverflowError 和 NPE，這就是為什麼 JVM 不會崩潰且我們能捕獲這兩個錯誤/異常的原因
2. 如果針對 SIGSEGV 等信號，在以上的函數中 JVM 沒有做額外的處理，那麼最終會走到 report_and_die 這個方法，這個方法主要做的事情是生成 hs_err_pid_xxx.log crash 文件（記錄了一些堆棧信息或錯誤），然後退出

至此我相信大家明白了為什麼發生了 StackoverflowError 和 NPE 這兩個非法訪問內存的錯誤，JVM 卻沒有崩潰。

**原因其實就是虛擬機內部定義了信號處理函數，而在信號處理函數中對這兩者做了額外的處理以讓 JVM 不崩潰，另一方面也可以看出如果 JVM 不對信號做額外的處理，最後會自己退出併產生 crash 文件 hs_err_pid_xxx.log（可以通過 -XX:ErrorFile=/var/*log*/hs_err.log 這樣的方式指定），這個文件記錄了虛擬機崩潰的重要原因**。

所以也可以說，虛擬機是否崩潰只要看它是否會產生此崩潰日誌文件

## 總結

正常情況下，操作系統為了保證系統安全，所以針對非法內存訪問會發送一個 SIGSEGV 信號，而操作系統一般會調用默認的信號處理函數（一般會讓相關的進程崩潰）。

但如果進程覺得"罪不致死"，那麼它也可以選擇自定義一個信號處理函數，這樣的話它就可以做一些自定義的邏輯，比如記錄 crash 信息等有意義的事。

回過頭來看為什麼虛擬機會針對 StackoverflowError 和 NullPointerException 做額外處理讓線程恢復呢，針對 stackoverflow 其實它採用了一種棧回溯的方法保證線程可以一直執行下去，而捕獲空指針錯誤主要是這個錯誤實在太普遍了。

為了這一個很常見的錯誤而讓 JVM 崩潰那線上的 JVM 要宕機多少次，所以出於工程健壯性的考慮，與其直接讓 JVM 崩潰倒不如讓線程起死回生，並且將這兩個錯誤/異常拋給用戶來處理。

---

***哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，歡迎微信搜索「小林coding」，關注後，回覆「網絡」再送你圖解網絡 PDF***

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)
