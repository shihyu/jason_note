# 4.22 TCP 四次揮手，可以變成三次嗎？

大家好，我是小林。

有位讀者面美團時，被問到：**TCP 四次揮手中，能不能把第二次的 ACK 報文， 放到第三次 FIN 報文一起發送？**

![](https://img-blog.csdnimg.cn/6e02477ccea24facbf7eada108158bc2.png)


雖然我們在學習 TCP 揮手時，學到的是需要四次來完成 TCP 揮手，但是**在一些情況下， TCP 四次揮手是可以變成 TCP 三次揮手的**。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/52f35dcbe24a4ca7abb23f292837c707.png)


而且在用 wireshark 工具抓包的時候，我們也會常看到 TCP 揮手過程是三次，而不是四次，如下圖：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/361207c2e5c34bec8708b79990ba7e99.png)

先來回答為什麼 RFC 文檔裡定義 TCP 揮手過程是要四次？

再來回答什麼情況下，什麼情況會出現三次揮手？

## TCP 四次揮手

TCP 四次揮手的過程如下：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/18635e15653a4affbdab2c9bf72d599e.png)


具體過程：

- 客戶端主動調用關閉連接的函數，於是就會發送 FIN 報文，這個  FIN 報文代表客戶端不會再發送數據了，進入 FIN_WAIT_1 狀態；
- 服務端收到了 FIN 報文，然後馬上回復一個 ACK 確認報文，此時服務端進入 CLOSE_WAIT 狀態。在收到 FIN 報文的時候，TCP 協議棧會為 FIN 包插入一個文件結束符 EOF 到接收緩衝區中，服務端應用程序可以通過 read 調用來感知這個 FIN 包，這個 EOF 會被**放在已排隊等候的其他已接收的數據之後**，所以必須要得繼續 read 接收緩衝區已接收的數據；
- 接著，當服務端在 read 數據的時候，最後自然就會讀到 EOF，接著 **read() 就會返回 0，這時服務端應用程序如果有數據要發送的話，就發完數據後才調用關閉連接的函數，如果服務端應用程序沒有數據要發送的話，可以直接調用關閉連接的函數**，這時服務端就會發一個 FIN 包，這個  FIN 報文代表服務端不會再發送數據了，之後處於 LAST_ACK 狀態；
- 客戶端接收到服務端的 FIN 包，併發送 ACK 確認包給服務端，此時客戶端將進入 TIME_WAIT 狀態；
- 服務端收到 ACK 確認包後，就進入了最後的 CLOSE 狀態；
- 客戶端經過 2MSL 時間之後，也進入 CLOSE 狀態；

你可以看到，每個方向都需要**一個 FIN 和一個 ACK**，因此通常被稱為**四次揮手**。

### 為什麼 TCP 揮手需要四次呢？

服務器收到客戶端的 FIN 報文時，內核會馬上回一個 ACK 應答報文，**但是服務端應用程序可能還有數據要發送，所以並不能馬上發送 FIN 報文，而是將發送 FIN 報文的控制權交給服務端應用程序**：

   - 如果服務端應用程序有數據要發送的話，就發完數據後，才調用關閉連接的函數；
   - 如果服務端應用程序沒有數據要發送的話，可以直接調用關閉連接的函數，

從上面過程可知，**是否要發送第三次揮手的控制權不在內核，而是在被動關閉方（上圖的服務端）的應用程序，因為應用程序可能還有數據要發送，由應用程序決定什麼時候調用關閉連接的函數，當調用了關閉連接的函數，內核就會發送 FIN 報文了，**所以服務端的 ACK 和 FIN 一般都會分開發送。

> FIN 報文一定得調用關閉連接的函數，才會發送嗎？


不一定。

如果進程退出了，不管是不是正常退出，還是異常退出（如進程崩潰），內核都會發送 FIN 報文，與對方完成四次揮手。

### 粗暴關閉 vs 優雅關閉

前面介紹 TCP 四次揮手的時候，並沒有詳細介紹關閉連接的函數，其實關閉的連接的函數有兩種函數：

- close 函數，同時 socket 關閉發送方向和讀取方向，也就是 socket 不再有發送和接收數據的能力。如果有多進程/多線程共享同一個 socket，如果有一個進程調用了 close 關閉只是讓 socket 引用計數 -1，並不會導致 socket 不可用，同時也不會發出 FIN 報文，其他進程還是可以正常讀寫該 socket，直到引用計數變為 0，才會發出 FIN 報文。
- shutdown 函數，可以指定 socket 只關閉發送方向而不關閉讀取方向，也就是 socket 不再有發送數據的能力，但是還是具有接收數據的能力。如果有多進程/多線程共享同一個 socket，shutdown 則不管引用計數，直接使得該 socket 不可用，然後發出 FIN 報文，如果有別的進程企圖使用該 socket，將會受到影響。

如果客戶端是用 close 函數來關閉連接，那麼在 TCP 	四次揮手過程中，如果收到了服務端發送的數據，由於客戶端已經不再具有發送和接收數據的能力，所以客戶端的內核會回 RST 報文給服務端，然後內核會釋放連接，這時就不會經歷完成的 TCP 四次揮手，所以我們常說，調用 close 是粗暴的關閉。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/3b5f1897d2d74028aaf4d552fbce1a74.png)


當服務端收到 RST 後，內核就會釋放連接，當服務端應用程序再次發起讀操作或者寫操作時，就能感知到連接已經被釋放了：

- 如果是讀操作，則會返回 RST 的報錯，也就是我們常見的Connection reset by peer。
- 如果是寫操作，那麼程序會產生 SIGPIPE 信號，應用層代碼可以捕獲並處理信號，如果不處理，則默認情況下進程會終止，異常退出。

相對的，shutdown 函數因為可以指定只關閉發送方向而不關閉讀取方向，所以即使在 TCP 四次揮手過程中，如果收到了服務端發送的數據，客戶端也是可以正常讀取到該數據的，然後就會經歷完整的 TCP 四次揮手，所以我們常說，調用 shutdown 是優雅的關閉。

![優雅關閉.drawio.png](https://img-blog.csdnimg.cn/71f5646ec58849e5921adc08bb6789d4.png)


但是注意，shutdown 函數也可以指定「只關閉讀取方向，而不關閉發送方向」，但是這時候內核是不會發送 FIN 報文的，因為發送 FIN 報文是意味著我方將不再發送任何數據，而 shutdown 如果指定「不關閉發送方向」，就意味著 socket 還有發送數據的能力，所以內核就不會發送 FIN。

## 什麼情況會出現三次揮手？

當被動關閉方（上圖的服務端）在 TCP 揮手過程中，「**沒有數據要發送」並且「開啟了 TCP 延遲確認機制」，那麼第二和第三次揮手就會合並傳輸，這樣就出現了三次揮手。**

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/d7b349efa4f94453943b433b704a4ca8.png)


然後因為 TCP 延遲確認機制是默認開啟的，所以導致我們抓包時，看見三次揮手的次數比四次揮手還多。

> 什麼是  TCP 延遲確認機制？

當發送沒有攜帶數據的 ACK，它的網絡效率也是很低的，因為它也有 40 個字節的 IP 頭 和 TCP 頭，但卻沒有攜帶數據報文。
為瞭解決 ACK 傳輸效率低問題，所以就衍生出了 **TCP 延遲確認**。
TCP 延遲確認的策略：

- 當有響應數據要發送時，ACK 會隨著響應數據一起立刻發送給對方
- 當沒有響應數據要發送時，ACK 將會延遲一段時間，以等待是否有響應數據可以一起發送
- 如果在延遲等待發送 ACK 期間，對方的第二個數據報文又到達了，這時就會立刻發送 ACK

![](https://img-blog.csdnimg.cn/33f3d2d54a924b0a80f565038327e0e4.png)


延遲等待的時間是在 Linux 內核中定義的，如下圖：

![](https://img-blog.csdnimg.cn/ae241915337a4d2c9cb2f7ab91e6661d.png)

關鍵就需要 HZ 這個數值大小，HZ 是跟系統的時鐘頻率有關，每個操作系統都不一樣，在我的 Linux 系統中 HZ 大小是 1000，如下圖：

![](https://img-blog.csdnimg.cn/7a67bd4dc2894335b974e38674ba90b4.png)


知道了 HZ 的大小，那麼就可以算出：

- 最大延遲確認時間是 200 ms （1000/5）
- 最短延遲確認時間是 40 ms （1000/25）

> 怎麼關閉 TCP 延遲確認機制？

如果要關閉 TCP 延遲確認機制，可以在 Socket 設置裡啟用 TCP_QUICKACK。

```cpp
// 1 表示開啟 TCP_QUICKACK，即關閉 TCP 延遲確認機制
int value = 1;
setsockopt(socketfd, IPPROTO_TCP, TCP_QUICKACK, (char*)& value, sizeof(int));
```

### 實驗驗證

#### 實驗一

接下來，來給大家做個實驗，驗證這個結論：

> 當被動關閉方（上圖的服務端）在 TCP 揮手過程中，「**沒有數據要發送」並且「開啟了 TCP 延遲確認機制」，那麼第二和第三次揮手就會合並傳輸，這樣就出現了三次揮手。**


服務端的代碼如下，做的事情很簡單，就讀取數據，然後當 read 返回 0 的時候，就馬上調用 close 關閉連接。因為 TCP 延遲確認機制是默認開啟的，所以不需要特殊設置。

```cpp
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <netinet/tcp.h>

#define MAXLINE 1024

int main(int argc, char *argv[])
{

    // 1. 創建一個監聽 socket
    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    if(listenfd < 0)
    {
        fprintf(stderr, "socket error : %s\n", strerror(errno));
        return -1;
    }

    // 2. 初始化服務器地址和端口
    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(struct sockaddr_in));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(8888);

    // 3. 綁定地址+端口
    if(bind(listenfd, (struct sockaddr *)(&server_addr), sizeof(struct sockaddr)) < 0)
    {
        fprintf(stderr,"bind error:%s\n", strerror(errno));
        return -1;
    }

    printf("begin listen....\n");

    // 4. 開始監聽
    if(listen(listenfd, 128))
    {
        fprintf(stderr, "listen error:%s\n\a", strerror(errno));
        exit(1);
    }


    // 5. 獲取已連接的socket
    struct sockaddr_in client_addr;
    socklen_t client_addrlen = sizeof(client_addr);
    int clientfd = accept(listenfd, (struct sockaddr *)&client_addr, &client_addrlen);
    if(clientfd < 0) {
        fprintf(stderr, "accept error:%s\n\a", strerror(errno));
        exit(1);
    }

    printf("accept success\n");

    char message[MAXLINE] = {0};
    
    while(1) {
        //6. 讀取客戶端發送的數據
        int n = read(clientfd, message, MAXLINE);
        if(n < 0) { // 讀取錯誤
            fprintf(stderr, "read error:%s\n\a", strerror(errno));
            break;
        } else if(n == 0) {  // 返回 0 ，代表讀到 FIN 報文
            fprintf(stderr, "client closed \n");
            close(clientfd); // 沒有數據要發送，立馬關閉連接
            break;
        }

        message[n] = 0; 
        printf("received %d bytes: %s\n", n, message);
    }
	
    close(listenfd);
    return 0;
}
```

客戶端代碼如下，做的事情也很簡單，與服務端連接成功後，就發送數據給服務端，然後睡眠一秒後，就調用 close 關閉連接，所以客戶端是主動關閉方：

```cpp
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>

int main(int argc, char *argv[])
{

    // 1. 創建一個監聽 socket
    int connectfd = socket(AF_INET, SOCK_STREAM, 0);
    if(connectfd < 0)
    {
        fprintf(stderr, "socket error : %s\n", strerror(errno));
        return -1;
    }

    // 2. 初始化服務器地址和端口
    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(struct sockaddr_in));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(8888);
    
    // 3. 連接服務器
    if(connect(connectfd, (struct sockaddr *)(&server_addr), sizeof(server_addr)) < 0)
    {
        fprintf(stderr,"connect error:%s\n", strerror(errno));
        return -1;
    }

    printf("connect success\n");


    char sendline[64] = "hello, i am xiaolin";

    //4. 發送數據
    int ret = send(connectfd, sendline, strlen(sendline), 0);
    if(ret != strlen(sendline)) {
        fprintf(stderr,"send data error:%s\n", strerror(errno));
        return -1;
    }

    printf("already send %d bytes\n", ret);

    sleep(1);

    //5. 關閉連接
    close(connectfd);
    return 0;
}
```

編譯服務端和客戶端的代碼：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/291c6bdf93fa4e04b1606eef57d76836.png)




先啟用服務端：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/a975aa542caf41b2a1f303563df697b7.png)


然後用 tcpdump 工具開始抓包，命令如下：

```bash
tcpdump -i lo tcp and port 8888 -s0 -w /home/tcp_close.pcap
```

然後啟用客戶端，可以看到，與服務端連接成功後，發完數據就退出了。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/8ea9f527a68a4c0184edc8842aaf55d6.png)


此時，服務端的輸出：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/ff5f9ae91a3a4576b59e6e9c4716464d.png)


接下來，我們來看看抓包的結果。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/b542a2777aca4419b47205484b52cc03.png)


可以看到，TCP 揮手次數是 3 次。

所以，下面這個結論是沒問題的。

> 結論：當被動關閉方（上圖的服務端）在 TCP 揮手過程中，「**沒有數據要發送」並且「開啟了 TCP 延遲確認機制（默認會開啟）」，那麼第二和第三次揮手就會合並傳輸，這樣就出現了三次揮手。**

#### 實驗二

我們再做一次實驗，來看看**關閉 TCP 延遲確認機制，會出現四次揮手嗎？**

客戶端代碼保持不變，服務端代碼需要增加一點東西。

在上面服務端代碼中，增加了打開了 TCP_QUICKACK （快速應答）機制的代碼，如下：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/fbbe19e6b1cc4a21b024588950b88eee.png)


編譯好服務端代碼後，就開始運行服務端和客戶端的代碼，同時用 tcpdump 進行抓包。

抓包的結果如下，可以看到是四次揮手。
![在這裡插入圖片描述](https://img-blog.csdnimg.cn/b6327b1057d64f54997c0eb322b28a55.png)


所以，當被動關閉方（上圖的服務端）在 TCP 揮手過程中，「**沒有數據要發送」，同時「關閉了 TCP 延遲確認機制」，那麼就會是四次揮手。**

> 設置 TCP_QUICKACK 的代碼，為什麼要放在 read 返回 0 之後？


我也是多次實驗才發現，在 bind 之前設置 TCP_QUICKACK 是不生效的，只有在 read 返回 0 的時候，設置 TCP_QUICKACK 才會出現四次揮手。

網上查了下資料說，設置 TCP_QUICKACK 並不是永久的，所以每次讀取數據的時候，如果想要立刻回 ACK，那就得在每次讀取數據之後，重新設置 TCP_QUICKACK。

而我這裡的實驗，目的是為了當收到客戶端的 FIN 報文（第一次揮手）後，立馬回 ACK 報文。所以就在 read 返回 0 的時候，設置 TCP_QUICKACK。當然，實際應用中，沒人會在這個位置設置 TCP_QUICKACK，因為操作系統都通過 TCP 延遲確認機制幫我們把四次揮手優化成了三次揮手了。

## 總結

當被動關閉方在 TCP 揮手過程中，如果「沒有數據要發送」，同時「沒有開啟 TCP_QUICKACK（默認情況就是沒有開啟，沒有開啟 TCP_QUICKACK，等於就是在使用 TCP 延遲確認機制）」，那麼第二和第三次揮手就會合並傳輸，這樣就出現了三次揮手。

**所以，出現三次揮手現象，是因為 TCP 延遲確認機制導致的。**

----

***哈嘍，我是小林，就愛圖解計算機基礎，如果覺得文章對你有幫助，歡迎微信搜索「小林coding」***

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)

