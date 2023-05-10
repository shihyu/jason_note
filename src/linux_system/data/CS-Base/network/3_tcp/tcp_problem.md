# 4.16 TCP 協議有什麼缺陷？

大家好，我是小林。

寫的多了後，忽然思考一個問題，TCP 通過序列號、確認應答、超時重傳、流量控制、擁塞控制等方式實現了可靠傳輸，看起來它很完美，事實真的是這樣嗎？TCP 就沒什麼缺陷嗎？

所以，今天就跟大家聊聊，TCP 協議有哪些缺陷？主要有四個方面：

- 升級 TCP 的工作很困難；
- TCP 建立連接的延遲；
- TCP 存在隊頭阻塞問題；
- 網絡遷移需要重新建立 TCP 連接；

接下來，針對這四個方面詳細說一下。

## 升級 TCP 的工作很困難

TCP 協議是誕生在 1973 年，至今 TCP 協議依然還在實現更多的新特性。

但是 TCP 協議是在內核中實現的，應用程序只能使用不能修改，如果要想升級 TCP 協議，那麼只能升級內核。

而升級內核這個工作是很麻煩的事情，麻煩的事情不是說升級內核這個操作很麻煩，而是由於內核升級涉及到底層軟件和運行庫的更新，我們的服務程序就需要回歸測試是否兼容新的內核版本，所以服務器的內核升級也比較保守和緩慢。

很多 TCP 協議的新特性，都是需要客戶端和服務端同時支持才能生效的，比如  TCP Fast Open 這個特性，雖然在2013 年就被提出了，但是 Windows 很多系統版本依然不支持它，這是因為 PC 端的系統升級滯後很嚴重，W	indows Xp 現在還有大量用戶在使用，儘管它已經存在快 20 年。

所以，即使 TCP 有比較好的特性更新，也很難快速推廣，用戶往往要幾年或者十年才能體驗到。

## TCP 建立連接的延遲

基於 TCP 實現的應用協議，都是需要先建立三次握手才能進行數據傳輸，比如 HTTP 1.0/1.1、HTTP/2、HTTPS。

現在大多數網站都是使用 HTTPS 的，這意味著在 TCP 三次握手之後，還需要經過 TLS 四次握手後，才能進行 HTTP 數據的傳輸，這在一定程序上增加了數據傳輸的延遲。

TCP 三次握手和 TLS 握手延遲，如圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/%E7%BD%91%E7%BB%9C/http3/TCP%2BTLS.gif)

TCP 三次握手的延遲被 TCP Fast Open （快速打開）這個特性解決了，這個特性可以在「第二次建立連接」時減少 TCP 連接建立的時延。

![常規 HTTP 請求 與 Fast  Open HTTP 請求](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-Wireshark/45.jpg)

過程如下：

- 在第一次建立連接的時候，服務端在第二次握手產生一個 `Cookie` （已加密）並通過 SYN、ACK 包一起發給客戶端，於是客戶端就會緩存這個 `Cookie`，所以第一次發起 HTTP Get 請求的時候，還是需要 2 個 RTT 的時延；
- 在下次請求的時候，客戶端在 SYN 包帶上 `Cookie` 發給服務端，就提前可以跳過三次握手的過程，因為 `Cookie` 中維護了一些信息，服務端可以從 `Cookie` 獲取 TCP 相關的信息，這時發起的 HTTP GET 請求就只需要 1 個 RTT 的時延；

TCP Fast Open 這個特性是不錯，但是它需要服務端和客戶端的操作系統同時支持才能體驗到，而 TCP Fast Open 是在 2013 年提出的，所以市面上依然有很多老式的操作系統不支持，而升級操作系統是很麻煩的事情，因此  TCP Fast Open 很難被普及開來。

還有一點，針對 HTTPS 來說，TLS 是在應用層實現的握手，而 TCP 是在內核實現的握手，這兩個握手過程是無法結合在一起的，總是得先完成 TCP 握手，才能進行 TLS 握手。

也正是 TCP 是在內核實現的，所以 TLS 是無法對 TCP 頭部加密的，這意味著 TCP 的序列號都是明文傳輸，所以就存安全的問題。

一個典型的例子就是攻擊者偽造一個的 RST 報文強制關閉一條 TCP 連接，而攻擊成功的關鍵則是 TCP 字段裡的序列號位於接收方的滑動窗口內，該報文就是合法的。

為此 TCP 也不得不進行三次握手來同步各自的序列號，而且初始化序列號時是採用隨機的方式（不完全隨機，而是隨著時間流逝而線性增長，到了 2^32 盡頭再回滾）來提升攻擊者猜測序列號的難度，以增加安全性。

但是這種方式只能避免攻擊者預測出合法的 RST 報文，而無法避免攻擊者截獲客戶端的報文，然後中途偽造出合法 RST 報文的攻擊的方式。

![](https://gw.alipayobjects.com/mdn/rms_1c90e8/afts/img/A*po6LQIBU7zIAAAAAAAAAAAAAARQnAQ)

大膽想一下，如果 TCP 的序列號也能被加密，或許真的不需要三次握手了，客戶端和服務端的初始序列號都從 0 開始，也就不用做同步序列號的工作了，但是要實現這個要改造整個協議棧，太過於麻煩，即使實現出來了，很多老的網絡設備未必能兼容。

## TCP 存在隊頭阻塞問題

TCP 是字節流協議，**TCP 層必須保證收到的字節數據是完整且有序的**，如果序列號較低的 TCP 段在網絡傳輸中丟失了，即使序列號較高的 TCP 段已經被接收了，應用層也無法從內核中讀取到這部分數據。如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/%E7%BD%91%E7%BB%9C/http3/tcp%E9%98%9F%E5%A4%B4%E9%98%BB%E5%A1%9E.gif)

圖中發送方發送了很多個 packet，每個 packet 都有自己的序號，你可以認為是 TCP 的序列號，其中 `packet #3` 在網絡中丟失了，即使 `packet #4-6` 被接收方收到後，由於內核中的 TCP 數據不是連續的，於是接收方的應用層就無法從內核中讀取到，只有等到 `packet #3` 重傳後，接收方的應用層才可以從內核中讀取到數據。

這就是 TCP 隊頭阻塞問題，但這也不能怪 TCP ，因為只有這樣做才能保證數據的有序性。

HTTP/2 多個請求是跑在一個 TCP 連接中的，那麼當 TCP 丟包時，整個 TCP 都要等待重傳，那麼就會阻塞該 TCP 連接中的所有請求，所以 HTTP/2 隊頭阻塞問題就是因為 TCP 協議導致的。

![](https://pic2.zhimg.com/80/v2-2dd2a9fb8693489b9a0b24771c8a40a1_1440w.jpg)



## 網絡遷移需要重新建立 TCP 連接

基於 TCP 傳輸協議的 HTTP 協議，由於是通過四元組（源 IP、源端口、目的 IP、目的端口）確定一條 TCP 連接。

![TCP 四元組](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9jZG4uanNkZWxpdnIubmV0L2doL3hpYW9saW5jb2Rlci9JbWFnZUhvc3QyLyVFOCVBRSVBMSVFNyVBRSU5NyVFNiU5QyVCQSVFNyVCRCU5MSVFNyVCQiU5Qy9UQ1AtJUU0JUI4JTg5JUU2JUFDJUExJUU2JThGJUExJUU2JTg5JThCJUU1JTkyJThDJUU1JTlCJTlCJUU2JUFDJUExJUU2JThDJUE1JUU2JTg5JThCLzEwLmpwZw?x-oss-process=image/format,png)

那麼**當移動設備的網絡從 4G 切換到 WIFI 時，意味著 IP 地址變化了，那麼就必須要斷開連接，然後重新建立 TCP 連接**。

而建立連接的過程包含 TCP 三次握手和 TLS 四次握手的時延，以及 TCP 慢啟動的減速過程，給用戶的感覺就是網絡突然卡頓了一下，因此連接的遷移成本是很高的。

## 結尾

我記得之前在群裡看到，有位讀者字節一面的時候被問到：「**如何基於 UDP 協議實現可靠傳輸？**」

很多同學第一反應就會說把 TCP 可靠傳輸的特性（序列號、確認應答、超時重傳、流量控制、擁塞控制）在應用層實現一遍。

實現的思路確實這樣沒錯，但是有沒有想過，**既然 TCP 天然支持可靠傳輸，為什麼還需要基於 UDP 實現可靠傳輸呢？這不是重複造輪子嗎？**

所以，我們要先弄清楚 TCP 協議有哪些痛點？而這些痛點是否可以在基於 UDP 協議實現的可靠傳輸協議中得到改進？

現在市面上已經有基於 UDP 協議實現的可靠傳輸協議的成熟方案了，那就是 QUIC 協議，**QUIC 協議把我本文說的 TCP 的缺點都給解決了**，而且已經應用在了 HTTP/3。

![](https://miro.medium.com/max/1400/1*uk5OZPL7gtUwqRLwaoGyFw.png)

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

