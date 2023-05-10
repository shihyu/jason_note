# 4.4 在 4GB 物理內存的機器上，申請 8G 內存會怎麼樣？

大家好，我是小林。

看到讀者在群裡討論這些面試題：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/讀者提問.png)

其中，第一個問題「**在 4GB 物理內存的機器上，申請 8G 內存會怎麼樣？**」存在比較大的爭議，有人說會申請失敗，有的人說可以申請成功。

這個問題在沒有前置條件下，就說出答案就是耍流氓。這個問題要考慮三個前置條件：

- 操作系統是 32 位的，還是 64 位的？
- 申請完 8G 內存後會不會被使用？
- 操作系統有沒有使用 Swap 機制？

所以，我們要分場景討論。

## 操作系統虛擬內存大小

應用程序通過 malloc 函數申請內存的時候，實際上申請的是虛擬內存，此時並不會分配物理內存。

當應用程序讀寫了這塊虛擬內存，CPU 就會去訪問這個虛擬內存， 這時會發現這個虛擬內存沒有映射到物理內存， CPU 就會產生**缺頁中斷**，進程會從用戶態切換到內核態，並將缺頁中斷交給內核的 Page Fault Handler （缺頁中斷函數）處理。

缺頁中斷處理函數會看是否有空閒的物理內存：

- 如果有，就直接分配物理內存，並建立虛擬內存與物理內存之間的映射關係。
- 如果沒有空閒的物理內存，那麼內核就會開始進行[回收內存](https://xiaolincoding.com/os/3_memory/mem_reclaim.html)的工作，如果回收內存工作結束後，空閒的物理內存仍然無法滿足此次物理內存的申請，那麼內核就會放最後的大招了觸發 OOM （Out of Memory）機制。

32 位操作系統和 64 位操作系統的虛擬地址空間大小是不同的，在 Linux 操作系統中，虛擬地址空間的內部又被分為**內核空間和用戶空間**兩部分，如下所示：

![](https://img-blog.csdnimg.cn/3a6cb4e3f27241d3b09b4766bb0b1124.png)

通過這裡可以看出：

- `32` 位系統的內核空間佔用 `1G`，位於最高處，剩下的 `3G` 是用戶空間；
- `64` 位系統的內核空間和用戶空間都是 `128T`，分別佔據整個內存空間的最高和最低處，剩下的中間部分是未定義的。

### 32 位系統的場景

> 現在可以回答這個問題了：在 32 位操作系統、4GB 物理內存的機器上，申請 8GB 內存，會怎麼樣？

因為 32 位操作系統，進程最多隻能申請 3 GB 大小的虛擬內存空間，所以進程申請 8GB 內存的話，在申請虛擬內存階段就會失敗（我手上沒有 32 位操作系統測試，我估計失敗的錯誤是 cannot allocate memory，也就是無法申請內存失敗）。

### 64 位系統的場景

> 在 64 位操作系統、4GB 物理內存的機器上，申請 8G 內存，會怎麼樣？

64 位操作系統，進程可以使用 128 TB 大小的虛擬內存空間，所以進程申請 8GB 內存是沒問題的，因為進程申請內存是申請虛擬內存，只要不讀寫這個虛擬內存，操作系統就不會分配物理內存。

我們可以簡單做個測試，我的服務器是 64 位操作系統，但是物理內存只有 2 GB：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/2gb.png)

現在，我在機器上，連續申請 4 次 1 GB 內存，也就是一共申請了 4 GB 內存，注意下面代碼只是單純分配了虛擬內存，並沒有使用該虛擬內存：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define MEM_SIZE 1024 * 1024 * 1024

int main() {
    char* addr[4];
    int i = 0;
    for(i = 0; i < 4; ++i) {
        addr[i] = (char*) malloc(MEM_SIZE);
        if(!addr[i]) {
            printf("執行 malloc 失敗, 錯誤：%s\n",strerror(errno));
		        return -1;
        }
        printf("主線程調用malloc後，申請1gb大小得內存，此內存起始地址：0X%p\n", addr[i]);
    }
    
    //輸入任意字符後，才結束
    getchar();
    return 0;
}
```

然後運行這個代碼，可以看到，我的物理內存雖然只有 2GB，但是程序正常分配了 4GB 大小的虛擬內存：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/虛擬內存4g.png)

我們可以通過下面這條命令查看進程（test）的虛擬內存大小：

```shell
# ps aux | grep test
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      7797  0.0  0.0 4198540  352 pts/1    S+   16:58   0:00 ./test
```

其中，VSZ 就代表進程使用的虛擬內存大小，RSS 代表進程使用的物理內存大小。可以看到，VSZ 大小為 4198540，也就是 4GB 的虛擬內存。

> 之前有讀者跟我反饋，說他自己也做了這個實驗，然後發現 64 位操作系統，在申請 4GB 虛擬內存的時候失敗了，這是為什麼呢？

失敗的錯誤：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-1.png)

我當時幫他排查了下，發現跟 Linux 中的 [overcommit_memory](http://linuxperf.com/?p=102) 參數有關，可以使用 `cat /proc/sys/vm/overcommit_memory` 來查看這個參數，這個參數接受三個值：

- 如果值為 0（默認值），代表：Heuristic overcommit handling，它允許overcommit，但過於明目張膽的overcommit會被拒絕，比如malloc一次性申請的內存大小就超過了系統總內存。Heuristic的意思是“試探式的”，內核利用某種算法猜測你的內存申請是否合理，大概可以理解為單次申請不能超過free memory + free swap + pagecache的大小 + SLAB中可回收的部分 ，超過了就會拒絕overcommit。
- 如果值為 1，代表：Always overcommit. 允許overcommit，對內存申請來者不拒。
- 如果值為 2，代表：Don’t overcommit. 禁止overcommit。

當時那位讀者的 overcommit_memory 參數是默認值 0 ，所以申請失敗的原因可能是內核認為我們申請的內存太大了，它認為不合理，所以 malloc() 返回了 Cannot allocate memory 錯誤，這裡申請 4GB 虛擬內存失敗的同學可以將這個 overcommit_memory 設置為1，就可以 overcommit 了。

```shell
echo 1 > /proc/sys/vm/overcommit_memory 
```

設置完為 1 後，讀者的機子就可以正常申請 4GB 虛擬內存了。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-2.png)

**不過我的環境 overcommit_memory 是 0，在 64 系統、2 G 物理內存場景下，也是可以成功申請 4 G 內存的，我懷疑可能是不同版本的內核在 overcommit_memory 為 0 時，檢測內存申請是否合理的算法可能是不同的。**

**總之，如果你申請大內存的時候，不想被內核檢測內存申請是否合理的算法幹擾的話，將 overcommit_memory 設置為 1 就行。**

> 那麼將這個 overcommit_memory 設置為 1 之後，64 位的主機就可以申請接近 128T 虛擬內存了嗎？

不一定，還得看你服務器的物理內存大小。

讀者的服務器物理內存是 2 GB，實驗後發現，進程還沒有申請到 128T 虛擬內存的時候就被殺死了。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-3.png)

注意，這次是 killed，而不是 Cannot Allocate Memory，說明並不是內存申請有問題，而是觸發 OOM 了。

但是為什麼會觸發 OOM 呢？

那得看你的主機的「物理內存」夠不夠大了，即使 malloc 申請的是虛擬內存，只要不去訪問就不會映射到物理內存，但是申請虛擬內存的過程中，還是使用到了物理內存（比如內核保存虛擬內存的數據結構，也是佔用物理內存的），如果你的主機是隻有 2GB 的物理內存的話，大概率會觸發 OOM。

可以使用 top 命令，點擊兩下 m，通過進度條觀察物理內存使用情況。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-4.png)

可以看到申請虛擬內存的過程中**物理內存使用量一直在增長**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-5.png)

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-6.png)

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-7.png)

直到直接內存回收之後，也無法回收出一塊空間供這個進程使用，這個時候就會觸發 OOM，給所有能殺死的進程打分，分數越高的進程越容易被殺死。

在這裡當然是這個進程得分最高，那麼操作系統就會將這個進程殺死，所以最後會出現 killed，而不是Cannot allocate memory。

> 那麼 2GB 的物理內存的 64 位操作系統，就不能申請128T的虛擬內存了嗎？

其實可以，上面的情況是還沒開啟 swap 的情況。

使用 swapfile 的方式開啟了 1GB 的 swap 空間之後再做實驗：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-8.png)

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-9.png)

發現出現了 Cannot allocate memory，但是其實到這裡已經成功了，

打開計算器計算一下，發現已經申請了 127.998T 虛擬內存了。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-10.png)

實際上我們是不可能申請完整個 128T 的用戶空間的，因為程序運行本身也需要申請虛擬空間

申請 127T 虛擬內存試試：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-11.png)

發現進程沒有被殺死，也沒有 Cannot allocate memory，也正好是 127T 虛擬內存空間。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-12.png)

在 top 中我們可以看到這個申請了127T虛擬內存的進程。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/033讀者-13.png)

## Swap 機制的作用

前面討論在 32 位/64 位操作系統環境下，申請的虛擬內存超過物理內存後會怎麼樣？

- 在 32 位操作系統，因為進程最大隻能申請 3 GB 大小的虛擬內存，所以直接申請 8G 內存，會申請失敗。
- 在 64 位操作系統，因為進程最大隻能申請 128 TB 大小的虛擬內存，即使物理內存只有 4GB，申請 8G 內存也是沒問題，因為申請的內存是虛擬內存。

程序申請的虛擬內存，如果沒有被使用，它是不會佔用物理空間的。當訪問這塊虛擬內存後，操作系統才會進行物理內存分配。

如果申請物理內存大小超過了空閒物理內存大小，就要看操作系統有沒有開啟 Swap 機制：

- 如果沒有開啟 Swap 機制，程序就會直接 OOM；
- 如果有開啟 Swap 機制，程序可以正常運行。

> 什麼是 Swap 機制？

當系統的物理內存不夠用的時候，就需要將物理內存中的一部分空間釋放出來，以供當前運行的程序使用。那些被釋放的空間可能來自一些很長時間沒有什麼操作的程序，這些被釋放的空間會被臨時保存到磁盤，等到那些程序要運行時，再從磁盤中恢復保存的數據到內存中。

另外，當內存使用存在壓力的時候，會開始觸發內存回收行為，會把這些不常訪問的內存先寫到磁盤中，然後釋放這些內存，給其他更需要的進程使用。再次訪問這些內存時，重新從磁盤讀入內存就可以了。

這種，將內存數據換出磁盤，又從磁盤中恢復數據到內存的過程，就是 Swap 機制負責的。

Swap 就是把一塊磁盤空間或者本地文件，當成內存來使用，它包含換出和換入兩個過程：

- **換出（Swap Out）** ，是把進程暫時不用的內存數據存儲到磁盤中，並釋放這些數據佔用的內存；
- **換入（Swap In）**，是在進程再次訪問這些內存的時候，把它們從磁盤讀到內存中來；

Swap 換入換出的過程如下圖：

![](https://img-blog.csdnimg.cn/388a29f45fe947e5a49240e4eff13538.png)

使用 Swap 機制優點是，應用程序實際可以使用的內存空間將遠遠超過系統的物理內存。由於硬盤空間的價格遠比內存要低，因此這種方式無疑是經濟實惠的。當然，頻繁地讀寫硬盤，會顯著降低操作系統的運行速率，這也是 Swap 的弊端。

Linux 中的 Swap 機制會在內存不足和內存閒置的場景下觸發：

- **內存不足**：當系統需要的內存超過了可用的物理內存時，內核會將內存中不常使用的內存頁交換到磁盤上為當前進程讓出內存，保證正在執行的進程的可用性，這個內存回收的過程是強制的直接內存回收（Direct Page Reclaim）。直接內存回收是同步的過程，會阻塞當前申請內存的進程。
- **內存閒置**：應用程序在啟動階段使用的大量內存在啟動後往往都不會使用，通過後臺運行的守護進程（kSwapd），我們可以將這部分只使用一次的內存交換到磁盤上為其他內存的申請預留空間。kSwapd 是 Linux 負責頁面置換（Page replacement）的守護進程，它也是負責交換閒置內存的主要進程，它會在[空閒內存低於一定水位](https://xiaolincoding.com/os/3_memory/mem_reclaim.html#%E5%B0%BD%E6%97%A9%E8%A7%A6%E5%8F%91-kSwapd-%E5%86%85%E6%A0%B8%E7%BA%BF%E7%A8%8B%E5%BC%82%E6%AD%A5%E5%9B%9E%E6%94%B6%E5%86%85%E5%AD%98)時，回收內存頁中的空閒內存保證系統中的其他進程可以儘快獲得申請的內存。kSwapd 是後臺進程，所以回收內存的過程是異步的，不會阻塞當前申請內存的進程。

Linux 提供了兩種不同的方法啟用 Swap，分別是 Swap 分區（Swap Partition）和 Swap 文件（Swapfile），開啟方法可以看[這個資料](https://support.huaweicloud.com/trouble-ecs/ecs_trouble_0322.html)：

- Swap 分區是硬盤上的獨立區域，該區域只會用於交換分區，其他的文件不能存儲在該區域上，我們可以使用 `swapon -s` 命令查看當前系統上的交換分區；
- Swap 文件是文件系統中的特殊文件，它與文件系統中的其他文件也沒有太多的區別；

> Swap 換入換出的是什麼類型的內存？

內核緩存的文件數據，因為都有對應的磁盤文件，所以在回收文件數據的時候， 直接寫回到對應的文件就可以了。

但是像進程的堆、棧數據等，它們是沒有實際載體，這部分內存被稱為匿名頁。而且這部分內存很可能還要再次被訪問，所以不能直接釋放內存，於是就需要有一個能保存匿名頁的磁盤載體，這個載體就是 Swap 分區。

匿名頁回收的方式是通過 Linux 的 Swap 機制，Swap 會把不常訪問的內存先寫到磁盤中，然後釋放這些內存，給其他更需要的進程使用。再次訪問這些內存時，重新從磁盤讀入內存就可以了。

接下來，通過兩個實驗，看看申請的物理內存超過物理內存會怎樣？

- 實驗一：沒有開啟 Swap 機制
- 實驗二：有開啟 Swap 機制

### 實驗一：沒有開啟 Swap 機制

我的服務器是 64 位操作系統，但是物理內存只有 2 GB，而且沒有 Swap 分區：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/2gb.png)

我們改一下前面的代碼，使得在申請完 4GB 虛擬內存後，通過 memset 函數訪問這個虛擬內存，看看在沒有 Swap 分區的情況下，會發生什麼？

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define MEM_SIZE 1024 * 1024 * 1024

int main() {
    char* addr[4];
    int i = 0;
    for(i = 0; i < 4; ++i) {
        addr[i] = (char*) malloc(MEM_SIZE);
        if(!addr[i]) {
            printf("執行 malloc 失敗, 錯誤：%s\n",strerror(errno));
            return -1;
        }
        printf("主線程調用malloc後，申請1gb大小得內存，此內存起始地址：0X%p\n", addr[i]);
    }

    for(i = 0; i < 4; ++i) {
        printf("開始訪問第 %d 塊虛擬內存(每一塊虛擬內存為 1 GB)\n", i + 1);
        memset(addr[i], 0, MEM_SIZE);
    }
    
    //輸入任意字符後，才結束
    getchar();
    return 0;
}
```

運行結果：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/發生oom.png)

可以看到，在訪問第 2 塊虛擬內存（每一塊虛擬內存是 1 GB）的時候，因為超過了機器的物理內存（2GB），進程（test）被操作系統殺掉了。

通過查看 message 系統日誌，可以發現該進程是被操作系統 OOM killer 機制殺掉了，日誌裡報錯了 Out of memory，也就是發生 OOM（內存溢出錯誤）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/oom日誌.png)

> 什麼是 OOM?

內存溢出(Out Of Memory，簡稱OOM)是指應用系統中存在無法回收的內存或使用的內存過多，最終使得程序運行要用到的內存大於能提供的最大內存。此時程序就運行不了，系統會提示內存溢出。

### 實驗二：有開啟 Swap 機制

我用我的 mac book pro 筆記本做測試，我的筆記本是 64 位操作系統，物理內存是 8 GB， 目前 Swap 分區大小為 1 GB（注意這個大小不是固定不變的，Swap 分區總大小是會動態變化的，當沒有使用 Swap 分區時，Swap 分區總大小是 0；當使用了 Swap 分區，Swap 分區總大小會增加至 1 GB；當 Swap 分區已使用的大小超過 1 GB 時；Swap 分區總大小就會增加到至 2 GB；當 Swap 分區已使用的大小超過 2 GB 時；Swap 分區總大小就增加至 3GB，如此往復。這個估計是 macos 自己實現的，Linux 的分區則是固定大小的，Swap 分區不會根據使用情況而自動增長）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/swap分區大小.png)

為了方便觀察磁盤 I/O 情況，我們改進一下前面的代碼，分配完 32 GB虛擬內存後（筆記本物理內存是 8 GB），通過一個 while 循環頻繁訪問虛擬內存，代碼如下：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MEM_SIZE 32 * 1024 * 1024 * 1024

int main() {
    char* addr = (char*) malloc((long)MEM_SIZE);
    printf("主線程調用malloc後，目前共申請了 32gb 的虛擬內存\n");
    
    //循環頻繁訪問虛擬內存
    while(1) {
          printf("開始訪問 32gb 大小的虛擬內存...\n");
          memset(addr, 0, (long)MEM_SIZE);
    }
    return 0;
}
```

運行結果如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/代碼3運行結果.png)

可以看到，在有 Swap 分區的情況下，即使筆記本物理內存是 8 GB，申請並使用 32 GB 內存是沒問題，程序正常運行了，並沒有發生 OOM。

從下圖可以看到，進程的內存顯示 32 GB（這個不要理解為佔用的物理內存，理解為已被訪問的虛擬內存大小，也就是在物理內存呆過的內存大小），系統已使用的 Swap 分區達到 2.3 GB。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/test進程內存情況.png)

此時我的筆記本電腦的磁盤開始出現“沙沙”的聲音，通過查看磁盤的 I/O 情況，可以看到磁盤 I/O 達到了一個峰值，非常高：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/磁盤io.png)

> 有了 Swap 分區，是不是意味著進程可以使用的內存是無上限的？

當然不是，我把上面的代碼改成了申請 64GB 內存後，當進程申請完 64GB 虛擬內存後，使用到 56 GB （這個不要理解為佔用的物理內存，理解為已被訪問的虛擬內存大小，也就是在物理內存呆過的內存大小）的時候，進程就被系統 kill 掉了，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/操作系統/內存管理/被kill掉.png)

當系統多次嘗試回收內存，還是無法滿足所需使用的內存大小，進程就會被系統 kill 掉了，意味著發生了 OOM （*PS：我沒有在 macos 系統找到像 linux 系統裡的 /var/log/message 系統日誌文件，所以無法通過查看日誌確認是否發生了 OOM*）。

## 總結

至此， 驗證完成了。簡單總結下：

- 在 32 位操作系統，因為進程理論上最大能申請 3 GB 大小的虛擬內存，所以直接申請 8G 內存，會申請失敗。
- 在 64位 位操作系統，因為進程理論上最大能申請 128 TB 大小的虛擬內存，即使物理內存只有 4GB，申請 8G 內存也是沒問題，因為申請的內存是虛擬內存。如果這塊虛擬內存被訪問了，要看系統有沒有 Swap 分區：
  - 如果沒有 Swap 分區，因為物理空間不夠，進程會被操作系統殺掉，原因是 OOM（內存溢出）；
  - 如果有 Swap 分區，即使物理內存只有 4GB，程序也能正常使用 8GB 的內存，進程可以正常運行；

---

***哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，歡迎微信搜索「小林coding」，關注後，回覆「網絡」再送你圖解網絡 PDF***

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)



