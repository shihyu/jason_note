# 2.3 如何寫出讓 CPU 跑得更快的代碼？

代碼都是由 CPU 跑起來的，我們代碼寫的好與壞就決定了 CPU 的執行效率，特別是在編寫計算密集型的程序，更要注重 CPU 的執行效率，否則將會大大影響系統性能。

CPU 內部嵌入了 CPU Cache（高速緩存），它的存儲容量很小，但是離 CPU 核心很近，所以緩存的讀寫速度是極快的，那麼如果 CPU 運算時，直接從 CPU Cache 讀取數據，而不是從內存的話，運算速度就會很快。

但是，大多數人不知道 CPU Cache 的運行機制，以至於不知道如何才能夠寫出能夠配合 CPU Cache 工作機制的代碼，一旦你掌握了它，你寫代碼的時候，就有新的優化思路了。

那麼，接下來我們就來看看，CPU Cache 到底是什麼樣的，是如何工作的呢，又該如何寫出讓 CPU 執行更快的代碼呢？

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CPU%E7%BC%93%E5%AD%98/CPUCache%E6%8F%90%E7%BA%B2.png)

---

## CPU Cache 有多快？

你可能會好奇為什麼有了內存，還需要 CPU Cache？根據摩爾定律，CPU 的訪問速度每 18 個月就會翻倍，相當於每年增長 60% 左右，內存的速度當然也會不斷增長，但是增長的速度遠小於 CPU，平均每年只增長 7% 左右。於是，CPU 與內存的訪問性能的差距不斷拉大。

到現在，一次內存訪問所需時間是 `200~300` 多個時鐘週期，這意味著 CPU 和內存的訪問速度已經相差 `200~300` 多倍了。

為了彌補 CPU 與內存兩者之間的性能差異，就在 CPU 內部引入了  CPU Cache，也稱高速緩存。

 CPU Cache 通常分為大小不等的三級緩存，分別是 **L1 Cache、L2 Cache 和 L3 Cache**。

 由於 CPU Cache 所使用的材料是 SRAM，價格比內存使用的 DRAM 高出很多，在當今每生產 1 MB 大小的 CPU Cache 需要 7 美金的成本，而內存只需要 0.015 美金的成本，成本方面相差了 466 倍，所以 CPU Cache 不像內存那樣動輒以 GB 計算，它的大小是以 KB 或 MB 來計算的。


在 Linux 系統中，我們可以使用下圖的方式來查看各級 CPU Cache 的大小，比如我這手上這臺服務器，離 CPU 核心最近的 L1 Cache 是 32KB，其次是 L2 Cache 是 256KB，最大的 L3 Cache 則是 3MB。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/查看CPU高速緩存大小.png)


其中，**L1 Cache 通常會分為「數據緩存」和「指令緩存」**，這意味著數據和指令在 L1 Cache 這一層是分開緩存的，上圖中的 `index0` 也就是數據緩存，而 `index1` 則是指令緩存，它兩的大小通常是一樣的。

另外，你也會注意到，L3 Cache 比 L1 Cache 和 L2 Cache 大很多，這是因為 **L1 Cache 和 L2 Cache 都是每個 CPU 核心獨有的，而 L3 Cache 是多個 CPU 核心共享的。**

程序執行時，會先將內存中的數據加載到共享的 L3 Cache 中，再加載到每個核心獨有的 L2 Cache，最後進入到最快的 L1 Cache，之後才會被 CPU 讀取。它們之間的層級關係，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/操作系統/存儲結構/CPU-Cache.png)

越靠近 CPU 核心的緩存其訪問速度越快，CPU 訪問 L1 Cache 只需要 `2~4` 個時鐘週期，訪問 L2 Cache 大約 `10~20` 個時鐘週期，訪問 L3 Cache 大約 `20~60` 個時鐘週期，而訪問內存速度大概在 `200~300` 個 時鐘週期之間。如下表格：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/訪問速度表格.png)


**所以，CPU 從 L1 Cache 讀取數據的速度，相比從內存讀取的速度，會快 `100` 多倍。**

---

## CPU Cache 的數據結構和讀取過程是什麼樣的？

我們先簡單瞭解下 CPU Cache 的結構，CPU Cache 是由很多個 Cache Line 組成的，Cache Line 是 CPU 從內存讀取數據的基本單位，而 Cache Line 是由各種標誌（Tag）+ 數據塊（Data Block）組成，你可以在下圖清晰的看到：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CPU%E7%BC%93%E5%AD%98%E4%B8%80%E8%87%B4%E6%80%A7/Cache%E7%9A%84%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84.png)

CPU Cache 的數據是從內存中讀取過來的，它是以一小塊一小塊讀取數據的，而不是按照單個數組元素來讀取數據的，在 CPU Cache 中的，這樣一小塊一小塊的數據，稱為 **Cache Line（緩存塊）**。

你可以在你的 Linux 系統，用下面這種方式來查看 CPU 的 Cache Line，你可以看我服務器的 L1 Cache Line 大小是 64 字節，也就意味著 **L1 Cache 一次載入數據的大小是 64 字節**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/查看CPULine大小.png)


比如，有一個 `int array[100]` 的數組，當載入 `array[0]` 時，由於這個數組元素的大小在內存只佔 4 字節，不足 64 字節，CPU 就會**順序加載**數組元素到 `array[15]`，意味著 `array[0]~array[15]` 數組元素都會被緩存在 CPU Cache 中了，因此當下次訪問這些數組元素時，會直接從 CPU Cache 讀取，而不用再從內存中讀取，大大提高了 CPU 讀取數據的性能。

事實上，CPU 讀取數據的時候，無論數據是否存放到 Cache 中，CPU 都是先訪問 Cache，只有當 Cache 中找不到數據時，才會去訪問內存，並把內存中的數據讀入到 Cache 中，CPU 再從 CPU Cache 讀取數據。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/緩存邏輯.png)

這樣的訪問機制，跟我們使用「內存作為硬盤的緩存」的邏輯是一樣的，如果內存有緩存的數據，則直接返回，否則要訪問龜速一般的硬盤。

那 CPU 怎麼知道要訪問的內存數據，是否在 Cache 裡？如果在的話，如何找到 Cache 對應的數據呢？我們從最簡單、基礎的**直接映射 Cache（*Direct Mapped Cache*）** 說起，來看看整個 CPU Cache 的數據結構和訪問邏輯。


前面，我們提到 CPU 訪問內存數據時，是一小塊一小塊數據讀取的，具體這一小塊數據的大小，取決於 `coherency_line_size` 的值，一般 64 字節。在內存中，這一塊的數據我們稱為**內存塊（*Block*）**，讀取的時候我們要拿到數據所在內存塊的地址。

對於直接映射 Cache 採用的策略，就是把內存塊的地址始終「映射」在一個 CPU Cache Line（緩存塊） 的地址，至於映射關係實現方式，則是使用「取模運算」，取模運算的結果就是內存塊地址對應的 CPU Cache Line（緩存塊） 的地址。

舉個例子，內存共被劃分為 32 個內存塊，CPU Cache 共有 8 個 CPU Cache Line，假設 CPU 想要訪問第 15 號內存塊，如果 15 號內存塊中的數據已經緩存在 CPU Cache Line 中的話，則是一定映射在 7 號 CPU Cache Line 中，因為 `15 % 8` 的值是 7。

機智的你肯定發現了，使用取模方式映射的話，就會出現多個內存塊對應同一個 CPU Cache Line，比如上面的例子，除了 15 號內存塊是映射在 7 號 CPU Cache Line 中，還有 7 號、23 號、31 號內存塊都是映射到 7 號 CPU Cache Line 中。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CPU%E7%BC%93%E5%AD%98/%E6%B1%82%E6%A8%A1%E6%98%A0%E5%B0%84%E7%AD%96%E7%95%A5.png)


因此，為了區別不同的內存塊，在對應的 CPU Cache Line 中我們還會存儲一個**組標記（Tag）**。這個組標記會記錄當前 CPU Cache Line 中存儲的數據對應的內存塊，我們可以用這個組標記來區分不同的內存塊。

除了組標記信息外，CPU Cache Line 還有兩個信息：

- 一個是，從內存加載過來的實際存放**數據（*Data*）**。
- 另一個是，**有效位（*Valid bit*）**，它是用來標記對應的 CPU Cache Line 中的數據是否是有效的，如果有效位是 0，無論 CPU Cache Line 中是否有數據，CPU 都會直接訪問內存，重新加載數據。


CPU 在從 CPU Cache 讀取數據的時候，並不是讀取 CPU Cache Line 中的整個數據塊，而是讀取 CPU 所需要的一個數據片段，這樣的數據統稱為一個**字（*Word*）**。那怎麼在對應的 CPU Cache Line 中數據塊中找到所需的字呢？答案是，需要一個**偏移量（Offset）**。

因此，一個內存的訪問地址，包括**組標記、CPU Cache Line 索引、偏移量**這三種信息，於是 CPU 就能通過這些信息，在 CPU Cache 中找到緩存的數據。而對於 CPU Cache 裡的數據結構，則是由**索引 + 有效位 + 組標記 + 數據塊**組成。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/直接Cache映射.png)




如果內存中的數據已經在 CPU Cahe 中了，那 CPU 訪問一個內存地址的時候，會經歷這 4 個步驟：

1. 根據內存地址中索引信息，計算在 CPU Cahe 中的索引，也就是找出對應的 CPU Cache Line 的地址；
2. 找到對應 CPU Cache Line 後，判斷 CPU Cache Line 中的有效位，確認 CPU Cache Line 中數據是否是有效的，如果是無效的，CPU 就會直接訪問內存，並重新加載數據，如果數據有效，則往下執行；
3. 對比內存地址中組標記和 CPU Cache Line 中的組標記，確認 CPU Cache Line 中的數據是我們要訪問的內存數據，如果不是的話，CPU 就會直接訪問內存，並重新加載數據，如果是的話，則往下執行；
4. 根據內存地址中偏移量信息，從 CPU Cache Line 的數據塊中，讀取對應的字。

到這裡，相信你對直接映射 Cache 有了一定認識，但其實除了直接映射 Cache 之外，還有其他通過內存地址找到 CPU Cache 中的數據的策略，比如全相連 Cache （*Fully Associative Cache*）、組相連 Cache （*Set Associative Cache*）等，這幾種策策略的數據結構都比較相似，我們理解了直接映射 Cache 的工作方式，其他的策略如果你有興趣去看，相信很快就能理解的了。

---

## 如何寫出讓 CPU 跑得更快的代碼？

我們知道 CPU 訪問內存的速度，比訪問 CPU Cache 的速度慢了 100 多倍，所以如果 CPU 所要操作的數據在 CPU Cache 中的話，這樣將會帶來很大的性能提升。訪問的數據在 CPU Cache 中的話，意味著**緩存命中**，緩存命中率越高的話，代碼的性能就會越好，CPU 也就跑的越快。

於是，「如何寫出讓 CPU 跑得更快的代碼？」這個問題，可以改成「如何寫出 CPU 緩存命中率高的代碼？」。


在前面我也提到， L1 Cache 通常分為「數據緩存」和「指令緩存」，這是因為 CPU 會分別處理數據和指令，比如 `1+1=2` 這個運算，`+` 就是指令，會被放在「指令緩存」中，而輸入數字 `1` 則會被放在「數據緩存」裡。

因此，**我們要分開來看「數據緩存」和「指令緩存」的緩存命中率**。


### 如何提升數據緩存的命中率？

假設要遍歷二維數組，有以下兩種形式，雖然代碼執行結果是一樣，但你覺得哪種形式效率最高呢？為什麼高呢？

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/遍歷數組.png)

經過測試，形式一 `array[i][j]`  執行時間比形式二 `array[j][i]` 快好幾倍。

之所以有這麼大的差距，是因為二維數組 `array` 所佔用的內存是連續的，比如長度 `N` 的值是 `2` 的話，那麼內存中的數組元素的佈局順序是這樣的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/數組內存佈局順序.png)



形式一用 `array[i][j]`  訪問數組元素的順序，正是和內存中數組元素存放的順序一致。當 CPU 訪問 `array[0][0]` 時，由於該數據不在 Cache 中，於是會「順序」把跟隨其後的 3 個元素從內存中加載到 CPU Cache，這樣當 CPU 訪問後面的 3 個數組元素時，就能在 CPU Cache 中成功地找到數據，這意味著緩存命中率很高，緩存命中的數據不需要訪問內存，這便大大提高了代碼的性能。

而如果用形式二的 `array[j][i]` 來訪問，則訪問的順序就是：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/形式二訪問順序.png)


你可以看到，訪問的方式跳躍式的，而不是順序的，那麼如果 N 的數值很大，那麼操作 `array[j][i]` 時，是沒辦法把 `array[j+1][i]` 也讀入到 CPU Cache 中的，既然 `array[j+1][i]` 沒有讀取到 CPU Cache，那麼就需要從內存讀取該數據元素了。很明顯，這種不連續性、跳躍式訪問數據元素的方式，可能不能充分利用到了 CPU Cache 的特性，從而代碼的性能不高。


那訪問 `array[0][0]` 元素時，CPU 具體會一次從內存中加載多少元素到 CPU Cache 呢？這個問題，在前面我們也提到過，這跟 CPU Cache Line 有關，它表示 **CPU Cache 一次性能加載數據的大小**，可以在 Linux 裡通過 `coherency_line_size` 配置查看 它的大小，通常是 64 個字節。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/查看CPULine大小.png)


也就是說，當 CPU 訪問內存數據時，如果數據不在 CPU Cache 中，則會一次性會連續加載 64 字節大小的數據到 CPU Cache，那麼當訪問 `array[0][0]` 時，由於該元素不足 64 字節，於是就會往後**順序**讀取 `array[0][0]~array[0][15]` 到 CPU Cache 中。順序訪問的 `array[i][j]` 因為利用了這一特點，所以就會比跳躍式訪問的 `array[j][i]` 要快。

**因此，遇到這種遍歷數組的情況時，按照內存佈局順序訪問，將可以有效的利用 CPU Cache 帶來的好處，這樣我們代碼的性能就會得到很大的提升，**


### 如何提升指令緩存的命中率？

提升數據的緩存命中率的方式，是按照內存佈局順序訪問，那針對指令的緩存該如何提升呢？

我們以一個例子來看看，有一個元素為 0 到 100 之間隨機數字組成的一維數組：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/隨機數數組.png)

接下來，對這個數組做兩個操作：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CPU%E7%BC%93%E5%AD%98/%E6%8E%92%E5%BA%8Fand%E6%95%B0%E7%BB%84%E9%81%8D%E5%8E%86.png)

- 第一個操作，循環遍歷數組，把小於 50 的數組元素置為 0；
- 第二個操作，將數組排序；

那麼問題來了，你覺得先遍歷再排序速度快，還是先排序再遍歷速度快呢？



在回答這個問題之前，我們先了解 CPU 的**分支預測器**。對於 if 條件語句，意味著此時至少可以選擇跳轉到兩段不同的指令執行，也就是 if 還是 else 中的指令。那麼，**如果分支預測可以預測到接下來要執行 if 裡的指令，還是 else 指令的話，就可以「提前」把這些指令放在指令緩存中，這樣 CPU 可以直接從 Cache 讀取到指令，於是執行速度就會很快**。

當數組中的元素是隨機的，分支預測就無法有效工作，而當數組元素都是是順序的，分支預測器會動態地根據歷史命中數據對未來進行預測，這樣命中率就會很高。

因此，先排序再遍歷速度會更快，這是因為排序之後，數字是從小到大的，那麼前幾次循環命中 `if < 50` 的次數會比較多，於是分支預測就會緩存 `if` 裡的 `array[i] = 0` 指令到 Cache 中，後續 CPU 執行該指令就只需要從 Cache 讀取就好了。

如果你肯定代碼中的 `if` 中的表達式判斷為 `true` 的概率比較高，我們可以使用顯示分支預測工具，比如在 C/C++ 語言中編譯器提供了 `likely` 和 `unlikely` 這兩種宏，如果 `if` 條件為 `ture` 的概率大，則可以用 `likely` 宏把 `if` 裡的表達式包裹起來，反之用 `unlikely` 宏。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/CPU%E7%BC%93%E5%AD%98/likely.png)

實際上，CPU 自身的動態分支預測已經是比較準的了，所以只有當非常確信 CPU 預測的不準，且能夠知道實際的概率情況時，才建議使用這兩種宏。


### 如何提升多核 CPU 的緩存命中率？


在單核 CPU，雖然只能執行一個線程，但是操作系統給每個線程分配了一個時間片，時間片用完了，就調度下一個線程，於是各個線程就按時間片交替地佔用 CPU，從宏觀上看起來各個線程同時在執行。

而現代 CPU 都是多核心的，線程可能在不同 CPU 核心來回切換執行，這對 CPU Cache 不是有利的，雖然 L3 Cache 是多核心之間共享的，但是 L1 和 L2 Cache 都是每個核心獨有的，**如果一個線程在不同核心來回切換，各個核心的緩存命中率就會受到影響**，相反如果線程都在同一個核心上執行，那麼其數據的 L1 和 L2 Cache 的緩存命中率可以得到有效提高，緩存命中率高就意味著 CPU 可以減少訪問 內存的頻率。

當有多個同時執行「計算密集型」的線程，為了防止因為切換到不同的核心，而導致緩存命中率下降的問題，我們可以把**線程綁定在某一個 CPU 核心上**，這樣性能可以得到非常可觀的提升。

在 Linux 上提供了 `sched_setaffinity` 方法，來實現將線程綁定到某個 CPU 核心這一功能。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/操作系統/CPU緩存/sched_setaffinity.png)

---

## 總結

由於隨著計算機技術的發展，CPU 與 內存的訪問速度相差越來越多，如今差距已經高達好幾百倍了，所以 CPU 內部嵌入了 CPU Cache 組件，作為內存與 CPU 之間的緩存層，CPU Cache 由於離 CPU 核心很近，所以訪問速度也是非常快的，但由於所需材料成本比較高，它不像內存動輒幾個 GB 大小，而是僅有幾十 KB 到 MB 大小。

當 CPU 訪問數據的時候，先是訪問 CPU Cache，如果緩存命中的話，則直接返回數據，就不用每次都從內存讀取數據了。因此，緩存命中率越高，代碼的性能越好。

但需要注意的是，當 CPU 訪問數據時，如果 CPU Cache 沒有緩存該數據，則會從內存讀取數據，但是並不是隻讀一個數據，而是一次性讀取一塊一塊的數據存放到 CPU Cache 中，之後才會被 CPU 讀取。

內存地址映射到 CPU Cache 地址裡的策略有很多種，其中比較簡單是直接映射 Cache，它巧妙的把內存地址拆分成「索引 + 組標記 + 偏移量」的方式，使得我們可以將很大的內存地址，映射到很小的 CPU Cache 地址裡。

要想寫出讓 CPU 跑得更快的代碼，就需要寫出緩存命中率高的代碼，CPU L1 Cache 分為數據緩存和指令緩存，因而需要分別提高它們的緩存命中率：

- 對於數據緩存，我們在遍歷數據的時候，應該按照內存佈局的順序操作，這是因為 CPU Cache 是根據 CPU Cache Line 批量操作數據的，所以順序地操作連續內存數據時，性能能得到有效的提升；
- 對於指令緩存，有規律的條件分支語句能夠讓 CPU 的分支預測器發揮作用，進一步提高執行的效率；

另外，對於多核 CPU 系統，線程可能在不同 CPU 核心來回切換，這樣各個核心的緩存命中率就會受到影響，於是要想提高線程的緩存命中率，可以考慮把線程綁定 CPU 到某一個 CPU 核心。 

----

## 關注作者

分享個喜事，小林平日裡忙著輸出文章，今天收到一份特別的快遞，是 CSDN 寄來的獎狀。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20201017154037.jpg)

驕傲的說，你們關注的是 CSDN 首屆技術原創第一名的博主，以後簡歷又可以吹牛逼了

沒有啦，其實主要還是**謝謝你們不離不棄的支持**。


sao

*哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，歡迎微信搜索「小林coding」，關注後，回覆「網絡」再送你圖解網絡 PDF*