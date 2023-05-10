# 4.10 四次揮手中收到亂序的 FIN 包會如何處理？

大家好，我是小林。

收到個讀者的問題，他在面試鵝廠的時候，被搞懵了，因為面試官問了他這麼一個網絡問題：

![](https://img-blog.csdnimg.cn/39f790ee7a45473587c8fe3e08e01ba4.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_17,color_FFFFFF,t_70,g_se,x_16)

不得不說，鵝廠真的很喜歡問網絡問題，而且愛問異常情況下的網絡問題，之前也有篇另外一個讀者面試鵝廠的網絡問題：「[被鵝廠面怕了！](https://blog.csdn.net/qq_34827674/article/details/117922761)」。


不過這道鵝廠的網絡題可能是提問的讀者表述有問題，**因為如果 FIN 報文比數據包先抵達客戶端，此時 FIN 報文其實是一個亂序的報文，此時客戶端的 TCP 連接並不會從 FIN_WAIT_2 狀態轉換到 TIME_WAIT 狀態**。

![](https://img-blog.csdnimg.cn/ccabc2f21b014c6c9118cd29ae11c18c.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)

因此，我們要關注到點是看「**在 FIN_WAIT_2 狀態下，是如何處理收到的亂序到 FIN 報文，然後 TCP 連接又是什麼時候才進入到 TIME_WAIT 狀態?**」。

我這裡先直接說結論：

**在 FIN_WAIT_2 狀態時，如果收到亂序的 FIN 報文，那麼就被會加入到「亂序隊列」，並不會進入到 TIME_WAIT 狀態。**

**等再次收到前面被網絡延遲的數據包時，會判斷亂序隊列有沒有數據，然後會檢測亂序隊列中是否有可用的數據，如果能在亂序隊列中找到與當前報文的序列號保持的順序的報文，就會看該報文是否有 FIN 標誌，如果發現有 FIN 標誌，這時才會進入 TIME_WAIT 狀態。**

我也畫了一張圖，大家可以結合著圖來理解。

![](https://img-blog.csdnimg.cn/4effcf2a9e7e4adeb892da98ee21694b.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)
## TCP 源碼分析
接下來，我帶大家看看源碼，聽到要源碼分析，可能有的同學就慫了。

其實要分析我們今天這個問題，只要懂 if else 就行了，我也會用中文來表述代碼的邏輯，所以單純看我的文字也是可以的。

這次我們重點分析的是，在 FIN_WAIT_2 狀態下，收到 FIN 報文是如何處理的。

在 Linux 內核裡，當 IP 層處理完消息後，會通過回調 tcp_v4_rcv 函數將消息轉給 TCP 層，所以這個函數就是 TCP 層收到消息的入口。

![](https://img-blog.csdnimg.cn/ad39a3204f914df89aa6c6138cfc31aa.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)
處於 FIN_WAIT_2 狀態下的客戶端，在收到服務端的報文後，最終會調用 tcp_v4_do_rcv 函數。


![](https://img-blog.csdnimg.cn/c5ca5b3fea0e4ad6baa2ab370358f03e.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)

接下來，tcp_v4_do_rcv 方法會調用 tcp_rcv_state_process，在這裡會根據 TCP 狀態做對應的處理，這裡我們只關注 FIN_WAIT_2 狀態。

![](https://img-blog.csdnimg.cn/f76b7e2167544fec859700f55138e95f.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)

在上面這個代碼裡，可以看到如果 shutdown 關閉了讀方向，那麼在收到對方發來的數據包，則會回覆 RST 報文。

而我們這次的題目裡， shutdown 只關閉了寫方向，所以會繼續往下調用 tcp_data_queue 函數（因為 case TCP_FIN_WAIT2 代碼塊裡並沒有 break 語句，所以會走到該函數）。

![](https://img-blog.csdnimg.cn/4ff161a34408447fa38b120b014b29f4.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)
在上面的 tcp_data_queue 函數裡，如果收到的報文的序列號是我們預期的，也就是有序的話：
- 會判斷該報文有沒有 FIN 標誌，如果有的話就會調用 tcp_fin 函數，這個函數負責將 FIN_WAIT_2 狀態轉換為 TIME_WAIT。
- 接著還會看亂序隊列有沒有數據，如果有的話會調用 tcp_ofo_queue 函數，這個函數負責檢查亂序隊列中是否有數據包可用，即能不能在亂序隊列找到與當前數據包保持序列號連續的數據包。

而當收到的報文的序列號不是我們預期的，也就是亂序的話，則調用 tcp_data_queue_ofo 函數，將報文加入到亂序隊列，這個隊列的數據結構是紅黑樹。

我們的題目裡，客戶端收到的 FIN 報文實際上是一個亂序的報文，因此此時並不會調用 tcp_fin 函數進行狀態轉換，而是將報文通過 tcp_data_queue_ofo 函數加入到亂序隊列。

然後當客戶端收到被網絡延遲的數據包後，此時因為該數據包的序列號是期望的，然後又因為上一次收到的亂序 FIN 報文被加入到了亂序隊列，表明亂序隊列是有數據的，於是就會調用 tcp_ofo_queue 函數。

我們來看看 tcp_ofo_queue 函數。

![](https://img-blog.csdnimg.cn/dd51b407245d45549eeae64d24634133.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)

在上面的 tcp_ofo_queue 函數裡，在亂序隊列中找到能與當前報文的序列號保持的順序的報文後，會看該報文是否有 FIN 標誌，如果有的話，就會調用 tcp_fin() 函數。

最後，我們來看看 tcp_fin 函數的處理。

![](https://img-blog.csdnimg.cn/67b33007fcd04d2fa98e79d19823fc95.jpg?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)

可以看到，如果當前的 TCP 狀態為 TCP_FIN_WAIT2，就會發送第四次揮手 ack，然後調用 tcp_time_wait 函數，這個函數裡會將 TCP 狀態變更為 TIME_WAIT，並啟動 TIME_WAIT 的定時器。

## 怎麼看 TCP 源碼？
之前有不少同學問我，我是怎麼看 TCP 源碼的？

其實我看 TCP 源碼，並不是直接打開 Linux 源碼直接看，因為 Linux 源碼實在太龐大了，如果我不知道 TCP 入口函數在哪，那簡直就是大海撈針。



所以，在看 TCP 源碼，我們可以去網上搜索下別人的源碼分析，網上已經有很多前輩幫我們分析了 TCP 源碼了，而且各個函數的調用鏈路，他們都有寫出來了。


比如，你想了解 TCP 三次握手/四次揮手的源碼實現，你就可以以「TCP 三次握手/四次揮手的源碼分析」這樣關鍵字來搜索，大部分文章的註釋寫的還是很清晰，我最開始就按這種方式來學習 TCP 源碼的。

網上的文章一般只會將重點的部分，很多代碼細節沒有貼出來，如果你想完整的看到函數的所有代碼，那就得看內核代碼了。


這裡推薦個看 Linux 內核代碼的在線網站：

https://elixir.bootlin.com/linux/latest/source

![](https://img-blog.csdnimg.cn/c56e69f998e747208abb82897edc2629.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBA5bCP5p6XY29kaW5n,size_20,color_FFFFFF,t_70,g_se,x_16)


我覺得還是挺好用的，左側各個版本的代碼都有，右上角也可以搜索函數。

所以，我看 TCP 源碼的經驗就是，先在網上找找前輩寫的 TCP 源碼分析，然後知道整個函數的調用鏈路後，如果想具體瞭解某個函數的具體實現，可以在我說的那個看 Linux 內核代碼的在線網站上搜索該函數，就可以看到完整的函數的實現。如果中途遇到看不懂的代碼，也可以將這個代碼複製到百度或者谷歌搜索，一般也能找到別人分析的過程。

學會了看 TCP 源碼其實有助於我們分析一些異常問題，就比如今天這道網絡題目，在網上其實是搜索不出答案的，而且我們也很難用實驗的方式來模擬。

所以要想知道答案，只能去看源碼。

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)