# update 沒加索引會鎖全表？

大家好，我是小林。

昨晚在群划水的時候，看到有位讀者說了這麼一件事。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/202e1521bc02411698eb6162cf121114.png)


大概就是，在線上執行一條 update 語句修改數據庫數據的時候，where 條件沒有帶上索引，導致業務直接崩了，被老闆教訓了一波

這次我們就來看看：
- 為什麼會發生這種的事故？
- 又該如何避免這種事故的發生？

說個前提，接下來說的案例都是基於 InnoDB 存儲引擎，且事務的隔離級別是可重複讀。

## 為什麼會發生這種的事故？


InnoDB 存儲引擎的默認事務隔離級別是「可重複讀」，但是在這個隔離級別下，在多個事務併發的時候，會出現幻讀的問題，所謂的幻讀是指在同一事務下，連續執行兩次同樣的查詢語句，第二次的查詢語句可能會返回之前不存在的行。

因此 InnoDB 存儲引擎自己實現了行鎖，通過 next-key  鎖（記錄鎖和間隙鎖的組合）來鎖住記錄本身和記錄之間的“間隙”，防止其他事務在這個記錄之間插入新的記錄，從而避免了幻讀現象。


當我們執行 update 語句時，實際上是會對記錄加獨佔鎖（X 鎖）的，如果其他事務對持有獨佔鎖的記錄進行修改時是會被阻塞的。另外，這個鎖並不是執行完 update 語句就會釋放的，而是會等事務結束時才會釋放。

在 InnoDB 事務中，對記錄加鎖帶基本單位是 next-key 鎖，但是會因為一些條件會退化成間隙鎖，或者記錄鎖。加鎖的位置準確的說，鎖是加在索引上的而非行上。

比如，在 update 語句的 where 條件使用了唯一索引，那麼 next-key 鎖會退化成記錄鎖，也就是隻會給一行記錄加鎖。

這裡舉個例子，這裡有一張數據庫表，其中 id 為主鍵索引。

![](https://img-blog.csdnimg.cn/img_convert/3c3af16e7a948833ccb6409e8b51daf8.png)


假設有兩個事務的執行順序如下：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/d2326f98cbb34fc09ca4013703251501.png)


可以看到，事務 A 的 update 語句中 where 是等值查詢，並且 id 是唯一索引，所以只會對 id = 1 這條記錄加鎖，因此，事務 B 的更新操作並不會阻塞。


但是，**在 update 語句的 where 條件沒有使用索引，就會全表掃描，於是就會對所有記錄加上 next-key 鎖（記錄鎖 + 間隙鎖），相當於把整個表鎖住了**。

假設有兩個事務的執行順序如下：

![](https://img-blog.csdnimg.cn/img_convert/1aa886fe95e7bc791c296e2d342fa435.png)


可以看到，這次事務 B 的 update 語句被阻塞了。

這是因為事務 A的 update 語句中 where 條件沒有索引列，觸發了全表掃描，在掃描過程中會對索引加鎖，所以全表掃描的場景下，所有記錄都會被加鎖，也就是這條 update 語句產生了 4 個記錄鎖和 5 個間隙鎖，相當於鎖住了全表。


![](https://img-blog.csdnimg.cn/img_convert/63e055617720853f5b64c99576227c09.png)


因此，當在數據量非常大的數據庫表執行 update 語句時，如果沒有使用索引，就會給全表的加上 next-key 鎖， 那麼鎖就會持續很長一段時間，直到事務結束，而這期間除了 `select ... from `語句，其他語句都會被鎖住不能執行，業務會因此停滯，接下來等著你的，就是老闆的捱罵。

那 update 語句的 where 帶上索引就能避免全表記錄加鎖了嗎？

並不是。

**關鍵還得看這條語句在執行過程種，優化器最終選擇的是索引掃描，還是全表掃描，如果走了全表掃描，就會對全表的記錄加鎖了**。

:::tip

網上很多資料說，update 沒加鎖索引會加表鎖，這是不對的。

Innodb 源碼裡面在掃描記錄的時候，都是針對索引項這個單位去加鎖的， update 不帶索引就是全表掃掃描，也就是表裡的索引項都加鎖，相當於鎖了整張表，所以大家誤以為加了表鎖。

:::


## 如何避免這種事故的發生？

我們可以將 MySQL 裡的 `sql_safe_updates` 參數設置為 1，開啟安全更新模式。

> 官方的解釋：
> If set to 1, MySQL aborts UPDATE or DELETE statements that do not use a key in the WHERE clause or a LIMIT clause. (Specifically, UPDATE statements must have a WHERE clause that uses a key or a LIMIT clause, or both. DELETE statements must have both.) This makes it possible to catch UPDATE or DELETE statements where keys are not used properly and that would probably change or delete a large number of rows. The default value is 0.

大致的意思是，當 sql_safe_updates 設置為 1 時。

update 語句必須滿足如下條件之一才能執行成功：
- 使用 where，並且 where 條件中必須有索引列；
- 使用 limit；
- 同時使用 where 和 limit，此時 where 條件中可以沒有索引列；

delete 語句必須滿足以下條件能執行成功：
- 同時使用 where 和 limit，此時 where 條件中可以沒有索引列；

如果 where 條件帶上了索引列，但是優化器最終掃描選擇的是全表，而不是索引的話，我們可以使用 `force index([index_name])` 可以告訴優化器使用哪個索引，以此避免有機率鎖全錶帶來的隱患。

##  總結

不要小看一條 update 語句，在生產機上使用不當可能會導致業務停滯，甚至崩潰。

當我們要執行 update 語句的時候，確保 where 條件中帶上了索引列，並且在測試機確認該語句是否走的是索引掃描，防止因為掃描全表，而對錶中的所有記錄加上鎖。

我們可以打開 MySQL sql_safe_updates 參數，這樣可以預防 update 操作時 where 條件沒有帶上索引列。

如果發現即使在 where 條件中帶上了索引列，優化器走的還是全表掃描，這時我們就要使用 `force index([index_name])` 可以告訴優化器使用哪個索引。

這次就說到這啦，下次要小心點，別再被老闆捱罵啦。

----

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)