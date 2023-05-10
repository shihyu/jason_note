# 3.7 HTTP/3 強勢來襲

HTTP/3 現在（2022 年 5 月）還沒正式推出，不過自 2017 年起，HTTP/3 已經更新到 34 個草案了，基本的特性已經確定下來了，對於包格式可能後續會有變化。

所以，這次 HTTP/3 介紹不會涉及到包格式，只說它的特性。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http3/HTTP3提綱.png)

## 美中不足的 HTTP/2 

HTTP/2 通過頭部壓縮、二進制編碼、多路複用、服務器推送等新特性大幅度提升了 HTTP/1.1 的性能，而美中不足的是 HTTP/2 協議是基於 TCP 實現的，於是存在的缺陷有三個。

- 隊頭阻塞；
- TCP 與 TLS 的握手時延遲；
- 網絡遷移需要重新連接；

### 隊頭阻塞

HTTP/2 多個請求是跑在一個 TCP 連接中的，那麼當 TCP 丟包時，整個 TCP 都要等待重傳，那麼就會阻塞該 TCP 連接中的所有請求。

比如下圖中，Stream 2 有一個 TCP 報文丟失了，那麼即使收到了 Stream 3 和 Stream 4 的 TCP 報文，應用層也是無法讀取的，相當於阻塞了 Stream 3 和 Stream 4 請求。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/http2阻塞.jpeg)

因為 TCP 是字節流協議，TCP 層必須保證收到的字節數據是完整且有序的，如果序列號較低的 TCP 段在網絡傳輸中丟失了，即使序列號較高的 TCP 段已經被接收了，應用層也無法從內核中讀取到這部分數據，從 HTTP 視角看，就是請求被阻塞了。

舉個例子，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http3/tcp隊頭阻塞.gif)

圖中發送方發送了很多個 Packet，每個 Packet 都有自己的序號，你可以認為是 TCP 的序列號，其中 Packet 3 在網絡中丟失了，即使 Packet 4-6 被接收方收到後，由於內核中的 TCP 數據不是連續的，於是接收方的應用層就無法從內核中讀取到，只有等到 Packet 3 重傳後，接收方的應用層才可以從內核中讀取到數據，這就是 HTTP/2 的隊頭阻塞問題，是在 TCP 層面發生的。

### TCP 與 TLS 的握手時延遲

發起 HTTP 請求時，需要經過 TCP 三次握手和 TLS 四次握手（TLS 1.2）的過程，因此共需要 3 個 RTT 的時延才能發出請求數據。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http3/TCP%2BTLS.gif)

另外，TCP 由於具有「擁塞控制」的特性，所以剛建立連接的 TCP 會有個「慢啟動」的過程，它會對 TCP 連接產生“減速”效果。

### 網絡遷移需要重新連接

一個 TCP 連接是由四元組（源 IP 地址，源端口，目標 IP 地址，目標端口）確定的，這意味著如果 IP 地址或者端口變動了，就會導致需要 TCP 與 TLS 重新握手，這不利於移動設備切換網絡的場景，比如 4G 網絡環境切換成 WiFi。

這些問題都是 TCP 協議固有的問題，無論應用層的 HTTP/2 在怎麼設計都無法逃脫。要解決這個問題，就必須把**傳輸層協議替換成 UDP**，這個大膽的決定，HTTP/3 做了！

![HTTP/1 ~ HTTP/3](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/HTTP/27-HTTP3.png)

## QUIC 協議的特點

我們深知，UDP 是一個簡單、不可靠的傳輸協議，而且是 UDP 包之間是無序的，也沒有依賴關係。

而且，UDP 是不需要連接的，也就不需要握手和揮手的過程，所以天然的就比 TCP 快。

當然，HTTP/3 不僅僅只是簡單將傳輸協議替換成了 UDP，還基於 UDP 協議在「應用層」實現了 **QUIC 協議**，它具有類似 TCP 的連接管理、擁塞窗口、流量控制的網絡特性，相當於將不可靠傳輸的 UDP 協議變成“可靠”的了，所以不用擔心數據包丟失的問題。

QUIC 協議的優點有很多，這裡舉例幾個，比如：

- 無隊頭阻塞；
- 更快的連接建立；
- 連接遷移；


### 無隊頭阻塞

QUIC 協議也有類似 HTTP/2 Stream 與多路複用的概念，也是可以在同一條連接上併發傳輸多個 Stream，Stream 可以認為就是一條 HTTP 請求。

由於 QUIC 使用的傳輸協議是 UDP，UDP 不關心數據包的順序，如果數據包丟失，UDP 也不關心。

不過 QUIC 協議會保證數據包的可靠性，每個數據包都有一個序號唯一標識。當某個流中的一個數據包丟失了，即使該流的其他數據包到達了，數據也無法被 HTTP/3 讀取，直到 QUIC 重傳丟失的報文，數據才會交給 HTTP/3。

而其他流的數據報文只要被完整接收，HTTP/3 就可以讀取到數據。這與 HTTP/2 不同，HTTP/2 只要某個流中的數據包丟失了，其他流也會因此受影響。

所以，QUIC 連接上的多個 Stream 之間並沒有依賴，都是獨立的，某個流發生丟包了，只會影響該流，其他流不受影響。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/quic無阻塞.jpeg)

### 更快的連接建立


對於 HTTP/1 和 HTTP/2 協議，TCP 和 TLS 是分層的，分別屬於內核實現的傳輸層、OpenSSL 庫實現的表示層，因此它們難以合併在一起，需要分批次來握手，先 TCP 握手，再 TLS 握手。

HTTP/3 在傳輸數據前雖然需要 QUIC 協議握手，這個握手過程只需要 1 RTT，握手的目的是為確認雙方的「連接 ID」，連接遷移就是基於連接 ID 實現的。

但是 HTTP/3 的 QUIC 協議並不是與 TLS 分層，而是 **QUIC 內部包含了 TLS，它在自己的幀會攜帶 TLS 裡的“記錄”，再加上 QUIC 使用的是 TLS 1.3，因此僅需 1 個 RTT 就可以「同時」完成建立連接與密鑰協商，甚至在第二次連接的時候，應用數據包可以和 QUIC 握手信息（連接信息 + TLS 信息）一起發送，達到 0-RTT 的效果**。

如下圖右邊部分，HTTP/3 當會話恢復時，有效負載數據與第一個數據包一起發送，可以做到 0-RTT：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http3/0-rtt.gif)


### 連接遷移

在前面我們提到，基於 TCP 傳輸協議的 HTTP 協議，由於是通過四元組（源 IP、源端口、目的 IP、目的端口）確定一條 TCP 連接。

![TCP 四元組](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9jZG4uanNkZWxpdnIubmV0L2doL3hpYW9saW5jb2Rlci9JbWFnZUhvc3QyLyVFOCVBRSVBMSVFNyVBRSU5NyVFNiU5QyVCQSVFNyVCRCU5MSVFNyVCQiU5Qy9UQ1AtJUU0JUI4JTg5JUU2JUFDJUExJUU2JThGJUExJUU2JTg5JThCJUU1JTkyJThDJUU1JTlCJTlCJUU2JUFDJUExJUU2JThDJUE1JUU2JTg5JThCLzEwLmpwZw?x-oss-process=image/format,png)

那麼當移動設備的網絡從 4G 切換到 WiFi 時，意味著 IP 地址變化了，那麼就必須要斷開連接，然後重新建立連接，而建立連接的過程包含 TCP 三次握手和 TLS 四次握手的時延，以及 TCP 慢啟動的減速過程，給用戶的感覺就是網絡突然卡頓了一下，因此連接的遷移成本是很高的。


而 QUIC 協議沒有用四元組的方式來“綁定”連接，而是通過**連接 ID** 來標記通信的兩個端點，客戶端和服務器可以各自選擇一組 ID 來標記自己，因此即使移動設備的網絡變化後，導致 IP 地址變化了，只要仍保有上下文信息（比如連接 ID、TLS 密鑰等），就可以“無縫”地複用原連接，消除重連的成本，沒有絲毫卡頓感，達到了**連接遷移**的功能。

## HTTP/3 協議

瞭解完 QUIC 協議的特點後，我們再來看看 HTTP/3 協議在 HTTP 這一層做了什麼變化。

HTTP/3 同 HTTP/2 一樣採用二進制幀的結構，不同的地方在於 HTTP/2 的二進制幀裡需要定義 Stream，而  HTTP/3 自身不需要再定義 Stream，直接使用 QUIC 裡的 Stream，於是 HTTP/3 的幀的結構也變簡單了。 

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http3/http3frame.png)

 從上圖可以看到，HTTP/3 幀頭只有兩個字段：類型和長度。


根據幀類型的不同，大體上分為數據幀和控制幀兩大類，Headers 幀（HTTP 頭部）和 DATA 幀（HTTP 包體）屬於數據幀。


HTTP/3 在頭部壓縮算法這一方面也做了升級，升級成了 **QPACK**。與 HTTP/2 中的 HPACK 編碼方式相似，HTTP/3 中的 QPACK 也採用了靜態表、動態表及 Huffman 編碼。

對於靜態表的變化，HTTP/2 中的 HPACK 的靜態表只有 61 項，而 HTTP/3 中的 QPACK 的靜態表擴大到 91 項。

HTTP/2 和 HTTP/3 的 Huffman 編碼並沒有多大不同，但是動態表編解碼方式不同。

所謂的動態表，在首次請求-響應後，雙方會將未包含在靜態表中的 Header 項更新各自的動態表，接著後續傳輸時僅用 1 個數字表示，然後對方可以根據這 1 個數字從動態表查到對應的數據，就不必每次都傳輸長長的數據，大大提升了編碼效率。

可以看到，**動態表是具有時序性的，如果首次出現的請求發生了丟包，後續的收到請求，對方就無法解碼出 HPACK 頭部，因為對方還沒建立好動態表，因此後續的請求解碼會阻塞到首次請求中丟失的數據包重傳過來**。


HTTP/3 的 QPACK 解決了這一問題，那它是如何解決的呢？

QUIC 會有兩個特殊的單向流，所謂的單向流只有一端可以發送消息，雙向則指兩端都可以發送消息，傳輸 HTTP 消息時用的是雙向流，這兩個單向流的用法：

- 一個叫 QPACK Encoder Stream，用於將一個字典（Key-Value）傳遞給對方，比如面對不屬於靜態表的 HTTP 請求頭部，客戶端可以通過這個 Stream 發送字典；
- 一個叫 QPACK Decoder Stream，用於響應對方，告訴它剛發的字典已經更新到自己的本地動態表了，後續就可以使用這個字典來編碼了。

這兩個特殊的單向流是用來**同步雙方的動態表**，編碼方收到解碼方更新確認的通知後，才使用動態表編碼 HTTP 頭部。

## 總結

HTTP/2 雖然具有多個流併發傳輸的能力，但是傳輸層是 TCP 協議，於是存在以下缺陷：

- **隊頭阻塞**，HTTP/2 多個請求跑在一個 TCP 連接中，如果序列號較低的 TCP 段在網絡傳輸中丟失了，即使序列號較高的 TCP 段已經被接收了，應用層也無法從內核中讀取到這部分數據，從 HTTP 視角看，就是多個請求被阻塞了；
- **TCP 和 TLS 握手時延**，TCP 三次握手和 TLS 四次握手，共有 3-RTT 的時延；
- **連接遷移需要重新連接**，移動設備從 4G 網絡環境切換到 WiFi 時，由於 TCP 是基於四元組來確認一條 TCP 連接的，那麼網絡環境變化後，就會導致 IP 地址或端口變化，於是 TCP 只能斷開連接，然後再重新建立連接，切換網絡環境的成本高；

HTTP/3 就將傳輸層從 TCP 替換成了 UDP，並在 UDP 協議上開發了 QUIC 協議，來保證數據的可靠傳輸。

QUIC 協議的特點：

- **無隊頭阻塞**，QUIC 連接上的多個 Stream 之間並沒有依賴，都是獨立的，也不會有底層協議限制，某個流發生丟包了，只會影響該流，其他流不受影響；
- **建立連接速度快**，因為 QUIC 內部包含 TLS 1.3，因此僅需 1 個 RTT 就可以「同時」完成建立連接與 TLS 密鑰協商，甚至在第二次連接的時候，應用數據包可以和 QUIC 握手信息（連接信息 + TLS 信息）一起發送，達到 0-RTT 的效果。
- **連接遷移**，QUIC 協議沒有用四元組的方式來“綁定”連接，而是通過「連接 ID 」來標記通信的兩個端點，客戶端和服務器可以各自選擇一組 ID 來標記自己，因此即使移動設備的網絡變化後，導致 IP 地址變化了，只要仍保有上下文信息（比如連接 ID、TLS 密鑰等），就可以“無縫”地複用原連接，消除重連的成本；

另外 HTTP/3 的 QPACK 通過兩個特殊的單向流來同步雙方的動態表，解決了 HTTP/2 的 HPACK 隊頭阻塞問題。

**期待，HTTP/3 正式推出的那一天！**

---

參考資料：

1. https://medium.com/faun/http-2-spdy-and-http-3-quic-bae7d9a3d484
2. https://developers.google.com/web/fundamentals/performance/http2?hl=zh-cn
3. https://blog.cloudflare.com/http3-the-past-present-and-future/
4. https://tools.ietf.org/html/draft-ietf-quic-http-34
5. https://tools.ietf.org/html/draft-ietf-quic-transport-34#section-17
6. https://ably.com/topic/http3?amp%3Butm_campaign=evergreen&amp%3Butm_source=reddit&utm_medium=referral
7. https://www.nginx.org.cn/article/detail/422
8. https://www.bilibili.com/read/cv793000/
9. https://www.chinaz.com/2020/1009/1192436.shtml


---

哈嘍，我是小林，就愛圖解計算機基礎，如果文章對你有幫助，別忘記關注哦！

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

