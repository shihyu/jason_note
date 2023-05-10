# 4.5 如何避免預讀失效和緩存汙染的問題？

大家好，我是小林。

上週群裡看到有位小夥伴面試時，被問到這兩個問題：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/操作系統/緩存/提問.png)

咋一看，以為是在問操作系統的問題，其實這兩個題目都是在問**如何改進 LRU 算法**。

因為傳統的 LRU 算法存在這兩個問題：

- **「預讀失效」導致緩存命中率下降（對應第一個題目）**
- **「緩存汙染」導致緩存命中率下降（對應第二個題目）**

Redis 的緩存淘汰算法則是通過**實現 LFU 算法**來避免「緩存汙染」而導致緩存命中率下降的問題（Redis 沒有預讀機制）。

MySQL 和 Linux 操作系統是通過**改進 LRU 算法**來避免「預讀失效和緩存汙染」而導致緩存命中率下降的問題。

這次，就重點講講 **MySQL 和 Linux 操作系統是如何改進 LRU 算法的？**

好了，開始發車，坐穩了！

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/操作系統/緩存/緩存汙染提綱.png)

## Linux 和 MySQL 的緩存

### Linux 操作系統的緩存

在應用程序讀取文件的數據的時候，Linux 操作系統是會對讀取的文件數據進行緩存的，會緩存在文件系統中的 **Page Cache**（如下圖中的頁緩存）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F/%E8%99%9A%E6%8B%9F%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F.png)

Page Cache 屬於內存空間裡的數據，由於內存訪問比磁盤訪問快很多，在下一次訪問相同的數據就不需要通過磁盤 I/O 了，命中緩存就直接返回數據即可。

因此，Page Cache 起到了加速訪問數據的作用。

### MySQL 的緩存

MySQL 的數據是存儲在磁盤裡的，為了提升數據庫的讀寫性能，Innodb 存儲引擎設計了一個**緩衝池**（Buffer Pool），Buffer Pool 屬於內存空間裡的數據。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/%E7%BC%93%E5%86%B2%E6%B1%A0.drawio.png)

有了緩衝池後：

- 當讀取數據時，如果數據存在於 Buffer Pool 中，客戶端就會直接讀取 Buffer Pool 中的數據，否則再去磁盤中讀取。
- 當修改數據時，首先是修改 Buffer Pool 中數據所在的頁，然後將其頁設置為髒頁，最後由後臺線程將髒頁寫入到磁盤。

## 傳統 LRU 是如何管理內存數據的？

Linux 的 Page Cache 和  MySQL 的 Buffer Pool 的大小是有限的，並不能無限的緩存數據，對於一些頻繁訪問的數據我們希望可以一直留在內存中，而一些很少訪問的數據希望可以在某些時機可以淘汰掉，從而保證內存不會因為滿了而導致無法再緩存新的數據，同時還能保證常用數據留在內存中。

要實現這個，最容易想到的就是 LRU（Least recently used）算法。

LRU 算法一般是用「鏈表」作為數據結構來實現的，鏈表頭部的數據是最近使用的，而鏈表末尾的數據是最久沒被使用的。那麼，當空間不夠了，就淘汰最久沒被使用的節點，也就是鏈表末尾的數據，從而騰出內存空間。

因為 Linux 的 Page Cache 和  MySQL 的 Buffer Pool 緩存的**基本數據單位都是頁（Page）單位**，所以**後續以「頁」名稱代替「數據」**。

傳統的 LRU 算法的實現思路是這樣的：

- 當訪問的頁在內存裡，就直接把該頁對應的 LRU 鏈表節點移動到鏈表的頭部。
- 當訪問的頁不在內存裡，除了要把該頁放入到 LRU 鏈表的頭部，還要淘汰 LRU 鏈表末尾的頁。

比如下圖，假設 LRU 鏈表長度為 5，LRU 鏈表從左到右有編號為 1，2，3，4，5 的頁。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lru.png)

如果訪問了 3 號頁，因為 3 號頁已經在內存了，所以把 3 號頁移動到鏈表頭部即可，表示最近被訪問了。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lru2.png)

而如果接下來，訪問了 8 號頁，因為 8 號頁不在內存裡，且 LRU 鏈表長度為 5，所以必須要淘汰數據，以騰出內存空間來緩存 8 號頁，於是就會淘汰末尾的 5 號頁，然後再將 8 號頁加入到頭部。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lru3.png)

傳統的 LRU 算法並沒有被 Linux 和 MySQL 使用，因為傳統的 LRU 算法無法避免下面這兩個問題：

- 預讀失效導致緩存命中率下降；
- 緩存汙染導致緩存命中率下降；

## 預讀失效，怎麼辦？

### 什麼是預讀機制？

Linux 操作系統為基於 Page Cache 的讀緩存機制提供**預讀機制**，一個例子是：

- 應用程序只想讀取磁盤上文件 A 的 offset 為 0-3KB 範圍內的數據，由於磁盤的基本讀寫單位為 block（4KB），於是操作系統至少會讀 0-4KB 的內容，這恰好可以在一個 page 中裝下。
- 但是操作系統出於空間局部性原理（靠近當前被訪問數據的數據，在未來很大概率會被訪問到），會選擇將磁盤塊 offset [4KB,8KB)、[8KB,12KB) 以及 [12KB,16KB) 都加載到內存，於是額外在內存中申請了 3 個 page；

下圖代表了操作系統的預讀機制：

![](https://img-blog.csdnimg.cn/img_convert/ae8252378169c8c14b8b9907983f7d8b.png)

上圖中，應用程序利用 read 系統調動讀取 4KB 數據，實際上內核使用預讀機制（ReadaHead） 機制完成了 16KB 數據的讀取，也就是通過一次磁盤順序讀將多個 Page 數據裝入 Page Cache。

這樣下次讀取 4KB 數據後面的數據的時候，就不用從磁盤讀取了，直接在 Page Cache 即可命中數據。因此，預讀機制帶來的好處就是**減少了 磁盤 I/O 次數，提高系統磁盤 I/O 吞吐量**。

MySQL Innodb 存儲引擎的 Buffer Pool 也有類似的預讀機制，MySQL 從磁盤加載頁時，會提前把它相鄰的頁一併加載進來，目的是為了減少磁盤 IO。

### 預讀失效會帶來什麼問題？

如果**這些被提前加載進來的頁，並沒有被訪問**，相當於這個預讀工作是白做了，這個就是**預讀失效**。

如果使用傳統的 LRU 算法，就會把「預讀頁」放到 LRU 鏈表頭部，而當內存空間不夠的時候，還需要把末尾的頁淘汰掉。

如果這些「預讀頁」如果一直不會被訪問到，就會出現一個很奇怪的問題，**不會被訪問的預讀頁卻佔用了 LRU 鏈表前排的位置，而末尾淘汰的頁，可能是熱點數據，這樣就大大降低了緩存命中率** 。

### 如何避免預讀失效造成的影響？

我們不能因為害怕預讀失效，而將預讀機制去掉，大部分情況下，空間局部性原理還是成立的。

要避免預讀失效帶來影響，最好就是**讓預讀頁停留在內存裡的時間要儘可能的短，讓真正被訪問的頁才移動到 LRU 鏈表的頭部，從而保證真正被讀取的熱數據留在內存裡的時間儘可能長**。

那到底怎麼才能避免呢？

Linux 操作系統和 MySQL Innodb 通過改進傳統 LRU 鏈表來避免預讀失效帶來的影響，具體的改進分別如下：

- Linux 操作系統實現兩個了 LRU 鏈表：**活躍 LRU 鏈表（active_list）和非活躍 LRU 鏈表（inactive_list）**；
- MySQL 的 Innodb 存儲引擎是在一個 LRU 鏈表上劃分來 2 個區域：**young 區域 和 old 區域**。

這兩個改進方式，設計思想都是類似的，**都是將數據分為了冷數據和熱數據，然後分別進行 LRU 算法**。不再像傳統的 LRU 算法那樣，所有數據都只用一個 LRU 算法管理。

接下來，具體聊聊 Linux 和 MySQL 是如何避免預讀失效帶來的影響？

> Linux 是如何避免預讀失效帶來的影響？

Linux 操作系統實現兩個了 LRU 鏈表：**活躍 LRU 鏈表（active_list）和非活躍 LRU 鏈表（inactive_list）**。

- **active list** 活躍內存頁鏈表，這裡存放的是最近被訪問過（活躍）的內存頁；
- **inactive list** 不活躍內存頁鏈表，這裡存放的是很少被訪問（非活躍）的內存頁；

有了這兩個 LRU 鏈表後，**預讀頁就只需要加入到 inactive list 區域的頭部，當頁被真正訪問的時候，才將頁插入 active list 的頭部**。如果預讀的頁一直沒有被訪問，就會從 inactive list 移除，這樣就不會影響 active list 中的熱點數據。

接下來，給大家舉個例子。

假設 active list 和 inactive list 的長度為 5，目前內存中已經有如下 10 個頁：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/操作系統/緩存/active_inactive_list.drawio.png)

現在有個編號為 20 的頁被預讀了，這個頁只會被插入到 inactive list 的頭部，而 inactive list 末尾的頁（10號）會被淘汰掉。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/操作系統/緩存/active_inactive_list1.drawio.png)

**即使編號為 20 的預讀頁一直不會被訪問，它也沒有佔用到  active list 的位置**，而且還會比 active list 中的頁更早被淘汰出去。

如果 20 號頁被預讀後，立刻被訪問了，那麼就會將它插入到  active list 的頭部， active list 末尾的頁（5號），會被**降級**到 inactive list ，作為 inactive list 的頭部，這個過程並不會有數據被淘汰。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/操作系統/緩存/active_inactive_list2.drawio.png)

> MySQL 是如何避免預讀失效帶來的影響？

MySQL 的 Innodb 存儲引擎是在一個 LRU 鏈表上劃分來 2 個區域，**young 區域 和 old 區域**。

young 區域在 LRU 鏈表的前半部分，old 區域則是在後半部分，這兩個區域都有各自的頭和尾節點，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/young%2Bold.png)

young 區域與 old 區域在 LRU 鏈表中的佔比關係並不是一比一的關係，而是是 7 比 3 （默認比例）的關係。

**劃分這兩個區域後，預讀的頁就只需要加入到 old 區域的頭部，當頁被真正訪問的時候，才將頁插入 young 區域的頭部**。如果預讀的頁一直沒有被訪問，就會從 old 區域移除，這樣就不會影響 young 區域中的熱點數據。

接下來，給大家舉個例子。

假設有一個長度為 10 的 LRU 鏈表，其中 young 區域佔比 70 %，old 區域佔比 30 %。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lrutwo.drawio.png)

現在有個編號為 20 的頁被預讀了，這個頁只會被插入到 old 區域頭部，而 old 區域末尾的頁（10號）會被淘汰掉。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lrutwo2.png)

如果 20 號頁一直不會被訪問，它也沒有佔用到 young 區域的位置，而且還會比 young 區域的數據更早被淘汰出去。

如果 20 號頁被預讀後，立刻被訪問了，那麼就會將它插入到 young 區域的頭部，young 區域末尾的頁（7號），會被擠到 old 區域，作為 old 區域的頭部，這個過程並不會有頁被淘汰。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lrutwo3.png)

## 緩存汙染，怎麼辦？

### 什麼是緩存汙染？

雖然 Linux （實現兩個 LRU 鏈表）和 MySQL （劃分兩個區域）通過改進傳統的 LRU 數據結構，避免了預讀失效帶來的影響。

但是如果還是使用「只要數據被訪問一次，就將數據加入到活躍 LRU 鏈表頭部（或者 young 區域）」這種方式的話，那麼**還存在緩存汙染的問題**。

當我們在批量讀取數據的時候，由於數據被訪問了一次，這些大量數據都會被加入到「活躍 LRU 鏈表」裡，然後之前緩存在活躍 LRU 鏈表（或者 young 區域）裡的熱點數據全部都被淘汰了，**如果這些大量的數據在很長一段時間都不會被訪問的話，那麼整個活躍 LRU 鏈表（或者 young 區域）就被汙染了**。

### 緩存汙染會帶來什麼問題？

緩存汙染帶來的影響就是很致命的，等這些熱數據又被再次訪問的時候，由於緩存未命中，就會產生大量的磁盤 I/O，系統性能就會急劇下降。

我以 MySQL 舉例子，Linux 發生緩存汙染的現象也是類似。

當某一個 SQL 語句**掃描了大量的數據**時，在 Buffer Pool 空間比較有限的情況下，可能會將 **Buffer Pool 裡的所有頁都替換出去，導致大量熱數據被淘汰了**，等這些熱數據又被再次訪問的時候，由於緩存未命中，就會產生大量的磁盤 I/O，MySQL 性能就會急劇下降。

注意， 緩存汙染並不只是查詢語句查詢出了大量的數據才出現的問題，即使查詢出來的結果集很小，也會造成緩存汙染。

比如，在一個數據量非常大的表，執行了這條語句：

```sql
select * from t_user where name like "%xiaolin%";
```

可能這個查詢出來的結果就幾條記錄，但是由於這條語句會發生索引失效，所以這個查詢過程是全表掃描的，接著會發生如下的過程：

- 從磁盤讀到的頁加入到 LRU 鏈表的 old 區域頭部；
- 當從頁裡讀取行記錄時，也就是**頁被訪問的時候，就要將該頁放到 young 區域頭部**；
- 接下來拿行記錄的 name 字段和字符串 xiaolin 進行模糊匹配，如果符合條件，就加入到結果集裡；
- 如此往復，直到掃描完表中的所有記錄。

經過這一番折騰，由於這條 SQL 語句訪問的頁非常多，每訪問一個頁，都會將其加入 young 區域頭部，那麼**原本 young 區域的熱點數據都會被替換掉，導致緩存命中率下降**。那些在批量掃描時，而被加入到 young 區域的頁，如果在很長一段時間都不會再被訪問的話，那麼就汙染了 young 區域。

舉個例子，假設需要批量掃描：21，22，23，24，25 這五個頁，這些頁都會被逐一訪問（讀取頁裡的記錄）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lruthree.drawio.png)

在批量訪問這些頁的時候，會被逐一插入到 young 區域頭部。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lruthree1.png)

可以看到，原本在 young 區域的 6 和 7 號頁都被淘汰了，而批量掃描的頁基本佔滿了 young 區域，如果這些頁在很長一段時間都不會被訪問，那麼就對 young 區域造成了汙染。

如果 6 和 7 號頁是熱點數據，那麼在被淘汰後，後續有 SQL 再次讀取  6 和 7 號頁時，由於緩存未命中，就要從磁盤中讀取了，降低了 MySQL 的性能，這就是緩存汙染帶來的影響。

### 怎麼避免緩存汙染造成的影響？

前面的 LRU 算法只要數據被訪問一次，就將數據加入活躍 LRU 鏈表（或者 young 區域），**這種 LRU 算法進入活躍 LRU 鏈表的門檻太低了**！正式因為門檻太低，才導致在發生緩存汙染的時候，很容就將原本在活躍 LRU 鏈表裡的熱點數據淘汰了。

所以，**只要我們提高進入到活躍 LRU 鏈表（或者 young 區域）的門檻，就能有效地保證活躍 LRU 鏈表（或者 young 區域）裡的熱點數據不會被輕易替換掉**。

Linux 操作系統和 MySQL Innodb 存儲引擎分別是這樣提高門檻的：

- **Linux 操作系統**：在內存頁被訪問**第二次**的時候，才將頁從 inactive list 升級到 active list 裡。
- **MySQL Innodb**：在內存頁被訪問**第二次**的時候，並不會馬上將該頁從 old 區域升級到 young 區域，因為還要進行**停留在 old 區域的時間判斷**：
  - 如果第二次的訪問時間與第一次訪問的時間**在 1 秒內**（默認值），那麼該頁就**不會**被從 old 區域升級到 young 區域；
  - 如果第二次的訪問時間與第一次訪問的時間**超過 1 秒**，那麼該頁就**會**從 old 區域升級到 young 區域；

提高了進入活躍 LRU 鏈表（或者 young 區域）的門檻後，就很好了避免緩存汙染帶來的影響。

在批量讀取數據時候，**如果這些大量數據只會被訪問一次，那麼它們就不會進入到活躍 LRU 鏈表（或者 young 區域）**，也就不會把熱點數據淘汰，只會待在非活躍 LRU 鏈表（或者 old 區域）中，後續很快也會被淘汰。

## 總結

傳統的 LRU 算法法無法避免下面這兩個問題：

- 預讀失效導致緩存命中率下降；
- 緩存汙染導致緩存命中率下降；

為了避免「預讀失效」造成的影響，Linux 和 MySQL 對傳統的 LRU 鏈表做了改進：

- Linux 操作系統實現兩個了 LRU 鏈表：**活躍 LRU 鏈表（active list）和非活躍 LRU 鏈表（inactive list）**。
- MySQL  Innodb 存儲引擎是在一個 LRU 鏈表上劃分來 2 個區域：**young 區域 和 old 區域**。

但是如果還是使用「只要數據被訪問一次，就將數據加入到活躍 LRU 鏈表頭部（或者 young 區域）」這種方式的話，那麼**還存在緩存汙染的問題**。

為了避免「緩存汙染」造成的影響，Linux 操作系統和 MySQL Innodb 存儲引擎分別提高了升級為熱點數據的門檻：

- Linux 操作系統：在內存頁被訪問**第二次**的時候，才將頁從 inactive list 升級到 active list 裡。
- MySQL Innodb：在內存頁被訪問**第二次**的時候，並不會馬上將該頁從 old 區域升級到 young 區域，因為還要進行**停留在 old 區域的時間判斷**：
  - 如果第二次的訪問時間與第一次訪問的時間**在 1 秒內**（默認值），那麼該頁就**不會**被從 old 區域升級到 young 區域；
  - 如果第二次的訪問時間與第一次訪問的時間**超過 1 秒**，那麼該頁就**會**從 old 區域升級到 young 區域；

通過提高了進入 active list  （或者 young 區域）的門檻後，就很好了避免緩存汙染帶來的影響。

完！

------

***哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，歡迎微信搜索「小林coding」，關注後，回覆「網絡」再送你圖解網絡 PDF***

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

