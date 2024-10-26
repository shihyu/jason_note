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