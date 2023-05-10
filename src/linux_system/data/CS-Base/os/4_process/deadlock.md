# 5.4 怎麼避免死鎖？

面試過程中，死鎖也是高頻的考點，因為如果線上環境真多發生了死鎖，那真的出大事了。

這次，我們就來系統地聊聊死鎖的問題。

- 死鎖的概念；
- 模擬死鎖問題的產生；
- 利用工具排查死鎖問題；
- 避免死鎖問題的發生；

---

## 死鎖的概念

在多線程編程中，我們為了防止多線程競爭共享資源而導致數據錯亂，都會在操作共享資源之前加上互斥鎖，只有成功獲得到鎖的線程，才能操作共享資源，獲取不到鎖的線程就只能等待，直到鎖被釋放。

那麼，當兩個線程為了保護兩個不同的共享資源而使用了兩個互斥鎖，那麼這兩個互斥鎖應用不當的時候，可能會造成**兩個線程都在等待對方釋放鎖**，在沒有外力的作用下，這些線程會一直相互等待，就沒辦法繼續運行，這種情況就是發生了**死鎖**。

舉個例子，小林拿了小美房間的鑰匙，而小林在自己的房間裡，小美拿了小林房間的鑰匙，而小美也在自己的房間裡。如果小林要從自己的房間裡出去，必須拿到小美手中的鑰匙，但是小美要出去，又必須拿到小林手中的鑰匙，這就形成了死鎖。

死鎖只有**同時滿足**以下四個條件才會發生：

- 互斥條件；
- 持有並等待條件；
- 不可剝奪條件；
- 環路等待條件；


### 互斥條件

互斥條件是指**多個線程不能同時使用同一個資源**。

比如下圖，如果線程 A 已經持有的資源，不能再同時被線程 B 持有，如果線程 B 請求獲取線程 A 已經佔用的資源，那線程 B 只能等待，直到線程 A 釋放了資源。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/操作系統/死鎖/互斥條件.png)

### 持有並等待條件

持有並等待條件是指，當線程 A 已經持有了資源 1，又想申請資源 2，而資源 2 已經被線程 C 持有了，所以線程  A 就會處於等待狀態，但是**線程  A 在等待資源 2 的同時並不會釋放自己已經持有的資源 1**。 

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/操作系統/死鎖/持有並等待條件.png)



### 不可剝奪條件

不可剝奪條件是指，當線程已經持有了資源 ，**在自己使用完之前不能被其他線程獲取**，線程 B 如果也想使用此資源，則只能在線程 A 使用完並釋放後才能獲取。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/操作系統/死鎖/不可剝奪條件.png)

### 環路等待條件

環路等待條件指的是，在死鎖發生的時候，**兩個線程獲取資源的順序構成了環形鏈**。

比如，線程 A 已經持有資源 2，而想請求資源 1， 線程 B 已經獲取了資源 1，而想請求資源 2，這就形成資源請求等待的環形圖。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/操作系統/死鎖/環路等待條件.png)


---

## 模擬死鎖問題的產生

Talk is cheap. Show me the code.

下面，我們用代碼來模擬死鎖問題的產生。

首先，我們先創建 2 個線程，分別為線程 A 和 線程 B，然後有兩個互斥鎖，分別是 mutex_A 和 mutex_B，代碼如下：

```c
pthread_mutex_t mutex_A = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mutex_B = PTHREAD_MUTEX_INITIALIZER;

int main()
{
    pthread_t tidA, tidB;
    
    //創建兩個線程
    pthread_create(&tidA, NULL, threadA_proc, NULL);
    pthread_create(&tidB, NULL, threadB_proc, NULL);
    
    pthread_join(tidA, NULL);
    pthread_join(tidB, NULL);
    
    printf("exit\n");
    
    return 0;
}
```

接下來，我們看下線程 A 函數做了什麼。


```c
//線程函數 A
void *threadA_proc(void *data)
{
    printf("thread A waiting get ResourceA \n");
    pthread_mutex_lock(&mutex_A);
    printf("thread A got ResourceA \n");
    
    sleep(1);
    
    printf("thread A waiting get ResourceB \n");
    pthread_mutex_lock(&mutex_B);
    printf("thread A got ResourceB \n");

    pthread_mutex_unlock(&mutex_B);
    pthread_mutex_unlock(&mutex_A);
    return (void *)0;
}
```

可以看到，線程 A 函數的過程：

- 先獲取互斥鎖 A，然後睡眠 1 秒；
- 再獲取互斥鎖 B，然後釋放互斥鎖 B；
- 最後釋放互斥鎖 A；

```c
//線程函數 B
void *threadB_proc(void *data)
{
    printf("thread B waiting get ResourceB \n");
    pthread_mutex_lock(&mutex_B);
    printf("thread B got ResourceB \n");
    
    sleep(1);
    
    printf("thread B waiting  get ResourceA \n");
    pthread_mutex_lock(&mutex_A);
    printf("thread B got ResourceA \n");
    
    pthread_mutex_unlock(&mutex_A);
    pthread_mutex_unlock(&mutex_B);
    return (void *)0;
}
```

可以看到，線程 B 函數的過程：

- 先獲取互斥鎖 B，然後睡眠 1 秒；
- 再獲取互斥鎖 A，然後釋放互斥鎖 A；
- 最後釋放互斥鎖 B；

然後，我們運行這個程序，運行結果如下：

```shell
thread B waiting get ResourceB 
thread B got ResourceB 
thread A waiting get ResourceA 
thread A got ResourceA 
thread B waiting get ResourceA 
thread A waiting get ResourceB 
// 阻塞中。。。
```

可以看到線程 B 在等待互斥鎖 A 的釋放，線程 A 在等待互斥鎖 B 的釋放，雙方都在等待對方資源的釋放，很明顯，產生了死鎖問題。

---

## 利用工具排查死鎖問題

如果你想排查你的 Java 程序是否死鎖，則可以使用 `jstack` 工具，它是 jdk 自帶的線程堆棧分析工具。

由於小林的死鎖代碼例子是 C 寫的，在 Linux 下，我們可以使用 `pstack` + `gdb` 工具來定位死鎖問題。

pstack 命令可以顯示每個線程的棧跟蹤信息（函數調用過程），它的使用方式也很簡單，只需要 `pstack <pid>` 就可以了。

那麼，在定位死鎖問題時，我們可以多次執行 pstack 命令查看線程的函數調用過程，多次對比結果，確認哪幾個線程一直沒有變化，且是因為在等待鎖，那麼大概率是由於死鎖問題導致的。

我用 pstack 輸出了我前面模擬死鎖問題的進程的所有線程的情況，我多次執行命令後，其結果都一樣，如下：

```shell
$ pstack 87746
Thread 3 (Thread 0x7f60a610a700 (LWP 87747)):
#0  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
#1  0x0000003720e093ca in _L_lock_829 () from /lib64/libpthread.so.0
#2  0x0000003720e09298 in pthread_mutex_lock () from /lib64/libpthread.so.0
#3  0x0000000000400725 in threadA_proc ()
#4  0x0000003720e07893 in start_thread () from /lib64/libpthread.so.0
#5  0x00000037206f4bfd in clone () from /lib64/libc.so.6
Thread 2 (Thread 0x7f60a5709700 (LWP 87748)):
#0  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
#1  0x0000003720e093ca in _L_lock_829 () from /lib64/libpthread.so.0
#2  0x0000003720e09298 in pthread_mutex_lock () from /lib64/libpthread.so.0
#3  0x0000000000400792 in threadB_proc ()
#4  0x0000003720e07893 in start_thread () from /lib64/libpthread.so.0
#5  0x00000037206f4bfd in clone () from /lib64/libc.so.6
Thread 1 (Thread 0x7f60a610c700 (LWP 87746)):
#0  0x0000003720e080e5 in pthread_join () from /lib64/libpthread.so.0
#1  0x0000000000400806 in main ()

....

$ pstack 87746
Thread 3 (Thread 0x7f60a610a700 (LWP 87747)):
#0  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
#1  0x0000003720e093ca in _L_lock_829 () from /lib64/libpthread.so.0
#2  0x0000003720e09298 in pthread_mutex_lock () from /lib64/libpthread.so.0
#3  0x0000000000400725 in threadA_proc ()
#4  0x0000003720e07893 in start_thread () from /lib64/libpthread.so.0
#5  0x00000037206f4bfd in clone () from /lib64/libc.so.6
Thread 2 (Thread 0x7f60a5709700 (LWP 87748)):
#0  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
#1  0x0000003720e093ca in _L_lock_829 () from /lib64/libpthread.so.0
#2  0x0000003720e09298 in pthread_mutex_lock () from /lib64/libpthread.so.0
#3  0x0000000000400792 in threadB_proc ()
#4  0x0000003720e07893 in start_thread () from /lib64/libpthread.so.0
#5  0x00000037206f4bfd in clone () from /lib64/libc.so.6
Thread 1 (Thread 0x7f60a610c700 (LWP 87746)):
#0  0x0000003720e080e5 in pthread_join () from /lib64/libpthread.so.0
#1  0x0000000000400806 in main ()
```

可以看到，Thread 2 和 Thread 3 一直阻塞獲取鎖（*pthread_mutex_lock*）的過程，而且 pstack 多次輸出信息都沒有變化，那麼可能大概率發生了死鎖。

但是，還不能夠確認這兩個線程是在互相等待對方的鎖的釋放，因為我們看不到它們是等在哪個鎖對象，於是我們可以使用 gdb 工具進一步確認。

整個 gdb 調試過程，如下：

```shell
// gdb 命令
$ gdb -p 87746

// 打印所有的線程信息
(gdb) info thread
  3 Thread 0x7f60a610a700 (LWP 87747)  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
  2 Thread 0x7f60a5709700 (LWP 87748)  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
* 1 Thread 0x7f60a610c700 (LWP 87746)  0x0000003720e080e5 in pthread_join () from /lib64/libpthread.so.0
//最左邊的 * 表示 gdb 鎖定的線程，切換到第二個線程去查看

// 切換到第2個線程
(gdb) thread 2
[Switching to thread 2 (Thread 0x7f60a5709700 (LWP 87748))]#0  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0 

// bt 可以打印函數堆棧，卻無法看到函數參數，跟 pstack 命令一樣 
(gdb) bt
#0  0x0000003720e0da1d in __lll_lock_wait () from /lib64/libpthread.so.0
#1  0x0000003720e093ca in _L_lock_829 () from /lib64/libpthread.so.0
#2  0x0000003720e09298 in pthread_mutex_lock () from /lib64/libpthread.so.0
#3  0x0000000000400792 in threadB_proc (data=0x0) at dead_lock.c:25
#4  0x0000003720e07893 in start_thread () from /lib64/libpthread.so.0
#5  0x00000037206f4bfd in clone () from /lib64/libc.so.6

// 打印第三幀信息，每次函數調用都會有壓棧的過程，而 frame 則記錄棧中的幀信息
(gdb) frame 3
#3  0x0000000000400792 in threadB_proc (data=0x0) at dead_lock.c:25
27    printf("thread B waiting get ResourceA \n");
28    pthread_mutex_lock(&mutex_A);

// 打印mutex_A的值 ,  __owner表示gdb中標示線程的值，即LWP
(gdb) p mutex_A
$1 = {__data = {__lock = 2, __count = 0, __owner = 87747, __nusers = 1, __kind = 0, __spins = 0, __list = {__prev = 0x0, __next = 0x0}}, 
  __size = "\002\000\000\000\000\000\000\000\303V\001\000\001", '\000' <repeats 26 times>, __align = 2}

// 打印mutex_B的值 ,  __owner表示gdb中標示線程的值，即LWP
(gdb) p mutex_B
$2 = {__data = {__lock = 2, __count = 0, __owner = 87748, __nusers = 1, __kind = 0, __spins = 0, __list = {__prev = 0x0, __next = 0x0}}, 
  __size = "\002\000\000\000\000\000\000\000\304V\001\000\001", '\000' <repeats 26 times>, __align = 2}  
```

我來解釋下，上面的調試過程：

1. 通過 `info thread` 打印了所有的線程信息，可以看到有 3 個線程，一個是主線程（LWP 87746），另外兩個都是我們自己創建的線程（LWP 87747 和 87748）；
2. 通過 `thread 2`，將切換到第 2 個線程（LWP 87748）；
3. 通過 `bt`，打印線程的調用棧信息，可以看到有 threadB_proc 函數，說明這個是線程 B 函數，也就說 LWP 87748 是線程 B;
4. 通過 `frame 3`，打印調用棧中的第三個幀的信息，可以看到線程 B 函數，在獲取互斥鎖 A 的時候阻塞了；
5. 通過 `p mutex_A`，打印互斥鎖 A 對象信息，可以看到它被 LWP 為 87747（線程 A） 的線程持有著；
6. 通過 `p mutex_B`，打印互斥鎖 B 對象信息，可以看到他被 LWP 為 87748 （線程 B） 的線程持有著；

因為線程 B 在等待線程 A 所持有的 mutex_A, 而同時線程 A 又在等待線程 B 所擁有的mutex_B, 所以可以斷定該程序發生了死鎖。


---

## 避免死鎖問題的發生

前面我們提到，產生死鎖的四個必要條件是：互斥條件、持有並等待條件、不可剝奪條件、環路等待條件。

那麼避免死鎖問題就只需要破環其中一個條件就可以，最常見的並且可行的就是**使用資源有序分配法，來破環環路等待條件**。

那什麼是資源有序分配法呢？

線程 A 和 線程 B 獲取資源的順序要一樣，當線程 A 是先嚐試獲取資源 A，然後嘗試獲取資源  B 的時候，線程 B 同樣也是先嚐試獲取資源 A，然後嘗試獲取資源 B。也就是說，線程 A 和 線程 B 總是以相同的順序申請自己想要的資源。

我們使用資源有序分配法的方式來修改前面發生死鎖的代碼，我們可以不改動線程 A 的代碼。

我們先要清楚線程 A 獲取資源的順序，它是先獲取互斥鎖 A，然後獲取互斥鎖 B。

所以我們只需將線程 B 改成以相同順序的獲取資源，就可以打破死鎖了。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/操作系統/死鎖/資源有序分配.png)

線程 B 函數改進後的代碼如下：

```c
//線程 B 函數，同線程 A 一樣，先獲取互斥鎖 A，然後獲取互斥鎖 B
void *threadB_proc(void *data)
{
    printf("thread B waiting get ResourceA \n");
    pthread_mutex_lock(&mutex_A);
    printf("thread B got ResourceA \n");
    
    sleep(1);
    
    printf("thread B waiting  get ResourceB \n");
    pthread_mutex_lock(&mutex_B);
    printf("thread B got ResourceB \n");
    
    pthread_mutex_unlock(&mutex_B);
    pthread_mutex_unlock(&mutex_A);
    return (void *)0;
}
```

執行結果如下，可以看，沒有發生死鎖。

```shell
thread B waiting get ResourceA 
thread B got ResourceA 
thread A waiting get ResourceA 
thread B waiting  get ResourceB 
thread B got ResourceB 
thread A got ResourceA 
thread A waiting get ResourceB 
thread A got ResourceB
exit
```

---

## 總結

簡單來說，死鎖問題的產生是由兩個或者以上線程並行執行的時候，爭奪資源而互相等待造成的。

死鎖只有同時滿足互斥、持有並等待、不可剝奪、環路等待這四個條件的時候才會發生。

所以要避免死鎖問題，就是要破壞其中一個條件即可，最常用的方法就是使用資源有序分配法來破壞環路等待條件。

---

## 關注作者

***哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，歡迎微信搜索「小林coding」，關注後，回覆「網絡」再送你圖解網絡 PDF***

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/其他/公眾號介紹.png)