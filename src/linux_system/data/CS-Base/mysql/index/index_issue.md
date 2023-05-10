# MySQL 使用 like “%x“，索引一定會失效嗎？ 



大家好，我是小林。

昨天發了一篇關於索引失效的文章：[誰還沒碰過索引失效呢](http://mp.weixin.qq.com/s?__biz=MzUxODAzNDg4NQ==&mid=2247503394&idx=1&sn=6e5b7b2c9bd9002a4b2dfa69273069b3&chksm=f98d8a88cefa039e726f1196ba14210ddbe49b5fcbb6da620778a7497fa25404433ef0b76268&scene=21#wechat_redirect)

我在文末留了一個有點意思的思考題：

![圖片](https://img-blog.csdnimg.cn/img_convert/c3e14ca7c5581a84820f7a9d647d4d14.png)



這個思考題其實是出自於，我之前這篇文章「[一條 SQL 語句引發的思考](http://mp.weixin.qq.com/s?__biz=MzUxODAzNDg4NQ==&mid=2247495686&idx=2&sn=dfa18870d8cd2f430f893d402b9f4e54&chksm=f98db4accefa3dba680c1b343700ef87d184c45d4d7739bb0263cece3c1b21d0ca5f875736f6&scene=21#wechat_redirect)」中留言區一位讀者朋友出的問題。

很多讀者都在留言區說了自己的想法，也有不少讀者私聊我答案到底是什麼？

所以，我今晚就跟大家聊聊這個思考題。

### 題目一 

題目一很簡單，相信大家都能分析出答案，我昨天分享的索引失效文章裡也提及過。

**「題目 1 」**的數據庫表如下，id 是主鍵索引，name 是二級索引，其他字段都是非索引字段。

![圖片](https://img-blog.csdnimg.cn/img_convert/f46694a7f2c91443b616eadf8526c09a.png)

這四條模糊匹配的查詢語句，第一條和第二條都會走索引掃描，而且都是選擇掃描二級索引（index_name），我貼個第二條查詢語句的執行計劃結果圖：

![圖片](https://img-blog.csdnimg.cn/img_convert/febffda129751df080f734c1fc7980f1.png)



而第三和第四條會發生索引失效，執行計劃的結果 type= ALL，代表了全表掃描。

![圖片](https://img-blog.csdnimg.cn/img_convert/52952f616b03318e196b6e1207b888ad.png)



### 題目二

題目 2 的數據庫表特別之處在於，只有兩個字段，一個是主鍵索引 id，另外一個是二級索引 name。

![圖片](https://img-blog.csdnimg.cn/img_convert/a80a15eb8cd65eec777908282e04be2a.png)

針對題目 2 的數據表，第一條和第二條模糊查詢語句也是一樣可以走索引掃描，第二條查詢語句的執行計劃如下，Extra 裡的 Using index 說明用上了覆蓋索引：

![圖片](https://img-blog.csdnimg.cn/img_convert/d250a6ba3068ef41da9039974dad206a.png)

我們來看一下第三條查詢語句的執行計劃（第四條也是一樣的結果）：

![圖片](https://img-blog.csdnimg.cn/img_convert/948ac3e63c36a93101860e7da11ddc42.png)

從執行計劃的結果中，可以看到 key=index_name，也就是說用上了二級索引，而且從 Extra 裡的 Using index 說明用上了覆蓋索引。

這是為什麼呢？

首先，這張表的字段沒有「非索引」字段，所以 `select *` 相當於 `select id,name`，然後**這個查詢的數據都在二級索引的 B+ 樹，因為二級索引的 B+ 樹的葉子節點包含「索引值+主鍵值」，所以查二級索引的 B+ 樹就能查到全部結果了，這個就是覆蓋索引。**

但是執行計劃裡的 type 是 `index`，這代表著是通過全掃描二級索引的 B+ 樹的方式查詢到數據的，也就是遍歷了整顆索引樹。

而第一和第二條查詢語句的執行計劃中 type 是 `range`，表示對索引列進行範圍查詢，也就是利用了索引樹的有序性的特點，通過查詢比較的方式，快速定位到了數據行。

所以，type=range 的查詢效率會比 type=index 的高一些。

> 為什麼選擇全掃描二級索引樹，而不掃描聚簇索引樹呢？

因為二級索引樹的記錄東西很少，就只有「索引列+主鍵值」，而聚簇索引記錄的東西會更多，比如聚簇索引中的葉子節點則記錄了主鍵值、事務 id、用於事務和 MVCC 的回滾指針以及所有的剩餘列。

再加上，這個 select * 不用執行回表操作。

所以， MySQL 優化器認為直接遍歷二級索引樹要比遍歷聚簇索引樹的成本要小的多，因此 MySQL 選擇了「全掃描二級索引樹」的方式查詢數據。

> 為什麼這個數據表加了非索引字段，執行同樣的查詢語句後，怎麼變成走的是全表掃描呢？

加了其他字段後，`select * from t_user where name like "%xx";` 要查詢的數據就不能只在二級索引樹裡找了，得需要回表操作才能完成查詢的工作，再加上是左模糊匹配，無法利用索引樹的有序性來快速定位數據，所以得在二級索引樹逐一遍歷，獲取主鍵值後，再到聚簇索引樹檢索到對應的數據行，這樣實在太累了。

所以，優化器認為上面這樣的查詢過程的成本實在太高了，所以直接選擇全表掃描的方式來查詢數據。

------

從這個思考題我們知道了，使用左模糊匹配（like "%xx"）並不一定會走全表掃描，關鍵還是看數據表中的字段。

如果數據庫表中的字段只有主鍵+二級索引，那麼即使使用了左模糊匹配，也不會走全表掃描（type=all），而是走全掃描二級索引樹(type=index)。

再說一個相似，我們都知道聯合索引要遵循最左匹配才能走索引，但是如果數據庫表中的字段都是索引的話，即使查詢過程中，沒有遵循最左匹配原則，也是走全掃描二級索引樹(type=index)，比如下圖：

![圖片](https://img-blog.csdnimg.cn/img_convert/35d04bff09bb638727245c7f9aa95b5c.png)

就說到這了，下次見啦

----

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)