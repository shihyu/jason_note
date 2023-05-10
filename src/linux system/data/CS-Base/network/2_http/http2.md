# 3.6 HTTP/2 牛逼在哪？ 


不多 BB 了，直接發車！

**一起來看看 HTTP/2 牛逼在哪？**


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/http2提綱.png)

---

## HTTP/1.1 協議的性能問題

我們得先要了解下 HTTP/1.1 協議存在的性能問題，因為 HTTP/2 協議就是把這些性能問題逐個攻破了。

現在的站點相比以前變化太多了，比如：

- *消息的大小變大了*，從幾 KB 大小的消息，到幾 MB 大小的消息；
- *頁面資源變多了*，從每個頁面不到 10 個的資源，到每頁超 100 多個資源；
- *內容形式變多樣了*，從單純到文本內容，到圖片、視頻、音頻等內容；
- *實時性要求變高了*，對頁面的實時性要求的應用越來越多；

這些變化帶來的最大性能問題就是 **HTTP/1.1 的高延遲**，延遲高必然影響的就是用戶體驗。主要原因如下幾個：

- *延遲難以下降*，雖然現在網絡的「帶寬」相比以前變多了，但是延遲降到一定幅度後，就很難再下降了，說白了就是到達了延遲的下限；
- *併發連接有限*，谷歌瀏覽器最大併發連接數是 6 個，而且每一個連接都要經過 TCP 和 TLS 握手耗時，以及 TCP 慢啟動過程給流量帶來的影響；
- *隊頭阻塞問題*，同一連接只能在完成一個 HTTP 事務（請求和響應）後，才能處理下一個事務；
- *HTTP 頭部巨大且重複*，由於 HTTP 協議是無狀態的，每一個請求都得攜帶 HTTP 頭部，特別是對於有攜帶 Cookie 的頭部，而 Cookie 的大小通常很大；
- *不支持服務器推送消息*，因此當客戶端需要獲取通知時，只能通過定時器不斷地拉取消息，這無疑浪費大量了帶寬和服務器資源。

為瞭解決 HTTP/1.1 性能問題，具體的優化手段你可以看這篇文章「[HTTP/1.1 如何優化？](https://xiaolincoding.com/network/2_http/http_optimize.html)」，這裡我舉例幾個常見的優化手段：

- 將多張小圖合併成一張大圖供瀏覽器 JavaScript 來切割使用，這樣可以將多個請求合併成一個請求，但是帶來了新的問題，當某張小圖片更新了，那麼需要重新請求大圖片，浪費了大量的網絡帶寬；
- 將圖片的二進制數據通過 Base64 編碼後，把編碼數據嵌入到 HTML 或 CSS 文件中，以此來減少網絡請求次數；
- 將多個體積較小的 JavaScript 文件使用 Webpack 等工具打包成一個體積更大的 JavaScript 文件，以一個請求替代了很多個請求，但是帶來的問題，當某個 js 文件變化了，需要重新請求同一個包裡的所有 js 文件；
- 將同一個頁面的資源分散到不同域名，提升併發連接上限，因為瀏覽器通常對同一域名的 HTTP 連接最大隻能是 6 個；


儘管對 HTTP/1.1 協議的優化手段如此之多，但是效果還是不盡人意，因為這些手段都是對 HTTP/1.1 協議的“外部”做優化，**而一些關鍵的地方是沒辦法優化的，比如請求-響應模型、頭部巨大且重複、併發連接耗時、服務器不能主動推送等，要改變這些必須重新設計 HTTP 協議，於是 HTTP/2 就出來了！**


---

## 兼容 HTTP/1.1 

HTTP/2 出來的目的是為了改善 HTTP 的性能。協議升級有一個很重要的地方，就是要**兼容**老版本的協議，否則新協議推廣起來就相當困難，所幸 HTTP/2 做到了兼容 HTTP/1.1。

那麼，HTTP/2 是怎麼做的呢？

第一點，HTTP/2 沒有在 URI 裡引入新的協議名，仍然用「http://」表示明文協議，用「https://」表示加密協議，於是隻需要瀏覽器和服務器在背後自動升級協議，這樣可以讓用戶意識不到協議的升級，很好的實現了協議的平滑升級。

第二點，只在應用層做了改變，還是基於 TCP 協議傳輸，應用層方面為了保持功能上的兼容，HTTP/2 把 HTTP 分解成了「語義」和「語法」兩個部分，「語義」層不做改動，與 HTTP/1.1 完全一致，比如請求方法、狀態碼、頭字段等規則保留不變。

但是，HTTP/2 在「語法」層面做了很多改造，基本改變了 HTTP 報文的傳輸格式。

## 頭部壓縮

HTTP 協議的報文是由「Header + Body」構成的，對於 Body 部分，HTTP/1.1 協議可以使用頭字段 「Content-Encoding」指定 Body 的壓縮方式，比如用 gzip 壓縮，這樣可以節約帶寬，但報文中的另外一部分 Header，是沒有針對它的優化手段。

HTTP/1.1 報文中 Header 部分存在的問題：

- 含很多固定的字段，比如 Cookie、User Agent、Accept 等，這些字段加起來也高達幾百字節甚至上千字節，所以有必要**壓縮**；
- 大量的請求和響應的報文裡有很多字段值都是重複的，這樣會使得大量帶寬被這些冗餘的數據佔用了，所以有必須要**避免重複性**；
- 字段是 ASCII 編碼的，雖然易於人類觀察，但效率低，所以有必要改成**二進制編碼**；

HTTP/2 對 Header 部分做了大改造，把以上的問題都解決了。


HTTP/2 沒使用常見的 gzip 壓縮方式來壓縮頭部，而是開發了 **HPACK** 算法，HPACK 算法主要包含三個組成部分：

- 靜態字典；
- 動態字典；
- Huffman 編碼（壓縮算法）；

客戶端和服務器兩端都會建立和維護「**字典**」，用長度較小的索引號表示重複的字符串，再用 Huffman 編碼壓縮數據，**可達到 50%~90% 的高壓縮率**。

### 靜態表編碼

HTTP/2 為高頻出現在頭部的字符串和字段建立了一張**靜態表**，它是寫入到 HTTP/2 框架裡的，不會變化的，靜態表裡共有 `61` 組，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/靜態表.png)

表中的 `Index` 表示索引（Key），`Header Value` 表示索引對應的  Value，`Header Name` 表示字段的名字，比如 Index 為 2 代表 GET，Index 為 8 代表狀態碼 200。

你可能注意到，表中有的 Index 沒有對應的 Header Value，這是因為這些 Value 並不是固定的而是變化的，這些 Value 都會經過 Huffman 編碼後，才會發送出去。

這麼說有點抽象，我們來看個具體的例子，下面這個 `server` 頭部字段，在 HTTP/1.1 的形式如下：

```
server: nghttpx\r\n
```

算上冒號空格和末尾的`\r\n`，共佔用了 17 字節，**而使用了靜態表和 Huffman 編碼，可以將它壓縮成 8 字節，壓縮率大概 47%**。

我抓了個 HTTP/2 協議的網絡包，你可以從下圖看到，高亮部分就是 `server` 頭部字段，只用了 8 個字節來表示 `server` 頭部數據。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/靜態編碼.png)


根據 RFC7541 規範，如果頭部字段屬於靜態表範圍，並且 Value 是變化，那麼它的 HTTP/2 頭部前 2 位固定為 `01`，所以整個頭部格式如下圖：


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/靜態頭部.png)


HTTP/2 頭部由於基於**二進制編碼**，就不需要冒號空格和末尾的\r\n作為分隔符，於是改用表示字符串長度（Value Length）來分割 Index 和 Value。

接下來，根據這個頭部格式來分析上面抓包的 `server` 頭部的二進制數據。

首先，從靜態表中能查到 `server` 頭部字段的 Index 為 54，二進制為 110110，再加上固定 01，頭部格式第 1 個字節就是 `01110110`，這正是上面抓包標註的紅色部分的二進制數據。        

然後，第二個字節的首個比特位表示 Value 是否經過 Huffman 編碼，剩餘的 7 位表示 Value 的長度，比如這次例子的第二個字節為 `10000110`，首位比特位為 1 就代表 Value 字符串是經過 Huffman 編碼的，經過 Huffman 編碼的 Value 長度為 6。

最後，字符串 `nghttpx` 經過 Huffman 編碼後壓縮成了 6 個字節，Huffman 編碼的原理是將高頻出現的信息用「較短」的編碼表示，從而縮減字符串長度。

於是，在統計大量的 HTTP 頭部後，HTTP/2 根據出現頻率將 ASCII 碼編碼為了 Huffman 編碼表，可以在 RFC7541 文檔找到這張**靜態 Huffman 表**，我就不把表的全部內容列出來了，我只列出字符串 `nghttpx` 中每個字符對應的 Huffman 編碼，如下圖：


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/nghttpx.png)

通過查表後，字符串 `nghttpx` 的 Huffman 編碼在下圖看到，共 6 個字節，每一個字符的 Huffman 編碼，我用相同的顏色將他們對應起來了，最後的 7 位是補位的。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/nghttpx2.png)

最終，`server` 頭部的二進制數據對應的靜態頭部格式如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/靜態頭部2.png)


### 動態表編碼

靜態表只包含了 61 種高頻出現在頭部的字符串，不在靜態表範圍內的頭部字符串就要自行構建**動態表**，它的 Index 從 `62` 起步，會在編碼解碼的時候隨時更新。


比如，第一次發送時頭部中的「`User-Agent` 」字段數據有上百個字節，經過 Huffman 編碼發送出去後，客戶端和服務器雙方都會更新自己的動態表，添加一個新的 Index 號 62。**那麼在下一次發送的時候，就不用重複發這個字段的數據了，只用發 1 個字節的 Index 號就好了，因為雙方都可以根據自己的動態表獲取到字段的數據**。

所以，使得動態表生效有一個前提：**必須同一個連接上，重複傳輸完全相同的 HTTP 頭部**。如果消息字段在 1 個連接上只發送了 1 次，或者重複傳輸時，字段總是略有變化，動態表就無法被充分利用了。

因此，隨著在同一 HTTP/2 連接上發送的報文越來越多，客戶端和服務器雙方的「字典」積累的越來越多，理論上最終每個頭部字段都會變成 1 個字節的 Index，這樣便避免了大量的冗餘數據的傳輸，大大節約了帶寬。

理想很美好，現實很骨感。動態表越大，佔用的內存也就越大，如果佔用了太多內存，是會影響服務器性能的，因此 Web 服務器都會提供類似 `http2_max_requests` 的配置，用於限制一個連接上能夠傳輸的請求數量，避免動態表無限增大，請求數量到達上限後，就會關閉 HTTP/2 連接來釋放內存。

綜上，HTTP/2 頭部的編碼通過「靜態表、動態表、Huffman 編碼」共同完成的。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/頭部編碼.png)

---

## 二進制幀

HTTP/2 厲害的地方在於將 HTTP/1 的文本格式改成二進制格式傳輸數據，極大提高了 HTTP 傳輸效率，而且二進制數據使用位運算能高效解析。

你可以從下圖看到，HTTP/1.1 的響應和 HTTP/2 的區別：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/二進制幀.png)

HTTP/2 把響應報文劃分成了兩類**幀（*Frame*）**，圖中的 HEADERS（首部）和 DATA（消息負載） 是幀的類型，也就是說一條 HTTP 響應，劃分成了兩類幀來傳輸，並且採用二進制來編碼。

比如狀態碼 200 ，在 HTTP/1.1 是用 '2''0''0' 三個字符來表示（二進制：00110010 00110000 00110000），共用了 3 個字節，如下圖

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/%E7%BD%91%E7%BB%9C/http2/http1.png)

在 HTTP/2 對於狀態碼 200 的二進制編碼是 10001000，只用了 1 字節就能表示，相比於 HTTP/1.1 節省了 2 個字節，如下圖：

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/%E7%BD%91%E7%BB%9C/http2/h2c.png)

Header: :status: 200 OK 的編碼內容為：1000 1000，那麼表達的含義是什麼呢？

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/http/index.png)

1. 最前面的 1 標識該 Header 是靜態表中已經存在的 KV。
2. 我們再回顧一下之前的靜態表內容，“:status: 200 OK”其靜態表編碼是 8，即 1000。

因此，整體加起來就是 1000 1000。

HTTP/2 **二進制幀**的結構如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/幀格式.png)

幀頭（Frame Header）很小，只有 9 個字節，幀開頭的前 3 個字節表示幀數據（Frame Playload）的**長度**。

幀長度後面的一個字節是表示**幀的類型**，HTTP/2 總共定義了 10 種類型的幀，一般分為**數據幀**和**控制幀**兩類，如下表格：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/幀類型.png)

幀類型後面的一個字節是**標誌位**，可以保存 8 個標誌位，用於攜帶簡單的控制信息，比如：

- **END_HEADERS** 表示頭數據結束標誌，相當於 HTTP/1 裡頭後的空行（“\r\n”）；
- **END_Stream** 表示單方向數據發送結束，後續不會再有數據幀。
- **PRIORITY** 表示流的優先級；


幀頭的最後 4 個字節是**流標識符**（Stream ID），但最高位被保留不用，只有 31 位可以使用，因此流標識符的最大值是 2^31，大約是 21 億，它的作用是用來標識該 Frame 屬於哪個 Stream，接收方可以根據這個信息從亂序的幀裡找到相同 Stream ID 的幀，從而有序組裝信息。

最後面就是**幀數據**了，它存放的是通過 **HPACK  算法**壓縮過的 HTTP 頭部和包體。

---

## 併發傳輸

知道了 HTTP/2 的幀結構後，我們再來看看它是如何實現**併發傳輸**的。

我們都知道 HTTP/1.1 的實現是基於請求-響應模型的。同一個連接中，HTTP 完成一個事務（請求與響應），才能處理下一個事務，也就是說在發出請求等待響應的過程中，是沒辦法做其他事情的，如果響應遲遲不來，那麼後續的請求是無法發送的，也造成了**隊頭阻塞**的問題。

而 HTTP/2 就很牛逼了，通過 Stream 這個設計，**多個 Stream 複用一條 TCP 連接，達到併發的效果**，解決了 HTTP/1.1 隊頭阻塞的問題，提高了 HTTP 傳輸的吞吐量。

為了理解 HTTP/2 的併發是怎樣實現的，我們先來理解 HTTP/2 中的 Stream、Message、Frame 這 3 個概念。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/stream.png)

你可以從上圖中看到：

- 1 個 TCP 連接包含一個或者多個 Stream，Stream 是 HTTP/2 併發的關鍵技術；
- Stream 裡可以包含 1 個或多個 Message，Message 對應 HTTP/1 中的請求或響應，由 HTTP 頭部和包體構成；
- Message 裡包含一條或者多個 Frame，Frame 是 HTTP/2 最小單位，以二進制壓縮格式存放 HTTP/1 中的內容（頭部和包體）；

因此，我們可以得出個結論：多個 Stream 跑在一條 TCP 連接，同一個 HTTP 請求與響應是跑在同一個 Stream 中，HTTP 消息可以由多個 Frame 構成， 一個 Frame 可以由多個 TCP 報文構成。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/stream2.png)

在 HTTP/2 連接上，**不同 Stream 的幀是可以亂序發送的（因此可以併發不同的 Stream ）**，因為每個幀的頭部會攜帶 Stream ID 信息，所以接收端可以通過 Stream ID 有序組裝成 HTTP 消息，而**同一 Stream 內部的幀必須是嚴格有序的**。

比如下圖，服務端**並行交錯地**發送了兩個響應： Stream 1 和 Stream 3，這兩個 Stream 都是跑在一個 TCP 連接上，客戶端收到後，會根據相同的 Stream ID 有序組裝成 HTTP 消息。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/http/http2多路複用.jpeg)

客戶端和服務器**雙方都可以建立 Stream**，因為服務端可以主動推送資源給客戶端， 客戶端建立的 Stream 必須是奇數號，而服務器建立的 Stream 必須是偶數號。

比如下圖，Stream 1 是客戶端向服務端請求的資源，屬於客戶端建立的 Stream，所以該 Stream 的 ID 是奇數（數字 1）；Stream 2 和 4 都是服務端主動向客戶端推送的資源，屬於服務端建立的 Stream，所以這兩個 Stream 的 ID 是偶數（數字 2 和 4）。

![](https://img-blog.csdnimg.cn/83445581dafe409d8cfd2c573b2781ac.png)

同一個連接中的 Stream ID 是不能複用的，只能順序遞增，所以當 Stream ID 耗盡時，需要發一個控制幀 `GOAWAY`，用來關閉 TCP 連接。 

在 Nginx 中，可以通過 `http2_max_concurrent_Streams` 配置來設置 Stream 的上限，默認是 128 個。

HTTP/2 通過 Stream 實現的併發，比 HTTP/1.1 通過 TCP 連接實現併發要牛逼的多，**因為當 HTTP/2 實現 100 個併發 Stream 時，只需要建立一次 TCP 連接，而 HTTP/1.1 需要建立 100 個 TCP 連接，每個 TCP 連接都要經過 TCP 握手、慢啟動以及 TLS 握手過程，這些都是很耗時的。**

HTTP/2 還可以對每個 Stream 設置不同**優先級**，幀頭中的「標誌位」可以設置優先級，比如客戶端訪問 HTML/CSS 和圖片資源時，希望服務器先傳遞 HTML/CSS，再傳圖片，那麼就可以通過設置 Stream 的優先級來實現，以此提高用戶體驗。

## 服務器主動推送資源

HTTP/1.1 不支持服務器主動推送資源給客戶端，都是由客戶端向服務器發起請求後，才能獲取到服務器響應的資源。

比如，客戶端通過 HTTP/1.1 請求從服務器那獲取到了 HTML 文件，而 HTML 可能還需要依賴 CSS 來渲染頁面，這時客戶端還要再發起獲取 CSS 文件的請求，需要兩次消息往返，如下圖左邊部分：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/push.png)

如上圖右邊部分，在 HTTP/2 中，客戶端在訪問 HTML 時，服務器可以直接主動推送 CSS 文件，減少了消息傳遞的次數。

在 Nginx 中，如果你希望客戶端訪問 /test.html 時，服務器直接推送 /test.css，那麼可以這麼配置：


```nginx
location /test.html { 
  http2_push /test.css; 
}
```

那 HTTP/2 的推送是怎麼實現的？

客戶端發起的請求，必須使用的是奇數號 Stream，服務器主動的推送，使用的是偶數號 Stream。服務器在推送資源時，會通過 `PUSH_PROMISE` 幀傳輸 HTTP 頭部，並通過幀中的 `Promised Stream ID` 字段告知客戶端，接下來會在哪個偶數號 Stream 中發送包體。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/http2/push2.png)

如上圖，在 Stream 1 中通知客戶端 CSS 資源即將到來，然後在 Stream 2 中發送 CSS 資源，注意 Stream 1 和 2 是可以**併發**的。

---

## 總結

HTTP/2 協議其實還有很多內容，比如流控制、流狀態、依賴關係等等。

這次主要介紹了關於 HTTP/2 是如何提升性能的幾個方向，它相比 HTTP/1 大大提高了傳輸效率、吞吐能力。

第一點，對於常見的 HTTP 頭部通過**靜態表和 Huffman 編碼**的方式，將體積壓縮了近一半，而且針對後續的請求頭部，還可以建立**動態表**，將體積壓縮近 90%，大大提高了編碼效率，同時節約了帶寬資源。

不過，動態表並非可以無限增大， 因為動態表是會佔用內存的，動態表越大，內存也越大，容易影響服務器總體的併發能力，因此服務器需要限制 HTTP/2 連接時長或者請求次數。

第二點，**HTTP/2 實現了 Stream 併發**，多個 Stream 只需複用 1 個 TCP 連接，節約了 TCP 和 TLS 握手時間，以及減少了 TCP 慢啟動階段對流量的影響。不同的 Stream ID 可以併發，即使亂序發送幀也沒問題，比如發送 A 請求幀 1 -> B 請求幀 1 -> A 請求幀 2 -> B 請求幀2，但是同一個 Stream 裡的幀必須嚴格有序。

另外，可以根據資源的渲染順序來設置 Stream 的**優先級**，從而提高用戶體驗。

第三點，**服務器支持主動推送資源**，大大提升了消息的傳輸性能，服務器推送資源時，會先發送 PUSH_PROMISE 幀，告訴客戶端接下來在哪個 Stream 發送資源，然後用偶數號 Stream 發送資源給客戶端。

HTTP/2 通過 Stream 的併發能力，解決了 HTTP/1 隊頭阻塞的問題，看似很完美了，但是 HTTP/2 還是存在“隊頭阻塞”的問題，只不過問題不是在 HTTP 這一層面，而是在 TCP 這一層。

**HTTP/2 是基於 TCP 協議來傳輸數據的，TCP 是字節流協議，TCP 層必須保證收到的字節數據是完整且連續的，這樣內核才會將緩衝區裡的數據返回給 HTTP 應用，那麼當「前 1 個字節數據」沒有到達時，後收到的字節數據只能存放在內核緩衝區裡，只有等到這 1 個字節數據到達時，HTTP/2 應用層才能從內核中拿到數據，這就是 HTTP/2 隊頭阻塞問題。**

有沒有什麼解決方案呢？既然是 TCP 協議自身的問題，那乾脆放棄 TCP 協議，轉而使用 UDP 協議作為傳輸層協議，這個大膽的決定，HTTP/3 協議做了！

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/HTTP/27-HTTP3.png)

---

參考資料：

1. https://developers.google.com/web/fundamentals/performance/http2
2. https://http2.akamai.com/demo
3. https://tools.ietf.org/html/rfc7541

---

哈嘍，我是小林，就愛圖解計算機基礎，如果文章對你有幫助，別忘記關注哦！

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)
