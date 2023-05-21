# 實現生產者/消費者模型——std::condition_variable

本節中，我們將使用多線程實現一個經典的生產者/消費者模型。其過程就是一個生產者線程將商品放到隊列中，然後另一個消費者線程對這個商品進行消費。如果不需要生產，生產者線程休眠。如果隊列中沒有商品能夠消費，消費者休眠。

這裡兩個線程都需要對同一個隊列進行修改，所以我們需要一個互斥量來保護這個隊列。

需要考慮的事情是：如果隊列中沒有商品了，那麼消費者做什麼呢？需要每秒對隊列進行檢查，直到看到新的商品嗎？當然，我們可以通過生產者觸發一些事件叫醒消費者，這樣消費者就能在第一時間獲取到新的商品。

C++11中提供了一個很不錯的數據結構` std::condition_variable`，其很適合處理這樣的情況。本節中，我們實現一個簡單的生產者/消費者應用，來對這個數據結構進行使用。

## How to do it...

我們將實現一個單生產者/消費者程序，每個角色都有自己的線程：

1. 包含必要的頭文件，並且聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <queue>
   #include <tuple>
   #include <condition_variable>
   #include <thread>
   
   using namespace std;
   using namespace chrono_literals;
   ```

2. 隊列進行實例化，並且隊列`q`裡只放簡單的數字。生產者將商品放入隊列中，消費者將商品從隊列中取出。為了進行同步，我們需要一個互斥量。這就需要我們對`condition_variable`進行實例化，其變量名為`cv`。`finished`變量將會告訴生產者，無需在繼續生產：

   ```c++
   queue<size_t> q;
   mutex mut;
   condition_variable cv;
   bool finished {false};
   ```

3. 首先，我們來實現一個生產者函數。其能接受一個參數`items`，其會限制生產者生產的最大數量。一個簡單的循環中，我們將會隔100毫秒生產一個商品，這個耗時就是在模擬生產的複雜性。然後，我們會對隊列的互斥量進行上鎖，並同步的對隊列進行訪問。成功的生產後，將商品加入隊列時，我們需要調用`cv.notify_all()`，函數會叫醒所有消費線程。我們將在後面看到消費者那邊是如何工作的：

   ```c++
   static void producer(size_t items) {
       for (size_t i {0}; i < items; ++i) {
           this_thread::sleep_for(100ms);
           {
               lock_guard<mutex> lk {mut};
               q.push(i);
           }
           cv.notify_all();
       }
   ```

4. 生產完所有商品後，我們會將互斥量再度上鎖，因為需要對`finished`位進行設置。然後，再次調用`cv.notify_all()`：

   ```c++
       {
           lock_guard<mutex> lk {mut};
           finished = true;
       }
       cv.notify_all();
   }
   ```

5.  現在來實現消費者函數。因為只是對隊列上的數值進行消費，直到消費完所有的數值，所以這個函數不需要參數。當`finished`未被設置時，循環會持續執行，並且會對保護隊列的互斥量進行上鎖，將對隊列和`finished`標識同時進行保護。當互斥量上鎖，則鎖就會調用`cv.wait`，並以Lambda表達式為參數。這個Lambda表達式其實就是個條件謂詞，如果生產者線程還在繼續工作，並且還有商品在隊列上，消費者線程就不能停下來：

   ```c++
   static void consumer() {
       while (!finished) {
           unique_lock<mutex> l {mut};
           
           cv.wait(l, [] { return !q.empty() || finished; });
   ```

6. `  cv.wait`的調用會對鎖進行解鎖，並且會等到給予的條件達成時才會繼續運行。然後，其會再次對互斥量上鎖，並對隊列上的商品進行消費，直到隊列為空。如果生成者還在繼續生成，那麼這個循環可能會一直進行下去。否則，當`finished`被設置時，循環將會終止，這也就表示生產者不會再進行生產：

   ```c++
           while (!q.empty()) {
               cout << "Got " << q.front()
               	<< " from queue.\n";
               q.pop();
           }
       }
   }
   ```

7. 主函數中，我們讓生產者生產10個商品。然後，我們就等待程序的結束：

   ```c++
   int main() {
       thread t1 {producer, 10};
       thread t2 {consumer};
       t1.join();
       t2.join();
       cout << "finished!\n";
   }
   ```

8. 編譯並運行程序，我們將會得到下面的輸出。當程序在運行階段時，我們將看到每一行，差不多隔100毫秒打印出來，因為生產者需要時間進行生產：

   ```c++
   $ ./producer_consumer
   Got 0 from queue.
   Got 1 from queue.
   Got 2 from queue.
   Got 3 from queue.
   Got 4 from queue.
   Got 5 from queue.
   Got 6 from queue.
   Got 7 from queue.
   Got 8 from queue.
   Got 9 from queue.
   finished!
   ```

## How it works...

本節中，我們只啟動了兩個線程。第一個線程會生產一些商品，並放到隊列中。另一個則是從隊列中取走商品。當其中一個線程需要對隊列進行訪問時，其否需要對公共互斥量`mut`進行上鎖，這樣才能對隊列進行訪問。這樣，我們就能保證兩個線程不能再同時對隊列進行操作。

除了隊列和互斥量，我們還聲明瞭2個變量，其也會對生產者和消費者有所影響：

```c++
queue<size_t> q;
mutex mut;
condition_variable cv;
bool finished {false};
```

`finished`變量很容易解釋。當其設置為true時，生產者則會對固定數量的產品進行生產。當消費者看到這個值為true的時候，其就要將隊列中的商品全部消費完。但是` condition_variable cv`代表了什麼呢？我們在兩個不同上下文中使用`cv`。其中一個上下文則會去等待一個特定的條件，並且另一個會達成對應的條件。

消費者這邊將會等待一個特殊的條件。消費者線程會在對互斥量`mut`使用`unique_lock`上鎖後，進行阻塞循環。然後，會調用`cv.wait`：

```c++
while (!finished) {
    unique_lock<mutex> l {mut};
    
    cv.wait(l, [] { return !q.empty() || finished; });
    
    while (!q.empty()) {
    	// consume
    }
}
```

我們寫了下面一段代碼，這上下來兩段代碼看起來是等價的。我們會在後面瞭解到，這兩段代碼真正的區別到底在哪裡：

```c++
while (!finished) {
    unique_lock<mutex> l {mut};
    
    while (q.empty() && !finished) {
        l.unlock();
        l.lock();
    }
   
    while (!q.empty()) {
    	// consume
    }
}
```

這就意味著，我們先要進行上鎖，然後對我們的應對方案進行檢查：

1. 還有商品能夠消費嗎？有的話，繼續持有鎖，消費，釋放鎖，結束。
2. 如果沒有商品可以消費，但是生產者依舊存在，釋放互斥鎖，也就是給生產者一個機會向隊列中添加商品。然後，嘗試再對現狀進行檢查，如果現狀有變，則跳轉到1方案中。

`cv.wait`為什麼與`while(q.empty() && ... )`不等價呢？因為在`wait`不需要再循環中持續的進行上鎖和解鎖的循環。如果生產者線程處於未激活狀態時，這就會導致互斥量持續的被上鎖和解鎖，這樣的操作是沒有意義的，而且還會耗費掉不必要的CPU週期。

` cv.wait(lock, predicate)`將會等到` predicate()`返回true時，結束等待。不過其不會對`lock`持續的進行解鎖與上鎖的操作。為了將使用`wait`阻塞的線程喚醒，我們就需要使用`condition_variable` 對象，另一個線程會對同一個對象調用`notify_one()`或`notify_all()`。等待中的線程將從休眠中醒來，並檢查`predicate()`條件是否成立。

`wait`還有一個很好的地方在於，如果出現了偽喚醒操作，那麼線程則會再次進行休眠狀態。這也就是當我們發出了過多的叫醒信號時，其不會對程序流有任何影響(但是會影響到性能)。

生產者端，在向隊列輸出商品後，調用` cv.notify_all()`，並且在生產最後一個商品時，將`finished`設置為true，這就等於引導了消費者進行消費。