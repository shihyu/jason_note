# 4.3 TCP 實戰抓包分析

為了讓大家更容易「看得見」 TCP，我搭建不少測試環境，並且數據包抓很多次，花費了不少時間，才抓到比較容易分析的數據包。

接下來丟包、亂序、超時重傳、快速重傳、選擇性確認、流量控制等等 TCP 的特性，都能「一覽無餘」。

沒錯，我把 TCP 的"衣服扒光"了，就為了給大家看的清楚，嘻嘻。

![提綱](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/2.jpg)

---

## 顯形“不可見”的網絡包

網絡世界中的數據包交互我們肉眼是看不見的，它們就好像隱形了一樣，我們對著課本學習計算機網絡的時候就會覺得非常的抽象，加大了學習的難度。

還別說，我自己在大學的時候，也是如此。

直到工作後，認識了兩大分析網絡的利器：**tcpdump 和 Wireshark**，這兩大利器把我們“看不見”的數據包，呈現在我們眼前，一目瞭然。

唉，當初大學學習計網的時候，要是能知道這兩個工具，就不會學的一臉懵逼。

> tcpdump 和 Wireshark 有什麼區別？

tcpdump 和 Wireshark 就是最常用的網絡抓包和分析工具，更是分析網絡性能必不可少的利器。

- tcpdump 僅支持命令行格式使用，常用在 Linux 服務器中抓取和分析網絡包。
- Wireshark 除了可以抓包外，還提供了可視化分析網絡包的圖形頁面。

所以，這兩者實際上是搭配使用的，先用 tcpdump 命令在 Linux 服務器上抓包，接著把抓包的文件拖出到 Windows 電腦後，用 Wireshark 可視化分析。

當然，如果你是在 Windows 上抓包，只需要用 Wireshark 工具就可以。

> tcpdump 在 Linux 下如何抓包？

tcpdump 提供了大量的選項以及各式各樣的過濾表達式，來幫助你抓取指定的數據包，不過不要擔心，只需要掌握一些常用選項和過濾表達式，就可以滿足大部分場景的需要了。

假設我們要抓取下面的 ping 的數據包：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/3.jpg)

要抓取上面的 ping 命令數據包，首先我們要知道 ping 的數據包是 `icmp` 協議，接著在使用 tcpdump 抓包的時候，就可以指定只抓 icmp 協議的數據包：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/4.jpg)

那麼當 tcpdump 抓取到 icmp 數據包後， 輸出格式如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/5.jpg)

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/6.jpg)

從 tcpdump 抓取的 icmp 數據包，我們很清楚的看到 `icmp echo` 的交互過程了，首先發送方發起了 `ICMP echo request` 請求報文，接收方收到後回了一個 `ICMP echo reply` 響應報文，之後 `seq` 是遞增的。

我在這裡也幫你整理了一些最常見的用法，並且繪製成了表格，你可以參考使用。

首先，先來看看常用的選項類，在上面的 ping 例子中，我們用過 `-i` 選項指定網口，用過 `-nn` 選項不對 IP 地址和端口名稱解析。其他常用的選項，如下表格：

![tcpdump 常用選項類](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/7.jpg)

接下來，我們再來看看常用的過濾表用法，在上面的 ping 例子中，我們用過的是 `icmp and host 183.232.231.174`，表示抓取 icmp 協議的數據包，以及源地址或目標地址為 183.232.231.174 的包。其他常用的過濾選項，我也整理成了下面這個表格。

![tcpdump 常用過濾表達式類](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/8.jpg)

說了這麼多，你應該也發現了，tcpdump 雖然功能強大，但是輸出的格式並不直觀。

所以，在工作中 tcpdump 只是用來抓取數據包，不用來分析數據包，而是把 tcpdump 抓取的數據包保存成 pcap 後綴的文件，接著用 Wireshark 工具進行數據包分析。

> Wireshark 工具如何分析數據包？

Wireshark 除了可以抓包外，還提供了可視化分析網絡包的圖形頁面，同時，還內置了一系列的彙總分析工具。

比如，拿上面的 ping 例子來說，我們可以使用下面的命令，把抓取的數據包保存到 ping.pcap 文件

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/9.jpg)

接著把 ping.pcap 文件拖到電腦，再用 Wireshark 打開它。打開後，你就可以看到下面這個界面：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/10.jpg)


是吧？在 Wireshark 的頁面裡，可以更加直觀的分析數據包，不僅展示各個網絡包的頭部信息，還會用不同的顏色來區分不同的協議，由於這次抓包只有 ICMP 協議，所以只有紫色的條目。

接著，在網絡包列表中選擇某一個網絡包後，在其下面的網絡包詳情中，**可以更清楚的看到，這個網絡包在協議棧各層的詳細信息**。比如，以編號 1 的網絡包為例子：

![ping 網絡包](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/11.jpg)

- 可以在數據鏈路層，看到 MAC 包頭信息，如源 MAC 地址和目標 MAC 地址等字段；
- 可以在 IP 層，看到 IP 包頭信息，如源 IP 地址和目標 IP 地址、TTL、IP 包長度、協議等 IP 協議各個字段的數值和含義；
- 可以在 ICMP 層，看到 ICMP 包頭信息，比如 Type、Code 等 ICMP 協議各個字段的數值和含義；

Wireshark 用了分層的方式，展示了各個層的包頭信息，把“不可見”的數據包，清清楚楚的展示了給我們，還有理由學不好計算機網絡嗎？是不是**相見恨晚**？

從 ping 的例子中，我們可以看到網絡分層就像有序的分工，每一層都有自己的責任範圍和信息，上層協議完成工作後就交給下一層，最終形成一個完整的網絡包。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/12.jpg)

---

## 解密 TCP 三次握手和四次揮手

既然學會了 tcpdump 和 Wireshark 兩大網絡分析利器，那我們快馬加鞭，接下來用它倆抓取和分析 HTTP 協議網絡包，並理解 TCP 三次握手和四次揮手的工作原理。

本次例子，我們將要訪問的 http://192.168.3.200 服務端。在終端一用 tcpdump 命令抓取數據包：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/13.jpg)

接著，在終端二執行下面的 curl 命令：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/14.jpg)

最後，回到終端一，按下 Ctrl+C 停止 tcpdump，並把得到的 http.pcap 取出到電腦。

使用 Wireshark 打開 http.pcap 後，你就可以在 Wireshark 中，看到如下的界面：

![HTTP 網絡包](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/15.jpg)

我們都知道 HTTP 是基於 TCP 協議進行傳輸的，那麼：

- 最開始的 3 個包就是 TCP 三次握手建立連接的包
- 中間是 HTTP 請求和響應的包
- 而最後的 3 個包則是 TCP 斷開連接的揮手包


Wireshark 可以用時序圖的方式顯示數據包交互的過程，從菜單欄中，點擊 統計 (Statistics) -> 流量圖 (Flow Graph)，然後，在彈出的界面中的「流量類型」選擇 「TCP Flows」，你可以更清晰的看到，整個過程中 TCP 流的執行過程：


![TCP 流量圖](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/16.jpg)

> 你可能會好奇，為什麼三次握手連接過程的 Seq 是 0 ？

實際上是因為 Wireshark 工具幫我們做了優化，它默認顯示的是序列號 seq 是相對值，而不是真實值。

如果你想看到實際的序列號的值，可以右鍵菜單， 然後找到「協議首選項」，接著找到「Relative Seq」後，把它給取消，操作如下：

![取消序列號相對值顯示](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/17.jpg)

取消後，Seq 顯示的就是真實值了：

![TCP 流量圖](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/18.jpg)

可見，客戶端和服務端的序列號實際上是不同的，序列號是一個隨機值。

這其實跟我們書上看到的 TCP 三次握手和四次揮手很類似，作為對比，你通常看到的 TCP 三次握手和四次揮手的流程，基本是這樣的：

![TCP 三次握手和四次揮手的流程](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/19.jpg)


> 為什麼抓到的 TCP 揮手是三次，而不是書上說的四次？

當被動關閉方（上圖的服務端）在 TCP 揮手過程中，「**沒有數據要發送」並且「開啟了 TCP 延遲確認機制」，那麼第二和第三次揮手就會合並傳輸，這樣就出現了三次揮手。**

而通常情況下，服務器端收到客戶端的 `FIN` 後，很可能還沒發送完數據，所以就會先回復客戶端一個 `ACK` 包，稍等一會兒，完成所有數據包的發送後，才會發送 `FIN` 包，這也就是四次揮手了。

---

## TCP 三次握手異常情況實戰分析

TCP 三次握手的過程相信大家都背的滾瓜爛熟，那麼你有沒有想過這三個異常情況：

- **TCP 第一次握手的 SYN 丟包了，會發生了什麼？**
- **TCP 第二次握手的 SYN、ACK 丟包了，會發生什麼？**
- **TCP 第三次握手的 ACK 包丟了，會發生什麼？**

有的小夥伴可能說：“很簡單呀，包丟了就會重傳嘛。”

那我在繼續問你：

- 那會重傳幾次？
- 超時重傳的時間 RTO 會如何變化？
- 在 Linux 下如何設置重傳次數？
- ....

是不是啞口無言，無法回答？

不知道沒關係，接下里我用三個實驗案例，帶大家一起探究探究這三種異常。

### 實驗場景

本次實驗用了兩臺虛擬機，一臺作為服務端，一臺作為客戶端，它們的關係如下：

![實驗環境](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/21.jpg)

- 客戶端和服務端都是 CentOs 6.5 Linux，Linux 內核版本 2.6.32
- 服務端 192.168.12.36，apache web 服務
- 客戶端 192.168.12.37

### 實驗一：TCP 第一次握手 SYN 丟包

為了模擬 TCP 第一次握手 SYN 丟包的情況，我是在拔掉服務器的網線後，立刻在客戶端執行 curl 命令：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/22.jpg)

其間 tcpdump 抓包的命令如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/23.jpg)

過了一會， curl 返回了超時連接的錯誤：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/24.jpg)

從 `date` 返回的時間，可以發現在超時接近 1 分鐘的時間後，curl 返回了錯誤。

接著，把 tcp_sys_timeout.pcap 文件用 Wireshark 打開分析，顯示如下圖：

![SYN 超時重傳五次](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/25.jpg)

從上圖可以發現， 客戶端發起了 SYN 包後，一直沒有收到服務端的 ACK ，所以一直超時重傳了 5 次，並且每次 RTO 超時時間是不同的：

- 第一次是在 1 秒超時重傳
- 第二次是在 3 秒超時重傳
- 第三次是在 7 秒超時重傳
- 第四次是在 15 秒超時重傳
- 第五次是在 31 秒超時重傳


可以發現，每次超時時間 RTO 是**指數（翻倍）上漲的**，當超過最大重傳次數後，客戶端不再發送 SYN 包。

在 Linux 中，第一次握手的 `SYN` 超時重傳次數，是如下內核參數指定的：

```bash
$ cat /proc/sys/net/ipv4/tcp_syn_retries
5
```

`tcp_syn_retries` 默認值為 5，也就是 SYN 最大重傳次數是 5 次。

接下來，我們繼續做實驗，把 `tcp_syn_retries` 設置為 2 次：

```bash
$ echo 2 > /proc/sys/net/ipv4/tcp_syn_retries
```

重傳抓包後，用 Wireshark 打開分析，顯示如下圖：

![SYN 超時重傳兩次](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/26.jpg)

> 實驗一的實驗小結

通過實驗一的實驗結果，我們可以得知，當客戶端發起的 TCP 第一次握手 SYN 包，在超時時間內沒收到服務端的 ACK，就會在超時重傳 SYN 數據包，每次超時重傳的 RTO 是翻倍上漲的，直到 SYN 包的重傳次數到達 `tcp_syn_retries` 值後，客戶端不再發送 SYN 包。

![SYN 超時重傳](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/27.jpg)

### 實驗二：TCP 第二次握手 SYN、ACK 丟包

為了模擬客戶端收不到服務端第二次握手 SYN、ACK 包，我的做法是在客戶端加上防火牆限制，直接粗暴的把來自服務端的數據都丟棄，防火牆的配置如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/28.jpg)

接著，在客戶端執行 curl 命令：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/29.jpg)

從 `date` 返回的時間前後，可以算出大概 1 分鐘後，curl 報錯退出了。

客戶端在這其間抓取的數據包，用 Wireshark 打開分析，顯示的時序圖如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/30.jpg)

從圖中可以發現：

- 客戶端發起 SYN 後，由於防火牆屏蔽了服務端的所有數據包，所以 curl 是無法收到服務端的 SYN、ACK 包，當發生超時後，就會重傳 SYN 包
- 服務端收到客戶的 SYN 包後，就會回 SYN、ACK 包，但是客戶端一直沒有回 ACK，服務端在超時後，重傳了 SYN、ACK 包，**接著一會，客戶端超時重傳的 SYN 包又抵達了服務端，服務端收到後，然後回了 SYN、ACK 包，但是SYN、ACK包的重傳定時器並沒有重置，還持續在重傳，因為第二次握手在沒收到第三次握手的 ACK 確認報文時，就會重傳到最大次數。**
- 最後，客戶端 SYN 超時重傳次數達到了 5 次（tcp_syn_retries 默認值 5 次），就不再繼續發送 SYN 包了。

所以，我們可以發現，**當第二次握手的 SYN、ACK 丟包時，客戶端會超時重發 SYN 包，服務端也會超時重傳 SYN、ACK 包。**

> 咦？客戶端設置了防火牆，屏蔽了服務端的網絡包，為什麼 tcpdump 還能抓到服務端的網絡包？

添加 iptables 限制後， tcpdump 是否能抓到包 ，這要看添加的 iptables 限制條件：

- 如果添加的是 `INPUT` 規則，則可以抓得到包
- 如果添加的是 `OUTPUT` 規則，則抓不到包

網絡包進入主機後的順序如下：

- 進來的順序 Wire -> NIC -> **tcpdump -> netfilter/iptables**
- 出去的順序 **iptables -> tcpdump** -> NIC -> Wire

> tcp_syn_retries 是限制 SYN 重傳次數，那第二次握手 SYN、ACK 限制最大重傳次數是多少？

TCP 第二次握手 SYN、ACK 包的最大重傳次數是通過 `tcp_synack_retries ` 內核參數限制的，其默認值如下：

```bash
$ cat /proc/sys/net/ipv4/tcp_synack_retries
5
```

是的，TCP 第二次握手 SYN、ACK 包的最大重傳次數默認值是 `5` 次。

為了驗證 SYN、ACK 包最大重傳次數是 5 次，我們繼續做下實驗，我們先把客戶端的 `tcp_syn_retries` 設置為 1，表示客戶端 SYN 最大超時次數是 1 次，目的是為了防止多次重傳 SYN，把服務端 SYN、ACK 超時定時器重置。

接著，還是如上面的步驟：

1. 客戶端配置防火牆屏蔽服務端的數據包
2. 客戶端 tcpdump 抓取 curl 執行時的數據包

把抓取的數據包，用 Wireshark 打開分析，顯示的時序圖如下： 

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/31.jpg)

從上圖，我們可以分析出：

- 客戶端的 SYN 只超時重傳了 1 次，因為 `tcp_syn_retries` 值為 1
- 服務端應答了客戶端超時重傳的 SYN 包後，由於一直收不到客戶端的 ACK 包，所以服務端一直在超時重傳 SYN、ACK 包，每次的 RTO 也是指數上漲的，一共超時重傳了 5 次，因為 `tcp_synack_retries` 值為 5

接著，我把 **tcp_synack_retries 設置為 2**，`tcp_syn_retries` 依然設置為 1:

```bash
$ echo 2 > /proc/sys/net/ipv4/tcp_synack_retries
$ echo 1 > /proc/sys/net/ipv4/tcp_syn_retries
```

依然保持一樣的實驗步驟進行操作，接著把抓取的數據包，用 Wireshark 打開分析，顯示的時序圖如下： 

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/32.jpg)

可見：

- 客戶端的 SYN 包只超時重傳了 1 次，符合 tcp_syn_retries 設置的值；
- 服務端的 SYN、ACK 超時重傳了 2 次，符合 tcp_synack_retries 設置的值

> 實驗二的實驗小結

通過實驗二的實驗結果，我們可以得知，當 TCP 第二次握手 SYN、ACK 包丟了後，客戶端 SYN 包會發生超時重傳，服務端 SYN、ACK 也會發生超時重傳。

客戶端 SYN 包超時重傳的最大次數，是由 tcp_syn_retries 決定的，默認值是 5 次；服務端 SYN、ACK 包時重傳的最大次數，是由 tcp_synack_retries 決定的，默認值是 5 次。

### 實驗三：TCP 第三次握手 ACK 丟包

為了模擬 TCP 第三次握手 ACK 包丟，我的實驗方法是**在服務端配置防火牆，屏蔽客戶端 TCP 報文中標誌位是 ACK 的包**，也就是當服務端收到客戶端的 TCP ACK 的報文時就會丟棄。

iptables 配置命令如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/33.jpg)

接著，在客戶端執行如下 tcpdump 命令：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/34.jpg)

然後，客戶端向服務端發起 telnet，因為 telnet 命令是會發起 TCP 連接，所以用此命令做測試：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/35.jpg)

此時，由於服務端收不到第三次握手的 ACK 包，所以一直處於 `SYN_RECV` 狀態：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/36.jpg)

而客戶端是已完成 TCP 連接建立，處於 `ESTABLISHED` 狀態：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/37.jpg)

過了 1 分鐘後，觀察發現服務端的 TCP 連接不見了：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/38.jpg)

過了 30 分鐘，客戶端依然還是處於 `ESTABLISHED` 狀態：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/39.jpg)

接著，在剛才客戶端建立的 telnet 會話，輸入 123456 字符，進行發送：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/40.jpg)

持續「好長」一段時間，客戶端的 telnet 才斷開連接：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/41.jpg)


以上就是本次的實現三的現象，這裡存在兩個疑點：

- 為什麼服務端原本處於 `SYN_RECV` 狀態的連接，過 1 分鐘後就消失了？
- 為什麼客戶端 telnet 輸入 123456 字符後，過了好長一段時間，telnet 才斷開連接？

不著急，我們把剛抓的數據包，用 Wireshark 打開分析，顯示的時序圖如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/42.jpg)

上圖的流程：

- 客戶端發送 SYN 包給服務端，服務端收到後，回了個 SYN、ACK 包給客戶端，此時服務端的 TCP 連接處於 `SYN_RECV` 狀態；
- 客戶端收到服務端的  SYN、ACK 包後，給服務端回了個 ACK 包，此時客戶端的 TCP 連接處於 `ESTABLISHED` 狀態；
- 由於服務端配置了防火牆，屏蔽了客戶端的 ACK 包，所以服務端一直處於 `SYN_RECV` 狀態，沒有進入  `ESTABLISHED` 狀態，tcpdump 之所以能抓到客戶端的 ACK 包，是因為數據包進入系統的順序是先進入 tcpudmp，後經過 iptables；
- 接著，服務端超時重傳了 SYN、ACK 包，重傳了 5 次後，也就是**超過 tcp_synack_retries 的值（默認值是 5），然後就沒有繼續重傳了，此時服務端的 TCP 連接主動中止了，所以剛才處於 SYN_RECV 狀態的 TCP 連接斷開了**，而客戶端依然處於`ESTABLISHED` 狀態；
- 雖然服務端 TCP 斷開了，但過了一段時間，發現客戶端依然處於`ESTABLISHED` 狀態，於是就在客戶端的 telnet 會話輸入了 123456 字符；
- 由於服務端的防火牆配置了屏蔽所有攜帶 ACK 標誌位的 TCP 報文，客戶端發送的數據報文，服務端並不會接收，而是丟棄（如果服務端沒有設置防火牆，由於服務端已經斷開連接，此時收到客戶的發來的數據報文後，會回 RST 報文）。客戶端由於一直收不到數據報文的確認報文，所以觸發超時重傳，在超時重傳過程中，每一次重傳，RTO 的值是指數增長的，所以持續了好長一段時間，客戶端的 telnet 才報錯退出了，此時共重傳了 15 次，然後客戶端的也斷開了連接。

通過這一波分析，剛才的兩個疑點已經解除了：

- 服務端在重傳 SYN、ACK 包時，超過了最大重傳次數 `tcp_synack_retries`，於是服務端的 TCP 連接主動斷開了。
- 客戶端向服務端發送數據報文時，如果遲遲沒有收到數據包的確認報文，也會觸發超時重傳，一共重傳了 15 次數據報文， 最後 telnet 就斷開了連接。

> TCP 第一次握手的 SYN 包超時重傳最大次數是由 tcp_syn_retries 指定，TCP 第二次握手的 SYN、ACK 包超時重傳最大次數是由 tcp_synack_retries 指定，那 TCP 建立連接後的數據包最大超時重傳次數是由什麼參數指定呢？

TCP 建立連接後的數據包傳輸，最大超時重傳次數是由 `tcp_retries2` 指定，默認值是 15 次，如下：

```
$ cat /proc/sys/net/ipv4/tcp_retries2
15
```

如果 15 次重傳都做完了，TCP 就會告訴應用層說：“搞不定了，包怎麼都傳不過去！”

> 那如果客戶端不發送數據，什麼時候才會斷開處於 ESTABLISHED 狀態的連接？

這裡就需要提到 TCP 的 **保活機制**。這個機制的原理是這樣的：

定義一個時間段，在這個時間段內，如果沒有任何連接相關的活動，TCP 保活機制會開始作用，每隔一個時間間隔，發送一個「探測報文」，該探測報文包含的數據非常少，如果連續幾個探測報文都沒有得到響應，則認為當前的 TCP 連接已經死亡，系統內核將錯誤信息通知給上層應用程序。

在 Linux 內核可以有對應的參數可以設置保活時間、保活探測的次數、保活探測的時間間隔，以下都為默認值：

```
net.ipv4.tcp_keepalive_time=7200
net.ipv4.tcp_keepalive_intvl=75  
net.ipv4.tcp_keepalive_probes=9
```

- tcp_keepalive_time=7200：表示保活時間是 7200 秒（2小時），也就 2 小時內如果沒有任何連接相關的活動，則會啟動保活機制
- tcp_keepalive_intvl=75：表示每次檢測間隔 75 秒；
- tcp_keepalive_probes=9：表示檢測 9 次無響應，認為對方是不可達的，從而中斷本次的連接。

也就是說在 Linux 系統中，最少需要經過 2 小時 11 分 15 秒才可以發現一個「死亡」連接。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/43.jpg)

這個時間是有點長的，所以如果我抓包足夠久，或許能抓到探測報文。

> 實驗三的實驗小結

在建立 TCP 連接時，如果第三次握手的 ACK，服務端無法收到，則服務端就會短暫處於 `SYN_RECV` 狀態，而客戶端會處於 `ESTABLISHED` 狀態。

由於服務端一直收不到 TCP 第三次握手的 ACK，則會一直重傳 SYN、ACK 包，直到重傳次數超過 `tcp_synack_retries` 值（默認值 5 次）後，服務端就會斷開 TCP 連接。

而客戶端則會有兩種情況：

- 如果客戶端沒發送數據包，一直處於 `ESTABLISHED` 狀態，然後經過 2 小時 11 分 15 秒才可以發現一個「死亡」連接，於是客戶端連接就會斷開連接。
- 如果客戶端發送了數據包，一直沒有收到服務端對該數據包的確認報文，則會一直重傳該數據包，直到重傳次數超過 `tcp_retries2` 值（默認值 15 次）後，客戶端就會斷開 TCP 連接。

---

## TCP 快速建立連接

客戶端在向服務端發起 HTTP GET 請求時，一個完整的交互過程，需要 2.5 個 RTT 的時延。

由於第三次握手是可以攜帶數據的，這時如果在第三次握手發起 HTTP GET 請求，需要 2 個 RTT 的時延。

但是在下一次（不是同個 TCP 連接的下一次）發起 HTTP GET 請求時，經歷的 RTT 也是一樣，如下圖：

![常規 HTTP 請求](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/44.jpg)

在 Linux 3.7 內核版本中，提供了 TCP Fast Open 功能，這個功能可以減少 TCP 連接建立的時延。

![常規 HTTP 請求 與 Fast  Open HTTP 請求](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/45.jpg)

- 在第一次建立連接的時候，服務端在第二次握手產生一個 `Cookie` （已加密）並通過 SYN、ACK 包一起發給客戶端，於是客戶端就會緩存這個 `Cookie`，所以第一次發起 HTTP Get 請求的時候，還是需要 2 個 RTT 的時延；
- 在下次請求的時候，客戶端在 SYN 包帶上 `Cookie` 發給服務端，就提前可以跳過三次握手的過程，因為 `Cookie` 中維護了一些信息，服務端可以從 `Cookie` 獲取 TCP 相關的信息，這時發起的 HTTP GET 請求就只需要 1 個 RTT 的時延；


注：客戶端在請求並存儲了 Fast Open Cookie 之後，可以不斷重複 TCP Fast Open 直至服務器認為 Cookie 無效（通常為過期）

> 在 Linux 上如何打開 Fast Open 功能？

可以通過設置 `net.ipv4.tcp_fastopn` 內核參數，來打開 Fast Open 功能。

net.ipv4.tcp_fastopn 各個值的意義: 

- 0 關閉
- 1 作為客戶端使用 Fast Open 功能
- 2 作為服務端使用 Fast Open 功能
- 3 無論作為客戶端還是服務器，都可以使用 Fast Open 功能

> TCP Fast Open 抓包分析

在下圖，數據包 7 號，客戶端發起了第二次 TCP 連接時，SYN 包會攜帶 Cooike，並且長度為 5 的數據。

服務端收到後，校驗 Cooike 合法，於是就回了 SYN、ACK 包，並且確認應答收到了客戶端的數據包，ACK = 5 + 1 = 6 

![TCP Fast Open 抓包分析](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/46.jpg)

---

## TCP 重複確認和快速重傳

當接收方收到亂序數據包時，會發送重複的 ACK，以便告知發送方要重發該數據包，**當發送方收到 3 個重複 ACK 時，就會觸發快速重傳，立刻重發丟失數據包。**

![快速重傳機制](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/47.jpg)

TCP 重複確認和快速重傳的一個案例，用 Wireshark 分析，顯示如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/48.jpg)

- 數據包 1 期望的下一個數據包 Seq 是 1，但是數據包 2 發送的 Seq 卻是 10945，說明收到的是亂序數據包，於是回了數據包 3 ，還是同樣的 Seq = 1，Ack = 1，這表明是重複的 ACK；
- 數據包 4 和 6 依然是亂序的數據包，於是依然回了重複的 ACK；
- 當對方收到三次重複的 ACK 後，於是就快速重傳了 Seq = 1 、Len = 1368 的數據包 8；
- 當收到重傳的數據包後，發現 Seq = 1 是期望的數據包，於是就發送了個確認收到快速重傳的 ACK

注意：快速重傳和重複 ACK 標記信息是 Wireshark 的功能，非數據包本身的信息。

以上案例在 TCP 三次握手時協商開啟了**選擇性確認 SACK**，因此一旦數據包丟失並收到重複 ACK ，即使在丟失數據包之後還成功接收了其他數據包，也只需要重傳丟失的數據包。如果不啟用 SACK，就必須重傳丟失包之後的每個數據包。

如果要支持 `SACK`，必須雙方都要支持。在 Linux 下，可以通過 `net.ipv4.tcp_sack` 參數打開這個功能（Linux 2.4 後默認打開）。

---

## TCP 流量控制

TCP 為了防止發送方無腦的發送數據，導致接收方緩衝區被填滿，所以就有了滑動窗口的機制，它可利用接收方的接收窗口來控制發送方要發送的數據量，也就是流量控制。

接收窗口是由接收方指定的值，存儲在 TCP 頭部中，它可以告訴發送方自己的 TCP 緩衝空間區大小，這個緩衝區是給應用程序讀取數據的空間：

- 如果應用程序讀取了緩衝區的數據，那麼緩衝空間區就會把被讀取的數據移除
- 如果應用程序沒有讀取數據，則數據會一直滯留在緩衝區。

接收窗口的大小，是在 TCP 三次握手中協商好的，後續數據傳輸時，接收方發送確認應答 ACK 報文時，會攜帶當前的接收窗口的大小，以此來告知發送方。

假設接收方接收到數據後，應用層能很快的從緩衝區裡讀取數據，那麼窗口大小會一直保持不變，過程如下：

![理想狀態下的窗口變化](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/49.jpg)

但是現實中服務器會出現繁忙的情況，當應用程序讀取速度慢，那麼緩存空間會慢慢被佔滿，於是為了保證發送方發送的數據不會超過緩衝區大小，服務器則會調整窗口大小的值，接著通過 ACK 報文通知給對方，告知現在的接收窗口大小，從而控制發送方發送的數據大小。

![服務端繁忙狀態下的窗口變化](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/50.jpg)

### 零窗口通知與窗口探測

假設接收方處理數據的速度跟不上接收數據的速度，緩存就會被佔滿，從而導致接收窗口為 0，當發送方接收到零窗口通知時，就會停止發送數據。

如下圖，可以看到接收方的窗口大小在不斷的收縮至 0：

![窗口大小在收縮](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/51.jpg)


接著，發送方會**定時發送窗口大小探測報文**，以便及時知道接收方窗口大小的變化。

以下圖 Wireshark 分析圖作為例子說明：

![零窗口 與 窗口探測](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/52.jpg)

- 發送方發送了數據包 1 給接收方，接收方收到後，由於緩衝區被佔滿，回了個零窗口通知；
- 發送方收到零窗口通知後，就不再發送數據了，直到過了 `3.4` 秒後，發送了一個 TCP Keep-Alive 報文，也就是窗口大小探測報文；
- 當接收方收到窗口探測報文後，就立馬回一個窗口通知，但是窗口大小還是 0；
- 發送方發現窗口還是 0，於是繼續等待了 `6.8`（翻倍） 秒後，又發送了窗口探測報文，接收方依然還是回了窗口為 0 的通知；
- 發送方發現窗口還是 0，於是繼續等待了 `13.5`（翻倍） 秒後，又發送了窗口探測報文，接收方依然還是回了窗口為 0 的通知；

可以發現，這些窗口探測報文以 3.4s、6.5s、13.5s 的間隔出現，說明超時時間會**翻倍**遞增。

這連接暫停了 25s，想象一下你在打王者的時候，25s 的延遲你還能上王者嗎？

### 發送窗口的分析

> 在 Wireshark 看到的 Windows size 也就是 " win = "，這個值表示發送窗口嗎？


這不是發送窗口，而是在向對方聲明自己的接收窗口。

你可能會好奇，抓包文件裡有「Window size scaling factor」，它其實是算出實際窗口大小的乘法因子，「Window size value」實際上並不是真實的窗口大小，真實窗口大小的計算公式如下：

「Window size value」 * 「Window size scaling factor」 = 「Caculated window size 」

對應的下圖案例，也就是 32 * 2048 = 65536。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/53.jpg)

實際上是 Caculated window size 的值是 Wireshark 工具幫我們算好的，Window size scaling factor 和 Windos size value 的值是在 TCP 頭部中，其中 Window size scaling factor 是在三次握手過程中確定的，如果你抓包的數據沒有 TCP 三次握手，那可能就無法算出真實的窗口大小的值，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/54.jpg)

> 如何在包裡看出發送窗口的大小？

很遺憾，沒有簡單的辦法，發送窗口雖然是由接收窗口決定，但是它又可以被網絡因素影響，也就是擁塞窗口，實際上發送窗口是值是 min(擁塞窗口，接收窗口)。

> 發送窗口和 MSS 有什麼關係？

發送窗口決定了一口氣能發多少字節，而 MSS 決定了這些字節要分多少包才能發完。

舉個例子，如果發送窗口為 16000 字節的情況下，如果 MSS 是 1000 字節，那就需要發送 1600/1000 = 16 個包。

> 發送方在一個窗口發出 n 個包，是不是需要 n 個 ACK 確認報文？

不一定，因為 TCP 有累計確認機制，所以當收到多個數據包時，只需要應答最後一個數據包的 ACK 報文就可以了。

---

## TCP 延遲確認與 Nagle 算法


當我們 TCP 報文的承載的數據非常小的時候，例如幾個字節，那麼整個網絡的效率是很低的，因為每個 TCP 報文中都會有 20 個字節的 TCP 頭部，也會有 20 個字節的 IP 頭部，而數據只有幾個字節，所以在整個報文中有效數據佔有的比重就會非常低。

這就好像快遞員開著大貨車送一個小包裹一樣浪費。

那麼就出現了常見的兩種策略，來減少小報文的傳輸，分別是：

- Nagle 算法
- 延遲確認

> Nagle 算法是如何避免大量 TCP 小數據報文的傳輸？

Nagle 算法做了一些策略來避免過多的小數據報文發送，這可提高傳輸效率。

Nagle 偽代碼如下：

```c
if 有數據要發送 {
    if 可用窗口大小 >= MSS and 可發送的數據 >= MSS {
    	立刻發送MSS大小的數據
    } else {
        if 有未確認的數據 {
            將數據放入緩存等待接收ACK
        } else {
            立刻發送數據
        }
    }
}
```

使用 Nagle 算法，該算法的思路是延時處理，只有滿足下面兩個條件中的任意一個條件，才能可以發送數據：

- 條件一：要等到窗口大小 >= `MSS` 並且 數據大小 >= `MSS`；
- 條件二：收到之前發送數據的 `ack` 回包；

只要上面兩個條件都不滿足，發送方一直在囤積數據，直到滿足上面的發送條件。

![禁用 Nagle 算法 與 啟用 Nagle 算法](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/55.jpg)

上圖右側啟用了 Nagle 算法，它的發送數據的過程：

- 一開始由於沒有已發送未確認的報文，所以就立刻發了 H 字符；
- 接著，在還沒收到對 H 字符的確認報文時，發送方就一直在囤積數據，直到收到了確認報文後，此時沒有已發送未確認的報文，於是就把囤積後的 ELL 字符一起發給了接收方；
- 待收到對 ELL 字符的確認報文後，於是把最後一個 O 字符發送了出去

可以看出，**Nagle 算法一定會有一個小報文，也就是在最開始的時候。**

另外，Nagle 算法默認是打開的，如果對於一些需要小數據包交互的場景的程序，比如，telnet 或 ssh 這樣的交互性比較強的程序，則需要關閉 Nagle 算法。

可以在 Socket 設置 `TCP_NODELAY` 選項來關閉這個算法（關閉 Nagle 算法沒有全局參數，需要根據每個應用自己的特點來關閉）。

![關閉 Nagle 算法](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/56.jpg)

> 那延遲確認又是什麼？

事實上當沒有攜帶數據的 ACK，它的網絡效率也是很低的，因為它也有 40 個字節的 IP 頭 和 TCP 頭，但卻沒有攜帶數據報文。

為瞭解決 ACK 傳輸效率低問題，所以就衍生出了 **TCP 延遲確認**。

TCP 延遲確認的策略：

- 當有響應數據要發送時，ACK 會隨著響應數據一起立刻發送給對方
- 當沒有響應數據要發送時，ACK 將會延遲一段時間，以等待是否有響應數據可以一起發送
- 如果在延遲等待發送 ACK 期間，對方的第二個數據報文又到達了，這時就會立刻發送 ACK

![TCP 延遲確認](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/57.jpg)


延遲等待的時間是在 Linux 內核中定義的，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/58.jpg)

關鍵就需要 `HZ` 這個數值大小，HZ 是跟系統的時鐘頻率有關，每個操作系統都不一樣，在我的 Linux 系統中 HZ 大小是 `1000`，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/59.jpg)

知道了 HZ 的大小，那麼就可以算出：

* 最大延遲確認時間是 `200` ms （1000/5）
* 最短延遲確認時間是 `40` ms （1000/25）

TCP 延遲確認可以在 Socket 設置 `TCP_QUICKACK` 選項來關閉這個算法。

![關閉 TCP 延遲確認](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/60.jpg)

>  延遲確認 和 Nagle 算法混合使用時，會產生新的問題

當 TCP 延遲確認 和 Nagle 算法混合使用時，會導致時耗增長，如下圖：

![TCP 延遲確認 和 Nagle 算法混合使用](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/TCP-Wireshark/61.jpg)

發送方使用了 Nagle 算法，接收方使用了 TCP 延遲確認會發生如下的過程：

- 發送方先發出一個小報文，接收方收到後，由於延遲確認機制，自己又沒有要發送的數據，只能乾等著發送方的下一個報文到達；
- 而發送方由於 Nagle 算法機制，在未收到第一個報文的確認前，是不會發送後續的數據；
- 所以接收方只能等待最大時間 200 ms 後，才回 ACK 報文，發送方收到第一個報文的確認報文後，也才可以發送後續的數據。

很明顯，這兩個同時使用會造成額外的時延，這就會使得網絡"很慢"的感覺。

要解決這個問題，只有兩個辦法：

- 要不發送方關閉 Nagle 算法
- 要不接收方關閉 TCP 延遲確認

---

參考資料：

[1] Wireshark網絡分析的藝術.林沛滿.人民郵電出版社.

[2] Wireshark網絡分析就這麼簡單.林沛滿.人民郵電出版社.

[3] Wireshark數據包分析實戰.Chris Sanders .人民郵電出版社.讀者問答

---

## 讀者問答

> 讀者問：“兩個問題，請教一下作者:
> tcp_retries1 參數，是什麼場景下生效？
> tcp_retries2是不是隻受限於規定的次數，還是受限於次數和時間限制的最小值？”

tcp_retries1和tcp_retries2都是在TCP三次握手之後的場景。

- 當重傳次數超過tcp_retries1就會指示 IP 層進行 MTU 探測、刷新路由等過程，並不會斷開TCP連接，當重傳次數超過 tcp_retries2 才會斷開TCP流。
- tcp_retries1 和 tcp_retries2 兩個重傳次數都是受一個 timeout 值限制的，timeout 的值是根據它倆的值計算出來的，當重傳時間超過 timeout，就不會繼續重傳了，即使次數還沒到達。

> 讀者問：“tcp_orphan_retries也是控制tcp連接的關閉。這個跟tcp_retries1 tcp_retries2有什麼區別嗎？”

主動方發送 FIN 報文後，連接就處於 FIN_WAIT1 狀態下，該狀態通常應在數十毫秒內轉為 FIN_WAIT2。如果遲遲收不到對方返回的 ACK 時，此時，內核會定時重發 FIN 報文，其中重發次數由 tcp_orphan_retries 參數控制。

> 讀者問：“請問，為什麼連續兩個報文的seq會是一樣的呢，比如三次握手之後的那個報文？還是說，序號相同的是同一個報文，只是拆開顯示了？”

1. 三次握手中的前兩次，是 seq+1；
2. 三次握手中的最後一個 ack，實際上是可以攜帶數據的，由於我文章的例子是沒有發送數據的，你可以看到第三次握手的 len=0 ，在數據傳輸階段「下一個 seq=seq+len 」，所以第三次握手的 seq 和下一個數據報的 seq 是一樣的，因為 len 為 0；

---

## 最後

文章中 Wireshark 分析的截圖，可能有些會看的不清楚，為了方便大家用 Wireshark 分析，**我已把文中所有抓包的源文件，已分享到公眾號了，大家在後臺回覆「抓包」，就可以獲取了。**

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-Wireshark/62.png)

**小林是專為大家圖解的工具人，Goodbye，我們下次見！**

