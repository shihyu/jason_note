# 4.17 如何基於 UDP 協議實現可靠傳輸？

大家好，我是小林。

我記得之前在群裡看到，有位讀者字節一面的時候被問到：「**如何基於 UDP 協議實現可靠傳輸？**」

很多同學第一反應就會說把 TCP 可靠傳輸的特性（序列號、確認應答、超時重傳、流量控制、擁塞控制）在應用層實現一遍。

實現的思路確實這樣沒錯，但是有沒有想過，**既然 TCP 天然支持可靠傳輸，為什麼還需要基於 UDP 實現可靠傳輸呢？這不是重複造輪子嗎？**

所以，我們要先弄清楚 TCP 協議有哪些痛點？而這些痛點是否可以在基於 UDP 協議實現的可靠傳輸協議中得到改進？

在之前這篇文章：[TCP 就沒什麼缺陷嗎？](https://mp.weixin.qq.com/s/9kHoRk6QIYOFUR_PCmHY6g)，我已經說了 TCP 協議四個方面的缺陷：

- 升級 TCP 的工作很困難；
- TCP 建立連接的延遲；
- TCP 存在隊頭阻塞問題；
- 網絡遷移需要重新建立 TCP 連接；

現在市面上已經有基於 UDP 協議實現的可靠傳輸協議的成熟方案了，那就是 QUIC 協議，已經應用在了 HTTP/3。

這次，**聊聊 QUIC 是如何實現可靠傳輸的？又是如何解決上面 TCP 協議四個方面的缺陷**？

![](https://img-blog.csdnimg.cn/605d1026df934f20a5ee12f3c55aa6a7.png)

## QUIC 是如何實現可靠傳輸的？

要基於 UDP 實現的可靠傳輸協議，那麼就要在應用層下功夫，也就是要設計好協議的頭部字段。

拿 HTTP/3 舉例子，在 UDP 報文頭部與 HTTP 消息之間，共有 3 層頭部：

![](https://static001.geekbang.org/resource/image/ab/7c/ab3283383013b707d1420b6b4cb8517c.png)

整體看的視角是這樣的：

![](https://docs.citrix.com/en-us/citrix-adc/media/http3-over-quic-protocol-works.png)

接下來，分別對每一個 Header 做個介紹。

### Packet Header

Packet Header 首次建立連接時和日常傳輸數據時使用的 Header 是不同的。如下圖（*注意我沒有把 Header 所有字段都畫出來，只是畫出了重要的字段*）：

![Packet Header](https://img-blog.csdnimg.cn/bcf3ccb6a15c4cdebe1cd0527fdd9a5e.png)

Packet Header 細分這兩種：

- Long Packet Header 用於首次建立連接。
- Short Packet Header 用於日常傳輸數據。

QUIC 也是需要三次握手來建立連接的，主要目的是為了協商連接 ID。協商出連接 ID 後，後續傳輸時，雙方只需要固定住連接 ID，從而實現連接遷移功能。所以，你可以看到日常傳輸數據的 Short Packet Header 不需要在傳輸 Source Connection ID 字段了，只需要傳輸 Destination Connection ID。

Short Packet Header 中的 `Packet Number` 是每個報文獨一無二的編號，它是**嚴格遞增**的，也就是說就算 Packet N 丟失了，重傳的 Packet N 的 Packet Number 已經不是 N，而是一個比 N 大的值。

![](https://img-blog.csdnimg.cn/635813465fbb449882da2e2bee39f24e.png)

>  為什麼要這麼設計呢？

我們先來看看  TCP 的問題，TCP 在重傳報文時的序列號和原始報文的序列號是一樣的，也正是由於這個特性，引入了 TCP 重傳的歧義問題。

![TCP 重傳的歧義問題](https://img-blog.csdnimg.cn/7e4e778413c1452bb6d58ec3d5452316.png)

比如上圖，當 TCP 發生超時重傳後，客戶端發起重傳，然後接收到了服務端確認 ACK 。由於客戶端原始報文和重傳報文序列號都是一樣的，那麼服務端針對這兩個報文回覆的都是相同的 ACK。

這樣的話，客戶端就無法判斷出是「原始報文的響應」還是「重傳報文的響應」，這樣在計算 RTT（往返時間） 時應該選擇從發送原始報文開始計算，還是重傳原始報文開始計算呢？

- 如果算成原始報文的響應，但實際上是重傳報文的響應（上圖左），會導致採樣 RTT 變大；
- 如果算成重傳報文的響應，但實際上是原始報文的響應（上圖右），又很容易導致採樣 RTT 過小；

RTO （超時時間）是基於 RTT 來計算的，那麼如果 RTT 計算不精準，那麼 RTO （超時時間）也會不精確，這樣可能導致重傳的概率事件增大。

QUIC 報文中的 Pakcet Number 是嚴格遞增的， 即使是重傳報文，它的 Pakcet Number 也是遞增的，這樣就能更加精確計算出報文的 RTT。

![](https://img-blog.csdnimg.cn/ca91985c9a94487a8a29db1249109717.png)

如果 ACK 的 Packet Number 是 N+M，就根據重傳報文計算採樣 RTT。如果 ACK 的 Pakcet Number 是 N，就根據原始報文的時間計算採樣 RTT，沒有歧義性的問題。

另外，還有一個好處，**QUIC 使用的 Packet Number 單調遞增的設計，可以讓數據包不再像 TCP 那樣必須有序確認，QUIC 支持亂序確認，當數據包Packet N 丟失後，只要有新的已接收數據包確認，當前窗口就會繼續向右滑動**（後面講流量控制的時候，會舉例子）。

待發送端獲知數據包Packet N 丟失後，會將需要重傳的數據包放到待發送隊列，重新編號比如數據包Packet N+M 後重新發送給接收端，對重傳數據包的處理跟發送新的數據包類似，這樣就不會因為丟包重傳將當前窗口阻塞在原地，從而解決了隊頭阻塞問題。

所以，Packet Number 單調遞增的兩個好處：

- 可以更加精確計算 RTT，沒有 TCP 重傳的歧義性問題；
- 可以支持亂序確認，因為丟包重傳將當前窗口阻塞在原地，而 TCP 必須是順序確認的，丟包時會導致窗口不滑動；

### QUIC Frame Header 

一個 Packet 報文中可以存放多個 QUIC Frame。

![](https://img-blog.csdnimg.cn/6a94d41ef3d14cb6b7846e73da6c3104.png)

每一個 Frame 都有明確的類型，針對類型的不同，功能也不同，自然格式也不同。

我這裡只舉例  Stream 類型的 Frame 格式，Stream 可以認為就是一條 HTTP 請求，它長這樣：

![](https://img-blog.csdnimg.cn/536298d2c54a43b699026bffe0f85010.png)

- Stream ID 作用：多個併發傳輸的 HTTP 消息，通過不同的 Stream ID 加以區別，類似於 HTTP2 的 Stream ID；
- Offset 作用：類似於 TCP 協議中的 Seq 序號，**保證數據的順序性和可靠性**；
- Length 作用：指明瞭 Frame 數據的長度。

在前面介紹 Packet Header 時，說到 Packet Number 是嚴格遞增，即使重傳報文的 Packet Number 也是遞增的，既然重傳數據包的 Packet N+M 與丟失數據包的 Packet N 編號並不一致，我們怎麼確定這兩個數據包的內容一樣呢？

所以引入 Frame Header 這一層，**通過 Stream ID + Offset 字段信息實現數據的有序性**，通過比較兩個數據包的 Stream ID 與 Stream Offset ，如果都是一致，就說明這兩個數據包的內容一致。

舉個例子，下圖中，數據包 Packet N 丟失了，後面重傳該數據包的編號為 Packet N+2，**丟失的數據包和重傳的數據包 Stream ID 與 Offset 都一致，說明這兩個數據包的內容一致**。這些數據包傳輸到接收端後，接收端能根據 Stream ID 與 Offset 字段信息將  Stream x 和 Stream x+y 按照順序組織起來，然後交給應用程序處理。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/Packet丟失.jpeg)

總的來說，**QUIC 通過單向遞增的 Packet Number，配合 Stream ID 與 Offset 字段信息，可以支持亂序確認而不影響數據包的正確組裝**，擺脫了TCP 必須按順序確認應答 ACK 的限制，解決了 TCP 因某個數據包重傳而阻塞後續所有待發送數據包的問題。

## QUIC 是如何解決 TCP 隊頭阻塞問題的？

### 什麼是 TCP 隊頭阻塞問題？

TCP 隊頭阻塞的問題要從兩個角度看，一個是**發送窗口的隊頭阻塞**，另外一個是**接收窗口的隊頭阻塞**。

*1、發送窗口的隊頭阻塞。*

TCP 發送出去的數據，都是需要按序確認的，只有在數據都被按順序確認完後，發送窗口才會往前滑動。

舉個例子，比如下圖的發送方把發送窗口內的數據全部都發出去了，可用窗口的大小就為 0 了，表明可用窗口耗盡，在沒收到 ACK 確認之前是無法繼續發送數據了。

![可用窗口耗盡](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8F%AF%E9%9D%A0%E7%89%B9%E6%80%A7/17.jpg?)

接著，當發送方收到對第 `32~36` 字節的 ACK 確認應答後，則**滑動窗口往右邊移動 5 個字節，因為有 5 個字節的數據被應答確認**，接下來第 `52~56` 字節又變成了可用窗口，那麼後續也就可以發送 `52~56` 這 5 個字節的數據了。

![32 ~ 36 字節已確認](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8F%AF%E9%9D%A0%E7%89%B9%E6%80%A7/18.jpg)

**但是如果某個數據報文丟失或者其對應的 ACK 報文在網絡中丟失，會導致發送方無法移動發送窗口，這時就無法再發送新的數據**，只能超時重傳這個數據報文，直到收到這個重傳報文的 ACK，發送窗口才會移動，繼續後面的發送行為。

舉個例子，比如下圖，客戶端是發送方，服務器是接收方。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/ack丟失.jpeg)

客戶端發送了第 5～9 字節的數據，但是第 5 字節的 ACK 確認報文在網絡中丟失了，那麼即使客戶端收到第 6～9 字節的 ACK 確認報文，發送窗口也不會往前移動。

**此時的第 5 字節相當於“隊頭”，因為沒有收到“隊頭”的 ACK 確認報文，導致發送窗口無法往前移動，此時發送方就無法繼續發送後面的數據，相當於按下了發送行為的暫停鍵，這就是發送窗口的隊頭阻塞問題**。

*2、接收窗口的隊頭阻塞。*

接收方收到的數據範圍必須在接收窗口範圍內，如果收到超過接收窗口範圍的數據，就會丟棄該數據，比如下圖接收窗口的範圍是 32 ～ 51 字節，如果收到第 52 字節以上數據都會被丟棄。

![接收窗口](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8F%AF%E9%9D%A0%E7%89%B9%E6%80%A7/20.jpg)

接收窗口什麼時候才能滑動？當接收窗口收到有序數據時，接收窗口才能往前滑動，然後那些已經接收並且被確認的「有序」數據就可以被應用層讀取。

但是，**當接收窗口收到的數據不是有序的，比如收到第 33～40 字節的數據，由於第 32 字節數據沒有收到， 接收窗口無法向前滑動，那麼即使先收到第 33～40 字節的數據，這些數據也無法被應用層讀取的**。只有當發送方重傳了第 32 字節數據並且被接收方收到後，接收窗口才會往前滑動，然後應用層才能從內核讀取第 32～40 字節的數據。

好了，至此發送窗口和接收窗口的隊頭阻塞問題都說完了，這兩個問題的原因都是因為 TCP 必須按序處理數據，也就是 TCP 層為了保證數據的有序性，只有在處理完有序的數據後，滑動窗口才能往前滑動，否則就停留。

- 停留「發送窗口」會使得發送方無法繼續發送數據。

- 停留「接收窗口」會使得應用層無法讀取新的數據。

其實也不能怪 TCP 協議，它本來設計目的就是為了保證數據的有序性。

### HTTP/2  的隊頭阻塞

HTTP/2 通過抽象出 Stream 的概念，實現了 HTTP 併發傳輸，一個 Stream 就代表 HTTP/1.1 裡的請求和響應。

![HTTP/2](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/%E7%BD%91%E7%BB%9C/http2/stream2.png)

在 HTTP/2 連接上，不同 Stream 的幀是可以亂序發送的（因此可以併發不同的 Stream ），因為每個幀的頭部會攜帶 Stream ID 信息，所以接收端可以通過 Stream ID 有序組裝成 HTTP 消息，而同一 Stream 內部的幀必須是嚴格有序的。

**但是 HTTP/2 多個 Stream 請求都是在一條 TCP 連接上傳輸，這意味著多個 Stream 共用同一個 TCP 滑動窗口，那麼當發生數據丟失，滑動窗口是無法往前移動的，此時就會阻塞住所有的 HTTP 請求，這屬於 TCP 層隊頭阻塞**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/http2阻塞.jpeg)

### 沒有隊頭阻塞的 QUIC

QUIC 也借鑑 HTTP/2 裡的 Stream 的概念，在一條 QUIC 連接上可以併發發送多個 HTTP 請求 (Stream)。

但是 **QUIC 給每一個 Stream 都分配了一個獨立的滑動窗口，這樣使得一個連接上的多個 Stream 之間沒有依賴關係，都是相互獨立的，各自控制的滑動窗口**。

假如 Stream2 丟了一個 UDP 包，也只會影響 Stream2 的處理，不會影響其他 Stream，與 HTTP/2 不同，HTTP/2 只要某個流中的數據包丟失了，其他流也會因此受影響。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/quic無阻塞.jpeg)

## QUIC 是如何做流量控制的？

TCP 流量控制是通過讓「接收方」告訴「發送方」，它（接收方）的接收窗口有多大，從而讓「發送方」根據「接收方」的實際接收能力控制發送的數據量。

QUIC 實現流量控制的方式：

- 通過 window_update 幀告訴對端自己可以接收的字節數，這樣發送方就不會發送超過這個數量的數據。
- 通過 BlockFrame 告訴對端由於流量控制被阻塞了，無法發送數據。

在前面說到，TCP 的接收窗口在收到有序的數據後，接收窗口才能往前滑動，否則停止滑動；TCP 的發送窗口在收到對已發送數據的順序確認 ACK後，發送窗口才能往前滑動，否則停止滑動。

QUIC 是基於 UDP 傳輸的，而 UDP 沒有流量控制，因此 QUIC 實現了自己的流量控制機制，QUIC 的滑動窗口滑動的條件跟 TCP 有一點差別，但是同一個 Stream 的數據也是要保證順序的，不然無法實現可靠傳輸，因此同一個 Stream 的數據包丟失了，也會造成窗口無法滑動。

**QUIC 的 每個 Stream 都有各自的滑動窗口，不同 Stream 互相獨立，隊頭的 Stream A 被阻塞後，不妨礙 StreamB、C的讀取**。而對於 HTTP/2 而言，所有的 Stream 都跑在一條 TCP 連接上，而這些 Stream 共享一個滑動窗口，因此同一個Connection內，Stream A 被阻塞後，StreamB、C 必須等待。

QUIC 實現了兩種級別的流量控制，分別為 Stream 和 Connection 兩種級別：

- **Stream 級別的流量控制**：Stream 可以認為就是一條 HTTP 請求，每個 Stream 都有獨立的滑動窗口，所以每個 Stream 都可以做流量控制，防止單個 Stream 消耗連接（Connection）的全部接收緩衝。
- **Connection 流量控制**：限制連接中所有 Stream 相加起來的總字節數，防止發送方超過連接的緩衝容量。

### Stream 級別的流量控制

最開始，接收方的接收窗口初始狀態如下（網上的講 QUIC 流量控制的資料太少了，下面的例子我是參考 google 文檔的：[Flow control in QUIC](https://docs.google.com/document/d/1F2YfdDXKpy20WVKJueEf4abn_LVZHhMUMS5gX6Pgjl4/mobilebasic)）：

![](https://img-blog.csdnimg.cn/f1070a6eccd24559904815297b07f789.png)

接著，接收方收到了發送方發送過來的數據，有的數據被上層讀取了，有的數據丟包了，此時的接收窗口狀況如下：

![](https://img-blog.csdnimg.cn/77e9a7cf70da4a1b981f61e78db2ad56.png)

可以看到，**接收窗口的左邊界取決於接收到的最大偏移字節數**，此時的`接收窗口  = 最大窗口數 - 接收到的最大偏移數`。

這裡就可以看出 QUIC 的流量控制和 TCP 有點區別了：

- TCP 的接收窗口只有在前面所有的 Segment 都接收的情況下才會移動左邊界，當在前面還有字節未接收但收到後面字節的情況下，窗口也不會移動。
- QUIC 的接收窗口的左邊界滑動條件取決於接收到的最大偏移字節數。

*PS：但是你要問我這麼設計有什麼好處？我也暫時沒想到，因為資料太少了，至今沒找到一個合理的說明，如果你知道，歡迎告訴我啊！*

那接收窗口右邊界觸發的滑動條件是什麼呢？看下圖：

![接收窗口觸發的滑動](https://img-blog.csdnimg.cn/bbde0c66088f439b919a6d18b389aadb.png)

當圖中的綠色部分數據超過最大接收窗口的一半後，最大接收窗口向右移動，接收窗口的右邊界也向右擴展，同時給對端發送「窗口更新幀」，當發送方收到接收方的窗口更新幀後，發送窗口的右邊界也會往右擴展，以此達到窗口滑動的效果。

綠色部分的數據是已收到的順序的數據，**如果中途丟失了數據包，導致綠色部分的數據沒有超過最大接收窗口的一半，那接收窗口就無法滑動了**，這個隻影響同一個 Stream，其他 Stream 是不會影響的，因為每個 Stream 都有各自的滑動窗口。

在前面我們說過 QUIC 支持亂序確認，具體是怎麼做到的呢？

接下來，舉個例子（下面的例子來源於：[QUIC——快速UDP網絡連接協議](https://juejin.cn/post/7066993430102016037)）：

如圖所示，當前發送方的緩衝區大小為8，發送方 QUIC 按序（offset順序）發送 29-36 的數據包：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/亂序確認1.png)

31、32、34數據包先到達，基於 offset 被優先亂序確認，但 30 數據包沒有確認，所以當前已提交的字節偏移量不變，發送方的緩存區不變。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/亂序確認2.png)

30 到達並確認，發送方的緩存區收縮到閾值，接收方發送 MAX_STREAM_DATA Frame（協商緩存大小的特定幀）給發送方，請求增長最大絕對字節偏移量。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/亂序確認3.png)

協商完畢後最大絕對字節偏移量右移，發送方的緩存區變大，同時發送方發現數據包33超時

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/亂序確認4.png)

發送方將超時數據包重新編號為 42 繼續發送

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/quic/亂序確認5.png)

以上就是最基本的數據包發送-接收過程，控制數據發送的唯一限制就是最大絕對字節偏移量，該值是接收方基於當前已經提交的偏移量（連續已確認並向上層應用提交的數據包offset）和發送方協商得出。

### Connection 流量控制

而對於 Connection 級別的流量窗口，其接收窗口大小就是各個 Stream 接收窗口大小之和。

![Connection 流量控制](https://img-blog.csdnimg.cn/839501cffa7146cbb8d992264594e61d.png)

上圖所示的例子，所有 Streams 的最大窗口數為 120，其中：

- Stream 1 的最大接收偏移為 100，可用窗口 = 120 - 100 = 20
- Stream 2 的最大接收偏移為 90，可用窗口 = 120 - 90 = 30
- Stream 3 的最大接收偏移為 110，可用窗口 = 120 - 110 = 10

那麼整個 Connection 的可用窗口 = 20 + 30 + 10 = 60

```text
可用窗口 = Stream 1 可用窗口 + Stream 2 可用窗口 + Stream 3 可用窗口
```

## QUIC 對擁塞控制改進

QUIC 協議當前默認使用了 TCP 的 Cubic 擁塞控制算法（我們熟知的慢開始、擁塞避免、快重傳、快恢復策略），同時也支持 CubicBytes、Reno、RenoBytes、BBR、PCC 等擁塞控制算法，相當於將 TCP 的擁塞控制算法照搬過來了。

QUIC 是如何改進 TCP 的擁塞控制算法的呢？

QUIC 是處於應用層的，應用程序層面就能實現不同的擁塞控制算法，不需要操作系統，不需要內核支持。這是一個飛躍，因為傳統的 TCP 擁塞控制，必須要端到端的網絡協議棧支持，才能實現控制效果。而內核和操作系統的部署成本非常高，升級週期很長，所以 TCP 擁塞控制算法迭代速度是很慢的。而 **QUIC 可以隨瀏覽器更新，QUIC 的擁塞控制算法就可以有較快的迭代速度**。

TCP 更改擁塞控制算法是對系統中所有應用都生效，無法根據不同應用設定不同的擁塞控制策略。但是因為 QUIC 處於應用層，所以就**可以針對不同的應用設置不同的擁塞控制算法**，這樣靈活性就很高了。

## QUIC 更快的連接建立

對於 HTTP/1 和 HTTP/2 協議，TCP 和 TLS 是分層的，分別屬於內核實現的傳輸層、openssl 庫實現的表示層，因此它們難以合併在一起，需要分批次來握手，先 TCP 握手（1RTT），再 TLS 握手（2RTT），所以需要 3RTT 的延遲才能傳輸數據，就算 Session 會話服用，也需要至少 2 個 RTT。

HTTP/3 在傳輸數據前雖然需要 QUIC 協議握手，這個握手過程只需要 1 RTT，握手的目的是為確認雙方的「連接 ID」，連接遷移就是基於連接 ID 實現的。

但是 HTTP/3 的 QUIC 協議並不是與 TLS 分層，而是**QUIC 內部包含了 TLS，它在自己的幀會攜帶 TLS 裡的“記錄”，再加上 QUIC 使用的是 TLS1.3，因此僅需 1 個 RTT 就可以「同時」完成建立連接與密鑰協商，甚至在第二次連接的時候，應用數據包可以和 QUIC 握手信息（連接信息 + TLS 信息）一起發送，達到 0-RTT 的效果**。

如下圖右邊部分，HTTP/3 當會話恢復時，有效負載數據與第一個數據包一起發送，可以做到 0-RTT（下圖的右下角）：

![](https://img-blog.csdnimg.cn/4cad213f5125432693e0e2a512c2d1a1.png)

## QUIC 是如何遷移連接的？

基於 TCP 傳輸協議的 HTTP 協議，由於是通過四元組（源 IP、源端口、目的 IP、目的端口）確定一條 TCP 連接。

![TCP 四元組](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9jZG4uanNkZWxpdnIubmV0L2doL3hpYW9saW5jb2Rlci9JbWFnZUhvc3QyLyVFOCVBRSVBMSVFNyVBRSU5NyVFNiU5QyVCQSVFNyVCRCU5MSVFNyVCQiU5Qy9UQ1AtJUU0JUI4JTg5JUU2JUFDJUExJUU2JThGJUExJUU2JTg5JThCJUU1JTkyJThDJUU1JTlCJTlCJUU2JUFDJUExJUU2JThDJUE1JUU2JTg5JThCLzEwLmpwZw?x-oss-process=image/format,png)

那麼**當移動設備的網絡從 4G 切換到 WIFI 時，意味著 IP 地址變化了，那麼就必須要斷開連接，然後重新建立 TCP 連接**。

而建立連接的過程包含 TCP 三次握手和 TLS 四次握手的時延，以及 TCP 慢啟動的減速過程，給用戶的感覺就是網絡突然卡頓了一下，因此連接的遷移成本是很高的。

QUIC 協議沒有用四元組的方式來“綁定”連接，而是通過**連接 ID**來標記通信的兩個端點，客戶端和服務器可以各自選擇一組 ID 來標記自己，因此即使移動設備的網絡變化後，導致 IP 地址變化了，只要仍保有上下文信息（比如連接 ID、TLS 密鑰等），就可以“無縫”地複用原連接，消除重連的成本，沒有絲毫卡頓感，達到了**連接遷移**的功能。

---

參考資料：

- https://www.taohui.tech/2021/02/04/%E7%BD%91%E7%BB%9C%E5%8D%8F%E8%AE%AE/%E6%B7%B1%E5%85%A5%E5%89%96%E6%9E%90HTTP3%E5%8D%8F%E8%AE%AE/
- https://zhuanlan.zhihu.com/p/32553477

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)