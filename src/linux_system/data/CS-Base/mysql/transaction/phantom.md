# MySQL 可重複讀隔離級別，完全解決幻讀了嗎？

大家好，我是小林。

我在[上一篇文章](https://xiaolincoding.com/mysql/transaction/mvcc.html)提到，MySQL InnoDB 引擎的默認隔離級別雖然是「可重複讀」，但是它很大程度上避免幻讀現象（並不是完全解決了），解決的方案有兩種：

- 針對**快照讀**（普通 select 語句），是**通過 MVCC 方式解決了幻讀**，因為可重複讀隔離級別下，事務執行過程中看到的數據，一直跟這個事務啟動時看到的數據是一致的，即使中途有其他事務插入了一條數據，是查詢不出來這條數據的，所以就很好了避免幻讀問題。
- 針對**當前讀**（select ... for update 等語句），是**通過 next-key lock（記錄鎖+間隙鎖）方式解決了幻讀**，因為當執行 select ... for update 語句的時候，會加上 next-key lock，如果有其他事務在 next-key lock 鎖範圍內插入了一條記錄，那麼這個插入語句就會被阻塞，無法成功插入，所以就很好了避免幻讀問題。

這兩個解決方案是很大程度上解決了幻讀現象，但是還是有個別的情況造成的幻讀現象是無法解決的。

這次，就跟大家好好聊這個問題。

## 什麼是幻讀？

首先來看看 MySQL 文檔是怎麼定義幻讀（Phantom Read）的:

***The so-called phantom problem occurs within a transaction when the same query produces different sets of rows at different times. For example, if a SELECT is executed twice, but returns a row the second time that was not returned the first time, the row is a “phantom” row.***

翻譯：當同一個查詢在不同的時間產生不同的結果集時，事務中就會出現所謂的幻象問題。例如，如果 SELECT 執行了兩次，但第二次返回了第一次沒有返回的行，則該行是“幻像”行。

舉個例子，假設一個事務在 T1 時刻和 T2 時刻分別執行了下面查詢語句，途中沒有執行其他任何語句：

```sql
SELECT * FROM t_test WHERE id > 100;
```

只要 T1 和 T2 時刻執行產生的結果集是不相同的，那就發生了幻讀的問題，比如：

- T1 時間執行的結果是有 5 條行記錄，而 T2 時間執行的結果是有 6 條行記錄，那就發生了幻讀的問題。
- T1 時間執行的結果是有 5 條行記錄，而 T2 時間執行的結果是有 4 條行記錄，也是發生了幻讀的問題。

## 快照讀是如何避免幻讀的？

可重複讀隔離級是由 MVCC（多版本併發控制）實現的，實現的方式是啟動事務後，在執行第一個查詢語句後，會創建一個 Read View，**後續的查詢語句利用這個 Read View，通過這個  Read View 就可以在 undo log 版本鏈找到事務開始時的數據，所以事務過程中每次查詢的數據都是一樣的**，即使中途有其他事務插入了新紀錄，是查詢不出來這條數據的，所以就很好了避免幻讀問題。

做個實驗，數據庫表 t_stu 如下，其中 id 為主鍵。

![](https://img-blog.csdnimg.cn/7f9df142b3594daeaaca495abb7133f5.png)

然後在可重複讀隔離級別下，有兩個事務的執行順序如下：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/e576e047dccc47d5a59636ea342750b8.png?)

從這個實驗結果可以看到，即使事務 B 中途插入了一條記錄，事務 A 前後兩次查詢的結果集都是一樣的，並沒有出現所謂的幻讀現象。

## 當前讀是如何避免幻讀的？

MySQL 裡除了普通查詢是快照讀，其他都是**當前讀**，比如 update、insert、delete，這些語句執行前都會查詢最新版本的數據，然後再做進一步的操作。

這很好理解，假設你要 update 一個記錄，另一個事務已經 delete 這條記錄並且提交事務了，這樣不是會產生衝突嗎，所以 update 的時候肯定要知道最新的數據。

另外，`select ... for update` 這種查詢語句是當前讀，每次執行的時候都是讀取最新的數據。 

接下來，我們假設`select ... for update`當前讀是不會加鎖的（實際上是會加鎖的），在做一遍實驗。

![](https://img-blog.csdnimg.cn/1f872ff92b644b5f81cee2dd9188b199.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)


這時候，事務 B 插入的記錄，就會被事務 A 的第二條查詢語句查詢到（因為是當前讀），這樣就會出現前後兩次查詢的結果集合不一樣，這就出現了幻讀。

所以，**Innodb 引擎為瞭解決「可重複讀」隔離級別使用「當前讀」而造成的幻讀問題，就引出了間隙鎖**。

假設，表中有一個範圍 id 為（3，5）間隙鎖，那麼其他事務就無法插入 id = 4 這條記錄了，這樣就有效的防止幻讀現象的發生。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/gap鎖.drawio.png)

舉個具體例子，場景如下：

![](https://img-blog.csdnimg.cn/3af285a8e70f4d4198318057eb955520.png?)

事務 A 執行了這面這條鎖定讀語句後，就在對錶中的記錄加上 id 範圍為 (2, +∞] 的 next-key lock（next-key lock 是間隙鎖+記錄鎖的組合）。

然後，事務 B 在執行插入語句的時候，判斷到插入的位置被事務 A 加了  next-key lock，於是事物 B 會生成一個插入意向鎖，同時進入等待狀態，直到事務 A 提交了事務。這就避免了由於事務 B 插入新記錄而導致事務 A 發生幻讀的現象。

## 幻讀被完全解決了嗎？

**可重複讀隔離級別下雖然很大程度上避免了幻讀，但是還是沒有能完全解決幻讀**。

我舉例一個可重複讀隔離級別發生幻讀現象的場景。

### 第一個發生幻讀現象的場景

還是以這張表作為例子：

![](https://img-blog.csdnimg.cn/7f9df142b3594daeaaca495abb7133f5.png)

事務 A 執行查詢 id = 5 的記錄，此時表中是沒有該記錄的，所以查詢不出來。

```sql
# 事務 A
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from t_stu where id = 5;
Empty set (0.01 sec)
```

然後事務 B 插入一條 id = 5 的記錄，並且提交了事務。

```sql
# 事務 B
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> insert into t_stu values(5, '小美', 18);
Query OK, 1 row affected (0.00 sec)

mysql> commit;
Query OK, 0 rows affected (0.00 sec)
```

此時，**事務 A  更新 id = 5 這條記錄，對沒錯，事務 A 看不到 id = 5 這條記錄，但是他去更新了這條記錄，這場景確實很違和，然後再次查詢 id = 5 的記錄，事務 A 就能看到事務 B 插入的紀錄了，幻讀就是發生在這種違和的場景**。

```sql
# 事務 A
mysql> update t_stu set name = '小林coding' where id = 5;
Query OK, 1 row affected (0.01 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> select * from t_stu where id = 5;
+----+--------------+------+
| id | name         | age  |
+----+--------------+------+
|  5 | 小林coding   |   18 |
+----+--------------+------+
1 row in set (0.00 sec)
```

整個發生幻讀的時序圖如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/幻讀發生.drawio.png)

在可重複讀隔離級別下，事務 A 第一次執行普通的 select 語句時生成了一個 ReadView，之後事務 B 向表中新插入了一條 id = 5 的記錄並提交。接著，事務 A 對 id = 5 這條記錄進行了更新操作，在這個時刻，這條新記錄的 trx_id 隱藏列的值就變成了事務 A 的事務 id，之後事務 A  再使用普通 select 語句去查詢這條記錄時就可以看到這條記錄了，於是就發生了幻讀。

因為這種特殊現象的存在，所以我們認為 **MySQL Innodb 中的 MVCC 並不能完全避免幻讀現象**。

### 第二個發生幻讀現象的場景

除了上面這一種場景會發生幻讀現象之外，還有下面這個場景也會發生幻讀現象。

- T1 時刻：事務 A 先執行「快照讀語句」：select * from t_test where id > 100 得到了 3 條記錄。
- T2 時刻：事務 B 往插入一個 id= 200 的記錄並提交；
- T3 時刻：事務 A 再執行「當前讀語句」 select * from t_test where id > 100 for update 就會得到 4 條記錄，此時也發生了幻讀現象。

**要避免這類特殊場景下發生幻讀的現象的話，就是儘量在開啟事務之後，馬上執行 select ... for update 這類當前讀的語句**，因為它會對記錄加 next-key lock，從而避免其他事務插入一條新記錄。

## 總結

MySQL InnoDB 引擎的可重複讀隔離級別（默認隔離級），根據不同的查詢方式，分別提出了避免幻讀的方案：

- 針對**快照讀**（普通 select 語句），是通過 MVCC 方式解決了幻讀。
- 針對**當前讀**（select ... for update 等語句），是通過 next-key lock（記錄鎖+間隙鎖）方式解決了幻讀。

我舉例了兩個發生幻讀場景的例子。

第一個例子：對於快照讀， MVCC 並不能完全避免幻讀現象。因為當事務 A 更新了一條事務 B 插入的記錄，那麼事務 A 前後兩次查詢的記錄條目就不一樣了，所以就發生幻讀。

第二個例子：對於當前讀，如果事務開啟後，並沒有執行當前讀，而是先快照讀，然後這期間如果其他事務插入了一條記錄，那麼事務後續使用當前讀進行查詢的時候，就會發現兩次查詢的記錄條目就不一樣了，所以就發生幻讀。

所以，**MySQL 可重複讀隔離級別並沒有徹底解決幻讀，只是很大程度上避免了幻讀現象的發生。**

要避免這類特殊場景下發生幻讀的現象的話，就是儘量在開啟事務之後，馬上執行 select ... for update 這類當前讀的語句，因為它會對記錄加 next-key lock，從而避免其他事務插入一條新記錄。

----

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)