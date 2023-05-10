# MySQL 死鎖了，怎麼辦？

大家好，我是小林。

說個很早之前自己遇到過數據庫死鎖問題。

有個業務主要邏輯就是新增訂單、修改訂單、查詢訂單等操作。然後因為訂單是不能重複的，所以當時在新增訂單的時候做了冪等性校驗，做法就是在新增訂單記錄之前，先通過 `select ... for update` 語句查詢訂單是否存在，如果不存在才插入訂單記錄。

而正是因為這樣的操作，當業務量很大的時候，就可能會出現死鎖。

接下來跟大家聊下**為什麼會發生死鎖，以及怎麼避免死鎖**。

## 死鎖的發生

本次案例使用存儲引擎 Innodb，隔離級別為可重複讀（RR）。

接下來，我用實戰的方式來帶大家看看死鎖是怎麼發生的。

我建了一張訂單表，其中 id 字段為主鍵索引，order_no 字段普通索引，也就是非唯一索引：

```sql
CREATE TABLE `t_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_no` int DEFAULT NULL,
  `create_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index_order` (`order_no`) USING BTREE
) ENGINE=InnoDB ;
```

然後，先 `t_order` 表裡現在已經有了 6 條記錄：

![圖片](https://img-blog.csdnimg.cn/img_convert/54fc00f9f87a60ab7b5ba92d824a892d.png)

假設這時有兩事務，一個事務要插入訂單 1007 ，另外一個事務要插入訂單 1008，因為需要對訂單做冪等性校驗，所以兩個事務先要查詢該訂單是否存在，不存在才插入記錄，過程如下：

![](https://img-blog.csdnimg.cn/img_convert/90c1e01d0345de639e3426cea0390e80.png)

可以看到，兩個事務都陷入了等待狀態（前提沒有打開死鎖檢測），也就是發生了死鎖，因為都在相互等待對方釋放鎖。

這裡在查詢記錄是否存在的時候，使用了 `select ... for update` 語句，目的為了防止事務執行的過程中，有其他事務插入了記錄，而出現幻讀的問題。

如果沒有使用 `select ... for update` 語句，而使用了單純的 select 語句，如果是兩個訂單號一樣的請求同時進來，就會出現兩個重複的訂單，有可能出現幻讀，如下圖：

![](https://img-blog.csdnimg.cn/img_convert/8ae18f10f1a89aac5e93f0e9794e469e.png)

## 為什麼會產生死鎖？

可重複讀隔離級別下，是存在幻讀的問題。

**Innodb 引擎為瞭解決「可重複讀」隔離級別下的幻讀問題，就引出了 next-key 鎖**，它是記錄鎖和間隙鎖的組合。

- Record Lock，記錄鎖，鎖的是記錄本身；
- Gap Lock，間隙鎖，鎖的就是兩個值之間的空隙，以防止其他事務在這個空隙間插入新的數據，從而避免幻讀現象。

普通的 select 語句是不會對記錄加鎖的，因為它是通過 MVCC 的機制實現的快照讀，如果要在查詢時對記錄加行鎖，可以使用下面這兩個方式：

```sql
begin;
//對讀取的記錄加共享鎖
select ... lock in share mode;
commit; //鎖釋放

begin;
//對讀取的記錄加排他鎖
select ... for update;
commit; //鎖釋放
```

行鎖的釋放時機是在事務提交（commit）後，鎖就會被釋放，並不是一條語句執行完就釋放行鎖。

比如，下面事務 A 查詢語句會鎖住 `(2, +∞]` 範圍的記錄，然後期間如果有其他事務在這個鎖住的範圍插入數據就會被阻塞。

![圖片](https://img-blog.csdnimg.cn/img_convert/8d1dfbab758fe7e4c58563fca9ccb6d4.png)

next-key 鎖的加鎖規則其實挺複雜的，在一些場景下會退化成記錄鎖或間隙鎖，我之前也寫一篇加鎖規則，詳細可以看這篇：[MySQL 是怎麼加鎖的？](https://xiaolincoding.com/mysql/lock/how_to_lock.html)

需要注意的是，如果 update 語句的 where 條件沒有用到索引列，那麼就會全表掃描，在一行行掃描的過程中，不僅給行記錄加上了行鎖，還給行記錄兩邊的空隙也加上了間隙鎖，相當於鎖住整個表，然後直到事務結束才會釋放鎖。

所以在線上千萬不要執行沒有帶索引條件的 update 語句，不然會造成業務停滯，我有個讀者就因為幹了這個事情，然後被老闆教育了一波，詳細可以看這篇：[update 沒加索引會鎖全表？](https://xiaolincoding.com/mysql/lock/update_index.html)

回到前面死鎖的例子。

![](https://img-blog.csdnimg.cn/img_convert/90c1e01d0345de639e3426cea0390e80.png)

事務 A 在執行下面這條語句的時候：

```sql
select id from t_order where order_no = 1007 for update;
```

我們可以通過 `select * from performance_schema.data_locks\G;` 這條語句，查看事務執行 SQL 過程中加了什麼鎖。

![](https://img-blog.csdnimg.cn/1cf8614eba3b45b9874dc6204b4d0cd1.png)

從上圖可以看到，共加了兩個鎖，分別是：

- 表鎖：X 類型的意向鎖；
- 行鎖：X 類型的 next-key 鎖；

這裡我們重點關注行鎖，圖中 LOCK_TYPE 中的 RECORD 表示行級鎖，而不是記錄鎖的意思，通過 LOCK_MODE 可以確認是 next-key 鎖，還是間隙鎖，還是記錄鎖：

- 如果 LOCK_MODE 為 `X`，說明是 X 型的 next-key 鎖；
- 如果 LOCK_MODE 為 `X, REC_NOT_GAP`，說明是 X 型的記錄鎖；
- 如果 LOCK_MODE 為 `X, GAP`，說明是 X 型的間隙鎖；

**因此，此時事務 A 在二級索引（INDEX_NAME : index_order）上加的是 X 型的 next-key 鎖，鎖範圍是`(1006, +∞]`**。

 next-key 鎖的範圍 (1006, +∞]，是怎麼確定的？

根據我的經驗，如果 LOCK_MODE 是 next-key 鎖或者間隙鎖，那麼 LOCK_DATA 就表示鎖的範圍最右值，此次的事務 A 的 LOCK_DATA 是 supremum pseudo-record，表示的是 +∞。然後鎖範圍的最左值是 t_order 表中最後一個記錄的 index_order 的值，也就是 1006。因此，next-key 鎖的範圍 (1006, +∞]。

::: tip

有的讀者問，[MySQL 是怎麼加鎖的？](https://xiaolincoding.com/mysql/lock/how_to_lock.html)這篇文章講非唯一索引等值查詢時，說「當查詢的記錄不存在時，加 next-key lock，然後會退化為間隙鎖」。為什麼上面事務 A 的 next-key lock 並沒有退化為間隙鎖？

如果表中最後一個記錄的 order_no 為 1005，那麼等值查詢 order_no =  1006（不存在），就是 next key lock，如上面事務 A 的情況。

如果表中最後一個記錄的 order_no 為 1010，那麼等值查詢  order_no = 1006（不存在），就是間隙鎖，比如下圖：

![](https://img-blog.csdnimg.cn/fb6709207ac445ddbc175e3cdf993ff2.png)

:::

當事務 B 往事務 A  next-key 鎖的範圍 (1006, +∞] 裡插入 id = 1008 的記錄就會被鎖住：

```sql
Insert into t_order (order_no, create_date) values (1008, now());
```

因為當我們執行以下插入語句時，會在插入間隙上獲取插入意向鎖，**而插入意向鎖與間隙鎖是衝突的，所以當其它事務持有該間隙的間隙鎖時，需要等待其它事務釋放間隙鎖之後，才能獲取到插入意向鎖。而間隙鎖與間隙鎖之間是兼容的，所以所以兩個事務中 `select ... for update` 語句並不會相互影響**。

案例中的事務 A 和事務 B 在執行完後 `select ... for update` 語句後都持有範圍為`(1006,+∞]`的next-key 鎖，而接下來的插入操作為了獲取到插入意向鎖，都在等待對方事務的間隙鎖釋放，於是就造成了循環等待，導致死鎖。

> 為什麼間隙鎖與間隙鎖之間是兼容的？

在MySQL官網上還有一段非常關鍵的描述：

*Gap locks in InnoDB are “purely inhibitive”, which means that their only purpose is to prevent other transactions from Inserting to the gap. Gap locks can co-exist. A gap lock taken by one transaction does not prevent another transaction from taking a gap lock on the same gap. There is no difference between shared and exclusive gap locks. They do not conflict with each other, and they perform the same function.*

**間隙鎖的意義只在於阻止區間被插入**，因此是可以共存的。**一個事務獲取的間隙鎖不會阻止另一個事務獲取同一個間隙範圍的間隙鎖**，共享和排他的間隙鎖是沒有區別的，他們相互不衝突，且功能相同，即兩個事務可以同時持有包含共同間隙的間隙鎖。

這裡的共同間隙包括兩種場景：

- 其一是兩個間隙鎖的間隙區間完全一樣；
- 其二是一個間隙鎖包含的間隙區間是另一個間隙鎖包含間隙區間的子集。

但是有一點要注意，**next-key lock 是包含間隙鎖+記錄鎖的，如果一個事務獲取了 X 型的 next-key lock，那麼另外一個事務在獲取相同範圍的 X 型的 next-key lock 時，是會被阻塞的**。

比如，一個事務持有了範圍為 (1, 10] 的 X 型的 next-key lock，那麼另外一個事務在獲取相同範圍的 X 型的 next-key lock 時，就會被阻塞。

雖然相同範圍的間隙鎖是多個事務相互兼容的，但對於記錄鎖，我們是要考慮 X 型與 S 型關係。X 型的記錄鎖與 X 型的記錄鎖是衝突的，比如一個事務執行了 select ... where id = 1 for update，後一個事務在執行這條語句的時候，就會被阻塞的。

但是還要注意！對於這種範圍為 (1006, +∞] 的 next-key lock，兩個事務是可以同時持有的，不會衝突。因為 +∞ 並不是一個真實的記錄，自然就不需要考慮 X 型與 S 型關係。

> 插入意向鎖是什麼？

注意！插入意向鎖名字雖然有意向鎖，但是它並不是意向鎖，它是一種特殊的間隙鎖。

在MySQL的官方文檔中有以下重要描述：

*An Insert intention lock is a type of gap lock set by Insert operations prior to row Insertion. This lock signals the intent to Insert in such a way that multiple transactions Inserting into the same index gap need not wait for each other if they are not Inserting at the same position within the gap. Suppose that there are index records with values of 4 and 7. Separate transactions that attempt to Insert values of 5 and 6, respectively, each lock the gap between 4 and 7 with Insert intention locks prior to obtaining the exclusive lock on the Inserted row, but do not block each other because the rows are nonconflicting.*

這段話表明儘管**插入意向鎖是一種特殊的間隙鎖，但不同於間隙鎖的是，該鎖只用於併發插入操作**。

如果說間隙鎖鎖住的是一個區間，那麼「插入意向鎖」鎖住的就是一個點。因而從這個角度來說，插入意向鎖確實是一種特殊的間隙鎖。

插入意向鎖與間隙鎖的另一個非常重要的差別是：儘管「插入意向鎖」也屬於間隙鎖，但兩個事務卻不能在同一時間內，一個擁有間隙鎖，另一個擁有該間隙區間內的插入意向鎖（當然，插入意向鎖如果不在間隙鎖區間內則是可以的）。

另外，我補充一點，插入意向鎖的生成時機：

- 每插入一條新記錄，都需要看一下待插入記錄的下一條記錄上是否已經被加了間隙鎖，如果已加間隙鎖，此時會生成一個插入意向鎖，然後鎖的狀態設置為等待狀態（*PS：MySQL 加鎖時，是先生成鎖結構，然後設置鎖的狀態，如果鎖狀態是等待狀態，並不是意味著事務成功獲取到了鎖，只有當鎖狀態為正常狀態時，才代表事務成功獲取到了鎖*），現象就是 Insert 語句會被阻塞。

## Insert 語句是怎麼加行級鎖的？

Insert 語句在正常執行時是不會生成鎖結構的，它是靠聚簇索引記錄自帶的 trx_id 隱藏列來作為**隱式鎖**來保護記錄的。

>  什麼是隱式鎖？

當事務需要加鎖的時，如果這個鎖不可能發生衝突，InnoDB會跳過加鎖環節，這種機制稱為隱式鎖。隱式鎖是 InnoDB 實現的一種延遲加鎖機制，其特點是隻有在可能發生衝突時才加鎖，從而減少了鎖的數量，提高了系統整體性能。

隱式鎖就是在 Insert 過程中不加鎖，只有在特殊情況下，才會將隱式鎖轉換為顯式鎖，這裡我們列舉兩個場景。

- 如果記錄之間加有間隙鎖，為了避免幻讀，此時是不能插入記錄的；
- 如果 Insert 的記錄和已有記錄存在唯一鍵衝突，此時也不能插入記錄；

### 1、記錄之間加有間隙鎖

每插入一條新記錄，都需要看一下待插入記錄的下一條記錄上是否已經被加了間隙鎖，如果已加間隙鎖，此時會生成一個插入意向鎖，然後鎖的狀態設置為等待狀態（*PS：MySQL 加鎖時，是先生成鎖結構，然後設置鎖的狀態，如果鎖狀態是等待狀態，並不是意味著事務成功獲取到了鎖，只有當鎖狀態為正常狀態時，才代表事務成功獲取到了鎖*），現象就是 Insert 語句會被阻塞。

舉個例子，現在 t_order 表中，只有這些數據，**order_no 是二級索引**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/5條數據.png)

現在，事務 A 執行了下面這條語句。

```sql
# 事務 A
mysql> begin;
Query OK, 0 rows affected (0.01 sec)

mysql> select * from t_order where order_no = 1006 for update;
Empty set (0.01 sec)
```

接著，我們執行 `select * from performance_schema.data_locks\G;` 語句  ，確定事務 A 加了什麼類型的鎖，這裡只關注在記錄上加鎖的類型。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務A間隙鎖.png)

本次的例子加的是 next-key 鎖（記錄鎖+間隙鎖），鎖範圍是`（1005, +∞]`。

然後，有個事務 B 在這個間隙鎖中，插入了一個記錄，那麼此時該事務 B 就會被阻塞：

```sql
# 事務 B 插入一條記錄
mysql> begin;
Query OK, 0 rows affected (0.01 sec)

mysql> insert into t_order(order_no, create_date) values(1010,now());
### 阻塞狀態。。。。
```

接著，我們執行 `select * from performance_schema.data_locks\G;` 語句  ，確定事務 B 加了什麼類型的鎖，這裡只關注在記錄上加鎖的類型。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務b插入意向鎖.png)

可以看到，事務 B 的狀態為等待狀態（LOCK_STATUS: WAITING），因為向事務 A 生成的 next-key 鎖（記錄鎖+間隙鎖）範圍`（1005, +∞]` 中插入了一條記錄，所以事務 B 的插入操作生成了一個插入意向鎖（` LOCK_MODE: X,INSERT_INTENTION     `），鎖的狀態是等待狀態，意味著事務 B 並沒有成功獲取到插入意向鎖，因此事務 B 發生阻塞。

### 2、遇到唯一鍵衝突

如果在插入新記錄時，插入了一個與「已有的記錄的主鍵或者唯一二級索引列值相同」的記錄（不過可以有多條記錄的唯一二級索引列的值同時為NULL，這裡不考慮這種情況），此時插入就會失敗，然後對於這條記錄加上了 **S 型的鎖**。

至於是行級鎖的類型是記錄鎖，還是 next-key 鎖，跟是「主鍵衝突」還是「唯一二級索引衝突」有關係。

如果主鍵索引重複：

- 當隔離級別為**讀已提交**時，插入新記錄的事務會給已存在的主鍵值重複的聚簇索引記錄**添加 S 型記錄鎖**。
- 當隔離級別是**可重複讀**（默認隔離級別），插入新記錄的事務會給已存在的主鍵值重複的聚簇索引記錄**添加 S 型記錄鎖**。

如果唯一二級索引列重複：

- **不論是哪個隔離級別**，插入新記錄的事務都會給已存在的二級索引列值重複的二級索引記錄**添加 S 型 next-key 鎖**。對的，沒錯，即使是讀已提交隔離級別也是加 next-key 鎖，這是讀已提交隔離級別中為數不多的給記錄添加間隙鎖的場景。至於為什麼要加 next-key 鎖，我也沒找到合理的解釋。

#### 主鍵索引衝突

下面舉個「主鍵衝突」的例子，MySQL 8.0 版本，事務隔離級別為可重複讀（默認隔離級別）。

t_order 表中的 id 字段為主鍵索引，並且已經存在 id 值為 5 的記錄，此時有個事務，插入了一條 id 為 5 的記錄，就會報主鍵索引衝突的錯誤。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/主鍵衝突.png)

但是除了報錯之外，還做一個很重要的事情，就是對 id 為 5 的這條記錄加上了 **S 型的記錄鎖**。

可以執行 `select * from performance_schema.data_locks\G;` 語句，確定事務加了什麼鎖。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/主鍵衝突鎖.png)

可以看到，主鍵索引為 5 （LOCK_DATA）的這條記錄中加了鎖類型為 S 型的記錄鎖。注意，這裡 LOCK_TYPE 中的 RECORD 表示行級鎖，而不是記錄鎖的意思。如果是 S 型記錄鎖的話，LOCK_MODE 會顯示 `S, REC_NOT_GAP`。

所以，在隔離級別是「可重複讀」的情況下，如果在插入數據的時候，發生了主鍵索引衝突，插入新記錄的事務會給已存在的主鍵值重複的聚簇索引記錄**添加 S 型記錄鎖**。

#### 唯一二級索引衝突

下面舉個「唯一二級索引衝突」的例子，MySQL 8.0 版本，事務隔離級別為可重複讀（默認隔離級別）。

t_order 表中的 order_no 字段為唯一二級索引，並且已經存在 order_no 值為 1001 的記錄，此時事務 A，插入了 order_no 為 1001 的記錄，就出現了報錯。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/插入失敗.png)

但是除了報錯之外，還做一個很重要的事情，就是對 order_no 值為 1001 這條記錄加上了 **S 型的 next-key 鎖**。

我們可以執行 `select * from performance_schema.data_locks\G;` 語句  ，確定事務加了什麼類型的鎖，這裡只關注在記錄上加鎖的類型。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/s類型鎖.png)

可以看到，**index_order 二級索引加了 S 型的 next-key 鎖，範圍是(-∞, 1001]**。注意，這裡 LOCK_TYPE 中的 RECORD 表示行級鎖，而不是記錄鎖的意思。如果是記錄鎖的話，LOCK_MODE 會顯示 `S, REC_NOT_GAP`。

此時，事務 B 執行了 select * from t_order where order_no = 1001 for update;  就會阻塞，因為這條語句想加 X 型的鎖，是與 S 型的鎖是衝突的，所以就會被阻塞。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/唯一索引衝突.drawio.png)

我們也可以從 performance_schema.data_locks 這個表中看到，事務 B 的狀態（LOCK_STATUS）是等待狀態，加鎖的類型 X 型的記錄鎖（LOCK_MODE: X,REC_NOT_GAP    ）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務b等待狀態.png)

上面的案例是針對唯一二級索引重複而插入失敗的場景。

> 接下來，分析兩個事務執行過程中，執行了相同的 insert 語句的場景。

現在 t_order 表中，只有這些數據，**order_no 為唯一二級索引**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/5條數據.png)

在隔離級別可重複讀的情況下，開啟兩個事務，前後執行相同的  Insert 語句，此時**事務 B 的  Insert 語句會發生阻塞**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/唯一索引加鎖.drawio.png)

兩個事務的加鎖過程：

- 事務 A 先插入 order_no 為 1006 的記錄，可以插入成功，此時對應的唯一二級索引記錄被「隱式鎖」保護，此時還沒有實際的鎖結構（執行完這裡的時候，你可以看查 performance_schema.data_locks 信息，可以看到這條記錄是沒有加任何鎖的）；
- 接著，事務 B 也插入 order_no 為 1006 的記錄，由於事務 A 已經插入 order_no 值為 1006 的記錄，所以事務 B 在插入二級索引記錄時會遇到重複的唯一二級索引列值，此時事務 B 想獲取一個 S 型 next-key 鎖，但是事務 A 並未提交，**事務 A 插入的 order_no 值為 1006 的記錄上的「隱式鎖」會變「顯示鎖」且鎖類型為  X 型的記錄鎖，所以事務 B 向獲取 S 型 next-key 鎖時會遇到鎖衝突，事務 B 進入阻塞狀態**。

我們可以執行 `select * from performance_schema.data_locks\G;` 語句  ，確定事務加了什麼類型的鎖，這裡只關注在記錄上加鎖的類型。

先看事務 A 對 order_no 為 1006 的記錄加了什麼鎖？

從下圖可以看到，**事務 A  對 order_no 為 1006 記錄加上了類型為  X 型的記錄鎖**（*注意，這個是在執行事務 B 之後才產生的鎖，沒執行事務 B 之前，該記錄還是隱式鎖*）。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務a顯示鎖.png)

然後看事務 B 想對 order_no 為 1006 的記錄加什麼鎖？

從下圖可以看到，**事務 B 想對 order_no 為 1006 的記錄加 S 型的 next-key 鎖，但是由於事務 A 在該記錄上持有了 X 型的記錄鎖，這兩個鎖是衝突的，所以導致事務 B 處於等待狀態**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/鎖/事務b等待.png)

從這個實驗可以得知，併發多個事務的時候，第一個事務插入的記錄，並不會加鎖，而是會用隱式鎖保護唯一二級索引的記錄。

但是當第一個事務還未提交的時候，有其他事務插入了與第一個事務相同的記錄，第二個事務就會**被阻塞**，**因為此時第一事務插入的記錄中的隱式鎖會變為顯示鎖且類型是 X 型的記錄鎖，而第二個事務是想對該記錄加上 S 型的 next-key 鎖，X 型與 S 型的鎖是衝突的**，所以導致第二個事務會等待，直到第一個事務提交後，釋放了鎖。

如果 order_no 不是唯一二級索引，那麼兩個事務，前後執行相同的  Insert 語句，是不會發生阻塞的，就如前面的這個例子。

![](https://img-blog.csdnimg.cn/img_convert/8ae18f10f1a89aac5e93f0e9794e469e.png)

## 如何避免死鎖？

死鎖的四個必要條件：**互斥、佔有且等待、不可強佔用、循環等待**。只要系統發生死鎖，這些條件必然成立，但是隻要破壞任意一個條件就死鎖就不會成立。

在數據庫層面，有兩種策略通過「打破循環等待條件」來解除死鎖狀態：

- **設置事務等待鎖的超時時間**。當一個事務的等待時間超過該值後，就對這個事務進行回滾，於是鎖就釋放了，另一個事務就可以繼續執行了。在 InnoDB 中，參數 `innodb_lock_wait_timeout` 是用來設置超時時間的，默認值時 50 秒。

  當發生超時後，就出現下面這個提示：

![圖片](https://img-blog.csdnimg.cn/img_convert/c296c1889f0101d335699311b4ef20a8.png)

- **開啟主動死鎖檢測**。主動死鎖檢測在發現死鎖後，主動回滾死鎖鏈條中的某一個事務，讓其他事務得以繼續執行。將參數 `innodb_deadlock_detect` 設置為 on，表示開啟這個邏輯，默認就開啟。

  當檢測到死鎖後，就會出現下面這個提示：

![圖片](https://img-blog.csdnimg.cn/img_convert/f380ef357d065498d8d54ad07f145e09.png)

上面這個兩種策略是「當有死鎖發生時」的避免方式。

我們可以迴歸業務的角度來預防死鎖，對訂單做冪等性校驗的目的是為了保證不會出現重複的訂單，那我們可以直接將 order_no 字段設置為唯一索引列，利用它的唯一性來保證訂單表不會出現重複的訂單，不過有一點不好的地方就是在我們插入一個已經存在的訂單記錄時就會拋出異常。

------

最後說個段子：

面試官: 解釋下什麼是死鎖?

應聘者: 你錄用我,我就告訴你

面試官: 你告訴我,我就錄用你

應聘者: 你錄用我,我就告訴你

面試官: 臥槽滾！

**...........**

---

參考資料：

- 《MySQL 是怎樣運行的？》
- http://mysql.taobao.org/monthly/2020/09/06/

----

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)