# 4.19 服務端沒有 listen，客戶端發起連接建立，會發生什麼？

大家好，我是小林。

早上看到一個讀者說面字節三面的時候，問了這個問題：

![圖片](https://img-blog.csdnimg.cn/img_convert/5f5b9c96c86580e3f14978d5c10c7721.jpeg)

這位讀者的角度是以為服務端沒有調用 listen，客戶端會 ping 不通服務器，很明顯，搞錯了。

ping 使用的協議是 ICMP，屬於網絡層的事情，而面試官問的是傳輸層的問題。

針對這個問題，服務端如果只 bind 了 IP 地址和端口，而沒有調用 listen 的話，然後客戶端對服務端發起了 TCP 連接建立，此時那麼會發生什麼呢？

## 做個實驗

這個問題，自己做個實驗就知道了。

我用下面這個程序作為例子，綁定了 IP 地址 + 端口，而沒有調用 listen。

```c
/*******服務器程序  TCPServer.c ************/
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
    int sockfd, ret;
    struct sockaddr_in server_addr;

    /* 服務器端創建 tcp socket 描述符 */
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if(sockfd < 0)
    {
        fprintf(stderr, "Socket error:%s\n\a", strerror(errno));
        exit(1);
    }

    /* 服務器端填充 sockaddr 結構 */
    bzero(&server_addr, sizeof(struct sockaddr_in));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(8888);
  
  /* 綁定 ip + 端口 */
    ret = bind(sockfd, (struct sockaddr *)(&server_addr), sizeof(struct sockaddr));
    if(ret < 0)
    {
        fprintf(stderr, "Bind error:%s\n\a", strerror(errno));
        exit(1);
    }
  
  //沒有調用 listen
    
    sleep(1000);
    close(sockfd);
    return 0;
}
```

然後，我用瀏覽器訪問這個地址：http://121.43.173.240:8888/

![圖片](https://img-blog.csdnimg.cn/img_convert/5bdb5443db5b97ff724ab94e014af6a5.png)

報錯連接服務器失敗。

同時，我也用抓包工具，抓了這個過程。

![圖片](https://img-blog.csdnimg.cn/img_convert/a77921ffafbbff86d07983ca0db3e6e0.png)

可以看到，客戶端對服務端發起 SYN 報文後，服務端回了 RST 報文。

所以，這個問題就有了答案，**服務端如果只 bind 了 IP 地址和端口，而沒有調用 listen 的話，然後客戶端對服務端發起了連接建立，服務端會回 RST 報文。**

## 源碼分析

接下來，帶大家源碼分析一下。

Linux 內核處理收到 TCP 報文的入口函數是  tcp_v4_rcv，在收到 TCP 報文後，會調用 __inet_lookup_skb 函數找到 TCP 報文所屬 socket 。

```
int tcp_v4_rcv(struct sk_buff *skb)
{
 ...
  
 sk = __inet_lookup_skb(&tcp_hashinfo, skb, th->source, th->dest);
 if (!sk)
  goto no_tcp_socket;
 ...
}
```

__inet_lookup_skb 函數首先查找連接建立狀態的socket（__inet_lookup_established），在沒有命中的情況下，才會查找監聽套接口（__inet_lookup_listener）。

![圖片](https://img-blog.csdnimg.cn/img_convert/88416aa95d255495e07fb3a002b2167b.png)

查找監聽套接口（__inet_lookup_listener）這個函數的實現是，根據目的地址和目的端口算出一個哈希值，然後在哈希表找到對應監聽該端口的 socket。

本次的案例中，服務端是沒有調用 listen 函數的，所以自然也是找不到監聽該端口的 socket。

所以，__inet_lookup_skb 函數最終找不到對應的 socket，於是跳轉到no_tcp_socket。

![圖片](https://img-blog.csdnimg.cn/img_convert/54ee363e149ee3dfba30efb1a542ef5c.png)

在這個錯誤處理中，只要收到的報文（skb）的「校驗和」沒問題的話，內核就會調用 tcp_v4_send_reset 發送 RST 中止這個連接。

至此，整個源碼流程就解析完。

其實很多網絡的問題，大家都可以自己做實驗來找到答案的。

![圖片](https://img-blog.csdnimg.cn/img_convert/8d04584bf7fa40f02229d611a569f370.jpeg)

## 沒有 listen，能建立 TCP 連接嗎？

標題的問題在前面已經解答，**現在我們看另外一個相似的問題**。

之前看群消息，看到有讀者面試騰訊的時候，被問到這麼一個問題。

> 不使用 listen ，可以建立 TCP 連接嗎？

答案，**是可以的，客戶端是可以自己連自己的形成連接（TCP自連接），也可以兩個客戶端同時向對方發出請求建立連接（TCP同時打開），這兩個情況都有個共同點，就是沒有服務端參與，也就是沒有listen，就能建立連接**。

> 那沒有listen，為什麼還能建立連接？

我們知道執行 listen 方法時，會創建半連接隊列和全連接隊列。

三次握手的過程中會在這兩個隊列中暫存連接信息。

所以形成連接，前提是你得有個地方存放著，方便握手的時候能根據 IP + 端口等信息找到對應的 socket。

> 那麼客戶端會有半連接隊列嗎？

顯然沒有，因為客戶端沒有執行listen，因為半連接隊列和全連接隊列都是在執行 listen 方法時，內核自動創建的。

但內核還有個全局 hash 表，可以用於存放 sock 連接的信息。

這個全局 hash 表其實還細分為 ehash，bhash和listen_hash等，但因為過於細節，大家理解成有一個全局 hash 就夠了，

**在 TCP 自連接的情況中，客戶端在 connect 方法時，最後會將自己的連接信息放入到這個全局 hash 表中，然後將信息發出，消息在經過迴環地址重新回到 TCP 傳輸層的時候，就會根據 IP + 端口信息，再一次從這個全局 hash 中取出信息。於是握手包一來一回，最後成功建立連接**。

TCP 同時打開的情況也類似，只不過從一個客戶端變成了兩個客戶端而已。

> 做個實驗

客戶端自連接的代碼，TCP socket 可以 connect 它本身 bind 的地址和端口：


```c
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#define LOCAL_IP_ADDR		(0x7F000001) // IP 127.0.0.1
#define LOCAL_TCP_PORT		(34567) // 端口

int main(void)
{
	struct sockaddr_in local, peer;
	int ret;
	char buf[128];
	int sock = socket(AF_INET, SOCK_STREAM, 0);

	memset(&local, 0, sizeof(local));
	memset(&peer, 0, sizeof(peer));

	local.sin_family = AF_INET;
	local.sin_port = htons(LOCAL_TCP_PORT);
	local.sin_addr.s_addr = htonl(LOCAL_IP_ADDR);

	peer = local;	

    int flag = 1;
    ret = setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag));
    if (ret == -1) {
        printf("Fail to setsocket SO_REUSEADDR: %s\n", strerror(errno));
        exit(1);
    }

	ret = bind(sock, (const struct sockaddr *)&local, sizeof(local));
	if (ret) {
		printf("Fail to bind: %s\n", strerror(errno));
		exit(1);
	}
	
	ret = connect(sock, (const struct sockaddr *)&peer, sizeof(peer));
	if (ret) {
		printf("Fail to connect myself: %s\n", strerror(errno));
		exit(1);
	}
	
	printf("Connect to myself successfully\n");

    //發送數據
	strcpy(buf, "Hello, myself~");
	send(sock, buf, strlen(buf), 0);

	memset(buf, 0, sizeof(buf));
	
	//接收數據
	recv(sock, buf, sizeof(buf), 0);
	printf("Recv the msg: %s\n", buf);

    sleep(1000);
	close(sock);
	return 0;
}
```

編譯運行：

![](https://img-blog.csdnimg.cn/9db974179b9e4a279f7edb0649752c27.png)


通過 netstat 命令命令客戶端自連接的 TCP 連接：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/e2b116e843c14e468eadf9d30e1b877c.png)

從截圖中，可以看到 TCP socket 成功的“連接”了自己，併發送和接收了數據包，netstat 的輸出更證明瞭 TCP 的兩端地址和端口是完全相同的。

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)