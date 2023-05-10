# 4.14 tcp_tw_reuse 為什麼默認是關閉的？

大家好，我是小林。

上週有個讀者在面試微信的時候，**被問到既然打開 net.ipv4.tcp_tw_reuse 參數可以快速複用處於 TIME_WAIT 狀態的 TCP 連接，那為什麼 Linux 默認是關閉狀態呢？**

![圖片](https://img-blog.csdnimg.cn/img_convert/23f1aea82a0b7c37f1031524600626f1.png)

![圖片](https://img-blog.csdnimg.cn/img_convert/076e60b984028bf3ad762eb2bd7ed0f3.png)

好傢伙，真的問好細節！

當時看到讀者這個問題的時候，我也是一臉懵逼的，經過我的一番思考後，終於知道怎麼回答這題了。

其實這題在變相問「**如果 TIME_WAIT 狀態持續時間過短或者沒有，會有什麼問題？**」

因為開啟 tcp_tw_reuse 參數可以快速複用處於 TIME_WAIT 狀態的 TCP 連接時，相當於縮短了 TIME_WAIT 狀態的持續時間。

可能有的同學會問說，使用 tcp_tw_reuse 快速複用處於 TIME_WAIT 狀態的 TCP 連接時，是需要保證  net.ipv4.tcp_timestamps 參數是開啟的（默認是開啟的），而 tcp_timestamps 參數可以避免舊連接的延遲報文，這不是解決了沒有 TIME_WAIT 狀態時的問題了嗎？

是解決部分問題，但是不能完全解決，接下來，我跟大家聊聊這個問題。

![圖片](https://img-blog.csdnimg.cn/img_convert/d17df1a39a750c33948062ecfc9a8d32.png)

## 什麼是 TIME_WAIT 狀態？

TCP 四次揮手過程，如下圖：

![圖片](https://img-blog.csdnimg.cn/img_convert/e973a17cb5b1092085ca1bbcd7083559.png)圖片

- 客戶端打算關閉連接，此時會發送一個 TCP 首部 `FIN` 標誌位被置為 `1`的報文，也即 `FIN` 報文，之後客戶端進入 `FIN_WAIT_1` 狀態。
- 服務端收到該報文後，就向客戶端發送 `ACK` 應答報文，接著服務端進入 `CLOSED_WAIT` 狀態。
- 客戶端收到服務端的 `ACK` 應答報文後，之後進入 `FIN_WAIT_2` 狀態。
- 等待服務端處理完數據後，也向客戶端發送 `FIN` 報文，之後服務端進入 `LAST_ACK` 狀態。
- 客戶端收到服務端的 `FIN` 報文後，回一個 `ACK` 應答報文，之後進入 `TIME_WAIT` 狀態
- 服務器收到了 `ACK` 應答報文後，就進入了 `CLOSE` 狀態，至此服務端已經完成連接的關閉。
- 客戶端在經過 `2MSL` 一段時間後，自動進入 `CLOSE` 狀態，至此客戶端也完成連接的關閉。

你可以看到，兩個方向都需要**一個 FIN 和一個 ACK**，因此通常被稱為**四次揮手**。

這裡一點需要注意是：**主動關閉連接的，才有 TIME_WAIT 狀態。**

可以看到，TIME_WAIT 是「主動關閉方」斷開連接時的最後一個狀態，該狀態會持續 ***2MSL(Maximum Segment Lifetime)\*** 時長，之後進入CLOSED 狀態。

MSL 指的是 TCP 協議中任何報文在網絡上最大的生存時間，任何超過這個時間的數據都將被丟棄。雖然 RFC 793 規定 MSL 為 2 分鐘，但是在實際實現的時候會有所不同，比如 Linux 默認為 30 秒，那麼 2MSL 就是 60 秒。

MSL 是由網絡層的 IP 包中的 TTL 來保證的，TTL 是 IP 頭部的一個字段，用於設置一個數據報可經過的路由器的數量上限。報文每經過一次路由器的轉發，IP 頭部的 TTL 字段就會減 1，減到 0 時報文就被丟棄。

MSL 與 TTL 的區別：MSL 的單位是時間，而 TTL 是經過路由跳數。所以 **MSL 應該要大於等於 TTL 消耗為 0 的時間**，以確保報文已被自然消亡。

**TTL 的值一般是 64，Linux 將 MSL 設置為 30 秒，意味著 Linux 認為數據報文經過 64 個路由器的時間不會超過 30 秒，如果超過了，就認為報文已經消失在網絡中了**。

## 為什麼要設計 TIME_WAIT 狀態？

設計 TIME_WAIT 狀態，主要有兩個原因：

- 防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收；
- 保證「被動關閉連接」的一方，能被正確的關閉；

#### 原因一：防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收

為了能更好的理解這個原因，我們先來瞭解序列號（SEQ）和初始序列號（ISN）。

- **序列號**，是 TCP 一個頭部字段，標識了 TCP 發送端到 TCP 接收端的數據流的一個字節，因為 TCP 是面向字節流的可靠協議，為了保證消息的順序性和可靠性，TCP 為每個傳輸方向上的每個字節都賦予了一個編號，以便於傳輸成功後確認、丟失後重傳以及在接收端保證不會亂序。**序列號是一個 32 位的無符號數，因此在到達 4G 之後再循環回到 0**。
- **初始序列號**，在 TCP 建立連接的時候，客戶端和服務端都會各自生成一個初始序列號，它是基於時鐘生成的一個隨機數，來保證每個連接都擁有不同的初始序列號。**初始化序列號可被視為一個 32 位的計數器，該計數器的數值每 4 微秒加 1，循環一次需要 4.55 小時**。

給大家抓了一個包，下圖中的 Seq 就是序列號，其中紅色框住的分別是客戶端和服務端各自生成的初始序列號。

![圖片](https://img-blog.csdnimg.cn/img_convert/b70ee2f17636deeb3930010b6dcdabb7.png)

通過前面我們知道，**序列號和初始化序列號並不是無限遞增的，會發生迴繞為初始值的情況，這意味著無法根據序列號來判斷新老數據**。

假設 TIME-WAIT 沒有等待時間或時間過短，被延遲的數據包抵達後會發生什麼呢？

![圖片](https://img-blog.csdnimg.cn/img_convert/f1ba45cdb7d772ccd12dc604dee26c91.png)



- 服務端在關閉連接之前發送的 `SEQ = 301` 報文，被網絡延遲了。
- 接著，服務端以相同的四元組重新打開了新連接，前面被延遲的 `SEQ = 301` 這時抵達了客戶端，而且該數據報文的序列號剛好在客戶端接收窗口內，因此客戶端會正常接收這個數據報文，但是這個數據報文是上一個連接殘留下來的，這樣就產生數據錯亂等嚴重的問題。

為了防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收，因此 TCP 設計了 TIME_WAIT 狀態，狀態會持續 `2MSL` 時長，這個時間**足以讓兩個方向上的數據包都被丟棄，使得原來連接的數據包在網絡中都自然消失，再出現的數據包一定都是新建立連接所產生的。**

#### 原因二：保證「被動關閉連接」的一方，能被正確的關閉

如果客戶端（主動關閉方）最後一次 ACK 報文（第四次揮手）在網絡中丟失了，那麼按照 TCP 可靠性原則，服務端（被動關閉方）會重發 FIN 報文。

假設客戶端沒有 TIME_WAIT 狀態，而是在發完最後一次回 ACK 報文就直接進入 CLOSED 狀態，如果該  ACK 報文丟失了，服務端則重傳的 FIN 報文，而這時客戶端已經進入到關閉狀態了，在收到服務端重傳的 FIN 報文後，就會回 RST 報文。

![圖片](https://img-blog.csdnimg.cn/img_convert/8016c9f9b875649a5ab8bdd245c34729.png)

服務端收到這個 RST 並將其解釋為一個錯誤（Connection reset by peer），這對於一個可靠的協議來說不是一個優雅的終止方式。

為了防止這種情況出現，客戶端必須等待足夠長的時間，確保服務端能夠收到 ACK，如果服務端沒有收到 ACK，那麼就會觸發 TCP 重傳機制，服務端會重新發送一個 FIN，這樣一去一來剛好兩個 MSL 的時間。

![TIME-WAIT 時間正常，確保了連接正常關閉](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4/網絡/TIME-WAIT連接正常關閉.drawio.png)

客戶端在收到服務端重傳的 FIN 報文時，TIME_WAIT 狀態的等待時間，會重置回 2MSL。

## tcp_tw_reuse 是什麼？

在 Linux  操作系統下，TIME_WAIT 狀態的持續時間是 60 秒，這意味著這 60 秒內，客戶端一直會佔用著這個端口。要知道，端口資源也是有限的，一般可以開啟的端口為 32768~61000 ，也可以通過如下參數設置指定範圍：

```
 net.ipv4.ip_local_port_range
```

**如果客戶端（主動關閉連接方）的 TIME_WAIT 狀態過多**，佔滿了所有端口資源，那麼就無法對「目的 IP+ 目的 PORT」都一樣的服務器發起連接了，但是被使用的端口，還是可以繼續對另外一個服務器發起連接的。具體可以看我這篇文章：[客戶端的端口可以重複使用嗎？](https://xiaolincoding.com/network/3_tcp/port.html#%E5%AE%A2%E6%88%B7%E7%AB%AF%E7%9A%84%E7%AB%AF%E5%8F%A3%E5%8F%AF%E4%BB%A5%E9%87%8D%E5%A4%8D%E4%BD%BF%E7%94%A8%E5%90%97)

因此，客戶端（主動關閉連接方）都是和「目的 IP+ 目的 PORT 」都一樣的服務器建立連接的話，當客戶端的 TIME_WAIT 狀態連接過多的話，就會受端口資源限制，如果佔滿了所有端口資源，那麼就無法再跟「目的 IP+ 目的 PORT」都一樣的服務器建立連接了。

不過，即使是在這種場景下，只要連接的是不同的服務器，端口是可以重複使用的，所以客戶端還是可以向其他服務器發起連接的，這是因為內核在定位一個連接的時候，是通過四元組（源IP、源端口、目的IP、目的端口）信息來定位的，並不會因為客戶端的端口一樣，而導致連接衝突。

好在，Linux 操作系統提供了兩個可以系統參數來快速回收處於 TIME_WAIT 狀態的連接，這兩個參數都是默認關閉的：

- net.ipv4.tcp_tw_reuse，如果開啟該選項的話，客戶端（連接發起方） 在調用 connect() 函數時，**如果內核選擇到的端口，已經被相同四元組的連接佔用的時候，就會判斷該連接是否處於 TIME_WAIT 狀態，如果該連接處於 TIME_WAIT 狀態並且 TIME_WAIT 狀態持續的時間超過了 1 秒，那麼就會重用這個連接，然後就可以正常使用該端口了**。所以該選項只適用於連接發起方。
- net.ipv4.tcp_tw_recycle，如果開啟該選項的話，允許處於 TIME_WAIT 狀態的連接被快速回收，該參數在 **NAT 的網絡下是不安全的**！詳細見這篇文章介紹：[SYN 報文什麼時候情況下會被丟棄？](https://xiaolincoding.com/network/3_tcp/syn_drop.html)

要使得上面這兩個參數生效，有一個前提條件，就是要打開 TCP 時間戳，即 net.ipv4.tcp_timestamps=1（默認即為 1）。

開啟了 tcp_timestamps 參數，TCP 頭部就會使用時間戳選項，它有兩個好處，**一個是便於精確計算 RTT ，另一個是能防止序列號迴繞（PAWS）**，我們先來介紹這個功能。

序列號是一個 32 位的無符號整型，上限值是 4GB，超過 4GB 後就需要將序列號迴繞進行重用。這在以前網速慢的年代不會造成什麼問題，但在一個速度足夠快的網絡中傳輸大量數據時，序列號的迴繞時間就會變短。如果序列號迴繞的時間極短，我們就會再次面臨之前延遲的報文抵達後序列號依然有效的問題。

為瞭解決這個問題，就需要有 TCP 時間戳。

試看下面的示例，假設 TCP 的發送窗口是 1 GB，並且使用了時間戳選項，發送方會為每個 TCP 報文分配時間戳數值，我們假設每個報文時間加 1，然後使用這個連接傳輸一個 6GB 大小的數據流。

![圖片](https://img-blog.csdnimg.cn/img_convert/bf004909d9e44c3bc740737ced6731a0.png)

32 位的序列號在時刻 D 和 E 之間迴繞。假設在時刻B有一個報文丟失並被重傳，又假設這個報文段在網絡上繞了遠路並在時刻 F 重新出現。如果 TCP 無法識別這個繞回的報文，那麼數據完整性就會遭到破壞。

使用時間戳選項能夠有效的防止上述問題，如果丟失的報文會在時刻 F 重新出現，由於它的時間戳為 2，小於最近的有效時間戳（5 或 6），因此防迴繞序列號算法（PAWS）會將其丟棄。

防迴繞序列號算法要求連接雙方維護最近一次收到的數據包的時間戳（Recent TSval），每收到一個新數據包都會讀取數據包中的時間戳值跟 Recent TSval 值做比較，**如果發現收到的數據包中時間戳不是遞增的，則表示該數據包是過期的，就會直接丟棄這個數據包**。

## 為什麼 tcp_tw_reuse  默認是關閉的？

通過前面這麼多鋪墊，終於可以說這個問題了。

開啟 tcp_tw_reuse 會有什麼風險呢？我覺得會有 2 個問題。

### 第一個問題

我們知道開啟 tcp_tw_reuse 的同時，也需要開啟 tcp_timestamps，意味著可以用時間戳的方式有效的判斷迴繞序列號的歷史報文。

但是，在看我看了防迴繞序列號函數的源碼後，發現對於 **RST 報文的時間戳即使過期了，只要 RST 報文的序列號在對方的接收窗口內，也是能被接受的**。

下面 tcp_validate_incoming 函數就是驗證接收到的 TCP 報文是否合格的函數，其中第一步就會進行 PAWS 檢查，由 tcp_paws_discard 函數負責。

```c
static bool tcp_validate_incoming(struct sock *sk, struct sk_buff *skb, const struct tcphdr *th, int syn_inerr)
{
    struct tcp_sock *tp = tcp_sk(sk);

    /* RFC1323: H1. Apply PAWS check first. */
    if (tcp_fast_parse_options(sock_net(sk), skb, th, tp) &&
        tp->rx_opt.saw_tstamp &&
        tcp_paws_discard(sk, skb)) {
        if (!th->rst) {
            ....
            goto discard;
        }
        /* Reset is accepted even if it did not pass PAWS. */
    }
```

當 tcp_paws_discard 返回 true，就代表報文是一個歷史報文，於是就要丟棄這個報文。但是在丟掉這個報文的時候，會先判斷是不是 RST 報文，如果不是 RST 報文，才會將報文丟掉。也就是說，即使 RST 報文是一個歷史報文，並不會被丟棄。

假設有這樣的場景，如下圖：

![](https://img-blog.csdnimg.cn/img_convert/0df2003d41ec0ef23844975a85cfb722.png)

過程如下：

- 客戶端向一個還沒有被服務端監聽的端口發起了 HTTP 請求，接著服務端就會回 RST 報文給對方，很可惜的是 **RST 報文被網絡阻塞了**。
- 由於客戶端遲遲沒有收到 TCP 第二次握手，於是重發了 SYN 包，與此同時服務端已經開啟了服務，監聽了對應的端口。於是接下來，客戶端和服務端就進行了 TCP 三次握手、數據傳輸（HTTP應答-響應）、四次揮手。
- 因為**客戶端開啟了 tcp_tw_reuse，於是快速複用 TIME_WAIT 狀態的端口，又與服務端建立了一個與剛才相同的四元組的連接**。
- 接著，**前面被網絡延遲 RST 報文這時抵達了客戶端，而且 RST 報文的序列號在客戶端的接收窗口內，由於防迴繞序列號算法不會防止過期的 RST，所以 RST 報文會被客戶端接受了，於是客戶端的連接就斷開了**。

上面這個場景就是開啟 tcp_tw_reuse 風險，**因為快速複用 TIME_WAIT 狀態的端口，導致新連接可能被迴繞序列號的 RST 報文斷開了，而如果不跳過 TIME_WAIT 狀態，而是停留 2MSL 時長，那麼這個 RST 報文就不會出現下一個新的連接**。

可能大家會有這樣的疑問，為什麼 PAWS 檢查要放過過期的 RST 報文。我翻了 RFC 1323 ，裡面有一句提到：

*It is recommended that RST segments NOT carry timestamps, and that RST segments be acceptable regardless of their timestamp.  Old duplicate RST segments should be exceedingly unlikely, and their cleanup function should take precedence over timestamps.*

大概的意思：*建議 RST 段不攜帶時間戳，並且無論其時間戳如何，RST 段都是可接受的。老的重複的 RST 段應該是極不可能的，並且它們的清除功能應優先於時間戳。*

RFC 1323 提到說收歷史的 RST 報文是極不可能，之所以有這樣的想法是因為 TIME_WAIT 狀態持續的 2MSL 時間，足以讓連接中的報文在網絡中自然消失，所以認為按正常操作來說是不會發生的，因此認為清除連接優先於時間戳。

而我前面提到的案例，是因為開啟了 tcp_tw_reuse 狀態，跳過了 TIME_WAIT 狀態，才發生的事情。

有同學會說，都經過一個 HTTP 請求了，延遲的 RST 報文竟然還會存活？

一個 HTTP 請求其實很快的，比如我下面這個抓包，只需要 0.2 秒就完成了，遠小於 MSL，所以延遲的 RST 報文存活是有可能的。

![圖片](https://img-blog.csdnimg.cn/img_convert/2ac40ca1757888b7154a2baa8bbb9885.png)

### 第二個問題

開啟 tcp_tw_reuse 來快速複用 TIME_WAIT 狀態的連接，如果第四次揮手的 ACK 報文丟失了，服務端會觸發超時重傳，重傳第三次揮手報文，處於 syn_sent 狀態的客戶端收到服務端重傳第三次揮手報文，則會回 RST 給服務端。如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/tcp/tcp_tw_reuse第二個問題.drawio.png)

這時候有同學就問了，如果 TIME_WAIT 狀態被快速複用後，剛好第四次揮手的 ACK 報文丟失了，那客戶端複用 TIME_WAIT 狀態後發送的 SYN 報文被處於 last_ack 狀態的服務端收到了會發生什麼呢？

處於 last_ack 狀態的服務端收到了 SYN 報文後，會回覆確認號與服務端上一次發送 ACK 報文一樣的 ACK 報文，這個 ACK 報文稱為 [Challenge ACK](https://xiaolincoding.com/network/3_tcp/challenge_ack.html)，並不是確認收到 SYN 報文。

處於 syn_sent 狀態的客戶端收到服務端的  [Challenge ACK](https://xiaolincoding.com/network/3_tcp/challenge_ack.html) 後，發現不是自己期望收到的確認號，於是就會回覆 RST 報文，服務端收到後，就會斷開連接。

## 總結

tcp_tw_reuse 的作用是讓客戶端快速複用處於 TIME_WAIT 狀態的端口，相當於跳過了 TIME_WAIT 狀態，這可能會出現這樣的兩個問題：

- 歷史 RST 報文可能會終止後面相同四元組的連接，因為 PAWS 檢查到即使 RST 是過期的，也不會丟棄。
- 如果第四次揮手的 ACK 報文丟失了，有可能被動關閉連接的一方不能被正常的關閉;

雖然 TIME_WAIT 狀態持續的時間是有一點長，顯得很不友好，但是它被設計來就是用來避免發生亂七八糟的事情。

《UNIX網絡編程》一書中卻說道：**TIME_WAIT 是我們的朋友，它是有助於我們的，不要試圖避免這個狀態，而是應該弄清楚它**。

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)