## 前言

私以為個人的技術水平應該是一個螺旋式上升的過程：先從書本去瞭解一個大概，然後在實踐中加深對相關知識的理解，遇到問題後再次回到書本，然後繼續實踐……接觸C++並行程式設計已經一年多，從慢慢啃《C++並行程式設計實戰》這本書開始，不停在期貨高頻交易軟體的開發實踐中去理解、運用、最佳化多執行緒相關技術。多執行緒知識的學習也是先從最基本的執行緒建立、互斥鎖、條件變數到更高級的執行緒安全資料結構、執行緒池等等技術，當然在項目中也用到了簡單的無鎖程式設計相關知識，今天把一些體會心得跟大家分享一下，如有錯誤，還望大家批評指正。

## 多執行緒並行讀寫

在編寫多執行緒程序時，最重要的問題就是多執行緒間共享資料的保護。多個執行緒之間共享地址空間，所以多個執行緒共享處理程序中的全域變數和堆，都可以對全域變數和堆上的資料進行讀寫，但是如果兩個執行緒同時修改同一個資料，可能造成某執行緒的修改丟失；如果一個執行緒寫的同時，另一個執行緒去讀該資料時可能會讀到寫了一半的資料。這些行為都是執行緒不安全的行為，會造成程式執行邏輯出現錯誤。舉個最簡單的例子：

```cpp
#include <iostream>
#include <thread>

using namespace std;

int  i = 0;
mutex mut;

void iplusplus() {
    int c = 10000000;  //循環次數
    while (c--) {
        i++;
    }
}
int main()
{
    thread thread1(iplusplus);  //建立並運行執行緒1
    thread thread2(iplusplus);  //建立並運行執行緒2
    thread1.join();  // 等待執行緒1運行完畢
    thread2.join();  // 等待執行緒2運行完畢
    cout << "i = " << i << endl;
    return 0;
}
```

上面程式碼main函數中建立了兩個執行緒thread1和thread2，兩個執行緒都是運行iplusplus函數，該函數功能就是運行i++語句10000000次，按照常識，兩個執行緒各對i自增10000000次，最後i的結果應該是20000000，但是運行後結果卻是如下：

![img](images/v2-031d9901f4adb2325eac0efb9380812d_720w.webp)

i並不等於20000000，這是在多執行緒讀寫情況下沒有對執行緒間共享的變數i進行保護所導致的問題。

## 有鎖程式設計

對於保護多執行緒共享資料，最常用也是最基本的方法就是使用C++11執行緒標準庫提供的互斥鎖mutex保護臨界區，保證同一時間只能有一個執行緒可以獲取鎖，持有鎖的執行緒可以對共享變數進行修改，修改完畢後釋放鎖，而不持有鎖的執行緒阻塞等待直到獲取到鎖，然後才能對共享變數進行修改，這種方法幾乎是並行程式設計中的標準做法。大體流程如下：

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>

using namespace std;
int  i = 0;
mutex mut; //互斥鎖

void iplusplus() {
    int c = 10000000;  //循環次數
    while (c--) {
        mut.lock();  //互斥鎖加鎖
        i++;
        mut.unlock(); //互斥鎖解鎖
    }
}
int main()
{
    chrono::steady_clock::time_point start_time = chrono::steady_clock::now();//開始時間
    thread thread1(iplusplus);
    thread thread2(iplusplus);
    thread1.join();  // 等待執行緒1運行完畢
    thread2.join();  // 等待執行緒2運行完畢
    cout << "i = " << i << endl;
    chrono::steady_clock::time_point stop_time = chrono::steady_clock::now();//結束時間
    chrono::duration<double> time_span = chrono::duration_cast<chrono::microseconds>(stop_time - start_time);
    std::cout << "共耗時：" << time_span.count() << " ms" << endl; // 耗時
    system("pause");
    return 0;
}
```

程式碼14行和16行分別為互斥鎖加鎖和解鎖程式碼，29行我們列印程式執行耗時，程式碼運行結果如下：

![img](images/v2-2ecdc6816641dec702b50b329d925d13_720w.webp)

可以看到，通過加互斥鎖，i的運行結果是正確的，由此解決了多執行緒同時寫一個資料產生的執行緒安全問題，程式碼總耗時3.37328ms。

## 無鎖程式設計

原子操作是無鎖程式設計的基石，原子操作是不可分隔的操作，一般通過CAS(Compare and
Swap)操作實現，CAS操作需要輸入兩個數值，一個舊值（期望操作前的值）和一個新值，在操作期間先比較下舊值有沒有發生變化，如果沒有發生變化，才交換成新值，發生了變化則不交換。C++11的執行緒庫為我們提供了一系列原子類型，同時提供了相對應的原子操作，我們通過使用這些原子類型即可擺脫每次對共享變數進行操作都進行的加鎖解鎖動作，節省了系統開銷，同時避免了執行緒因阻塞而頻繁的切換。原子類型的基本使用方法如下：

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>

using namespace std;
atomic<int> i = 0;

void iplusplus() {
    int c = 10000000;  //循環次數
    while (c--) {
        i++;
    }
}
int main()
{
    chrono::steady_clock::time_point start_time = chrono::steady_clock::now();//開始時間
    thread thread1(iplusplus);
    thread thread2(iplusplus);
    thread1.join();  // 等待執行緒1運行完畢
    thread2.join();  // 等待執行緒2運行完畢
    cout << "i = " << i << endl;
    chrono::steady_clock::time_point stop_time = chrono::steady_clock::now();//結束時間
    chrono::duration<double> time_span = chrono::duration_cast<chrono::microseconds>(stop_time - start_time);
    std::cout << "共耗時：" << time_span.count() << " ms" << endl; // 耗時
    system("pause");
    return 0;
}
```

程式碼的第8行定義了一個原子類型（int）變數i，在第13行多執行緒修改i的時候即可免去加鎖和解鎖的步驟，同時又能保證變數i的執行緒安全性。程式碼運行結果如下：

![img](images/v2-3b9ca8e34703c8daa7493486f01cbcbe_720w.webp)

可以看到i的值是符合預期的，程式碼運行總耗時1.12731ms，僅為有鎖程式設計的耗時3.37328ms的1/3，由此可以看出無鎖程式設計由於避免了加鎖而相對於有鎖程式設計提高了一定的性能。

## 總結

無鎖程式設計最大的優勢是什麼？是性能提高嗎？其實並不是，我們的測試程式碼中臨界區非常短，只有一個語句，所以顯得加鎖解鎖操作對程序性能影響很大，但在實際應用中，我們的臨界區一般不會這麼短，臨界區越長，加鎖和解鎖操作的性能損耗越微小，無鎖程式設計和有鎖程式設計之間的性能差距也就越微小。

我認為無鎖程式設計最大的優勢在於兩點：

1. 避免了死鎖的產生。由於無鎖程式設計避免了使用鎖，所以也就不會出現並行程式設計中最讓人頭疼的死鎖問題，對於提高程序健壯性有很大積極意義
2. 程式碼更加清晰與簡潔。對於一個多執行緒共享的變數，保證其安全性我們只需在聲明時將其聲明為原子類型即可，在程式碼中使用的時候和使用一個普通變數一樣，而不用每次使用都要在前面寫個加鎖操作，在後面寫一個解鎖操作。我寫的C++期貨高頻交易軟體中，有一個全域變數fund，儲存的是當前資金量，程序採用執行緒池運行交易策略，交易策略中頻繁使用到fund變數，如果採用加鎖的方式，使用起來極其繁瑣，為了保護一個fund變數需要非常頻繁的加鎖解鎖，後來將fund變數改為原子類型，後面使用就不用再考慮加鎖問題，整個程序閱讀起來清晰很多。

如果是為了提高性能將程序大幅改寫成無鎖程式設計，一般來說結果可能會讓我們失望，而且無鎖程式設計裡面需要注意的地方也非常多，比如ABA問題，記憶體順序問題，正確實現無鎖程式設計比實現有鎖程式設計要困難很多，除非有必要（確定了性能瓶頸）才去考慮使用無鎖程式設計，否則還是使用互斥鎖更好，畢竟程序的高性能是建立在程序正確性的基礎上，如果程序不正確，一切性能提升都是徒勞無功。