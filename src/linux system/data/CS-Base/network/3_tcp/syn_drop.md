# 4.8 SYN 報文什麼時候情況下會被丟棄？

大家好，我是小林。

之前有個讀者在秋招面試的時候，被問了這麼一個問題：SYN 報文什麼時候情況下會被丟棄？

![](https://img-blog.csdnimg.cn/img_convert/d4df0c85e08f66f6a2aa2038af73adcc.png)

好傢伙，現在面試都問那麼細節了嗎？

不過話說回來，這個問題跟工作上也是有關係的，因為我就在工作中碰到這麼奇怪的時候，客戶端向服務端發起了連接，但是連接並沒有建立起來，通過抓包分析發現，服務端是收到 SYN 報文了，但是並沒有回覆 SYN+ACK（TCP 第二次握手），說明 SYN 報文被服務端忽略了，然後客戶端就一直在超時重傳 SYN 報文，直到達到最大的重傳次數。

接下來，我就給出我遇到過 SYN 報文被丟棄的兩種場景：

- 開啟 tcp_tw_recycle 參數，並且在 NAT 環境下，造成 SYN 報文被丟棄

- TCP 兩個隊列滿了（半連接隊列和全連接隊列），造成 SYN 報文被丟棄

## 坑爹的 tcp_tw_recycle

TCP 四次揮手過程中，主動斷開連接方會有一個 TIME_WAIT 的狀態，這個狀態會持續 2 MSL 後才會轉變為 CLOSED 狀態。

![](https://img-blog.csdnimg.cn/img_convert/bee0c8e8d84047e7434803fb340f9e5d.png)

在 Linux  操作系統下，TIME_WAIT 狀態的持續時間是 60 秒，這意味著這 60 秒內，客戶端一直會佔用著這個端口。要知道，端口資源也是有限的，一般可以開啟的端口為 32768~61000 ，也可以通過如下參數設置指定範圍：

```
 net.ipv4.ip_local_port_range
```

**如果客戶端（發起連接方）的 TIME_WAIT 狀態過多**，佔滿了所有端口資源，那麼就無法對「目的 IP+ 目的 PORT」都一樣的服務器發起連接了，但是被使用的端口，還是可以繼續對另外一個服務器發起連接的。具體可以看我這篇文章：[客戶端的端口可以重複使用嗎？](https://xiaolincoding.com/network/3_tcp/port.html#%E5%AE%A2%E6%88%B7%E7%AB%AF%E7%9A%84%E7%AB%AF%E5%8F%A3%E5%8F%AF%E4%BB%A5%E9%87%8D%E5%A4%8D%E4%BD%BF%E7%94%A8%E5%90%97)

因此，客戶端（發起連接方）都是和「目的 IP+ 目的 PORT 」都一樣的服務器建立連接的話，當客戶端的 TIME_WAIT 狀態連接過多的話，就會受端口資源限制，如果佔滿了所有端口資源，那麼就無法再跟「目的 IP+ 目的 PORT」都一樣的服務器建立連接了。

不過，即使是在這種場景下，只要連接的是不同的服務器，端口是可以重複使用的，所以客戶端還是可以向其他服務器發起連接的，這是因為內核在定位一個連接的時候，是通過四元組（源IP、源端口、目的IP、目的端口）信息來定位的，並不會因為客戶端的端口一樣，而導致連接衝突。

但是 TIME_WAIT 狀態也不是擺設作用，它的作用有兩個：

- 防止具有相同四元組的舊數據包被收到，也就是防止歷史連接中的數據，被後面的連接接受，否則就會導致後面的連接收到一個無效的數據，
- 保證「被動關閉連接」的一方能被正確的關閉，即保證最後的 ACK 能讓被動關閉方接收，從而幫助其正常關閉;

不過，Linux 操作系統提供了兩個可以系統參數來快速回收處於 TIME_WAIT 狀態的連接，這兩個參數都是默認關閉的：

- net.ipv4.tcp_tw_reuse，如果開啟該選項的話，客戶端（連接發起方） 在調用 connect() 函數時，**如果內核選擇到的端口，已經被相同四元組的連接佔用的時候，就會判斷該連接是否處於 TIME_WAIT 狀態，如果該連接處於 TIME_WAIT 狀態並且 TIME_WAIT 狀態持續的時間超過了 1 秒，那麼就會重用這個連接，然後就可以正常使用該端口了。**所以該選項只適用於連接發起方。
- net.ipv4.tcp_tw_recycle，如果開啟該選項的話，允許處於 TIME_WAIT 狀態的連接被快速回收；

要使得這兩個選項生效，有一個前提條件，就是要打開 TCP 時間戳，即 net.ipv4.tcp_timestamps=1（默認即為 1)）。

**tcp_tw_recycle 在使用了 NAT 的網絡下是不安全的！**

對於服務器來說，如果同時開啟了recycle 和 timestamps 選項，則會開啟一種稱之為「 per-host 的 PAWS 機制」。

> 首先給大家說說什麼是  PAWS 機制？

tcp_timestamps 選項開啟之後， PAWS 機制會自動開啟，它的作用是防止 TCP 包中的序列號發生繞回。

正常來說每個 TCP 包都會有自己唯一的 SEQ，出現 TCP 數據包重傳的時候會複用 SEQ 號，這樣接收方能通過 SEQ 號來判斷數據包的唯一性，也能在重複收到某個數據包的時候判斷數據是不是重傳的。**但是 TCP 這個 SEQ 號是有限的，一共 32 bit，SEQ 開始是遞增，溢出之後從 0 開始再次依次遞增**。

所以當 SEQ 號出現溢出後單純通過 SEQ 號無法標識數據包的唯一性，某個數據包延遲或因重發而延遲時可能導致連接傳遞的數據被破壞，比如：

![](https://img-blog.csdnimg.cn/img_convert/f5fbe947240026cc2f076267cb698496.png)

上圖 A 數據包出現了重傳，並在 SEQ 號耗盡再次從 A 遞增時，第一次發的 A 數據包延遲到達了 Server，這種情況下如果沒有別的機制來保證，Server 會認為延遲到達的 A 數據包是正確的而接收，反而是將正常的第三次發的 SEQ 為 A 的數據包丟棄，造成數據傳輸錯誤。

PAWS 就是為了避免這個問題而產生的，在開啟 tcp_timestamps 選項情況下，一臺機器發的所有 TCP 包都會帶上發送時的時間戳，PAWS 要求連接雙方維護最近一次收到的數據包的時間戳（Recent TSval），每收到一個新數據包都會讀取數據包中的時間戳值跟 Recent TSval 值做比較，**如果發現收到的數據包中時間戳不是遞增的，則表示該數據包是過期的，就會直接丟棄這個數據包**。

對於上面圖中的例子有了 PAWS 機制就能做到在收到 Delay 到達的 A 號數據包時，識別出它是個過期的數據包而將其丟掉。

> 那什麼是 per-host 的 PAWS 機制呢？

前面我提到，開啟了 recycle 和 timestamps 選項，就會開啟一種叫 per-host 的 PAWS 機制。**per-host 是對「對端 IP 做 PAWS 檢查」**，而非對「IP + 端口」四元組做 PAWS 檢查。

但是如果客戶端網絡環境是用了 NAT 網關，那麼客戶端環境的每一臺機器通過 NAT 網關後，都會是相同的 IP 地址，在服務端看來，就好像只是在跟一個客戶端打交道一樣，無法區分出來。

Per-host PAWS 機制利用TCP option裡的 timestamp 字段的增長來判斷串擾數據，而 timestamp 是根據客戶端各自的 CPU tick 得出的值。

當客戶端 A 通過 NAT 網關和服務器建立 TCP 連接，然後服務器主動關閉並且快速回收 TIME-WAIT 狀態的連接後，**客戶端 B 也通過 NAT 網關和服務器建立 TCP 連接，注意客戶端 A  和 客戶端 B 因為經過相同的 NAT 網關，所以是用相同的 IP 地址與服務端建立 TCP 連接，如果客戶端 B 的 timestamp 比 客戶端 A 的 timestamp 小，那麼由於服務端的 per-host 的 PAWS 機制的作用，服務端就會丟棄客戶端主機 B 發來的 SYN 包**。

因此，tcp_tw_recycle 在使用了 NAT 的網絡下是存在問題的，如果它是對 TCP 四元組做 PAWS 檢查，而不是對「相同的 IP 做 PAWS 檢查」，那麼就不會存在這個問題了。

網上很多博客都說開啟 tcp_tw_recycle 參數來優化 TCP，我信你個鬼，糟老頭壞的很！

tcp_tw_recycle 在 Linux 4.12 版本後，直接取消了這一參數。

## accpet 隊列滿了

在 TCP 三次握手的時候，Linux 內核會維護兩個隊列，分別是：

- 半連接隊列，也稱 SYN 隊列；
- 全連接隊列，也稱 accepet 隊列；

服務端收到客戶端發起的 SYN 請求後，**內核會把該連接存儲到半連接隊列**，並向客戶端響應 SYN+ACK，接著客戶端會返回 ACK，服務端收到第三次握手的 ACK 後，**內核會把連接從半連接隊列移除，然後創建新的完全的連接，並將其添加到 accept 隊列，等待進程調用 accept 函數時把連接取出來。**

![](https://img-blog.csdnimg.cn/img_convert/c9959166180b0e239bb48234ff7c2f5b.png)



### 半連接隊列滿了

當服務器造成syn攻擊，就有可能導致 **TCP 半連接隊列滿了，這時後面來的 syn 包都會被丟棄**。

但是，**如果開啟了syncookies 功能，即使半連接隊列滿了，也不會丟棄syn 包**。

syncookies 是這麼做的：服務器根據當前狀態計算出一個值，放在己方發出的 SYN+ACK 報文中發出，當客戶端返回 ACK 報文時，取出該值驗證，如果合法，就認為連接建立成功，如下圖所示。

![](https://img-blog.csdnimg.cn/img_convert/58e01036d1febd0103dd0ec4d5acff05.png)

syncookies 參數主要有以下三個值：

- 0 值，表示關閉該功能；
- 1 值，表示僅當 SYN 半連接隊列放不下時，再啟用它；
- 2 值，表示無條件開啟功能；

那麼在應對 SYN 攻擊時，只需要設置為 1 即可：


![](https://img-blog.csdnimg.cn/img_convert/e795b4ff5be76c85814ee190b4921f25.png)

這裡給出幾種防禦 SYN 攻擊的方法：

- 增大半連接隊列；
- 開啟 tcp_syncookies 功能
- 減少 SYN+ACK 重傳次數

*方式一：增大半連接隊列*

**要想增大半連接隊列，我們得知不能只單純增大 tcp_max_syn_backlog 的值，還需一同增大 somaxconn 和 backlog，也就是增大全連接隊列**。否則，只單純增大 tcp_max_syn_backlog 是無效的。

增大 tcp_max_syn_backlog 和 somaxconn 的方法是修改 Linux 內核參數：

![](https://img-blog.csdnimg.cn/img_convert/29f1fd2894162e15cbac938a2373b543.png)

增大 backlog 的方式，每個 Web 服務都不同，比如 Nginx 增大 backlog 的方法如下：

![](https://img-blog.csdnimg.cn/img_convert/a6b11fbd1fcb742cdcc87447fc23b73f.png)

最後，改變瞭如上這些參數後，要重啟 Nginx 服務，因為半連接隊列和全連接隊列都是在 listen() 初始化的。

*方式二：開啟 tcp_syncookies 功能*

開啟 tcp_syncookies 功能的方式也很簡單，修改 Linux 內核參數：

![](https://img-blog.csdnimg.cn/img_convert/54b7411607978cb9ff36d88cf47eb5c4.png)

*方式三：減少 SYN+ACK 重傳次數*

當服務端受到 SYN 攻擊時，就會有大量處於 SYN_RECV 狀態的 TCP 連接，處於這個狀態的 TCP 會重傳 SYN+ACK ，當重傳超過次數達到上限後，就會斷開連接。

那麼針對 SYN 攻擊的場景，我們可以減少 SYN+ACK 的重傳次數，以加快處於 SYN_RECV 狀態的 TCP 連接斷開。

![](https://img-blog.csdnimg.cn/img_convert/19443a03430368b72c201113150471c5.png)

### 全連接隊列滿了

**在服務端併發處理大量請求時，如果 TCP accpet 隊列過小，或者應用程序調用 accept() 不及時，就會造成 accpet 隊列滿了 ，這時後續的連接就會被丟棄，這樣就會出現服務端請求數量上不去的現象。**

![](https://img-blog.csdnimg.cn/img_convert/d1538f8d3b50da26039bc6b171a13ad1.png)

我們可以通過 ss 命令來看 accpet 隊列大小，在「LISTEN 狀態」時，`Recv-Q/Send-Q` 表示的含義如下：

![](https://img-blog.csdnimg.cn/img_convert/d7e8fcbb4afa583687b76064b7f1afac.png)


- Recv-Q：當前 accpet 隊列的大小，也就是當前已完成三次握手並等待服務端 `accept()` 的 TCP 連接個數；
- Send-Q：當前 accpet 最大隊列長度，上面的輸出結果說明監聽 8088 端口的 TCP 服務進程，accpet 隊列的最大長度為 128；

如果 Recv-Q 的大小超過 Send-Q，就說明發生了 accpet 隊列滿的情況。

要解決這個問題，我們可以：

- 調大 accpet 隊列的最大長度，調大的方式是通過**調大 backlog 以及 somaxconn 參數。**
- 檢查系統或者代碼為什麼調用 accept()  不及時；

關於 SYN 隊列和 accpet 隊列，我之前寫過一篇很詳細的文章：[TCP 半連接隊列和全連接隊列滿了會發生什麼？又該如何應對？](https://mp.weixin.qq.com/s/2qN0ulyBtO2I67NB_RnJbg)

---

好了，今天就分享到這裡啦。

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

