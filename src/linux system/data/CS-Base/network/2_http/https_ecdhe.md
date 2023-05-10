# 3.4 HTTPS ECDHE 握手解析

HTTPS 常用的密鑰交換算法有兩種，分別是 RSA 和 ECDHE 算法。

其中，RSA 是比較傳統的密鑰交換算法，它不具備前向安全的性質，因此現在很少服務器使用的。而 ECDHE 算法具有前向安全，所以被廣泛使用。

我在上一篇已經介紹了 [RSA 握手的過程](https://mp.weixin.qq.com/s/U9SRLE7jZTB6lUZ6c8gTKg)，今天這一篇就「從理論再到實戰抓包」介紹 **ECDHE 算法**。


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ecdhe提綱.png)

---

## 離散對數

ECDHE 密鑰協商算法是 DH 算法演進過來的，所以我們先從 DH 算法說起。

DH 算法是非對稱加密算法， 因此它可以用於密鑰交換，該算法的核心數學思想是**離散對數**。

是不是聽到這個數學概念就慫了？不怕，這次不會說離散對數推導的過程，只簡單提一下它的數學公式。

離散對數是「離散 + 對數」的兩個數學概念的組合，所以我們先來複習一遍對數。

要說起對數，必然要說指數，因為它們是互為反函數，指數就是冪運算，對數是指數的逆運算。

舉個栗子，如果以 2 作為底數，那麼指數和對數運算公式，如下圖所示：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/指數與對數.png)

那麼對於底數為 2 的時候， 32 的對數是 5，64 的對數是 6，計算過程如下：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/求對數.png)

對數運算的取值是可以連續的，而離散對數的取值是不能連續的，因此也以「離散」得名，

離散對數是在對數運算的基礎上加了「模運算」，也就說取餘數，對應編程語言的操作符是「%」，也可以用 mod 表示。離散對數的概念如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/離散對數.png)

上圖的，底數 a 和模數 p 是離散對數的公共參數，也就說是公開的，b 是真數，i 是對數。知道了對數，就可以用上面的公式計算出真數。但反過來，知道真數卻很難推算出對數。

**特別是當模數 p 是一個很大的質數，即使知道底數 a 和真數 b ，在現有的計算機的計算水平是幾乎無法算出離散對數的，這就是 DH 算法的數學基礎。**



---

## DH 算法

認識了離散對數，我們來看看 DH 算法是如何密鑰交換的。

現假設小紅和小明約定使用 DH 算法來交換密鑰，那麼基於離散對數，小紅和小明需要先確定模數和底數作為算法的參數，這兩個參數是公開的，用 P 和 G 來代稱。

然後小紅和小明各自生成一個隨機整數作為**私鑰**，雙方的私鑰要各自嚴格保管，不能洩漏，小紅的私鑰用 a 代稱，小明的私鑰用 b 代稱。

現在小紅和小明雙方都有了 P 和 G 以及各自的私鑰，於是就可以計算出**公鑰**：

- 小紅的公鑰記作 A，A = G ^ a ( mod P )；
- 小明的公鑰記作 B，B = G ^ b ( mod P )；

A 和 B 也是公開的，因為根據離散對數的原理，從真數（A 和 B）反向計算對數 a 和 b 是非常困難的，至少在現有計算機的計算能力是無法破解的，如果量子計算機出來了，那就有可能被破解，當然如果量子計算機真的出來了，那麼密鑰協商算法就要做大的升級了。


雙方交換各自 DH 公鑰後，小紅手上共有 5 個數：P、G、a、A、B，小明手上也同樣共有 5 個數：P、G、b、B、A。

然後小紅執行運算： B ^ a ( mod P )，其結果為 K，因為離散對數的冪運算有交換律，所以小明執行運算： A ^ b ( mod P )，得到的結果也是 K。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/dh算法.png)

這個 K 就是小紅和小明之間用的**對稱加密密鑰**，可以作為會話密鑰使用。

可以看到，整個密鑰協商過程中，小紅和小明公開了 4 個信息：P、G、A、B，其中 P、G 是算法的參數，A 和 B 是公鑰，而 a、b 是雙方各自保管的私鑰，黑客無法獲取這 2 個私鑰，因此黑客只能從公開的 P、G、A、B 入手，計算出離散對數（私鑰）。

前面也多次強調， 根據離散對數的原理，如果 P 是一個大數，在現有的計算機的計算能力是很難破解出 私鑰 a、b 的，破解不出私鑰，也就無法計算出會話密鑰，因此 DH 密鑰交換是安全的。

---

## DHE 算法

根據私鑰生成的方式，DH 算法分為兩種實現：

- static DH 算法，這個是已經被廢棄了；
- DHE 算法，現在常用的；

static DH 算法裡有一方的私鑰是靜態的，也就說每次密鑰協商的時候有一方的私鑰都是一樣的，一般是服務器方固定，即 a 不變，客戶端的私鑰則是隨機生成的。

於是，DH 交換密鑰時就只有客戶端的公鑰是變化，而服務端公鑰是不變的，那麼隨著時間延長，黑客就會截獲海量的密鑰協商過程的數據，因為密鑰協商的過程有些數據是公開的，黑客就可以依據這些數據暴力破解出服務器的私鑰，然後就可以計算出會話密鑰了，於是之前截獲的加密數據會被破解，所以 **static DH 算法不具備前向安全性**。

既然固定一方的私鑰有被破解的風險，那麼幹脆就讓雙方的私鑰在每次密鑰交換通信時，都是隨機生成的、臨時的，這個方式也就是 DHE 算法，E 全稱是 ephemeral（臨時性的）。

所以，即使有個牛逼的黑客破解了某一次通信過程的私鑰，其他通信過程的私鑰仍然是安全的，因為**每個通信過程的私鑰都是沒有任何關係的，都是獨立的，這樣就保證了「前向安全」**。


----

## ECDHE 算法

DHE 算法由於計算性能不佳，因為需要做大量的乘法，為了提升 DHE 算法的性能，所以就出現了現在廣泛用於密鑰交換算法 ——  **ECDHE 算法**。

ECDHE 算法是在 DHE 算法的基礎上利用了 ECC 橢圓曲線特性，可以用更少的計算量計算出公鑰，以及最終的會話密鑰。

小紅和小明使用 ECDHE 密鑰交換算法的過程：

- 雙方事先確定好使用哪種橢圓曲線，和曲線上的基點 G，這兩個參數都是公開的；
- 雙方各自隨機生成一個隨機數作為**私鑰d**，並與基點 G相乘得到**公鑰Q**（Q = dG），此時小紅的公私鑰為 Q1 和 d1，小明的公私鑰為 Q2 和 d2；
- 雙方交換各自的公鑰，最後小紅計算點（x1，y1） = d1Q2，小明計算點（x2，y2） = d2Q1，由於橢圓曲線上是可以滿足乘法交換和結合律，所以 d1Q2 = d1d2G = d2d1G = d2Q1 ，因此**雙方的 x 座標是一樣的，所以它是共享密鑰，也就是會話密鑰**。

這個過程中，雙方的私鑰都是隨機、臨時生成的，都是不公開的，即使根據公開的信息（橢圓曲線、公鑰、基點 G）也是很難計算出橢圓曲線上的離散對數（私鑰）。

---


## ECDHE 握手過程

知道了 ECDHE 算法基本原理後，我們就結合實際的情況來看看。  

我用 Wireshark 工具抓了用 ECDHE 密鑰協商算法的 TSL 握手過程，可以看到是四次握手：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_tls握手.png)

細心的小夥伴應該發現了，**使用了 ECDHE，在 TLS 第四次握手前，客戶端就已經發送了加密的 HTTP 數據**，而對於 RSA 握手過程，必須要完成 TLS 四次握手，才能傳輸應用數據。

所以，**ECDHE 相比 RSA 握手過程省去了一個消息往返的時間**，這個有點「搶跑」的意思，它被稱為是「*TLS False Start*」，跟「*TCP Fast Open*」有點像，都是在還沒連接完全建立前，就發送了應用數據，這樣便提高了傳輸的效率。

接下來，分析每一個 ECDHE 握手過程。

### TLS 第一次握手

客戶端首先會發一個「**Client Hello**」消息，消息裡面有客戶端使用的 TLS 版本號、支持的密碼套件列表，以及生成的**隨機數（*Client Random*）**。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_clinethello.png)


### TLS 第二次握手

服務端收到客戶端的「打招呼」，同樣也要回禮，會返回「**Server Hello**」消息，消息面有服務器確認的 TLS 版本號，也給出了一個**隨機數（*Server Random*）**，然後從客戶端的密碼套件列表選擇了一個合適的密碼套件。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_serverhello.png)

不過，這次選擇的密碼套件就和 RSA 不一樣了，我們來分析一下這次的密碼套件的意思。

「 TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384」

- 密鑰協商算法使用 ECDHE；
- 簽名算法使用 RSA；
- 握手後的通信使用 AES 對稱算法，密鑰長度 256 位，分組模式是 GCM；
- 摘要算法使用 SHA384；

接著，服務端為了證明自己的身份，發送「**Certificate**」消息，會把證書也發給客戶端。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_certificate.png)


這一步就和 RSA 握手過程有很大到區別了，因為服務端選擇了 ECDHE 密鑰協商算法，所以會在發送完證書後，發送「**Server Key Exchange**」消息。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_serverkey.png)


這個過程服務器做了三件事：

- 選擇了**名為 x25519 的橢圓曲線**，選好了橢圓曲線相當於橢圓曲線基點 G 也定好了，這些都會公開給客戶端；
- 生成隨機數作為服務端橢圓曲線的私鑰，保留到本地；
- 根據基點 G 和私鑰計算出**服務端的橢圓曲線公鑰**，這個會公開給客戶端。

為了保證這個橢圓曲線的公鑰不被第三方篡改，服務端會用 RSA 簽名算法給服務端的橢圓曲線公鑰做個簽名。


隨後，就是「**Server Hello Done**」消息，服務端跟客戶端表明：“這些就是我提供的信息，打招呼完畢”。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_serverhellodone.png)


至此，TLS 兩次握手就已經完成了，目前客戶端和服務端通過明文共享了這幾個信息：**Client Random、Server Random 、使用的橢圓曲線、橢圓曲線基點 G、服務端橢圓曲線的公鑰**，這幾個信息很重要，是後續生成會話密鑰的材料。

### TLS 第三次握手

客戶端收到了服務端的證書後，自然要校驗證書是否合法，如果證書合法，那麼服務端到身份就是沒問題的。校驗證書的過程會走證書鏈逐級驗證，確認證書的真實性，再用證書的公鑰驗證簽名，這樣就能確認服務端的身份了，確認無誤後，就可以繼續往下走。

客戶端會生成一個隨機數作為客戶端橢圓曲線的私鑰，然後再根據服務端前面給的信息，生成**客戶端的橢圓曲線公鑰**，然後用「**Client Key Exchange**」消息發給服務端。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_clientkeyexchange.png)


至此，雙方都有對方的橢圓曲線公鑰、自己的橢圓曲線私鑰、橢圓曲線基點 G。於是，雙方都就計算出點（x，y），其中 x 座標值雙方都是一樣的，前面說 ECDHE 算法時候，說  x 是會話密鑰，**但實際應用中，x 還不是最終的會話密鑰**。

還記得 TLS 握手階段，客戶端和服務端都會生成了一個隨機數傳遞給對方嗎？

**最終的會話密鑰，就是用「客戶端隨機數 + 服務端隨機數 + x（ECDHE 算法算出的共享密鑰） 」三個材料生成的**。

之所以這麼麻煩，是因為 TLS 設計者不信任客戶端或服務器「偽隨機數」的可靠性，為了保證真正的完全隨機，把三個不可靠的隨機數混合起來，那麼「隨機」的程度就非常高了，足夠讓黑客計算不出最終的會話密鑰，安全性更高。


算好會話密鑰後，客戶端會發一個「**Change Cipher Spec**」消息，告訴服務端後續改用對稱算法加密通信。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_schangecipherspec.png)


接著，客戶端會發「**Encrypted Handshake Message**」消息，把之前發送的數據做一個摘要，再用對稱密鑰加密一下，讓服務端做個驗證，驗證下本次生成的對稱密鑰是否可以正常使用。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/ech_encryptedhandshakemessage.png)


### TLS 第四次握手

最後，服務端也會有一個同樣的操作，發「**Change Cipher Spec**」和「**Encrypted Handshake Message**」消息，如果雙方都驗證加密和解密沒問題，那麼握手正式完成。於是，就可以正常收發加密的 HTTP 請求和響應了。

----

## 總結

RSA  和 ECDHE 握手過程的區別：

- RSA 密鑰協商算法「不支持」前向保密，ECDHE 密鑰協商算法「支持」前向保密；
- 使用了 RSA 密鑰協商算法，TLS 完成四次握手後，才能進行應用數據傳輸，而對於 ECDHE 算法，客戶端可以不用等服務端的最後一次 TLS 握手，就可以提前發出加密的 HTTP 數據，節省了一個消息的往返時間（這個是 RFC 文檔規定的，具體原因文檔沒有說明，所以這點我也不太明白）；
- 使用 ECDHE， 在 TLS 第 2 次握手中，會出現服務器端發出的「Server Key Exchange」消息，而 RSA 握手過程沒有該消息；

---

參考資料：

1. https://zh.wikipedia.org/wiki/橢圓曲線迪菲-赫爾曼金鑰交換
2. https://zh.wikipedia.org/wiki/橢圓曲線
3. https://zh.wikipedia.org/wiki/迪菲-赫爾曼密鑰交換
4. https://time.geekbang.org/column/article/148188
5. https://zhuanlan.zhihu.com/p/106967180

---

哈嘍，我是小林，就愛圖解計算機基礎，如果文章對你有幫助，別忘記關注哦！

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

