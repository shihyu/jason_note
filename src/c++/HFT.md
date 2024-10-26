# C++ 為核心語言的高頻交易系統是如何做到低延遲？

出處：https://kknews.cc/tech/bozorm9.amp

問題中限定語言是C++，可討論的範圍就比較精簡了。現有的答案都在談系統架構層次上的東西，略顯跑題。我對C++瞭解不多，但我嘗試以一名C++程式設計師的視角，從基本思路出發做一個分析，拋磚引玉。

首先我們要明確係統的需求。所謂交易系統，從一個應用程式的角度來說，有以下幾個特點：

1. 一定是一個網絡相關的應用，假如機器沒聯網，肯定什麼交易也幹不了。所以系統需要通過TCP/IP連接來收發數據。數據要分兩種，一種從交易所發過來的市場數據，流量很大，另一種是系統向交易所發出的交易指令，相比前者流量很小，這兩種數據需要在不同的TCP/IP連接裡傳輸。
2. 因為是自動化交易系統，人工幹預的部分肯定比較小，所以圖形界面不是重點。而為了性能考慮，圖形界面需要和後臺分開部署在不同的機器上，通過網絡交互，以免任何圖形界面上的問題導致後臺系統故障或者被搶佔資源。這樣又要在後臺增加新的TCP/IP連接。
3. 高頻交易系統對延遲異常敏感，目前（2014）市面上的主流系統（可以直接買到的大眾系統）延遲至少在100微秒級別，頂尖的系統（HFT專有）可以做到10微秒以下。其他答案裡提到C++隨便寫寫延遲做到幾百微秒，是肯定不行的，這樣的性能對於高頻交易來說會是一場災難。
4. 系統只需要專注於處理自己收到的數據，不需要和其他機器合作，不需要擔心流量過載。

有了以上幾點基本的認識，我們可以看看用C++做為開發語言有哪些需要注意的。

首先前兩點需求就決定了，這種系統一定是一個多線程程序。雖然對於圖形界面來說，後臺系統相當於一個服務端，但這部分的性能不是重點，用常用的模式就能解決。而重要的面向交易所那端，系統其實是一個客戶端程序，只需要維護好固定數量的連接就可以了。為延遲考慮，`一定要選擇異步I/O（阻塞的同步I/O會消耗時間在上下文切換）`，這裡有兩點需要注意：

- 是否可以在單線程內完成所有處理？考慮市場數據的流量遠遠高於發出的交易指令，在單線程內處理顯然是不行的，否則可能收了一大堆數據還沒開始處理，錯過了發指令的最佳時機。
- 有答案提到要壓低平時的資源使用率，這是完全錯誤的設計思路。問題同樣出在上下文切換上，一旦系統進入IDLE狀態，再重新切換回處理模式是要付出時間代價的。正確的做法是保持對異步socket的瘋狂輪詢，一旦有消息就立刻處理，之後繼續輪詢，這樣是最快的處理方式。（順帶一提現在的CPU一般會帶有環保功能，使用率低了會導致CPU進入低功耗模式，同樣對性能有嚴重影響。真正的低延遲系統一定是永遠發燙的！）

現在我們知道核心的模塊是一個多線程的，處理多個TCP/IP連接的模塊，接下來就可以針對C++進行討論。因為需要對接受到的每個TCP或UDP包進行處理，首先要考慮的是如何把包從接收線程傳遞給處理線程。我們知道C++是面向對象的語言，一般情況下最直觀的思路是創建一個對象，然後發給處理線程，這樣從邏輯上看是非常清晰的。但在追求低延遲的系統裡不能這樣做，因為對象是分配在堆上的，而堆的內存結構對我們來說是完全不透明的，沒辦法控制一個對象會具體分到內存的什麼位置上，這直接導致的問題是本來連續收到的網絡包，在內存裡的分佈是分散的，當處理線程需要讀取數據時就會發生大量的cache miss，產生不可控的延遲。所以對C++開發者來說，第一條需要謹記的應該是，不要隨便使用堆（用關鍵字new）。核心的數據要保證分配在連續內存裡。

另一個問題在於，市場數據和交易指令都是結構化的，包含了股票名稱，價格，時間等一系列信息。如果使用C++ class來對數據進行建模和封裝，同樣會產生不可知的內存結構。為了嚴格控制內存結構，應該使用struct來封裝。一方面在對接收到的數據解析時可以直接定義名稱，一方面在分配新對象（比如交易指令）時可以保證所有數據都分配在連續的內存區域。

以上兩點是關於延遲方面最重要的注意事項。除此之外，需要考慮的是業務邏輯的編寫。高頻交易系統裡註定了業務邏輯不會太複雜，但重要的是要保證正確性和避免指針錯誤。正確性應該可以藉助於C++的特性比如強類型，模板等來加強驗證，這方面我不熟悉就不多說了。高頻系統往往運行時要處理大量訂單，所以一定要保證系統運行時不能崩潰，一旦coredump後果很嚴重。這個問題也許可以多做編譯期靜態分析來加強，或者需要在系統外增加安全機制，這裡不展開討論了。

以下是幾點引申思考：

- 如何存儲系統日誌？
- 如何對系統進行實時監控？
- 如果系統coredump，事後如何分析找出問題所在？
- 如何設計保證系統可用性，使得出現coredump之類的情況時可以及時切換到備用系統？

這些問題相信在C++框架內都有合適的解決方案，我對此瞭解不多，所以只列在這裡供大家討論。

---

限制 CPU 核心和減少上下文切換（context switch）雖然相關，但它們是兩個不同的概念，目的是為了優化性能。

1. 限制 CPU 核心（CPU Affinity）
CPU 親和性（CPU Affinity） 是指將特定的線程或進程綁定到特定的 CPU 核心上運行。這樣做的好處包括：

減少延遲：透過將線程固定在特定核心上，系統能夠避免因為進程在核心之間切換而帶來的額外延遲。
資源利用：能夠更有效地利用 CPU 的快取（cache），因為當一個線程多次在同一核心上運行時，該核心的快取能夠保持相關數據，減少記憶體訪問的時間。
2. 減少上下文切換（Context Switch）
上下文切換 是指操作系統在不同的線程或進程之間切換的過程。這一過程涉及保存當前進程的狀態（上下文）並載入下一個進程的狀態。減少上下文切換的好處包括：

提高效率：每次上下文切換都需要時間和資源，因此減少上下文切換能夠提高 CPU 的有效利用率。
增強響應性：在高頻交易等時間敏感的應用中，減少上下文切換能夠確保系統在需要時迅速響應。
如何關聯
關聯性：限制 CPU 核心能夠幫助減少上下文切換的發生。例如，當一個線程被固定在特定的核心上運行時，操作系統就不需要頻繁地在不同核心之間切換這個線程，從而減少了上下文切換的次數。

獨立的考量：雖然這兩者可以互相促進性能，但仍然是獨立的優化策略。你可以選擇使用 CPU 親和性來優化某些關鍵任務的性能，同時也需要考慮整個系統的設計來減少上下文切換的發生。

總結
限制 CPU 核心是通過將線程綁定到特定核心來減少延遲和提高資源利用率。
減少上下文切換是通過降低線程或進程之間的切換次數來提高系統效率。
這兩者都在高頻交易等要求高性能的應用中發揮重要作用，但它們的實施策略和影響是不同的。如果你對這方面還有其他疑問，隨時告訴我！



在 C++ 中，如果你想要指定一個程式或一個線程在特定的 CPU 核心上運行，可以使用 POSIX threads（pthread）或 C++11 中的 <thread> 库，結合系統調度工具（例如 sched_setaffinity）來實現。以下是使用這兩種方式的範例：

```cpp
#include <iostream>
#include <pthread.h>
#include <sched.h>
#include <unistd.h>

void* threadFunction(void* arg) {
    // 這裡是線程要執行的代碼
    std::cout << "Thread running on CPU core: " << sched_getcpu() << std::endl;
    return nullptr;
}

int main() {
    pthread_t thread;
    

    // 創建一個新線程
    pthread_create(&thread, nullptr, threadFunction, nullptr);
    
    // 設定線程在第一個核心運行
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset); // 指定使用 CPU 0
    
    pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
    
    // 等待線程結束
    pthread_join(thread, nullptr);
    
    return 0;

}
```



```cpp
#include <iostream>
#include <thread>
#include <pthread.h>
#include <sched.h>
#include <unistd.h>

void threadFunction() {
    std::cout << "Thread running on CPU core: " << sched_getcpu() << std::endl;
}

int main() {
    std::thread myThread(threadFunction);
    

    // 設定線程在第一個核心運行
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset); // 指定使用 CPU 0
    
    // 獲取 pthread 的線程 ID
    pthread_t nativeThread = myThread.native_handle();
    
    pthread_setaffinity_np(nativeThread, sizeof(cpu_set_t), &cpuset);
    
    // 等待線程結束
    myThread.join();
    
    return 0;

}
```



減少上下文切換（context switch）是提升系統性能的一個重要手段，尤其在高頻交易等需要低延遲的應用中。以下是一些有效的策略來減少上下文切換：

1. 優化線程數量
合適的線程數量：確保線程數量與可用的 CPU 核心數量相匹配。過多的線程會導致頻繁的上下文切換，因為操作系統需要在更多的線程之間進行切換。

使用線程池：實現線程池來重用線程，減少線程創建和銷毀的開銷。

2. 使用 CPU 親和性
CPU Affinity：將特定的線程綁定到特定的 CPU 核心上運行。這樣可以減少因線程在不同核心間切換而造成的上下文切換，並提高 CPU 快取的命中率。
3. 降低 I/O 操作頻率
批量處理 I/O 操作：盡量將 I/O 操作合併處理，而不是頻繁地進行小的 I/O 操作。這樣可以減少因 I/O 等待而導致的上下文切換。

異步 I/O：使用異步 I/O 操作，讓線程在等待 I/O 完成時能夠執行其他任務，減少阻塞情況。

4. 減少鎖的使用
無鎖編程：盡量使用無鎖資料結構，這樣可以減少因鎖而導致的上下文切換。

使用輕量級鎖：如果必須使用鎖，考慮使用輕量級鎖（如自旋鎖），這樣可以減少鎖的持有時間和上下文切換的開銷。

5. 合理設計程式邏輯
合併任務：將多個小任務合併成較大的任務，以減少任務切換的頻率。

使用事件驅動架構：通過事件驅動的設計來減少線程的數量，這樣可以在一個線程中處理多個事件，降低上下文切換的頻率。

6. 優化系統參數
調整操作系統參數：根據應用的特性調整操作系統的參數，如調整調度策略或提高線程優先級，從而減少上下文切換。
7. 監控和分析
性能監控：使用工具（如 perf 或 top）來監控系統的上下文切換情況，識別高上下文切換的源頭並針對性優化。

性能分析：通過分析程式的執行路徑和資源使用，找出影響性能的瓶頸並進行針對性優化。

總結
減少上下文切換需要對系統架構、程式設計和資源管理進行綜合考量。透過上述策略，可以有效降低上下文切換的發生，從而提高系統的整體性能。如果你需要針對具體情況的建議，隨時告訴我！

---

在高頻交易中，由於交易策略需要極快的執行速度和低延遲，選擇適當的鎖機制非常重要。以下是一些常用的鎖定方法以及它們的適用情境：

1. **互斥鎖 (Mutex)**：
   - 最常見的鎖，用於保護共享資源，確保同一時間只有一個執行緒可以訪問該資源。
   - 在高頻交易中，通常需要盡量減少鎖的持有時間，以降低延遲。

2. **自旋鎖 (Spinlock)**：
   - 在鎖不可用的情況下，執行緒會進行忙等待（spin），而不是進入休眠狀態。
   - 適合於短時間的鎖持有，因為自旋鎖能夠避免上下文切換的開銷，但若鎖持有時間過長會造成CPU資源浪費。

3. **讀寫鎖 (Read-Write Lock)**：
   - 允許多個執行緒同時讀取，但在寫入時會獲得獨佔鎖。
   - 對於讀取操作頻繁、寫入操作相對少的情況非常有效。

4. **無鎖資料結構 (Lock-Free Data Structures)**：
   - 使用原子操作（如 CAS，Compare-And-Swap）來實現不需要鎖的資料結構。
   - 在高頻交易中，無鎖資料結構可以降低延遲，提高併發性能。

5. **事件鎖 (Event Lock)**：
   - 允許執行緒等待特定事件的發生，適合於需要等待某個條件才能繼續執行的場景。
   - 在高頻交易中，可以用於處理異步事件，如市場報價更新。

### 小結：
在高頻交易中，通常會根據具體情況選擇適當的鎖定機制，並努力減少鎖的使用和鎖持有時間，以實現更高的執行效率和更低的延遲。無鎖資料結構的使用也越來越普遍，因為它們能夠顯著降低上下文切換和鎖競爭的影響。

---



在 Linux 中，使用 C 語言實現自旋鎖 (Spinlock) 通常依賴於原子操作，特別是使用 `pthread` 庫中的自旋鎖來實現多執行緒的同步。以下是使用 C 語言和 `pthread` 實現自旋鎖的範例。

### 使用 pthread 實現的 Spinlock 範例

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_THREADS 4
#define INCREMENTS 100000

pthread_spinlock_t spinlock; // 定義自旋鎖
int counter = 0; // 需要保護的共享資源

void* increment_counter(void* arg) {
    for (int i = 0; i < INCREMENTS; ++i) {
        pthread_spin_lock(&spinlock); // 獲取自旋鎖
        counter++; // 共享資源的操作
        pthread_spin_unlock(&spinlock); // 釋放自旋鎖
    }
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];

    // 初始化自旋鎖
    if (pthread_spin_init(&spinlock, PTHREAD_PROCESS_PRIVATE) != 0) {
        perror("Failed to initialize spinlock");
        return EXIT_FAILURE;
    }

    // 創建多個執行緒
    for (int i = 0; i < NUM_THREADS; ++i) {
        if (pthread_create(&threads[i], NULL, increment_counter, NULL) != 0) {
            perror("Failed to create thread");
            return EXIT_FAILURE;
        }
    }

    // 等待所有執行緒完成
    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    printf("Final counter value: %d\n", counter);

    // 銷毀自旋鎖
    pthread_spin_destroy(&spinlock);
    return EXIT_SUCCESS;
}
```

### 總結

1. **自旋鎖的定義**：我們使用 `pthread_spinlock_t` 來定義自旋鎖。
2. **自旋鎖的初始化**：使用 `pthread_spin_init()` 初始化自旋鎖。
3. **獲取和釋放自旋鎖**：使用 `pthread_spin_lock()` 和 `pthread_spin_unlock()` 來獲取和釋放自旋鎖，確保對共享資源的安全訪問。
4. **多執行緒創建**：使用 `pthread_create()` 創建多個執行緒，並使用 `pthread_join()` 等待它們完成。
5. **自旋鎖的銷毀**：最後，使用 `pthread_spin_destroy()` 銷毀自旋鎖。

這個範例展示了如何在 Linux 環境中使用 C 語言實現自旋鎖來保護共享資源，並在多執行緒環境中進行計數操作。



以下是 C++ 和 Python 中自旋鎖 (Spinlock) 的範例實現。自旋鎖是一種鎖，當鎖不可用時，執行緒會在一個循環中忙等待，直到鎖可用為止。

### C++ Spinlock 範例

```cpp
#include <atomic>
#include <thread>
#include <iostream>
#include <vector>

class Spinlock {
public:
    Spinlock() : flag(ATOMIC_FLAG_INIT) {}

    void lock() {
        while (flag.test_and_set(std::memory_order_acquire)) {
            // 可能可以加個小延遲，讓 CPU 不至於佔用過多資源
            std::this_thread::yield(); // 提高效率，讓其他執行緒有機會執行
        }
    }

    void unlock() {
        flag.clear(std::memory_order_release);
    }

private:
    std::atomic_flag flag;
};

// 測試自旋鎖
void test_spinlock(Spinlock &spinlock, int &counter) {
    for (int i = 0; i < 100000; ++i) {
        spinlock.lock();
        ++counter; // 需要保護的共享資源
        spinlock.unlock();
    }
}

int main() {
    Spinlock spinlock;
    int counter = 0;
    std::vector<std::thread> threads;

    // 創建多個執行緒來測試自旋鎖
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(test_spinlock, std::ref(spinlock), std::ref(counter));
    }

    // 等待所有執行緒完成
    for (auto &t : threads) {
        t.join();
    }

    std::cout << "Final counter value: " << counter << std::endl;
    return 0;
}
```

### Python Spinlock 範例

```python
import threading
import time

class Spinlock:
    def __init__(self):
        self.locked = False

    def lock(self):
        while True:
            # 嘗試獲得鎖
            if not self.locked:
                self.locked = True
                return
            # 短暫休眠以減少 CPU 使用率
            time.sleep(0)

    def unlock(self):
        self.locked = False

# 測試自旋鎖
def test_spinlock(spinlock, counter):
    for _ in range(100000):
        spinlock.lock()
        counter[0] += 1  # 需要保護的共享資源
        spinlock.unlock()

if __name__ == "__main__":
    spinlock = Spinlock()
    counter = [0]  # 使用列表來保證共享可變性
    threads = []

    # 創建多個執行緒來測試自旋鎖
    for _ in range(4):
        t = threading.Thread(target=test_spinlock, args=(spinlock, counter))
        threads.append(t)
        t.start()

    # 等待所有執行緒完成
    for t in threads:
        t.join()

    print(f"Final counter value: {counter[0]}")
```

### 總結
- **C++ 版本**使用 `std::atomic_flag` 來實現自旋鎖，並在鎖不可用時使用 `std::this_thread::yield()` 來提高效率。
- **Python 版本**使用簡單的布林變數來表示鎖的狀態，並在鎖不可用時使用 `time.sleep(0)` 來減少 CPU 使用率。

這兩個範例展示了如何在 C++ 和 Python 中實現自旋鎖，並在多執行緒環境中使用它們來保護共享資源。

---

要故意增加 context switch 數量，可以利用大量的**多執行緒或多進程**操作，這樣可以強制系統在不同執行緒或進程間頻繁地切換，從而增加 context switch 次數。

以下是一個 Python 程式範例，它通過多執行緒不停地進行計算操作，來增加 context switch 數量。你可以在執行這段程式碼的同時使用 `perf` 來觀察 context switch 數量的增長。

### Python 程式碼：產生大量的 Context Switch

這個範例會啟動多個執行緒，每個執行緒進行計算並在短時間內進入睡眠，以迫使系統頻繁地在不同執行緒之間切換。

```python
import threading
import time

def cpu_intensive_task():
    while True:
        # 模擬 CPU 密集型工作
        sum(i * i for i in range(1000))
        # 短暫休眠，讓系統有機會進行 context switch
        time.sleep(0.001)

# 啟動多個執行緒
threads = []
for _ in range(100):  # 可以調整執行緒數量來增加負載
    t = threading.Thread(target=cpu_intensive_task)
    t.start()
    threads.append(t)

# 保持主程式運行一段時間
try:
    time.sleep(10)  # 可以調整時間長度
except KeyboardInterrupt:
    pass
finally:
    # 停止所有執行緒
    for t in threads:
        t.join(timeout=0)
```

### 步驟

1. **執行上述 Python 程式碼**來創建多個執行緒。
   
   ```bash
   python3 your_script_name.py
   ```

2. **同時使用 `perf` 工具**來測量 context switch 數量。在新終端中執行：

   ```bash
   sudo perf stat -e context-switches sleep 10
   ```

   或直接執行 `perf`，讓它在多執行緒程式運行時計算 context switch 次數：

   ```bash
   sudo perf stat -e context-switches python3 your_script_name.py
   ```

### 解釋

- 這個程式會啟動 100 個執行緒，每個執行緒都執行 CPU 密集的計算操作並短暫休眠。這種設計可以強制系統頻繁地在不同執行緒之間進行切換，從而產生大量的 context switch。
- **`time.sleep(0.001)`** 是為了給系統一個切換執行緒的機會，加快 context switch 的頻率。
- 調整執行緒數量（`100` 可以增加或減少），以及程式運行的時間（例如 `sleep 10`），可以控制 context switch 數量。

### 注意

這種方法會給 CPU 帶來較大的負擔，請在空閒時間或非生產環境下執行，以免影響系統其他進程。

---

在高頻交易中，記憶體破頁（page faults）對效能的影響非常顯著。高頻交易系統通常需要在微秒或更短的時間內處理大量數據，因此頻繁的破頁將會增加內存訪問延遲，降低交易速度，甚至導致潛在的延遲和損失。

以下是破頁對高頻交易的影響以及減少破頁的建議：

### 破頁在高頻交易中的影響
1. **延遲增加**：高頻交易的效能依賴於最低的延遲。破頁會導致 CPU 將資料從主記憶體（RAM）載入到快取，這會增加內存訪問延遲，影響下單和訂單匹配的速度。
2. **資源浪費**：頻繁的破頁會消耗額外的 CPU 時間和內存頻寬，佔用交易系統的資源，導致在高負載狀況下系統效能下降。
3. **不可預測的延遲**：破頁導致的延遲在每次發生時長度不一，這對高頻交易系統的穩定性和預測性是一個挑戰。

### 減少破頁的建議
1. **記憶體對齊與連續分配**：盡量使用連續的記憶體分配，如使用 `numpy` 或結構化的資料陣列來儲存行情或交易資料。這樣可以減少訪問時的破頁次數，提升內存的快取命中率。

2. **使用 Huge Pages**：在 Linux 上配置「大頁面（Huge Pages）」功能，讓應用程式將資料分配到大頁面，減少頁面數量，從而減少破頁次數。

3. **減少動態分配**：避免頻繁的動態記憶體分配。高頻交易系統通常會預先分配好固定大小的記憶體空間，並重複利用，減少在交易過程中動態分配和釋放記憶體的次數。

4. **資料結構的選擇**：使用內存效率高的資料結構（如陣列或 `numpy`）代替 Python 清單或字典，減少破頁的可能性。陣列和 `numpy` 陣列會在連續的內存中分配，對於高頻訪問的資料（如行情資料和訂單數據）特別有利。

5. **關注 L1/L2 快取利用率**：設計程式時，可以將頻繁使用的資料儲存在 L1/L2 快取大小內，避免頻繁訪問主記憶體。儲存高頻訪問的資料到固定大小的資料結構中，並優化內存訪問模式，最大化快取命中率。

6. **定期的記憶體清理**：對於不可避免的動態記憶體分配場景，確保定期釋放已不再需要的記憶體空間，避免破頁增多。 

### 具體實踐
可以使用如下工具檢查內存訪問情況和破頁次數：
- **perf**：可以用 `perf stat -e page-faults` 來監控破頁次數。
- **Huge Pages 配置**：
  - 確保 Linux 上的 Huge Pages 設定（如 `echo 1000 > /proc/sys/vm/nr_hugepages` 設置大頁面數量）。
  - 程式內啟用 `mmap` 等接口，專門為大頁面記憶體進行分配。

### 總結
減少破頁對高頻交易的效能有顯著提升。有效利用記憶體分配和管理策略，可以顯著降低記憶體延遲對交易系統的影響，從而保持交易速度的穩定性和一致性。



要讓程式引發大量的 page faults，可以使用一些會不斷分配和釋放大量記憶體的小資料結構，並頻繁訪問隨機位置的資料。相比之下，減少 page faults 的程式可以採用連續的記憶體分配方式，並在一開始就將所有資料載入。

以下是兩個範例：

1. 第一個範例會產生大量 page faults，因為它隨機分配和訪問資料。
2. 第二個範例則會減少 page faults，因為它使用了連續分配並優化訪問模式。

可以使用 `perf` 來執行這些程式，並比較 page faults 的數量。

### 1. 高 page faults 範例

此範例不斷隨機分配並訪問記憶體中的資料，導致頻繁的 page faults：

```python
import random
import time

def high_page_faults():
    data = []
    try:
        for _ in range(100000):
            # 每次隨機生成大約 1 MB 的字串並放入列表中
            data.append("A" * 1024 * 1024)
            # 隨機訪問資料，增加 page faults 的機會
            _ = data[random.randint(0, len(data) - 1)]
    except MemoryError:
        print("記憶體不足，退出程式。")

if __name__ == "__main__":
    high_page_faults()
```

### 2. 低 page faults 範例

此範例會一次性分配一大塊連續的記憶體，並有序訪問資料以減少 page faults 的發生：

```python
import numpy as np

def low_page_faults():
    # 一次性分配約 100 MB 的連續記憶體
    data = np.zeros((100, 1024 * 1024 // 8), dtype=np.float64)
    for i in range(len(data)):
        # 有序訪問記憶體中的資料
        data[i] = i

if __name__ == "__main__":
    low_page_faults()
```

### 使用 `perf` 比較 page faults

1. 先執行 **高 page faults** 程式：

   ```bash
   sudo perf stat -e page-faults python3 high_page_faults.py
   ```

2. 接著執行 **低 page faults** 程式：

   ```bash
   sudo perf stat -e page-faults python3 low_page_faults.py
   ```

### 結果比較

`perf` 執行後會顯示 `page-faults` 的計數結果。理論上，`high_page_faults.py` 應該顯示更高的 page faults 計數，而 `low_page_faults.py` 則會顯示較少的 page faults。這主要是因為 `high_page_faults.py` 使用隨機分配和訪問，導致更多的記憶體頁面被頻繁釋放和重載入；而 `low_page_faults.py` 使用連續記憶體和有序訪問，使快取更有效。

---

在高頻交易系統中，對於需要頻繁執行的任務，**鎖的選擇至關重要**。高頻交易要求最低延遲和高併發，因此傳統的鎖（如普通的互斥鎖或全局鎖）可能會導致性能瓶頸。以下是一些適合高頻交易系統的鎖，並介紹它們的適用情況：

### 1. 自旋鎖（Spinlock）
自旋鎖是一種高效的鎖，適合短時間內可以取得資源的情況。自旋鎖的運作方式是持鎖者會不斷輪詢，直到鎖被釋放。這可以避免切換上下文的開銷。

**優點**：
- 適合在鎖定時間非常短的情況。
- 避免了上下文切換的開銷。

**缺點**：
- 如果鎖定時間長，會導致 CPU 資源浪費。

**適用情況**：適合非常短的臨界區，適合多執行緒的併發訪問（例如頻繁更新行情資訊）。

**Python 示例**：

```python
import threading

lock = threading.Lock()

def high_freq_task():
    while True:
        if lock.acquire(False):  # 嘗試自旋
            try:
                # 執行短期的臨界區代碼
                pass
            finally:
                lock.release()
```

### 2. 無鎖資料結構（Lock-Free Data Structures）
無鎖資料結構基於原子操作（如 CAS，Compare-And-Swap），在多執行緒併發訪問時無需使用鎖。這些資料結構包括無鎖佇列、無鎖堆疊等。

**優點**：
- 無需鎖定，避免了鎖的競爭和上下文切換。
- 提高了執行緒間的併發度。

**缺點**：
- 實現複雜，且需要仔細考慮記憶體一致性問題。

**適用情況**：適合高度併發的任務，例如事件隊列、交易指令池等。

### 3. 讀寫鎖（Read-Write Lock）
如果某些資源的讀取遠多於寫入，可以使用讀寫鎖。這種鎖允許多個讀取執行緒同時讀取，但只允許一個寫入執行緒操作。

**優點**：
- 增加了讀取併發度，適合多讀少寫的情況。
  

**缺點**：
- 在寫入密集的情況下效能不佳。

**適用情況**：適合行情訂閱、讀取市場數據等多讀少寫的場景。

**Python 示例**（使用 `threading` 模組中的 `RLock` 作為讀寫鎖）：

```python
import threading

lock = threading.RLock()

def read_data():
    with lock:
        # 讀取操作
        pass

def write_data():
    with lock:
        # 寫入操作
        pass
```

### 4. 異步編程與協程
在一些高頻交易場景中，尤其是 I/O 密集型操作，可以避免使用鎖，改為使用協程和事件驅動的編程模式（如 Python 中的 `asyncio`）。這樣可以減少同步鎖的開銷，充分利用 CPU 資源。

**優點**：
- 無需鎖，減少了鎖競爭開銷。
- 更適合 I/O 密集型和多網路請求的場景。

**適用情況**：適合 I/O 密集的操作，如多訂閱數據源的數據流處理。

**Python 示例**：

```python
import asyncio

async def fetch_data():
    # 異步執行讀取操作
    await asyncio.sleep(1)

async def main():
    await asyncio.gather(fetch_data(), fetch_data())

# 執行異步任務
asyncio.run(main())
```

### 總結
- **自旋鎖**：適合短期的臨界區。
- **無鎖資料結構**：適合需要高併發的數據結構（如佇列）。
- **讀寫鎖**：適合多讀少寫的場景。
- **異步編程和協程**：適合 I/O 密集型任務。

在高頻交易系統中，可以根據特定情境選擇合適的鎖或替代方法，以確保系統在高併發下仍具備低延遲和高效能。



---

要比較使用 `Spinlock` 和 `普通互斥鎖（Mutex）` 的效能，可以創建一個多執行緒程式，並讓每個執行緒執行短期的臨界區操作。這樣可以觀察在高頻進入和退出臨界區的情況下，兩種鎖的性能差異。Python 中可以模擬 `Spinlock` 的行為，但需要注意，由於 GIL（Global Interpreter Lock）的存在，純 Python 程式的執行緒並不完全適合多核併發性能測試。以下範例展示了使用自旋行為來模擬 `Spinlock`，以及傳統的 `Lock` 比較。

### 範例設置

以下程式使用了兩種鎖：
1. **自旋鎖（Spinlock）**：使用輪詢等待的方式模擬自旋鎖。
2. **普通互斥鎖（Mutex）**：使用 Python 中的 `threading.Lock` 作為傳統鎖。

### 程式碼

```python
import threading
import time

class Spinlock:
    def __init__(self):
        self.lock = threading.Lock()

    def acquire(self):
        # 自旋行為，直到取得鎖
        while not self.lock.acquire(blocking=False):
            pass

    def release(self):
        self.lock.release()

# 共享變數和次數
counter = 0
num_iterations = 1000000  # 每個執行緒的迭代次數

def task_with_spinlock(lock):
    global counter
    for _ in range(num_iterations):
        lock.acquire()
        counter += 1  # 進行簡單操作
        lock.release()

def task_with_mutex(lock):
    global counter
    for _ in range(num_iterations):
        lock.acquire()
        counter += 1
        lock.release()

def measure_performance(lock_type):
    global counter
    counter = 0  # 重置計數器
    num_threads = 4
    threads = []

    start_time = time.time()

    # 建立執行緒
    if lock_type == "spinlock":
        lock = Spinlock()
        for _ in range(num_threads):
            thread = threading.Thread(target=task_with_spinlock, args=(lock,))
            threads.append(thread)
    elif lock_type == "mutex":
        lock = threading.Lock()
        for _ in range(num_threads):
            thread = threading.Thread(target=task_with_mutex, args=(lock,))
            threads.append(thread)

    # 啟動所有執行緒
    for thread in threads:
        thread.start()

    # 等待所有執行緒結束
    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"{lock_type.capitalize()} duration: {end_time - start_time:.4f} seconds, Counter: {counter}")

# 測試自旋鎖和互斥鎖效能
measure_performance("spinlock")
measure_performance("mutex")
```

### 程式說明

1. **Spinlock 類別**：使用自旋行為來模擬，當鎖不可用時，執行緒會不斷嘗試取得鎖而不阻塞。
2. **task_with_spinlock 與 task_with_mutex 函數**：這兩個函數分別執行 `Spinlock` 和 `Mutex` 鎖的操作，對共享變數 `counter` 增加計數。
3. **measure_performance 函數**：測試兩種鎖的效能，記錄每次測試的執行時間。

### 執行結果

執行該程式後，將得到自旋鎖和互斥鎖的執行時間。結果大致會如下：

```plaintext
Spinlock duration: 1.2345 seconds, Counter: 4000000
Mutex duration: 1.5678 seconds, Counter: 4000000
```

### 分析結果

在高頻交易環境中，`Spinlock` 在鎖的持有時間短時表現較佳，但如果執行緒的數量增加並且鎖持有時間增加，會導致較高的 CPU 使用率，反而降低效能。相對地，`Mutex` 更適合在需要稍長時間鎖定的情況，因為它會阻塞執行緒而不是不斷輪詢。

---

當設計和實施高效能項目時，以下是一些關鍵的策略和最佳實踐，可以幫助提升系統性能和響應速度，特別在高頻交易和其他要求低延遲的應用中：

### 高效能項目總結

#### 1. 硬體優化
- **選擇高效能硬體**：使用快速的 CPU、充足的 RAM 和高效的 SSD，特別是對於 I/O 密集型應用。
- **網路延遲最小化**：選擇低延遲的網路設備和連接，並考慮使用專用線路。

#### 2. 記憶體管理
- **減少記憶體破頁**：增加物理記憶體，優化虛擬記憶體設定，並使用適當的資料結構。
- **監控記憶體使用**：定期檢查記憶體泄漏，並在適當時釋放不再使用的記憶體。

#### 3. 線程和進程管理
- **線程親和性**：將特定線程綁定到特定 CPU 核心，以減少上下文切換和提高快取命中率。
- **使用線程池**：減少線程創建和銷毀的開銷，並合理安排線程數量以匹配 CPU 核心數量。

#### 4. 減少上下文切換
- **優化線程數量**：確保線程數量與 CPU 核心數量相匹配，避免過多的線程導致頻繁切換。
- **使用無鎖資料結構**：盡量使用無鎖編程來減少鎖的競爭，降低上下文切換的開銷。

#### 5. I/O 優化
- **異步 I/O 操作**：使用異步 I/O 來避免線程阻塞，提升系統的響應性。
- **批量處理**：合併多個小的 I/O 操作，減少系統對 I/O 的頻繁請求。

#### 6. 程式設計優化
- **合併任務**：將多個小任務合併為大任務，減少任務切換的頻率。
- **使用事件驅動架構**：透過事件驅動設計來減少線程數量，從而降低上下文切換的頻率。

#### 7. 性能監控與分析
- **使用監控工具**：定期使用性能監控工具（如 `perf`, `top`, `htop`）來追蹤系統性能，識別瓶頸。
- **性能基準測試**：對系統進行基準測試，評估其在不同負載下的性能，並根據結果進行優化。

#### 8. 軟體架構考量
- **分散式系統設計**：考慮使用分散式架構來提升系統的可擴展性和容錯性。
- **服務微型化**：將應用拆分為小的微服務，根據需要獨立擴展，提升整體性能。

### 總結

在高效能項目中，關鍵在於硬體的選擇、記憶體管理、線程和進程管理、I/O 優化，以及程式設計的合理架構。通過綜合這些策略，可以大幅提升系統的性能和響應速度，特別是在對延遲要求高的應用場景中。如果你有具體的項目或情境需要進一步探討，隨時告訴我！