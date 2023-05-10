# 4.9 已建立連接的TCP，收到SYN會發生什麼？

大家好，我是小林。

昨晚有位讀者問了我這麼個問題：

![](https://img-blog.csdnimg.cn/ea1c6e0165f04232ab02046132e63d0f.jpg)


大概意思是，一個已經建立的 TCP 連接，客戶端中途宕機了，而服務端此時也沒有數據要發送，一直處於 Established 狀態，客戶端恢復後，向服務端建立連接，此時服務端會怎麼處理？

看過我的圖解網絡的讀者都知道，TCP 連接是由「四元組」唯一確認的。

然後這個場景中，客戶端的 IP、服務端 IP、目的端口並沒有變化，所以這個問題關鍵要看客戶端發送的 SYN 報文中的源端口是否和上一次連接的源端口相同。

**1. 客戶端的 SYN 報文裡的端口號與歷史連接不相同**

如果客戶端恢復後發送的 SYN 報文中的源端口號跟上一次連接的源端口號不一樣，此時服務端會認為是新的連接要建立，於是就會通過三次握手來建立新的連接。

那舊連接裡處於 Established 狀態的服務端最後會怎麼樣呢？

如果服務端發送了數據包給客戶端，由於客戶端的連接已經被關閉了，此時客戶的內核就會回 RST 報文，服務端收到後就會釋放連接。

如果服務端一直沒有發送數據包給客戶端，在超過一段時間後，TCP 保活機制就會啟動，檢測到客戶端沒有存活後，接著服務端就會釋放掉該連接。

**2. 客戶端的 SYN 報文裡的端口號與歷史連接相同**

如果客戶端恢復後，發送的 SYN 報文中的源端口號跟上一次連接的源端口號一樣，也就是處於 Established 狀態的服務端收到了這個 SYN 報文。

大家覺得服務端此時會做什麼處理呢？
- 丟掉 SYN 報文？
- 回覆 RST 報文？
- 回覆 ACK 報文？

剛開始我看到這個問題的時候，也是沒有思路的，因為之前沒關注過，然後這個問題不能靠猜，所以我就看了 RFC 規範和看了 Linux 內核源碼，最終知道了答案。

我不賣關子，先直接說答案。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/est_syn.png)

**處於 Established 狀態的服務端，如果收到了客戶端的 SYN 報文（注意此時的 SYN 報文其實是亂序的，因為 SYN 報文的初始化序列號其實是一個隨機數），會回覆一個攜帶了正確序列號和確認號的 ACK 報文，這個 ACK 被稱之為 Challenge ACK。**

**接著，客戶端收到這個 Challenge ACK，發現確認號（ack num）並不是自己期望收到的，於是就會回 RST 報文，服務端收到後，就會釋放掉該連接。**

## RFC 文檔解釋

RFC 793 文檔裡的第 34 頁裡，有說到這個例子。

![](https://img-blog.csdnimg.cn/873ad18443c040708c415bab6592ae41.png)

原文的解釋我也貼出來給大家看看。

- When the SYN arrives at line 3, TCP B, being in a synchronized state,
and the incoming segment outside the window, responds with an
acknowledgment indicating what sequence it next expects to hear (ACK
100).
- TCP A sees that this segment does not acknowledge anything it
sent and, being unsynchronized, sends a reset (RST) because it has
detected a half-open connection.
- TCP B aborts at line 5.  
- TCP A willcontinue to try to Established the connection;

我就不瞎翻譯了，意思和我在前面用中文說的解釋差不多。

## 源碼分析
處於 Established 狀態的服務端如果收到了客戶端的 SYN 報文時，內核會調用這些函數：

```csharp
tcp_v4_rcv
  -> tcp_v4_do_rcv
    -> tcp_rcv_Establisheded
      -> tcp_validate_incoming
        -> tcp_send_ack
```


我們只關注 tcp_validate_incoming 函數是怎麼處理 SYN 報文的，精簡後的代碼如下：

![](https://img-blog.csdnimg.cn/780bc02c8fa940c0a320a5916b216c21.png)

從上面的代碼實現可以看到，處於 Established 狀態的服務端，在收到報文後，首先會判斷序列號是否在窗口內，如果不在，則看看 RST 標記有沒有被設置，如果有就會丟掉。然後如果沒有 RST 標誌，就會判斷是否有 SYN 標記，如果有 SYN 標記就會跳轉到 syn_challenge 標籤，然後執行 tcp_send_challenge_ack 函數。

tcp_send_challenge_ack 函數裡就會調用 tcp_send_ack 函數來回復一個攜帶了正確序列號和確認號的 ACK 報文。

## 如何關閉一個 TCP 連接？

這裡問題大家這麼一個問題，如何關閉一個 TCP 連接？

可能大家第一反應是「殺掉進程」不就行了嗎？

是的，這個是最粗暴的方式，殺掉客戶端進程和服務端進程影響的範圍會有所不同：
- 在客戶端殺掉進程的話，就會發送 FIN 報文，來斷開這個客戶端進程與服務端建立的所有 TCP 連接，這種方式影響範圍只有這個客戶端進程所建立的連接，而其他客戶端或進程不會受影響。
- 而在服務端殺掉進程影響就大了，此時所有的 TCP 連接都會被關閉，服務端無法繼續提供訪問服務。

所以，關閉進程的方式並不可取，最好的方式要精細到關閉某一條 TCP 連接。

有的小夥伴可能會說，偽造一個四元組相同的 RST 報文不就行了？

這個思路很好，但是不要忘了還有個序列號的問題，你偽造的 RST 報文的序列號一定能被對方接受嗎？

如果 RST 報文的序列號不是對方期望收到的序列號，這個 RST 報文會被對方丟棄的，就達不到關閉的連接的效果。

舉個例子，下面這個場景，客戶端發送了一個長度為 100 的 TCP 數據報文，服務端收到後響應了 ACK 報文，表示收到了這個 TCP 數據報文。**服務端響應的這個 ACK 報文中的確認號（ack = x + 100）就是表明服務端下一次期望收到的序列號是 x + 100**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/rst合法.png)

所以，**要偽造一個能關閉 TCP 連接的 RST 報文，必須同時滿足「四元組相同」和「序列號是對方期望的」這兩個條件。**

直接偽造符合預期的序列號是比較困難，因為如果一個正在傳輸數據的 TCP 連接，序列號都是時刻都在變化，因此很難剛好偽造一個正確序列號的 RST 報文。

### killcx 的工具

辦法還是有的，**我們可以偽造一個四元組相同的 SYN 報文，來拿到“合法”的序列號！**

正如我們最開始學到的，如果處於 Established 狀態的服務端，收到四元組相同的 SYN 報文後，**會回覆一個 Challenge ACK，這個 ACK 報文裡的「確認號」，正好是服務端下一次想要接收的序列號，說白了，就是可以通過這一步拿到服務端下一次預期接收的序列號。**

**然後用這個確認號作為 RST 報文的序列號，發送給服務端，此時服務端會認為這個 RST 報文裡的序列號是合法的，於是就會釋放連接！**

在 Linux 上有個叫 killcx 的工具，就是基於上面這樣的方式實現的，它會主動發送 SYN 包獲取 SEQ/ACK 號，然後利用 SEQ/ACK 號偽造兩個 RST 報文分別發給客戶端和服務端，這樣雙方的 TCP 連接都會被釋放，這種方式活躍和非活躍的 TCP 連接都可以殺掉。


killcx 的工具使用方式也很簡單，如果在服務端執行 killcx 工具，只需指明客戶端的 IP 和端口號，如果在客戶端執行 killcx 工具，則就指明服務端的  IP 和端口號。

```csharp
./killcx <IP地址>:<端口號>
```
killcx 工具的工作原理，如下圖，下圖是在客戶端執行 killcx 工具。

![](https://img-blog.csdnimg.cn/95592346a9a747819cd27741a660213c.png)

它偽造客戶端發送 SYN 報文，服務端收到後就會回覆一個攜帶了正確「序列號和確認號」的 ACK 報文（Challenge ACK），然後就可以利用這個 ACK 報文裡面的信息，偽造兩個 RST 報文：
- 用 Challenge ACK 裡的確認號偽造 RST 報文發送給服務端，服務端收到 RST 報文後就會釋放連接。
- 用 Challenge ACK 裡的序列號偽造 RST 報文發送給客戶端，客戶端收到 RST 也會釋放連接。

正是通過這樣的方式，成功將一個 TCP 連接關閉了！

這裡給大家貼一個使用 killcx 工具關閉連接的抓包圖，大家多看看序列號和確認號的變化。

![](https://img-blog.csdnimg.cn/71cbefee5ab741018386b6a37f492614.png?)

所以，以後抓包中，如果莫名奇妙出現一個 SYN 包，有可能對方接下來想要對你發起的 RST 攻擊，直接將你的 TCP 連接斷開！

怎麼樣，很巧妙吧！

### tcpkill 的工具

除了 killcx 工具能關閉 TCP 連接，還有 tcpkill 工具也可以做到。

這兩個工具都是通過偽造 RST 報文來關閉指定的 TCP 連接，但是它們拿到正確的序列號的實現方式是不同的。

- tcpkill 工具是在雙方進行 TCP 通信時，拿到對方下一次期望收到的序列號，然後將序列號填充到偽造的 RST 報文，並將其發送給對方，達到關閉 TCP 連接的效果。
- killcx 工具是主動發送一個 SYN 報文，對方收到後會回覆一個攜帶了正確序列號和確認號的 ACK 報文，這個 ACK 被稱之為 Challenge ACK，這時就可以拿到對方下一次期望收到的序列號，然後將序列號填充到偽造的 RST 報文，並將其發送給對方，達到關閉 TCP 連接的效果。

可以看到， 這兩個工具在獲取對方下一次期望收到的序列號的方式是不同的。

tcpkill 工具屬於被動獲取，就是在雙方進行 TCP 通信的時候，才能獲取到正確的序列號，很顯然**這種方式無法關閉非活躍的 TCP 連接**，只能用於關閉活躍的 TCP 連接。因為如果這條 TCP 連接一直沒有任何數據傳輸，則就永遠獲取不到正確的序列號。

killcx 工具則是屬於主動獲取，它是主動發送一個 SYN 報文，通過對方回覆的 Challenge ACK 來獲取正確的序列號，所以這種方式**無論 TCP 連接是否活躍，都可以關閉**。

接下來，我就用這 tcpkill 工具來做個實驗。

在這裡， 我用 nc 工具來模擬一個 TCP 服務端，監聽 8888 端口。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill1.png)

接著，在客戶端機子上，用 nc 工具模擬一個 TCP 客戶端，連接我們剛才啟動的服務端，並且指定了客戶端的端口為 11111。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill2.png)

這時候， 服務端就可以看到這條 TCP 連接了。

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill3.png)

注意，我這臺服務端的公網 IP 地址是 121.43.173.240，私網 IP 地址是 172.19.11.21，在服務端通過 netstat 命令查看 TCP 連接的時候，則會將服務端的地址顯示成私網 IP 地址 。至此，我們前期工作就做好了。

接下來，我們在服務端執行 tcpkill 工具，來關閉這條 TCP 連接，看看會發生什麼？

在這裡，我指定了要關閉的客戶端 IP 為 114.132.166.90 和端口為 11111 的 TCP 連接。

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill4.png)

可以看到，tcpkill 工具阻塞中，沒有任何輸出，而且此時的 TCP 連接還是存在的，並沒有被幹掉。

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill5.png)

為什麼 TCP 連接沒用被幹掉？

因為在執行 tcpkill 工具後，這條 TCP 連接並沒有傳輸任何數據，而 tcpkill 工具是需要攔截雙方的 TCP 通信，才能獲取到正確的序列號，從而才能偽裝出正確的序列號的 RST 報文。

所以，從這裡也說明瞭，**tcpkill 工具不適合關閉非活躍的 TCP 連接**。

接下來，我們嘗試在客戶端發送一個數據。

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill8.png)

可以看到，在發送了「hi」數據後，客戶端就斷開了，並且錯誤提示連接被對方關閉了。

此時，服務端已經查看不到剛才那條 TCP 連接了。

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill7.png)

然後，我們在服務端看看 tcpkill 工具輸出的信息。

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill8.png)

可以看到， **tcpkill 工具給服務端和客戶端都發送了偽造的 RST 報文，從而達到關閉一條 TCP 連接的效果**。

到這裡我們知道了， 運行 tcpkill 工具後，只有目標連接有新 TCP 包發送/接收的時候，才能關閉一條 TCP 連接。因此，**tcpkill 只適合關閉活躍的 TCP 連接，不適合用來關閉非活躍的 TCP 連接**。

上面的實驗過程，我也抓了數據包，流程如下：

![圖片](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/tcpkill/tcpkill9.png)

最後一個 RST 報文就是 tcpkill 工具偽造的 RST 報文。

## 總結

要偽造一個能關閉 TCP 連接的 RST 報文，必須同時滿足「四元組相同」和「序列號是對方期望的」這兩個條件。

今天給大家介紹了兩種關閉 TCP 連接的工具：tcpkill 和 killcx 工具。

這兩種工具都是通過偽造 RST 報文來關閉 TCP 連接的，但是它們獲取「對方下一次期望收到的序列號的方式是不同的，也正因此，造就了這兩個工具的應用場景有區別。

- tcpkill 工具只能用來關閉活躍的 TCP 連接，無法關閉非活躍的 TCP 連接，因為 tcpkill 工具是等雙方進行 TCP 通信後，才去獲取正確的序列號，如果這條 TCP 連接一直沒有任何數據傳輸，則就永遠獲取不到正確的序列號。
- killcx 工具可以用來關閉活躍和非活躍的 TCP 連接，因為 killcx 工具是主動發送 SYN 報文，這時對方就會回覆  Challenge ACK ，然後  killcx 工具就能從這個 ACK 獲取到正確的序列號。

完！

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)