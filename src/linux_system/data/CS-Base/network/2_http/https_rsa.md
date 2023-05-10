# 3.3 HTTPS RSA 握手解析

我前面講，簡單給大家介紹了的 HTTPS 握手過程，但是還不夠細！

只講了比較基礎的部分，所以這次我們再來深入一下 HTTPS，用**實戰抓包**的方式，帶大家再來窺探一次 HTTPS。


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/https提綱.png)

對於還不知道對稱加密和非對稱加密的同學，你先複習我以前的這篇文章[「硬核！30 張圖解 HTTP 常見的面試題」，](https://mp.weixin.qq.com/s/bUy220-ect00N4gnO0697A)本篇文章默認大家已經具備了這些知識。

---

## TLS 握手過程

HTTP 由於是明文傳輸，所謂的明文，就是說客戶端與服務端通信的信息都是肉眼可見的，隨意使用一個抓包工具都可以截獲通信的內容。

所以安全上存在以下三個風險：

- *竊聽風險*，比如通信鏈路上可以獲取通信內容，用戶號容易沒。
- *篡改風險*，比如強制植入垃圾廣告，視覺汙染，用戶眼容易瞎。
- *冒充風險*，比如冒充淘寶網站，用戶錢容易沒。

HTTP**S** 在 HTTP 與 TCP 層之間加入了 TLS 協議，來解決上述的風險。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost/計算機網絡/HTTP/19-HTTPS與HTTP.png)

TLS 協議是如何解決 HTTP 的風險的呢？

- *信息加密*： HTTP 交互信息是被加密的，第三方就無法被竊取；
- *校驗機制*：校驗信息傳輸過程中是否有被第三方篡改過，如果被篡改過，則會有警告提示；
- *身份證書*：證明淘寶是真的淘寶網；

可見，有了 TLS 協議，能保證 HTTP 通信是安全的了，那麼在進行 HTTP 通信前，需要先進行 TLS 握手。TLS 的握手過程，如下圖：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/tls握手.png)


上圖簡要概述了 TLS 的握手過程，其中每一個「框」都是一個記錄（*record*），記錄是 TLS 收發數據的基本單位，類似於 TCP 裡的 segment。多個記錄可以組合成一個 TCP 包發送，所以**通常經過「四個消息」就可以完成 TLS 握手，也就是需要 2個 RTT       的時延**，然後就可以在安全的通信環境裡發送 HTTP 報文，實現 HTTPS 協議。

所以可以發現，HTTPS 是應用層協議，需要先完成 TCP 連接建立，然後走 TLS 握手過程後，才能建立通信安全的連接。

事實上，不同的密鑰交換算法，TLS 的握手過程可能會有一些區別。

這裡先簡單介紹下密鑰交換算法，因為考慮到性能的問題，所以雙方在加密應用信息時使用的是對稱加密密鑰，而對稱加密密鑰是不能被洩漏的，為了保證對稱加密密鑰的安全性，所以使用非對稱加密的方式來保護對稱加密密鑰的協商，這個工作就是密鑰交換算法負責的。

接下來，我們就以最簡單的 `RSA` 密鑰交換算法，來看看它的 TLS 握手過程。

---

## RSA 握手過程

傳統的 TLS 握手基本都是使用 RSA 算法來實現密鑰交換的，在將 TLS 證書部署服務端時，證書文件其實就是服務端的公鑰，會在 TLS 握手階段傳遞給客戶端，而服務端的私鑰則一直留在服務端，一定要確保私鑰不能被竊取。

在 RSA 密鑰協商算法中，客戶端會生成隨機密鑰，並使用服務端的公鑰加密後再傳給服務端。根據非對稱加密算法，公鑰加密的消息僅能通過私鑰解密，這樣服務端解密後，雙方就得到了相同的密鑰，再用它加密應用消息。

我用 Wireshark 工具抓了用 RSA 密鑰交換的 TLS 握手過程，你可以從下面看到，一共經歷了四次握手：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/tls四次握手.png)

對應 Wireshark 的抓包，我也畫了一幅圖，你可以從下圖很清晰地看到該過程：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/https_rsa.png)


那麼，接下來針對每一個 TLS 握手做進一步的介紹。

### TLS 第一次握手

客戶端首先會發一個「**Client Hello**」消息，字面意思我們也能理解到，這是跟服務器「打招呼」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/clienthello.png)

消息裡面有客戶端使用的 TLS 版本號、支持的密碼套件列表，以及生成的**隨機數（*Client Random*）**，這個隨機數會被服務端保留，它是生成對稱加密密鑰的材料之一。


### TLS 第二次握手

當服務端收到客戶端的「Client Hello」消息後，會確認 TLS 版本號是否支持，和從密碼套件列表中選擇一個密碼套件，以及生成**隨機數（*Server Random*）**。

接著，返回「**Server Hello**」消息，消息裡面有服務器確認的 TLS 版本號，也給出了隨機數（Server Random），然後從客戶端的密碼套件列表選擇了一個合適的密碼套件。


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/serverhello.png)

可以看到，服務端選擇的密碼套件是  “Cipher Suite: TLS_RSA_WITH_AES_128_GCM_SHA256”。

這個密碼套件看起來真讓人頭暈，好一大串，但是其實它是有固定格式和規範的。基本的形式是「**密鑰交換算法 + 簽名算法 + 對稱加密算法 + 摘要算法**」， 一般 WITH 單詞前面有兩個單詞，第一個單詞是約定密鑰交換的算法，第二個單詞是約定證書的驗證算法。比如剛才的密碼套件的意思就是：

- 由於 WITH 單詞只有一個 RSA，則說明握手時密鑰交換算法和簽名算法都是使用 RSA；
- 握手後的通信使用 AES 對稱算法，密鑰長度 128 位，分組模式是 GCM；
- 摘要算法 SHA256 用於消息認證和產生隨機數；


就前面這兩個客戶端和服務端相互「打招呼」的過程，客戶端和服務端就已確認了 TLS 版本和使用的密碼套件，而且你可能發現客戶端和服務端都會各自生成一個隨機數，並且還會把隨機數傳遞給對方。

那這個隨機數有啥用呢？其實這兩個隨機數是後續作為生成「會話密鑰」的條件，所謂的會話密鑰就是數據傳輸時，所使用的對稱加密密鑰。

然後，服務端為了證明自己的身份，會發送「**Server Certificate**」給客戶端，這個消息裡含有數字證書。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/certificate.png)


隨後，服務端發了「**Server Hello Done**」消息，目的是告訴客戶端，我已經把該給你的東西都給你了，本次打招呼完畢。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/serverhellodone.png)


### 客戶端驗證證書

在這裡剎個車，客戶端拿到了服務端的數字證書後，要怎麼校驗該數字證書是真實有效的呢？

#### 數字證書和 CA 機構

在說校驗數字證書是否可信的過程前，我們先來看看數字證書是什麼，一個數字證書通常包含了：

- 公鑰；
- 持有者信息；
- 證書認證機構（CA）的信息；
- CA 對這份文件的數字簽名及使用的算法；
- 證書有效期；
- 還有一些其他額外信息；

那數字證書的作用，是用來認證公鑰持有者的身份，以防止第三方進行冒充。說簡單些，證書就是用來告訴客戶端，該服務端是否是合法的，因為只有證書合法，才代表服務端身份是可信的。

我們用證書來認證公鑰持有者的身份（服務端的身份），那證書又是怎麼來的？又該怎麼認證證書呢？

為了讓服務端的公鑰被大家信任，服務端的證書都是由 CA （*Certificate Authority*，證書認證機構）簽名的，CA 就是網絡世界裡的公安局、公證中心，具有極高的可信度，所以由它來給各個公鑰簽名，信任的一方簽發的證書，那必然證書也是被信任的。

之所以要簽名，是因為簽名的作用可以避免中間人在獲取證書時對證書內容的篡改。

#### 數字證書籤發和驗證流程

如下圖圖所示，為數字證書籤發和驗證流程：


![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/證書的校驗.png)

CA 簽發證書的過程，如上圖左邊部分：

- 首先 CA 會把持有者的公鑰、用途、頒發者、有效時間等信息打成一個包，然後對這些信息進行 Hash 計算，得到一個 Hash 值；
- 然後 CA 會使用自己的私鑰將該 Hash 值加密，生成 Certificate Signature，也就是 CA 對證書做了簽名；
- 最後將 Certificate Signature 添加在文件證書上，形成數字證書；

客戶端校驗服務端的數字證書的過程，如上圖右邊部分：

- 首先客戶端會使用同樣的 Hash 算法獲取該證書的 Hash 值 H1；
- 通常瀏覽器和操作系統中集成了 CA 的公鑰信息，瀏覽器收到證書後可以使用 CA 的公鑰解密 Certificate Signature 內容，得到一個 Hash 值 H2 ；
- 最後比較 H1 和 H2，如果值相同，則為可信賴的證書，否則則認為證書不可信。

#### 證書鏈

但事實上，證書的驗證過程中還存在一個證書信任鏈的問題，因為我們向 CA 申請的證書一般不是根證書籤發的，而是由中間證書籤發的，比如百度的證書，從下圖你可以看到，證書的層級有三級：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/baidu證書.png)

對於這種三級層級關係的證書的驗證過程如下：

- 客戶端收到 baidu.com 的證書後，發現這個證書的簽發者不是根證書，就無法根據本地已有的根證書中的公鑰去驗證 baidu.com 證書是否可信。於是，客戶端根據 baidu.com 證書中的簽發者，找到該證書的頒發機構是 “GlobalSign Organization Validation CA - SHA256 - G2”，然後向 CA 請求該中間證書。
- 請求到證書後發現 “GlobalSign Organization Validation CA - SHA256 - G2” 證書是由 “GlobalSign Root CA” 簽發的，由於 “GlobalSign Root CA” 沒有再上級簽發機構，說明它是根證書，也就是自簽證書。應用軟件會檢查此證書有否已預載於根證書清單上，如果有，則可以利用根證書中的公鑰去驗證 “GlobalSign Organization Validation CA - SHA256 - G2” 證書，如果發現驗證通過，就認為該中間證書是可信的。
- “GlobalSign Organization Validation CA - SHA256 - G2” 證書被信任後，可以使用 “GlobalSign Organization Validation CA - SHA256 - G2” 證書中的公鑰去驗證 baidu.com 證書的可信性，如果驗證通過，就可以信任 baidu.com 證書。

在這四個步驟中，最開始客戶端只信任根證書 GlobalSign Root CA 證書的，然後 “GlobalSign Root CA” 證書信任 “GlobalSign Organization Validation CA - SHA256 - G2” 證書，而 “GlobalSign Organization Validation CA - SHA256 - G2” 證書又信任 baidu.com 證書，於是客戶端也信任 baidu.com 證書。

總括來說，由於用戶信任 GlobalSign，所以由 GlobalSign 所擔保的 baidu.com 可以被信任，另外由於用戶信任操作系統或瀏覽器的軟件商，所以由軟件商預載了根證書的 GlobalSign 都可被信任。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/用戶信任.png)


操作系統裡一般都會內置一些根證書，比如我的 MAC 電腦裡內置的根證書有這麼多：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/系統根證書.png)

這樣的一層層地驗證就構成了一條信任鏈路，整個證書信任鏈驗證流程如下圖所示：

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/證書鏈.png)

最後一個問題，為什麼需要證書鏈這麼麻煩的流程？Root CA 為什麼不直接頒發證書，而是要搞那麼多中間層級呢？

這是為了確保根證書的絕對安全性，將根證書隔離地越嚴格越好，不然根證書如果失守了，那麼整個信任鏈都會有問題。

### TLS 第三次握手

客戶端驗證完證書後，認為可信則繼續往下走。

接著，客戶端就會生成一個新的**隨機數  (*pre-master*)**，用服務器的 RSA 公鑰加密該隨機數，通過「**Client Key Exchange**」消息傳給服務端。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/clietnkeyexchange.png)

服務端收到後，用 RSA 私鑰解密，得到客戶端發來的隨機數 (pre-master)。

至此，**客戶端和服務端雙方都共享了三個隨機數，分別是 Client Random、Server Random、pre-master**。

於是，雙方根據已經得到的三個隨機數，生成**會話密鑰（Master Secret）**，它是對稱密鑰，用於對後續的 HTTP 請求/響應的數據加解密。


生成完「會話密鑰」後，然後客戶端發一個「**Change Cipher Spec**」，告訴服務端開始使用加密方式發送消息。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/cipherspecmessage.png)

然後，客戶端再發一個「**Encrypted Handshake Message（Finishd）**」消息，把之前所有發送的數據做個**摘要**，再用會話密鑰（master secret）加密一下，讓服務器做個驗證，驗證加密通信「是否可用」和「之前握手信息是否有被中途篡改過」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost4@main/網絡/https/encryptd.png)

可以發現，「Change Cipher Spec」之前傳輸的 TLS 握手數據都是明文，之後都是對稱密鑰加密的密文。

### TLS 第四次握手

服務器也是同樣的操作，發「**Change Cipher Spec**」和「**Encrypted Handshake Message**」消息，如果雙方都驗證加密和解密沒問題，那麼握手正式完成。

最後，就用「會話密鑰」加解密 HTTP 請求和響應了。

---

## RSA 算法的缺陷

**使用 RSA 密鑰協商算法的最大問題是不支持前向保密**。

因為客戶端傳遞隨機數（用於生成對稱加密密鑰的條件之一）給服務端時使用的是公鑰加密的，服務端收到後，會用私鑰解密得到隨機數。所以一旦服務端的私鑰洩漏了，過去被第三方截獲的所有 TLS 通訊密文都會被破解。


為瞭解決這個問題，後面就出現了 ECDHE 密鑰協商算法，我們現在大多數網站使用的正是 ECDHE 密鑰協商算法，關於 ECDHE 握手的過程，將在下一篇揭曉。

---

哈嘍，我是小林，就愛圖解計算機基礎，如果文章對你有幫助，別忘記關注哦！

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)


