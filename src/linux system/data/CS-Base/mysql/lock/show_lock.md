# 字節面試：加了什麼鎖，導致死鎖的？

大家好，我是小林。

之前收到讀者面試字節時，被問到一個關於 MySQL 的問題。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/字節mysql面試題.png)

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/提問.png)

如果對 MySQL 加鎖機制比較熟悉的同學，應該一眼就能看出**會發生死鎖**，但是具體加了什麼鎖而導致死鎖，是需要我們具體分析的。

接下來，就跟聊聊上面兩個事務執行 SQL 語句的過程中，加了什麼鎖，從而導致死鎖的。

## 準備工作

先創建一張 t_student 表，假設除了 id 字段，其他字段都是普通字段。

```sql
CREATE TABLE `t_student` (
  `id` int NOT NULL,
  `no` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `score` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

然後，插入相關的數據後，t_student 表中的記錄如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/t_student.png)

## 開始實驗

在實驗開始前，先說明下實驗環境：

- MySQL 版本：8.0.26
- 隔離級別：可重複讀（RR）

啟動兩個事務，按照題目的 SQL 執行順序，過程如下表格：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/ab事務死鎖.drawio.png)

可以看到，事務 A 和 事務 B 都在執行  insert 語句後，都陷入了等待狀態（前提沒有打開死鎖檢測），也就是發生了死鎖，因為都在相互等待對方釋放鎖。

## 為什麼會發生死鎖？

我們可以通過 `select * from performance_schema.data_locks\G;` 這條語句，查看事務執行 SQL 過程中加了什麼鎖。

接下來，針對每一條 SQL 語句分析具體加了什麼鎖。

### Time 1 階段加鎖分析

Time 1 階段，事務 A 執行以下語句：

```sql
# 事務 A
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> update t_student set score = 100 where id = 25;
Query OK, 0 rows affected (0.01 sec)
Rows matched: 0  Changed: 0  Warnings: 0
```

然後執行 `select * from performance_schema.data_locks\G;` 這條語句，查看事務 A 此時加了什麼鎖。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務a的鎖.png)

從上圖可以看到，共加了兩個鎖，分別是：

- 表鎖：X 類型的意向鎖；
- 行鎖：X 類型的間隙鎖；

這裡我們重點關注行鎖，圖中 LOCK_TYPE 中的 RECORD 表示行級鎖，而不是記錄鎖的意思，通過 LOCK_MODE 可以確認是 next-key 鎖，還是間隙鎖，還是記錄鎖：

- 如果 LOCK_MODE 為 `X`，說明是 next-key 鎖；
- 如果 LOCK_MODE 為 `X, REC_NOT_GAP`，說明是記錄鎖；
- 如果 LOCK_MODE 為 `X, GAP`，說明是間隙鎖；

**因此，此時事務 A 在主鍵索引（INDEX_NAME : PRIMARY）上加的是間隙鎖，鎖範圍是`(20, 30)`**。

> 間隙鎖的範圍`(20, 30)` ，是怎麼確定的？

根據我的經驗，如果 LOCK_MODE 是 next-key 鎖或者間隙鎖，那麼 LOCK_DATA 就表示鎖的範圍最右值，此次的事務 A 的 LOCK_DATA 是 30。

然後鎖範圍的最左值是 t_student 表中 id 為 30 的上一條記錄的 id 值，即 20。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/403f9c1012e84a4c83bfb2fc3990f177.png)

因此，間隙鎖的範圍`(20, 30)`。

### Time 2 階段加鎖分析

Time 2 階段，事務 B 執行以下語句：

```sql
# 事務 B
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> update t_student set score = 100 where id = 26;
Query OK, 0 rows affected (0.01 sec)
Rows matched: 0  Changed: 0  Warnings: 0
```

然後執行 `select * from performance_schema.data_locks\G;` 這條語句，查看事務 B 此時加了什麼鎖。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/44277cfefbd6446db861bfb81a1e4a59.png)

從上圖可以看到，行鎖是 X 類型的間隙鎖，間隙鎖的範圍是`(20, 30)`。

> 事務 A 和 事務 B 的間隙鎖範圍都是一樣的，為什麼不會衝突？

兩個事務的間隙鎖之間是相互兼容的，不會產生衝突。

在MySQL官網上還有一段非常關鍵的描述：

*Gap locks in InnoDB are “purely inhibitive”, which means that their only purpose is to prevent other transactions from Inserting to the gap. Gap locks can co-exist. A gap lock taken by one transaction does not prevent another transaction from taking a gap lock on the same gap. There is no difference between shared and exclusive gap locks. They do not conflict with each other, and they perform the same function.*

**間隙鎖的意義只在於阻止區間被插入**，因此是可以共存的。**一個事務獲取的間隙鎖不會阻止另一個事務獲取同一個間隙範圍的間隙鎖**，共享（S型）和排他（X型）的間隙鎖是沒有區別的，他們相互不衝突，且功能相同。

### Time 3 階段加鎖分析

Time 3，事務 A 插入了一條記錄：

```sql
# Time 3 階段，事務 A 插入了一條記錄
mysql> insert into t_student(id, no, name, age,score) value (25, 'S0025', 'sony', 28, 90);
    /// 阻塞等待......
```

此時，事務 A 就陷入了等待狀態。

然後執行 `select * from performance_schema.data_locks\G;` 這條語句，查看事務 A 在獲取什麼鎖而導致被阻塞。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務a等待中.png)

可以看到，事務 A 的狀態為等待狀態（LOCK_STATUS: WAITING），因為向事務 B 生成的間隙鎖（範圍 `(20, 30)`）中插入了一條記錄，所以事務 A 的插入操作生成了一個插入意向鎖（`LOCK_MODE:INSERT_INTENTION`）。

> 插入意向鎖是什麼？

注意！插入意向鎖名字裡雖然有意向鎖這三個字，但是它並不是意向鎖，它屬於行級鎖，是一種特殊的間隙鎖。

在MySQL的官方文檔中有以下重要描述：

*An Insert intention lock is a type of gap lock set by Insert operations prior to row Insertion. This lock signals the intent to Insert in such a way that multiple transactions Inserting into the same index gap need not wait for each other if they are not Inserting at the same position within the gap. Suppose that there are index records with values of 4 and 7. Separate transactions that attempt to Insert values of 5 and 6, respectively, each lock the gap between 4 and 7 with Insert intention locks prior to obtaining the exclusive lock on the Inserted row, but do not block each other because the rows are nonconflicting.*

這段話表明儘管**插入意向鎖是一種特殊的間隙鎖，但不同於間隙鎖的是，該鎖只用於併發插入操作**。

如果說間隙鎖鎖住的是一個區間，那麼「插入意向鎖」鎖住的就是一個點。因而從這個角度來說，插入意向鎖確實是一種特殊的間隙鎖。

插入意向鎖與間隙鎖的另一個非常重要的差別是：**儘管「插入意向鎖」也屬於間隙鎖，但兩個事務卻不能在同一時間內，一個擁有間隙鎖，另一個擁有該間隙區間內的插入意向鎖（當然，插入意向鎖如果不在間隙鎖區間內則是可以的）。所以，插入意向鎖和間隙鎖之間是衝突的**。

另外，我補充一點，插入意向鎖的生成時機：

- 每插入一條新記錄，都需要看一下待插入記錄的下一條記錄上是否已經被加了間隙鎖，如果已加間隙鎖，此時會生成一個插入意向鎖，然後鎖的狀態設置為等待狀態（*PS：MySQL 加鎖時，是先生成鎖結構，然後設置鎖的狀態，如果鎖狀態是等待狀態，並不是意味著事務成功獲取到了鎖，只有當鎖狀態為正常狀態時，才代表事務成功獲取到了鎖*），現象就是 Insert 語句會被阻塞。

### Time 4 階段加鎖分析

Time 4，事務 B 插入了一條記錄：

```sql
# Time 4 階段，事務 B 插入了一條記錄
mysql> insert into t_student(id, no, name, age,score) value (26, 'S0026', 'ace', 28, 90);
    /// 阻塞等待......
```

此時，事務 B 就陷入了等待狀態。

然後執行 `select * from performance_schema.data_locks\G;` 這條語句，查看事務 B 在獲取什麼鎖而導致被阻塞。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務b等待中.png)

可以看到，事務 B 在生成插入意向鎖時而導致被阻塞，這是因為事務 B 向事務 A 生成的範圍為 (20, 30) 的間隙鎖插入了一條記錄，而插入意向鎖和間隙鎖是衝突的，所以事務  B 在獲取插入意向鎖時就陷入了等待狀態。

> 最後回答，為什麼會發生死鎖？

本次案例中，事務 A 和事務 B 在執行完後 update 語句後都持有範圍為`(20, 30）`的間隙鎖，而接下來的插入操作為了獲取到插入意向鎖，都在等待對方事務的間隙鎖釋放，於是就造成了循環等待，滿足了死鎖的四個條件：**互斥、佔有且等待、不可強佔用、循環等待**，因此發生了死鎖。

## 總結

兩個事務即使生成的間隙鎖的範圍是一樣的，也不會發生衝突，因為間隙鎖目的是為了防止其他事務插入數據，因此間隙鎖與間隙鎖之間是相互兼容的。

在執行插入語句時，如果插入的記錄在其他事務持有間隙鎖範圍內，插入語句就會被阻塞，因為插入語句在碰到間隙鎖時，會生成一個插入意向鎖，然後插入意向鎖和間隙鎖之間是互斥的關係。

如果兩個事務分別向對方持有的間隙鎖範圍內插入一條記錄，而插入操作為了獲取到插入意向鎖，都在等待對方事務的間隙鎖釋放，於是就造成了循環等待，滿足了死鎖的四個條件：**互斥、佔有且等待、不可強佔用、循環等待**，因此發生了死鎖。

## 讀者問答

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/f4d4d7fdb9074b098b1077acff698aea.png)

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)