# 實現多生產者/多消費者模型——std::condition_variable

讓我們再來回顧一下生產者/消費者問題，這要比上一節的問題更加複雜。我們創建了多個生成這和多個消費者。並且，我們定義的隊列沒有限制上限。

當隊列中沒有商品時，消費者會處於等待狀態，而當隊列中沒有空間可以盛放商品時，生產者也會處於等待狀態。

我們將會使用多個`std::condition_variable`對象來解決這個問題，不過使用的方式與上節有些不同。

## How to do it...

本節中，我們將實現一個類似於上節的程序，這次我們有多個生產者和消費者：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <sstream>
   #include <vector>
   #include <queue>
   #include <thread>
   #include <mutex>
   #include <condition_variable>
   #include <chrono>
   
   using namespace std;
   using namespace chrono_literals;
   ```

2. 接下來從本章的其他小節中拿過來一個同步打印的輔助類型，因為其能幫助我們在大量併發時進行打印：

   ```c++
   struct pcout : public stringstream {
       static inline mutex cout_mutex;
       ~pcout() {
           lock_guard<mutex> l {cout_mutex};
           cout << rdbuf();
       }
   };
   ```

3. 所有生產者都會將值寫入到同一個隊列中，並且所有消費者也會從這個隊列中獲取值。對於這個隊列，我們需要使用一個互斥量對隊列進行保護，並設置一個標識，其會告訴我們生產者是否已經停止生產：

   ```c++
   queue<size_t> q;
   mutex q_mutex;
   bool production_stopped {false};
   ```

4. 我們將在程序中使用兩個`condition_variable`對象。單生產者/消費者的情況下，只需要一個`condition_variable`告訴我們隊列上面擺放了新商品。本節的例子中，我們將來處理更加複雜的情況。我們需要生產者持續生產，以保證隊列上一直有可消費的商品存在。如果商品囤積到一定程度，則生產者休息。` go_consume`變量就用來提醒消費者消費的，而`go_produce`則是用來提醒生產者進行生產的：

   ```c++
   condition_variable go_produce;
   condition_variable go_consume;
   ```

5. 生產者函數能夠接受一個生產者ID，所要生產的商品數量，以及囤積商品值的上限。然後，生產者就會進入循環生產階段。這裡，首先其會對隊列的互斥量進行上鎖，然後在通過調用` go_produce.wait`對互斥量進行解鎖。隊列上的商品數量未達到囤積閾值時，滿足等待條件：

   ```c++
   static void producer(size_t id, size_t items, size_t stock)
   {
       for (size_t i = 0; i < items; ++i) {
           unique_lock<mutex> lock(q_mutex);
           go_produce.wait(lock,
           	[&] { return q.size() < stock; });
   ```

6. 生產者開始生產後，就會有商品放入隊列中。隊列商品的表達式為`id * 100 + i`。因為百位和線程id強相關，這樣我們就能瞭解到哪些商品是哪些生產者生產的。我們也能將生產事件打印到終端上。格式看起來可能有些奇怪，不過其會與消費者打印輸出對齊：

   ```c++
           q.push(id * 100 + i);
           
   		pcout{} << " Producer " << id << " --> item "
           		<< setw(3) << q.back() << '\n';
   ```

7. 生產商品之後，我們叫醒沉睡中的消費者。每個睡眠週期為90毫秒，這用來模擬生產者生產商品的時間：

   ```c++
           go_consume.notify_all();
           this_thread::sleep_for(90ms);
       }
   
       pcout{} << "EXIT: Producer " << id << '\n';
   }
   ```

8. 現在來實現消費者函數，其只接受一個消費者ID作為參數。當生產者停止生產，或是隊列上沒有商品，消費者就會繼續等待。隊列上沒有商品時，生產者還在生產的話，那麼可以肯定的是，隊列上肯定會有新商品的產生：

   ```c++
   static void consumer(size_t id)
   {
       while (!production_stopped || !q.empty()) {
       	unique_lock<mutex> lock(q_mutex);
   ```

9. 對隊列的互斥量上鎖之後，我們將會在等待`go_consume`事件變量時對互斥量進行解鎖。Lambda表達式表明，當隊列中有商品的時候我們就會對其進行獲取。第二個參數`1s`說明，我們並不想等太久。如果等待時間超過1秒，我們將不會等待。當謂詞條件達成，則`wait_for`函數返回；否則就會因為超時而放棄等待。如果隊列中有新商品，我們將會獲取這個商品，並進行相應的打印：

   ```c++
   		if (go_consume.wait_for(lock, 1s,
   				[] { return !q.empty(); })) {
   			pcout{} << " item "
   					<< setw(3) << q.front()
   					<< " --> Consumer "
   					<< id << '\n';
   			q.pop();
   ```

10. 商品被消費之後，我們將會提醒生產者，並進入130毫秒的休眠狀態，這個時間用來模擬消費時間：

    ```c++
                go_produce.notify_all();
                this_thread::sleep_for(130ms);
            }
        }
    
        pcout{} << "EXIT: Producer " << id << '\n';
    }
    ```

11. 主函數中，我們對工作線程和消費線程各自創建一個`vector`:

    ```c++
    int main()
    {
        vector<thread> workers;
        vector<thread> consumers;
    ```

12. 然後，我們創建3個生產者和5個消費者：

    ```c++
        for (size_t i = 0; i < 3; ++i) {
        	workers.emplace_back(producer, i, 15, 5);
        }
    
        for (size_t i = 0; i < 5; ++i) {
        	consumers.emplace_back(consumer, i);
        }
    ```

13. 我們會先讓生產者線程終止。然後返回，並對`production_stopped`標識進行設置，這將會讓消費者線程同時停止。然後，我們要將這些線程進行回收，然後退出程序：

    ```c++
        for (auto &t : workers) { t.join(); }
        production_stopped = true;
        for (auto &t : consumers) { t.join(); }
    }
    ```

14. 編譯並運行程序，我們將獲得如下的輸出。輸出特別長，我們進行了截斷。我們能看到生產者偶爾會休息一下，並且消費者會消費掉對應的商品，直到再次生產。若是將生產者/消費者的休眠時間進行修改，則會得到完全不一樣的結果：

    ```c++
    $ ./multi_producer_consumer
    Producer 0 --> item 0
    Producer 1 --> item 100
    item 0 --> Consumer 0
    Producer 2 --> item 200
    item 100 --> Consumer 1
    item 200 --> Consumer 2
    Producer 0 --> item 1
    Producer 1 --> item 101
    item 1 --> Consumer 0
    ...
    Producer 0 --> item14
    EXIT: Producer 0
    Producer 1 --> item 114
    EXIT: Producer 1
    item14 --> Consumer 0
    Producer 2 --> item 214
    EXIT: Producer 2
    item 114 --> Consumer 1
    item 214 --> Consumer 2
    EXIT: Consumer 2
    EXIT: Consumer 3
    EXIT: Consumer 4
    EXIT: Consumer 0
    EXIT: Consumer 1
    ```

## How it works...

這節可以作為之前章節的擴展。與單生產者和消費者不同，我們實現了M個生產者和N個消費者之間的同步。因此，程序中不是消費者因為隊列中沒有商品而等待，就是因為隊列中囤積了太多商品讓生產者等待。

當有多個消費者等待同一個隊列中出現新的商品時，程序的模式就又和單生產者/消費者工作的模式相同了。當有一個線程對保護隊列的互斥量上鎖時，然後對貨物進行添加或減少，這樣代碼就是安全的。這樣的話，無論有多少線程在同時等待這個鎖，對於我們來說都無所謂。生產者也同理，其中最重要的就是，隊列不允許兩個及兩個以上的線程進行訪問。

比單生產者/消費者原理複雜的原因在於，當商品的數量在隊列中囤積到一定程度，我們將會讓生產者線程停止。為了迎合這個需求，我們使用兩個不同的`condition_variable`：

1. `go_produce`表示隊列沒有被填滿，並且生產者會繼續生產，而後將商品放置在隊列中。
2. `go_consume`表示隊列已經填滿，消費者可以繼續消費。

這樣，生產者會將隊列用貨物填滿，並且`go_consume`會用如下代碼，提醒消費者線程：

```c++
if (go_consume.wait_for(lock, 1s, [] { return !q.empty(); })) {
	// got the event without timeout
}
```

生產者也會進行等待，直到可以再次生產：

```c++
go_produce.wait(lock, [&] { return q.size() < stock; });
```

還有一個細節就是我們不會讓消費者線程等太久。在對`go_consume.wait_for`的調用中，我們添加了超時參數，並且設置為1秒。這對於消費者來說是一種退出機制：當隊列為空的狀態持續多於1秒，那麼就可能沒有生產者在工作。

這個處理起來很簡單，代碼會盡可能讓隊列中商品的數量達到閾值的上限。更復雜的程序中，當商品的數量為閾值上限的一半時，消費者線程會對生產者線程進行提醒。這樣生產者就會在隊列為空前繼續生產。

` condition_variable`幫助我們完美的解決了一個問題：當一個消費者觸發了`go_produce`的提醒，那麼將會有很多生產者競爭的去生產下一個商品。如果只需要生產一個商品，那麼只需要一個生產者就好。當`go_produce`被觸發時，所有生產者都爭相生產這一個商品，我們將會看到的情況就是商品在隊列中的數量超過了閾值的上限。

我們試想一下這種情況，我們有`(max - 1)`個商品在隊列中，並且想在要一個商品將隊列填滿。不論是一個消費者線程調用了`go_produce.notify_one()`(只叫醒一個等待線程)或` go_produce.notify_all()`(叫醒所有等待的線程)，都需要保證只有一個生產者線程調用了`go_produce.wait`，因為對於其他生成線程來說，一旦互斥鎖解鎖，那麼`q.size() < stock`(stock貨物閾值上限)的條件將不復存在。