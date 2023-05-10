# 4.15 TCP Keepalive 和 HTTP Keep-Alive 是一個東西嗎？

大家好，我是小林。

之前有讀者問了我這麼個問題：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/20210715090027883.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


大致問題是，**TCP 的 Keepalive 和 HTTP 的 Keep-Alive 是一個東西嗎？**

這是個好問題，應該有不少人都會搞混，因為這兩個東西看上去太像了，很容易誤以為是同一個東西。

事實上，**這兩個完全是兩樣不同東西**，實現的層面也不同：
- HTTP 的 Keep-Alive，是由**應用層（用戶態）** 實現的，稱為 HTTP 長連接；
- TCP 的 Keepalive，是由 **TCP 層（內核態）** 實現的，稱為 TCP 保活機制；

接下來，分別說說它們。

## HTTP 的 Keep-Alive

HTTP 協議採用的是「請求-應答」的模式，也就是客戶端發起了請求，服務端才會返回響應，一來一回這樣子。

![請求-應答](https://img-blog.csdnimg.cn/img_convert/6c062074058f40ae65ed722e2d082a90.png)


由於 HTTP 是基於 TCP 傳輸協議實現的，客戶端與服務端要進行 HTTP 通信前，需要先建立 TCP 連接，然後客戶端發送 HTTP  請求，服務端收到後就返回響應，至此「請求-應答」的模式就完成了，隨後就會釋放 TCP 連接。

![一個 HTTP 請求](https://img-blog.csdnimg.cn/img_convert/9acbaebbbe07cc870858a350052d9c87.png)


如果每次請求都要經歷這樣的過程：建立 TCP -> 請求資源 -> 響應資源 -> 釋放連接，那麼此方式就是 **HTTP 短連接**，如下圖：


![HTTP 短連接](https://img-blog.csdnimg.cn/img_convert/d6f6757c02e3afbf113d1048c937f8ee.png)


這樣實在太累人了，一次連接只能請求一次資源。

能不能在第一個 HTTP 請求完後，先不斷開 TCP 連接，讓後續的 HTTP 請求繼續使用此連接？

當然可以，HTTP 的 Keep-Alive 就是實現了這個功能，可以使用同一個 TCP 連接來發送和接收多個 HTTP 請求/應答，避免了連接建立和釋放的開銷，這個方法稱為 **HTTP 長連接**。

![HTTP 長連接](https://img-blog.csdnimg.cn/img_convert/d2b20d1cc03936332adb2a68512eb167.png)

HTTP 長連接的特點是，只要任意一端沒有明確提出斷開連接，則保持 TCP 連接狀態。

怎麼才能使用 HTTP 的 Keep-Alive 功能？

在 HTTP 1.0 中默認是關閉的，如果瀏覽器要開啟 Keep-Alive，它必須在請求的包頭中添加：


```
Connection: Keep-Alive
```

然後當服務器收到請求，作出迴應的時候，它也添加一個頭在響應中：

```
Connection: Keep-Alive
```

這樣做，連接就不會中斷，而是保持連接。當客戶端發送另一個請求時，它會使用同一個連接。這一直繼續到客戶端或服務器端提出斷開連接。

**從 HTTP 1.1 開始， 就默認是開啟了 Keep-Alive**，如果要關閉 Keep-Alive，需要在 HTTP 請求的包頭裡添加：

```
Connection:close
```

現在大多數瀏覽器都默認是使用 HTTP/1.1，所以 Keep-Alive 都是默認打開的。一旦客戶端和服務端達成協議，那麼長連接就建立好了。

HTTP 長連接不僅僅減少了 TCP 連接資源的開銷，而且這給 **HTTP 流水線**技術提供了可實現的基礎。

所謂的 HTTP 流水線，是**客戶端可以先一次性發送多個請求，而在發送過程中不需先等待服務器的迴應**，可以減少整體的響應時間。

舉例來說，客戶端需要請求兩個資源。以前的做法是，在同一個 TCP 連接裡面，先發送 A 請求，然後等待服務器做出迴應，收到後再發出 B 請求。HTTP 流水線機制則允許客戶端同時發出 A 請求和 B 請求。

![右邊為 HTTP 流水線機制](https://img-blog.csdnimg.cn/img_convert/b3fa409edd8aa1dea830af2a69fc8a31.png)

但是**服務器還是按照順序響應**，先回應 A 請求，完成後再回應 B 請求。

而且要等服務器響應完客戶端第一批發送的請求後，客戶端才能發出下一批的請求，也就說如果服務器響應的過程發生了阻塞，那麼客戶端就無法發出下一批的請求，此時就造成了「隊頭阻塞」的問題。

可能有的同學會問，如果使用了 HTTP 長連接，如果客戶端完成一個 HTTP 請求後，就不再發起新的請求，此時這個 TCP 連接一直佔用著不是挺浪費資源的嗎？

對沒錯，所以為了避免資源浪費的情況，web 服務軟件一般都會提供 `keepalive_timeout` 參數，用來指定 HTTP 長連接的超時時間。

比如設置了 HTTP 長連接的超時時間是 60 秒，web 服務軟件就會**啟動一個定時器**，如果客戶端在完後一個 HTTP 請求後，在 60 秒內都沒有再發起新的請求，**定時器的時間一到，就會觸發回調函數來釋放該連接。**

![HTTP 長連接超時](https://img-blog.csdnimg.cn/img_convert/7e995ecb2e42941342f97256707496c9.png)

## TCP 的 Keepalive

TCP 的 Keepalive 這東西其實就是 **TCP 的保活機制**，它的工作原理我之前的文章寫過，這裡就直接貼下以前的內容。


如果兩端的 TCP 連接一直沒有數據交互，達到了觸發 TCP 保活機制的條件，那麼內核裡的 TCP 協議棧就會發送探測報文。
- 如果對端程序是正常工作的。當 TCP 保活的探測報文發送給對端, 對端會正常響應，這樣 **TCP 保活時間會被重置**，等待下一個 TCP 保活時間的到來。
- 如果對端主機宕機（*注意不是進程崩潰，進程崩潰後操作系統在回收進程資源的時候，會發送 FIN 報文，而主機宕機則是無法感知的，所以需要 TCP 保活機制來探測對方是不是發生了主機宕機*），或對端由於其他原因導致報文不可達。當 TCP 保活的探測報文發送給對端後，石沉大海，沒有響應，連續幾次，達到保活探測次數後，**TCP 會報告該 TCP 連接已經死亡**。


所以，TCP 保活機制可以在雙方沒有數據交互的情況，通過探測報文，來確定對方的 TCP 連接是否存活，這個工作是在內核完成的。

![TCP 保活機制](https://img-blog.csdnimg.cn/img_convert/87e138ae9f2438c8f4e2c9c46ec40b95.png)


注意，應用程序若想使用 TCP 保活機制需要通過 socket 接口設置 `SO_KEEPALIVE` 選項才能夠生效，如果沒有設置，那麼就無法使用 TCP 保活機制。


## 總結

HTTP 的 Keep-Alive 也叫 HTTP 長連接，該功能是由「應用程序」實現的，可以使得用同一個 TCP 連接來發送和接收多個 HTTP 請求/應答，減少了 HTTP 短連接帶來的多次 TCP 連接建立和釋放的開銷。


TCP 的 Keepalive 也叫 TCP 保活機制，該功能是由「內核」實現的，當客戶端和服務端長達一定時間沒有進行數據交互時，內核為了確保該連接是否還有效，就會發送探測報文，來檢測對方是否還在線，然後來決定是否要關閉該連接。


---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)