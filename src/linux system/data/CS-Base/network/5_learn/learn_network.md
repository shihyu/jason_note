# 6.1 計算機網絡怎麼學？

計算機網絡相比操作系統好學非常多，因為計算機網絡不抽象，你要想知道網絡中的細節，你都可以通過抓包來分析，而且不管是手機、個人電腦和服務器，它們所使用的計算網絡協議是一致的。

也就是說，計算機網絡不會因為設備的不同而不同，大家都遵循這一套「規則」來相互通信，這套規則就是 TCP/IP 網絡模型。

![OSI 參考模型與 TCP/IP 的關係](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BD%91%E7%BB%9C/TCP-%E4%B8%89%E6%AC%A1%E6%8F%A1%E6%89%8B%E5%92%8C%E5%9B%9B%E6%AC%A1%E6%8C%A5%E6%89%8B/7.jpg)

TCP/IP 網絡參考模型共有 `4` 層，其中需要我們熟練掌握的是應用層、傳輸層和網絡層，至於網絡接口層（數據鏈路層和物理層）我們只需要做簡單的瞭解就可以了。

對於應用層，當然重點要熟悉最常見的 [HTTP 和 HTTPS](https://mp.weixin.qq.com/s/bUy220-ect00N4gnO0697A)，傳輸層 TCP 和 UDP 都要熟悉，網絡層要熟悉 [IPv4](https://mp.weixin.qq.com/s/bUy220-ect00N4gnO0697A)，IPv6 可以做簡單點瞭解。


我覺得學習一個東西，就從我們常見的事情開始著手。

比如， ping 命令可以說在我們判斷網絡環境的時候，最常使用的了，你可以先把你電腦 ping 你舍友或同事的電腦的過程中發生的事情都搞明白，這樣就基本知道一個數據包是怎麼轉發的了，於是你就知道了網絡層、數據鏈路層和物理層之間是如何工作，如何相互配合的了。


搞明白了 ping 過程，我相信你學起 HTTP 請求過程的時候，會很快就能掌握了，因為網絡層以下的工作方式，你在學習 ping 的時候就已經明白了，這時就只需要認真掌握傳輸層中的 TCP 和應用層中的 HTTP 協議，就能搞明白[訪問網頁的整個過程](https://mp.weixin.qq.com/s/iSZp41SRmh5b2bXIvzemIw)了，這也是面試常見的題目了，畢竟它能考察你網絡知識的全面性。

重中之重的知識就是 TCP 了，TCP 不管是[建立連接、斷開連接](https://mp.weixin.qq.com/s/tH8RFmjrveOmgLvk9hmrkw)的過程，還是數據傳輸的過程，都不能放過，針對數據可靠傳輸的特性，又可以拆解為[超時重傳、流量控制、滑動窗口、擁塞控制](https://mp.weixin.qq.com/s/Tc09ovdNacOtnMOMeRc_uA)等等知識點，學完這些只能算對 TCP 有個「**感性**」的認識，另外我們還得知道 Linux 提供的 [TCP 內核的參數](https://mp.weixin.qq.com/s/fjnChU3MKNc_x-Wk7evLhg)的作用，這樣才能從容地應對工作中遇到的問題。

接下來，推薦我看過並覺得不錯的計算機網絡相關的書籍和視頻。

## 入門系列

此係列針對沒有任何計算機基礎的朋友，如果已經對計算機輕車熟路的大佬，也不要忽略，不妨看看我推薦的正確嗎。

如果你要入門 HTTP，首先最好書籍就是《**圖解 HTTP**》了，作者真的做到完完全全的「圖解」，小林的圖解功夫還是從這裡偷學到不少，書籍不厚，相信優秀的你，幾天就可以看完了。

![《圖解 HTTP》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/其他/圖解HTTP.jpg)


如果要入門 TCP/IP 網絡模型，我推薦的是《**圖解 TCP/IP**》，這本書也是以大量的圖文來介紹了 TCP/IP 網絡模式的每一層，但是這個書籍的順序不是從「應用層 —> 物理層」，而是從「物理層 -> 應用層」順序開始講的，這一點我覺得不太好，這樣一上來就把最枯燥的部分講了，很容易就被勸退了，所以我建議先跳過前面幾個章節，先看網絡層和傳輸層的章節，然後再回頭看前面的這幾個章節。

![《圖解 TCP/IP》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%9B%BE%E8%A7%A3TCPIP.png)



另外，你想了解網絡是怎麼傳輸，那我推薦《**網絡是怎樣連接的**》，這本書相對比較全面的把訪問一個網頁的發生的過程講解了一遍，其中關於電信等運營商是怎麼傳輸的，這部分你可以跳過，當然你感興趣也可以看，只是我覺得沒必要看。



![《網絡是怎樣連接的》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E7%BD%91%E7%BB%9C%E6%98%AF%E6%80%8E%E4%B9%88%E8%BF%9E%E6%8E%A5%E7%9A%84.png)


如果你覺得書籍過於枯燥，你可以結合 B 站《**計算機網絡微課堂**》視頻一起學習，這個視頻是湖南科技大學老師製作的，PPT 的動圖是我見過做的最用心的了，一看就懂的佳作。

![《計算機網絡微課堂》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/其他/計算機網絡微課堂.png)


> B 站視頻地址：https://www.bilibili.com/video/BV1c4411d7jb?p=1



## 深入學習系列

看完入門系列，相信你對計算機網絡已經有個大體的認識了，接下來我們也不能放慢腳步，快馬加鞭，藉此機會繼續深入學習，因為隱藏在背後的細節還是很多的。

對於 TCP/IP 網絡模型深入學習的話，推薦《**計算機網絡 - 自頂向下方法**》，這本書是從我們最熟悉 HTTP 開始說起，一層一層的說到最後物理層的，有種挖地洞的感覺，這樣的內容編排順序相對是比較合理的。

![《計算機網絡 - 自頂向下方法》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/其他/計算機網絡自定向下.png)



但如果要深入 TCP，前面的這些書還遠遠不夠，賦有計算機網絡聖經的之說的《**TCP/IP 詳解 卷一：協議**》這本書，是進一步深入學習的好資料，這本書的作者用各種實驗的方式來細說各種協議，但不得不說，這本書真的很枯燥，當時我也啃的很難受，但是它質量是真的很高，這本書我只看了 TCP 部分，其他部分你可以選擇性看，但是你一定要過幾遍這本書的 TCP 部分，涵蓋的內容非常全且細。


![《TCP/IP 詳解 卷一：協議》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/TCPIP%E5%8D%8F%E8%AE%AE%E8%AF%A6%E8%A7%A3.png)


要說我看過最好的 TCP 資料，那必定是《**The TCP/IP GUIDE**》這本書了，目前只有英文版本的，而且有個專門的網址可以白嫖看這本書的內容，圖片都是彩色，看起來很舒服很鮮明，小林之前寫的 TCP 文章不少案例和圖片都是參考這裡的，這本書精華部分就是把 TCP 滑動窗口和流量控制說的超級明白，很可惜擁塞控制部分說的不多。

![《The TCP/IP GUIDE》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/TCPIP%20GUIDE.png)



> 白嫖站點：http://www.tcpipguide.com/free/t_TCPSlidingWindowAcknowledgmentSystemForDataTranspo-6.htm



當然，計算機網絡最牛逼的資料，那必定 **RFC 文檔**，它可以稱為計算機網絡世界的「法規」，也是最新、最權威和最正確的地方了，困惑大家的 TCP 為什麼三次握手和四次揮手，其實在 RFC 文檔幾句話就說明白了。

> TCP 協議的 RFC 文檔：https://datatracker.ietf.org/doc/rfc1644/


## 實戰系列


在學習書籍資料的時候，不管是 TCP、UDP、ICMP、DNS、HTTP、HTTPS 等協議，最好都可以親手嘗試抓數據報，接著可以用 [Wireshark 工具](https://mp.weixin.qq.com/s/bHZ2_hgNQTKFZpWMCfUH9A)看每一個數據報文的信息，這樣你會覺得計算機網絡沒有想象中那麼抽象了，因為它們被你「抓」出來了，並毫無保留地顯現在你面前了，於是你就可以肆無忌憚地「扒開」它們，看清它們每一個頭信息。

那在這裡，我也給你推薦 2 本關於 Wireshark 網絡分析的書，這兩本書都是同一個作者，書中的案例都是源於作者工作中的實際的案例，作者的文筆相當有趣，看起來堪比小說一樣爽，相信你不用一個星期 2 本都能看完了。

![《Wireshark 網絡分析就這麼簡單》 與 《Wireshark 網絡分析的藝術》](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/其他/wireshark書.png)

## 最後

文中推薦的書，小林都已經把電子書整理好給大家了，只需要在小林的公眾號後臺回覆「**我要學習**」，即可獲取百度網盤下載鏈接。

![](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)