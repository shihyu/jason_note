# 小林 x 圖解計算機基礎

![](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost4@main/網站封面.png)

👉 **點擊**：[圖解計算機基礎在線閱讀](https://xiaolincoding.com/)

本站所有文章都是我[公眾號：小林coding](https://mp.weixin.qq.com/s/FYH1I8CRsuXDSybSGY_AFA)的原創文章，內容包含圖解計算機網絡、操作系統、計算機組成、數據庫，共 1000 張圖 + 50 萬字，破除晦澀難懂的計算機基礎知識，讓天下沒有難懂的八股文（口嗨一下，大家不要當真哈哈）！🚀

曾經我也苦惱於那些晦澀難弄的計算機基礎知識，但在我啃了一本又一本的書，看了一個又一個的視頻後，終於對這些“傢伙”有了認識。我想著，這世界上肯定有一些朋友也跟我有一樣的苦惱，為此下決心，用圖解 + 通熟易懂的講解來幫助大家理解，利用工作之餘，堅持輸出圖解文章兩年之久，這才有了今天的網站!



## :open_book:《圖解網絡》
- **介紹**:point_down:：
  - [圖解網絡介紹](https://xiaolincoding.com/network/)
- **網絡基礎篇** :point_down:
  - [TCP/IP 網絡模型有哪幾層？](https://xiaolincoding.com/network/1_base/tcp_ip_model.html) 
  - [鍵入網址到網頁顯示，期間發生了什麼？](https://xiaolincoding.com/network/1_base/what_happen_url.html) 
  - [Linux 系統是如何收發網絡包的？](https://xiaolincoding.com/network/1_base/how_os_deal_network_package.html) 
- **HTTP 篇** :point_down:
  - [HTTP 常見面試題](https://xiaolincoding.com/network/2_http/http_interview.html) 
  - [HTTP/1.1 如何優化？](https://xiaolincoding.com/network/2_http/http_optimize.html) 
  - [HTTPS RSA 握手解析](https://xiaolincoding.com/network/2_http/https_rsa.html) 
  - [HTTPS ECDHE 握手解析](https://xiaolincoding.com/network/2_http/https_ecdhe.html) 
  - [HTTPS 如何優化？](https://xiaolincoding.com/network/2_http/https_optimize.html) 
  - [HTTP/2 牛逼在哪？](https://xiaolincoding.com/network/2_http/http2.html) 
  - [HTTP/3 強勢來襲](https://xiaolincoding.com/network/2_http/http3.html) 
  - [既然有 HTTP 協議，為什麼還要有 RPC？](https://xiaolincoding.com/network/2_http/http_rpc.html) 
  - [既然有 HTTP 協議，為什麼還要有 WebSocket？](https://xiaolincoding.com/network/2_http/http_websocket.html) 
- **TCP 篇** :point_down:
  - [TCP 三次握手與四次揮手面試題](https://xiaolincoding.com/network/3_tcp/tcp_interview.html) 
  - [TCP 重傳、滑動窗口、流量控制、擁塞控制](https://xiaolincoding.com/network/3_tcp/tcp_feature.html) 
  - [TCP 實戰抓包分析](https://xiaolincoding.com/network/3_tcp/tcp_tcpdump.html) 
  - [TCP 半連接隊列和全連接隊列](https://xiaolincoding.com/network/3_tcp/tcp_queue.html) 
  - [如何優化 TCP?](https://xiaolincoding.com/network/3_tcp/tcp_optimize.html) 
  - [如何理解是 TCP 面向字節流協議？](https://xiaolincoding.com/network/3_tcp/tcp_stream.html) 
  - [為什麼 TCP 每次建立連接時，初始化序列號都要不一樣呢？](https://xiaolincoding.com/network/3_tcp/isn_deff.html) 
  - [SYN 報文什麼時候情況下會被丟棄？](https://xiaolincoding.com/network/3_tcp/syn_drop.html) 
  - [四次揮手中收到亂序的 FIN 包會如何處理？](https://xiaolincoding.com/network/3_tcp/out_of_order_fin.html) 
  - [在 TIME_WAIT 狀態的 TCP 連接，收到 SYN 後會發生什麼？](https://xiaolincoding.com/network/3_tcp/time_wait_recv_syn.html) 
  - [TCP 連接，一端斷電和進程崩潰有什麼區別？](https://xiaolincoding.com/network/3_tcp/tcp_down_and_crash.html) 
  - [拔掉網線後， 原本的 TCP 連接還存在嗎？](https://xiaolincoding.com/network/3_tcp/tcp_unplug_the_network_cable.html) 
  - [tcp_tw_reuse 為什麼默認是關閉的？](https://xiaolincoding.com/network/3_tcp/tcp_tw_reuse_close.html) 
  - [HTTPS 中 TLS 和 TCP 能同時握手嗎？](https://xiaolincoding.com/network/3_tcp/tcp_tls.html) 
  - [TCP Keepalive 和 HTTP Keep-Alive 是一個東西嗎？](https://xiaolincoding.com/network/3_tcp/tcp_http_keepalive.html) 
  - [TCP 協議有什麼缺陷？](https://xiaolincoding.com/network/3_tcp/tcp_problem.html)
  - [如何基於 UDP 協議實現可靠傳輸？](https://xiaolincoding.com/network/3_tcp/quic.html)
  - [TCP 和 UDP 可以使用同一個端口嗎？](https://xiaolincoding.com/network/3_tcp/port.html)
  - [服務端沒有 listen，客戶端發起連接建立，會發生什麼？](https://xiaolincoding.com/network/3_tcp/tcp_no_listen.html)
  - [沒有 accept，可以建立 TCP 連接嗎？](https://xiaolincoding.com/network/3_tcp/tcp_no_accpet.html) 
  - [用了 TCP 協議，數據一定不會丟嗎？](https://xiaolincoding.com/network/3_tcp/tcp_drop.html)
  - [TCP 四次揮手，可以變成三次嗎？](https://xiaolincoding.com/network/3_tcp/tcp_three_fin.html)
  - [TCP 序列號和確認號是如何變化的？](https://xiaolincoding.com/network/3_tcp/tcp_seq_ack.html)
- **IP 篇** :point_down:
  - [IP 基礎知識全家桶](https://xiaolincoding.com/network/4_ip/ip_base.html) 	
  - [ping 的工作原理](https://xiaolincoding.com/network/4_ip/ping.html) 	
  - [斷網了，還能 ping 通 127.0.0.1 嗎？](https://xiaolincoding.com/network/4_ip/ping_lo.html)
- **學習心得** :point_down:
  - [計算機網絡怎麼學？](https://xiaolincoding.com/network/5_learn/learn_network.html) 	
  - [畫圖經驗分享](https://xiaolincoding.com/network/5_learn/draw.html) 	

## :open_book:《圖解系統》
- **介紹**:point_down:：
  - [圖解系統介紹](https://xiaolincoding.com/os/)
- **硬件結構** :point_down:
  - [CPU 是如何執行程序的？](https://xiaolincoding.com/os/1_hardware/how_cpu_run.html) 
  - [磁盤比內存慢幾萬倍？](https://xiaolincoding.com/os/1_hardware/storage.html) 
  - [如何寫出讓 CPU 跑得更快的代碼？](https://xiaolincoding.com/os/1_hardware/how_to_make_cpu_run_faster.html) 
  - [CPU 緩存一致性](https://xiaolincoding.com/os/1_hardware/cpu_mesi.html) 
  - [CPU 是如何執行任務的？](https://xiaolincoding.com/os/1_hardware/how_cpu_deal_task.html) 
  - [什麼是軟中斷？](https://xiaolincoding.com/os/1_hardware/soft_interrupt.html) 
  - [為什麼 0.1 + 0.2 不等於 0.3 ？](https://xiaolincoding.com/os/1_hardware/float.html) 
- **操作系統結構** :point_down:
  - [Linux 內核 vs Windows 內核](https://xiaolincoding.com/os/2_os_structure/linux_vs_windows.html) 
- **內存管理** :point_down:
  - [為什麼要有虛擬內存？](https://xiaolincoding.com/os/3_memory/vmem.html) 
  - [malloc 是如何分配內存的？](https://xiaolincoding.com/os/3_memory/malloc.html)
  - [內存滿了，會發生什麼？](https://xiaolincoding.com/os/3_memory/mem_reclaim.html)
  - [在 4GB 物理內存的機器上，申請 8G 內存會怎麼樣？](https://xiaolincoding.com/os/3_memory/alloc_mem.html)
  - [如何避免預讀失效和緩存汙染的問題？](https://xiaolincoding.com/os/3_memory/cache_lru.html)
  - [深入理解 Linux 虛擬內存管理](https://xiaolincoding.com/os/3_memory/linux_mem.html)
  - [深入理解 Linux 物理內存管理](https://xiaolincoding.com/os/3_memory/linux_mem2.html)
- **進程管理** :point_down:
  - [進程、線程基礎知識](https://xiaolincoding.com/os/4_process/process_base.html) 
  - [進程間有哪些通信方式？](https://xiaolincoding.com/os/4_process/process_commu.html) 
  - [多線程衝突了怎麼辦？](https://xiaolincoding.com/os/4_process/multithread_sync.html) 
  - [怎麼避免死鎖？](https://xiaolincoding.com/os/4_process/deadlock.html) 
  - [什麼是悲觀鎖、樂觀鎖？](https://xiaolincoding.com/os/4_process/pessim_and_optimi_lock.html) 
  - [一個進程最多可以創建多少個線程？](https://xiaolincoding.com/os/4_process/create_thread_max.html) 
  - [線程崩潰了，進程也會崩潰嗎？](https://xiaolincoding.com/os/4_process/thread_crash.html)
- **調度算法** :point_down:
  - [進程調度/頁面置換/磁盤調度算法](https://xiaolincoding.com/os/5_schedule/schedule.html)
- **文件系統** :point_down:
  - [文件系統全家桶](https://xiaolincoding.com/os/6_file_system/file_system.html) 	
  - [進程寫文件時，進程發生了崩潰，已寫入的數據會丟失嗎？](https://xiaolincoding.com/os/6_file_system/pagecache.html)
- **設備管理** :point_down:
  - [鍵盤敲入 A 字母時，操作系統期間發生了什麼？](https://xiaolincoding.com/os/7_device/device.html) 
- **網絡系統** :point_down:
  - [什麼是零拷貝？](https://xiaolincoding.com/os/8_network_system/zero_copy.html) 
  - [I/O 多路複用：select/poll/epoll](https://xiaolincoding.com/os/8_network_system/selete_poll_epoll.html) 
  - [高性能網絡模式：Reactor 和 Proactor](https://xiaolincoding.com/os/8_network_system/reactor.html) 
  - [什麼是一致性哈希？](https://xiaolincoding.com/os/8_network_system/hash.html) 
- **學習心得** :point_down:
  - [如何查看網絡的性能指標？](https://xiaolincoding.com/os/9_linux_chtml/linux_network.html) 	
  - [畫圖經驗分享](https://xiaolincoding.com/os/9_linux_chtml/pv_uv.html) 	
- **學習心得** :point_down:
  - [計算機網絡怎麼學？](https://xiaolincoding.com/os/10_learn/learn_os.html) 	
  - [畫圖經驗分享](https://xiaolincoding.com/os/10_learn/draw.html) 

## :open_book:《圖解MySQL》
- **介紹**:point_down:：
  - [圖解 MySQL 介紹](https://xiaolincoding.com/mysql/)
- **基礎篇**:point_down:：
  - [執行一條 select 語句，期間發生了什麼？](https://xiaolincoding.com/mysql/base/how_select.html)
  - [MySQL 一行記錄是怎麼存儲的？](https://xiaolincoding.com/mysql/base/row_format.html)
- **索引篇** :point_down:
  - [索引常見面試題](https://xiaolincoding.com/mysql/index/index_interview.html)
  - [從數據頁的角度看 B+ 樹](https://xiaolincoding.com/mysql/index/page.html)
  - [為什麼 MySQL 採用 B+ 樹作為索引？](https://xiaolincoding.com/mysql/index/why_index_chose_bpuls_tree.html)
  - [MySQL 單表不要超過 2000W 行，靠譜嗎？](https://xiaolincoding.com/mysql/index/2000w.html)
  - [索引失效有哪些？](https://xiaolincoding.com/mysql/index/index_lose.html)
  - [MySQL 使用 like “%x“，索引一定會失效嗎？](https://xiaolincoding.com/mysql/index/index_issue.html)
  - [count(\*) 和 count(1) 有什麼區別？哪個性能最好？](https://xiaolincoding.com/mysql/index/count.html)
- **事務篇** :point_down:
  - [事務隔離級別是怎麼實現的？](https://xiaolincoding.com/mysql/transaction/mvcc.html)
  - [MySQL 可重複讀隔離級別，完全解決幻讀了嗎？](https://xiaolincoding.com/mysql/transaction/phantom.html) 		
- **鎖篇** :point_down:
  - [MySQL 有哪些鎖？](https://xiaolincoding.com/mysql/lock/mysql_lock.html) 	
  - [MySQL 是怎麼加鎖的？](https://xiaolincoding.com/mysql/lock/how_to_lock.html) 	
  - [update 沒加索引會鎖全表](https://xiaolincoding.com/mysql/lock/update_index.html) 	
  - [MySQL 死鎖了，怎麼辦？](https://xiaolincoding.com/mysql/lock/deadlock.html) 
  - [字節面試：加了什麼鎖，導致死鎖的？](https://xiaolincoding.com/mysql/lock/show_lock.html)
- **日誌篇** :point_down:
  - [MySQL 日誌：undo log、redo log、binlog 有什麼用？](https://xiaolincoding.com/mysql/log/how_update.html)
- **內存篇** :point_down:
  - [揭開 Buffer Pool 的面紗](https://xiaolincoding.com/mysql/buffer_pool/buffer_pool.html) 	

##  :open_book: 《圖解Redis》

- **面試篇** :point_down:
   - [Redis 常見面試題](https://xiaolincoding.com/redis/base/redis_interview.html)
- **數據類型篇** :point_down:
   - [Redis 數據類型和應用場景](https://xiaolincoding.com/redis/data_struct/command.html)
   - [圖解 Redis 數據結構](https://xiaolincoding.com/redis/data_struct/data_struct.html)
- **持久化篇** :point_down:
  - [AOF 持久化是怎麼實現的？](https://xiaolincoding.com/redis/storage/aof.html) 	
  - [RDB 快照是怎麼實現的？](https://xiaolincoding.com/redis/storage/rdb.html) 
- **功能篇**:point_down:
   - [Redis 過期刪除策略和內存淘汰策略有什麼區別？](https://xiaolincoding.com/redis/module/strategy.html) 
- **高可用篇** :point_down:
   - [主從複製是怎麼實現的？](https://xiaolincoding.com/redis/cluster/master_slave_replication.html) 	
   - [為什麼要有哨兵？](https://xiaolincoding.com/redis/cluster/sentinel.html)
- **緩存篇** :point_down:
   - [什麼是緩存雪崩、擊穿、穿透？](https://xiaolincoding.com/redis/cluster/cache_problem.html) 	
   - [數據庫和緩存如何保證一致性？](https://xiaolincoding.com/redis/architecture/mysql_redis_consistency.html) 


## :muscle: 學習心得

- [計算機基礎學習路線](https://xiaolincoding.com/cs_learn/) ：計算機基礎學習書籍 + 視頻推薦，全面且清晰。
- [互聯網校招心得](https://xiaolincoding.com/reader_nb/) ：小林神仙讀者們的校招和學習心得，值得學習。

##  :books:  圖解系列 PDF 下載

- [圖解網絡 + 圖解系統 PDF 下載](https://mp.weixin.qq.com/s/02036z-FMOCLpZ_otwMwBg)

## 勘誤及提問
如果有疑問或者發現錯誤，可以在相應的 Issues 進行提問或勘誤，也可以在[圖解計算機基礎網站](https://xiaolincoding.com/)對應的文章底部留言。

如果喜歡或者有所啟發，歡迎 Star，對作者也是一種鼓勵。


## 公眾號


最新的圖解文章都在公眾號首發，強烈推薦關注！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![](https://cdn.jsdelivr.net/gh/xiaolincoder/ImageHost3@main/其他/公眾號介紹.png)

 
