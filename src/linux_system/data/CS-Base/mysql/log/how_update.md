# MySQL 日誌：undo log、redo log、binlog 有什麼用？

大家好，我是小林。

從這篇「[執行一條 SQL 查詢語句，期間發生了什麼？](https://xiaolincoding.com/mysql/base/how_select.html)」中，我們知道了一條查詢語句經歷的過程，這屬於「讀」一條記錄的過程，如下圖：

![查詢語句執行流程](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/sql%E6%89%A7%E8%A1%8C%E8%BF%87%E7%A8%8B/mysql%E6%9F%A5%E8%AF%A2%E6%B5%81%E7%A8%8B.png)

那麼，**執行一條 update 語句，期間發生了什麼？**，比如這一條 update 語句：

```sql
UPDATE t_user SET name = 'xiaolin' WHERE id = 1;
```

查詢語句的那一套流程，更新語句也是同樣會走一遍：

- 客戶端先通過連接器建立連接，連接器自會判斷用戶身份；
- 因為這是一條 update 語句，所以不需要經過查詢緩存，但是表上有更新語句，是會把整個表的查詢緩存清空的，所以說查詢緩存很雞肋，在 MySQL 8.0 就被移除這個功能了；
- 解析器會通過詞法分析識別出關鍵字 update，表名等等，構建出語法樹，接著還會做語法分析，判斷輸入的語句是否符合 MySQL 語法；
- 預處理器會判斷表和字段是否存在；
- 優化器確定執行計劃，因為 where 條件中的 id 是主鍵索引，所以決定要使用 id 這個索引；
- 執行器負責具體執行，找到這一行，然後更新。

不過，更新語句的流程會涉及到  undo log（回滾日誌）、redo log（重做日誌） 、binlog （歸檔日誌）這三種日誌：

- **undo log（回滾日誌）**：是 Innodb 存儲引擎層生成的日誌，實現了事務中的**原子性**，主要**用於事務回滾和 MVCC**。
- **redo log（重做日誌）**：是 Innodb 存儲引擎層生成的日誌，實現了事務中的**持久性**，主要**用於掉電等故障恢復**；
- **binlog （歸檔日誌）**：是 Server 層生成的日誌，主要**用於數據備份和主從複製**；

所以這次就帶著這個問題，看看這三種日誌是怎麼工作的。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/提綱.png)

## 為什麼需要 undo log？

我們在執行執行一條“增刪改”語句的時候，雖然沒有輸入 begin 開啟事務和 commit 提交事務，但是 MySQL 會**隱式開啟事務**來執行“增刪改”語句的，執行完就自動提交事務的，這樣就保證了執行完“增刪改”語句後，我們可以及時在數據庫表看到“增刪改”的結果了。

執行一條語句是否自動提交事務，是由 `autocommit` 參數決定的，默認是開啟。所以，執行一條 update 語句也是會使用事務的。

那麼，考慮一個問題。一個事務在執行過程中，在還沒有提交事務之前，如果MySQL 發生了崩潰，要怎麼回滾到事務之前的數據呢？

如果我們每次在事務執行過程中，都記錄下回滾時需要的信息到一個日誌裡，那麼在事務執行中途發生了 MySQL 崩潰後，就不用擔心無法回滾到事務之前的數據，我們可以通過這個日誌回滾到事務之前的數據。

實現這一機制就是  **undo log（回滾日誌），它保證了事務的 [ACID 特性](https://xiaolincoding.com/mysql/transaction/mvcc.html#%E4%BA%8B%E5%8A%A1%E6%9C%89%E5%93%AA%E4%BA%9B%E7%89%B9%E6%80%A7)中的原子性（Atomicity）**。

undo log 是一種用於撤銷回退的日誌。在事務沒提交之前，MySQL 會先記錄更新前的數據到 undo log 日誌文件裡面，當事務回滾時，可以利用 undo log 來進行回滾。如下圖：

![回滾事務](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/回滾事務.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

每當 InnoDB 引擎對一條記錄進行操作（修改、刪除、新增）時，要把回滾時需要的信息都記錄到 undo log 裡，比如：

- 在**插入**一條記錄時，要把這條記錄的主鍵值記下來，這樣之後回滾時只需要把這個主鍵值對應的記錄**刪掉**就好了；
- 在**刪除**一條記錄時，要把這條記錄中的內容都記下來，這樣之後回滾時再把由這些內容組成的記錄**插入**到表中就好了；
- 在**更新**一條記錄時，要把被更新的列的舊值記下來，這樣之後回滾時再把這些列**更新為舊值**就好了。

在發生回滾時，就讀取 undo log 裡的數據，然後做原先相反操作。比如當 delete 一條記錄時，undo log 中會把記錄中的內容都記下來，然後執行回滾操作的時候，就讀取 undo log 裡的數據，然後進行 insert 操作。

不同的操作，需要記錄的內容也是不同的，所以不同類型的操作（修改、刪除、新增）產生的 undo log 的格式也是不同的，具體的每一個操作的 undo log 的格式我就不詳細介紹了，感興趣的可以自己去查查。

一條記錄的每一次更新操作產生的 undo log 格式都有一個 roll_pointer 指針和一個 trx_id 事務id：

- 通過 trx_id 可以知道該記錄是被哪個事務修改的；
- 通過 roll_pointer 指針可以將這些 undo log 串成一個鏈表，這個鏈表就被稱為版本鏈；

版本鏈如下圖：

![版本鏈](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/版本鏈.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

另外，**undo log 還有一個作用，通過 ReadView + undo log 實現 MVCC（多版本併發控制）**。

對於「讀提交」和「可重複讀」隔離級別的事務來說，它們的快照讀（普通 select 語句）是通過 Read View  + undo log 來實現的，它們的區別在於創建 Read View 的時機不同：

- 「讀提交」隔離級別是在每個 select 都會生成一個新的 Read View，也意味著，事務期間的多次讀取同一條數據，前後兩次讀的數據可能會出現不一致，因為可能這期間另外一個事務修改了該記錄，並提交了事務。
- 「可重複讀」隔離級別是啟動事務時生成一個 Read View，然後整個事務期間都在用這個 Read View，這樣就保證了在事務期間讀到的數據都是事務啟動前的記錄。

這兩個隔離級別實現是通過「事務的 Read View 裡的字段」和「記錄中的兩個隱藏列（trx_id 和 roll_pointer）」的比對，如果不滿足可見行，就會順著 undo log 版本鏈裡找到滿足其可見性的記錄，從而控制併發事務訪問同一個記錄時的行為，這就叫 MVCC（多版本併發控制）。具體的實現可以看我這篇文章：[事務隔離級別是怎麼實現的？](https://xiaolincoding.com/mysql/transaction/mvcc.html#%E4%BA%8B%E5%8A%A1%E7%9A%84%E9%9A%94%E7%A6%BB%E7%BA%A7%E5%88%AB%E6%9C%89%E5%93%AA%E4%BA%9B)

因此，undo log 兩大作用：

- **實現事務回滾，保障事務的原子性**。事務處理過程中，如果出現了錯誤或者用戶執
  行了 ROLLBACK 語句，MySQL 可以利用 undo log 中的歷史數據將數據恢復到事務開始之前的狀態。
- **實現 MVCC（多版本併發控制）關鍵因素之一**。MVCC 是通過 ReadView + undo log 實現的。undo log 為每條記錄保存多份歷史數據，MySQL 在執行快照讀（普通 select 語句）的時候，會根據事務的 Read View 裡的信息，順著 undo log 的版本鏈找到滿足其可見性的記錄。

## 為什麼需要 Buffer Pool？

MySQL 的數據都是存在磁盤中的，那麼我們要更新一條記錄的時候，得先要從磁盤讀取該記錄，然後在內存中修改這條記錄。那修改完這條記錄是選擇直接寫回到磁盤，還是選擇緩存起來呢？

當然是緩存起來好，這樣下次有查詢語句命中了這條記錄，直接讀取緩存中的記錄，就不需要從磁盤獲取數據了。

為此，Innodb 存儲引擎設計了一個**緩衝池（Buffer Pool）**，來提高數據庫的讀寫性能。

![Buffer Poo](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/%E7%BC%93%E5%86%B2%E6%B1%A0.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

有了 Buffer Poo 後：

- 當讀取數據時，如果數據存在於 Buffer Pool 中，客戶端就會直接讀取 Buffer Pool 中的數據，否則再去磁盤中讀取。
- 當修改數據時，如果數據存在於  Buffer Pool  中，那直接修改 Buffer Pool 中數據所在的頁，然後將其頁設置為髒頁（該頁的內存數據和磁盤上的數據已經不一致），為了減少磁盤I/O，不會立即將髒頁寫入磁盤，後續由後臺線程選擇一個合適的時機將髒頁寫入到磁盤。

### Buffer Pool 緩存什麼？

InnoDB 會把存儲的數據劃分為若干個「頁」，以頁作為磁盤和內存交互的基本單位，一個頁的默認大小為 16KB。因此，Buffer Pool 同樣需要按「頁」來劃分。

在 MySQL 啟動的時候，**InnoDB 會為 Buffer Pool 申請一片連續的內存空間，然後按照默認的`16KB`的大小劃分出一個個的頁， Buffer Pool 中的頁就叫做緩存頁**。此時這些緩存頁都是空閒的，之後隨著程序的運行，才會有磁盤上的頁被緩存到 Buffer Pool 中。

所以，MySQL 剛啟動的時候，你會觀察到使用的虛擬內存空間很大，而使用到的物理內存空間卻很小，這是因為只有這些虛擬內存被訪問後，操作系統才會觸發缺頁中斷，申請物理內存，接著將虛擬地址和物理地址建立映射關係。

Buffer Pool 除了緩存「索引頁」和「數據頁」，還包括了 Undo 頁，插入緩存、自適應哈希索引、鎖信息等等。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/mysql/innodb/bufferpool%E5%86%85%E5%AE%B9.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

> Undo 頁是記錄什麼？

開啟事務後，InnoDB 層更新記錄前，首先要記錄相應的 undo log，如果是更新操作，需要把被更新的列的舊值記下來，也就是要生成一條 undo log，undo log 會寫入 Buffer Pool 中的 Undo 頁面。

> 查詢一條記錄，就只需要緩衝一條記錄嗎？

不是的。

當我們查詢一條記錄時，InnoDB 是會把整個頁的數據加載到 Buffer Pool 中，將頁加載到 Buffer Pool 後，再通過頁裡的「頁目錄」去定位到某條具體的記錄。

關於頁結構長什麼樣和索引怎麼查詢數據的問題可以在這篇找到答案：[換一個角度看 B+ 樹](https://mp.weixin.qq.com/s/A5gNVXMNE-iIlY3oofXtLw)

## 為什麼需要 redo log ？

Buffer Pool 是提高了讀寫效率沒錯，但是問題來了，Buffer Pool 是基於內存的，而內存總是不可靠，萬一斷電重啟，還沒來得及落盤的髒頁數據就會丟失。

為了防止斷電導致數據丟失的問題，當有一條記錄需要更新的時候，InnoDB 引擎就會先更新內存（同時標記為髒頁），然後將本次對這個頁的修改以 redo log 的形式記錄下來，**這個時候更新就算完成了**。

後續，InnoDB 引擎會在適當的時候，由後臺線程將緩存在 Buffer Pool  的髒頁刷新到磁盤裡，這就是  **WAL （Write-Ahead Logging）技術**。

**WAL 技術指的是， MySQL 的寫操作並不是立刻寫到磁盤上，而是先寫日誌，然後在合適的時間再寫到磁盤上**。

過程如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/wal.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

> 什麼是  redo log？

redo log 是物理日誌，記錄了某個數據頁做了什麼修改，比如**對 XXX 表空間中的 YYY 數據頁 ZZZ 偏移量的地方做了AAA 更新**，每當執行一個事務就會產生這樣的一條或者多條物理日誌。

在事務提交時，只要先將 redo log 持久化到磁盤即可，可以不需要等到將緩存在  Buffer Pool  裡的髒頁數據持久化到磁盤。

當系統崩潰時，雖然髒頁數據沒有持久化，但是 redo log 已經持久化，接著 MySQL 重啟後，可以根據 redo log 的內容，將所有數據恢復到最新的狀態。

> 被修改 Undo 頁面，需要記錄對應 redo log 嗎？

需要的。

開啟事務後，InnoDB 層更新記錄前，首先要記錄相應的 undo log，如果是更新操作，需要把被更新的列的舊值記下來，也就是要生成一條 undo log，undo log 會寫入 Buffer Pool 中的 Undo 頁面。

不過，**在內存修改該 Undo 頁面後，需要記錄對應的 redo log**。

> redo log 和 undo log 區別在哪？

這兩種日誌是屬於 InnoDB 存儲引擎的日誌，它們的區別在於：

- redo log 記錄了此次事務「**完成後**」的數據狀態，記錄的是更新**之後**的值；
- undo log 記錄了此次事務「**開始前**」的數據狀態，記錄的是更新**之前**的值；

事務提交之前發生了崩潰，重啟後會通過 undo log 回滾事務，事務提交之後發生了崩潰，重啟後會通過 redo log 恢復事務，如下圖：

![事務恢復](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/事務恢復.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

所以有了 redo log，再通過 WAL 技術，InnoDB 就可以保證即使數據庫發生異常重啟，之前已提交的記錄都不會丟失，這個能力稱為 **crash-safe**（崩潰恢復）。可以看出來， **redo log 保證了事務四大特性中的持久性**。

>  redo log 要寫到磁盤，數據也要寫磁盤，為什麼要多此一舉？

寫入 redo log  的方式使用了追加操作， 所以磁盤操作是**順序寫**，而寫入數據需要先找到寫入位置，然後才寫到磁盤，所以磁盤操作是**隨機寫**。

磁盤的「順序寫 」比「隨機寫」 高效的多，因此  redo log 寫入磁盤的開銷更小。

針對「順序寫」為什麼比「隨機寫」更快這個問題，可以比喻為你有一個本子，按照順序一頁一頁寫肯定比寫一個字都要找到對應頁寫快得多。

可以說這是 WAL 技術的另外一個優點：**MySQL 的寫操作從磁盤的「隨機寫」變成了「順序寫」**，提升語句的執行性能。這是因為 MySQL 的寫操作並不是立刻更新到磁盤上，而是先記錄在日誌上，然後在合適的時間再更新到磁盤上 。

至此， 針對為什麼需要 redo log 這個問題我們有兩個答案：

- **實現事務的持久性，讓 MySQL 有 crash-safe 的能力**，能夠保證 MySQL 在任何時間段突然崩潰，重啟後之前已提交的記錄都不會丟失；
- **將寫操作從「隨機寫」變成了「順序寫」**，提升 MySQL 寫入磁盤的性能。

> 產生的 redo log 是直接寫入磁盤的嗎？

不是的。

實際上， 執行一個事務的過程中，產生的 redo log 也不是直接寫入磁盤的，因為這樣會產生大量的 I/O 操作，而且磁盤的運行速度遠慢於內存。

所以，redo log 也有自己的緩存—— **redo log buffer**，每當產生一條 redo log 時，會先寫入到 redo log buffer，後續在持久化到磁盤如下圖：

![事務恢復](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/redologbuf.webp)

redo log buffer 默認大小 16 MB，可以通過 `innodb_log_Buffer_size` 參數動態的調整大小，增大它的大小可以讓 MySQL 處理「大事務」是不必寫入磁盤，進而提升寫 IO 性能。

### redo log 什麼時候刷盤？

緩存在 redo log buffer 裡的 redo log 還是在內存中，它什麼時候刷新到磁盤？

主要有下面幾個時機：

- MySQL 正常關閉時；
- 當 redo log buffer 中記錄的寫入量大於 redo log buffer 內存空間的一半時，會觸發落盤；
- InnoDB 的後臺線程每隔 1 秒，將 redo log buffer 持久化到磁盤。
- 每次事務提交時都將緩存在 redo log buffer 裡的 redo log 直接持久化到磁盤（這個策略可由 innodb_flush_log_at_trx_commit 參數控制，下面會說）。

> innodb_flush_log_at_trx_commit 參數控制的是什麼？

單獨執行一個更新語句的時候，InnoDB 引擎會自己啟動一個事務，在執行更新語句的過程中，生成的 redo log 先寫入到  redo log buffer 中，然後等事務提交的時候，再將緩存在 redo log buffer 中的 redo log 按組的方式「順序寫」到磁盤。

上面這種 redo log 刷盤時機是在事務提交的時候，這個默認的行為。

除此之外，InnoDB 還提供了另外兩種策略，由參數 `innodb_flush_log_at_trx_commit` 參數控制，可取的值有：0、1、2，默認值為 1，這三個值分別代表的策略如下：

- 當設置該**參數為 0 時**，表示每次事務提交時 ，還是**將 redo log 留在  redo log buffer 中** ，該模式下在事務提交時不會主動觸發寫入磁盤的操作。
- 當設置該**參數為 1 時**，表示每次事務提交時，都**將緩存在  redo log buffer 裡的  redo log 直接持久化到磁盤**，這樣可以保證 MySQL 異常重啟之後數據不會丟失。
- 當設置該**參數為 2 時**，表示每次事務提交時，都只是緩存在  redo log buffer 裡的  redo log **寫到 redo log 文件，注意寫入到「 redo log 文件」並不意味著寫入到了磁盤**，因為操作系統的文件系統中有個 Page Cache（如果你想了解  Page Cache，可以看[這篇](https://xiaolincoding.com/os/6_file_system/pagecache.html) ），Page Cache 是專門用來緩存文件數據的，所以寫入「 redo log文件」意味著寫入到了操作系統的文件緩存。

我畫了一個圖，方便大家理解：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/innodb_flush_log_at_trx_commit.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

> innodb_flush_log_at_trx_commit 為 0 和 2 的時候，什麼時候才將 redo log 寫入磁盤？

InnoDB 的後臺線程每隔 1 秒：

- 針對參數 0 ：會把緩存在 redo log buffer 中的 redo log ，通過調用 `write()` 寫到操作系統的 Page Cache，然後調用 `fsync()` 持久化到磁盤。**所以參數為 0 的策略，MySQL 進程的崩潰會導致上一秒鐘所有事務數據的丟失**;
- 針對參數 2 ：調用 fsync，將緩存在操作系統中 Page Cache 裡的 redo log 持久化到磁盤。**所以參數為 2 的策略，較取值為 0 情況下更安全，因為 MySQL 進程的崩潰並不會丟失數據，只有在操作系統崩潰或者系統斷電的情況下，上一秒鐘所有事務數據才可能丟失**。

加入了後臺現線程後，innodb_flush_log_at_trx_commit 的刷盤時機如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/innodb_flush_log_at_trx_commit2.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

> 這三個參數的應用場景是什麼？

這三個參數的數據安全性和寫入性能的比較如下：

- 數據安全性：參數 1 > 參數 2 > 參數 0
- 寫入性能：參數 0 > 參數 2> 參數 1

所以，數據安全性和寫入性能是熊掌不可得兼的，**要不追求數據安全性，犧牲性能；要不追求性能，犧牲數據安全性**。

- 在一些對數據安全性要求比較高的場景中，顯然 `innodb_flush_log_at_trx_commit`  參數需要設置為 1。
- 在一些可以容忍數據庫崩潰時丟失 1s 數據的場景中，我們可以將該值設置為 0，這樣可以明顯地減少日誌同步到磁盤的 I/O 操作。
- 安全性和性能折中的方案就是參數 2，雖然參數 2 沒有參數 0 的性能高，但是數據安全性方面比參數 0 強，因為參數 2 只要操作系統不宕機，即使數據庫崩潰了，也不會丟失數據，同時性能方便比參數 1 高。

### redo log 文件寫滿了怎麼辦？

默認情況下， InnoDB 存儲引擎有 1 個重做日誌文件組( redo log Group），「重做日誌文件組」由有 2 個 redo log 文件組成，這兩個  redo  日誌的文件名叫 ：`ib_logfile0` 和 `ib_logfile1` 。

![重做日誌文件組](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/重做日誌文件組.drawio.png)

在重做日誌組中，每個 redo log File 的大小是固定且一致的，假設每個 redo log File 設置的上限是 1 GB，那麼總共就可以記錄 2GB 的操作。

重做日誌文件組是以**循環寫**的方式工作的，從頭開始寫，寫到末尾就又回到開頭，相當於一個環形。

所以 InnoDB 存儲引擎會先寫 ib_logfile0 文件，當 ib_logfile0 文件被寫滿的時候，會切換至  ib_logfile1 文件，當 ib_logfile1 文件也被寫滿時，會切換回 ib_logfile0 文件。

![重做日誌文件組寫入過程](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/重做日誌文件組寫入過程.drawio.png)

我們知道 redo log 是為了防止 Buffer Pool 中的髒頁丟失而設計的，那麼如果隨著系統運行，Buffer Pool 的髒頁刷新到了磁盤中，那麼 redo log 對應的記錄也就沒用了，這時候我們擦除這些舊記錄，以騰出空間記錄新的更新操作。

redo log 是循環寫的方式，相當於一個環形，InnoDB 用 write pos 表示 redo log 當前記錄寫到的位置，用 checkpoint 表示當前要擦除的位置，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/checkpoint.png)

圖中的：

- write pos 和 checkpoint 的移動都是順時針方向；
- write pos ～ checkpoint 之間的部分（圖中的紅色部分），用來記錄新的更新操作；
- check point ～ write pos 之間的部分（圖中藍色部分）：待落盤的髒數據頁記錄；

如果 write pos  追上了  checkpoint，就意味著 **redo log 文件滿了，這時 MySQL 不能再執行新的更新操作，也就是說 MySQL 會被阻塞**（*因此所以針對併發量大的系統，適當設置  redo log 的文件大小非常重要*），此時**會停下來將 Buffer Pool 中的髒頁刷新到磁盤中，然後標記 redo log 哪些記錄可以被擦除，接著對舊的 redo log 記錄進行擦除，等擦除完舊記錄騰出了空間，checkpoint 就會往後移動（圖中順時針）**，然後 MySQL 恢復正常運行，繼續執行新的更新操作。

所以，一次 checkpoint 的過程就是髒頁刷新到磁盤中變成乾淨頁，然後標記 redo log  哪些記錄可以被覆蓋的過程。

## 為什麼需要 binlog ？

前面介紹的 undo log 和 redo log 這兩個日誌都是 Innodb 存儲引擎生成的。

MySQL 在完成一條更新操作後，Server 層還會生成一條 binlog，等之後事務提交的時候，會將該事物執行過程中產生的所有 binlog 統一寫 入 binlog 文件。

binlog 文件是記錄了所有數據庫表結構變更和表數據修改的日誌，不會記錄查詢類的操作，比如 SELECT 和 SHOW 操作。

> 為什麼有了 binlog， 還要有 redo log？

這個問題跟 MySQL 的時間線有關係。

最開始 MySQL 裡並沒有 InnoDB 引擎，MySQL 自帶的引擎是 MyISAM，但是 MyISAM 沒有 crash-safe 的能力，binlog 日誌只能用於歸檔。

而 InnoDB 是另一個公司以插件形式引入 MySQL 的，既然只依靠 binlog 是沒有 crash-safe 能力的，所以 InnoDB 使用  redo log 來實現 crash-safe 能力。

### redo log 和 binlog 有什麼區別？

這兩個日誌有四個區別。

*1、適用對象不同：*

- binlog 是 MySQL 的 Server 層實現的日誌，所有存儲引擎都可以使用；
- redo log 是 Innodb 存儲引擎實現的日誌；

*2、文件格式不同：*

- binlog 有 3 種格式類型，分別是 STATEMENT（默認格式）、ROW、 MIXED，區別如下：
  - STATEMENT：每一條修改數據的 SQL 都會被記錄到 binlog 中（相當於記錄了邏輯操作，所以針對這種格式， binlog 可以稱為邏輯日誌），主從複製中 slave 端再根據 SQL 語句重現。但 STATEMENT 有動態函數的問題，比如你用了 uuid 或者 now 這些函數，你在主庫上執行的結果並不是你在從庫執行的結果，這種隨時在變的函數會導致複製的數據不一致；
  - ROW：記錄行數據最終被修改成什麼樣了（這種格式的日誌，就不能稱為邏輯日誌了），不會出現 STATEMENT 下動態函數的問題。但 ROW 的缺點是每行數據的變化結果都會被記錄，比如執行批量 update 語句，更新多少行數據就會產生多少條記錄，使 binlog 文件過大，而在 STATEMENT 格式下只會記錄一個 update 語句而已；
  - MIXED：包含了 STATEMENT 和 ROW 模式，它會根據不同的情況自動使用 ROW 模式和 STATEMENT 模式；
- redo log 是物理日誌，記錄的是在某個數據頁做了什麼修改，比如對 XXX 表空間中的 YYY 數據頁 ZZZ 偏移量的地方做了AAA 更新；

*3、寫入方式不同：*

- binlog 是追加寫，寫滿一個文件，就創建一個新的文件繼續寫，不會覆蓋以前的日誌，保存的是全量的日誌。
- redo log 是循環寫，日誌空間大小是固定，全部寫滿就從頭開始，保存未被刷入磁盤的髒頁日誌。

*4、用途不同：*

- binlog 用於備份恢復、主從複製；
- redo log 用於掉電等故障恢復。

> 如果不小心整個數據庫的數據被刪除了，能使用 redo log 文件恢復數據嗎？

不可以使用 redo log 文件恢復，只能使用 binlog 文件恢復。

因為 redo log  文件是循環寫，是會邊寫邊擦除日誌的，只記錄未被刷入磁盤的數據的物理日誌，已經刷入磁盤的數據都會從 redo log 文件裡擦除。

binlog 文件保存的是全量的日誌，也就是保存了所有數據變更的情況，理論上只要記錄在 binlog 上的數據，都可以恢復，所以如果不小心整個數據庫的數據被刪除了，得用 binlog 文件恢復數據。

### 主從複製是怎麼實現？

MySQL 的主從複製依賴於 binlog ，也就是記錄 MySQL 上的所有變化並以二進制形式保存在磁盤上。複製的過程就是將 binlog 中的數據從主庫傳輸到從庫上。

這個過程一般是**異步**的，也就是主庫上執行事務操作的線程不會等待複製 binlog 的線程同步完成。

![MySQL 主從複製過程](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/主從複製過程.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

MySQL 集群的主從複製過程梳理成 3 個階段：

- **寫入 Binlog**：主庫寫 binlog 日誌，提交事務，並更新本地存儲數據。
- **同步 Binlog**：把 binlog 複製到所有從庫上，每個從庫把 binlog 寫到暫存日誌中。
- **回放 Binlog**：回放 binlog，並更新存儲引擎中的數據。

具體詳細過程如下：

- MySQL 主庫在收到客戶端提交事務的請求之後，會先寫入 binlog，再提交事務，更新存儲引擎中的數據，事務提交完成後，返回給客戶端“操作成功”的響應。
- 從庫會創建一個專門的 I/O 線程，連接主庫的 log dump 線程，來接收主庫的 binlog 日誌，再把 binlog 信息寫入 relay log 的中繼日誌裡，再返回給主庫“複製成功”的響應。
- 從庫會創建一個用於回放 binlog 的線程，去讀 relay log 中繼日誌，然後回放 binlog 更新存儲引擎中的數據，最終實現主從的數據一致性。

在完成主從複製之後，你就可以在寫數據時只寫主庫，在讀數據時只讀從庫，這樣即使寫請求會鎖表或者鎖記錄，也不會影響讀請求的執行。

![MySQL 主從架構](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/主從架構.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

> 從庫是不是越多越好？

不是的。

因為從庫數量增加，從庫連接上來的 I/O 線程也比較多，**主庫也要創建同樣多的 log dump 線程來處理複製的請求，對主庫資源消耗比較高，同時還受限於主庫的網絡帶寬**。

所以在實際使用中，一個主庫一般跟 2～3 個從庫（1 套數據庫，1 主 2 從 1 備主），這就是一主多從的 MySQL 集群結構。

>  MySQL 主從複製還有哪些模型？

主要有三種：

- **同步複製**：MySQL 主庫提交事務的線程要等待所有從庫的複製成功響應，才返回客戶端結果。這種方式在實際項目中，基本上沒法用，原因有兩個：一是性能很差，因為要複製到所有節點才返回響應；二是可用性也很差，主庫和所有從庫任何一個數據庫出問題，都會影響業務。
- **異步複製**（默認模型）：MySQL 主庫提交事務的線程並不會等待 binlog 同步到各從庫，就返回客戶端結果。這種模式一旦主庫宕機，數據就會發生丟失。
- **半同步複製**：MySQL 5.7 版本之後增加的一種複製方式，介於兩者之間，事務線程不用等待所有的從庫複製成功響應，只要一部分複製成功響應回來就行，比如一主二從的集群，只要數據成功複製到任意一個從庫上，主庫的事務線程就可以返回給客戶端。這種**半同步複製的方式，兼顧了異步複製和同步複製的優點，即使出現主庫宕機，至少還有一個從庫有最新的數據，不存在數據丟失的風險**。

### binlog 什麼時候刷盤？

事務執行過程中，先把日誌寫到 binlog cache（Server 層的 cache），事務提交的時候，再把 binlog cache 寫到 binlog 文件中。

MySQL 給 binlog cache 分配了一片內存，每個線程一個，參數 binlog_cache_size 用於控制單個線程內 binlog cache 所佔內存的大小。如果超過了這個參數規定的大小，就要暫存到磁盤。

> 什麼時候 binlog cache 會寫到 binlog 文件？

在事務提交的時候，執行器把 binlog cache 裡的完整事務寫入到 binlog 文件中，並清空 binlog cache。如下圖：

![binlog cach](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/binlogcache.drawio.png)

雖然每個線程有自己 binlog cache，但是最終都寫到同一個 binlog 文件：

- 圖中的 write，指的就是指把日誌寫入到 binlog 文件，但是並沒有把數據持久化到磁盤，因為數據還緩存在文件系統的 page cache 裡，write 的寫入速度還是比較快的，因為不涉及磁盤 I/O。
- 圖中的 fsync，才是將數據持久化到磁盤的操作，這裡就會涉及磁盤 I/O，所以頻繁的 fsync 會導致磁盤的 I/O 升高。

MySQL提供一個 sync_binlog 參數來控制數據庫的 binlog 刷到磁盤上的頻率：

- sync_binlog = 0 的時候，表示每次提交事務都只 write，不 fsync，後續交由操作系統決定何時將數據持久化到磁盤；
- sync_binlog = 1 的時候，表示每次提交事務都會 write，然後馬上執行 fsync；
- sync_binlog =N(N>1) 的時候，表示每次提交事務都 write，但累積 N 個事務後才 fsync。

在MySQL中系統默認的設置是 sync_binlog = 0，也就是不做任何強制性的磁盤刷新指令，這時候的性能是最好的，但是風險也是最大的。因為一旦主機發生異常重啟，還沒持久化到磁盤的數據就會丟失。

而當 sync_binlog 設置為 1 的時候，是最安全但是性能損耗最大的設置。因為當設置為 1 的時候，即使主機發生異常重啟，最多丟失一個事務的 binlog，而已經持久化到磁盤的數據就不會有影響，不過就是對寫入性能影響太大。

如果能容少量事務的 binlog 日誌丟失的風險，為了提高寫入的性能，一般會 sync_binlog 設置為 100~1000 中的某個數值。

> 三個日誌講完了，至此我們可以先小結下，update 語句的執行過程。

當優化器分析出成本最小的執行計劃後，執行器就按照執行計劃開始進行更新操作。

具體更新一條記錄 `UPDATE t_user SET name = 'xiaolin' WHERE id = 1;` 的流程如下:

1. 執行器負責具體執行，會調用存儲引擎的接口，通過主鍵索引樹搜索獲取 id = 1 這一行記錄：
   - 如果 id=1 這一行所在的數據頁本來就在 buffer pool 中，就直接返回給執行器更新；
   - 如果記錄不在 buffer pool，將數據頁從磁盤讀入到 buffer pool，返回記錄給執行器。
2. 執行器得到聚簇索引記錄後，會看一下更新前的記錄和更新後的記錄是否一樣：
   - 如果一樣的話就不進行後續更新流程；
   - 如果不一樣的話就把更新前的記錄和更新後的記錄都當作參數傳給 InnoDB 層，讓 InnoDB 真正的執行更新記錄的操作；
3. 開啟事務， InnoDB 層更新記錄前，首先要記錄相應的 undo log，因為這是更新操作，需要把被更新的列的舊值記下來，也就是要生成一條 undo log，undo log 會寫入 Buffer Pool 中的 Undo 頁面，不過在內存修改該 Undo 頁面後，需要記錄對應的 redo log。
4. InnoDB 層開始更新記錄，會先更新內存（同時標記為髒頁），然後將記錄寫到 redo log 裡面，這個時候更新就算完成了。為了減少磁盤I/O，不會立即將髒頁寫入磁盤，後續由後臺線程選擇一個合適的時機將髒頁寫入到磁盤。這就是 **WAL 技術**，MySQL 的寫操作並不是立刻寫到磁盤上，而是先寫 redo 日誌，然後在合適的時間再將修改的行數據寫到磁盤上。
5. 至此，一條記錄更新完了。
6. 在一條更新語句執行完成後，然後開始記錄該語句對應的 binlog，此時記錄的 binlog 會被保存到 binlog cache，並沒有刷新到硬盤上的 binlog 文件，在事務提交時才會統一將該事務運行過程中的所有 binlog 刷新到硬盤。
7. 事務提交，剩下的就是「兩階段提交」的事情了，接下來就講這個。

## 為什麼需要兩階段提交？

事務提交後，redo log 和 binlog 都要持久化到磁盤，但是這兩個是獨立的邏輯，可能出現半成功的狀態，這樣就造成兩份日誌之間的邏輯不一致。

舉個例子，假設 id = 1 這行數據的字段 name 的值原本是 'jay'，然後執行 `UPDATE t_user SET name = 'xiaolin' WHERE id = 1;` 如果在持久化 redo log 和 binlog 兩個日誌的過程中，出現了半成功狀態，那麼就有兩種情況：

- **如果在將 redo log 刷入到磁盤之後， MySQL 突然宕機了，而 binlog 還沒有來得及寫入**。MySQL 重啟後，通過 redo log 能將 Buffer Pool 中 id = 1 這行數據的 name 字段恢復到新值 xiaolin，但是 binlog 裡面沒有記錄這條更新語句，在主從架構中，binlog 會被複制到從庫，由於 binlog 丟失了這條更新語句，從庫的這一行 name 字段是舊值 jay，與主庫的值不一致性；
- **如果在將 binlog 刷入到磁盤之後， MySQL 突然宕機了，而 redo log 還沒有來得及寫入**。由於 redo log 還沒寫，崩潰恢復以後這個事務無效，所以 id = 1 這行數據的 name 字段還是舊值 jay，而 binlog 裡面記錄了這條更新語句，在主從架構中，binlog 會被複制到從庫，從庫執行了這條更新語句，那麼這一行 name 字段是新值 xiaolin，與主庫的值不一致性；

可以看到，在持久化 redo log 和 binlog 這兩份日誌的時候，如果出現半成功的狀態，就會造成主從環境的數據不一致性。這是因為 redo log 影響主庫的數據，binlog 影響從庫的數據，所以 redo log 和 binlog 必須保持一致才能保證主從數據一致。

**MySQL 為了避免出現兩份日誌之間的邏輯不一致的問題，使用了「兩階段提交」來解決**，兩階段提交其實是分佈式事務一致性協議，它可以保證多個邏輯操作要不全部成功，要不全部失敗，不會出現半成功的狀態。

**兩階段提交把單個事務的提交拆分成了 2 個階段，分別是「準備（Prepare）階段」和「提交（Commit）階段」**，每個階段都由協調者（Coordinator）和參與者（Participant）共同完成。注意，不要把提交（Commit）階段和 commit 語句混淆了，commit 語句執行的時候，會包含提交（Commit）階段。

舉個拳擊比賽的例子，兩位拳擊手（參與者）開始比賽之前，裁判（協調者）會在中間確認兩位拳擊手的狀態，類似於問你準備好了嗎？

- **準備階段**：裁判（協調者）會依次詢問兩位拳擊手（參與者）是否準備好了，然後拳擊手聽到後做出應答，如果覺得自己準備好了，就會跟裁判說準備好了；如果沒有自己還沒有準備好（比如拳套還沒有帶好），就會跟裁判說還沒準備好。
- **提交階段**：如果兩位拳擊手（參與者）都回答準備好了，裁判（協調者）宣佈比賽正式開始，兩位拳擊手就可以直接開打；如果任何一位拳擊手（參與者）回答沒有準備好，裁判（協調者）會宣佈比賽暫停，對應事務中的回滾操作。

### 兩階段提交的過程是怎樣的？

在 MySQL 的 InnoDB 存儲引擎中，開啟 binlog 的情況下，MySQL 會同時維護 binlog 日誌與 InnoDB 的 redo log，為了保證這兩個日誌的一致性，MySQL 使用了**內部 XA 事務**（是的，也有外部  XA 事務，跟本文不太相關，我就不介紹了），內部 XA 事務由 binlog 作為協調者，存儲引擎是參與者。

當客戶端執行 commit 語句或者在自動提交的情況下，MySQL 內部開啟一個 XA 事務，**分兩階段來完成 XA 事務的提交**，如下圖：

![兩階段提交](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/兩階段提交.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

從圖中可看出，事務的提交過程有兩個階段，就是**將 redo log 的寫入拆成了兩個步驟：prepare 和 commit，中間再穿插寫入binlog**，具體如下：

- **prepare 階段**：將 XID（內部 XA 事務的 ID） 寫入到 redo log，同時將 redo log 對應的事務狀態設置為 prepare，然後將 redo log 刷新到硬盤；

- **commit 階段**：把 XID  寫入到 binlog，然後將 binlog 刷新到磁盤，接著調用引擎的提交事務接口，將 redo log 狀態設置為 commit（將事務設置為 commit 狀態後，刷入到磁盤 redo log 文件，所以 commit 狀態也是會刷盤的）；

### 異常重啟會出現什麼現象？

我們來看看在兩階段提交的不同時刻，MySQL 異常重啟會出現什麼現象？下圖中有時刻 A 和時刻 B 都有可能發生崩潰：

![時刻 A 與時刻 B](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/兩階段提交崩潰點.drawio.png?image_process=watermark,text_5YWs5LyX5Y-377ya5bCP5p6XY29kaW5n,type_ZnpsdHpoaw,x_10,y_10,g_se,size_20,color_0000CD,t_70,fill_0)

不管是時刻 A（已經 redo log，還沒寫入 binlog），還是時刻 B （已經寫入 redo log 和 binlog，還沒寫入 commit 標識）崩潰，**此時的 redo log 都處於 prepare 狀態**。

在 MySQL 重啟後會按順序掃描 redo log 文件，碰到處於 prepare 狀態的 redo log，就拿著 redo log 中的 XID 去 binlog 查看是否存在此 XID：

- **如果 binlog 中沒有當前內部 XA 事務的 XID，說明 redolog 完成刷盤，但是 binlog 還沒有刷盤，則回滾事務**。對應時刻 A 崩潰恢復的情況。
- **如果 binlog 中有當前內部 XA 事務的 XID，說明 redolog 和 binlog 都已經完成了刷盤，則提交事務**。對應時刻 B 崩潰恢復的情況。

可以看到，**對於處於 prepare 階段的 redo log，即可以提交事務，也可以回滾事務，這取決於是否能在 binlog 中查找到與 redo log 相同的  XID**，如果有就提交事務，如果沒有就回滾事務。這樣就可以保證 redo log 和 binlog 這兩份日誌的一致性了。

所以說，**兩階段提交是以 binlog 寫成功為事務提交成功的標識**，因為 binlog 寫成功了，就意味著能在 binlog 中查找到與 redo log 相同的  XID。

> 處於 prepare 階段的 redo log 加上完整 binlog，重啟就提交事務，MySQL 為什麼要這麼設計?

binlog 已經寫入了，之後就會被從庫（或者用這個 binlog 恢復出來的庫）使用。

所以，在主庫上也要提交這個事務。採用這個策略，主庫和備庫的數據就保證了一致性。

> 事務沒提交的時候，redo log 會被持久化到磁盤嗎？

會的。

事務執行中間過程的 redo log 也是直接寫在 redo log buffer 中的，這些緩存在  redo log buffer  裡的 redo log 也會被「後臺線程」每隔一秒一起持久化到磁盤。

也就是說，事務沒提交的時候，redo log 也是可能被持久化到磁盤的。

有的同學可能會問，如果 mysql 崩潰了，還沒提交事務的 redo log 已經被持久化磁盤了，mysql 重啟後，數據不就不一致了？

放心，這種情況 mysql 重啟會進行回滾操作，因為事務沒提交的時候，binlog 是還沒持久化到磁盤的。

所以， redo log 可以在事務沒提交之前持久化到磁盤，但是 binlog 必須在事務提交之後，才可以持久化到磁盤。

## 兩階段提交有什麼問題？

兩階段提交雖然保證了兩個日誌文件的數據一致性，但是性能很差，主要有兩個方面的影響：

- **磁盤 I/O 次數高**：對於“雙1”配置，每個事務提交都會進行兩次 fsync（刷盤），一次是 redo log 刷盤，另一次是 binlog 刷盤。
- **鎖競爭激烈**：兩階段提交雖然能夠保證「單事務」兩個日誌的內容一致，但在「多事務」的情況下，卻不能保證兩者的提交順序一致，因此，在兩階段提交的流程基礎上，還需要加一個鎖來保證提交的原子性，從而保證多事務的情況下，兩個日誌的提交順序一致。

> 為什麼兩階段提交的磁盤 I/O 次數會很高？

binlog 和 redo log 在內存中都對應的緩存空間，binlog 會緩存在 binlog cache，redo log 會緩存在 redo log buffer，它們持久化到磁盤的時機分別由下面這兩個參數控制。一般我們為了避免日誌丟失的風險，會將這兩個參數設置為 1：

- 當 sync_binlog = 1 的時候，表示每次提交事務都會將  binlog cache 裡的 binlog 直接持久到磁盤；
- 當 innodb_flush_log_at_trx_commit = 1 時，表示每次事務提交時，都將緩存在  redo log buffer 裡的  redo log 直接持久化到磁盤；

可以看到，如果 sync_binlog 和 當 innodb_flush_log_at_trx_commit 都設置為 1，那麼在每個事務提交過程中， 都會至少調用 2 次刷盤操作，一次是 redo log 刷盤，一次是 binlog 落盤，所以這會成為性能瓶頸。

> 為什麼鎖競爭激烈？

在早期的 MySQL 版本中，通過使用 prepare_commit_mutex 鎖來保證事務提交的順序，在一個事務獲取到鎖時才能進入 prepare 階段，一直到 commit 階段結束才能釋放鎖，下個事務才可以繼續進行 prepare 操作。

通過加鎖雖然完美地解決了順序一致性的問題，但在併發量較大的時候，就會導致對鎖的爭用，性能不佳。

### 組提交

**MySQL  引入了 binlog 組提交（group commit）機制，當有多個事務提交的時候，會將多個 binlog 刷盤操作合併成一個，從而減少磁盤 I/O 的次數**，如果說 10 個事務依次排隊刷盤的時間成本是 10，那麼將這 10 個事務一次性一起刷盤的時間成本則近似於 1。

引入了組提交機制後，prepare 階段不變，只針對 commit 階段，將 commit 階段拆分為三個過程：

- **flush 階段**：多個事務按進入的順序將 binlog 從 cache 寫入文件（不刷盤）；
- **sync 階段**：對 binlog 文件做 fsync 操作（多個事務的 binlog 合併一次刷盤）；
- **commit 階段**：各個事務按順序做 InnoDB commit 操作；

上面的**每個階段都有一個隊列**，每個階段有鎖進行保護，因此保證了事務寫入的順序，第一個進入隊列的事務會成為 leader，leader領導所在隊列的所有事務，全權負責整隊的操作，完成後通知隊內其他事務操作結束。

![每個階段都有一個隊列](http://keithlan.github.io/image/mysql_innodb_arch/commit_4.png)

對每個階段引入了隊列後，鎖就只針對每個隊列進行保護，不再鎖住提交事務的整個過程，可以看的出來，**鎖粒度減小了，這樣就使得多個階段可以併發執行，從而提升效率**。

> 有  binlog 組提交，那有  redo log 組提交嗎？

這個要看 MySQL 版本，MySQL 5.6 沒有 redo log 組提交，MySQL 5.7 有 redo log 組提交。

在 MySQL 5.6 的組提交邏輯中，每個事務各自執行 prepare 階段，也就是各自將  redo log 刷盤，這樣就沒辦法對 redo log 進行組提交。

所以在 MySQL 5.7 版本中，做了個改進，在 prepare 階段不再讓事務各自執行 redo log 刷盤操作，而是推遲到組提交的 flush 階段，也就是說 prepare 階段融合在了  flush 階段。

這個優化是將 redo log 的刷盤延遲到了 flush 階段之中，sync 階段之前。通過延遲寫 redo log 的方式，為 redolog 做了一次組寫入，這樣 binlog 和 redo log 都進行了優化。

接下來介紹每個階段的過程，注意下面的過程針對的是“雙 1” 配置（sync_binlog 和 innodb_flush_log_at_trx_commit 都配置為 1）。

> flush 階段

第一個事務會成為 flush 階段的 Leader，此時後面到來的事務都是 Follower ：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/組提交1.png)

接著，獲取隊列中的事務組，由綠色事務組的 Leader 對 rodo log 做一次  write + fsync，即一次將同組事務的 redolog 刷盤：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/組提交2.png)

完成了 prepare 階段後，將綠色這一組事務執行過程中產生的 binlog 寫入 binlog 文件（調用 write，不會調用 fsync，所以不會刷盤，binlog 緩存在操作系統的文件系統中）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/write_binlog.png)

從上面這個過程，可以知道 flush 階段隊列的作用是**用於支撐 redo log 的組提交**。

如果在這一步完成後數據庫崩潰，由於 binlog 中沒有該組事務的記錄，所以 MySQL 會在重啟後回滾該組事務。

> sync 階段

綠色這一組事務的 binlog 寫入到 binlog 文件後，並不會馬上執行刷盤的操作，而是**會等待一段時間**，這個等待的時長由 `Binlog_group_commit_sync_delay` 參數控制，**目的是為了組合更多事務的 binlog，然後再一起刷盤**，如下過程：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/組提交4.png)

不過，在等待的過程中，如果事務的數量提前達到了 `Binlog_group_commit_sync_no_delay_count` 參數設置的值，就不用繼續等待了，就馬上將 binlog 刷盤，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/組提交5.png)

從上面的過程，可以知道 sync 階段隊列的作用是**用於支持 binlog 的組提交**。

如果想提升 binlog 組提交的效果，可以通過設置下面這兩個參數來實現：

- `binlog_group_commit_sync_delay= N`，表示在等待 N 微妙後，直接調用 fsync，將處於文件系統中 page cache 中的 binlog 刷盤，也就是將「 binlog 文件」持久化到磁盤。
- `binlog_group_commit_sync_no_delay_count = N`，表示如果隊列中的事務數達到 N 個，就忽視binlog_group_commit_sync_delay 的設置，直接調用 fsync，將處於文件系統中 page cache 中的 binlog 刷盤。

如果在這一步完成後數據庫崩潰，由於 binlog 中已經有了事務記錄，MySQL會在重啟後通過 redo log 刷盤的數據繼續進行事務的提交。

> commit 階段

最後進入 commit 階段，調用引擎的提交事務接口，將 redo log 狀態設置為 commit。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/how_update/組提交6.png)

commit 階段隊列的作用是承接 sync 階段的事務，完成最後的引擎提交，使得 sync 可以儘早的處理下一組事務，最大化組提交的效率。

## MySQL 磁盤 I/O 很高，有什麼優化的方法？

現在我們知道事務在提交的時候，需要將 binlog 和 redo log 持久化到磁盤，那麼如果出現 MySQL 磁盤 I/O 很高的現象，我們可以通過控制以下參數，來 “延遲” binlog 和 redo log 刷盤的時機，從而降低磁盤 I/O 的頻率：

- 設置組提交的兩個參數： binlog_group_commit_sync_delay 和 binlog_group_commit_sync_no_delay_count 參數，延遲 binlog 刷盤的時機，從而減少 binlog 的刷盤次數。這個方法是基於“額外的故意等待”來實現的，因此可能會增加語句的響應時間，但即使 MySQL 進程中途掛了，也沒有丟失數據的風險，因為 binlog 早被寫入到 page cache 了，只要系統沒有宕機，緩存在 page cache 裡的 binlog 就會被持久化到磁盤。
- 將 sync_binlog 設置為大於 1 的值（比較常見是 100~1000），表示每次提交事務都 write，但累積 N 個事務後才 fsync，相當於延遲了 binlog 刷盤的時機。但是這樣做的風險是，主機掉電時會丟 N 個事務的 binlog 日誌。
- 將 innodb_flush_log_at_trx_commit 設置為 2。表示每次事務提交時，都只是緩存在  redo log buffer 裡的  redo log 寫到 redo log 文件，注意寫入到「 redo log 文件」並不意味著寫入到了磁盤，因為操作系統的文件系統中有個 Page Cache，專門用來緩存文件數據的，所以寫入「 redo log文件」意味著寫入到了操作系統的文件緩存，然後交由操作系統控制持久化到磁盤的時機。但是這樣做的風險是，主機掉電的時候會丟數據。

## 總結

具體更新一條記錄 `UPDATE t_user SET name = 'xiaolin' WHERE id = 1;` 的流程如下:

1. 執行器負責具體執行，會調用存儲引擎的接口，通過主鍵索引樹搜索獲取 id = 1 這一行記錄：
   - 如果 id=1 這一行所在的數據頁本來就在 buffer pool 中，就直接返回給執行器更新；
   - 如果記錄不在 buffer pool，將數據頁從磁盤讀入到 buffer pool，返回記錄給執行器。
2. 執行器得到聚簇索引記錄後，會看一下更新前的記錄和更新後的記錄是否一樣：
   - 如果一樣的話就不進行後續更新流程；
   - 如果不一樣的話就把更新前的記錄和更新後的記錄都當作參數傳給 InnoDB 層，讓 InnoDB 真正的執行更新記錄的操作；
3. 開啟事務， InnoDB 層更新記錄前，首先要記錄相應的 undo log，因為這是更新操作，需要把被更新的列的舊值記下來，也就是要生成一條 undo log，undo log 會寫入 Buffer Pool 中的 Undo 頁面，不過在內存修改該 Undo 頁面後，需要記錄對應的 redo log。
4. InnoDB 層開始更新記錄，會先更新內存（同時標記為髒頁），然後將記錄寫到 redo log 裡面，這個時候更新就算完成了。為了減少磁盤I/O，不會立即將髒頁寫入磁盤，後續由後臺線程選擇一個合適的時機將髒頁寫入到磁盤。這就是 **WAL 技術**，MySQL 的寫操作並不是立刻寫到磁盤上，而是先寫 redo 日誌，然後在合適的時間再將修改的行數據寫到磁盤上。
5. 至此，一條記錄更新完了。
6. 在一條更新語句執行完成後，然後開始記錄該語句對應的 binlog，此時記錄的 binlog 會被保存到 binlog cache，並沒有刷新到硬盤上的 binlog 文件，在事務提交時才會統一將該事務運行過程中的所有 binlog 刷新到硬盤。
7. 事務提交（為了方便說明，這裡不說組提交的過程，只說兩階段提交）：
   - **prepare 階段**：將 redo log 對應的事務狀態設置為 prepare，然後將 redo log 刷新到硬盤；
   - **commit 階段**：將 binlog 刷新到磁盤，接著調用引擎的提交事務接口，將 redo log 狀態設置為 commit（將事務設置為 commit 狀態後，刷入到磁盤 redo log 文件）；
8. 至此，一條更新語句執行完成。

---

參考資料：

- 《MySQL 45 講》
- 《MySQL 是怎樣運行的？》
- https://developer.aliyun.com/article/617776
- http://mysql.taobao.org/monthly/2021/10/01/
- https://www.cnblogs.com/Neeo/articles/13883976.html
- https://www.cnblogs.com/mengxinJ/p/14211427.html

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)