# 打造異常安全的共享鎖——std::unique_lock和std::shared_lock

由於對於線程的操作嚴重依賴於操作系統，所以STL提供與系統無關的接口是非常明智的，當然STL也會提供線程間的同步操作。這樣就不僅是能夠啟動和停止線程，使用STL庫也能完成線程的同步操作。

本節中，我們將瞭解到STL中的互斥量和RAII鎖。我們使用這些工具對線程進行同步時，也會瞭解STL中更多同步輔助的方式。

## How to do it...

我們將使用`std::shared_mutex`在獨佔(exclusive)和共享(shared)模式下來完成一段程序，並且也會瞭解到這兩種方式意味著什麼。另外，我們將不會對手動的對程序進行上鎖和解鎖的操作，這些操作都交給RAII輔助函數來完成：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <shared_mutex>
   #include <thread>
   #include <vector>
   
   using namespace std;
   using namespace chrono_literals;
   ```

2. 整個程序都會圍繞共享互斥量展開，為了簡單，我們定義了一個全局實例：

   ```c++
   shared_mutex shared_mut;
   ```

3. 接下來，我們將會使用`std::shared_lock`和`std::unique_lock`這兩個RAII輔助者。為了讓其類型看起來沒那麼複雜，這裡進行別名操作：

   ```c++
   using shrd_lck = shared_lock<shared_mutex>;
   using uniq_lck = unique_lock<shared_mutex>;
   ```

4. 開始寫主函數之前，先使用互斥鎖的獨佔模式來實現兩個輔助函數。下面的函數中，我們將使用`unique_lock`實例來作為共享互斥鎖。其構造函數的第二個參數`defer_lock`會告訴對象讓鎖處於解鎖的狀態。否則，構造函數會嘗試對互斥量上鎖阻塞程序，直至成功為止。然後，會對`exclusive_lock`的成員函數`try_lock`進行調用。該函數會立即返回，並且返回相應的布爾值，布爾值表示互斥量是否已經上鎖，或是在其他地方已經鎖住：

   ```c++
   static void print_exclusive()
   {
       uniq_lck l {shared_mut, defer_lock};
       
       if (l.try_lock()) {
       	cout << "Got exclusive lock.\n";
       } else {
       	cout << "Unable to lock exclusively.\n";
       }
   }
   ```

5. 另一個函數也差不多。其會將程序阻塞，直至其獲取相應的鎖。然後，會使用拋出異常的方式來模擬發生錯誤的情況(只會返回一個整數，而非一個非常複雜的異常對象)。雖然，其會立即退出，並且在上下文中我們獲取了一個鎖住的互斥量，但是這個互斥量也可以被釋放。這是因為`unique_lock`的析構函數在任何情況下都會將對應的鎖進行釋放：

   ```c++
   static void exclusive_throw()
   {
       uniq_lck l {shared_mut};
       throw 123;
   }
   ```

6. 現在，讓我們來寫主函數。首先，先開一個新的代碼段，並且實例化一個`shared_lock`實例。其構造函數將會立即對共享模式下的互斥量進行上鎖。我們將會在下一步瞭解到這一動作的意義：

   ```c++
   int main()
   {
       {
           shrd_lck sl1 {shared_mut};
           
           cout << "shared lock once.\n";
   ```

7. 現在我們開啟另一個代碼段，並使用同一個互斥量實例化第二個`shared_lock`實例。現在具有兩個`shared_lock`實例，並且都具有同一個互斥量的共享鎖。實際上，可以使用同一個互斥量實例化很多的`shared_lock`實例。然後，調用`print_exclusive`，其會嘗試使用互斥量的獨佔模式對互斥量進行上鎖。這樣的調用當然不會成功，因為互斥量已經在共享模式下鎖住了：

   ```c++
           {
               shrd_lck sl2 {shared_mut};
   
               cout << "shared lock twice.\n";
   
               print_exclusive();
           }
   ```

8. 離開這個代碼段後，`shared_locks12`的析構函數將會釋放互斥量的共享鎖。`print_exclusive`函數還是失敗，這是因為互斥量依舊處於共享鎖模式：

   ```c++
           cout << "shared lock once again.\n";
   
           print_exclusive();
       }
       cout << "lock is free.\n";
   ```

9. 離開這個代碼段時，所有`shared_lock`對象就都被銷燬了，並且互斥量再次處於解鎖狀態，現在我們可以在獨佔模式下對互斥量進行上鎖了。調用`exclusive_throw`，然後調用`print_exclusive`。不過因為`unique_lock`是一個RAII對象，所以是異常安全的，也就是無論`exclusive_throw`返回了什麼，互斥量最後都會再次解鎖。這樣即便是互斥量處於鎖定狀態，`print_exclusive` 也不會被錯誤的狀態所阻塞：

   ```c++
       try {
      		exclusive_throw();
       } catch (int e) {
       	cout << "Got exception " << e << '\n';
       }
   
       print_exclusive();
   }
   ```

10. 編譯並運行這段代碼則會得到如下的輸出。前兩行展示的是兩個共享鎖實例。然後，`print_exclusive`函數無法使用獨佔模式對互斥量上鎖。在離開內部代碼段後，第二個共享鎖解鎖，`print_exclusive`函數依舊會失敗。在離開這個代碼段後，將會對互斥量所持有的鎖進行釋放，這樣`exclusive_throw`和`print_exclusive`最終才能對互斥量進行上鎖：

   ```c++
   $ ./shared_lock
   shared lock once.
   shared lock twice.
   Unable to lock exclusively.
   shared lock once again.
   Unable to lock exclusively.
   lock is free.
   Got exception 123
   Got exclusive lock.
   ```

## How it works...

查閱C++文檔時，我們會對不同的互斥量和RAII輔助鎖有些困惑。在我們回看這節的代碼之前，讓我們來對STL的這兩個部分進行總結。

**互斥量**

其為**mut**ual **ex**clusion的縮寫。併發時不同的線程對於相關的共享數據同時進行修改時，可能會造成結果錯誤，我們在這裡就可以使用互斥量對象來避免這種情況的發生，STL提供了不同特性的互斥量。不過，這些互斥量的共同點就是具有`lock`和`unlock`兩個成員函數。

一個互斥量在解鎖狀態下時，當有線程對其使用`lock()`時，這個線程就獲取了互斥量，並對互斥量進行上鎖。這樣，但其他線程要對這互斥量進行上鎖時，就會處於阻塞狀態，知道第一個線程對該互斥量進行釋放。`std::mutex`就可以做到。

這裡將STL一些不同的互斥量進行對比：

| 類型名                                                       | 描述                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [mutex](http://zh.cppreference.com/w/cpp/thread/mutex)       | 具有`lock`和`unlock`成員函數的標準互斥量。並提供非阻塞函數`try_lock`成員函數。 |
| [timed_mutex](http://zh.cppreference.com/w/cpp/thread/timed_mutex) | 與互斥量相同，並提供`try_lock_for`和`try_lock_until`成員函數，其能在某個時間段內對程序進行阻塞。 |
| [recursive_mutex](http://zh.cppreference.com/w/cpp/thread/recursive_mutex) | 與互斥量相同，不過當一個線程對實例進行上鎖，其可以對同一個互斥量對象多次調用`lock`而不產生阻塞。持有線程可以多次調用`unlock`，不過需要和`lock`調用的次數匹配時，線程才不再擁有這個互斥量。 |
| [recursive_timed_mutex](http://zh.cppreference.com/w/cpp/thread/recursive_timed_mutex) | 提供與`timed_mutex`和`recursive_mutex`的特性。               |
| [shared_mutex](http://zh.cppreference.com/w/cpp/thread/shared_mutex) | 這個互斥量在這方面比較特殊，它可以被鎖定為獨佔模式或共享模式。獨佔模式時，其與標準互斥量的行為一樣。共享模式時，其他線程也可能在共享模式下對其進行上鎖。其會在最後一個處於共享模式下的鎖擁有者進行解鎖時，整個互斥量才會解鎖。其行為有些類似於`shared_ptr`，只不過互斥量不對內存進行管理，而是對鎖的所有權進行管理。 |
| [shared_timed_mutex](http://zh.cppreference.com/w/cpp/thread/shared_timed_mutex) | 同時具有`shared_mutex`和`timed_mutex`兩種互斥量獨佔模式和共享模式的特性。 |

**鎖**

線程對互斥量上鎖之後，很多事情都變的非常簡單，我們只需要上鎖、訪問、解鎖三步就能完成我們想要做的工作。不過對於有些比較健忘的開發者來說，在上鎖之後，很容易忘記對其進行解鎖，或是互斥量在上鎖狀態下拋出一個異常，如果要對這個異常進行處理，那麼代碼就會變得很難看。最優的方式就是程序能夠自動來處理這種事情。這種問題很類似與內存洩漏，開發者在分配內存之後，忘記使用`delete`操作進行內存釋放。

內存管理部分，我們有`unique_ptr`，`shared_ptr`和`weak_ptr`。這些輔助類可以很完美幫我們避免內存洩漏。互斥量也有類似的幫手，最簡單的一個就是`std::lock_guard`。使用方式如下：

```c++
void critical_function()
{
    lock_guard<mutex> l {some_mutex};
    
    // critical section
}
```

`lock_guard`的構造函數能接受一個互斥量，其會立即自動調用`lock`，構造函數會直到獲取互斥鎖為止。當實例進行銷燬時，其會對互斥量再次進行解鎖。這樣互斥量就很難陷入到`lock/unlock`循環錯誤中。

C++17 STL提供瞭如下的RAII輔助鎖。其都能接受一個模板參數，其與互斥量的類型相同(在C++17中，編譯器可以自動推斷出相應的類型)：

| 名稱                                                         | 描述                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [lock_guard](http://zh.cppreference.com/w/cpp/thread/lock_guard) | 這個類沒有什麼其他的，構造函數中調用`lock`，析構函數中調用`unlock`。 |
| [scoped_lock](http://zh.cppreference.com/w/cpp/thread/scoped_lock) | 與`lock_guard`類似，構造函數支持多個互斥量。析構函數中會以相反的順序進行解鎖。 |
| [unique_lock](http://zh.cppreference.com/w/cpp/thread/unique_lock) | 使用獨佔模式對互斥量進行上鎖。構造函數也能接受一個參數用於表示超時到的時間，並不會讓鎖一直處於上鎖的狀態。其也可能不對互斥量進行上鎖，或是假設互斥量已經鎖定，或是嘗試對互斥量進行上鎖。另外，函數可以在`unique_lock`鎖的聲明週期中，對互斥量進行上鎖或解鎖。 |
| [shared_lock](http://zh.cppreference.com/w/cpp/thread/shared_lock) | 與`unique_lock`類似，不過所有操作都是在互斥量的共享模式下進行操作。 |

`lock_guard`和`scoped_lock`只擁有構造和析構函數，`unique_lock`和`shared_lock`就比較複雜了，但也更為通用。我們將在本章的後續章節中瞭解到，這些類型如何用於更加複雜的情況。

現在我們來回看一下本節的代碼。雖然，只在單線程的上下文中運行程序，但是我們可以瞭解到如何對輔助鎖進行使用。`shrd_lck`類型為`shared_lock<shared_mutex>`的縮寫，並且其允許我們在共享模式下對一個實例多次上鎖。當`sl1`和`sl2`存在的情況下，`print_exclusive`無法使用獨佔模式對互斥量進行上鎖。

現在來看看處於獨佔模式的上鎖函數：

```c++
int main()
{
    {
    	shrd_lck sl1 {shared_mut};
    	{
    		shrd_lck sl2 {shared_mut};
    		print_exclusive();
    	}
    	print_exclusive();
    }
    
    try {
    	exclusive_throw();
    } catch (int e) {
    	cout << "Got exception " << e << '\n';
    }
    
    print_exclusive();
}
```

`exclusive_throw`的返回也比較重要，即便是拋出異常退出，`exclusive_throw`函數依舊會讓互斥量再度鎖上。

因為`print_exclusive`使用了一個奇怪的構造函數，我們就再來看一下這個函數：

```c++
void print_exclusive()
{
    uniq_lck l {shared_mut, defer_lock};
    
    if (l.try_lock()) {
    	// ...
    }
}	
```

這裡我們不僅提供了`shared_mut`，還有`defer_lock`作為`unique_lock`構造函數的參數。`defer_lock`是一個空的全局對象，其不會對互斥量立即上鎖，所以我們可以通過這個參數對`unique_lock`不同的構造函數進行選擇。這樣做之後，我們可以調用`l.try_lock()`，其會告訴我們有沒有上鎖。在互斥量上鎖的情況下，就可以做些別的事情了。如果的確有機會獲取鎖，依舊需要析構函數對互斥量進行清理。