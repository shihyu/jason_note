# 4.11 在 TIME_WAIT 狀態的 TCP 連接，收到 SYN 後會發生什麼？

大家好，我是小林。

週末跟朋友討論了一些 TCP 的問題，在查閱《Linux 服務器高性能編程》這本書的時候，發現書上寫了這麼一句話：

![圖片](https://img-blog.csdnimg.cn/img_convert/65739ee668999bda02aa9236aad6437f.png)

書上說，處於 TIME_WAIT 狀態的連接，在收到相同四元組的 SYN 後，會回 RST 報文，對方收到後就會斷開連接。

書中作者只是提了這麼一句話，沒有給予源碼或者抓包圖的證據。

起初，我看到也覺得這個邏輯也挺符合常理的，但是當我自己去啃了 TCP 源碼後，發現並不是這樣的。

所以，今天就來討論下這個問題，「**在 TCP 正常揮手過程中，處於 TIME_WAIT 狀態的連接，收到相同四元組的 SYN 後會發生什麼？**」

問題現象如下圖，左邊是服務端，右邊是客戶端：

![圖片](https://img-blog.csdnimg.cn/img_convert/74b53919396dcda634cfd5b5795cbf16.png)

## 先說結論

在跟大家分析 TCP 源碼前，我先跟大家直接說下結論。

針對這個問題，**關鍵是要看 SYN 的「序列號和時間戳」是否合法**，因為處於 TIME_WAIT 狀態的連接收到 SYN 後，會判斷 SYN 的「序列號和時間戳」是否合法，然後根據判斷結果的不同做不同的處理。

先跟大家說明下， 什麼是「合法」的 SYN？

- **合法 SYN**：客戶端的  SYN 的「序列號」比服務端「期望下一個收到的序列號」要**大**，**並且** SYN 的「時間戳」比服務端「最後收到的報文的時間戳」要**大**。
- **非法 SYN**：客戶端的  SYN 的「序列號」比服務端「期望下一個收到的序列號」要**小**，**或者** SYN 的「時間戳」比服務端「最後收到的報文的時間戳」要**小**。

上面 SYN 合法判斷是基於雙方都開啟了 TCP 時間戳機制的場景，如果雙方都沒有開啟 TCP 時間戳機制，則 SYN 合法判斷如下：

- **合法 SYN**：客戶端的  SYN 的「序列號」比服務端「期望下一個收到的序列號」要**大**。
- **非法 SYN**：客戶端的  SYN 的「序列號」比服務端「期望下一個收到的序列號」要**小**。

### 收到合法 SYN

如果處於 TIME_WAIT 狀態的連接收到「合法的 SYN 」後，**就會重用此四元組連接，跳過 2MSL 而轉變為 SYN_RECV 狀態，接著就能進行建立連接過程**。

用下圖作為例子，雙方都啟用了 TCP 時間戳機制，TSval 是發送報文時的時間戳：

![圖片](https://img-blog.csdnimg.cn/img_convert/39d0d04adf72fe3d37623acff9ae2507.png)

上圖中，在收到第三次揮手的 FIN 報文時，會記錄該報文的 TSval （21），用 ts_recent 變量保存。然後會計算下一次期望收到的序列號，本次例子下一次期望收到的序列號就是 301，用 rcv_nxt 變量保存。

處於 TIME_WAIT 狀態的連接收到 SYN 後，**因為 SYN 的 seq（400） 大於 rcv_nxt（301），並且 SYN 的 TSval（30） 大於 ts_recent（21），所以是一個「合法的 SYN」，於是就會重用此四元組連接，跳過 2MSL 而轉變為 SYN_RECV 狀態，接著就能進行建立連接過程。**

### 收到非法的 SYN

如果處於 TIME_WAIT 狀態的連接收到「非法的 SYN 」後，就會**再回復一個第四次揮手的 ACK 報文，客戶端收到後，發現並不是自己期望收到確認號（ack num），就回 RST 報文給服務端**。

用下圖作為例子，雙方都啟用了 TCP 時間戳機制，TSval 是發送報文時的時間戳：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/network/tcp/tw收到不合法.png)

上圖中，在收到第三次揮手的 FIN 報文時，會記錄該報文的 TSval （21），用 ts_recent 變量保存。然後會計算下一次期望收到的序列號，本次例子下一次期望收到的序列號就是 301，用 rcv_nxt 變量保存。

處於 TIME_WAIT 狀態的連接收到 SYN 後，**因為 SYN 的 seq（200） 小於 rcv_nxt（301），所以是一個「非法的 SYN」，就會再回復一個與第四次揮手一樣的 ACK 報文，客戶端收到後，發現並不是自己期望收到確認號，就回 RST 報文給服務端**。

> PS：這裡先埋一個疑問，處於 TIME_WAIT 狀態的連接，收到 RST 會斷開連接嗎？

## 源碼分析

下面源碼分析是基於 Linux 4.2 版本的內核代碼。

Linux 內核在收到 TCP 報文後，會執行 `tcp_v4_rcv` 函數，在該函數和 TIME_WAIT 狀態相關的主要代碼如下：

```c
int tcp_v4_rcv(struct sk_buff *skb)
{
  struct sock *sk;
 ...
  //收到報文後，會調用此函數，查找對應的 sock
 sk = __inet_lookup_skb(&tcp_hashinfo, skb, __tcp_hdrlen(th), th->source,
          th->dest, sdif, &refcounted);
 if (!sk)
  goto no_tcp_socket;

process:
  //如果連接的狀態為 time_wait，會跳轉到 do_time_wait
 if (sk->sk_state == TCP_TIME_WAIT)
  goto do_time_wait;

...

do_time_wait:
  ...
  //由tcp_timewait_state_process函數處理在 time_wait 狀態收到的報文
 switch (tcp_timewait_state_process(inet_twsk(sk), skb, th)) {
    // 如果是TCP_TW_SYN，那麼允許此 SYN 重建連接
    // 即允許TIM_WAIT狀態躍遷到SYN_RECV
    case TCP_TW_SYN: {
      struct sock *sk2 = inet_lookup_listener(....);
      if (sk2) {
          ....
          goto process;
      }
    }
    // 如果是TCP_TW_ACK，那麼，返回記憶中的ACK
    case TCP_TW_ACK:
      tcp_v4_timewait_ack(sk, skb);
      break;
    // 如果是TCP_TW_RST直接發送RESET包
    case TCP_TW_RST:
      tcp_v4_send_reset(sk, skb);
      inet_twsk_deschedule_put(inet_twsk(sk));
      goto discard_it;
     // 如果是TCP_TW_SUCCESS則直接丟棄此包，不做任何響應
    case TCP_TW_SUCCESS:;
 }
 goto discard_it;
}
```

該代碼的過程：

1. 接收到報文後，會調用 `__inet_lookup_skb()` 函數查找對應的 sock 結構；
2. 如果連接的狀態是 `TIME_WAIT`，會跳轉到 do_time_wait 處理；
3. 由 `tcp_timewait_state_process()` 函數來處理收到的報文，處理後根據返回值來做相應的處理。

先跟大家說下，如果收到的 SYN 是合法的，`tcp_timewait_state_process()` 函數就會返回 `TCP_TW_SYN`，然後重用此連接。如果收到的 SYN 是非法的，`tcp_timewait_state_process()` 函數就會返回 `TCP_TW_ACK`，然後會回上次發過的 ACK。

接下來，看 `tcp_timewait_state_process()` 函數是如何判斷 SYN 包的。

```c
enum tcp_tw_status
tcp_timewait_state_process(struct inet_timewait_sock *tw, struct sk_buff *skb,
      const struct tcphdr *th)
{
 ...
  //paws_reject 為 false，表示沒有發生時間戳迴繞
  //paws_reject 為 true，表示發生了時間戳迴繞
 bool paws_reject = false;

 tmp_opt.saw_tstamp = 0;
  //TCP頭中有選項且舊連接開啟了時間戳選項
 if (th->doff > (sizeof(*th) >> 2) && tcptw->tw_ts_recent_stamp) { 
  //解析選項
    tcp_parse_options(twsk_net(tw), skb, &tmp_opt, 0, NULL);

  if (tmp_opt.saw_tstamp) {
   ...
      //檢查收到的報文的時間戳是否發生了時間戳迴繞
   paws_reject = tcp_paws_reject(&tmp_opt, th->rst);
  }
 }

....

  //是SYN包、沒有RST、沒有ACK、時間戳沒有迴繞，並且序列號也沒有迴繞，
 if (th->syn && !th->rst && !th->ack && !paws_reject &&
     (after(TCP_SKB_CB(skb)->seq, tcptw->tw_rcv_nxt) ||
      (tmp_opt.saw_tstamp && //新連接開啟了時間戳
       (s32)(tcptw->tw_ts_recent - tmp_opt.rcv_tsval) < 0))) { //時間戳沒有迴繞
    // 初始化序列號
    u32 isn = tcptw->tw_snd_nxt + 65535 + 2; 
    if (isn == 0)
      isn++;
    TCP_SKB_CB(skb)->tcp_tw_isn = isn;
    return TCP_TW_SYN; //允許重用TIME_WAIT四元組重新建立連接
 }


 if (!th->rst) {
    // 如果時間戳迴繞，或者報文裡包含ack，則將 TIMEWAIT 狀態的持續時間重新延長
  if (paws_reject || th->ack)
    inet_twsk_schedule(tw, &tcp_death_row, TCP_TIMEWAIT_LEN,
        TCP_TIMEWAIT_LEN);

     // 返回TCP_TW_ACK, 發送上一次的 ACK
    return TCP_TW_ACK;
 }
 inet_twsk_put(tw);
 return TCP_TW_SUCCESS;
}
```

如果雙方啟用了 TCP 時間戳機制，就會通過 `tcp_paws_reject()` 函數來判斷時間戳是否發生了迴繞，也就是「當前收到的報文的時間戳」是否大於「上一次收到的報文的時間戳」：

- 如果大於，就說明沒有發生時間戳繞回，函數返回 false。
- 如果小於，就說明發生了時間戳迴繞，函數返回 true。

從源碼可以看到，當收到 SYN 包後，如果該 SYN 包的時間戳沒有發生迴繞，也就是時間戳是遞增的，並且 SYN 包的序列號也沒有發生迴繞，也就是 SYN 的序列號「大於」下一次期望收到的序列號。就會初始化一個序列號，然後返回 TCP_TW_SYN，接著就重用該連接，也就跳過 2MSL 而轉變為 SYN_RECV 狀態，接著就能進行建立連接過程。

如果雙方都沒有啟用 TCP 時間戳機制，就只需要判斷 SYN 包的序列號有沒有發生迴繞，如果 SYN 的序列號大於下一次期望收到的序列號，就可以跳過 2MSL，重用該連接。

如果 SYN 包是非法的，就會返回 TCP_TW_ACK，接著就會發送與上一次一樣的 ACK 給對方。

## 在 TIME_WAIT 狀態，收到 RST 會斷開連接嗎？

在前面我留了一個疑問，處於 TIME_WAIT 狀態的連接，收到 RST 會斷開連接嗎？

會不會斷開，關鍵看 `net.ipv4.tcp_rfc1337` 這個內核參數（默認情況是為 0）：

- 如果這個參數設置為 0， 收到 RST 報文會提前結束 TIME_WAIT 狀態，釋放連接。
- 如果這個參數設置為 1， 就會丟掉 RST 報文。

源碼處理如下：

```c
enum tcp_tw_status
tcp_timewait_state_process(struct inet_timewait_sock *tw, struct sk_buff *skb,
      const struct tcphdr *th)
{
....
  //rst報文的時間戳沒有發生迴繞
 if (!paws_reject &&
     (TCP_SKB_CB(skb)->seq == tcptw->tw_rcv_nxt &&
      (TCP_SKB_CB(skb)->seq == TCP_SKB_CB(skb)->end_seq || th->rst))) {

      //處理rst報文
      if (th->rst) {
        //不開啟這個選項，當收到 RST 時會立即回收tw，但這樣做是有風險的
        if (twsk_net(tw)->ipv4.sysctl_tcp_rfc1337 == 0) {
          kill:
          //刪除tw定時器，並釋放tw
          inet_twsk_deschedule_put(tw);
          return TCP_TW_SUCCESS;
        }
      } else {
        //將 TIMEWAIT 狀態的持續時間重新延長
        inet_twsk_reschedule(tw, TCP_TIMEWAIT_LEN);
      }

      ...
      return TCP_TW_SUCCESS;
    }
}
```

TIME_WAIT 狀態收到 RST 報文而釋放連接，這樣等於跳過 2MSL 時間，這麼做還是有風險。

sysctl_tcp_rfc1337 這個參數是在 rfc 1337 文檔提出來的，目的是避免因為 TIME_WAIT 狀態收到 RST 報文而跳過  2MSL 的時間，文檔裡也給出跳過  2MSL 時間會有什麼潛在問題。

TIME_WAIT 狀態之所以要持續 2MSL 時間，主要有兩個目的：

- 防止歷史連接中的數據，被後面相同四元組的連接錯誤的接收；
- 保證「被動關閉連接」的一方，能被正確的關閉；

詳細的為什麼要設計 TIME_WAIT 狀態，我在這篇有詳細說明：[如果 TIME_WAIT 狀態持續時間過短或者沒有，會有什麼問題？](https://mp.weixin.qq.com/s?__biz=MzUxODAzNDg4NQ==&mid=2247502380&idx=1&sn=7b82818a5fb6f1127d17f0ded550c4bd&scene=21#wechat_redirect)

雖然 TIME_WAIT 狀態持續的時間是有一點長，顯得很不友好，但是它被設計來就是用來避免發生亂七八糟的事情。

《UNIX網絡編程》一書中卻說道：**TIME_WAIT 是我們的朋友，它是有助於我們的，不要試圖避免這個狀態，而是應該弄清楚它**。

所以，我個人覺得將 `net.ipv4.tcp_rfc1337` 設置為 1 會比較安全。

## 總結

在 TCP 正常揮手過程中，處於 TIME_WAIT 狀態的連接，收到相同四元組的 SYN 後會發生什麼？

如果雙方開啟了時間戳機制：

- 如果客戶端的  SYN 的「序列號」比服務端「期望下一個收到的序列號」要**大**，**並且**SYN 的「時間戳」比服務端「最後收到的報文的時間戳」要**大**。那麼就會重用該四元組連接，跳過 2MSL 而轉變為 SYN_RECV 狀態，接著就能進行建立連接過程。
- 如果客戶端的  SYN 的「序列號」比服務端「期望下一個收到的序列號」要**小**，**或者**SYN 的「時間戳」比服務端「最後收到的報文的時間戳」要**小**。那麼就會**再回復一個第四次揮手的 ACK 報文，客戶端收到後，發現並不是自己期望收到確認號，就回 RST 報文給服務端**。

在 TIME_WAIT 狀態，收到 RST 會斷開連接嗎？

- 如果 `net.ipv4.tcp_rfc1337` 參數為 0，則提前結束 TIME_WAIT 狀態，釋放連接。
- 如果 `net.ipv4.tcp_rfc1337` 參數為 1，則會丟掉該 RST 報文。

完！

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)