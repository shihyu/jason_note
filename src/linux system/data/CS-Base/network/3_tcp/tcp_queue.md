# 4.4 TCP 半連接隊列和全連接隊列

網上許多博客針對增大 TCP 半連接隊列和全連接隊列的方式如下：

- 增大 TCP 半連接隊列的方式是增大 /proc/sys/net/ipv4/tcp_max_syn_backlog；
- 增大 TCP 全連接隊列的方式是增大 listen() 函數中的 backlog；

這裡先跟大家說下，**上面的方式都是不準確的。**

> “你怎麼知道不準確？”

很簡單呀，因為我做了實驗和看了 TCP 協議棧的內核源碼，發現要增大這兩個隊列長度，不是簡簡單單增大某一個參數就可以的。

接下來，就會以**實戰 + 源碼分析，帶大家解密 TCP 半連接隊列和全連接隊列。**

> “源碼分析，那不是勸退嗎？我們搞 Java 的看不懂呀”

放心，本文的源碼分析不會涉及很深的知識，因為都被我刪減了，你只需要會條件判斷語句 if、左移右移操作符、加減法等基本語法，就可以看懂。

另外，不僅有源碼分析，還會介紹 Linux 排查半連接隊列和全連接隊列的命令。

> “哦？似乎很有看頭，那我姑且看一下吧！”

行，沒有被勸退的小夥伴，值得鼓勵，下面這圖是本文的提綱：

![本文提綱](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/2.jpg)
    

---


## 什麼是 TCP 半連接隊列和全連接隊列？

在 TCP 三次握手的時候，Linux 內核會維護兩個隊列，分別是：

- 半連接隊列，也稱 SYN 隊列；
- 全連接隊列，也稱 accept 隊列；

服務端收到客戶端發起的 SYN 請求後，**內核會把該連接存儲到半連接隊列**，並向客戶端響應 SYN+ACK，接著客戶端會返回 ACK，服務端收到第三次握手的 ACK 後，**內核會把連接從半連接隊列移除，然後創建新的完全的連接，並將其添加到 accept 隊列，等待進程調用 accept 函數時把連接取出來。**

![半連接隊列與全連接隊列](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/3.jpg)


不管是半連接隊列還是全連接隊列，都有最大長度限制，超過限制時，內核會直接丟棄，或返回 RST 包。

---

## 實戰 - TCP 全連接隊列溢出

> 如何知道應用程序的 TCP 全連接隊列大小？

在服務端可以使用 `ss` 命令，來查看 TCP 全連接隊列的情況：

但需要注意的是 `ss` 命令獲取的 `Recv-Q/Send-Q` 在「LISTEN 狀態」和「非 LISTEN 狀態」所表達的含義是不同的。從下面的內核代碼可以看出區別：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/4.jpg)


在「LISTEN 狀態」時，`Recv-Q/Send-Q` 表示的含義如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/5.jpg)

- Recv-Q：當前全連接隊列的大小，也就是當前已完成三次握手並等待服務端 `accept()` 的 TCP 連接；
- Send-Q：當前全連接最大隊列長度，上面的輸出結果說明監聽 8088 端口的 TCP 服務，最大全連接長度為 128；


在「非 LISTEN 狀態」時，`Recv-Q/Send-Q` 表示的含義如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/6.jpg)

- Recv-Q：已收到但未被應用進程讀取的字節數；
- Send-Q：已發送但未收到確認的字節數；


> 如何模擬 TCP 全連接隊列溢出的場景？


![測試環境](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/7.jpg)

實驗環境：

- 客戶端和服務端都是 CentOs 6.5 ，Linux 內核版本 2.6.32
- 服務端 IP 192.168.3.200，客戶端 IP 192.168.3.100 
- 服務端是 Nginx 服務，端口為 8088

這裡先介紹下 `wrk` 工具，它是一款簡單的 HTTP 壓測工具，它能夠在單機多核 CPU 的條件下，使用系統自帶的高性能 I/O 機制，通過多線程和事件模式，對目標機器產生大量的負載。

本次模擬實驗就使用 `wrk` 工具來壓力測試服務端，發起大量的請求，一起看看服務端 TCP 全連接隊列滿了會發生什麼？有什麼觀察指標？

客戶端執行 `wrk` 命令對服務端發起壓力測試，併發 3 萬個連接：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/8.jpg)


在服務端可以使用 `ss` 命令，來查看當前 TCP 全連接隊列的情況：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/9.jpg)

其間共執行了兩次 ss 命令，從上面的輸出結果，可以發現當前 TCP 全連接隊列上升到了 129 大小，超過了最大 TCP 全連接隊列。

**當超過了 TCP 最大全連接隊列，服務端則會丟掉後續進來的 TCP 連接**，丟掉的 TCP 連接的個數會被統計起來，我們可以使用 netstat -s 命令來查看：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/10.jpg)

上面看到的 41150 times ，表示全連接隊列溢出的次數，注意這個是累計值。可以隔幾秒鐘執行下，如果這個數字一直在增加的話肯定全連接隊列偶爾滿了。

從上面的模擬結果，可以得知，**當服務端併發處理大量請求時，如果 TCP 全連接隊列過小，就容易溢出。發生 TCP 全連接隊溢出的時候，後續的請求就會被丟棄，這樣就會出現服務端請求數量上不去的現象。**

![全連接隊列溢出](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/11.jpg)

> Linux 有個參數可以指定當 TCP 全連接隊列滿了會使用什麼策略來回應客戶端。

實際上，丟棄連接只是 Linux 的默認行為，我們還可以選擇向客戶端發送 RST 復位報文，告訴客戶端連接已經建立失敗。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/12.jpg)

tcp_abort_on_overflow 共有兩個值分別是 0 和 1，其分別表示：

- 0 ：如果全連接隊列滿了，那麼 server 扔掉 client  發過來的 ack ；
- 1 ：如果全連接隊列滿了，server 發送一個 `reset` 包給 client，表示廢掉這個握手過程和這個連接；

如果要想知道客戶端連接不上服務端，是不是服務端 TCP 全連接隊列滿的原因，那麼可以把 tcp_abort_on_overflow 設置為 1，這時如果在客戶端異常中可以看到很多 `connection reset by peer` 的錯誤，那麼就可以證明是由於服務端 TCP 全連接隊列溢出的問題。

通常情況下，應當把 tcp_abort_on_overflow 設置為 0，因為這樣更有利於應對突發流量。

舉個例子，當 TCP 全連接隊列滿導致服務器丟掉了 ACK，與此同時，客戶端的連接狀態卻是 ESTABLISHED，進程就在建立好的連接上發送請求。只要服務器沒有為請求回覆 ACK，請求就會被多次**重發**。如果服務器上的進程只是**短暫的繁忙造成 accept 隊列滿，那麼當 TCP 全連接隊列有空位時，再次接收到的請求報文由於含有 ACK，仍然會觸發服務器端成功建立連接。**

所以，tcp_abort_on_overflow 設為 0 可以提高連接建立的成功率，只有你非常肯定 TCP 全連接隊列會長期溢出時，才能設置為 1 以儘快通知客戶端。


> 如何增大 TCP 全連接隊列呢？

是的，當發現 TCP 全連接隊列發生溢出的時候，我們就需要增大該隊列的大小，以便可以應對客戶端大量的請求。

**TCP 全連接隊列的最大值取決於 somaxconn 和 backlog 之間的最小值，也就是 min(somaxconn, backlog)**。從下面的 Linux 內核代碼可以得知：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/13.jpg)


- `somaxconn` 是 Linux 內核的參數，默認值是 128，可以通過 ` /proc/sys/net/core/somaxconn` 來設置其值；
- `backlog` 是 `listen(int sockfd, int backlog)` 函數中的 backlog 大小，Nginx 默認值是 511，可以通過修改配置文件設置其長度；

前面模擬測試中，我的測試環境：

- somaxconn 是默認值 128；
- Nginx 的 backlog 是默認值 511

所以測試環境的 TCP 全連接隊列最大值為 min(128, 511)，也就是 `128`，可以執行 `ss` 命令查看：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/14.jpg)


現在我們重新壓測，把 TCP 全連接隊列**搞大**，把 `somaxconn` 設置成 5000：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/15.jpg)

接著把 Nginx 的 backlog 也同樣設置成 5000：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/16.jpg)

最後要重啟 Nginx 服務，因為只有重新調用 `listen()` 函數 TCP 全連接隊列才會重新初始化。

重啟完後 Nginx 服務後，服務端執行 ss 命令，查看 TCP 全連接隊列大小：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/17.jpg)

從執行結果，可以發現 TCP 全連接最大值為 5000。

> 增大 TCP 全連接隊列後，繼續壓測

客戶端同樣以 3 萬個連接併發發送請求給服務端：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/18.jpg)

服務端執行 `ss` 命令，查看 TCP 全連接隊列使用情況：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/19.jpg)

從上面的執行結果，可以發現全連接隊列使用增長的很快，但是一直都沒有超過最大值，所以就不會溢出，那麼 `netstat -s` 就不會有 TCP 全連接隊列溢出個數的顯示：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/20.jpg)

說明 TCP 全連接隊列最大值從 128 增大到 5000 後，服務端抗住了 3 萬連接併發請求，也沒有發生全連接隊列溢出的現象了。

**如果持續不斷地有連接因為 TCP 全連接隊列溢出被丟棄，就應該調大 backlog 以及 somaxconn 參數。**

---

## 實戰 - TCP 半連接隊列溢出

> 如何查看 TCP 半連接隊列長度？

很遺憾，TCP 半連接隊列長度的長度，沒有像全連接隊列那樣可以用 ss 命令查看。

但是我們可以抓住 TCP 半連接的特點，就是服務端處於 `SYN_RECV` 狀態的 TCP 連接，就是 TCP 半連接隊列。

於是，我們可以使用如下命令計算當前 TCP 半連接隊列長度：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/21.jpg)

> 如何模擬 TCP 半連接隊列溢出場景？

模擬 TCP 半連接溢出場景不難，實際上就是對服務端一直髮送 TCP SYN 包，但是不回第三次握手 ACK，這樣就會使得服務端有大量的處於 `SYN_RECV` 狀態的 TCP 連接。

這其實也就是所謂的 SYN 洪泛、SYN 攻擊、DDos 攻擊。

![測試環境](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/22.jpg)

實驗環境：

- 客戶端和服務端都是 CentOs 6.5 ，Linux 內核版本 2.6.32
- 服務端 IP 192.168.3.200，客戶端 IP 192.168.3.100 
- 服務端是 Nginx 服務，端口為 8088

注意：本次模擬實驗是沒有開啟 tcp_syncookies，關於 tcp_syncookies 的作用，後續會說明。

本次實驗使用 `hping3` 工具模擬 SYN 攻擊：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/23.jpg)

當服務端受到 SYN 攻擊後，連接服務端 ssh 就會斷開了，無法再連上。只能在服務端主機上執行查看當前 TCP 半連接隊列大小：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/24.jpg)

同時，還可以通過 netstat -s 觀察半連接隊列溢出的情況：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/25.jpg)

上面輸出的數值是**累計值**，表示共有多少個 TCP 連接因為半連接隊列溢出而被丟棄。**隔幾秒執行幾次，如果有上升的趨勢，說明當前存在半連接隊列溢出的現象**。

> 大部分人都說 tcp_max_syn_backlog 是指定半連接隊列的大小，是真的嗎？

很遺憾，半連接隊列的大小並不單單隻跟 `tcp_max_syn_backlog` 有關係。

上面模擬 SYN 攻擊場景時，服務端的 tcp_max_syn_backlog 的默認值如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/26.jpg)

但是在測試的時候發現，服務端最多隻有 256 個半連接隊列，而不是 512，所以**半連接隊列的最大長度不一定由 tcp_max_syn_backlog 值決定的**。

> 接下來，走進 Linux 內核的源碼，來分析 TCP 半連接隊列的最大值是如何決定的。

TCP 第一次握手（收到 SYN 包）的 Linux 內核代碼如下，其中縮減了大量的代碼，只需要重點關注 TCP 半連接隊列溢出的處理邏輯：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/27.jpg)

從源碼中，我可以得出共有三個條件因隊列長度的關係而被丟棄的：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/28.jpg)

1. **如果半連接隊列滿了，並且沒有開啟 tcp_syncookies，則會丟棄；**
2. **若全連接隊列滿了，且沒有重傳 SYN+ACK 包的連接請求多於 1 個，則會丟棄；**
3. **如果沒有開啟 tcp_syncookies，並且 max_syn_backlog 減去 當前半連接隊列長度小於 (max_syn_backlog >> 2)，則會丟棄；**

關於 tcp_syncookies 的設置，後面在詳細說明，可以先給大家說一下，開啟 tcp_syncookies 是緩解 SYN 攻擊其中一個手段。

接下來，我們繼續跟一下檢測半連接隊列是否滿的函數 inet_csk_reqsk_queue_is_full 和 檢測全連接隊列是否滿的函數 sk_acceptq_is_full ：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/29.jpg)

從上面源碼，可以得知：

- **全**連接隊列的最大值是 `sk_max_ack_backlog` 變量，sk_max_ack_backlog 實際上是在 listen() 源碼裡指定的，也就是 **min(somaxconn, backlog)**；
- **半**連接隊列的最大值是 `max_qlen_log` 變量，max_qlen_log 是在哪指定的呢？現在暫時還不知道，我們繼續跟進；

我們繼續跟進代碼，看一下是哪裡初始化了半連接隊列的最大值 max_qlen_log：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/30.jpg)

從上面的代碼中，我們可以算出 max_qlen_log 是 8，於是代入到 檢測半連接隊列是否滿的函數 reqsk_queue_is_full ：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/31.jpg)

也就是 `qlen >> 8` 什麼時候為 1 就代表半連接隊列滿了。這計算這不難，很明顯是當 qlen 為 256 時，`256 >> 8 = 1`。

至此，總算知道為什麼上面模擬測試 SYN 攻擊的時候，服務端處於 `SYN_RECV` 連接最大隻有 256 個。

可見，**半連接隊列最大值不是單單由 max_syn_backlog 決定，還跟 somaxconn 和 backlog 有關係。**

在 Linux 2.6.32 內核版本，它們之間的關係，總體可以概況為：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/32.jpg)

- 當 max_syn_backlog > min(somaxconn, backlog) 時， 半連接隊列最大值 max_qlen_log = min(somaxconn, backlog) * 2;
- 當 max_syn_backlog < min(somaxconn, backlog) 時， 半連接隊列最大值 max_qlen_log = max_syn_backlog * 2;


> 半連接隊列最大值 max_qlen_log 就表示服務端處於 SYN_RECV 狀態的最大個數嗎？

依然很遺憾，並不是。

max_qlen_log 是**理論**半連接隊列最大值，並不一定代表服務端處於 SYN_RECV 狀態的最大個數。

在前面我們在分析 TCP 第一次握手（收到 SYN 包）時會被丟棄的三種條件：

1. 如果半連接隊列滿了，並且沒有開啟 tcp_syncookies，則會丟棄；
2. 若全連接隊列滿了，且沒有重傳 SYN+ACK 包的連接請求多於 1 個，則會丟棄；
3. **如果沒有開啟 tcp_syncookies，並且 max_syn_backlog 減去 當前半連接隊列長度小於 (max_syn_backlog >> 2)，則會丟棄；**

假設條件 1 當前半連接隊列的長度 「沒有超過」理論的半連接隊列最大值  max_qlen_log，那麼如果條件 3 成立，則依然會丟棄 SYN 包，也就會使得服務端處於 SYN_RECV 狀態的最大個數不會是理論值 max_qlen_log。

似乎很難理解，我們繼續接著做實驗，實驗見真知。

服務端環境如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/33.jpg)

配置完後，服務端要重啟 Nginx，因為全連接隊列最大值和半連接隊列最大值是在 listen() 函數初始化。

根據前面的源碼分析，我們可以計算出半連接隊列 max_qlen_log 的最大值為 256：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/34.jpg)

客戶端執行 hping3 發起 SYN 攻擊：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/35.jpg)

服務端執行如下命令，查看處於 SYN_RECV 狀態的最大個數：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/36.jpg)

可以發現，服務端處於 SYN_RECV 狀態的最大個數並不是 max_qlen_log 變量的值。

這就是前面所說的原因：**如果當前半連接隊列的長度 「沒有超過」理論半連接隊列最大值  max_qlen_log，那麼如果條件 3 成立，則依然會丟棄 SYN 包，也就會使得服務端處於 SYN_RECV 狀態的最大個數不會是理論值 max_qlen_log。**

我們來分析一波條件 3 :

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/37.jpg)

從上面的分析，可以得知如果觸發「當前半連接隊列長度 > 192」條件，TCP 第一次握手的 SYN 包是會被丟棄的。

在前面我們測試的結果，服務端處於 SYN_RECV 狀態的最大個數是 193，正好是觸發了條件 3，所以處於 SYN_RECV 狀態的個數還沒到「理論半連接隊列最大值 256」，就已經把 SYN 包丟棄了。

所以，服務端處於 SYN_RECV 狀態的最大個數分為如下兩種情況：

- 如果「當前半連接隊列」**沒超過**「理論半連接隊列最大值」，但是**超過** max_syn_backlog  - (max_syn_backlog >> 2)，那麼處於 SYN_RECV 狀態的最大個數就是 max_syn_backlog  - (max_syn_backlog >> 2)；
- 如果「當前半連接隊列」**超過**「理論半連接隊列最大值」，那麼處於 SYN_RECV 狀態的最大個數就是「理論半連接隊列最大值」；


> 每個 Linux 內核版本「理論」半連接最大值計算方式會不同。

在上面我們是針對 Linux 2.6.32 版本分析的「理論」半連接最大值的算法，可能每個版本有些不同。

比如在 Linux 5.0.0 的時候，「理論」半連接最大值就是全連接隊列最大值，但依然還是有隊列溢出的三個條件：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/38.jpg)

> 如果 SYN 半連接隊列已滿，只能丟棄連接嗎？

並不是這樣，**開啟 syncookies 功能就可以在不使用 SYN 半連接隊列的情況下成功建立連接**，在前面我們源碼分析也可以看到這點，當開啟了  syncookies 功能就不會丟棄連接。

syncookies 是這麼做的：服務器根據當前狀態計算出一個值，放在己方發出的 SYN+ACK 報文中發出，當客戶端返回 ACK 報文時，取出該值驗證，如果合法，就認為連接建立成功，如下圖所示。

![開啟 syncookies 功能](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/39.jpg)

syncookies 參數主要有以下三個值：

- 0 值，表示關閉該功能；
- 1 值，表示僅當 SYN 半連接隊列放不下時，再啟用它；
- 2 值，表示無條件開啟功能；

那麼在應對 SYN 攻擊時，只需要設置為 1 即可：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/40.jpg)

> 如何防禦 SYN 攻擊？

這裡給出幾種防禦 SYN 攻擊的方法：

- 增大半連接隊列；
- 開啟 tcp_syncookies 功能
- 減少 SYN+ACK 重傳次數

*方式一：增大半連接隊列*

在前面源碼和實驗中，得知**要想增大半連接隊列，我們得知不能只單純增大 tcp_max_syn_backlog 的值，還需一同增大 somaxconn 和 backlog，也就是增大全連接隊列**。否則，只單純增大 tcp_max_syn_backlog 是無效的。

增大 tcp_max_syn_backlog 和 somaxconn 的方法是修改 Linux 內核參數：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/41.jpg)


增大 backlog 的方式，每個 Web 服務都不同，比如 Nginx 增大 backlog 的方法如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/42.jpg)


最後，改變瞭如上這些參數後，要重啟 Nginx 服務，因為半連接隊列和全連接隊列都是在 listen() 初始化的。

*方式二：開啟 tcp_syncookies 功能*

開啟 tcp_syncookies 功能的方式也很簡單，修改 Linux 內核參數：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/43.jpg)


*方式三：減少 SYN+ACK 重傳次數*

當服務端受到 SYN 攻擊時，就會有大量處於 SYN_RECV 狀態的 TCP 連接，處於這個狀態的 TCP 會重傳 SYN+ACK ，當重傳超過次數達到上限後，就會斷開連接。

那麼針對 SYN 攻擊的場景，我們可以減少 SYN+ACK 的重傳次數，以加快處於 SYN_RECV 狀態的 TCP 連接斷開。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E5%8D%8A%E8%BF%9E%E6%8E%A5%E5%92%8C%E5%85%A8%E8%BF%9E%E6%8E%A5/44.jpg)


---

參考資料：

[1] 系統性能調優必知必會.陶輝.極客時間.

[2] https://www.cnblogs.com/zengkefu/p/5606696.html

[3] https://blog.cloudflare.com/syn-packet-handling-in-the-wild/

---

## 讀者問答

> 讀者問：“咦 我比較好奇博主都是從哪裡學到這些知識的呀？書籍？視頻？還是多種參考資料”

你可以看我的參考文獻呀，知識點我主要是在極客專欄學的，實戰模擬實驗和源碼解析是自己瞎折騰出來的。

> 讀者問：“syncookies 啟用後就不需要半鏈接了？那請求的數據會存在哪裡？”

syncookies = 1 時，半連接隊列滿後，後續的請求就不會存放到半連接隊列了，而是在第二次握手的時候，服務端會計算一個 cookie 值，放入到 SYN +ACK 包中的序列號發給客戶端，客戶端收到後並回 ack ，服務端就會校驗連接是否合法，合法就直接把連接放入到全連接隊列。

----

## 最後

本文是以 Linux 2.6.32 版本的內核用實驗 + 源碼的方式，給大家說明瞭 TCP 半連接隊列和全連接隊列，我們可以看到 TCP 半連接隊列「並不是」如網上說的那樣 tcp_max_syn_backlog 表示半連接隊列。

TCP 半連接隊列的大小對於不同的 Linux 內核版本會有不同的計算方式，所以並不要求大家要死記住本文計算 TCP 半連接隊列的大小。

重要的是要學會自我源碼分析，這樣不管碰到什麼版本的 Linux 內核，都不再怕了。


網上搜索出來的信息，並不一定針對你的系統，通過自我分析一波，你會更瞭解你當前使用的 Linux 內核版本！


**小林是專為大家圖解的工具人，Goodbye，我們下次見！**

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

