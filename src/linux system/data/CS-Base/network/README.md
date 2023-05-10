
# 圖解網絡介紹

大家好，我是小林，是《圖解網絡》的作者，本站的內容都是整理於我[公眾號](https://mp.weixin.qq.com/s/FYH1I8CRsuXDSybSGY_AFA)裡的圖解文章。

還沒關注的朋友，可以微信搜索「**小林coding**」，關注我的公眾號，**後續最新版本的 PDF 會在我的公眾號第一時間發佈**，而且會有更多其他系列的圖解文章，比如操作系統、計算機組成、數據庫、算法等等。

簡單介紹下《圖解網絡》，整個內容共有 **`20W` 字 + `500` 張圖**，每一篇都自己手繪了很多圖，目的也很簡單，擊破大家對於「八股文」的恐懼。

## 適合什麼群體？

《圖解網絡》寫的網絡知識主要是**面向程序員**的，因為小林本身也是個程序員，所以涉及到的知識主要是關於程序員日常工作或者面試的網絡知識。

非常適合有一點網絡基礎，但是又不怎麼紮實，或者知識點串不起來的同學，說白**這本圖解網絡就是為了拯救半桶水的同學而出來的**。

因為小林寫的圖解網絡就四個字，**通俗易懂**！

相信你在看這本圖解網絡的時候，你心裡的感受會是：

- 「臥槽，原來是這樣，大學老師教知識原來是這麼理解」
- 「臥槽，我的網絡知識串起來了」
- 「臥槽，我感覺面試穩了」
- 「臥槽，相見恨晚」

當然，也適合面試突擊網絡知識時拿來看。圖解網絡裡的內容基本是面試常見的協議，比如 HTTP、HTTPS、TCP、UDP、IP 等等，也有很多面試常問的問題，比如：

- TCP 為什麼三次握手？四次揮手？
- TCP 為什麼要有 TIME_WAIT 狀態？
- TCP 為什麼是可靠傳輸協議，而 UDP 不是？
- 鍵入網址到網頁顯示，期間發生了什麼？
- HTTPS 握手過程是怎樣的？
- ….

不敢說 100 % 涵蓋了面試的網絡問題，但是至少 90% 是有的，而且內容的深度應對大廠也是綽綽有餘，有非常多的讀者跑來感激小林的圖解網絡，幫助他們拿到了國內很多一線大廠的 offer。

## 要怎麼閱讀？

很誠懇的告訴你，《圖解網絡》不是教科書，而是我寫的圖解網絡文章的整合，所以肯定是沒有教科書那麼細緻和全面，當然也就不會有很多廢話，都是直擊重點，不繞彎，而且有的知識點書上看不到。

閱讀的順序可以不用從頭讀到尾，你可以根據你想要了解的知識點，通過本站的搜索功能，去看哪個章節的內容就好，可以隨意閱讀任何章節。

本站的左側邊攔就是《圖解網絡》的目錄結構（別看篇章不多，每一章都是很長很長的文章哦 :laughing:）：

- **網絡基礎篇** :point_down:
  - [TCP/IP 網絡模型有哪幾層？](/network/1_base/tcp_ip_model.md) 
  - [鍵入網址到網頁顯示，期間發生了什麼？](/network/1_base/what_happen_url.md) 
  - [Linux 系統是如何收發網絡包的？](/network/1_base/how_os_deal_network_package.md) 
- **HTTP 篇** :point_down:
	- [HTTP 常見面試題](/network/2_http/http_interview.md) 
	- [HTTP/1.1 如何優化？](/network/2_http/http_optimize.md) 
	- [HTTPS RSA 握手解析](/network/2_http/https_rsa.md) 
	- [HTTPS ECDHE 握手解析](/network/2_http/https_ecdhe.md) 
	- [HTTPS 如何優化？](/network/2_http/https_optimize.md) 
	- [HTTP/2 牛逼在哪？](/network/2_http/http2.md) 
	- [HTTP/3 強勢來襲](/network/2_http/http3.md) 
	- [既然有 HTTP 協議，為什麼還要有 RPC？](/network/2_http/http_rpc.md) 
	- [既然有 HTTP 協議，為什麼還要有 websocket？](/network/2_http/http_websocket.md) 
- **TCP 篇** :point_down:
	- [TCP 三次握手與四次揮手面試題](/network/3_tcp/tcp_interview.md) 
	- [TCP 重傳、滑動窗口、流量控制、擁塞控制](/network/3_tcp/tcp_feature.md) 
	- [TCP 實戰抓包分析](/network/3_tcp/tcp_tcpdump.md) 
	- [TCP 半連接隊列和全連接隊列](/network/3_tcp/tcp_queue.md) 
	- [如何優化 TCP?](/network/3_tcp/tcp_optimize.md) 
	- [如何理解是 TCP 面向字節流協議？](/network/3_tcp/tcp_stream.md) 
	- [為什麼 TCP 每次建立連接時，初始化序列號都要不一樣呢？](/network/3_tcp/isn_deff.md) 
	- [SYN 報文什麼時候情況下會被丟棄？](/network/3_tcp/syn_drop.md) 
	- [四次揮手中收到亂序的 FIN 包會如何處理？](/network/3_tcp/out_of_order_fin.md) 
	- [在 TIME_WAIT 狀態的 TCP 連接，收到 SYN 後會發生什麼？](/network/3_tcp/time_wait_recv_syn.md) 
	- [TCP 連接，一端斷電和進程崩潰有什麼區別？](/network/3_tcp/tcp_down_and_crash.md) 
	- [拔掉網線後， 原本的 TCP 連接還存在嗎？](/network/3_tcp/tcp_unplug_the_network_cable.md) 
	- [tcp_tw_reuse 為什麼默認是關閉的？](/network/3_tcp/tcp_tw_reuse_close.md) 
	- [HTTPS 中 TLS 和 TCP 能同時握手嗎？](/network/3_tcp/tcp_tls.md) 
	- [TCP Keepalive 和 HTTP Keep-Alive 是一個東西嗎？](/network/3_tcp/tcp_http_keepalive.md) 
	- [TCP 有什麼缺陷？](/network/3_tcp/tcp_problem.md)
	- [如何基於 UDP 協議實現可靠傳輸？](/network/3_tcp/quic.md)
	- [TCP 和 UDP 可以使用同一個端口嗎？](/network/3_tcp/port.md)
	- [服務端沒有 listen，客戶端發起連接建立，會發生什麼？](/network/3_tcp/tcp_no_listen.md)
	- [沒有 accept，可以建立 TCP 連接嗎？](/network/3_tcp/tcp_no_accpet.md)
	- [用了 TCP 協議，數據一定不會丟嗎？](/network/3_tcp/tcp_drop.md)
	- [TCP 四次揮手，可以變成三次嗎？](/network/3_tcp/tcp_three_fin.md)
- **IP 篇** :point_down:
	- [IP 基礎知識全家桶](/network/4_ip/ip_base.md) 	
	- [ping 的工作原理](/network/4_ip/ping.md) 	
	- [斷網了，還能 ping 通 127.0.0.1 嗎？](/network/4_ip/ping_lo.md)
- **學習心得** :point_down:
	- [計算機網絡怎麼學？](/network/5_learn/learn_network.md) 	
  - [畫圖經驗分享](/network/5_learn/draw.md) 	

## 質量如何？

圖解網絡的質量小林說的不算，讀者說的算！

圖解網絡的第一個版本自去年發佈以來，每隔一段時間，就會有不少的讀者跑來感激小林。

他們說看了我的圖解網絡，輕鬆應對大廠的網絡面試題，而且每次面試時問到網絡問題，他們一點都不慌，甚至暗暗竊喜。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/160f55b965cf4c42ba160e327178a783.png)

## 有錯誤怎麼辦？

小林是個手殘黨，時常寫出錯別字。

如果你在學習的過程中，**如果你發現有任何錯誤或者疑惑的地方，歡迎你通過郵箱或者底部留言給小林**，勘誤郵箱：xiaolincoding@163.com

小林抽時間會逐個修正，然後發佈新版本的圖解網絡 PDF，一起迭代出更好的圖解網絡！

新的圖解文章都在公眾號首發，別忘記關注了哦！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/其他/公眾號介紹.png)

