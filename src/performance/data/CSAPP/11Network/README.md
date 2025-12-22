<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [第十一章：網絡編程](#%E7%AC%AC%E5%8D%81%E4%B8%80%E7%AB%A0%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B)
  - [11.1 客戶端-服務器編程模型](#111-%E5%AE%A2%E6%88%B7%E7%AB%AF-%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%BC%96%E7%A8%8B%E6%A8%A1%E5%9E%8B)
  - [11.2 網絡](#112-%E7%BD%91%E7%BB%9C)
  - [11.3 全球IP因特網](#113-%E5%85%A8%E7%90%83ip%E5%9B%A0%E7%89%B9%E7%BD%91)
    - [IP地址](#ip%E5%9C%B0%E5%9D%80)
    - [因特網域名](#%E5%9B%A0%E7%89%B9%E7%BD%91%E5%9F%9F%E5%90%8D)
    - [因特網連接](#%E5%9B%A0%E7%89%B9%E7%BD%91%E8%BF%9E%E6%8E%A5)
  - [11.4 套接字接口](#114-%E5%A5%97%E6%8E%A5%E5%AD%97%E6%8E%A5%E5%8F%A3)
    - [套接字地址結構](#%E5%A5%97%E6%8E%A5%E5%AD%97%E5%9C%B0%E5%9D%80%E7%BB%93%E6%9E%84)
    - [socket函數](#socket%E5%87%BD%E6%95%B0)
    - [connect函數](#connect%E5%87%BD%E6%95%B0)
    - [bind函數](#bind%E5%87%BD%E6%95%B0)
    - [listen函數](#listen%E5%87%BD%E6%95%B0)
    - [accept函數](#accept%E5%87%BD%E6%95%B0)
    - [主機和服務的轉換](#%E4%B8%BB%E6%9C%BA%E5%92%8C%E6%9C%8D%E5%8A%A1%E7%9A%84%E8%BD%AC%E6%8D%A2)
    - [套接字接口的輔助函數](#%E5%A5%97%E6%8E%A5%E5%AD%97%E6%8E%A5%E5%8F%A3%E7%9A%84%E8%BE%85%E5%8A%A9%E5%87%BD%E6%95%B0)
    - [echo客戶端和服務器示例](#echo%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%92%8C%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%A4%BA%E4%BE%8B)
  - [11.5 Web服務器](#115-web%E6%9C%8D%E5%8A%A1%E5%99%A8)
  - [11.6 綜合：TINY Web服務器](#116-%E7%BB%BC%E5%90%88tiny-web%E6%9C%8D%E5%8A%A1%E5%99%A8)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 第十一章：網絡編程

網絡應用依賴於很多概念：進程、信號、字節序、內存映射、動態內存分配等。

## 11.1 客戶端-服務器編程模型

每個網絡應用都基於**客戶端-服務器模型**（Client-Server Model）：
- 採用這個模型，一個應用由一個服務端進程和多個客戶端進程組成。
- 服務器管理某種資源，通過操作這種資源為客戶端提供服務。
- 客戶端-服務器模型中的基本操作是事務（transaction），一個客戶端-服務器模型由四步組成：
    - 客戶端需要服務，像服務器發送一個請求，發起一個事務。
    - 服務器收到請求，解釋它，以適當方式操作它的資源。
    - 服務器向客戶端發送一個響應，並等待下一個請求。
    - 客戶端收到響應並處理它。
- 這裡的客戶與服務器並不是機器或者主機，而是進程。一臺主機上可以同時運行許多不同的客戶端和服務器，而且一個客戶端和服務器的事務可以在同一臺或是不同的主機上。
- 客戶端-服務器事務不同於數據庫事務，沒有數據庫事務的任何特性，比如原子性。在之類，客戶和服務器端的事務僅僅是客戶端和服務器執行的一系列步驟。

## 11.2 網絡

網絡是一個非常複雜的系統，這裡只關注其提供的思維模型：
- 對主機而言，網絡是一種IO設備，是數據源和數據接收方。
- 一個插到I/O總線擴展槽的適配器，提供了到網絡的物理接口。從網絡上接受的數據從適配器經過I/O和內存總線複製到內存，通常是通過DMA傳送，類似地，數據也能從內存複製到網絡適配器。
- 物理上來說，網絡是一個按照地理遠近組成的層次系統，最底層是LAN（Local Area Network，**局域網**）。現在最流行的以太網技術是**以太網**（Ethernet）。
- 一個以太網段包括一個**集線器**（hub）和一系列電纜連接起來的主機，每個以太網適配器都有一個全球唯一的48位的硬件（MAC）地址，存儲在適配器上。
- 一臺主機可以發送一段位（稱為**幀**frame）到這個網段的其他任何主機。每個幀包括一些固定長度的**頭部**（header）位，用來標識此幀的源和目的地以及此幀的長度，此後跟隨的數據稱為**有效載荷**（payload）。
- 使用電纜或者**網橋**（bridge），多個以太網可以連接成較大的局域網，成為橋接以太網（bridged Ethernet）。不同電纜可以擁有不同的帶寬。
- 網橋會聰明地將幀發送到需要的端口，而不是發送到所有端口。
- 在層次的更高級別中，多個不兼容的局域網可以通過叫做路由器（router）的特殊計算機連接起來，組成一個internet（互聯網絡）。
- 每臺路由器對於它所連接到的每個網絡都有一個適配器（端口）。路由器也能連接到廣域網（WAN，Wide-Area Network）。
- 互聯網絡的重要特徵是：它能由採用不同和不兼容技術的各種局域網和廣域網組成。
- 那麼如何讓某臺源主機跨過不兼容的網絡向另一臺目的主機發送數據呢？解決方法是實現一層運行在每臺主機和路由器上的**協議軟件**，它消除了不同網絡之間的差異。
- 這個軟件就是協議，這種協議控制主機和路由器如何協同工作來實現數據傳輸，這種協議提供兩種基本能力：
    - 命名機制：不同局域網技術有不同和不兼容的方式分配主機地址，互聯網協議通過定義一種一致的主機地址格式消除這種差異。每臺主機會被分配到至少一個互聯網絡地址（internet address），這個地址唯一標識一臺主機。
    - 傳送機制：不同的聯網技術有不同不兼容的在電纜上編碼位和將這些為封裝成幀的方式。互聯網協議通過定義一種把數據位捆紮成不連續的片（稱為**包**）的統一方式，消除了這種差異。

## 11.3 全球IP因特網

- 全球IP因特網是最著名和成功的互聯網實現，每臺因特網主機都運行實現TCP/IP協議的軟件，幾乎每個現代計算機都支持這個協議。
- 因特網的客戶端和服務端混合使用**套接字接口**函數和Unix IO函數進行通信。
- 通常套接字函數實現為系統調用，這些系統調用將會陷入內核，並調用內核模式的TCP/IP函數。
- TCP/IP是一個協議族，其中每一個都提供不同的功能。
    - 例如，IP協議提供基本的命名方法和遞送機制，這種遞送機制是從一臺主機到另一臺主機的。
    - UDP在其上稍微進行了擴展，這樣，它在進程間而不是主機間傳播。但和IP一樣，依然是不可靠的。
    - TCP是一個構建在IP之上的複雜協議，提供了進程間可靠的全雙工（雙向）**連接**。
- 這裡為了討論方便，將不討論太多細節，只討論TCP和IP提供的某些基本功能，不討論UDP。
- 從程序員角度，可以將互聯網抽象為一個世界範圍的主機集合：
    - 主機集合被映射到32位的IP地址。
    - 這些IP地址被映射為一組成為因特網域名的標識符。
    - 因特網主機的進程能夠通過連接和任何其他因特網主機上的進程通信。

### IP地址

因為IPV6還未普及，這裡僅基於IPV4，原理是一樣。IP地址：
- IPV4地址原則上來說可以存在32位無符號整數中。
```C
struct in_addr {
    uint32_t s_addr; // big-endian
};
```
- 原則上來說放在32位無符號整數即可，但用一個結構保存是歷史原因。
- TCP/IP規定任意整數數據項都是用大斷序存放，因為因特網主機可能有不同字節序。
- IP地址結構中存放的總是大端序存放的，如果要將主機字節序和網絡字節序相互轉換可以用：
```C
#include <arpa/inet.h>
uint32_t htonl(uint32_t hostlong);
uint16_t htons(uint16_t hostshort);
uint32_t ntohl(uint32_t netlong);
uint16_t ntohs(uint16_t netshort);
```
- IP地址通常用點分十進制表示，`hostname -i`可以獲取本機IP地址。
- 轉換點分十進制IP和整數IP：
```C
#include <arpa/inet.h>
int inet_pton(int af, const char *src, void *dst);
const char *inet_ntop(int af, const void *src,
                      char *dst, socklen_t size);
```
- `af`可以是`AF_INET AF_INET6`表示IPV4或者IPV6地址。

### 因特網域名

互聯網客戶端和服務端相互通信使用IP地址，但是大整數很難記住，點分十進制也不是很好記，所以互聯網定義了一組更為人性化的域名（domain name），以及一種將域名映射到IP地址的機制。
- 域名是一串用點號分隔的單詞（字母、數字或破折號），比如`hello.cmu.edu`。
- 域名集合形成了一個樹狀的層次結構，每個域名編碼了它在層次中的一個位置。從上到下稱為頂級域名、二級域名、以此類推。
- 域名和IP的映射由分佈世界範圍內的數據庫來維護（DNS）。
- 可以使用`nslookup`命令探究DNS映射的一些屬性。
- 每臺互聯網主機都有本地域名`localhost`，總是映射到`127.0.0.1`：
```shell
tch@KillingBoat:~/CSAPP$ nslookup localhost
Server:         172.26.0.1
Address:        172.26.0.1#53

Non-authoritative answer:
Name:   localhost
Address: 127.0.0.1
Name:   localhost
Address: ::1
```
- 我們可以用這個命令查看某個網址的IP：
```shell
tch@KillingBoat:~/CSAPP$ nslookup google.com
Server:         172.26.0.1
Address:        172.26.0.1#53

Non-authoritative answer:
Name:   google.com
Address: 172.217.160.110
```
- 某些域名可以映射到多個IP，某些合法域名則沒有映射到任何IP。

### 因特網連接

互聯網客戶端和服務端通過在連接上發送和接收字節流來通信：
- 連接是點對點、全雙工、可靠的。
- **套接字**（socket）是連接的端點，由一個IP地址和一個16位端口（port）構成。
- 客戶端發起連接時，端口由內核臨時分配，稱為臨時端口。而服務器端端口一般是固定的，比如HTTP固定用80端口。
- 一個連接由兩端的套接字地址唯一確定，這對套接字地址叫做套接字對（socket pair）：由一個元組`(cliaddr : cliport, servaddr : servport)`唯一確定。

## 11.4 套接字接口

套接字接口（socket interface）是一組函數，和Unix IO函數結合起來，用以創建網絡應用。大多數現代系統上都實現了套接字接口，包括所有類Unix、Windows、MacOS上。

### 套接字地址結構

從Linux內核來看，套接字就是通信的一個端點。從Linux程序員角度來看，套接字就是一個打開文件。

套接字結構：
```C
// IP socket address structure
struct sockaddr_in
{
    uint16_t        sin_family;  // protocal family, always AF_INET
    uint16_t        sin_port;    // port number
    struct in_addr  sin_addr;    // IP address
    unsigned char   sin_zero[8]; // Pad to sizeof(struct sockaddr)
};
// generic  socket address structure (for connect bind and accept)
struct sockaddr 
{
    uint16_t    sa_family;      // protocal family
    char        sa_data[14];    // address data
}
```
- `sockaddr`的存在是為了統一各種類型的套接字，實際的套接字比如`sockaddr_in`需要轉化為`sockaddr`。對應的前者的後三個成員就存在了後者的`sa_data`數組中。

### socket函數

客戶端和服務器使用`socket`函數來創建一個套接字描述符（socket descriptor）：
```C
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
int socket(int domain, int type, int protocol);
```
- 出錯返回`-1`，成功返回非負描述符。
- 如果想使套接字成為連接的一個端點，那麼就使用如下硬編碼來調用：
```C
clientfd = socket(AF_INET, SOCK_STREAM, 0);
```
- `AF_INET`表明使用IPV4，`SOCK_STREAM`表明這個套接字是連接的一個端點。不過最好的方式是使用`getaddrinfo`來自動生成這些參數，這樣代碼就與協議無關了。
- 返回的描述符是僅部分打開的，還不能用於讀寫，如何完成接下來的工作，取決於是服務端還是客戶端。

### connect函數

客戶端通過`connect`來建立和服務器的連接：
```C
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
int connect(int sockfd, const struct sockaddr *addr,
            socklen_t addrlen);
```
- `connect`函數試圖與套接字地址為`addr`的服務器建立一個因特網連接，其中`addrlen`是`sizeof(sockaddr_in)`。
- `connect`函數會阻塞，一直到連接成功建立，或者發生錯誤，如果成功，`clientfd`現在就已經準備好可以讀寫了，得到的連接由套接字對`(x:y, addr.sin_addr:addr.sin_port)`標識。
- 它唯一確定了客戶端主機上的客戶端進程。對於`socket`，更好方法是用`getaddrinfo`為`connect`提供參數。

剩下的函數：`bind listen accept`是服務器用來和客戶端建立連接的。

### bind函數

`bind`函數告訴內核將`addr`中的服務器套接字地址和套接字描述符`sockfd`聯繫起來。
```C
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
int bind(int sockfd, const struct sockaddr *addr,
         socklen_t addrlen);
```
- `addrlen`是`sizeof(sockaddr_in)`。

### listen函數

客戶端是發起連接請求的主動實體，服務器是等待來自客戶端的連接請求的被動實體：
```C
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
int listen(int sockfd, int backlog);
```
- 默認情況下，內核會認為`socket`創建的描述符應用於主動套接字（active socket），存在於一個連接的客戶端。服務端調用`listen`函數告訴內核，描述符是被用於服務器而不是客戶端使用的。
- `listen`將一個主動套接字轉換為一個監聽套接字（listening socket），該套接字可以接受來自客戶端的連接請求。
- `backlog`參數暗示了內核在開始拒絕連接請求前，隊列中要排隊的未完成連接請求數量。確切含義這裡不表，設為1024即可。

### accept函數

等待客戶端的連接請求：
```C
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
#define _GNU_SOURCE             /* See feature_test_macros(7) */
#include <sys/socket.h>
int accept4(int sockfd, struct sockaddr *addr,
            socklen_t *addrlen, int flags);
```
- 服務器調用`accept`來等待來自客戶端的連接請求到達監聽描述符`sockfd`，然後在`addr`中填寫客戶端的套接字地址，並返回一個已連接描述符（connected descritor），失敗則返回-1。
- 這個描述符可以被用來利用Unix IO函數與客戶端通信。

監聽描述符與已連接描述符：
- 監聽描述符作為客戶端請求的一個端點，通常被創建一次，並存在於服務器的整個生命週期。
- 已連接描述符是客戶端和服務器之間已經建立起來的連接的一個端點，每次接受連接請求會創建一次，只存在於服務器為一個客戶端服務的過程中。
- 區分兩者可以使我們在同一個監聽描述符上建立多個連接，用於併發服務器。比如每次一個連接請求到達監聽描述符時，可以派生（fork）一個新進程，通過已連接描述符和客戶端通信。並同時在其他進程中繼續監聽。

### 主機和服務的轉換

Linux提供了一些函數實現二進制套接字地址結構、主機名、主機地址、服務名、端口號的字符串表示之間的相互轉換：
```C
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
int getaddrinfo(const char *node, const char *service,
                const struct addrinfo *hints,
                struct addrinfo **res);
void freeaddrinfo(struct addrinfo *res);
const char *gai_strerror(int errcode);
```
- 和套接字接口一起使用，能夠使我們編寫獨立於任何特定版本的IP協議的網絡程序。
- `getaddrinfo`將主機名、主機地址、服務名、端口號的字符串轉換為套接字地址結構。
- 與只相反的相反的函數是`getnameinfo`：
```C
#include <sys/socket.h>
#include <netdb.h>
int getnameinfo(const struct sockaddr *addr, socklen_t addrlen,
                char *host, socklen_t hostlen,
                char *serv, socklen_t servlen, int flags);
```

### 套接字接口的輔助函數

略。

### echo客戶端和服務器示例

略，作為替代實現一個簡單的程序作為替代：客戶端輸入內容，並不斷傳輸到服務端顯示。

## 11.5 Web服務器

HTTP協議，端口80，略。

## 11.6 綜合：TINY Web服務器

略。
