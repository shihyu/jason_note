# MySQL 記錄鎖+間隙鎖可以防止刪除操作而導致的幻讀嗎？

大家好，我是小林。

昨天有位讀者在美團二面的時候，被問到關於幻讀的問題：

![](https://img-blog.csdnimg.cn/4c48fe8a02374754b1cf92591ae8d3b4.png)

面試官反問的大概意思是，**MySQL 記錄鎖+間隙鎖可以防止刪除操作而導致的幻讀嗎？**

答案是可以的。

接下來，通過幾個小實驗來證明這個結論吧，順便再幫大家複習一下記錄鎖+間隙鎖。

## 什麼是幻讀？

首先來看看 MySQL 文檔是怎麼定義幻讀（Phantom Read）的:

***The so-called phantom problem occurs within a transaction when the same query produces different sets of rows at different times. For example, if a SELECT is executed twice, but returns a row the second time that was not returned the first time, the row is a “phantom” row.***

翻譯：當同一個查詢在不同的時間產生不同的結果集時，事務中就會出現所謂的幻象問題。例如，如果 SELECT 執行了兩次，但第二次返回了第一次沒有返回的行，則該行是“幻像”行。

舉個例子，假設一個事務在 T1 時刻和 T2 時刻分別執行了下面查詢語句，途中沒有執行其他任何語句：

```sql
SELECT * FROM t_test WHERE id > 100;
```

只要 T1 和 T2 時刻執行產生的結果集是不相同的，那就發生了幻讀的問題，比如：
-	T1 時間執行的結果是有 5 條行記錄，而 T2 時間執行的結果是有 6 條行記錄，那就發生了幻讀的問題。
-	T1 時間執行的結果是有 5 條行記錄，而 T2 時間執行的結果是有 4 條行記錄，也是發生了幻讀的問題。


> MySQL  是怎麼解決幻讀的？

MySQL InnoDB 引擎的默認隔離級別雖然是「可重複讀」，但是它很大程度上避免幻讀現象（並不是完全解決了，詳見這篇[文章](https://xiaolincoding.com/mysql/transaction/phantom.html)），解決的方案有兩種：
-	針對**快照讀**（普通 select 語句），是**通過 MVCC 方式解決了幻讀**，因為可重複讀隔離級別下，事務執行過程中看到的數據，一直跟這個事務啟動時看到的數據是一致的，即使中途有其他事務插入了一條數據，是查詢不出來這條數據的，所以就很好了避免幻讀問題。
-	針對**當前讀**（select ... for update 等語句），是**通過 next-key lock（記錄鎖+間隙鎖）方式解決了幻讀**，因為當執行 select ... for update 語句的時候，會加上 next-key lock，如果有其他事務在 next-key lock 鎖範圍內插入了一條記錄，那麼這個插入語句就會被阻塞，無法成功插入，所以就很好了避免幻讀問題。

## 實驗驗證

接下來，來驗證「 MySQL 記錄鎖+間隙鎖**可以防止**刪除操作而導致的幻讀問題」的結論。

實驗環境：MySQL 8.0 版本，可重複讀隔離級。

現在有一張用戶表（t_user），表裡**只有一個主鍵索引**，表裡有以下行數據：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/75c5c503d7df4ad091bfc35708dce6c4.png)

現在有一個 A 事務執行了一條查詢語句，查詢到年齡大於 20 歲的用戶共有 6 條行記錄。

![](https://img-blog.csdnimg.cn/68dd89fc95aa42cf9b0c4251d4e9226c.png)


然後， B 事務執行了一條刪除 id = 2 的語句：

![](https://img-blog.csdnimg.cn/2332fad58bc548ec917ba7ea44d09d30.png)

此時，B 事務的刪除語句就陷入了**等待狀態**，說明是無法進行刪除的。

因此，MySQL 記錄鎖+間隙鎖**可以防止**刪除操作而導致的幻讀問題。

### 加鎖分析

問題來了，A 事務在執行 select ... for update 語句時，具體加了什麼鎖呢？

我們可以通過 `select * from performance_schema.data_locks\G;` 這條語句，查看事務執行 SQL 過程中加了什麼鎖。

輸出的內容很多，共有 11 行信息，我刪減了一些不重要的信息：

![請添加圖片描述](https://img-blog.csdnimg.cn/90e68bf52b2c4e8a9127cfcbb0f0a322.png)


從上面輸出的信息可以看到，共加了兩種不同粒度的鎖，分別是：

- 表鎖（`LOCK_TYPE: TABLE`）：X 類型的意向鎖；
- 行鎖（`LOCK_TYPE: RECORD`）：X 類型的 next-key 鎖；

這裡我們重點關注「行鎖」，圖中 `LOCK_TYPE` 中的 `RECORD` 表示行級鎖，而不是記錄鎖的意思：
- 如果 LOCK_MODE 為 `X`，說明是 next-key 鎖；
- 如果 LOCK_MODE 為 `X, REC_NOT_GAP`，說明是記錄鎖；
- 如果 LOCK_MODE 為 `X, GAP`，說明是間隙鎖；

然後通過 `LOCK_DATA` 信息，可以確認 next-key 鎖的範圍，具體怎麼確定呢？

- 根據我的經驗，如果 LOCK_MODE 是 next-key 鎖或者間隙鎖，那麼 **LOCK_DATA 就表示鎖的範圍最右值**，而鎖範圍的最左值為 LOCK_DATA 的上一條記錄的值。

因此，此時事務 A 在主鍵索引（`INDEX_NAME : PRIMARY`）上加了 10 個 next-key 鎖，如下：
-	X 型的 next-key 鎖，範圍：(-∞, 1]
-	X 型的 next-key 鎖，範圍：(1, 2]
-	X 型的 next-key 鎖，範圍：(2, 3]
-	X 型的 next-key 鎖，範圍：(3, 4]
-	X 型的 next-key 鎖，範圍：(4, 5]
-	X 型的 next-key 鎖，範圍：(5, 6]
-	X 型的 next-key 鎖，範圍：(6, 7]
-	X 型的 next-key 鎖，範圍：(7, 8]
-	X 型的 next-key 鎖，範圍：(8, 9]
-	X 型的 next-key 鎖，範圍：(9, +∞]

**這相當於把整個表給鎖住了，其他事務在對該表進行增、刪、改操作的時候都會被阻塞**。

只有在事務 A 提交了事務，事務 A 執行過程中產生的鎖才會被釋放。

> 為什麼只是查詢年齡 20 歲以上行記錄，而把整個表給鎖住了呢？

這是因為事務 A 的這條查詢語句是**全表掃描，鎖是在遍歷索引的時候加上的，並不是針對輸出的結果加鎖**。

![](https://img-blog.csdnimg.cn/e0b2a18daa864306a84ec51c0866d170.png)

因此，**在線上在執行 update、delete、select ... for update 等具有加鎖性質的語句，一定要檢查語句是否走了索引，如果是全表掃描的話，會對每一個索引加 next-key 鎖，相當於把整個表鎖住了**，這是挺嚴重的問題。


> 如果對 age 建立索引，事務 A 這條查詢會加什麼鎖呢？

接下來，我**對 age 字段建立索引**，然後再執行這條查詢語句：

![](https://img-blog.csdnimg.cn/68dd89fc95aa42cf9b0c4251d4e9226c.png)


接下來，繼續通過 `select * from performance_schema.data_locks\G;` 這條語句，查看事務執行 SQL 過程中加了什麼鎖。

具體的信息，我就不打印了，我直接說結論吧。

**因為表中有兩個索引，分別是主鍵索引和 age 索引，所以會分別對這兩個索引加鎖。**

主鍵索引會加如下的鎖：
-  X 型的記錄鎖，鎖住 id = 2 的記錄；
- X 型的記錄鎖，鎖住 id = 3 的記錄；
- X 型的記錄鎖，鎖住 id = 5 的記錄；
- X 型的記錄鎖，鎖住 id = 6 的記錄；
- X 型的記錄鎖，鎖住 id = 7 的記錄；
- X 型的記錄鎖，鎖住 id = 8 的記錄；

分析 age 索引加鎖的範圍時，要先對 age 字段進行排序。
![請添加圖片描述](https://img-blog.csdnimg.cn/b93b31af4eec416e9f00c2adc1f7d0c1.png)

age 索引加的鎖：
- X 型的 next-key lock，鎖住 age 範圍 (19, 21] 的記錄；
- X 型的 next-key lock，鎖住 age 範圍 (21, 21] 的記錄；
- X 型的 next-key lock，鎖住 age 範圍 (21, 23] 的記錄；
- X 型的 next-key lock，鎖住 age 範圍 (23, 23] 的記錄；
- X 型的 next-key lock，鎖住 age 範圍 (23, 39] 的記錄；
- X 型的 next-key lock，鎖住 age 範圍 (39, 43] 的記錄；
- X 型的 next-key lock，鎖住 age 範圍 (43, +∞] 的記錄；

化簡一下，**age 索引  next-key 鎖的範圍是 (19, +∞]。**

可以看到，對 age 字段建立了索引後，查詢語句是索引查詢，並不會全表掃描，因此**不會把整張表給鎖住**。

![](https://img-blog.csdnimg.cn/2920c60d5a9b42f2a65933fa14761c20.png)

總結一下，在對 age 字段建立索引後，事務 A 在執行下面這條查詢語句後，主鍵索引和 age 索引會加下圖中的鎖。

![請添加圖片描述](https://img-blog.csdnimg.cn/5b9a2d7a2cd240fea47b938364f0b76a.png)

事務 A 加上鎖後，事務 B、C、D、E 在執行以下語句都會被阻塞。

![請添加圖片描述](https://img-blog.csdnimg.cn/46c9b44142f14217b39bd973868e732e.png)


## 總結

在 MySQL 的可重複讀隔離級別下，針對當前讀的語句會對**索引**加記錄鎖+間隙鎖，這樣可以避免其他事務執行增、刪、改時導致幻讀的問題。

有一點要注意的是，在執行 update、delete、select ... for update 等具有加鎖性質的語句，一定要檢查語句是否走了索引，如果是全表掃描的話，會對每一個索引加 next-key 鎖，相當於把整個表鎖住了，這是挺嚴重的問題。

完！

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)