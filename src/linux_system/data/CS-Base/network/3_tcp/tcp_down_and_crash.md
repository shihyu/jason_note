# 4.12 TCP 連接，一端斷電和進程崩潰有什麼區別？

有位讀者找我說，他在面試騰訊的時候，遇到了這麼個問題：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/2021061513401120.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)



這個屬於 **TCP 異常斷開連接**的場景，這部分內容在我的「圖解網絡」還沒有詳細介紹過，這次就乘著這次機會補一補。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/20210615134020994.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)

這個問題有幾個關鍵詞：

- 沒有開啟 keepalive；
- 一直沒有數據交互；
- 進程崩潰；
- 主機崩潰；


我們先來認識認識什麼是 TCP keepalive 呢？

這東西其實就是 **TCP 的保活機制**，它的工作原理我之前的文章寫過，這裡就直接貼下以前的內容。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/20210615134028909.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)



如果兩端的 TCP 連接一直沒有數據交互，達到了觸發 TCP 保活機制的條件，那麼內核裡的 TCP 協議棧就會發送探測報文。
- 如果對端程序是正常工作的。當 TCP 保活的探測報文發送給對端, 對端會正常響應，這樣 **TCP 保活時間會被重置**，等待下一個 TCP 保活時間的到來。
- 如果對端主機崩潰，或對端由於其他原因導致報文不可達。當 TCP 保活的探測報文發送給對端後，石沉大海，沒有響應，連續幾次，達到保活探測次數後，**TCP 會報告該 TCP 連接已經死亡**。


所以，TCP 保活機制可以在雙方沒有數據交互的情況，通過探測報文，來確定對方的 TCP 連接是否存活。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/20210615134036676.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)

注意，應用程序若想使用 TCP 保活機制需要通過 socket 接口設置 `SO_KEEPALIVE` 選項才能夠生效，如果沒有設置，那麼就無法使用 TCP 保活機制。

## 主機崩潰

知道了 TCP keepalive 作用，我們再回過頭看題目中的「主機崩潰」這種情況。

> 在沒有開啟 TCP keepalive，且雙方一直沒有數據交互的情況下，如果客戶端的「主機崩潰」了，會發生什麼。


客戶端主機崩潰了，服務端是**無法感知到的**，在加上服務端沒有開啟 TCP keepalive，又沒有數據交互的情況下，**服務端的 TCP 連接將會一直處於 ESTABLISHED 連接狀態**，直到服務端重啟進程。

所以，我們可以得知一個點，在沒有使用 TCP 保活機制且雙方不傳輸數據的情況下，一方的 TCP 連接處在 ESTABLISHED 狀態，並不代表另一方的連接還一定正常。

## 進程崩潰


> 那題目中的「進程崩潰」的情況呢？

TCP 的連接信息是由內核維護的，所以當服務端的進程崩潰後，內核需要回收該進程的所有 TCP 連接資源，於是內核會發送第一次揮手 FIN 報文，後續的揮手過程也都是在內核完成，並不需要進程的參與，所以即使服務端的進程退出了，還是能與客戶端完成 TCP四次揮手的過程。

我自己做了實驗，使用 kill -9 來模擬進程崩潰的情況，發現**在 kill 掉進程後，服務端會發送 FIN 報文，與客戶端進行四次揮手**。


所以，即使沒有開啟 TCP keepalive，且雙方也沒有數據交互的情況下，如果其中一方的進程發生了崩潰，這個過程操作系統是可以感知的到的，於是就會發送 FIN 報文給對方，然後與對方進行 TCP 四次揮手。

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/2021061513405211.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


---

## 有數據傳輸的場景

以上就是對這個面試題的回答，接下來我們看看在「**有數據傳輸**」的場景下的一些異常情況：

- 第一種，客戶端主機宕機，又迅速重啟，會發生什麼？
- 第二種，客戶端主機宕機，一直沒有重啟，會發生什麼？

### 客戶端主機宕機，又迅速重啟

在客戶端主機宕機後，服務端向客戶端發送的報文會得不到任何的響應，在一定時長後，服務端就會觸發**超時重傳**機制，重傳未得到響應的報文。

服務端重傳報文的過程中，客戶端主機重啟完成後，客戶端的內核就會接收重傳的報文，然後根據報文的信息傳遞給對應的進程：
- 如果客戶端主機上**沒有**進程綁定該 TCP 報文的目標端口號，那麼客戶端內核就會**回覆 RST 報文，重置該 TCP 連接**；
- 如果客戶端主機上**有**進程綁定該 TCP 報文的目標端口號，由於客戶端主機重啟後，之前的 TCP 連接的數據結構已經丟失了，客戶端內核裡協議棧會發現找不到該 TCP 連接的 socket 結構體，於是就會**回覆 RST 報文，重置該 TCP 連接**。

所以，**只要有一方重啟完成後，收到之前 TCP 連接的報文，都會回覆 RST 報文，以斷開連接**。


### 客戶端主機宕機，一直沒有重啟

這種情況，服務端超時重傳報文的次數達到一定閾值後，內核就會判定出該 TCP 有問題，然後通過 Socket 接口告訴應用程序該 TCP 連接出問題了，於是服務端的 TCP 連接就會斷開。

![](https://img-blog.csdnimg.cn/20210615134110763.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)

> 那 TCP 的數據報文具體重傳幾次呢？

在 Linux 系統中，提供一個叫 tcp_retries2 配置項，默認值是 15，如下圖：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/20210615134059647.png)


這個內核參數是控制，在 TCP 連接建立的情況下，超時重傳的最大次數。

不過 tcp_retries2 設置了 15 次，並不代表 TCP 超時重傳了 15 次才會通知應用程序終止該 TCP 連接，**內核會根據 tcp_retries2 設置的值，計算出一個 timeout**（*如果 tcp_retries2 =15，那麼計算得到的 timeout = 924600 ms*），**如果重傳間隔超過這個 timeout，則認為超過了閾值，就會停止重傳，然後就會斷開 TCP 連接**。

在發生超時重傳的過程中，每一輪的超時時間（RTO）都是**倍數增長**的，比如如果第一輪 RTO 是 200 毫秒，那麼第二輪 RTO 是 400 毫秒，第三輪 RTO 是 800 毫秒，以此類推。

而 RTO 是基於 RTT（一個包的往返時間） 來計算的，如果 RTT 較大，那麼計算出來的 RTO 就越大，那麼經過幾輪重傳後，很快就達到了上面的 timeout 值了。

舉個例子，如果 tcp_retries2 =15，那麼計算得到的 timeout = 924600 ms，如果重傳總間隔時長達到了 timeout 就會停止重傳，然後就會斷開 TCP 連接：

- 如果 RTT 比較小，那麼 RTO 初始值就約等於下限 200ms，也就是第一輪的超時時間是 200 毫秒，由於 timeout 總時長是 924600 ms，表現出來的現象剛好就是重傳了 15 次，超過了 timeout 值，從而斷開 TCP 連接
- 如果 RTT 比較大，假設 RTO 初始值計算得到的是 1000 ms，也就是第一輪的超時時間是 1 秒，那麼根本不需要重傳 15 次，重傳總間隔就會超過 924600 ms。

最小 RTO 和最大 RTO 是在 Linux 內核中定義好了：

```c
#define TCP_RTO_MAX ((unsigned)(120*HZ))
#define TCP_RTO_MIN ((unsigned)(HZ/5))
```

Linux 2.6+ 使用 1000 毫秒的 HZ，因此`TCP_RTO_MIN`約為 200 毫秒，`TCP_RTO_MAX`約為 120 秒。

如果`tcp_retries`設置為`15`，且  RTT 比較小，那麼 RTO 初始值就約等於下限 200ms，這意味著**它需要 924.6 秒**才能將斷開的 TCP 連接通知給上層（即應用程序），每一輪的 RTO 增長關係如下表格：

![在這裡插入圖片描述](https://img-blog.csdnimg.cn/2021061513410645.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


---

## 總結

如果「**客戶端進程崩潰**」，客戶端的進程在發生崩潰的時候，內核會發送 FIN 報文，與服務端進行四次揮手。

但是，「**客戶端主機宕機**」，那麼是不會發生四次揮手的，具體後續會發生什麼？還要看服務端會不會發送數據？

- 如果服務端會發送數據，由於客戶端已經不存在，收不到數據報文的響應報文，服務端的數據報文會超時重傳，當重傳總間隔時長達到一定閾值（內核會根據 tcp_retries2 設置的值計算出一個閾值）後，會斷開 TCP 連接；
- 如果服務端一直不會發送數據，再看服務端有沒有開啟 TCP keepalive 機制？
  - 如果有開啟，服務端在一段時間沒有進行數據交互時，會觸發 TCP keepalive 機制，探測對方是否存在，如果探測到對方已經消亡，則會斷開自身的 TCP 連接；
  - 如果沒有開啟，服務端的 TCP 連接會一直存在，並且一直保持在 ESTABLISHED 狀態。

最後說句，TCP 牛逼，啥異常都考慮到了。

**小林是專為大家圖解的工具人，Goodbye，我們下次見！**

![](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost2/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)