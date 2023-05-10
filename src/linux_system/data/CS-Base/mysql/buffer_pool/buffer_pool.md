# 揭開 Buffer Pool  的面紗

大家好，我是小林。

今天就聊 MySQL 的 Buffer Pool，發車！

![](https://img-blog.csdnimg.cn/e5a23e5c53ef471b947b5007866229fe.png#pic_center)



## 為什麼要有 Buffer Pool？

雖然說 MySQL 的數據是存儲在磁盤裡的，但是也不能每次都從磁盤裡面讀取數據，這樣性能是極差的。

要想提升查詢性能，加個緩存就行了嘛。所以，當數據從磁盤中取出後，緩存內存中，下次查詢同樣的數據的時候，直接從內存中讀取。

為此，Innodb 存儲引擎設計了一個**緩衝池（*Buffer Pool*）**，來提高數據庫的讀寫性能。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/緩衝池.drawio.png)

有了緩衝池後：

- 當讀取數據時，如果數據存在於  Buffer Pool 中，客戶端就會直接讀取  Buffer Pool 中的數據，否則再去磁盤中讀取。
- 當修改數據時，首先是修改  Buffer Pool  中數據所在的頁，然後將其頁設置為髒頁，最後由後臺線程將髒頁寫入到磁盤。

### Buffer Pool 有多大？

Buffer Pool 是在 MySQL 啟動的時候，向操作系統申請的一片連續的內存空間，默認配置下 Buffer Pool 只有 `128MB` 。

可以通過調整 `innodb_buffer_pool_size` 參數來設置 Buffer Pool 的大小，一般建議設置成可用物理內存的 60%~80%。

### Buffer Pool 緩存什麼？

InnoDB 會把存儲的數據劃分為若干個「頁」，以頁作為磁盤和內存交互的基本單位，一個頁的默認大小為 16KB。因此，Buffer Pool  同樣需要按「頁」來劃分。

在 MySQL 啟動的時候，**InnoDB 會為 Buffer Pool 申請一片連續的內存空間，然後按照默認的`16KB`的大小劃分出一個個的頁， Buffer Pool 中的頁就叫做緩存頁**。此時這些緩存頁都是空閒的，之後隨著程序的運行，才會有磁盤上的頁被緩存到 Buffer Pool 中。

所以，MySQL 剛啟動的時候，你會觀察到使用的虛擬內存空間很大，而使用到的物理內存空間卻很小，這是因為只有這些虛擬內存被訪問後，操作系統才會觸發缺頁中斷，接著將虛擬地址和物理地址建立映射關係。

Buffer Pool  除了緩存「索引頁」和「數據頁」，還包括了 undo 頁，插入緩存、自適應哈希索引、鎖信息等等。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/bufferpool內容.drawio.png)

為了更好的管理這些在 Buffer Pool 中的緩存頁，InnoDB 為每一個緩存頁都創建了一個**控制塊**，控制塊信息包括「緩存頁的表空間、頁號、緩存頁地址、鏈表節點」等等。

控制塊也是佔有內存空間的，它是放在 Buffer Pool 的最前面，接著才是緩存頁，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/緩存頁.drawio.png)

上圖中控制塊和緩存頁之間灰色部分稱為碎片空間。

>  為什麼會有碎片空間呢？

你想想啊，每一個控制塊都對應一個緩存頁，那在分配足夠多的控制塊和緩存頁後，可能剩餘的那點兒空間不夠一對控制塊和緩存頁的大小，自然就用不到嘍，這個用不到的那點兒內存空間就被稱為碎片了。

當然，如果你把 Buffer Pool 的大小設置的剛剛好的話，也可能不會產生碎片。

> 查詢一條記錄，就只需要緩衝一條記錄嗎？

不是的。

當我們查詢一條記錄時，InnoDB 是會把整個頁的數據加載到 Buffer Pool 中，因為，通過索引只能定位到磁盤中的頁，而不能定位到頁中的一條記錄。將頁加載到 Buffer Pool 後，再通過頁裡的頁目錄去定位到某條具體的記錄。

關於頁結構長什麼樣和索引怎麼查詢數據的問題可以在這篇找到答案：[換一個角度看 B+ 樹](https://mp.weixin.qq.com/s/A5gNVXMNE-iIlY3oofXtLw)

## 如何管理 Buffer Pool？

### 如何管理空閒頁？

Buffer Pool 是一片連續的內存空間，當 MySQL 運行一段時間後，這片連續的內存空間中的緩存頁既有空閒的，也有被使用的。

那當我們從磁盤讀取數據的時候，總不能通過遍歷這一片連續的內存空間來找到空閒的緩存頁吧，這樣效率太低了。

所以，為了能夠快速找到空閒的緩存頁，可以使用鏈表結構，將空閒緩存頁的「控制塊」作為鏈表的節點，這個鏈表稱為 **Free 鏈表**（空閒鏈表）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/freelist.drawio.png)

Free 鏈表上除了有控制塊，還有一個頭節點，該頭節點包含鏈表的頭節點地址，尾節點地址，以及當前鏈表中節點的數量等信息。

Free 鏈表節點是一個一個的控制塊，而每個控制塊包含著對應緩存頁的地址，所以相當於 Free 鏈表節點都對應一個空閒的緩存頁。

有了 Free 鏈表後，每當需要從磁盤中加載一個頁到 Buffer Pool 中時，就從 Free鏈表中取一個空閒的緩存頁，並且把該緩存頁對應的控制塊的信息填上，然後把該緩存頁對應的控制塊從 Free 鏈表中移除。

### 如何管理髒頁？

設計 Buffer Pool 除了能提高讀性能，還能提高寫性能，也就是更新數據的時候，不需要每次都要寫入磁盤，而是將 Buffer Pool 對應的緩存頁標記為**髒頁**，然後再由後臺線程將髒頁寫入到磁盤。

那為了能快速知道哪些緩存頁是髒的，於是就設計出 **Flush 鏈表**，它跟 Free 鏈表類似的，鏈表的節點也是控制塊，區別在於 Flush 鏈表的元素都是髒頁。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/Flush.drawio.png)

有了 Flush 鏈表後，後臺線程就可以遍歷 Flush 鏈表，將髒頁寫入到磁盤。

### 如何提高緩存命中率？

Buffer Pool  的大小是有限的，對於一些頻繁訪問的數據我們希望可以一直留在 Buffer Pool 中，而一些很少訪問的數據希望可以在某些時機可以淘汰掉，從而保證 Buffer Pool  不會因為滿了而導致無法再緩存新的數據，同時還能保證常用數據留在 Buffer Pool 中。

要實現這個，最容易想到的就是 LRU（Least recently used）算法。

該算法的思路是，鏈表頭部的節點是最近使用的，而鏈表末尾的節點是最久沒被使用的。那麼，當空間不夠了，就淘汰最久沒被使用的節點，從而騰出空間。

簡單的 LRU 算法的實現思路是這樣的：

- 當訪問的頁在 Buffer Pool  裡，就直接把該頁對應的 LRU 鏈表節點移動到鏈表的頭部。
- 當訪問的頁不在 Buffer Pool 裡，除了要把頁放入到 LRU 鏈表的頭部，還要淘汰  LRU 鏈表末尾的節點。

比如下圖，假設 LRU 鏈表長度為 5，LRU 鏈表從左到右有 1，2，3，4，5 的頁。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lru.png)

如果訪問了 3 號的頁，因為 3 號頁在 Buffer Pool 裡，所以把 3 號頁移動到頭部即可。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lru2.png)

而如果接下來，訪問了 8 號頁，因為 8 號頁不在 Buffer Pool  裡，所以需要先淘汰末尾的 5 號頁，然後再將 8 號頁加入到頭部。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lru3.png)

到這裡我們可以知道，Buffer Pool 裡有三種頁和鏈表來管理數據。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/bufferpoll_page.png)

圖中：

- Free Page（空閒頁），表示此頁未被使用，位於 Free 鏈表；
- Clean Page（乾淨頁），表示此頁已被使用，但是頁面未發生修改，位於LRU 鏈表。
- Dirty Page（髒頁），表示此頁「已被使用」且「已經被修改」，其數據和磁盤上的數據已經不一致。當髒頁上的數據寫入磁盤後，內存數據和磁盤數據一致，那麼該頁就變成了乾淨頁。髒頁同時存在於 LRU 鏈表和 Flush 鏈表。

簡單的 LRU 算法並沒有被  MySQL 使用，因為簡單的 LRU 算法無法避免下面這兩個問題：

- 預讀失效；
-  Buffer Pool  汙染；

> 什麼是預讀失效？

先來說說 MySQL 的預讀機制。程序是有空間局部性的，靠近當前被訪問數據的數據，在未來很大概率會被訪問到。

所以，MySQL 在加載數據頁時，會提前把它相鄰的數據頁一併加載進來，目的是為了減少磁盤 IO。

但是可能這些**被提前加載進來的數據頁，並沒有被訪問**，相當於這個預讀是白做了，這個就是**預讀失效**。

如果使用簡單的 LRU 算法，就會把預讀頁放到 LRU 鏈表頭部，而當  Buffer Pool空間不夠的時候，還需要把末尾的頁淘汰掉。

如果這些預讀頁如果一直不會被訪問到，就會出現一個很奇怪的問題，不會被訪問的預讀頁卻佔用了 LRU 鏈表前排的位置，而末尾淘汰的頁，可能是頻繁訪問的頁，這樣就大大降低了緩存命中率。

> 怎麼解決預讀失效而導致緩存命中率降低的問題？

我們不能因為害怕預讀失效，而將預讀機制去掉，大部分情況下，局部性原理還是成立的。

要避免預讀失效帶來影響，最好就是**讓預讀的頁停留在 Buffer Pool 裡的時間要儘可能的短，讓真正被訪問的頁才移動到 LRU 鏈表的頭部，從而保證真正被讀取的熱數據留在 Buffer Pool 裡的時間儘可能長**。

那到底怎麼才能避免呢？

MySQL 是這樣做的，它改進了 LRU 算法，將 LRU 劃分了 2 個區域：**old 區域 和 young 區域**。

young 區域在 LRU 鏈表的前半部分，old 區域則是在後半部分，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/young%2Bold.png)

old 區域佔整個 LRU 鏈表長度的比例可以通過 `innodb_old_blocks_pct` 參數來設置，默認是 37，代表整個 LRU 鏈表中 young 區域與 old 區域比例是 63:37。

**劃分這兩個區域後，預讀的頁就只需要加入到 old 區域的頭部，當頁被真正訪問的時候，才將頁插入 young 區域的頭部**。如果預讀的頁一直沒有被訪問，就會從 old 區域移除，這樣就不會影響 young 區域中的熱點數據。

接下來，給大家舉個例子。

假設有一個長度為 10 的 LRU 鏈表，其中 young 區域佔比 70 %，old 區域佔比 30 %。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lrutwo.drawio.png)

現在有個編號為 20 的頁被預讀了，這個頁只會被插入到  old 區域頭部，而 old 區域末尾的頁（10號）會被淘汰掉。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lrutwo2.png)

如果 20 號頁一直不會被訪問，它也沒有佔用到 young 區域的位置，而且還會比 young 區域的數據更早被淘汰出去。

如果 20 號頁被預讀後，立刻被訪問了，那麼就會將它插入到 young 區域的頭部，young 區域末尾的頁（7號），會被擠到 old 區域，作為 old 區域的頭部，這個過程並不會有頁被淘汰。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lrutwo3.png)

雖然通過劃分 old 區域 和 young 區域避免了預讀失效帶來的影響，但是還有個問題無法解決，那就是  Buffer Pool  汙染的問題。

> 什麼是  Buffer Pool  汙染？

當某一個 SQL 語句**掃描了大量的數據**時，在  Buffer Pool 空間比較有限的情況下，可能會將 **Buffer Pool 裡的所有頁都替換出去，導致大量熱數據被淘汰了**，等這些熱數據又被再次訪問的時候，由於緩存未命中，就會產生大量的磁盤 IO，MySQL 性能就會急劇下降，這個過程被稱為 **Buffer Pool  汙染**。

注意， Buffer Pool  汙染並不只是查詢語句查詢出了大量的數據才出現的問題，即使查詢出來的結果集很小，也會造成 Buffer Pool  汙染。

比如，在一個數據量非常大的表，執行了這條語句：

```sql
select * from t_user where name like "%xiaolin%";
```

可能這個查詢出來的結果就幾條記錄，但是由於這條語句會發生索引失效，所以這個查詢過程是全表掃描的，接著會發生如下的過程：

- 從磁盤讀到的頁加入到 LRU 鏈表的 old 區域頭部；
- 當從頁裡讀取行記錄時，也就是頁被訪問的時候，就要將該頁放到 young 區域頭部；
- 接下來拿行記錄的 name 字段和字符串 xiaolin 進行模糊匹配，如果符合條件，就加入到結果集裡；
- 如此往復，直到掃描完表中的所有記錄。

經過這一番折騰，原本 young 區域的熱點數據都會被替換掉。

舉個例子，假設需要批量掃描：21，22，23，24，25 這五個頁，這些頁都會被逐一訪問（讀取頁裡的記錄）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lruthree.drawio.png)

在批量訪問這些數據的時候，會被逐一插入到 young 區域頭部。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/lruthree1.png)

可以看到，原本在 young 區域的熱點數據 6 和 7 號頁都被淘汰了，這就是  Buffer Pool  汙染的問題。

> 怎麼解決出現   Buffer Pool  汙染而導致緩存命中率下降的問題？

像前面這種全表掃描的查詢，很多緩衝頁其實只會被訪問一次，但是它卻只因為被訪問了一次而進入到 young 區域，從而導致熱點數據被替換了。

LRU 鏈表中 young 區域就是熱點數據，只要我們提高進入到 young 區域的門檻，就能有效地保證 young 區域裡的熱點數據不會被替換掉。

MySQL 是這樣做的，進入到 young 區域條件增加了一個**停留在 old 區域的時間判斷**。

具體是這樣做的，在對某個處在 old 區域的緩存頁進行第一次訪問時，就在它對應的控制塊中記錄下來這個訪問時間：

- 如果後續的訪問時間與第一次訪問的時間**在某個時間間隔內**，那麼**該緩存頁就不會被從 old 區域移動到 young 區域的頭部**；
- 如果後續的訪問時間與第一次訪問的時間**不在某個時間間隔內**，那麼**該緩存頁移動到 young 區域的頭部**；

這個間隔時間是由 `innodb_old_blocks_time` 控制的，默認是 1000 ms。

也就說，**只有同時滿足「被訪問」與「在 old 區域停留時間超過 1 秒」兩個條件，才會被插入到 young 區域頭部**，這樣就解決了 Buffer Pool  汙染的問題 。

另外，MySQL 針對 young 區域其實做了一個優化，為了防止 young 區域節點頻繁移動到頭部。young 區域前面 1/4 被訪問不會移動到鏈表頭部，只有後面的 3/4被訪問了才會。

### 髒頁什麼時候會被刷入磁盤？

引入了 Buffer Pool  後，當修改數據時，首先是修改  Buffer Pool  中數據所在的頁，然後將其頁設置為髒頁，但是磁盤中還是原數據。

因此，髒頁需要被刷入磁盤，保證緩存和磁盤數據一致，但是若每次修改數據都刷入磁盤，則性能會很差，因此一般都會在一定時機進行批量刷盤。

可能大家擔心，如果在髒頁還沒有來得及刷入到磁盤時，MySQL 宕機了，不就丟失數據了嗎？

這個不用擔心，InnoDB 的更新操作採用的是 Write Ahead Log 策略，即先寫日誌，再寫入磁盤，通過 redo log 日誌讓 MySQL 擁有了崩潰恢復能力。

下面幾種情況會觸發髒頁的刷新：

- 當 redo log 日誌滿了的情況下，會主動觸發髒頁刷新到磁盤；
- Buffer Pool 空間不足時，需要將一部分數據頁淘汰掉，如果淘汰的是髒頁，需要先將髒頁同步到磁盤；
- MySQL 認為空閒時，後臺線程回定期將適量的髒頁刷入到磁盤；
- MySQL 正常關閉之前，會把所有的髒頁刷入到磁盤；

在我們開啟了慢 SQL 監控後，如果你發現**「偶爾」會出現一些用時稍長的 SQL**，這可能是因為髒頁在刷新到磁盤時可能會給數據庫帶來性能開銷，導致數據庫操作抖動。

如果間斷出現這種現象，就需要調大 Buffer Pool 空間或 redo log 日誌的大小。

## 總結

Innodb 存儲引擎設計了一個**緩衝池（*Buffer Pool*）**，來提高數據庫的讀寫性能。

Buffer Pool 以頁為單位緩衝數據，可以通過 `innodb_buffer_pool_size` 參數調整緩衝池的大小，默認是 128 M。

Innodb 通過三種鏈表來管理緩頁：

- Free List （空閒頁鏈表），管理空閒頁；
- Flush List （髒頁鏈表），管理髒頁；
- LRU List，管理髒頁+乾淨頁，將最近且經常查詢的數據緩存在其中，而不常查詢的數據就淘汰出去。；

InnoDB 對 LRU 做了一些優化，我們熟悉的 LRU 算法通常是將最近查詢的數據放到 LRU 鏈表的頭部，而 InnoDB 做 2 點優化：

- 將 LRU 鏈表 分為**young 和 old 兩個區域**，加入緩衝池的頁，優先插入 old 區域；頁被訪問時，才進入 young 區域，目的是為瞭解決預讀失效的問題。
- 當**「頁被訪問」且「 old 區域停留時間超過 `innodb_old_blocks_time` 閾值（默認為1秒）」**時，才會將頁插入到 young 區域，否則還是插入到 old 區域，目的是為瞭解決批量數據訪問，大量熱數據淘汰的問題。

可以通過調整 `innodb_old_blocks_pct` 參數，設置  young 區域和 old 區域比例。

在開啟了慢 SQL 監控後，如果你發現「偶爾」會出現一些用時稍長的 SQL，這可因為髒頁在刷新到磁盤時導致數據庫性能抖動。如果在很短的時間出現這種現象，就需要調大 Buffer Pool 空間或 redo log 日誌的大小。

----

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

















