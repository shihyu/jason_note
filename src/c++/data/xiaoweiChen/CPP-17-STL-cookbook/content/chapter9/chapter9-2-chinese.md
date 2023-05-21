# 讓程序在特定時間休眠

C++11中對於線程的控制非常優雅和簡單。在`this_thread`的命名空間中，包含了只能被運行線程調用的函數。其包含了兩個不同的函數，讓線程睡眠一段時間，這樣就不需要使用任何額外的庫，或是操作系統依賴的庫來執行這個任務。

本節中，我們將關注於如何將線程暫停一段時間，或是讓其休眠一段時間。

## How to do it...

我們將完成一個短小的程序，並讓主線程休眠一段時間：

1. 包含必要的頭文件，並聲明所使用的命名空間。`chrono_literals`空間包含一段時間的縮略值：

   ```c++
   #include <iostream>
   #include <chrono>
   #include <thread>
   
   using namespace std;
   using namespace chrono_literals; 
   ```

2. 我們直接寫主函數，並讓主線程休眠5秒和300毫秒。感謝`chrono_literals`，我們可以寫成一種非常可讀方式：

   ```c++
   int main()
   {
       cout << "Going to sleep for 5 seconds"
       	    " and 300 milli seconds.\n";
       
       this_thread::sleep_for(5s + 300ms);
   ```

3. 休眠狀態是相對的。當然，我們能用絕對時間來表示。讓休眠直到某個時間點才終止，這裡我們在`now`的基礎上加了3秒：

   ```c++
   	cout << "Going to sleep for another 3 seconds.\n";
   
   	this_thread::sleep_until(
   		chrono::high_resolution_clock::now() + 3s);
   ```

4. 在程序退出之前，我們會打印一個表示睡眠結束：

   ```c++
   	cout << "That's it.\n";
   }
   ```

5. 編譯並運行程序，我們就能獲得如下的輸出。Linux，Mac或其他類似UNIX的操作系統會提供time命令，其能對一個可運行程序的耗時進行統計。使用time對我們的程序進行耗時統計，其告訴我們花費了8.32秒，因為我們讓主線程休眠了5.3秒和3秒。最後還有一個打印，用來告訴我們主函數的休眠終止：

   ```c++
   $ time ./sleep
   Going to sleep for 5 seconds and 300 milli seconds.
   Going to sleep for another 3 seconds.
   That's it.
       
   real0m8.320s
   user0m0.005s
   sys 0m0.003s
   ```

## How it works...

`sleep_for`和`sleep_until`函數都已經在C++11中加入，存放於`std::this_thread`命名空間中。其能對當前線程進行限時阻塞(並不是整個程序或整個進程)。線程被阻塞時不會消耗CPU時間，操作系統會將其標記掛起的狀態，時間到了後線程會自動醒來。這種方式的好處在於，不需要知道操作系統對我們運行的程序做了什麼，因為STL會將其中的細節進行包裝。

`this_thread::sleep_for`函數能夠接受一個`chrono::duration`值。最簡單的方式就是`1s`或`5s+300ms`。為了使用這種非常簡潔的字面時間表示方式，我們需要對命名空間進行聲明`using namespace std::chrono_literals;`。

`this_thread::sleep_until`函數能夠接受一個`chrono::time_out`參數。這就能夠簡單的指定對應的壁掛鐘時間，來限定線程休眠的時間。

喚醒時間和操作系統的時間的精度一樣。大多數操作系統的時間精度通常夠用，但是其可能對於一些時間敏感的應用非常不利。

另一種讓線程休眠一段時間的方式是使用`this_thread::yield`。其沒有參數，也就意味著這個函數不知道這個線程要休眠多長時間。所以，這個函數並不建議用來對線程進行休眠或停滯一個線程。其只會以協作的方式告訴操作系統，讓操作系統對線程和進程重新進行調度。如果沒有其他可以調度的線程或進程，那麼這個“休眠”線程則會立即執行。正因為如此，很少用`yield`讓線程休眠一段時間。