# Redis 常見數據類型和應用場景

大家好，我是小林。

我們都知道 Redis 提供了豐富的數據類型，常見的有五種：**String（字符串），Hash（哈希），List（列表），Set（集合）、Zset（有序集合）**。

隨著 Redis 版本的更新，後面又支持了四種數據類型： **BitMap（2.2 版新增）、HyperLogLog（2.8 版新增）、GEO（3.2 版新增）、Stream（5.0 版新增）**。

每種數據對象都各自的應用場景，你能說出它們各自的應用場景嗎？

面試過程中，這個問題也很常被問到，又比如會舉例一個應用場景來問你，讓你說使用哪種 Redis 數據類型來實現。

所以，這次我們就來學習 **Redis 數據類型的使用以及應用場景**。

> PS：你可以自己本機安裝 Redis 或者通過 Redis 官網提供的[在線 Redis 環境](https://try.redis.io/) 來敲命令。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/redis命令提綱.png)

## String

### 介紹

String 是最基本的 key-value 結構，key 是唯一標識，value 是具體的值，value其實不僅是字符串， 也可以是數字（整數或浮點數），value 最多可以容納的數據長度是 `512M`。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/string.png)

### 內部實現

String 類型的底層的數據結構實現主要是 int 和 SDS（簡單動態字符串）。

SDS 和我們認識的 C 字符串不太一樣，之所以沒有使用 C 語言的字符串表示，因為 SDS 相比於 C 的原生字符串：

- **SDS  不僅可以保存文本數據，還可以保存二進制數據**。因為 `SDS` 使用 `len` 屬性的值而不是空字符來判斷字符串是否結束，並且 SDS 的所有 API 都會以處理二進制的方式來處理 SDS 存放在 `buf[]` 數組裡的數據。所以 SDS 不光能存放文本數據，而且能保存圖片、音頻、視頻、壓縮文件這樣的二進制數據。
- **SDS 獲取字符串長度的時間複雜度是 O(1)**。因為 C 語言的字符串並不記錄自身長度，所以獲取長度的複雜度為 O(n)；而 SDS 結構裡用 `len` 屬性記錄了字符串長度，所以複雜度為 `O(1)`。
- **Redis 的 SDS API 是安全的，拼接字符串不會造成緩衝區溢出**。因為 SDS 在拼接字符串之前會檢查 SDS 空間是否滿足要求，如果空間不夠會自動擴容，所以不會導致緩衝區溢出的問題。

字符串對象的內部編碼（encoding）有 3 種 ：**int、raw和 embstr**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/string結構.png)

如果一個字符串對象保存的是整數值，並且這個整數值可以用`long`類型來表示，那麼字符串對象會將整數值保存在字符串對象結構的`ptr`屬性裡面（將`void*`轉換成 long），並將字符串對象的編碼設置為`int`。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/int.png)

如果字符串對象保存的是一個字符串，並且這個字符申的長度小於等於 32 字節（redis 2.+版本），那麼字符串對象將使用一個簡單動態字符串（SDS）來保存這個字符串，並將對象的編碼設置為`embstr`， `embstr`編碼是專門用於保存短字符串的一種優化編碼方式：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/embstr.png)

如果字符串對象保存的是一個字符串，並且這個字符串的長度大於 32 字節（redis 2.+版本），那麼字符串對象將使用一個簡單動態字符串（SDS）來保存這個字符串，並將對象的編碼設置為`raw`：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/raw.png)

注意，embstr 編碼和 raw 編碼的邊界在 redis 不同版本中是不一樣的：

- redis 2.+ 是 32 字節
- redis 3.0-4.0 是 39 字節
- redis 5.0 是 44 字節

可以看到`embstr`和`raw`編碼都會使用`SDS`來保存值，但不同之處在於`embstr`會通過一次內存分配函數來分配一塊連續的內存空間來保存`redisObject`和`SDS`，而`raw`編碼會通過調用兩次內存分配函數來分別分配兩塊空間來保存`redisObject`和`SDS`。Redis這樣做會有很多好處：

- `embstr`編碼將創建字符串對象所需的內存分配次數從 `raw` 編碼的兩次降低為一次；
- 釋放 `embstr`編碼的字符串對象同樣只需要調用一次內存釋放函數；
- 因為`embstr`編碼的字符串對象的所有數據都保存在一塊連續的內存裡面可以更好的利用 CPU 緩存提升性能。

但是 embstr 也有缺點的：

- 如果字符串的長度增加需要重新分配內存時，整個redisObject和sds都需要重新分配空間，所以**embstr編碼的字符串對象實際上是隻讀的**，redis沒有為embstr編碼的字符串對象編寫任何相應的修改程序。當我們對embstr編碼的字符串對象執行任何修改命令（例如append）時，程序會先將對象的編碼從embstr轉換成raw，然後再執行修改命令。

### 常用指令

普通字符串的基本操作：

```shell
# 設置 key-value 類型的值
> SET name lin
OK
# 根據 key 獲得對應的 value
> GET name
"lin"
# 判斷某個 key 是否存在
> EXISTS name
(integer) 1
# 返回 key 所儲存的字符串值的長度
> STRLEN name
(integer) 3
# 刪除某個 key 對應的值
> DEL name
(integer) 1
```

批量設置 :

```shell
# 批量設置 key-value 類型的值
> MSET key1 value1 key2 value2 
OK
# 批量獲取多個 key 對應的 value
> MGET key1 key2 
1) "value1"
2) "value2"
```

計數器（字符串的內容為整數的時候可以使用）：

```shell
# 設置 key-value 類型的值
> SET number 0
OK
# 將 key 中儲存的數字值增一
> INCR number
(integer) 1
# 將key中存儲的數字值加 10
> INCRBY number 10
(integer) 11
# 將 key 中儲存的數字值減一
> DECR number
(integer) 10
# 將key中存儲的數字值鍵 10
> DECRBY number 10
(integer) 0
```

過期（默認為永不過期）：

```bash
# 設置 key 在 60 秒後過期（該方法是針對已經存在的key設置過期時間）
> EXPIRE name  60 
(integer) 1
# 查看數據還有多久過期
> TTL name 
(integer) 51

#設置 key-value 類型的值，並設置該key的過期時間為 60 秒
> SET key  value EX 60
OK
> SETEX key  60 value
OK
```

不存在就插入：

```shell
# 不存在就插入（not exists）
>SETNX key value
(integer) 1
```

### 應用場景

#### 緩存對象

使用 String 來緩存對象有兩種方式：

- 直接緩存整個對象的 JSON，命令例子： `SET user:1 '{"name":"xiaolin", "age":18}'`。
- 採用將 key 進行分離為 user:ID:屬性，採用 MSET 存儲，用 MGET 獲取各屬性值，命令例子： `MSET user:1:name xiaolin user:1:age 18 user:2:name xiaomei user:2:age 20`。

#### 常規計數

因為 Redis 處理命令是單線程，所以執行命令的過程是原子的。因此 String 數據類型適合計數場景，比如計算訪問次數、點贊、轉發、庫存數量等等。

比如計算文章的閱讀量：

```shell
# 初始化文章的閱讀量
> SET aritcle:readcount:1001 0
OK
#閱讀量+1
> INCR aritcle:readcount:1001
(integer) 1
#閱讀量+1
> INCR aritcle:readcount:1001
(integer) 2
#閱讀量+1
> INCR aritcle:readcount:1001
(integer) 3
# 獲取對應文章的閱讀量
> GET aritcle:readcount:1001
"3"
```

#### 分佈式鎖

SET 命令有個 NX 參數可以實現「key不存在才插入」，可以用它來實現分佈式鎖：

- 如果 key 不存在，則顯示插入成功，可以用來表示加鎖成功；
- 如果 key 存在，則會顯示插入失敗，可以用來表示加鎖失敗。

一般而言，還會對分佈式鎖加上過期時間，分佈式鎖的命令如下：

```shell
SET lock_key unique_value NX PX 10000
```

- lock_key 就是 key 鍵；
- unique_value 是客戶端生成的唯一的標識；
- NX 代表只在 lock_key 不存在時，才對 lock_key 進行設置操作；
- PX 10000 表示設置 lock_key 的過期時間為 10s，這是為了避免客戶端發生異常而無法釋放鎖。

而解鎖的過程就是將 lock_key 鍵刪除，但不能亂刪，要保證執行操作的客戶端就是加鎖的客戶端。所以，解鎖的時候，我們要先判斷鎖的 unique_value 是否為加鎖客戶端，是的話，才將 lock_key 鍵刪除。

可以看到，解鎖是有兩個操作，這時就需要 Lua 腳本來保證解鎖的原子性，因為 Redis 在執行 Lua 腳本時，可以以原子性的方式執行，保證了鎖釋放操作的原子性。

```Lua
// 釋放鎖時，先比較 unique_value 是否相等，避免鎖的誤釋放
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
```

這樣一來，就通過使用 SET 命令和 Lua 腳本在 Redis 單節點上完成了分佈式鎖的加鎖和解鎖。

#### 共享 Session 信息

通常我們在開發後臺管理系統時，會使用 Session 來保存用戶的會話(登錄)狀態，這些 Session 信息會被保存在服務器端，但這隻適用於單系統應用，如果是分佈式系統此模式將不再適用。

例如用戶一的 Session 信息被存儲在服務器一，但第二次訪問時用戶一被分配到服務器二，這個時候服務器並沒有用戶一的 Session 信息，就會出現需要重複登錄的問題，問題在於分佈式系統每次會把請求隨機分配到不同的服務器。

分佈式系統單獨存儲 Session 流程圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/Session1.png)

因此，我們需要藉助 Redis 對這些 Session 信息進行統一的存儲和管理，這樣無論請求發送到那臺服務器，服務器都會去同一個 Redis 獲取相關的 Session 信息，這樣就解決了分佈式系統下 Session 存儲的問題。

分佈式系統使用同一個 Redis 存儲 Session 流程圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/Session2.png)

## List

### 介紹

List 列表是簡單的字符串列表，**按照插入順序排序**，可以從頭部或尾部向 List 列表添加元素。

列表的最大長度為 `2^32 - 1`，也即每個列表支持超過 `40 億`個元素。

### 內部實現

List 類型的底層數據結構是由**雙向鏈表或壓縮列表**實現的：

- 如果列表的元素個數小於 `512` 個（默認值，可由 `list-max-ziplist-entries` 配置），列表每個元素的值都小於 `64` 字節（默認值，可由 `list-max-ziplist-value` 配置），Redis 會使用**壓縮列表**作為 List 類型的底層數據結構；
- 如果列表的元素不滿足上面的條件，Redis 會使用**雙向鏈表**作為 List 類型的底層數據結構；

但是**在 Redis 3.2 版本之後，List 數據類型底層數據結構就只由 quicklist 實現了，替代了雙向鏈表和壓縮列表**。

### 常用命令

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/list.png)

```shell
# 將一個或多個值value插入到key列表的表頭(最左邊)，最後的值在最前面
LPUSH key value [value ...] 
# 將一個或多個值value插入到key列表的表尾(最右邊)
RPUSH key value [value ...]
# 移除並返回key列表的頭元素
LPOP key     
# 移除並返回key列表的尾元素
RPOP key 

# 返回列表key中指定區間內的元素，區間以偏移量start和stop指定，從0開始
LRANGE key start stop

# 從key列表表頭彈出一個元素，沒有就阻塞timeout秒，如果timeout=0則一直阻塞
BLPOP key [key ...] timeout
# 從key列表表尾彈出一個元素，沒有就阻塞timeout秒，如果timeout=0則一直阻塞
BRPOP key [key ...] timeout
```

### 應用場景

#### 消息隊列

消息隊列在存取消息時，必須要滿足三個需求，分別是**消息保序、處理重複的消息和保證消息可靠性**。

Redis 的 List 和 Stream 兩種數據類型，就可以滿足消息隊列的這三個需求。我們先來瞭解下基於 List 的消息隊列實現方法，後面在介紹 Stream 數據類型時候，在詳細說說 Stream。

*1、如何滿足消息保序需求？*

List 本身就是按先進先出的順序對數據進行存取的，所以，如果使用 List 作為消息隊列保存消息的話，就已經能滿足消息保序的需求了。

List 可以使用 LPUSH + RPOP （或者反過來，RPUSH+LPOP）命令實現消息隊列。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/list消息隊列.png)

- 生產者使用 `LPUSH key value[value...]` 將消息插入到隊列的頭部，如果 key 不存在則會創建一個空的隊列再插入消息。

- 消費者使用 `RPOP key` 依次讀取隊列的消息，先進先出。

不過，在消費者讀取數據時，有一個潛在的性能風險點。

在生產者往 List 中寫入數據時，List 並不會主動地通知消費者有新消息寫入，如果消費者想要及時處理消息，就需要在程序中不停地調用 `RPOP` 命令（比如使用一個while(1)循環）。如果有新消息寫入，RPOP命令就會返回結果，否則，RPOP命令返回空值，再繼續循環。

所以，即使沒有新消息寫入List，消費者也要不停地調用 RPOP 命令，這就會導致消費者程序的 CPU 一直消耗在執行 RPOP 命令上，帶來不必要的性能損失。

為瞭解決這個問題，Redis提供了 BRPOP 命令。**BRPOP命令也稱為阻塞式讀取，客戶端在沒有讀到隊列數據時，自動阻塞，直到有新的數據寫入隊列，再開始讀取新數據**。和消費者程序自己不停地調用RPOP命令相比，這種方式能節省CPU開銷。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/消息隊列.png)

*2、如何處理重複的消息？*

消費者要實現重複消息的判斷，需要 2 個方面的要求：

- 每個消息都有一個全局的 ID。
- 消費者要記錄已經處理過的消息的 ID。當收到一條消息後，消費者程序就可以對比收到的消息 ID 和記錄的已處理過的消息 ID，來判斷當前收到的消息有沒有經過處理。如果已經處理過，那麼，消費者程序就不再進行處理了。

但是 **List 並不會為每個消息生成 ID 號，所以我們需要自行為每個消息生成一個全局唯一ID**，生成之後，我們在用 LPUSH 命令把消息插入 List 時，需要在消息中包含這個全局唯一 ID。

例如，我們執行以下命令，就把一條全局 ID 為 111000102、庫存量為 99 的消息插入了消息隊列：

```shell
> LPUSH mq "111000102:stock:99"
(integer) 1
```

*3、如何保證消息可靠性？*

當消費者程序從 List 中讀取一條消息後，List 就不會再留存這條消息了。所以，如果消費者程序在處理消息的過程出現了故障或宕機，就會導致消息沒有處理完成，那麼，消費者程序再次啟動後，就沒法再次從 List 中讀取消息了。

為了留存消息，List 類型提供了 `BRPOPLPUSH` 命令，這個命令的**作用是讓消費者程序從一個 List 中讀取消息，同時，Redis 會把這個消息再插入到另一個 List（可以叫作備份 List）留存**。

這樣一來，如果消費者程序讀了消息但沒能正常處理，等它重啟後，就可以從備份 List 中重新讀取消息並進行處理了。

好了，到這裡可以知道基於 List 類型的消息隊列，滿足消息隊列的三大需求（消息保序、處理重複的消息和保證消息可靠性）。

- 消息保序：使用 LPUSH + RPOP；
- 阻塞讀取：使用 BRPOP；
- 重複消息處理：生產者自行實現全局唯一 ID；
- 消息的可靠性：使用 BRPOPLPUSH

> List 作為消息隊列有什麼缺陷？

**List 不支持多個消費者消費同一條消息**，因為一旦消費者拉取一條消息後，這條消息就從 List 中刪除了，無法被其它消費者再次消費。

要實現一條消息可以被多個消費者消費，那麼就要將多個消費者組成一個消費組，使得多個消費者可以消費同一條消息，但是 **List 類型並不支持消費組的實現**。

這就要說起 Redis 從 5.0 版本開始提供的 Stream 數據類型了，Stream 同樣能夠滿足消息隊列的三大需求，而且它還支持「消費組」形式的消息讀取。

## Hash

### 介紹

Hash 是一個鍵值對（key - value）集合，其中 value 的形式如： `value=[{field1，value1}，...{fieldN，valueN}]`。Hash 特別適合用於存儲對象。 

Hash 與 String 對象的區別如下圖所示:

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/hash.png)

### 內部實現

Hash 類型的底層數據結構是由**壓縮列表或哈希表**實現的：

- 如果哈希類型元素個數小於 `512` 個（默認值，可由 `hash-max-ziplist-entries` 配置），所有值小於 `64` 字節（默認值，可由 `hash-max-ziplist-value` 配置）的話，Redis 會使用**壓縮列表**作為 Hash 類型的底層數據結構；
- 如果哈希類型元素不滿足上面條件，Redis 會使用**哈希表**作為 Hash 類型的 底層數據結構。

**在 Redis 7.0 中，壓縮列表數據結構已經廢棄了，交由 listpack 數據結構來實現了**。

### 常用命令

```shell
# 存儲一個哈希表key的鍵值
HSET key field value   
# 獲取哈希表key對應的field鍵值
HGET key field

# 在一個哈希表key中存儲多個鍵值對
HMSET key field value [field value...] 
# 批量獲取哈希表key中多個field鍵值
HMGET key field [field ...]       
# 刪除哈希表key中的field鍵值
HDEL key field [field ...]    

# 返回哈希表key中field的數量
HLEN key       
# 返回哈希表key中所有的鍵值
HGETALL key 

# 為哈希表key中field鍵的值加上增量n
HINCRBY key field n                         
```

### 應用場景

#### 緩存對象

Hash 類型的 （key，field， value） 的結構與對象的（對象id， 屬性， 值）的結構相似，也可以用來存儲對象。

我們以用戶信息為例，它在關係型數據庫中的結構是這樣的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/用戶信息.png)

我們可以使用如下命令，將用戶對象的信息存儲到 Hash 類型：

```shell
# 存儲一個哈希表uid:1的鍵值
> HMSET uid:1 name Tom age 15
2
# 存儲一個哈希表uid:2的鍵值
> HMSET uid:2 name Jerry age 13
2
# 獲取哈希表用戶id為1中所有的鍵值
> HGETALL uid:1
1) "name"
2) "Tom"
3) "age"
4) "15"
```

Redis Hash 存儲其結構如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/hash存儲結構.png)

在介紹 String 類型的應用場景時有所介紹，String + Json也是存儲對象的一種方式，那麼存儲對象時，到底用 String + json 還是用 Hash 呢？

一般對象用 String + Json 存儲，對象中某些頻繁變化的屬性可以考慮抽出來用 Hash 類型存儲。

#### 購物車

以用戶 id 為 key，商品 id 為 field，商品數量為 value，恰好構成了購物車的3個要素，如下圖所示。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/購物車.png)

涉及的命令如下：

- 添加商品：`HSET  cart:{用戶id}  {商品id}  1`
- 添加數量：`HINCRBY  cart:{用戶id}  {商品id}  1`
- 商品總數：`HLEN  cart:{用戶id}`
- 刪除商品：`HDEL  cart:{用戶id}  {商品id}`
- 獲取購物車所有商品：`HGETALL  cart:{用戶id}`

當前僅僅是將商品ID存儲到了Redis 中，在回顯商品具體信息的時候，還需要拿著商品 id 查詢一次數據庫，獲取完整的商品的信息。

## Set

### 介紹

Set 類型是一個無序並唯一的鍵值集合，它的存儲順序不會按照插入的先後順序進行存儲。

一個集合最多可以存儲 `2^32-1` 個元素。概念和數學中個的集合基本類似，可以交集，並集，差集等等，所以 Set 類型除了支持集合內的增刪改查，同時還支持多個集合取交集、並集、差集。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/set.png)

Set 類型和 List 類型的區別如下：

- List 可以存儲重複元素，Set 只能存儲非重複元素；
- List 是按照元素的先後順序存儲元素的，而 Set 則是無序方式存儲元素的。

### 內部實現

Set 類型的底層數據結構是由**哈希表或整數集合**實現的：

- 如果集合中的元素都是整數且元素個數小於 `512` （默認值，`set-maxintset-entries`配置）個，Redis 會使用**整數集合**作為 Set 類型的底層數據結構；
- 如果集合中的元素不滿足上面條件，則 Redis 使用**哈希表**作為 Set 類型的底層數據結構。

### 常用命令

Set常用操作：

```shell
# 往集合key中存入元素，元素存在則忽略，若key不存在則新建
SADD key member [member ...]
# 從集合key中刪除元素
SREM key member [member ...] 
# 獲取集合key中所有元素
SMEMBERS key
# 獲取集合key中的元素個數
SCARD key

# 判斷member元素是否存在於集合key中
SISMEMBER key member

# 從集合key中隨機選出count個元素，元素不從key中刪除
SRANDMEMBER key [count]
# 從集合key中隨機選出count個元素，元素從key中刪除
SPOP key [count]
```

Set運算操作：

```shell
# 交集運算
SINTER key [key ...]
# 將交集結果存入新集合destination中
SINTERSTORE destination key [key ...]

# 並集運算
SUNION key [key ...]
# 將並集結果存入新集合destination中
SUNIONSTORE destination key [key ...]

# 差集運算
SDIFF key [key ...]
# 將差集結果存入新集合destination中
SDIFFSTORE destination key [key ...]
```

### 應用場景

集合的主要幾個特性，無序、不可重複、支持並交差等操作。

因此 Set 類型比較適合用來數據去重和保障數據的唯一性，還可以用來統計多個集合的交集、錯集和並集等，當我們存儲的數據是無序並且需要去重的情況下，比較適合使用集合類型進行存儲。

但是要提醒你一下，這裡有一個潛在的風險。**Set 的差集、並集和交集的計算複雜度較高，在數據量較大的情況下，如果直接執行這些計算，會導致 Redis 實例阻塞**。

在主從集群中，為了避免主庫因為 Set 做聚合計算（交集、差集、並集）時導致主庫被阻塞，我們可以選擇一個從庫完成聚合統計，或者把數據返回給客戶端，由客戶端來完成聚合統計。

#### 點贊

Set 類型可以保證一個用戶只能點一個贊，這裡舉例子一個場景，key 是文章id，value 是用戶id。

`uid:1` 、`uid:2`、`uid:3`   三個用戶分別對 article:1 文章點讚了。

```shell
# uid:1 用戶對文章 article:1 點贊
> SADD article:1 uid:1
(integer) 1
# uid:2 用戶對文章 article:1 點贊
> SADD article:1 uid:2
(integer) 1
# uid:3 用戶對文章 article:1 點贊
> SADD article:1 uid:3
(integer) 1
```

`uid:1` 取消了對 article:1 文章點贊。

```
> SREM article:1 uid:1
(integer) 1
```

獲取  article:1 文章所有點贊用戶 :

```shell
> SMEMBERS article:1
1) "uid:3"
2) "uid:2"
```

獲取 article:1 文章的點贊用戶數量：

```shell
> SCARD article:1
(integer) 2
```

判斷用戶 `uid:1` 是否對文章 article:1 點讚了：

```shell
> SISMEMBER article:1 uid:1
(integer) 0  # 返回0說明沒點贊，返回1則說明點讚了
```

#### 共同關注

Set 類型支持交集運算，所以可以用來計算共同關注的好友、公眾號等。

key 可以是用戶id，value 則是已關注的公眾號的id。

`uid:1` 用戶關注公眾號 id 為 5、6、7、8、9，`uid:2`  用戶關注公眾號 id 為 7、8、9、10、11。

```shell
# uid:1 用戶關注公眾號 id 為 5、6、7、8、9
> SADD uid:1 5 6 7 8 9
(integer) 5
# uid:2  用戶關注公眾號 id 為 7、8、9、10、11
> SADD uid:2 7 8 9 10 11
(integer) 5
```

`uid:1`  和 `uid:2`  共同關注的公眾號：

```shell
# 獲取共同關注
> SINTER uid:1 uid:2
1) "7"
2) "8"
3) "9"
```

給  `uid:2`   推薦 `uid:1` 關注的公眾號：

```shell
> SDIFF uid:1 uid:2
1) "5"
2) "6"
```

驗證某個公眾號是否同時被  `uid:1`   或  `uid:2`   關注:

```shell
> SISMEMBER uid:1 5
(integer) 1 # 返回0，說明關注了
> SISMEMBER uid:2 5
(integer) 0 # 返回0，說明沒關注
```

#### 抽獎活動

存儲某活動中中獎的用戶名 ，Set 類型因為有去重功能，可以保證同一個用戶不會中獎兩次。

key為抽獎活動名，value為員工名稱，把所有員工名稱放入抽獎箱 ：

```shell
>SADD lucky Tom Jerry John Sean Marry Lindy Sary Mark
(integer) 5
```

如果允許重複中獎，可以使用 SRANDMEMBER 命令。

```shell
# 抽取 1 個一等獎：
> SRANDMEMBER lucky 1
1) "Tom"
# 抽取 2 個二等獎：
> SRANDMEMBER lucky 2
1) "Mark"
2) "Jerry"
# 抽取 3 個三等獎：
> SRANDMEMBER lucky 3
1) "Sary"
2) "Tom"
3) "Jerry"
```

如果不允許重複中獎，可以使用 SPOP 命令。

```shell
# 抽取一等獎1個
> SPOP lucky 1
1) "Sary"
# 抽取二等獎2個
> SPOP lucky 2
1) "Jerry"
2) "Mark"
# 抽取三等獎3個
> SPOP lucky 3
1) "John"
2) "Sean"
3) "Lindy"
```

## Zset

### 介紹

Zset 類型（有序集合類型）相比於 Set 類型多了一個排序屬性 score（分值），對於有序集合 ZSet 來說，每個存儲元素相當於有兩個值組成的，一個是有序結合的元素值，一個是排序值。

有序集合保留了集合不能有重複成員的特性（分值可以重複），但不同的是，有序集合中的元素可以排序。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/zset.png)

### 內部實現

Zset 類型的底層數據結構是由**壓縮列表或跳錶**實現的：

- 如果有序集合的元素個數小於 `128` 個，並且每個元素的值小於 `64` 字節時，Redis 會使用**壓縮列表**作為 Zset 類型的底層數據結構；
- 如果有序集合的元素不滿足上面的條件，Redis 會使用**跳錶**作為 Zset 類型的底層數據結構；

**在 Redis 7.0 中，壓縮列表數據結構已經廢棄了，交由 listpack 數據結構來實現了。**

### 常用命令

Zset 常用操作：

```shell
# 往有序集合key中加入帶分值元素
ZADD key score member [[score member]...]   
# 往有序集合key中刪除元素
ZREM key member [member...]                 
# 返回有序集合key中元素member的分值
ZSCORE key member
# 返回有序集合key中元素個數
ZCARD key 

# 為有序集合key中元素member的分值加上increment
ZINCRBY key increment member 

# 正序獲取有序集合key從start下標到stop下標的元素
ZRANGE key start stop [WITHSCORES]
# 倒序獲取有序集合key從start下標到stop下標的元素
ZREVRANGE key start stop [WITHSCORES]

# 返回有序集合中指定分數區間內的成員，分數由低到高排序。
ZRANGEBYSCORE key min max [WITHSCORES] [LIMIT offset count]

# 返回指定成員區間內的成員，按字典正序排列, 分數必須相同。
ZRANGEBYLEX key min max [LIMIT offset count]
# 返回指定成員區間內的成員，按字典倒序排列, 分數必須相同
ZREVRANGEBYLEX key max min [LIMIT offset count]
```

Zset 運算操作（相比於 Set 類型，ZSet 類型沒有支持差集運算）：

```shell
# 並集計算(相同元素分值相加)，numberkeys一共多少個key，WEIGHTS每個key對應的分值乘積
ZUNIONSTORE destkey numberkeys key [key...] 
# 交集計算(相同元素分值相加)，numberkeys一共多少個key，WEIGHTS每個key對應的分值乘積
ZINTERSTORE destkey numberkeys key [key...]
```

### 應用場景

Zset 類型（Sorted Set，有序集合） 可以根據元素的權重來排序，我們可以自己來決定每個元素的權重值。比如說，我們可以根據元素插入 Sorted Set 的時間確定權重值，先插入的元素權重小，後插入的元素權重大。

在面對需要展示最新列表、排行榜等場景時，如果數據更新頻繁或者需要分頁顯示，可以優先考慮使用 Sorted Set。

#### 排行榜

有序集合比較典型的使用場景就是排行榜。例如學生成績的排名榜、遊戲積分排行榜、視頻播放排名、電商系統中商品的銷量排名等。

我們以博文點贊排名為例，小林發表了五篇博文，分別獲得贊為 200、40、100、50、150。

```shell
# arcticle:1 文章獲得了200個贊
> ZADD user:xiaolin:ranking 200 arcticle:1
(integer) 1
# arcticle:2 文章獲得了40個贊
> ZADD user:xiaolin:ranking 40 arcticle:2
(integer) 1
# arcticle:3 文章獲得了100個贊
> ZADD user:xiaolin:ranking 100 arcticle:3
(integer) 1
# arcticle:4 文章獲得了50個贊
> ZADD user:xiaolin:ranking 50 arcticle:4
(integer) 1
# arcticle:5 文章獲得了150個贊
> ZADD user:xiaolin:ranking 150 arcticle:5
(integer) 1
```

文章 arcticle:4 新增一個贊，可以使用 ZINCRBY 命令（為有序集合key中元素member的分值加上increment）：

```shell
> ZINCRBY user:xiaolin:ranking 1 arcticle:4
"51"
```

查看某篇文章的贊數，可以使用 ZSCORE 命令（返回有序集合key中元素個數）：

```shell
> ZSCORE user:xiaolin:ranking arcticle:4
"50"
```

獲取小林文章贊數最多的 3 篇文章，可以使用 ZREVRANGE 命令（倒序獲取有序集合 key 從start下標到stop下標的元素）：

```shell
# WITHSCORES 表示把 score 也顯示出來
> ZREVRANGE user:xiaolin:ranking 0 2 WITHSCORES
1) "arcticle:1"
2) "200"
3) "arcticle:5"
4) "150"
5) "arcticle:3"
6) "100"
```

獲取小林 100 贊到 200 讚的文章，可以使用 ZRANGEBYSCORE 命令（返回有序集合中指定分數區間內的成員，分數由低到高排序）：

```shell
> ZRANGEBYSCORE user:xiaolin:ranking 100 200 WITHSCORES
1) "arcticle:3"
2) "100"
3) "arcticle:5"
4) "150"
5) "arcticle:1"
6) "200"
```

#### 電話、姓名排序

使用有序集合的 `ZRANGEBYLEX` 或 `ZREVRANGEBYLEX` 可以幫助我們實現電話號碼或姓名的排序，我們以 `ZRANGEBYLEX` （返回指定成員區間內的成員，按 key 正序排列，分數必須相同）為例。

**注意：不要在分數不一致的 SortSet 集合中去使用 ZRANGEBYLEX和 ZREVRANGEBYLEX 指令，因為獲取的結果會不準確。**

*1、電話排序*

我們可以將電話號碼存儲到 SortSet 中，然後根據需要來獲取號段：

```shell
> ZADD phone 0 13100111100 0 13110114300 0 13132110901 
(integer) 3
> ZADD phone 0 13200111100 0 13210414300 0 13252110901 
(integer) 3
> ZADD phone 0 13300111100 0 13310414300 0 13352110901 
(integer) 3
```

獲取所有號碼:

```shell
> ZRANGEBYLEX phone - +
1) "13100111100"
2) "13110114300"
3) "13132110901"
4) "13200111100"
5) "13210414300"
6) "13252110901"
7) "13300111100"
8) "13310414300"
9) "13352110901"
```

獲取 132 號段的號碼：

```shell
> ZRANGEBYLEX phone [132 (133
1) "13200111100"
2) "13210414300"
3) "13252110901"
```

獲取132、133號段的號碼：

```shell
> ZRANGEBYLEX phone [132 (134
1) "13200111100"
2) "13210414300"
3) "13252110901"
4) "13300111100"
5) "13310414300"
6) "13352110901"
```

*2、姓名排序*

```shell
> zadd names 0 Toumas 0 Jake 0 Bluetuo 0 Gaodeng 0 Aimini 0 Aidehua 
(integer) 6
```

獲取所有人的名字:

```shell
> ZRANGEBYLEX names - +
1) "Aidehua"
2) "Aimini"
3) "Bluetuo"
4) "Gaodeng"
5) "Jake"
6) "Toumas"
```

獲取名字中大寫字母A開頭的所有人：

```shell
> ZRANGEBYLEX names [A (B
1) "Aidehua"
2) "Aimini"
```

獲取名字中大寫字母 C 到 Z 的所有人：

```shell
> ZRANGEBYLEX names [C [Z
1) "Gaodeng"
2) "Jake"
3) "Toumas"
```

## BitMap

### 介紹

Bitmap，即位圖，是一串連續的二進制數組（0和1），可以通過偏移量（offset）定位元素。BitMap通過最小的單位bit來進行`0|1`的設置，表示某個元素的值或者狀態，時間複雜度為O(1)。

由於 bit 是計算機中最小的單位，使用它進行儲存將非常節省空間，特別適合一些數據量大且使用**二值統計的場景**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/bitmap.png)

### 內部實現

Bitmap 本身是用 String 類型作為底層數據結構實現的一種統計二值狀態的數據類型。

String 類型是會保存為二進制的字節數組，所以，Redis 就把字節數組的每個 bit 位利用起來，用來表示一個元素的二值狀態，你可以把 Bitmap 看作是一個 bit 數組。

### 常用命令

bitmap 基本操作：

```shell
# 設置值，其中value只能是 0 和 1
SETBIT key offset value

# 獲取值
GETBIT key offset

# 獲取指定範圍內值為 1 的個數
# start 和 end 以字節為單位
BITCOUNT key start end
```

bitmap 運算操作：

```shell
# BitMap間的運算
# operations 位移操作符，枚舉值
  AND 與運算 &
  OR 或運算 |
  XOR 異或 ^
  NOT 取反 ~
# result 計算的結果，會存儲在該key中
# key1 … keyn 參與運算的key，可以有多個，空格分割，not運算只能一個key
# 當 BITOP 處理不同長度的字符串時，較短的那個字符串所缺少的部分會被看作 0。返回值是保存到 destkey 的字符串的長度（以字節byte為單位），和輸入 key 中最長的字符串長度相等。
BITOP [operations] [result] [key1] [keyn…]

# 返回指定key中第一次出現指定value(0/1)的位置
BITPOS [key] [value]
```

### 應用場景

Bitmap 類型非常適合二值狀態統計的場景，這裡的二值狀態就是指集合元素的取值就只有 0 和 1 兩種，在記錄海量數據時，Bitmap 能夠有效地節省內存空間。

#### 簽到統計

在簽到打卡的場景中，我們只用記錄簽到（1）或未簽到（0），所以它就是非常典型的二值狀態。

簽到統計時，每個用戶一天的簽到用 1 個 bit 位就能表示，一個月（假設是 31 天）的簽到情況用 31 個 bit 位就可以，而一年的簽到也只需要用 365 個 bit 位，根本不用太複雜的集合類型。

假設我們要統計 ID 100 的用戶在 2022 年 6 月份的簽到情況，就可以按照下面的步驟進行操作。

第一步，執行下面的命令，記錄該用戶 6 月 3 號已簽到。

```shell
SETBIT uid:sign:100:202206 2 1
```

第二步，檢查該用戶 6 月 3 日是否簽到。

```shell
GETBIT uid:sign:100:202206 2 
```

第三步，統計該用戶在 6 月份的簽到次數。

```shell
BITCOUNT uid:sign:100:202206
```

這樣，我們就知道該用戶在 6 月份的簽到情況了。

> 如何統計這個月首次打卡時間呢？

Redis 提供了 `BITPOS key bitValue [start] [end]`指令，返回數據表示 Bitmap 中第一個值為 `bitValue` 的 offset 位置。

在默認情況下， 命令將檢測整個位圖， 用戶可以通過可選的 `start` 參數和 `end` 參數指定要檢測的範圍。所以我們可以通過執行這條命令來獲取 userID = 100 在 2022 年 6 月份**首次打卡**日期：

```apache
BITPOS uid:sign:100:202206 1
```

需要注意的是，因為 offset 從 0 開始的，所以我們需要將返回的 value + 1 。

#### 判斷用戶登陸態

Bitmap 提供了 `GETBIT、SETBIT` 操作，通過一個偏移值 offset 對 bit 數組的 offset 位置的 bit 位進行讀寫操作，需要注意的是 offset 從 0 開始。

只需要一個 key = login_status 表示存儲用戶登陸狀態集合數據， 將用戶 ID 作為 offset，在線就設置為 1，下線設置 0。通過 `GETBIT`判斷對應的用戶是否在線。 50000 萬 用戶只需要 6 MB 的空間。

假如我們要判斷 ID = 10086 的用戶的登陸情況：

第一步，執行以下指令，表示用戶已登錄。

```shell
SETBIT login_status 10086 1
```

第二步，檢查該用戶是否登陸，返回值 1 表示已登錄。

```apache
GETBIT login_status 10086
```

第三步，登出，將 offset 對應的 value 設置成 0。

```shell
SETBIT login_status 10086 0
```

#### 連續簽到用戶總數

如何統計出這連續 7 天連續打卡用戶總數呢？

我們把每天的日期作為 Bitmap 的 key，userId 作為 offset，若是打卡則將 offset 位置的 bit 設置成 1。

key 對應的集合的每個 bit 位的數據則是一個用戶在該日期的打卡記錄。

一共有 7 個這樣的 Bitmap，如果我們能對這 7 個 Bitmap 的對應的 bit 位做 『與』運算。同樣的 UserID offset 都是一樣的，當一個 userID 在 7 個 Bitmap 對應對應的 offset 位置的 bit = 1 就說明該用戶 7 天連續打卡。

結果保存到一個新 Bitmap 中，我們再通過 `BITCOUNT` 統計 bit = 1 的個數便得到了連續打卡 7 天的用戶總數了。

Redis 提供了 `BITOP operation destkey key [key ...]`這個指令用於對一個或者多個 key 的 Bitmap 進行位元操作。

- `operation` 可以是 `and`、`OR`、`NOT`、`XOR`。當 BITOP 處理不同長度的字符串時，較短的那個字符串所缺少的部分會被看作 `0` 。空的 `key` 也被看作是包含 `0` 的字符串序列。

假設要統計 3 天連續打卡的用戶數，則是將三個 bitmap 進行 AND 操作，並將結果保存到 destmap 中，接著對 destmap 執行 BITCOUNT 統計，如下命令：

```shell
# 與操作
BITOP AND destmap bitmap:01 bitmap:02 bitmap:03
# 統計 bit 位 =  1 的個數
BITCOUNT destmap
```

即使一天產生一個億的數據，Bitmap 佔用的內存也不大，大約佔 12 MB 的內存（10^8/8/1024/1024），7 天的 Bitmap 的內存開銷約為 84 MB。同時我們最好給 Bitmap 設置過期時間，讓 Redis 刪除過期的打卡數據，節省內存。

## HyperLogLog

### 介紹

Redis HyperLogLog 是 Redis 2.8.9 版本新增的數據類型，是一種用於「統計基數」的數據集合類型，基數統計就是指統計一個集合中不重複的元素個數。但要注意，HyperLogLog 是統計規則是基於概率完成的，不是非常準確，標準誤算率是 0.81%。

所以，簡單來說 HyperLogLog **提供不精確的去重計數**。

HyperLogLog 的優點是，在輸入元素的數量或者體積非常非常大時，計算基數所需的內存空間總是固定的、並且是很小的。

在 Redis 裡面，**每個 HyperLogLog 鍵只需要花費 12 KB 內存，就可以計算接近 `2^64` 個不同元素的基數**，和元素越多就越耗費內存的 Set 和 Hash 類型相比，HyperLogLog 就非常節省空間。

這什麼概念？舉個例子給大家對比一下。

用 Java 語言來說，一般 long 類型佔用 8 字節，而 1 字節有 8 位，即：1 byte = 8 bit，即 long 數據類型最大可以表示的數是：`2^63-1`。對應上面的`2^64`個數，假設此時有`2^63-1`這麼多個數，從 `0 ~ 2^63-1`，按照`long`以及`1k = 1024 字節`的規則來計算內存總數，就是：`((2^63-1) * 8/1024)K`，這是很龐大的一個數，存儲空間遠遠超過`12K`，而 `HyperLogLog` 卻可以用 `12K` 就能統計完。

### 內部實現

HyperLogLog 的實現涉及到很多數學問題，太費腦子了，我也沒有搞懂，如果你想了解一下，課下可以看看這個：[HyperLogLog](https://en.wikipedia.org/wiki/HyperLogLog)。

### 常見命令

HyperLogLog 命令很少，就三個。

```shell
# 添加指定元素到 HyperLogLog 中
PFADD key element [element ...]

# 返回給定 HyperLogLog 的基數估算值。
PFCOUNT key [key ...]

# 將多個 HyperLogLog 合併為一個 HyperLogLog
PFMERGE destkey sourcekey [sourcekey ...]
```

### 應用場景

#### 百萬級網頁 UV 計數

Redis HyperLogLog  優勢在於只需要花費 12 KB 內存，就可以計算接近 2^64 個元素的基數，和元素越多就越耗費內存的 Set 和 Hash 類型相比，HyperLogLog 就非常節省空間。

所以，非常適合統計百萬級以上的網頁 UV 的場景。

在統計 UV 時，你可以用 PFADD 命令（用於向 HyperLogLog 中添加新元素）把訪問頁面的每個用戶都添加到 HyperLogLog 中。

```shell
PFADD page1:uv user1 user2 user3 user4 user5
```

接下來，就可以用 PFCOUNT 命令直接獲得 page1 的 UV 值了，這個命令的作用就是返回 HyperLogLog 的統計結果。

```shell
PFCOUNT page1:uv
```

不過，有一點需要你注意一下，HyperLogLog 的統計規則是基於概率完成的，所以它給出的統計結果是有一定誤差的，標準誤算率是 0.81%。

這也就意味著，你使用 HyperLogLog 統計的 UV 是 100 萬，但實際的 UV 可能是 101 萬。雖然誤差率不算大，但是，如果你需要精確統計結果的話，最好還是繼續用 Set 或 Hash 類型。

## GEO

Redis GEO 是 Redis 3.2 版本新增的數據類型，主要用於存儲地理位置信息，並對存儲的信息進行操作。

在日常生活中，我們越來越依賴搜索“附近的餐館”、在打車軟件上叫車，這些都離不開基於位置信息服務（Location-Based Service，LBS）的應用。LBS 應用訪問的數據是和人或物關聯的一組經緯度信息，而且要能查詢相鄰的經緯度範圍，GEO 就非常適合應用在 LBS 服務的場景中。

### 內部實現

GEO 本身並沒有設計新的底層數據結構，而是直接使用了 Sorted Set 集合類型。

GEO 類型使用 GeoHash 編碼方法實現了經緯度到 Sorted Set 中元素權重分數的轉換，這其中的兩個關鍵機制就是「對二維地圖做區間劃分」和「對區間進行編碼」。一組經緯度落在某個區間後，就用區間的編碼值來表示，並把編碼值作為 Sorted Set 元素的權重分數。

這樣一來，我們就可以把經緯度保存到 Sorted Set 中，利用 Sorted Set 提供的“按權重進行有序範圍查找”的特性，實現 LBS 服務中頻繁使用的“搜索附近”的需求。

### 常用命令

```shell
# 存儲指定的地理空間位置，可以將一個或多個經度(longitude)、緯度(latitude)、位置名稱(member)添加到指定的 key 中。
GEOADD key longitude latitude member [longitude latitude member ...]

# 從給定的 key 裡返回所有指定名稱(member)的位置（經度和緯度），不存在的返回 nil。
GEOPOS key member [member ...]

# 返回兩個給定位置之間的距離。
GEODIST key member1 member2 [m|km|ft|mi]

# 根據用戶給定的經緯度座標來獲取指定範圍內的地理位置集合。
GEORADIUS key longitude latitude radius m|km|ft|mi [WITHCOORD] [WITHDIST] [WITHHASH] [COUNT count] [ASC|DESC] [STORE key] [STOREDIST key]
```

### 應用場景

#### 滴滴叫車

這裡以滴滴叫車的場景為例，介紹下具體如何使用 GEO 命令：GEOADD 和 GEORADIUS 這兩個命令。

假設車輛 ID 是 33，經緯度位置是（116.034579，39.030452），我們可以用一個 GEO 集合保存所有車輛的經緯度，集合 key 是 cars:locations。

執行下面的這個命令，就可以把 ID 號為 33 的車輛的當前經緯度位置存入 GEO 集合中：

```shell
GEOADD cars:locations 116.034579 39.030452 33
```

當用戶想要尋找自己附近的網約車時，LBS 應用就可以使用 GEORADIUS 命令。

例如，LBS 應用執行下面的命令時，Redis 會根據輸入的用戶的經緯度信息（116.054579，39.030452 ），查找以這個經緯度為中心的 5 公里內的車輛信息，並返回給 LBS 應用。

```shell
GEORADIUS cars:locations 116.054579 39.030452 5 km ASC COUNT 10
```

## Stream

### 介紹

Redis Stream 是 Redis 5.0 版本新增加的數據類型，Redis 專門為消息隊列設計的數據類型。

在 Redis 5.0 Stream 沒出來之前，消息隊列的實現方式都有著各自的缺陷，例如：

- 發佈訂閱模式，不能持久化也就無法可靠的保存消息，並且對於離線重連的客戶端不能讀取歷史消息的缺陷；
- List 實現消息隊列的方式不能重複消費，一個消息消費完就會被刪除，而且生產者需要自行實現全局唯一 ID。

基於以上問題，Redis 5.0 便推出了 Stream 類型也是此版本最重要的功能，用於完美地實現消息隊列，它支持消息的持久化、支持自動生成全局唯一 ID、支持 ack 確認消息的模式、支持消費組模式等，讓消息隊列更加的穩定和可靠。

### 常見命令

Stream 消息隊列操作命令：

- XADD：插入消息，保證有序，可以自動生成全局唯一 ID；
- XLEN ：查詢消息長度；
- XREAD：用於讀取消息，可以按 ID 讀取數據；
- XDEL ： 根據消息 ID 刪除消息；
- DEL ：刪除整個 Stream；
- XRANGE ：讀取區間消息
- XREADGROUP：按消費組形式讀取消息；
- XPENDING 和 XACK：
  - XPENDING 命令可以用來查詢每個消費組內所有消費者「已讀取、但尚未確認」的消息；
  -  XACK 命令用於向消息隊列確認消息處理已完成；

### 應用場景

#### 消息隊列

生產者通過 XADD 命令插入一條消息：

```shell
# * 表示讓 Redis 為插入的數據自動生成一個全局唯一的 ID
# 往名稱為 mymq 的消息隊列中插入一條消息，消息的鍵是 name，值是 xiaolin
> XADD mymq * name xiaolin
"1654254953808-0"
```

插入成功後會返回全局唯一的 ID："1654254953808-0"。消息的全局唯一 ID 由兩部分組成：

- 第一部分“1654254953808”是數據插入時，以毫秒為單位計算的當前服務器時間；
- 第二部分表示插入消息在當前毫秒內的消息序號，這是從 0 開始編號的。例如，“1654254953808-0”就表示在“1654254953808”毫秒內的第 1 條消息。

消費者通過 XREAD 命令從消息隊列中讀取消息時，可以指定一個消息 ID，並從這個消息 ID 的下一條消息開始進行讀取（注意是輸入消息 ID 的下一條信息開始讀取，不是查詢輸入ID的消息）。

```shell
# 從 ID 號為 1654254953807-0 的消息開始，讀取後續的所有消息（示例中一共 1 條）。
> XREAD STREAMS mymq 1654254953807-0
1) 1) "mymq"
   2) 1) 1) "1654254953808-0"
         2) 1) "name"
            2) "xiaolin"
```

如果**想要實現阻塞讀（當沒有數據時，阻塞住），可以調用 XRAED 時設定 BLOCK 配置項**，實現類似於 BRPOP 的阻塞讀取操作。

比如，下面這命令，設置了 BLOCK 10000 的配置項，10000 的單位是毫秒，表明 XREAD 在讀取最新消息時，如果沒有消息到來，XREAD 將阻塞 10000 毫秒（即 10 秒），然後再返回。

```shell
# 命令最後的“$”符號表示讀取最新的消息
> XREAD BLOCK 10000 STREAMS mymq $
(nil)
(10.00s)
```

Stream 的基礎方法，使用 xadd 存入消息和 xread 循環阻塞讀取消息的方式可以實現簡易版的消息隊列，交互流程如下圖所示：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/Stream簡易.png)

> 前面介紹的這些操作 List 也支持的，接下來看看 Stream 特有的功能。

Stream 可以以使用 **XGROUP 創建消費組**，創建消費組之後，Stream 可以使用 XREADGROUP 命令讓消費組內的消費者讀取消息。

創建兩個消費組，這兩個消費組消費的消息隊列是 mymq，都指定從第一條消息開始讀取：

```shell
# 創建一個名為 group1 的消費組，0-0 表示從第一條消息開始讀取。
> XGROUP CREATE mymq group1 0-0
OK
# 創建一個名為 group2 的消費組，0-0 表示從第一條消息開始讀取。
> XGROUP CREATE mymq group2 0-0
OK
```

消費組 group1 內的消費者  consumer1 從 mymq 消息隊列中讀取所有消息的命令如下：

```shell
# 命令最後的參數“>”，表示從第一條尚未被消費的消息開始讀取。
> XREADGROUP GROUP group1 consumer1 STREAMS mymq >
1) 1) "mymq"
   2) 1) 1) "1654254953808-0"
         2) 1) "name"
            2) "xiaolin"
```

**消息隊列中的消息一旦被消費組裡的一個消費者讀取了，就不能再被該消費組內的其他消費者讀取了，即同一個消費組裡的消費者不能消費同一條消息**。

比如說，我們執行完剛才的 XREADGROUP 命令後，再執行一次同樣的命令，此時讀到的就是空值了：

```shell
> XREADGROUP GROUP group1 consumer1 STREAMS mymq >
(nil)
```

但是，**不同消費組的消費者可以消費同一條消息（但是有前提條件，創建消息組的時候，不同消費組指定了相同位置開始讀取消息）**。

比如說，剛才 group1 消費組裡的 consumer1 消費者消費了一條 id 為 1654254953808-0 的消息，現在用 group2 消費組裡的 consumer1 消費者消費消息：

```shell
> XREADGROUP GROUP group2 consumer1 STREAMS mymq >
1) 1) "mymq"
   2) 1) 1) "1654254953808-0"
         2) 1) "name"
            2) "xiaolin"
```

因為我創建兩組的消費組都是從第一條消息開始讀取，所以可以看到第二組的消費者依然可以消費 id 為 1654254953808-0 的這一條消息。因此，不同的消費組的消費者可以消費同一條消息。

使用消費組的目的是讓組內的多個消費者共同分擔讀取消息，所以，我們通常會讓每個消費者讀取部分消息，從而實現消息讀取負載在多個消費者間是均衡分佈的。

例如，我們執行下列命令，讓 group2 中的 consumer1、2、3 各自讀取一條消息。

```shell
# 讓 group2 中的 consumer1 從 mymq 消息隊列中消費一條消息
> XREADGROUP GROUP group2 consumer1 COUNT 1 STREAMS mymq >
1) 1) "mymq"
   2) 1) 1) "1654254953808-0"
         2) 1) "name"
            2) "xiaolin"
# 讓 group2 中的 consumer2 從 mymq 消息隊列中消費一條消息
> XREADGROUP GROUP group2 consumer2 COUNT 1 STREAMS mymq >
1) 1) "mymq"
   2) 1) 1) "1654256265584-0"
         2) 1) "name"
            2) "xiaolincoding"
# 讓 group2 中的 consumer3 從 mymq 消息隊列中消費一條消息
> XREADGROUP GROUP group2 consumer3 COUNT 1 STREAMS mymq >
1) 1) "mymq"
   2) 1) 1) "1654256271337-0"
         2) 1) "name"
            2) "Tom"
```

> 基於 Stream 實現的消息隊列，如何保證消費者在發生故障或宕機再次重啟後，仍然可以讀取未處理完的消息？

Streams 會自動使用內部隊列（也稱為 PENDING List）留存消費組裡每個消費者讀取的消息，直到消費者使用 XACK 命令通知 Streams“消息已經處理完成”。

消費確認增加了消息的可靠性，一般在業務處理完成之後，需要執行 XACK 命令確認消息已經被消費完成，整個流程的執行如下圖所示：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/消息確認.png)

如果消費者沒有成功處理消息，它就不會給 Streams 發送 XACK 命令，消息仍然會留存。此時，**消費者可以在重啟後，用 XPENDING 命令查看已讀取、但尚未確認處理完成的消息**。

例如，我們來查看一下 group2 中各個消費者已讀取、但尚未確認的消息個數，命令如下：

```shell
127.0.0.1:6379> XPENDING mymq group2
1) (integer) 3
2) "1654254953808-0"  # 表示 group2 中所有消費者讀取的消息最小 ID
3) "1654256271337-0"  # 表示 group2 中所有消費者讀取的消息最大 ID
4) 1) 1) "consumer1"
      2) "1"
   2) 1) "consumer2"
      2) "1"
   3) 1) "consumer3"
      2) "1"
```

如果想查看某個消費者具體讀取了哪些數據，可以執行下面的命令：

```shell
# 查看 group2 裡 consumer2 已從 mymq 消息隊列中讀取了哪些消息
> XPENDING mymq group2 - + 10 consumer2
1) 1) "1654256265584-0"
   2) "consumer2"
   3) (integer) 410700
   4) (integer) 1
```

可以看到，consumer2 已讀取的消息的 ID 是 1654256265584-0。

**一旦消息 1654256265584-0 被 consumer2 處理了，consumer2 就可以使用 XACK 命令通知 Streams，然後這條消息就會被刪除**。

```shell
> XACK mymq group2 1654256265584-0
(integer) 1
```

當我們再使用 XPENDING 命令查看時，就可以看到，consumer2 已經沒有已讀取、但尚未確認處理的消息了。

```shell
> XPENDING mymq group2 - + 10 consumer2
(empty array)
```

好了，基於 Stream 實現的消息隊列就說到這裡了，小結一下：

- 消息保序：XADD/XREAD
- 阻塞讀取：XREAD block
- 重複消息處理：Stream 在使用  XADD 命令，會自動生成全局唯一 ID；
- 消息可靠性：內部使用 PENDING List 自動保存消息，使用 XPENDING 命令查看消費組已經讀取但是未被確認的消息，消費者使用 XACK 確認消息；
- 支持消費組形式消費數據

>Redis 基於 Stream 消息隊列與專業的消息隊列有哪些差距？

一個專業的消息隊列，必須要做到兩大塊：

- 消息不丟。
- 消息可堆積。

*1、Redis Stream 消息會丟失嗎？*

使用一個消息隊列，其實就分為三大塊：**生產者、隊列中間件、消費者**，所以要保證消息就是保證三個環節都不能丟失數據。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/redis/數據類型/消息隊列三個階段.png)

Redis Stream 消息隊列能不能保證三個環節都不丟失數據？

- Redis 生產者會不會丟消息？生產者會不會丟消息，取決於生產者對於異常情況的處理是否合理。 從消息被生產出來，然後提交給 MQ 的過程中，只要能正常收到 （ MQ 中間件） 的 ack 確認響應，就表示發送成功，所以只要處理好返回值和異常，如果返回異常則進行消息重發，那麼這個階段是不會出現消息丟失的。
- Redis 消費者會不會丟消息？不會，因為 Stream （ MQ 中間件）會自動使用內部隊列（也稱為 PENDING List）留存消費組裡每個消費者讀取的消息，但是未被確認的消息。消費者可以在重啟後，用 XPENDING 命令查看已讀取、但尚未確認處理完成的消息。等到消費者執行完業務邏輯後，再發送消費確認 XACK 命令，也能保證消息的不丟失。
- Redis 消息中間件會不會丟消息？**會**，Redis 在以下 2 個場景下，都會導致數據丟失：
  - AOF 持久化配置為每秒寫盤，但這個寫盤過程是異步的，Redis 宕機時會存在數據丟失的可能
  - 主從複製也是異步的，[主從切換時，也存在丟失數據的可能](https://xiaolincoding.com/redis/cluster/master_slave_replication.html#redis-%E4%B8%BB%E4%BB%8E%E5%88%87%E6%8D%A2%E5%A6%82%E4%BD%95%E5%87%8F%E5%B0%91%E6%95%B0%E6%8D%AE%E4%B8%A2%E5%A4%B1)。

可以看到，Redis 在隊列中間件環節無法保證消息不丟。像 RabbitMQ 或 Kafka 這類專業的隊列中間件，在使用時是部署一個集群，生產者在發佈消息時，隊列中間件通常會寫「多個節點」，也就是有多個副本，這樣一來，即便其中一個節點掛了，也能保證集群的數據不丟失。

*2、Redis Stream 消息可堆積嗎？*

Redis 的數據都存儲在內存中，這就意味著一旦發生消息積壓，則會導致 Redis 的內存持續增長，如果超過機器內存上限，就會面臨被 OOM 的風險。

所以 Redis 的 Stream 提供了可以指定隊列最大長度的功能，就是為了避免這種情況發生。

當指定隊列最大長度時，隊列長度超過上限後，舊消息會被刪除，只保留固定長度的新消息。這麼來看，Stream 在消息積壓時，如果指定了最大長度，還是有可能丟失消息的。

但 Kafka、RabbitMQ 專業的消息隊列它們的數據都是存儲在磁盤上，當消息積壓時，無非就是多佔用一些磁盤空間。

因此，把 Redis 當作隊列來使用時，會面臨的 2 個問題：

- Redis 本身可能會丟數據；
- 面對消息擠壓，內存資源會緊張；

所以，能不能將 Redis 作為消息隊列來使用，關鍵看你的業務場景：

- 如果你的業務場景足夠簡單，對於數據丟失不敏感，而且消息積壓概率比較小的情況下，把 Redis 當作隊列是完全可以的。
- 如果你的業務有海量消息，消息積壓的概率比較大，並且不能接受數據丟失，那麼還是用專業的消息隊列中間件吧。

> 補充：Redis 發佈/訂閱機制為什麼不可以作為消息隊列？

發佈訂閱機制存在以下缺點，都是跟丟失數據有關：

1. 發佈/訂閱機制沒有基於任何數據類型實現，所以不具備「數據持久化」的能力，也就是發佈/訂閱機制的相關操作，不會寫入到 RDB 和 AOF 中，當 Redis 宕機重啟，發佈/訂閱機制的數據也會全部丟失。
2. 發佈訂閱模式是“發後既忘”的工作模式，如果有訂閱者離線重連之後不能消費之前的歷史消息。
3. 當消費端有一定的消息積壓時，也就是生產者發送的消息，消費者消費不過來時，如果超過 32M 或者是 60s 內持續保持在 8M 以上，消費端會被強行斷開，這個參數是在配置文件中設置的，默認值是 `client-output-buffer-limit pubsub 32mb 8mb 60`。

所以，發佈/訂閱機制只適合即時通訊的場景，比如[構建哨兵集群](https://xiaolincoding.com/redis/cluster/sentinel.html#%E5%93%A8%E5%85%B5%E9%9B%86%E7%BE%A4%E6%98%AF%E5%A6%82%E4%BD%95%E7%BB%84%E6%88%90%E7%9A%84)的場景採用了發佈/訂閱機制。

## 總結

Redis 常見的五種數據類型：**String（字符串），Hash（哈希），List（列表），Set（集合）及 Zset(sorted set：有序集合)**。

這五種數據類型都由多種數據結構實現的，主要是出於時間和空間的考慮，當數據量小的時候使用更簡單的數據結構，有利於節省內存，提高性能。

這五種數據類型與底層數據結構對應關係圖如下，左邊是 Redis 3.0版本的，也就是《Redis 設計與實現》這本書講解的版本，現在看還是有點過時了，右邊是現在 Github 最新的 Redis 代碼的。

![](https://img-blog.csdnimg.cn/img_convert/9fa26a74965efbf0f56b707a03bb9b7f.png)

可以看到，Redis 數據類型的底層數據結構隨著版本的更新也有所不同，比如：

- 在 Redis 3.0 版本中 List 對象的底層數據結構由「雙向鏈表」或「壓縮表列表」實現，但是在 3.2 版本之後，List 數據類型底層數據結構是由 quicklist 實現的；
- 在最新的 Redis 代碼中，壓縮列表數據結構已經廢棄了，交由 listpack 數據結構來實現了。

Redis 五種數據類型的應用場景：

- String 類型的應用場景：緩存對象、常規計數、分佈式鎖、共享session信息等。
- List 類型的應用場景：消息隊列（有兩個問題：1. 生產者需要自行實現全局唯一 ID；2. 不能以消費組形式消費數據）等。
- Hash 類型：緩存對象、購物車等。
- Set 類型：聚合計算（並集、交集、差集）場景，比如點贊、共同關注、抽獎活動等。
- Zset 類型：排序場景，比如排行榜、電話和姓名排序等。

Redis 後續版本又支持四種數據類型，它們的應用場景如下：

-  BitMap（2.2 版新增）：二值狀態統計的場景，比如簽到、判斷用戶登陸狀態、連續簽到用戶總數等；
- HyperLogLog（2.8 版新增）：海量數據基數統計的場景，比如百萬級網頁 UV 計數等；
- GEO（3.2 版新增）：存儲地理位置信息的場景，比如滴滴叫車；
- Stream（5.0 版新增）：消息隊列，相比於基於 List 類型實現的消息隊列，有這兩個特有的特性：自動生成全局唯一消息ID，支持以消費組形式消費數據。

針對 Redis 是否適合做消息隊列，關鍵看你的業務場景：

- 如果你的業務場景足夠簡單，對於數據丟失不敏感，而且消息積壓概率比較小的情況下，把 Redis 當作隊列是完全可以的。
- 如果你的業務有海量消息，消息積壓的概率比較大，並且不能接受數據丟失，那麼還是用專業的消息隊列中間件吧。

---

參考資料：

- 《Redis 核心技術與實戰》
- https://www.cnblogs.com/hunternet/p/12742390.html
- https://www.cnblogs.com/qdhxhz/p/15669348.html
- https://www.cnblogs.com/bbgs-xc/p/14376109.html
- http://kaito-kidd.com/2021/04/19/can-redis-be-used-as-a-queue/

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)