# 4.20 沒有 accept，能建立 TCP 連接嗎？

> 來源：公眾號@小白debug
> 原文地址：[阿里二面：沒有 accept，能建立 TCP 連接嗎？](https://mp.weixin.qq.com/s/oPX_JoZUaLn6sW54yppfvA)

大家好，我是小林。

這次，我們來討論一下，**沒有 accept，能建立 TCP 連接嗎？**

下面這個動圖，是我們平時客戶端和服務端建立連接時的代碼流程。

![握手建立連接流程](https://img-blog.csdnimg.cn/img_convert/e0d405a55626eb8e4a52553a54680618.gif)

對應的是下面一段簡化過的服務端偽代碼。

```c
int main()
{
    /*Step 1: 創建服務器端監聽socket描述符listen_fd*/    
    listen_fd = socket(AF_INET, SOCK_STREAM, 0);

    /*Step 2: bind綁定服務器端的IP和端口，所有客戶端都向這個IP和端口發送和請求數據*/    
    bind(listen_fd, xxx);

    /*Step 3: 服務端開啟監聽*/    
    listen(listen_fd, 128);

    /*Step 4: 服務器等待客戶端的鏈接，返回值cfd為客戶端的socket描述符*/    
    cfd = accept(listen_fd, xxx);

      /*Step 5: 讀取客戶端發來的數據*/
      n = read(cfd, buf, sizeof(buf));
}
```

估計大家也是老熟悉這段偽代碼了。

需要注意的是，在執行`listen()`方法之後還會執行一個`accept()`方法。

**一般情況**下，如果啟動服務器，會發現最後程序會**阻塞在**`accept()`裡。

此時服務端就算ok了，就等客戶端了。

那麼，再看下簡化過的客戶端偽代碼。

```c
int main()
{
    /*Step 1: 創建客戶端端socket描述符cfd*/    
    cfd = socket(AF_INET, SOCK_STREAM, 0);

    /*Step 2: connect方法,對服務器端的IP和端口號發起連接*/    
    ret = connect(cfd, xxxx);

    /*Step 4: 向服務器端寫數據*/
    write(cfd, buf, strlen(buf));
}
```

客戶端比較簡單，創建好`socket`之後，直接就發起`connect`方法。

此時回到服務端，會發現**之前一直阻塞的accept方法，返回結果了**。

這就算兩端成功建立好了一條連接。之後就可以愉快的進行讀寫操作了。

那麼，我們今天的問題是，**如果沒有這個accept方法，TCP連接還能建立起來嗎？**

其實只要在執行`accept()` 之前執行一個 `sleep(20)`，然後立刻執行客戶端相關的方法，同時抓個包，就能得出結論。

![不執行accept時抓包結果](https://img-blog.csdnimg.cn/img_convert/2cfc1d028f3e37f10c2f81375ddb998a.png)

從抓包結果看來，**就算不執行accept()方法，三次握手照常進行，並順利建立連接。**

更騷氣的是，**在服務端執行accept()前，如果客戶端發送消息給服務端，服務端是能夠正常回復ack確認包的。**

並且，`sleep(20)`結束後，服務端正常執行`accept()`，客戶端前面發送的消息，還是能正常收到的。

通過這個現象，我們可以多想想為什麼。順便好好了解下三次握手的細節。

## 三次握手的細節分析

我們先看面試八股文的老股，三次握手。

![TCP三次握手](https://img-blog.csdnimg.cn/img_convert/8d55a06f2efa946921ff61a008c76b00.png)

服務端代碼，對socket執行bind方法可以綁定監聽端口，然後執行`listen方法`後，就會進入監聽（`LISTEN`）狀態。內核會為每一個處於`LISTEN`狀態的`socket` 分配兩個隊列，分別叫**半連接隊列和全連接隊列**。

![每個listen Socket都有一個全連接和半連接隊列](https://img-blog.csdnimg.cn/img_convert/d7e2d60b28b0f9b460aafbf1bd6e7892.png)

### 半連接隊列、全連接隊列是什麼

![半連接隊列和全連接隊列](https://img-blog.csdnimg.cn/img_convert/36242c85809865fcd2da48594de15ebb.png)

- **半連接隊列（SYN隊列）**，服務端收到**第一次握手**後，會將`sock`加入到這個隊列中，隊列內的`sock`都處於`SYN_RECV` 狀態。
- **全連接隊列（ACCEPT隊列）**，在服務端收到**第三次握手**後，會將半連接隊列的`sock`取出，放到全連接隊列中。隊列裡的`sock`都處於 `ESTABLISHED`狀態。這裡面的連接，就**等著服務端執行accept()後被取出了。**

看到這裡，文章開頭的問題就有了答案，建立連接的過程中根本不需要`accept()`參與， **執行accept()只是為了從全連接隊列裡取出一條連接。**

我們把話題再重新回到這兩個隊列上。

雖然都叫**隊列**，但其實**全連接隊列（icsk_accept_queue）是個鏈表**，而**半連接隊列（syn_table）是個哈希表**。

![半連接全連接隊列的內部結構](https://img-blog.csdnimg.cn/img_convert/6f964fb09d6971dab1762a45dfa30b3b.png)

### 為什麼半連接隊列要設計成哈希表

先對比下**全連接裡隊列**，他本質是個鏈表，因為也是線性結構，說它是個隊列也沒毛病。它裡面放的都是已經建立完成的連接，這些連接正等待被取走。而服務端取走連接的過程中，並不關心具體是哪個連接，只要是個連接就行，所以直接從隊列頭取就行了。這個過程算法複雜度為`O(1)`。

而**半連接隊列**卻不太一樣，因為隊列裡的都是不完整的連接，嗷嗷等待著第三次握手的到來。那麼現在有一個第三次握手來了，則需要從隊列裡把相應IP端口的連接取出，**如果半連接隊列還是個鏈表，那我們就需要依次遍歷，才能拿到我們想要的那個連接，算法複雜度就是O(n)。**

而如果將半連接隊列設計成哈希表，那麼查找半連接的算法複雜度就回到`O(1)`了。

因此出於效率考慮，全連接隊列被設計成鏈表，而半連接隊列被設計為哈希表。

### 怎麼觀察兩個隊列的大小

#### 查看全連接隊列

```shell
# ss -lnt
State      Recv-Q Send-Q     Local Address:Port           Peer Address:Port
LISTEN     0      128        127.0.0.1:46269              *:*              
```

通過`ss -lnt`命令，可以看到全連接隊列的大小，其中`Send-Q`是指全連接隊列的最大值，可以看到我這上面的最大值是`128`；`Recv-Q`是指當前的全連接隊列的使用值，我這邊用了`0`個，也就是全連接隊列裡為空，連接都被取出來了。

當上面`Send-Q`和`Recv-Q`數值很接近的時候，那麼全連接隊列可能已經滿了。可以通過下面的命令查看是否發生過隊列**溢出**。

```shell
# netstat -s | grep overflowed
    4343 times the listen queue of a socket overflowed
```

上面說明發生過`4343次`全連接隊列溢出的情況。這個查看到的是**歷史發生過的次數**。

如果配合使用`watch -d` 命令，可以自動每`2s`間隔執行相同命令，還能高亮顯示變化的數字部分，如果溢出的數字不斷變多，說明**正在發生**溢出的行為。

```shell
# watch -d 'netstat -s | grep overflowed'
Every 2.0s: netstat -s | grep overflowed                                
Fri Sep 17 09:00:45 2021

    4343 times the listen queue of a socket overflowed
```

#### 查看半連接隊列

半連接隊列沒有命令可以直接查看到，但因為半連接隊列裡，放的都是`SYN_RECV`狀態的連接，那可以通過統計處於這個狀態的連接的數量，間接獲得半連接隊列的長度。

```shell
# netstat -nt | grep -i '127.0.0.1:8080' | grep -i 'SYN_RECV' | wc -l
0
```

注意半連接隊列和全連接隊列都是掛在某個`Listen socket`上的，我這裡用的是`127.0.0.1:8080`，大家可以替換成自己想要查看的**IP端口**。

可以看到我的機器上的半連接隊列長度為`0`，這個很正常，**正經連接誰會沒事老待在半連接隊列裡。**

當隊列裡的半連接不斷增多，最終也是會發生溢出，可以通過下面的命令查看。

```shell
# netstat -s | grep -i "SYNs to LISTEN sockets dropped" 
    26395 SYNs to LISTEN sockets dropped
```

可以看到，我的機器上一共發生了`26395`次半連接隊列溢出。同樣建議配合`watch -d` 命令使用。

```shell
# watch -d 'netstat -s | grep -i "SYNs to LISTEN sockets dropped"'
Every 2.0s: netstat -s | grep -i "SYNs to LISTEN sockets dropped"       
Fri Sep 17 08:36:38 2021

    26395 SYNs to LISTEN sockets dropped
```

### 全連接隊列滿了會怎麼樣？

如果隊列滿了，服務端還收到客戶端的第三次握手ACK，默認當然會丟棄這個ACK。

但除了丟棄之外，還有一些附帶行為，這會受 `tcp_abort_on_overflow` 參數的影響。

```shell
# cat /proc/sys/net/ipv4/tcp_abort_on_overflow
0
```

- `tcp_abort_on_overflow`設置為 0，全連接隊列滿了之後，會丟棄這個第三次握手ACK包，並且開啟定時器，重傳第二次握手的SYN+ACK，如果重傳超過一定限制次數，還會把對應的**半連接隊列裡的連接**給刪掉。

![tcp_abort_on_overflow為0](https://img-blog.csdnimg.cn/img_convert/874f2fb7108020fd4dcfa021f377ec66.png)

- `tcp_abort_on_overflow`設置為 1，全連接隊列滿了之後，就直接發RST給客戶端，效果上看就是連接斷了。

這個現象是不是很熟悉，服務端**端口未監聽**時，客戶端嘗試去連接，服務端也會回一個RST。這兩個情況長一樣，所以客戶端這時候收到RST之後，其實無法區分到底是**端口未監聽**，還是**全連接隊列滿了**。

![tcp_abort_on_overflow為1](https://img-blog.csdnimg.cn/img_convert/6a01c5df74748870a69921da89825d9c.png)

### 半連接隊列要是滿了會怎麼樣

**一般是丟棄**，但這個行為可以通過 `tcp_syncookies` 參數去控制。但比起這個，更重要的是先了解下半連接隊列為什麼會被打滿。

首先我們需要明白，一般情況下，半連接的"生存"時間其實很短，只有在第一次和第三次握手間，如果半連接都滿了，說明服務端瘋狂收到第一次握手請求，如果是線上遊戲應用，能有這麼多請求進來，那說明你可能要富了。但現實往往比較骨感，你可能遇到了**SYN Flood攻擊**。

所謂**SYN Flood攻擊**，可以簡單理解為，攻擊方模擬客戶端瘋狂發第一次握手請求過來，在服務端憨憨地回覆第二次握手過去之後，客戶端死活不發第三次握手過來，這樣做，可以把服務端半連接隊列打滿，從而導致正常連接不能正常進來。

![syn攻擊](https://img-blog.csdnimg.cn/img_convert/d894de5374a12bd5d75d86d4a718d186.png)

那這種情況怎麼處理？有沒有一種方法可以**繞過半連接隊列**？

有，上面提到的`tcp_syncookies`派上用場了。

```shell
# cat /proc/sys/net/ipv4/tcp_syncookies
1
```

當它被設置為1的時候，客戶端發來**第一次握手**SYN時，服務端**不會將其放入半連接隊列中**，而是直接生成一個`cookies`，這個`cookies`會跟著**第二次握手**，發回客戶端。客戶端在發**第三次握手**的時候帶上這個`cookies`，服務端驗證到它就是當初發出去的那個，就會建立連接並放入到全連接隊列中。可以看出整個過程不再需要半連接隊列的參與。

![tcp_syncookies=1](https://img-blog.csdnimg.cn/img_convert/d696b8b345526533bde8fa990e205c32.png)

#### 會有一個cookies隊列嗎

生成是`cookies`，保存在哪呢？**是不是會有一個隊列保存這些cookies？**

我們可以反過來想一下，如果有`cookies`隊列，那它會跟半連接隊列一樣，到頭來，還是會被**SYN Flood 攻擊**打滿。

實際上`cookies`並不會有一個專門的隊列保存，它是通過**通信雙方的IP地址端口、時間戳、MSS**等信息進行**實時計算**的，保存在**TCP報頭**的`seq`裡。

![tcp報頭_seq的位置](https://img-blog.csdnimg.cn/img_convert/6d280b0946a73ea6185653cbcfcc489f.png)

當服務端收到客戶端發來的第三次握手包時，會通過seq還原出**通信雙方的IP地址端口、時間戳、MSS**，驗證通過則建立連接。

#### cookies方案為什麼不直接取代半連接隊列？

目前看下來`syn cookies`方案省下了半連接隊列所需要的隊列內存，還能解決 **SYN Flood攻擊**，那為什麼不直接取代半連接隊列？

凡事皆有利弊，`cookies`方案雖然能防 **SYN Flood攻擊**，但是也有一些問題。因為服務端並不會保存連接信息，所以如果傳輸過程中數據包丟了，也不會重發第二次握手的信息。

另外，編碼解碼`cookies`，都是比較**耗CPU**的，利用這一點，如果此時攻擊者構造大量的**第三次握手包（ACK包）**，同時帶上各種瞎編的`cookies`信息，服務端收到`ACK包`後**以為是正經cookies**，憨憨地跑去解碼（**耗CPU**），最後發現不是正經數據包後才丟棄。

這種通過構造大量`ACK包`去消耗服務端資源的攻擊，叫**ACK攻擊**，受到攻擊的服務器可能會因為**CPU資源耗盡**導致沒能響應正經請求。

![ack攻擊](https://img-blog.csdnimg.cn/img_convert/15a0a5f7fe15ee2bc5e07492eda5a8ea.gif)

### 沒有listen，為什麼還能建立連接

那既然沒有`accept`方法能建立連接，那是不是沒有`listen`方法，也能建立連接？是的，之前寫的一篇文章提到過客戶端是可以自己連自己的形成連接（**TCP自連接**），也可以兩個客戶端同時向對方發出請求建立連接（**TCP同時打開**），這兩個情況都有個共同點，就是**沒有服務端參與，也就是沒有listen，就能建立連接。**

當時文章最後也留了個疑問，**沒有listen，為什麼還能建立連接？**

我們知道執行`listen`方法時，會創建半連接隊列和全連接隊列。

三次握手的過程中會在這兩個隊列中暫存連接信息。

所以形成連接，前提是你得**有個地方存放著**，方便握手的時候能根據IP端口等信息找到socket信息。

**那麼客戶端會有半連接隊列嗎？**

**顯然沒有**，因為客戶端沒有執行`listen`，因為半連接隊列和全連接隊列都是在執行`listen`方法時，內核自動創建的。

但內核還有個**全局hash表**，可以用於存放`sock`連接的信息。這個全局`hash`表其實還細分為`ehash，bhash和listen_hash`等，但因為過於細節，大家理解成有一個**全局hash**就夠了，

在TCP自連接的情況中，客戶端在`connect`方法時，最後會將自己的連接信息放入到這個**全局hash表**中，然後將信息發出，消息在經過迴環地址重新回到TCP傳輸層的時候，就會根據IP端口信息，再一次從這個**全局hash**中取出信息。於是握手包一來一回，最後成功建立連接。

TCP 同時打開的情況也類似，只不過從一個客戶端變成了兩個客戶端而已。

## 總結

- **每一個**`socket`執行`listen`時，內核都會自動創建一個半連接隊列和全連接隊列。
- 第三次握手前，TCP連接會放在半連接隊列中，直到第三次握手到來，才會被放到全連接隊列中。
- `accept方法`只是為了從全連接隊列中拿出一條連接，本身跟三次握手幾乎**毫無關係**。
- 出於效率考慮，雖然都叫隊列，但半連接隊列其實被設計成了**哈希表**，而全連接隊列本質是鏈表。
- 全連接隊列滿了，再來第三次握手也會丟棄，此時如果`tcp_abort_on_overflow=1`，還會直接發`RST`給客戶端。
- 半連接隊列滿了，可能是因為受到了`SYN Flood`攻擊，可以設置`tcp_syncookies`，繞開半連接隊列。
- 客戶端沒有半連接隊列和全連接隊列，但有一個**全局hash**，可以通過它實現自連接或TCP同時打開。

---

最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。

![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)