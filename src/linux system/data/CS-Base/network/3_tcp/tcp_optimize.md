# 4.5 如何優化 TCP?

TCP 性能的提升不僅考察 TCP 的理論知識，還考察了對於操作系統提供的內核參數的理解與應用。

TCP 協議是由操作系統實現，所以操作系統提供了不少調節 TCP 的參數。

![Linux TCP 參數](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/2.jpg)


如何正確有效的使用這些參數，來提高 TCP 性能是一個不那麼簡單事情。我們需要針對 TCP 每個階段的問題來對症下藥，而不是病急亂投醫。

接下來，將以三個角度來闡述提升 TCP 的策略，分別是：

- TCP 三次握手的性能提升；
- TCP 四次揮手的性能提升；
- TCP 數據傳輸的性能提升；

![本節提綱](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/3.jpg)

---

## TCP 三次握手的性能提升

TCP 是面向連接的、可靠的、雙向傳輸的傳輸層通信協議，所以在傳輸數據之前需要經過三次握手才能建立連接。

![三次握手與數據傳輸](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/4.jpg)

那麼，三次握手的過程在一個 HTTP 請求的平均時間佔比 10% 以上，在網絡狀態不佳、高併發或者遭遇 SYN 攻擊等場景中，如果不能有效正確的調節三次握手中的參數，就會對性能產生很多的影響。

如何正確有效的使用這些參數，來提高 TCP 三次握手的性能，這就需要理解「三次握手的狀態變遷」，這樣當出現問題時，先用 `netstat` 命令查看是哪個握手階段出現了問題，再來對症下藥，而不是病急亂投醫。

![TCP 三次握手的狀態變遷](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/5.jpg)

客戶端和服務端都可以針對三次握手優化性能。主動發起連接的客戶端優化相對簡單些，而服務端需要監聽端口，屬於被動連接方，其間保持許多的中間狀態，優化方法相對複雜一些。

所以，客戶端（主動發起連接方）和服務端（被動連接方）優化的方式是不同的，接下來分別針對客戶端和服務端優化。

### 客戶端優化

三次握手建立連接的首要目的是「同步序列號」。

只有同步了序列號才有可靠傳輸，TCP 許多特性都依賴於序列號實現，比如流量控制、丟包重傳等，這也是三次握手中的報文稱為 SYN 的原因，SYN 的全稱就叫 *Synchronize Sequence Numbers*（同步序列號）。

![TCP 頭部](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/6.jpg)

> SYN_SENT 狀態的優化

客戶端作為主動發起連接方，首先它將發送 SYN 包，於是客戶端的連接就會處於 `SYN_SENT` 狀態。

客戶端在等待服務端回覆的 ACK 報文，正常情況下，服務器會在幾毫秒內返回 SYN+ACK ，但如果客戶端長時間沒有收到 SYN+ACK 報文，則會重發 SYN 包，**重發的次數由 tcp_syn_retries 參數控制**，默認是 5 次：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/7.jpg)

通常，第一次超時重傳是在 1 秒後，第二次超時重傳是在 2 秒，第三次超時重傳是在 4 秒後，第四次超時重傳是在 8 秒後，第五次是在超時重傳 16 秒後。沒錯，**每次超時的時間是上一次的 2 倍**。

當第五次超時重傳後，會繼續等待 32 秒，如果服務端仍然沒有迴應 ACK，客戶端就會終止三次握手。

所以，總耗時是 1+2+4+8+16+32=63 秒，大約 1 分鐘左右。

![SYN 超時重傳](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/8.jpg)

你可以根據網絡的穩定性和目標服務器的繁忙程度修改 SYN 的重傳次數，調整客戶端的三次握手時間上限。比如內網中通訊時，就可以適當調低重試次數，儘快把錯誤暴露給應用程序。

### 服務端優化


當服務端收到 SYN 包後，服務端會立馬回覆 SYN+ACK 包，表明確認收到了客戶端的序列號，同時也把自己的序列號發給對方。

此時，服務端出現了新連接，狀態是 `SYN_RCV`。在這個狀態下，Linux 內核就會建立一個「半連接隊列」來維護「未完成」的握手信息，當半連接隊列溢出後，服務端就無法再建立新的連接。

![半連接隊列與全連接隊列](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/9.jpg)

SYN 攻擊，攻擊的是就是這個半連接隊列。

> 如何查看由於 SYN 半連接隊列已滿，而被丟棄連接的情況？

我們可以通過該 `netstat -s` 命令給出的統計結果中，  可以得到由於半連接隊列已滿，引發的失敗次數：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/10.jpg)

上面輸出的數值是**累計值**，表示共有多少個 TCP 連接因為半連接隊列溢出而被丟棄。**隔幾秒執行幾次，如果有上升的趨勢，說明當前存在半連接隊列溢出的現象**。

> 如何調整 SYN 半連接隊列大小？

要想增大半連接隊列，**不能只單純增大 tcp_max_syn_backlog 的值，還需一同增大 somaxconn 和 backlog，也就是增大 accept 隊列。否則，只單純增大 tcp_max_syn_backlog 是無效的。**

增大 tcp_max_syn_backlog 和 somaxconn 的方法是修改 Linux 內核參數：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/11.jpg)

增大 backlog 的方式，每個 Web 服務都不同，比如 Nginx 增大 backlog 的方法如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/12.jpg)

最後，改變瞭如上這些參數後，要重啟 Nginx 服務，因為 SYN 半連接隊列和 accept 隊列都是在 `listen()` 初始化的。

> 如果 SYN 半連接隊列已滿，只能丟棄連接嗎？

並不是這樣，**開啟 syncookies 功能就可以在不使用 SYN 半連接隊列的情況下成功建立連接**。

syncookies 的工作原理：服務器根據當前狀態計算出一個值，放在己方發出的 SYN+ACK 報文中發出，當客戶端返回 ACK 報文時，取出該值驗證，如果合法，就認為連接建立成功，如下圖所示。

![開啟 syncookies 功能](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/13.jpg)

syncookies 參數主要有以下三個值：

- 0 值，表示關閉該功能；
- 1 值，表示僅當 SYN 半連接隊列放不下時，再啟用它；
- 2 值，表示無條件開啟功能；

那麼在應對 SYN 攻擊時，只需要設置為 1 即可：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/14.jpg)

> SYN_RCV 狀態的優化

當客戶端接收到服務器發來的 SYN+ACK 報文後，就會回覆 ACK 給服務器，同時客戶端連接狀態從 SYN_SENT 轉換為 ESTABLISHED，表示連接建立成功。

服務器端連接成功建立的時間還要再往後，等到服務端收到客戶端的 ACK 後，服務端的連接狀態才變為 ESTABLISHED。

如果服務器沒有收到 ACK，就會重發 SYN+ACK 報文，同時一直處於 SYN_RCV 狀態。

當網絡繁忙、不穩定時，報文丟失就會變嚴重，此時應該調大重發次數。反之則可以調小重發次數。**修改重發次數的方法是，調整 tcp_synack_retries 參數**：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/15.jpg)

tcp_synack_retries 的默認重試次數是 5 次，與客戶端重傳 SYN 類似，它的重傳會經歷 1、2、4、8、16 秒，最後一次重傳後會繼續等待 32 秒，如果服務端仍然沒有收到 ACK，才會關閉連接，故共需要等待 63 秒。

服務器收到 ACK 後連接建立成功，此時，內核會把連接從半連接隊列移除，然後創建新的完全的連接，並將其添加到 accept 隊列，等待進程調用 accept 函數時把連接取出來。

如果進程不能及時地調用 accept 函數，就會造成 accept 隊列（也稱全連接隊列）溢出，最終導致建立好的 TCP 連接被丟棄。

![ accept 隊列溢出](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/16.jpg)

> accept 隊列已滿，只能丟棄連接嗎？

丟棄連接只是 Linux 的默認行為，我們還可以選擇向客戶端發送 RST 復位報文，告訴客戶端連接已經建立失敗。打開這一功能需要將 tcp_abort_on_overflow 參數設置為 1。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/17.jpg)

tcp_abort_on_overflow 共有兩個值分別是 0 和 1，其分別表示：

- 0 ：如果 accept 隊列滿了，那麼 server 扔掉 client  發過來的 ack ；
- 1 ：如果 accept 隊列滿了，server 發送一個 `RST` 包給 client，表示廢掉這個握手過程和這個連接；

如果要想知道客戶端連接不上服務端，是不是服務端 TCP 全連接隊列滿的原因，那麼可以把 tcp_abort_on_overflow 設置為 1，這時如果在客戶端異常中可以看到很多 `connection reset by peer` 的錯誤，那麼就可以證明是由於服務端 TCP 全連接隊列溢出的問題。

通常情況下，應當把 tcp_abort_on_overflow 設置為 0，因為這樣更有利於應對突發流量。

舉個例子，當 accept 隊列滿導致服務器丟掉了 ACK，與此同時，客戶端的連接狀態卻是 ESTABLISHED，客戶端進程就在建立好的連接上發送請求。只要服務器沒有為請求回覆 ACK，客戶端的請求就會被多次「重發」。**如果服務器上的進程只是短暫的繁忙造成 accept 隊列滿，那麼當 accept 隊列有空位時，再次接收到的請求報文由於含有 ACK，仍然會觸發服務器端成功建立連接。**

![tcp_abort_on_overflow 為 0 可以應對突發流量](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/18.jpg)


所以，tcp_abort_on_overflow 設為 0 可以提高連接建立的成功率，只有你非常肯定 TCP 全連接隊列會長期溢出時，才能設置為 1 以儘快通知客戶端。


> 如何調整 accept 隊列的長度呢？

accept 隊列的長度取決於 somaxconn 和 backlog 之間的最小值，也就是 min(somaxconn, backlog)，其中：

- somaxconn 是 Linux 內核的參數，默認值是 128，可以通過 `net.core.somaxconn` 來設置其值；
- backlog 是 `listen(int sockfd, int backlog)` 函數中的 backlog 大小；

Tomcat、Nginx、Apache 常見的 Web 服務的 backlog 默認值都是 511。

> 如何查看服務端進程 accept 隊列的長度？

可以通過 `ss -ltn` 命令查看：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/19.jpg)

- Recv-Q：當前 accept 隊列的大小，也就是當前已完成三次握手並等待服務端 `accept()` 的 TCP 連接；
- Send-Q：accept 隊列最大長度，上面的輸出結果說明監聽 8088 端口的 TCP 服務，accept 隊列的最大長度為 128；

> 如何查看由於 accept 連接隊列已滿，而被丟棄的連接？

當超過了 accept 連接隊列，服務端則會丟掉後續進來的 TCP 連接，丟掉的 TCP 連接的個數會被統計起來，我們可以使用 netstat -s 命令來查看：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/20.jpg)

上面看到的 41150 times ，表示 accept 隊列溢出的次數，注意這個是累計值。可以隔幾秒鐘執行下，如果這個數字一直在增加的話，說明 accept 連接隊列偶爾滿了。

如果持續不斷地有連接因為 accept 隊列溢出被丟棄，就應該調大 backlog 以及 somaxconn 參數。

### 如何繞過三次握手？

以上我們只是在對三次握手的過程進行優化，接下來我們看看如何繞過三次握手發送數據。

三次握手建立連接造成的後果就是，HTTP 請求必須在一個 RTT（從客戶端到服務器一個往返的時間）後才能發送。

![常規 HTTP 請求](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/21.jpg)

在 Linux 3.7 內核版本之後，提供了 TCP Fast Open 功能，這個功能可以減少 TCP 連接建立的時延。

> 接下來說說，TCP Fast Open 功能的工作方式。

![開啟 TCP Fast Open 功能](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/22.jpg)

在客戶端首次建立連接時的過程：

1. 客戶端發送 SYN 報文，該報文包含 Fast Open 選項，且該選項的 Cookie 為空，這表明客戶端請求 Fast Open Cookie；
2. 支持 TCP Fast Open 的服務器生成 Cookie，並將其置於 SYN-ACK 數據包中的 Fast Open 選項以發回客戶端；
3. 客戶端收到 SYN-ACK 後，本地緩存 Fast Open 選項中的 Cookie。

所以，第一次發起 HTTP GET 請求的時候，還是需要正常的三次握手流程。

之後，如果客戶端再次向服務器建立連接時的過程：

1. 客戶端發送 SYN 報文，該報文包含「數據」（對於非 TFO 的普通 TCP 握手過程，SYN 報文中不包含「數據」）以及此前記錄的 Cookie；
2. 支持 TCP Fast Open 的服務器會對收到 Cookie 進行校驗：如果 Cookie 有效，服務器將在 SYN-ACK 報文中對 SYN 和「數據」進行確認，服務器隨後將「數據」遞送至相應的應用程序；如果 Cookie 無效，服務器將丟棄 SYN 報文中包含的「數據」，且其隨後發出的 SYN-ACK 報文將只確認 SYN 的對應序列號；
3. 如果服務器接受了 SYN 報文中的「數據」，服務器可在握手完成之前發送「數據」，**這就減少了握手帶來的 1 個 RTT 的時間消耗**；
4. 客戶端將發送 ACK 確認服務器發回的 SYN 以及「數據」，但如果客戶端在初始的 SYN 報文中發送的「數據」沒有被確認，則客戶端將重新發送「數據」；
5. 此後的 TCP 連接的數據傳輸過程和非 TFO 的正常情況一致。

所以，之後發起 HTTP GET 請求的時候，可以繞過三次握手，這就減少了握手帶來的 1 個 RTT 的時間消耗。

開啟了 TFO 功能，cookie 的值是存放到 TCP option 字段裡的：

![TCP option 字段 - TFO](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8F%82%E6%95%B0/TCP%20option%E5%AD%97%E6%AE%B5%20-%20TFO.png)

注：客戶端在請求並存儲了 Fast Open Cookie 之後，可以不斷重複 TCP Fast Open 直至服務器認為 Cookie 無效（通常為過期）。

> Linux 下怎麼打開 TCP Fast Open 功能呢？

在 Linux 系統中，可以通過**設置 tcp_fastopn 內核參數，來打開 Fast Open 功能**：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/23.jpg)

tcp_fastopn 各個值的意義: 

- 0 關閉
- 1 作為客戶端使用 Fast Open 功能
- 2 作為服務端使用 Fast Open 功能
- 3 無論作為客戶端還是服務器，都可以使用 Fast Open 功能

**TCP Fast Open 功能需要客戶端和服務端同時支持，才有效果。**

### 小結

本小結主要介紹了關於優化 TCP 三次握手的幾個 TCP 參數。

![三次握手優化策略](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/24.jpg)

> 客戶端的優化

當客戶端發起 SYN 包時，可以通過 `tcp_syn_retries` 控制其重傳的次數。

> 服務端的優化

當服務端 SYN 半連接隊列溢出後，會導致後續連接被丟棄，可以通過 `netstat -s` 觀察半連接隊列溢出的情況，如果 SYN 半連接隊列溢出情況比較嚴重，可以通過 `tcp_max_syn_backlog、somaxconn、backlog` 參數來調整 SYN 半連接隊列的大小。

服務端回覆 SYN+ACK 的重傳次數由 `tcp_synack_retries` 參數控制。如果遭受 SYN 攻擊，應把 `tcp_syncookies` 參數設置為 1，表示僅在 SYN 隊列滿後開啟 syncookie 功能，可以保證正常的連接成功建立。

服務端收到客戶端返回的 ACK，會把連接移入 accpet 隊列，等待進行調用 accpet() 函數取出連接。

可以通過 `ss -lnt` 查看服務端進程的 accept 隊列長度，如果 accept 隊列溢出，系統默認丟棄 ACK，如果可以把 `tcp_abort_on_overflow` 設置為 1 ，表示用 RST 通知客戶端連接建立失敗。

如果 accpet 隊列溢出嚴重，可以通過 listen 函數的 `backlog` 參數和 `somaxconn` 系統參數提高隊列大小，accept 隊列長度取決於 min(backlog, somaxconn)。

> 繞過三次握手

TCP Fast Open 功能可以繞過三次握手，使得 HTTP 請求減少了 1 個 RTT 的時間，Linux 下可以通過 `tcp_fastopen` 開啟該功能，同時必須保證服務端和客戶端同時支持。

---

## TCP 四次揮手的性能提升

接下來，我們一起看看針對 TCP 四次揮手關閉連接時，如何優化性能。

在開始之前，我們得先了解四次揮手狀態變遷的過程。

客戶端和服務端雙方都可以主動斷開連接，**通常先關閉連接的一方稱為主動方，後關閉連接的一方稱為被動方。**

![客戶端主動關閉](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/25.jpg)

可以看到，**四次揮手過程只涉及了兩種報文，分別是 FIN 和 ACK**：

- FIN 就是結束連接的意思，誰發出 FIN 報文，就表示它將不會再發送任何數據，關閉這一方向上的傳輸通道；
- ACK 就是確認的意思，用來通知對方：你方的發送通道已經關閉；

四次揮手的過程:

- 當主動方關閉連接時，會發送 FIN 報文，此時發送方的 TCP 連接將從 ESTABLISHED 變成 FIN_WAIT1。
- 當被動方收到 FIN 報文後，內核會自動回覆 ACK 報文，連接狀態將從 ESTABLISHED 變成 CLOSE_WAIT，表示被動方在等待進程調用 close 函數關閉連接。
- 當主動方收到這個 ACK 後，連接狀態由 FIN_WAIT1 變為 FIN_WAIT2，也就是表示**主動方的發送通道就關閉了**。
- 當被動方進入 CLOSE_WAIT 時，被動方還會繼續處理數據，等到進程的 read 函數返回 0 後，應用程序就會調用 close 函數，進而觸發內核發送 FIN 報文，此時被動方的連接狀態變為 LAST_ACK。
- 當主動方收到這個 FIN 報文後，內核會回覆 ACK 報文給被動方，同時主動方的連接狀態由 FIN_WAIT2 變為 TIME_WAIT，**在 Linux 系統下大約等待 1 分鐘後，TIME_WAIT 狀態的連接才會徹底關閉**。
- 當被動方收到最後的 ACK 報文後，**被動方的連接就會關閉**。

你可以看到，每個方向都需要**一個 FIN 和一個 ACK**，因此通常被稱為**四次揮手**。

這裡一點需要注意是：**主動關閉連接的，才有 TIME_WAIT 狀態。**

主動關閉方和被動關閉方優化的思路也不同，接下來分別說說如何優化他們。

### 主動方的優化

關閉連接的方式通常有兩種，分別是 RST 報文關閉和 FIN 報文關閉。

如果進程收到 RST 報文，就直接關閉連接了，不需要走四次揮手流程，是一個暴力關閉連接的方式。

安全關閉連接的方式必須通過四次揮手，它由進程調用 `close` 和 `shutdown` 函數發起 FIN 報文（shutdown 參數須傳入 SHUT_WR 或者 SHUT_RDWR 才會發送 FIN）。

> 調用 close 函數和 shutdown 函數有什麼區別？

調用了 close 函數意味著完全斷開連接，**完全斷開不僅指無法傳輸數據，而且也不能發送數據。 此時，調用了 close 函數的一方的連接叫做「孤兒連接」，如果你用 netstat -p 命令，會發現連接對應的進程名為空。**

使用 close 函數關閉連接是不優雅的。於是，就出現了一種優雅關閉連接的 `shutdown` 函數，**它可以控制只關閉一個方向的連接**：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/26.jpg)

第二個參數決定斷開連接的方式，主要有以下三種方式：

- SHUT_RD(0)：**關閉連接的「讀」這個方向**，如果接收緩衝區有已接收的數據，則將會被丟棄，並且後續再收到新的數據，會對數據進行 ACK，然後悄悄地丟棄。也就是說，對端還是會接收到 ACK，在這種情況下根本不知道數據已經被丟棄了。
- SHUT_WR(1)：**關閉連接的「寫」這個方向**，這就是常被稱為「半關閉」的連接。如果發送緩衝區還有未發送的數據，將被立即發送出去，併發送一個 FIN 報文給對端。
- SHUT_RDWR(2)：相當於 SHUT_RD 和 SHUT_WR 操作各一次，**關閉套接字的讀和寫兩個方向**。

close 和 shutdown 函數都可以關閉連接，但這兩種方式關閉的連接，不只功能上有差異，控制它們的 Linux 參數也不相同。

> FIN_WAIT1 狀態的優化

主動方發送 FIN 報文後，連接就處於 FIN_WAIT1 狀態，正常情況下，如果能及時收到被動方的 ACK，則會很快變為 FIN_WAIT2 狀態。

但是當遲遲收不到對方返回的 ACK 時，連接就會一直處於 FIN_WAIT1 狀態。此時，**內核會定時重發 FIN 報文，其中重發次數由 tcp_orphan_retries 參數控制**（注意，orphan 雖然是孤兒的意思，該參數卻不只對孤兒連接有效，事實上，它對所有 FIN_WAIT1 狀態下的連接都有效），默認值是 0。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/27.jpg)

你可能會好奇，這 0 表示幾次？**實際上當為 0 時，特指 8 次**，從下面的內核源碼可知：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/28.jpg)

如果 FIN_WAIT1 狀態連接很多，我們就需要考慮降低 tcp_orphan_retries 的值，當重傳次數超過 tcp_orphan_retries 時，連接就會直接關閉掉。

對於普遍正常情況時，調低 tcp_orphan_retries 就已經可以了。如果遇到惡意攻擊，FIN 報文根本無法發送出去，這由 TCP 兩個特性導致的：

- 首先，TCP 必須保證報文是有序發送的，FIN 報文也不例外，當發送緩衝區還有數據沒有發送時，FIN 報文也不能提前發送。
- 其次，TCP 有流量控制功能，當接收方接收窗口為 0 時，發送方就不能再發送數據。所以，當攻擊者下載大文件時，就可以通過接收窗口設為 0 ，這就會使得 FIN 報文都無法發送出去，那麼連接會一直處於 FIN_WAIT1 狀態。

解決這種問題的方法，是**調整 tcp_max_orphans 參數，它定義了「孤兒連接」的最大數量**：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/29.jpg)

當進程調用了 `close` 函數關閉連接，此時連接就會是「孤兒連接」，因為它無法再發送和接收數據。Linux 系統為了防止孤兒連接過多，導致系統資源長時間被佔用，就提供了 `tcp_max_orphans` 參數。如果孤兒連接數量大於它，新增的孤兒連接將不再走四次揮手，而是直接發送 RST 復位報文強制關閉。

> FIN_WAIT2 狀態的優化

當主動方收到 ACK 報文後，會處於 FIN_WAIT2 狀態，就表示主動方的發送通道已經關閉，接下來將等待對方發送 FIN 報文，關閉對方的發送通道。

這時，**如果連接是用 shutdown 函數關閉的，連接可以一直處於 FIN_WAIT2 狀態，因為它可能還可以發送或接收數據。但對於 close 函數關閉的孤兒連接，由於無法再發送和接收數據，所以這個狀態不可以持續太久，而 tcp_fin_timeout 控制了這個狀態下連接的持續時長**，默認值是 60 秒：


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/30.jpg)

它意味著對於孤兒連接（調用 close 關閉的連接），如果在 60 秒後還沒有收到 FIN 報文，連接就會直接關閉。

這個 60 秒不是隨便決定的，它與 TIME_WAIT 狀態持續的時間是相同的，後面我們再來說說為什麼是 60 秒。

> TIME_WAIT 狀態的優化

TIME_WAIT 是主動方四次揮手的最後一個狀態，也是最常遇見的狀態。

當收到被動方發來的 FIN 報文後，主動方會立刻回覆 ACK，表示確認對方的發送通道已經關閉，接著就處於 TIME_WAIT 狀態。在 Linux 系統，TIME_WAIT 狀態會持續 60 秒後才會進入關閉狀態。

TIME_WAIT 狀態的連接，在主動方看來確實快已經關閉了。然後，被動方沒有收到 ACK 報文前，還是處於 LAST_ACK 狀態。如果這個 ACK 報文沒有到達被動方，被動方就會重發 FIN 報文。重發次數仍然由前面介紹過的 tcp_orphan_retries 參數控制。

TIME-WAIT 的狀態尤其重要，主要是兩個原因：

- 防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收；
- 保證「被動關閉連接」的一方，能被正確的關閉；

*原因一：防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收*

TIME-WAIT 的一個作用是**防止收到歷史數據，從而導致數據錯亂的問題。**

假設 TIME-WAIT 沒有等待時間或時間過短，被延遲的數據包抵達後會發生什麼呢？

![TIME-WAIT 時間過短，收到舊連接的數據報文](https://img-blog.csdnimg.cn/img_convert/6385cc99500b01ba2ef288c27523c1e7.png)


- 如上圖：

  - 服務端在關閉連接之前發送的 `SEQ = 301` 報文，被網絡延遲了。
  - 接著，服務端以相同的四元組重新打開了新連接，前面被延遲的 `SEQ = 301` 這時抵達了客戶端，而且該數據報文的序列號剛好在客戶端接收窗口內，因此客戶端會正常接收這個數據報文，但是這個數據報文是上一個連接殘留下來的，這樣就產生數據錯亂等嚴重的問題。

為了防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收，因此 TCP 設計了 TIME_WAIT 狀態，狀態會持續 `2MSL` 時長，這個時間**足以讓兩個方向上的數據包都被丟棄，使得原來連接的數據包在網絡中都自然消失，再出現的數據包一定都是新建立連接所產生的。**

*原因二：保證「被動關閉連接」的一方，能被正確的關閉*

在 RFC 793 指出 TIME-WAIT 另一個重要的作用是：

*TIME-WAIT - represents waiting for enough time to pass to be sure the remote TCP received the acknowledgment of its connection termination request.*

也就是說，TIME-WAIT 作用是**等待足夠的時間以確保最後的 ACK 能讓被動關閉方接收，從而幫助其正常關閉。**

如果客戶端（主動關閉方）最後一次 ACK 報文（第四次揮手）在網絡中丟失了，那麼按照 TCP 可靠性原則，服務端（被動關閉方）會重發 FIN 報文。

假設客戶端沒有 TIME_WAIT 狀態，而是在發完最後一次回 ACK 報文就直接進入 CLOSED 狀態，如果該  ACK 報文丟失了，服務端則重傳的 FIN 報文，而這時客戶端已經進入到關閉狀態了，在收到服務端重傳的 FIN 報文後，就會回 RST 報文。

![TIME-WAIT 時間過短，沒有確保連接正常關閉](https://img-blog.csdnimg.cn/img_convert/3a81c23ce57c27cf63fc2b77e34de0ab.png)

服務端收到這個 RST 並將其解釋為一個錯誤（Connection reset by peer），這對於一個可靠的協議來說不是一個優雅的終止方式。

為了防止這種情況出現，客戶端必須等待足夠長的時間，確保服務端能夠收到 ACK，如果服務端沒有收到 ACK，那麼就會觸發 TCP 重傳機制，服務端會重新發送一個 FIN，這樣一去一來剛好兩個 MSL 的時間。

![TIME-WAIT 時間正常，確保了連接正常關閉](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4/網絡/TIME-WAIT連接正常關閉.drawio.png)

客戶端在收到服務端重傳的 FIN 報文時，TIME_WAIT 狀態的等待時間，會重置回 2MSL。

我們再回過頭來看看，為什麼 TIME_WAIT 狀態要保持 60 秒呢？

這與孤兒連接 FIN_WAIT2 狀態默認保留 60 秒的原理是一樣的，**因為這兩個狀態都需要保持 2MSL 時長。MSL 全稱是 Maximum Segment Lifetime，它定義了一個報文在網絡中的最長生存時間**（報文每經過一次路由器的轉發，IP 頭部的 TTL 字段就會減 1，減到 0 時報文就被丟棄，這就限制了報文的最長存活時間）。

為什麼是 2 MSL 的時長呢？這其實是相當於**至少允許報文丟失一次**。比如，若 ACK 在一個 MSL 內丟失，這樣被動方重發的 FIN 會在第 2 個 MSL 內到達，TIME_WAIT 狀態的連接可以應對。

為什麼不是 4 或者 8 MSL 的時長呢？你可以想象一個丟包率達到百分之一的糟糕網絡，連續兩次丟包的概率只有萬分之一，這個概率實在是太小了，忽略它比解決它更具性價比。

**因此，TIME_WAIT 和 FIN_WAIT2 狀態的最大時長都是 2 MSL，由於在 Linux 系統中，MSL 的值固定為 30 秒，所以它們都是 60 秒。**

> TIME_WAIT 狀態優化方式一

**Linux 提供了 tcp_max_tw_buckets 參數，當 TIME_WAIT 的連接數量超過該參數時，新關閉的連接就不再經歷 TIME_WAIT 而直接關閉：**

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/33.jpg)

當服務器的併發連接增多時，相應地，同時處於 TIME_WAIT 狀態的連接數量也會變多，此時就應當調大 `tcp_max_tw_buckets` 參數，減少不同連接間數據錯亂的概率。tcp_max_tw_buckets 也不是越大越好，畢竟系統資源是有限的。

> TIME_WAIT 狀態優化方式二

**有一種方式可以在建立新連接時，複用處於 TIME_WAIT 狀態的連接，那就是打開 tcp_tw_reuse 參數。但是需要注意，該參數是隻用於客戶端（建立連接的發起方），因為是在調用 connect() 時起作用的，而對於服務端（被動連接方）是沒有用的。**

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/34.jpg)

網上很多博客都說在服務端開啟 tcp_tw_reuse 參數來優化 TCP，我信你個鬼，糟老頭壞的很！**tcp_tw_reuse 只作用在 connect 函數，也就是客戶端，跟服務端一毛關係的沒有**。

tcp_tw_reuse 從協議角度理解是安全可控的，可以複用處於 TIME_WAIT 的端口為新的連接所用。

什麼是協議角度理解的安全可控呢？主要有兩點：

- 只適用於連接發起方，也就是 C/S 模型中的客戶端；
- 對應的 TIME_WAIT 狀態的連接創建時間超過 1 秒才可以被複用。

使用這個選項，還有一個前提，需要打開對 TCP 時間戳的支持（對方也要打開 ）：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/35.jpg)

由於引入了時間戳，它能帶來了些好處：

- 我們在前面提到的 2MSL（TIME_WAIT狀態的持續時間） 問題就不復存在了，因為重複的數據包會因為時間戳過期被自然丟棄；
- 同時，它還可以防止序列號繞回，也是因為重複的數據包會由於時間戳過期被自然丟棄；

時間戳是在 TCP 的選項字段裡定義的，開啟了時間戳功能，在 TCP 報文傳輸的時候會帶上發送報文的時間戳。

![TCP option 字段 - 時間戳](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8F%82%E6%95%B0/TCP%20option%E5%AD%97%E6%AE%B5-%E6%97%B6%E9%97%B4%E6%88%B3.png)

另外，老版本的 Linux 還提供了 `tcp_tw_recycle` 參數，但是當開啟了它，允許處於 TIME_WAIT 狀態的連接被快速回收，但是有個**大坑**。

開啟了 recycle 和 timestamps 選項，就會開啟一種叫 per-host 的 PAWS（判斷TCP 報文中時間戳是否是歷史報文） 機制，**per-host 是對「對端 IP 做 PAWS 檢查」**，而非對「IP + 端口」四元組做 PAWS 檢查。

如果客戶端網絡環境是用了 NAT 網關，那麼客戶端環境的每一臺機器通過 NAT 網關後，都會是相同的 IP 地址，在服務端看來，就好像只是在跟一個客戶端打交道一樣，無法區分出來。

Per-host PAWS 機制利用 TCP option 裡的 timestamp 字段的增長來判斷串擾數據，而 timestamp 是根據客戶端各自的 CPU tick 得出的值。

當客戶端 A 通過 NAT 網關和服務器建立 TCP 連接，然後服務器主動關閉並且快速回收 TIME-WAIT 狀態的連接後，**客戶端 B 也通過 NAT 網關和服務器建立 TCP 連接，注意客戶端 A 和 客戶端 B 因為經過相同的 NAT 網關，所以是用相同的 IP 地址與服務端建立 TCP 連接，如果客戶端 B 的 timestamp 比 客戶端 A 的 timestamp 小，那麼由於服務端的 per-host 的 PAWS 機制的作用，服務端就會丟棄客戶端主機 B 發來的 SYN 包**。

因此，tcp_tw_recycle 在使用了 NAT 的網絡下是存在問題的，如果它是對 TCP 四元組做 PAWS 檢查，而不是對「相同的 IP 做 PAWS 檢查」，那麼就不會存在這個問題了。

網上很多博客都說開啟 tcp_tw_recycle 參數來優化 TCP，我信你個鬼，糟老頭壞的很！

所以，不建議設置為 1 ，在 Linux 4.12 版本後，Linux 內核直接取消了這一參數，建議關閉它：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/36.jpg)

> TIME_WAIT 狀態優化方式三

我們可以在程序中設置 socket 選項，來設置調用 close 關閉連接行為。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/37.jpg)

如果 `l_onoff` 為非 0， 且 `l_linger` 值為 0，**那麼調用 close 後，會立該發送一個 RST 標誌給對端，該 TCP 連接將跳過四次揮手，也就跳過了 TIME_WAIT 狀態，直接關閉。**

這種方式只推薦在客戶端使用，服務端千萬不要使用。因為服務端一調用 close，就發送 RST 報文的話，客戶端就總是看到 TCP 連接錯誤 “connnection reset by peer”。

### 被動方的優化

當被動方收到 FIN 報文時，內核會自動回覆 ACK，同時連接處於 CLOSE_WAIT 狀態，顧名思義，它表示等待應用進程調用 close 函數關閉連接。

內核沒有權利替代進程去關閉連接，因為如果主動方是通過 shutdown 關閉連接，那麼它就是想在半關閉連接上接收數據或發送數據。因此，Linux 並沒有限制 CLOSE_WAIT 狀態的持續時間。

當然，大多數應用程序並不使用 shutdown 函數關閉連接。所以，**當你用 netstat 命令發現大量 CLOSE_WAIT 狀態。就需要排查你的應用程序，因為可能因為應用程序出現了 Bug，read 函數返回 0 時，沒有調用 close 函數。**

處於 CLOSE_WAIT 狀態時，調用了 close 函數，內核就會發出 FIN 報文關閉發送通道，同時連接進入 LAST_ACK 狀態，等待主動方返回 ACK 來確認連接關閉。

如果遲遲收不到這個 ACK，內核就會重發 FIN 報文，重發次數仍然由 tcp_orphan_retries 參數控制，這與主動方重發 FIN 報文的優化策略一致。

還有一點我們需要注意的，**如果被動方迅速調用 close 函數，那麼被動方的 ACK 和 FIN 有可能在一個報文中發送，這樣看起來，四次揮手會變成三次揮手，這只是一種特殊情況，不用在意。**

> 如果連接雙方同時關閉連接，會怎麼樣？

由於 TCP 是雙全工的協議，所以是會出現兩方同時關閉連接的現象，也就是同時發送了 FIN 報文。

此時，上面介紹的優化策略仍然適用。兩方發送 FIN 報文時，都認為自己是主動方，所以都進入了 FIN_WAIT1 狀態，FIN 報文的重發次數仍由 tcp_orphan_retries 參數控制。

![同時關閉](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/38.jpg)

接下來，**雙方在等待 ACK 報文的過程中，都等來了 FIN 報文。這是一種新情況，所以連接會進入一種叫做 CLOSING 的新狀態，它替代了 FIN_WAIT2 狀態**。接著，雙方內核回覆 ACK 確認對方發送通道的關閉後，進入 TIME_WAIT 狀態，等待 2MSL 的時間後，連接自動關閉。

### 小結

針對 TCP 四次揮手的優化，我們需要根據主動方和被動方四次揮手狀態變化來調整系統 TCP 內核參數。

![四次揮手的優化策略](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/39.jpg)

> 主動方的優化

主動發起 FIN 報文斷開連接的一方，如果遲遲沒收到對方的 ACK 回覆，則會重傳 FIN 報文，重傳的次數由 `tcp_orphan_retries` 參數決定。

當主動方收到 ACK 報文後，連接就進入 FIN_WAIT2 狀態，根據關閉的方式不同，優化的方式也不同：

- 如果這是 close 函數關閉的連接，那麼它就是孤兒連接。如果 `tcp_fin_timeout` 秒內沒有收到對方的 FIN 報文，連接就直接關閉。同時，為了應對孤兒連接佔用太多的資源，`tcp_max_orphans` 定義了最大孤兒連接的數量，超過時連接就會直接釋放。
- 反之是 shutdown 函數關閉的連接，則不受此參數限制；

當主動方接收到 FIN 報文，並返回 ACK 後，主動方的連接進入 TIME_WAIT 狀態。這一狀態會持續 1 分鐘，為了防止 TIME_WAIT 狀態佔用太多的資源，`tcp_max_tw_buckets` 定義了最大數量，超過時連接也會直接釋放。

當 TIME_WAIT 狀態過多時，還可以通過設置 `tcp_tw_reuse` 和 `tcp_timestamps` 為 1 ，將 TIME_WAIT 狀態的端口複用於作為客戶端的新連接，注意該參數只適用於客戶端。

> 被動方的優化

被動關閉的連接方應對非常簡單，它在回覆 ACK 後就進入了 CLOSE_WAIT 狀態，等待進程調用 close 函數關閉連接。因此，出現大量 CLOSE_WAIT 狀態的連接時，應當從應用程序中找問題。

當被動方發送 FIN 報文後，連接就進入 LAST_ACK 狀態，在未等到 ACK 時，會在 `tcp_orphan_retries` 參數的控制下重發 FIN 報文。

---

## TCP 傳輸數據的性能提升

在前面介紹的是三次握手和四次揮手的優化策略，接下來主要介紹的是 TCP 傳輸數據時的優化策略。

TCP 連接是由內核維護的，內核會為每個連接建立內存緩衝區：

- 如果連接的內存配置過小，就無法充分使用網絡帶寬，TCP 傳輸效率就會降低；
- 如果連接的內存配置過大，很容易把服務器資源耗盡，這樣就會導致新連接無法建立；

因此，我們必須理解 Linux 下 TCP 內存的用途，才能正確地配置內存大小。

### 滑動窗口是如何影響傳輸速度的？

TCP 會保證每一個報文都能夠抵達對方，它的機制是這樣：報文發出去後，必須接收到對方返回的確認報文 ACK，如果遲遲未收到，就會超時重發該報文，直到收到對方的 ACK 為止。

**所以，TCP 報文發出去後，並不會立馬從內存中刪除，因為重傳時還需要用到它。**

由於 TCP 是內核維護的，所以報文存放在內核緩衝區。如果連接非常多，我們可以通過 free 命令觀察到 `buff/cache` 內存是會增大。


如果 TCP 是每發送一個數據，都要進行一次確認應答。當上一個數據包收到了應答了， 再發送下一個。這個模式就有點像我和你面對面聊天，你一句我一句，但這種方式的缺點是效率比較低的。

![按數據包進行確認應答](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/40.jpg)

所以，這樣的傳輸方式有一個缺點：數據包的**往返時間越長，通信的效率就越低**。

**要解決這一問題不難，並行批量發送報文，再批量確認報文即可。**

![並行處理](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/41.jpg)

然而，這引出了另一個問題，發送方可以隨心所欲的發送報文嗎？**當然這不現實，我們還得考慮接收方的處理能力。**

當接收方硬件不如發送方，或者系統繁忙、資源緊張時，是無法瞬間處理這麼多報文的。於是，這些報文只能被丟掉，使得網絡效率非常低。

**為瞭解決這種現象發生，TCP 提供一種機制可以讓「發送方」根據「接收方」的實際接收能力控制發送的數據量，這就是滑動窗口的由來。**

接收方根據它的緩衝區，可以計算出後續能夠接收多少字節的報文，這個數字叫做接收窗口。當內核接收到報文時，必須用緩衝區存放它們，這樣剩餘緩衝區空間變小，接收窗口也就變小了；當進程調用 read 函數後，數據被讀入了用戶空間，內核緩衝區就被清空，這意味著主機可以接收更多的報文，接收窗口就會變大。

因此，接收窗口並不是恆定不變的，接收方會把當前可接收的大小放在 TCP 報文頭部中的**窗口字段**，這樣就可以起到窗口大小通知的作用。

發送方的窗口等價於接收方的窗口嗎？如果不考慮擁塞控制，發送方的窗口大小「約等於」接收方的窗口大小，因為窗口通知報文在網絡傳輸是存在時延的，所以是約等於的關係。

![TCP 頭部](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/42.jpg)

從上圖中可以看到，窗口字段只有 2 個字節，因此它最多能表達 65535 字節大小的窗口，也就是 64KB 大小。

這個窗口大小最大值，在當今高速網絡下，很明顯是不夠用的。所以後續有了擴充窗口的方法：**在 TCP 選項字段定義了窗口擴大因子，用於擴大 TCP 通告窗口，其值大小是 2^14，這樣就使 TCP 的窗口大小從 16 位擴大為 30 位（2^16 * 2^ 14 = 2^30），所以此時窗口的最大值可以達到 1GB。**

![TCP option 選項 - 窗口擴展](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8F%82%E6%95%B0/TCP%20option%E5%AD%97%E6%AE%B5-%E7%AA%97%E5%8F%A3.png)

Linux 中打開這一功能，需要把 tcp_window_scaling 配置設為 1（默認打開）：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/43.jpg)

要使用窗口擴大選項，通訊雙方必須在各自的 SYN 報文中發送這個選項：

- 主動建立連接的一方在 SYN 報文中發送這個選項；
- 而被動建立連接的一方只有在收到帶窗口擴大選項的 SYN 報文之後才能發送這個選項。


這樣看來，只要進程能及時地調用 read 函數讀取數據，並且接收緩衝區配置得足夠大，那麼接收窗口就可以無限地放大，發送方也就無限地提升發送速度。

**這是不可能的，因為網絡的傳輸能力是有限的，當發送方依據發送窗口，發送超過網絡處理能力的報文時，路由器會直接丟棄這些報文。因此，緩衝區的內存並不是越大越好。**


### 如何確定最大傳輸速度？

在前面我們知道了 TCP 的傳輸速度，受制於發送窗口與接收窗口，以及網絡設備傳輸能力。其中，窗口大小由內核緩衝區大小決定。如果緩衝區與網絡傳輸能力匹配，那麼緩衝區的利用率就達到了最大化。

問題來了，如何計算網絡的傳輸能力呢？

相信大家都知道網絡是有「帶寬」限制的，帶寬描述的是網絡傳輸能力，它與內核緩衝區的計量單位不同:

- 帶寬是單位時間內的流量，表達是「速度」，比如常見的帶寬 100 MB/s；
- 緩衝區單位是字節，當網絡速度乘以時間才能得到字節數；

這裡需要說一個概念，就是帶寬時延積，它決定網絡中飛行報文的大小，它的計算方式：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/44.jpg)

比如最大帶寬是 100 MB/s，網絡時延（RTT）是 10ms 時，意味著客戶端到服務端的網絡一共可以存放 100MB/s * 0.01s = 1MB 的字節。

這個 1MB 是帶寬和時延的乘積，所以它就叫「帶寬時延積」（縮寫為 BDP，Bandwidth Delay Product）。同時，這 1MB 也表示「飛行中」的 TCP 報文大小，它們就在網絡線路、路由器等網絡設備上。如果飛行報文超過了 1 MB，就會導致網絡過載，容易丟包。

**由於發送緩衝區大小決定了發送窗口的上限，而發送窗口又決定了「已發送未確認」的飛行報文的上限。因此，發送緩衝區不能超過「帶寬時延積」。**

發送緩衝區與帶寬時延積的關係：

- 如果發送緩衝區「超過」帶寬時延積，超出的部分就沒辦法有效的網絡傳輸，同時導致網絡過載，容易丟包；
- 如果發送緩衝區「小於」帶寬時延積，就不能很好的發揮出網絡的傳輸效率。

所以，發送緩衝區的大小最好是往帶寬時延積靠近。


### 怎樣調整緩衝區大小？

在 Linux 中發送緩衝區和接收緩衝都是可以用參數調節的。設置完後，Linux 會根據你設置的緩衝區進行**動態調節**。

> 調節發送緩衝區範圍

先來看看發送緩衝區，它的範圍通過 tcp_wmem 參數配置；

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/45.jpg)

上面三個數字單位都是字節，它們分別表示：

- 第一個數值是動態範圍的最小值，4096 byte = 4K；
- 第二個數值是初始默認值，16384 byte ≈ 16K；
- 第三個數值是動態範圍的最大值，4194304 byte = 4096K（4M）；

**發送緩衝區是自行調節的**，當發送方發送的數據被確認後，並且沒有新的數據要發送，就會把發送緩衝區的內存釋放掉。

> 調節接收緩衝區範圍

而接收緩衝區的調整就比較複雜一些，先來看看設置接收緩衝區範圍的 tcp_rmem 參數：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/46.jpg)

上面三個數字單位都是字節，它們分別表示：

- 第一個數值是動態範圍的最小值，表示即使在內存壓力下也可以保證的最小接收緩衝區大小，4096 byte = 4K；
- 第二個數值是初始默認值，87380 byte ≈ 86K；
- 第三個數值是動態範圍的最大值，6291456 byte = 6144K（6M）；

**接收緩衝區可以根據系統空閒內存的大小來調節接收窗口：**

- 如果系統的空閒內存很多，就可以自動把緩衝區增大一些，這樣傳給對方的接收窗口也會變大，因而提升發送方發送的傳輸數據數量；
- 反之，如果系統的內存很緊張，就會減少緩衝區，這雖然會降低傳輸效率，可以保證更多的併發連接正常工作；

發送緩衝區的調節功能是自動開啟的，**而接收緩衝區則需要配置 tcp_moderate_rcvbuf 為 1 來開啟調節功能**：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/47.jpg)

> 調節 TCP 內存範圍

接收緩衝區調節時，怎麼知道當前內存是否緊張或充分呢？這是通過 tcp_mem 配置完成的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/48.jpg)

上面三個數字單位不是字節，而是「頁面大小」，1 頁表示 4KB，它們分別表示：

- 當 TCP 內存小於第 1 個值時，不需要進行自動調節；
- 在第 1 和第 2 個值之間時，內核開始調節接收緩衝區的大小；
- 大於第 3 個值時，內核不再為 TCP 分配新內存，此時新連接是無法建立的；

一般情況下這些值是在系統啟動時根據系統內存數量計算得到的。根據當前 tcp_mem 最大內存頁面數是 177120，當內存為 (177120 * 4) / 1024K ≈ 692M 時，系統將無法為新的 TCP 連接分配內存，即 TCP 連接將被拒絕。

> 根據實際場景調節的策略

在高併發服務器中，為了兼顧網速與大量的併發連接，**我們應當保證緩衝區的動態調整的最大值達到帶寬時延積，而最小值保持默認的 4K 不變即可。而對於內存緊張的服務而言，調低默認值是提高併發的有效手段。**

同時，如果這是網絡 IO 型服務器，那麼，**調大 tcp_mem 的上限可以讓 TCP 連接使用更多的系統內存，這有利於提升併發能力**。需要注意的是，tcp_wmem 和 tcp_rmem 的單位是字節，而 tcp_mem 的單位是頁面大小。而且，**千萬不要在 socket 上直接設置 SO_SNDBUF 或者 SO_RCVBUF，這樣會關閉緩衝區的動態調整功能。**

### 小結

本節針對 TCP 優化數據傳輸的方式，做了一些介紹。

![數據傳輸的優化策略](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-參數/49.jpg)

TCP 可靠性是通過 ACK 確認報文實現的，又依賴滑動窗口提升了發送速度也兼顧了接收方的處理能力。

可是，默認的滑動窗口最大值只有 64 KB，不滿足當今的高速網絡的要求，要想提升發送速度必須提升滑動窗口的上限，在 Linux 下是通過設置 `tcp_window_scaling` 為 1 做到的，此時最大值可高達 1GB。

滑動窗口定義了網絡中飛行報文的最大字節數，當它超過帶寬時延積時，網絡過載，就會發生丟包。而當它小於帶寬時延積時，就無法充分利用網絡帶寬。因此，滑動窗口的設置，必須參考帶寬時延積。

內核緩衝區決定了滑動窗口的上限，緩衝區可分為：發送緩衝區 tcp_wmem 和接收緩衝區 tcp_rmem。

Linux 會對緩衝區動態調節，我們應該把緩衝區的上限設置為帶寬時延積。發送緩衝區的調節功能是自動打開的，而接收緩衝區需要把 tcp_moderate_rcvbuf 設置為 1 來開啟。其中，調節的依據是 TCP 內存範圍 tcp_mem。

但需要注意的是，如果程序中的 socket 設置 SO_SNDBUF 和 SO_RCVBUF，則會關閉緩衝區的動態整功能，所以不建議在程序設置它倆，而是交給內核自動調整比較好。

有效配置這些參數後，既能夠最大程度地保持併發性，也能讓資源充裕時連接傳輸速度達到最大值。

---

參考資料：


[1] 系統性能調優必知必會.陶輝.極客時間.

[2] 網絡編程實戰專欄.盛延敏.極客時間.

[3] http://www.blogjava.net/yongboy/archive/2013/04/11/397677.html

[4] http://blog.itpub.net/31559359/viewspace-2284113/

[5] https://blog.51cto.com/professor/1909022

[6] https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux

---

## 讀者問答

> 讀者問：“小林，請教個問題，somaxconn和backlog是不是都是指的是accept隊列？然後somaxconn是內核參數，backlog是通過系統調用間隔地修改somaxconn，比如Linux中listen()函數？”

兩者取最小值才是 accpet 隊列。

> 讀者問：“小林，還有個問題要請教下，“如果 accept 隊列滿了，那麼 server 扔掉 client  發過來的 ack”，也就是說該TCP連接還是位於半連接隊列中，沒有丟棄嗎？”

1. 當 accept 隊列滿了，後續新進來的syn包都會被丟失
2. 我文章的突發流量例子是，那個連接進來的時候 accept 隊列還沒滿，但是在第三次握手的時候，accept 隊列突然滿了，就會導致 ack 被丟棄，就一直處於半連接隊列。

----

**小林是專為大家圖解的工具人，Goodbye，我們下次見！**

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)


