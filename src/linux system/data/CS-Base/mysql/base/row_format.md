# MySQL 一行記錄是怎麼存儲的？

大家好，我是小林。

之前有位讀者在面字節的時候，被問到這麼個問題：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/讀者問題.jpeg)

如果你知道 MySQL 一行記錄的存儲結構，那麼這個問題對你沒什麼難度。

如果你不知道也沒關係，這次我跟大家聊聊 **MySQL 一行記錄是怎麼存儲的？**

知道了這個之後，除了能應解鎖前面這道面試題，你還會解鎖這些面試題：

- MySQL 的 NULL 值會佔用空間嗎？
- MySQL 怎麼知道 varchar(n) 實際佔用數據的大小？
- varchar(n) 中 n 最大取值為多少？
- 行溢出後，MySQL 是怎麼處理的？

這些問題看似毫不相干，其實都是在圍繞「 MySQL 一行記錄的存儲結構」這一個知識點，所以攻破了這個知識點後，這些問題就引刃而解了。

好了，話不多說，發車！

## MySQL 的數據存放在哪個文件？

大家都知道 MySQL 的數據都是保存在磁盤的，那具體是保存在哪個文件呢？

MySQL 存儲的行為是由存儲引擎實現的，MySQL 支持多種存儲引擎，不同的存儲引擎保存的文件自然也不同。

InnoDB 是我們常用的存儲引擎，也是 MySQL 默認的存儲引擎。所以，本文主要以 InnoDB 存儲引擎展開討論。

先來看看 MySQL 數據庫的文件存放在哪個目錄？

``` sql
mysql> SHOW VARIABLES LIKE 'datadir';
+---------------+-----------------+
| Variable_name | Value           |
+---------------+-----------------+
| datadir       | /var/lib/mysql/ |
+---------------+-----------------+
1 row in set (0.00 sec)
```

我們每創建一個 database（數據庫） 都會在 /var/lib/mysql/ 目錄裡面創建一個以 database 為名的目錄，然後保存表結構和表數據的文件都會存放在這個目錄裡。

比如，我這裡有一個名為 my_test 的 database，該 database 裡有一張名為 t_order 數據庫表。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/database.png)

然後，我們進入 /var/lib/mysql/my_test 目錄，看看裡面有什麼文件？

```shell
[root@xiaolin ~]#ls /var/lib/mysql/my_test
db.opt  
t_order.frm  
t_order.ibd
```

可以看到，共有三個文件，這三個文件分別代表著：

- db.opt，用來存儲當前數據庫的默認字符集和字符校驗規則。
- t_order.frm ，t_order 的**表結構**會保存在這個文件。在 MySQL 中建立一張表都會生成一個.frm 文件，該文件是用來保存每個表的元數據信息的，主要包含表結構定義。
- t_order.ibd，t_order 的**表數據**會保存在這個文件。表數據既可以存在共享表空間文件（文件名：ibdata1）裡，也可以存放在獨佔表空間文件（文件名：表名字.ibd）。這個行為是由參數 innodb_file_per_table 控制的，若設置了參數 innodb_file_per_table 為 1，則會將存儲的數據、索引等信息單獨存儲在一個獨佔表空間，從 MySQL 5.6.6 版本開始，它的默認值就是 1 了，因此從這個版本之後， MySQL 中每一張表的數據都存放在一個獨立的 .ibd 文件。

好了，現在我們知道了一張數據庫表的數據是保存在「 表名字.ibd 」的文件裡的，這個文件也稱為獨佔表空間文件。

### 表空間文件的結構是怎麼樣的？

**表空間由段（segment）、區（extent）、頁（page）、行（row）組成**，InnoDB存儲引擎的邏輯存儲結構大致如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/表空間結構.drawio.png)

下面我們從下往上一個個看看。

#### 1、行（row）

數據庫表中的記錄都是按行（row）進行存放的，每行記錄根據不同的行格式，有不同的存儲結構。

後面我們詳細介紹 InnoDB 存儲引擎的行格式，也是本文重點介紹的內容。

#### 2、頁（page）

記錄是按照行來存儲的，但是數據庫的讀取並不以「行」為單位，否則一次讀取（也就是一次 I/O 操作）只能處理一行數據，效率會非常低。

因此，**InnoDB 的數據是按「頁」為單位來讀寫的**，也就是說，當需要讀一條記錄的時候，並不是將這個行記錄從磁盤讀出來，而是以頁為單位，將其整體讀入內存。

**默認每個頁的大小為 16KB**，也就是最多能保證 16KB 的連續存儲空間。

頁是 InnoDB 存儲引擎磁盤管理的最小單元，意味著數據庫每次讀寫都是以 16KB 為單位的，一次最少從磁盤中讀取 16K 的內容到內存中，一次最少把內存中的 16K 內容刷新到磁盤中。

頁的類型有很多，常見的有數據頁、undo 日誌頁、溢出頁等等。數據表中的行記錄是用「數據頁」來管理的，數據頁的結構這裡我就不講細說了，之前文章有說過，感興趣的可以去看這篇文章：[換一個角度看 B+ 樹](https://xiaolincoding.com/mysql/index/page.html)

總之知道表中的記錄存儲在「數據頁」裡面就行。

#### 3、區（extent）

我們知道 InnoDB 存儲引擎是用 B+ 樹來組織數據的。

B+ 樹中每一層都是通過雙向鏈表連接起來的，如果是以頁為單位來分配存儲空間，那麼鏈表中相鄰的兩個頁之間的物理位置並不是連續的，可能離得非常遠，那麼磁盤查詢時就會有大量的隨機I/O，隨機 I/O 是非常慢的。

解決這個問題也很簡單，就是讓鏈表中相鄰的頁的物理位置也相鄰，這樣就可以使用順序 I/O 了，那麼在範圍查詢（掃描葉子節點）的時候性能就會很高。

那具體怎麼解決呢？

**在表中數據量大的時候，為某個索引分配空間的時候就不再按照頁為單位分配了，而是按照區（extent）為單位分配。每個區的大小為 1MB，對於  16KB 的頁來說，連續的 64 個頁會被劃為一個區，這樣就使得鏈表中相鄰的頁的物理位置也相鄰，就能使用順序 I/O 了**。

#### 4、段（segment）

表空間是由各個段（segment）組成的，段是由多個區（extent）組成的。段一般分為數據段、索引段和回滾段等。

- 索引段：存放 B + 樹的非葉子節點的區的集合；
- 數據段：存放 B + 樹的葉子節點的區的集合；
- 回滾段：存放的是回滾數據的區的集合，之前講[事務隔離](https://xiaolincoding.com/mysql/transaction/mvcc.html)的時候就介紹到了 MVCC 利用了回滾段實現了多版本查詢數據。

好了，終於說完表空間的結構了。接下來，就具體講一下 InnoDB 的行格式了。

之所以要繞一大圈才講行記錄的格式，主要是想讓大家知道行記錄是存儲在哪個文件，以及行記錄在這個表空間文件中的哪個區域，有一個從上往下切入的視角，這樣理解起來不會覺得很抽象。

## InnoDB 行格式有哪些？

行格式（row_format），就是一條記錄的存儲結構。

InnoDB 提供了 4 種行格式，分別是 Redundant、Compact、Dynamic和 Compressed 行格式。

- Redundant 是很古老的行格式了， MySQL 5.0 版本之前用的行格式，現在基本沒人用了。
- 由於 Redundant 不是一種緊湊的行格式，所以 MySQL 5.0 之後引入了 Compact 行記錄存儲方式，Compact 是一種緊湊的行格式，設計的初衷就是為了讓一個數據頁中可以存放更多的行記錄，從 MySQL 5.1 版本之後，行格式默認設置成 Compact。
- Dynamic 和 Compressed 兩個都是緊湊的行格式，它們的行格式都和 Compact 差不多，因為都是基於 Compact 改進一點東西。從 MySQL5.7 版本之後，默認使用 Dynamic 行格式。

Redundant 行格式我這裡就不講了，因為現在基本沒人用了，這次重點介紹 Compact 行格式，因為 Dynamic 和 Compressed 這兩個行格式跟 Compact 非常像。

所以，弄懂了 Compact 行格式，之後你們在去了解其他行格式，很快也能看懂。

## COMPACT 行格式長什麼樣？

先跟 Compact 行格式混個臉熟，它長這樣：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/COMPACT.drawio.png)

可以看到，一條完整的記錄分為「記錄的額外信息」和「記錄的真實數據」兩個部分。

接下里，分別詳細說下。

### 記錄的額外信息

記錄的額外信息包含 3 個部分：變長字段長度列表、NULL 值列表、記錄頭信息。

#### 1. 變長字段長度列表

varchar(n) 和 char(n) 的區別是什麼，相信大家都非常清楚，char 是定長的，varchar 是變長的，變長字段實際存儲的數據的長度（大小）不固定的。

所以，在存儲數據的時候，也要把數據佔用的大小存起來，存到「變長字段長度列表」裡面，讀取數據的時候才能根據這個「變長字段長度列表」去讀取對應長度的數據。其他 TEXT、BLOB 等變長字段也是這麼實現的。

為了展示「變長字段長度列表」具體是怎麼保存「變長字段的真實數據佔用的字節數」，我們先創建這樣一張表，字符集是 ascii（所以每一個字符佔用的 1 字節），行格式是 Compact，t_user 表中 name 和 phone 字段都是變長字段：

```sql
CREATE TABLE `t_user` (
  `id` int(11) NOT NULL,
  `name` VARCHAR(20) DEFAULT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARACTER SET = ascii ROW_FORMAT = COMPACT;
```

現在 t_user 表裡有這三條記錄：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/t_test.png)

接下來，我們看看看看這三條記錄的行格式中的 「變長字段長度列表」是怎樣存儲的。

先來看第一條記錄：

- name 列的值為 a，真實數據佔用的字節數是 1 字節，十六進制 0x01；
- phone 列的值為 123，真實數據佔用的字節數是 3 字節，十六進制 0x03；
- age 列和 id 列不是變長字段，所以這裡不用管。

這些變長字段的真實數據佔用的字節數會按照列的順序**逆序存放**（等下會說為什麼要這麼設計），所以「變長字段長度列表」裡的內容是「 03 01」，而不是 「01 03」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/變長字段長度列表1.png)

同樣的道理，我們也可以得出**第二條記錄**的行格式中，「變長字段長度列表」裡的內容是「 04 02」，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/變長字段長度列表2.png)

**第三條記錄**中 phone 列的值是 NULL，**NULL 是不會存放在行格式中記錄的真實數據部分裡的**，所以「變長字段長度列表」裡不需要保存值為  NULL 的變長字段的長度。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/變長字段長度列表3.png)

> 為什麼「變長字段長度列表」的信息要按照逆序存放？

這個設計是有想法的，主要是因為「記錄頭信息」中指向下一個記錄的指針，指向的是下一條記錄的「記錄頭信息」和「真實數據」之間的位置，這樣的好處是向左讀就是記錄頭信息，向右讀就是真實數據，比較方便。

「變長字段長度列表」中的信息之所以要逆序存放，是因為這樣可以**使得位置靠前的記錄的真實數據和數據對應的字段長度信息可以同時在一個 CPU Cache Line 中，這樣就可以提高 CPU Cache 的命中率**。

同樣的道理， NULL 值列表的信息也需要逆序存放。

如果你不知道什麼是 CPU Cache，可以看[這篇文章](https://xiaolincoding.com/os/1_hardware/how_to_make_cpu_run_faster.html)，這屬於計算機組成的知識。

> 每個數據庫表的行格式都有「變長字段字節數列表」嗎？

其實變長字段字節數列表不是必須的。

**當數據表沒有變長字段的時候，比如全部都是 int 類型的字段，這時候表裡的行格式就不會有「變長字段長度列表」了**，因為沒必要，不如去掉以節省空間。

所以「變長字段長度列表」只出現在數據表有變長字段的時候。

#### 2. NULL 值列表

表中的某些列可能會存儲 NULL 值，如果把這些 NULL 值都放到記錄的真實數據中會比較浪費空間，所以 Compact 行格式把這些值為 NULL 的列存儲到 NULL值列表中。

如果存在允許 NULL 值的列，則每個列對應一個二進制位（bit），二進制位按照列的順序逆序排列。

- 二進制位的值為`1`時，代表該列的值為NULL。
- 二進制位的值為`0`時，代表該列的值不為NULL。

另外，NULL 值列表必須用整數個字節的位表示（1字節8位），如果使用的二進制位個數不足整數個字節，則在字節的高位補 `0`。

還是以 t_user 表的這三條記錄作為例子：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/t_test.png)

接下來，我們看看看看這三條記錄的行格式中的 NULL 值列表是怎樣存儲的。

先來看**第一條記錄**，第一條記錄所有列都有值，不存在 NULL 值，所以用二進制來表示是醬紫的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/null值列表1.png)

但是 InnoDB 是用整數字節的二進制位來表示 NULL 值列表的，現在不足 8 位，所以要在高位補 0，最終用二進制來表示是醬紫的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/null值列表2.png)

所以，對於第一條數據，NULL 值列表用十六進製表示是 0x00。

接下來看**第二條記錄**，第二條記錄 age 列是 NULL 值，所以，對於第二條數據，NULL值列表用十六進製表示是 0x04。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/null值列表3.png)

最後**第三條記錄**，第三條記錄 phone 列 和 age 列是 NULL 值，所以，對於第三條數據，NULL 值列表用十六進製表示是 0x06。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/null值列表4.png)

我們把三條記錄的 NULL 值列表都填充完畢後，它們的行格式是這樣的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/null值列表5.png)

> 每個數據庫表的行格式都有「NULL 值列表」嗎？

NULL 值列表也不是必須的。

**當數據表的字段都定義成 NOT NULL 的時候，這時候表裡的行格式就不會有 NULL 值列表了**。

所以在設計數據庫表的時候，通常都是建議將字段設置為  NOT NULL，這樣可以至少節省 1 字節的空間（NULL 值列表至少佔用 1 字節空間）。

> 「NULL 值列表」是固定 1 字節空間嗎？如果這樣的話，一條記錄有 9 個字段值都是 NULL，這時候怎麼表示？

「NULL 值列表」的空間不是固定 1 字節的。

當一條記錄有 9 個字段值都是 NULL，那麼就會創建 2 字節空間的「NULL 值列表」，以此類推。

#### 3. 記錄頭信息

記錄頭信息中包含的內容很多，我就不一一列舉了，這裡說幾個比較重要的：

- delete_mask ：標識此條數據是否被刪除。從這裡可以知道，我們執行 detele 刪除記錄的時候，並不會真正的刪除記錄，只是將這個記錄的 delete_mask 標記為 1。
- next_record：下一條記錄的位置。從這裡可以知道，記錄與記錄之間是通過鏈表組織的。在前面我也提到了，指向的是下一條記錄的「記錄頭信息」和「真實數據」之間的位置，這樣的好處是向左讀就是記錄頭信息，向右讀就是真實數據，比較方便。
- record_type：表示當前記錄的類型，0表示普通記錄，1表示B+樹非葉子節點記錄，2表示最小記錄，3表示最大記錄

### 記錄的真實數據

記錄真實數據部分除了我們定義的字段，還有三個隱藏字段，分別為：row_id、trx_id、roll_pointer，我們來看下這三個字段是什麼。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/記錄的真實數據.png)

- row_id

如果我們建表的時候指定了主鍵或者唯一約束列，那麼就沒有 row_id 隱藏字段了。如果既沒有指定主鍵，又沒有唯一約束，那麼 InnoDB 就會為記錄添加 row_id 隱藏字段。row_id不是必需的，佔用 6 個字節。

- trx_id

事務id，表示這個數據是由哪個事務生成的。 trx_id是必需的，佔用 6 個字節。

- roll_pointer

這條記錄上一個版本的指針。roll_pointer 是必需的，佔用 7 個字節。

如果你熟悉 MVCC 機制，你應該就清楚 trx_id 和 roll_pointer 的作用了，如果你還不知道 MVCC 機制，可以看完[這篇文章](https://xiaolincoding.com/mysql/transaction/mvcc.html)，一定要掌握，面試也很經常問 MVCC 是怎麼實現的。

## varchar(n) 中 n 最大取值為多少？

我們要清楚一點，**MySQL 規定除了 TEXT、BLOBs 這種大對象類型之外，其他所有的列（不包括隱藏列和記錄頭信息）佔用的字節長度加起來不能超過 65535 個字節**。

也就是說，一行記錄除了 TEXT、BLOBs 類型的列，限制最大為 65535 字節，注意是一行的總長度，不是一列。

知道了這個前提之後，我們再來看看這個問題：「varchar(n) 中 n 最大取值為多少？」

varchar(n) 字段類型的 n 代表的是最多存儲的字符數量，並不是字節大小哦。

要算 varchar(n) 最大能允許存儲的字節數，還要看數據庫表的字符集，因為字符集代表著，1個字符要佔用多少字節，比如 ascii 字符集， 1 個字符佔用 1 字節，那麼  varchar(100) 意味著最大能允許存儲 100 字節的數據。

### 單字段的情況

前面我們知道了，一行記錄最大隻能存儲 65535 字節的數據。

那假設數據庫表只有一個 varchar(n) 類型的列且字符集是 ascii，在這種情況下， varchar(n) 中 n 最大取值是 65535 嗎？

不著急說結論，我們先來做個實驗驗證一下。

我們定義一個 varchar(65535) 類型的字段，字符集為 ascii 的數據庫表。

```sql
CREATE TABLE test ( 
`name` VARCHAR(65535)  NULL
) ENGINE = InnoDB DEFAULT CHARACTER SET = ascii ROW_FORMAT = COMPACT;
```

看能不能成功創建一張表：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/error.png)

可以看到，創建失敗了。

從報錯信息就可以知道**一行數據的最大字節數是 65535（不包含 TEXT、BLOBs 這種大對象類型），其中包含了 storage overhead**。

問題來了，這個 storage overhead 是什麼呢？其實就是「變長字段長度列表」和 「NULL 值列表」，也就是說**一行數據的最大字節數 65535，其實是包含「變長字段長度列表」和 「NULL 值列表」所佔用的字節數的**。所以， 我們在算 varchar(n) 中 n 最大值時，需要減去 storage overhead  佔用的字節數。

這是因為我們存儲字段類型為 varchar(n)  的數據時，其實分成了三個部分來存儲：

- 真實數據
- 真實數據佔用的字節數
- NULL 標識，如果不允許為NULL，這部分不需要

> 本次案例中，「NULL 值列表」所佔用的字節數是多少？

前面我創建表的時候，字段是允許為 NULL 的，所以**會用 1 字節來表示「NULL 值列表」**。

> 本次案例中，「變長字段長度列表」所佔用的字節數是多少？

「變長字段長度列表」所佔用的字節數 = 所有「變長字段長度」佔用的字節數之和。

所以，我們要先知道每個變長字段的「變長字段長度」需要用多少字節表示？具體情況分為：

- 條件一：如果變長字段允許存儲的最大字節數小於等於 255 字節，就會用 1 字節表示「變長字段長度」；
- 條件二：如果變長字段允許存儲的最大字節數大於 255 字節，就會用 2 字節表示「變長字段長度」；

我們這裡字段類型是 varchar(65535) ，字符集是 ascii，所以代表著變長字段允許存儲的最大字節數是 65535，符合條件二，所以會用 2 字節來表示「變長字段長度」。

**因為我們這個案例是隻有 1 個變長字段，所以「變長字段長度列表」= 1 個「變長字段長度」佔用的字節數，也就是 2 字節**。

因為我們在算 varchar(n) 中 n 最大值時，需要減去 「變長字段長度列表」和 「NULL 值列表」所佔用的字節數的。所以，**在數據庫表只有一個 varchar(n)  字段且字符集是 ascii 的情況下，varchar(n) 中 n 最大值 =  65535 - 2 - 1 = 65532**。

我們先來測試看看  varchar(65533)  是否可行？

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/65533.png)

可以看到，還是不行，接下來看看 varchar(65532)  是否可行？

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/65532.png)

可以看到，創建成功了。說明我們的推論是正確的，在算 varchar(n) 中 n 最大值時，需要減去 「變長字段長度列表」和 「NULL 值列表」所佔用的字節數的。

當然，我上面這個例子是針對字符集為 ascii 情況，如果採用的是 UTF-8，varchar(n)  最多能存儲的數據計算方式就不一樣了：

- 在 UTF-8 字符集下，一個字符串最多需要三個字節，varchar(n) 的 n 最大取值就是 65532/3 = 21844。

上面所說的只是針對於一個字段的計算方式。

### 多字段的情況

**如果有多個字段的話，要保證所有字段的長度 + 變長字段字節數列表所佔用的字節數 + NULL值列表所佔用的字節數 <= 65535**。

這裡舉個多字段的情況的例子（感謝@Emoji同學提供的例子）

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/多字段的情況.png)

## 行溢出後，MySQL 是怎麼處理的？

MySQL 中磁盤和內存交互的基本單位是頁，一個頁的大小一般是 `16KB`，也就是 `16384字節`，而一個 varchar(n)  類型的列最多可以存儲 `65532字節`，一些大對象如 TEXT、BLOB 可能存儲更多的數據，這時一個頁可能就存不了一條記錄。這個時候就會**發生行溢出，多的數據就會存到另外的「溢出頁」中**。

如果一個數據頁存不了一條記錄，InnoDB 存儲引擎會自動將溢出的數據存放到「溢出頁」中。在一般情況下，InnoDB 的數據都是存放在 「數據頁」中。但是當發生行溢出時，溢出的數據會存放到「溢出頁」中。

當發生行溢出時，在記錄的真實數據處只會保存該列的一部分數據，而把剩餘的數據放在「溢出頁」中，然後真實數據處用 20 字節存儲指向溢出頁的地址，從而可以找到剩餘數據所在的頁。大致如下圖所示。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/行溢出.png)

上面這個是 Compact 行格式在發生行溢出後的處理。

Compressed 和 Dynamic 這兩個行格式和 Compact 非常類似，主要的區別在於處理行溢出數據時有些區別。

這兩種格式採用完全的行溢出方式，記錄的真實數據處不會存儲該列的一部分數據，只存儲 20 個字節的指針來指向溢出頁。而實際的數據都存儲在溢出頁中，看起來就像下面這樣：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/mysql/row_format/行溢出2.png)

## 總結

>  MySQL 的 NULL 值是怎麼存放的？

MySQL 的 Compact 行格式中會用「NULL值列表」來標記值為 NULL 的列，NULL 值並不會存儲在行格式中的真實數據部分。

NULL值列表會佔用 1 字節空間，當表中所有字段都定義成 NOT NULL，行格式中就不會有 NULL值列表，這樣可節省 1 字節的空間。

> MySQL 怎麼知道 varchar(n) 實際佔用數據的大小？

MySQL 的 Compact 行格式中會用「變長字段長度列表」存儲變長字段實際佔用的數據大小。

> varchar(n) 中 n 最大取值為多少？

一行記錄最大能存儲 65535 字節的數據，但是這個是包含「變長字段字節數列表所佔用的字節數」和「NULL值列表所佔用的字節數」。所以， 我們在算 varchar(n) 中 n 最大值時，需要減去這兩個列表所佔用的字節數。

如果一張表只有一個 varchar(n)  字段，且允許為 NULL，字符集為 ascii。varchar(n) 中 n 最大取值為 65532。

計算公式：65535 - 變長字段字節數列表所佔用的字節數 - NULL值列表所佔用的字節數 = 65535 - 2 - 1 = 65532。

如果有多個字段的話，要保證所有字段的長度 + 變長字段字節數列表所佔用的字節數 + NULL值列表所佔用的字節數 <= 65535。

> 行溢出後，MySQL 是怎麼處理的？

如果一個數據頁存不了一條記錄，InnoDB 存儲引擎會自動將溢出的數據存放到「溢出頁」中。

Compact 行格式針對行溢出的處理是這樣的：當發生行溢出時，在記錄的真實數據處只會保存該列的一部分數據，而把剩餘的數據放在「溢出頁」中，然後真實數據處用 20 字節存儲指向溢出頁的地址，從而可以找到剩餘數據所在的頁。

Compressed 和 Dynamic 這兩種格式採用完全的行溢出方式，記錄的真實數據處不會存儲該列的一部分數據，只存儲 20 個字節的指針來指向溢出頁。而實際的數據都存儲在溢出頁中。

參考資料：

- 《MySQL 是怎樣運行的》
- 《MySQL技術內幕 InnoDB存儲引擎》

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

