# 5.6 一個進程最多可以創建多少個線程？

大家好，我是小林。

昨天有位讀者問了我這麼個問題：

![](https://img-blog.csdnimg.cn/20210715092002563.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)
![](https://img-blog.csdnimg.cn/20210715092015507.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


大致意思就是，他看了一個面經，說虛擬內存是 2G 大小，然後他看了我的圖解系統 PDF 裡說虛擬內存是 4G，然後他就懵逼了。

其實他看這個面經很有問題，沒有說明是什麼操作系統，以及是多少位操作系統。

因為不同的操作系統和不同位數的操作系統，虛擬內存可能是不一樣多。

Windows 系統我不瞭解，我就說說 Linux 系統。 


在 Linux 操作系統中，虛擬地址空間的內部又被分為內核空間和用戶空間兩部分，不同位數的系統，地址 空間的範圍也不同。比如最常⻅的 32 位和 64 位系統，如下所示:

![](https://img-blog.csdnimg.cn/20210715092026648.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)



通過這裡可以看出:
- 32 位系統的內核空間佔用 1G ，位於最高處，剩下的 3G 是用戶空間;
- 64 位系統的內核空間和用戶空間都是 128T ，分別佔據整個內存空間的最高和最低處，剩下的中
  間部分是未定義的。

---

接著，來看看讀者那個面經題目：**一個進程最多可以創建多少個線程？**

這個問題跟兩個東西有關係：
- **進程的虛擬內存空間上限**，因為創建一個線程，操作系統需要為其分配一個棧空間，如果線程數量越多，所需的棧空間就要越大，那麼虛擬內存就會佔用的越多。
- **系統參數限制**，雖然 Linux 並沒有內核參數來控制單個進程創建的最大線程個數，但是有系統級別的參數來控制整個系統的最大線程個數。


我們先看看，在進程裡創建一個線程需要消耗多少虛擬內存大小？

我們可以執行 ulimit -a 這條命令，查看進程創建線程時默認分配的棧空間大小，比如我這臺服務器默認分配給線程的棧空間大小為 8M。

![](https://img-blog.csdnimg.cn/20210715092041211.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)



在前面我們知道，在 32 位 Linux 系統裡，一個進程的虛擬空間是 4G，內核分走了1G，**留給用戶用的只有 3G**。

那麼假設創建一個線程需要佔用 10M 虛擬內存，總共有 3G 虛擬內存可以使用。於是我們可以算出，最多可以創建差不多 300 個（3G/10M）左右的線程。


如果你想自己做個實驗，你可以找臺 32 位的 Linux 系統運行下面這個代碼：

![](https://img-blog.csdnimg.cn/20210715092052531.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


由於我手上沒有 32 位的系統，我這裡貼一個網上別人做的測試結果：

![](https://img-blog.csdnimg.cn/202107150921005.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)




如果想使得進程創建上千個線程，那麼我們可以調整創建線程時分配的棧空間大小，比如調整為 512k：

```
$ ulimit -s 512
```

----

說完 32 位系統的情況，我們來看看 64 位系統裡，一個進程能創建多少線程呢？

我的測試服務器的配置：
- 64 位系統；
- 2G 物理內存；
- 單核 CPU。

64 位系統意味著用戶空間的虛擬內存最大值是 128T，這個數值是很大的，如果按創建一個線程需佔用 10M 棧空間的情況來算，那麼理論上可以創建 128T/10M 個線程，也就是 1000多萬個線程，有點魔幻！

所以按 64 位系統的虛擬內存大小，理論上可以創建無數個線程。

事實上，肯定創建不了那麼多線程，除了虛擬內存的限制，還有系統的限制。

比如下面這三個內核參數的大小，都會影響創建線程的上限：
- ***/proc/sys/kernel/threads-max***，表示系統支持的最大線程數，默認值是 `14553`；
-  ***/proc/sys/kernel/pid_max***，表示系統全局的 PID 號數值的限制，每一個進程或線程都有 ID，ID 的值超過這個數，進程或線程就會創建失敗，默認值是 `32768`；
-  ***/proc/sys/vm/max_map_count***，表示限制一個進程可以擁有的VMA(虛擬內存區域)的數量，具體什麼意思我也沒搞清楚，反正如果它的值很小，也會導致創建線程失敗，默認值是 `65530`。



那接下針對我的測試服務器的配置，看下一個進程最多能創建多少個線程呢？

我在這臺服務器跑了前面的程序，其結果如下：

![](https://img-blog.csdnimg.cn/20210715092109740.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)



可以看到，創建了 14374 個線程後，就無法在創建了，而且報錯是因為資源的限制。

前面我提到的 `threads-max` 內核參數，它是限制系統裡最大線程數，默認值是 14553。



我們可以運行那個測試線程數的程序後，看下當前系統的線程數是多少，可以通過 `top -H` 查看。

![](https://img-blog.csdnimg.cn/20210715092125376.png)


左上角的 Threads 的數量顯示是 14553，與 `threads-max` 內核參數的值相同，所以我們可以認為是因為這個參數導致無法繼續創建線程。

那麼，我們可以把 threads-max 參數設置成 `99999`:


```
echo 99999 > /proc/sys/kernel/threads-max
```

設置完 threads-max 參數後，我們重新跑測試線程數的程序，運行後結果如下圖：

![](https://img-blog.csdnimg.cn/20210715092138115.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)



可以看到，當進程創建了 32326 個線程後，就無法繼續創建裡，且報錯是無法繼續申請內存。

此時的上限個數很接近 `pid_max` 內核參數的默認值（32768），那麼我們可以嘗試將這個參數設置為 99999：


```
echo 99999 > /proc/sys/kernel/pid_max
```

設置完 pid_max 參數後，繼續跑測試線程數的程序，運行後結果創建線程的個數還是一樣卡在了 32768 了。

當時我也挺疑惑的，明明 pid_max 已經調整大後，為什麼線程個數還是上不去呢？

後面經過查閱資料發現，`max_map_count` 這個內核參數也是需要調大的，但是它的數值與最大線程數之間有什麼關係，我也不太明白，只是知道它的值是會限制創建線程個數的上限。

然後，我把 max_map_count 內核參數也設置成後 99999：

```
echo 99999 > /proc/sys/kernel/max_map_count 
```

繼續跑測試線程數的程序，結果如下圖：

![](https://img-blog.csdnimg.cn/20210715092151214.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


當創建差不多 5 萬個線程後，我的服務器就卡住不動了，CPU 都已經被佔滿了，畢竟這個是單核 CPU，所以現在是 CPU 的瓶頸了。

我只有這臺服務器，如果你們有性能更強的服務器來測試的話，有興趣的小夥伴可以去測試下。

接下來，我們換個思路測試下，把創建線程時分配的棧空間調大，比如調大為 100M，在大就會創建線程失敗。

```
ulimit -s 1024000
```

設置完後，跑測試線程的程序，其結果如下：

![](https://img-blog.csdnimg.cn/20210715092207662.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzM0ODI3Njc0,size_16,color_FFFFFF,t_70)


總共創建了 26390 個線程，然後就無法繼續創建了，而且該進程的虛擬內存空間已經高達 25T，要知道這臺服務器的物理內存才 2G。

為什麼物理內存只有 2G，進程的虛擬內存卻可以使用 25T 呢？

因為虛擬內存並不是全部都映射到物理內存的，程序是有局部性的特性，也就是某一個時間只會執行部分代碼，所以只需要映射這部分程序就好。

你可以從上面那個 top 的截圖看到，雖然進程虛擬空間很大，但是物理內存（RES）只有使用了 400 多M。


好了，簡單總結下：
- 32 位系統，用戶態的虛擬空間只有 3G，如果創建線程時分配的棧空間是 10M，那麼一個進程最多隻能創建 300 個左右的線程。
- 64 位系統，用戶態的虛擬空間大到有 128T，理論上不會受虛擬內存大小的限制，而會受系統的參數或性能限制。

