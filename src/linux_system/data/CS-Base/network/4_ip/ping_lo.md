# 5.3 斷網了，還能 ping 通 127.0.0.1 嗎？

> 來源：公眾號@小白debug
>
> 原文地址：[斷網了，還能 ping 通 127.0.0.1 嗎？](https://mp.weixin.qq.com/s/qqfnyw4wKFjJqnV1eoRDhw)

你**女神愛不愛你**，你問她，她可能不會告訴你。

但**網通不通**，你 `ping` 一下就知道了。

可能看到標題，你就知道答案了，但是你瞭解背後的原因嗎？

那如果把 `127.0.0.1` 換成 `0.0.0.0` 或 `localhost` 會怎麼樣呢？你知道這幾個`IP`有什麼區別嗎？

以前面試的時候就遇到過這個問題，大家看個動圖瞭解下面試官和我當時的場景，求當時我的心裡陰影面積。

![圖片](https://img-blog.csdnimg.cn/img_convert/c3a97f36607c0e7ef6805bfba482a060.gif)

話不多說，我們直接開車。

拔掉網線，斷網。

![圖片](https://img-blog.csdnimg.cn/img_convert/5137bc7bce08dc60cfa2f8152b738dfd.jpeg)

然後在控制檯輸入`ping 127.0.0.1`。

```shell
$ ping 127.0.0.1
PING 127.0.0.1 (127.0.0.1): 56 data bytes
64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.080 ms
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.093 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.074 ms
64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.079 ms
64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.079 ms
^C
--- 127.0.0.1 ping statistics ---
5 packets transmitted, 5 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 0.074/0.081/0.093/0.006 ms
```

說明，拔了網線，`ping 127.0.0.1` 是**能ping通的**。

其實這篇文章看到這裡，標題前半個問題已經被回答了。但是我們可以再想深一點。

為什麼斷網了還能 `ping` 通 `127.0.0.1` 呢？

**這能說明你不用交網費就能上網嗎？**

**不能。**

首先我們需要進入基礎科普環節。

不懂的同學看了就懂了，懂的看了就當查漏補缺吧。

## 什麼是127.0.0.1

首先，這是個 `IPV4` 地址。

`IPV4` 地址有 `32` 位，一個字節有 `8` 位，共 `4` 個字節。

其中**127 開頭的都屬於迴環地址**，也是 `IPV4` 的特殊地址，沒什麼道理，就是人為規定的。

而`127.0.0.1`是**眾多**迴環地址中的一個。之所以不是 `127.0.0.2` ，而是 `127.0.0.1`，是因為源碼裡就是這麼定義的，也沒什麼道理。

```c
/* Address to loopback in software to local host.  */
#define    INADDR_LOOPBACK     0x7f000001  /* 127.0.0.1   */
```

![圖片](https://img-blog.csdnimg.cn/img_convert/fa904fbcf66cc7abf510a8dc16f867fa.png)

`IPv4` 的地址是 `32` 位的，2的32次方，大概是`40+億`。地球光人口就76億了，40億IP這點量，**塞牙縫都不夠**，實際上**IP也確實用完**了。

所以就有了`IPV6`， `IPv6` 的地址是 `128` 位的，大概是2的128次方≈**10的38次方**。據說地球的沙子數量大概是 **10的23次方**，所以IPV6的IP可以認為用不完。

IPV4以8位一組，每組之間用 **.** 號隔開。

IPV6就以16位為一組，每組之間用 **:** 號隔開。如果全是0，那麼可以省略不寫。

![圖片](https://img-blog.csdnimg.cn/img_convert/e841adeeecf9451e1aca296d5c7a7f30.png)

在IPV4下的迴環地址是 `127.0.0.1`，在`IPV6`下，表達為 `::1` 。中間把**連續的0**給省略了，之所以不是**7個 冒號**，而是**2個冒號:** ， 是因為一個 IPV6 地址中**只允許出現⼀次兩個連續的冒號**。

> 多說一句：在IPV4下用的是 **ping 127.0.0.1** 命令。在IPV6下用的是 **ping6  ::1** 命令。

## 什麼是 ping

ping 是應用層命令，可以理解為它跟遊戲或者聊天軟件屬於同一層。只不過聊天軟件可以收發消息，還能點個贊什麼的，有很多複雜的功能。而 ping 作為一個小軟件，它的功能比較簡單，就是**嘗試**發送一個小小的消息到目標機器上，判斷目的機器是否**可達**，其實也就是判斷目標機器網絡是否能連通。

ping應用的底層，用的是網絡層的**ICMP協議**。

IP和ICMP和Ping所在分層

雖然ICMP協議和IP協議**都屬於網絡層協議**，但其實**ICMP也是利用了IP協議進行消息的傳輸**。

![圖片](https://img-blog.csdnimg.cn/img_convert/8e0aba146432baeb407ab445292c8019.png)

所以，大家在這裡完全可以簡單的理解為 ping 某個IP 就是往某個IP地址發個消息。

## TCP發數據和ping的區別

一般情況下，我們會使用 TCP 進行網絡數據傳輸，那麼我們可以看下它和 ping 的區別。

*PS：下圖中有一處畫錯了，右邊是 tcp 數據，而不是 ping 數據，我偷懶就不重畫了*。

![圖片](https://img-blog.csdnimg.cn/img_convert/eb0963a11439dff361dbe0e7a8876abd.png)

ping和其他應用層軟件都屬於**應用層**。

那麼我們橫向對比一下，比方說聊天軟件，如果用的是TCP的方式去發送消息。

為了發送消息，那就得先知道往哪發。linux裡萬物皆文件，那你要發消息的目的地，也是個文件，這裡就引出了socket 的概念。

要使用 `socket` , 那麼首先需要創建它。

在 TCP 傳輸中創建的方式是  `socket(AF_INET, SOCK_STREAM, 0);`，其中 `AF_INET` 表示將使用 IPV4 裡 **host:port** 的方式去解析待會你輸入的網絡地址。`SOCK_STREAM` 是指使用面向字節流的 TCP 協議，**工作在傳輸層**。

創建好了 `socket` 之後，就可以愉快的把要傳輸的數據寫到這個文件裡。調用 socket 的`sendto`接口的過程中進程會從**用戶態進入到內核態**，最後會調用到 `sock_sendmsg` 方法。

然後進入傳輸層，帶上`TCP`頭。網絡層帶上`IP`頭，數據鏈路層帶上 `MAC`頭等一系列操作後。進入網卡的**發送隊列 ring buffer** ，順著網卡就發出去了。

回到 `ping` ， 整個過程也基本跟 `TCP` 發數據類似，差異的地方主要在於，創建 `socket` 的時候用的是  `socket(AF_INET,SOCK_RAW,IPPROTO_ICMP)`，`SOCK_RAW` 是原始套接字 ，**工作在網絡層**， 所以構建`ICMP`（網絡層協議）的數據，是再合適不過了。ping 在進入內核態後最後也是調用的  `sock_sendmsg` 方法，進入到網絡層後加上**ICMP和IP頭**後，數據鏈路層加上**MAC頭**，也是順著網卡發出。因此 本質上ping 跟 普通應用發消息 在程序流程上沒太大差別。

這也解釋了**為什麼當你發現懷疑網絡有問題的時候，別人第一時間是問你能ping通嗎？** 因為可以簡單理解為ping就是自己組了個數據包，讓系統按著其他軟件發送數據的路徑往外發一遍，能通的話說明其他軟件發的數據也能通。

## 為什麼斷網了還能 ping 通 127.0.0.1

前面提到，有網的情況下，ping 最後是**通過網卡**將數據發送出去的。

那麼斷網的情況下，網卡已經不工作了，ping 迴環地址卻一切正常，我們可以看下這種情況下的工作原理。

![圖片](https://img-blog.csdnimg.cn/img_convert/c1019a8be584b27c4fc8b8abda9d3cf1.png)

從應用層到傳輸層再到網絡層。這段路徑跟ping外網的時候是幾乎是一樣的。到了網絡層，系統會根據目的IP，在路由表中獲取對應的**路由信息**，而這其中就包含選擇**哪個網卡**把消息發出。

當發現**目標IP是外網IP**時，會從"真網卡"發出。

當發現**目標IP是迴環地址**時，就會選擇**本地網卡**。

本地網卡，其實就是個 **"** **假網卡** **"**，它不像"真網卡"那樣有個`ring buffer`什麼的，"假網卡"會把數據推到一個叫 `input_pkt_queue` 的 **鏈表** 中。這個鏈表，其實是所有網卡共享的，上面掛著發給本機的各種消息。消息被髮送到這個鏈表後，會再觸發一個**軟中斷**。

專門處理軟中斷的工具人 **"** **ksoftirqd** **"**（這是個**內核線程**），它在收到軟中斷後就會立馬去鏈表裡把消息取出，然後順著數據鏈路層、網絡層等層層往上傳遞最後給到應用程序。

![圖片](https://img-blog.csdnimg.cn/img_convert/a207c14a5416f44e9dbf0fe0a41179e4.png)

ping 迴環地址和**通過TCP等各種協議發送數據到迴環地址**都是走這條路徑。整條路徑從發到收，都沒有經過"真網卡"。**之所以127.0.0.1叫本地迴環地址，可以理解為，消息發出到這個地址上的話，就不會出網絡，在本機打個轉就又回來了。** 所以斷網，依然能 `ping` 通 `127.0.0.1`。

## ping迴環地址和ping本機地址有什麼區別

我們在mac裡執行 `ifconfig` 。

```shell
$ ifconfig
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
    inet 127.0.0.1 netmask 0xff000000
    ...
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
    inet 192.168.31.6 netmask 0xffffff00 broadcast 192.168.31.255
    ...
```

能看到 **lo0**，表示本地迴環接口，對應的地址，就是我們前面提到的 **127.0.0.1** ，也就是**迴環地址**。

和 **eth0**，表示本機第一塊網卡，對應的IP地址是**192.168.31.6**，管它叫**本機IP**。

之前一直認為ping本機IP的話會通過"真網卡"出去，然後遇到第一個路由器，再發回來到本機。

為了驗證這個說法，可以進行抓包，但結果跟上面的說法並不相同。

ping 127.0.0.1:

![圖片](https://img-blog.csdnimg.cn/img_convert/bc2765b1d6d3e37a5663f98085198926.png)

ping 本機地址:

![圖片](https://img-blog.csdnimg.cn/img_convert/50cd584f9f82aee8d3d9bfaf7d910cb8.png)

可以看到 ping 本機IP 跟 ping 迴環地址一樣，相關的網絡數據，都是走的  **lo0**，本地迴環接口，也就是前面提到的**"假網卡"**。

只要走了本地迴環接口，那數據都不會發送到網絡中，在本機網絡協議棧中兜一圈，就發回來了。因此 **ping迴環地址和ping本機地址沒有區別**。

## 127.0.0.1 和 localhost 以及 0.0.0.0 有區別嗎

回到文章開頭動圖裡的提問，算是面試八股文裡的老常客了。

以前第一次用 `nginx` 的時候，發現用這幾個 `IP`，都能正常訪問到 `nginx` 的歡迎網頁。一度認為這幾個 `IP` 都是一樣的。

訪問127.0.0.1:80

![圖片](https://img-blog.csdnimg.cn/img_convert/12e13316a18009ce8b2983846819e270.png)

訪問localhost:80

![圖片](https://img-blog.csdnimg.cn/img_convert/2c35f573e91e94733d009384a4657859.png)

訪問0.0.0.0:80

![圖片](https://img-blog.csdnimg.cn/img_convert/ba534fdc5f21b3ab26d0b8c890bb02c3.png)

訪問本機的IP地址

![圖片](https://img-blog.csdnimg.cn/img_convert/9b31572ced19805fab02a23b22819b92.png)

但本質上還是有些區別的。

首先 `localhost` 就不叫 `IP`，它是一個域名，就跟 `"baidu.com"`,是一個形式的東西，只不過默認會把它解析為 `127.0.0.1` ，當然這可以在 `/etc/hosts` 文件下進行修改。

所以默認情況下，使用 `localhost` 跟使用  `127.0.0.1` 確實是沒區別的。

其次就是 `0.0.0.0`，執行 ping 0.0.0.0  ，是會失敗的，因為它在`IPV4`中表示的是無效的**目標地址**。

```shell
$ ping 0.0.0.0
PING 0.0.0.0 (0.0.0.0): 56 data bytes
ping: sendto: No route to host
ping: sendto: No route to host
```

但它還是很有用處的，回想下，我們啟動服務器的時候，一般會 `listen` 一個 IP 和端口，等待客戶端的連接。

如果此時 `listen` 的是本機的 `0.0.0.0` , 那麼它表示本機上的**所有IPV4地址**。

```c
/* Address to accept any incoming messages. */
#define    INADDR_ANY      ((unsigned long int) 0x00000000) /* 0.0.0.0   */
```

舉個例子。剛剛提到的 `127.0.0.1` 和 `192.168.31.6` ，都是本機的IPV4地址，如果監聽 `0.0.0.0` ，那麼用上面兩個地址，都能訪問到這個服務器。

當然， 客戶端 `connect` 時，不能使用 `0.0.0.0` 。必須指明要連接哪個服務器IP。

## 總結

- `127.0.0.1` 是**迴環地址**。`localhost`是**域名**，但默認等於 `127.0.0.1`。
- `ping` 迴環地址和 `ping` 本機地址，是一樣的，走的是**lo0 "假網卡"**，都會經過網絡層和數據鏈路層等邏輯，最後在快要出網卡前**狠狠拐了個彎**， 將數據插入到一個**鏈表**後就**軟中斷**通知 **ksoftirqd** 來進行**收數據**的邏輯，**壓根就不出網絡**。所以斷網了也能 `ping` 通迴環地址。
- 如果服務器 `listen` 的是 `0.0.0.0`，那麼此時用`127.0.0.1`和本機地址**都可以**訪問到服務。

---

哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，別忘記關注我哦！

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)