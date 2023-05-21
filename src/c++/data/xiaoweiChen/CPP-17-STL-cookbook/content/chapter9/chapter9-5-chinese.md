# 避免死鎖——std::scoped_lock

如果在路上發生了死鎖，就會像下圖一樣：

![](../../images/chapter9/9-5-1.png)

為了讓交通順暢，可能需要一個大型起重機，將路中間的一輛車挪到其他地方去。如果找不到起重機，那麼我們就希望這些司機們能互相配合。當幾個司機願意將車往後退，留給空間給其他車通行，那麼每輛車就不會停在原地了。

多線程編程中，開發者肯定需要避免這種情況的發生。不過，程序比較複雜的情況下，這種情況其實很容易發生。

本節中，我們將會故意的創造一個死鎖的情況。然後，在相同資源的情況下，如何創造出一個死鎖的情形。再使用C++17中，STL的`std::scoped_lock`如何避免死鎖的發生。

## How to do it...

本節中有兩對函數要在併發的線程中執行，並且有兩個互斥量。其中一對製造死鎖，另一對解決死鎖。主函數中，我們將使用這兩個互斥量：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <thread>
   #include <mutex>
   
   using namespace std;
   using namespace chrono_literals;
   ```

2. 實例化兩個互斥量對象，製造死鎖：

   ```c++
   mutex mut_a;
   mutex mut_b;
   ```

3. 為了使用兩個互斥量製造死鎖，我們需要有兩個函數。其中一個函數試圖對互斥量`A`進行上鎖，然後對互斥量B進行上鎖，而另一個函數則試圖使用相反的方式運行。讓兩個函數在等待鎖時進行休眠，我們確定這段代碼永遠處於一個死鎖的狀態。(這就達到了我們演示的目的。當我們重複運行程序，那麼程序在沒有任何休眠代碼的同時，可能會有成功運行的情況。)需要注意的是，這裡我們沒有使用`\n`字符作為換行符，我們使用的是`endl`。`endl`會輸出一個換行符，同時也會對`cout`的流緩衝區進行刷新，所以我們可以確保打印信息不會有延遲或同時出現：

   ```c++
   static void deadlock_func_1()
   {
       cout << "bad f1 acquiring mutex A..." << endl;
       
       lock_guard<mutex> la {mut_a};
       
       this_thread::sleep_for(100ms);
       
       cout << "bad f1 acquiring mutex B..." << endl;
       
       lock_guard<mutex> lb {mut_b};
       
       cout << "bad f1 got both mutexes." << endl;
   }
   ```

4. `deadlock_func_2`和`deadlock_func_1`看起來一樣，就是`A`和`B`的順序相反：

   ```c++
   static void deadlock_func_2()
   {
       cout << "bad f2 acquiring mutex B..." << endl;
       
       lock_guard<mutex> lb {mut_b};
       
       this_thread::sleep_for(100ms);
       
       cout << "bad f2 acquiring mutex A..." << endl;
       
       lock_guard<mutex> la {mut_a};
       
       cout << "bad f2 got both mutexes." << endl;
   }
   ```

5. 現在我們將完成與上面函數相比，兩個無死鎖版本的函數。它們使用了`scoped_lock`，其會作為構造函數參數的所有互斥量進行上鎖。其析構函數會進行解鎖操作。鎖定這些互斥量時，其內部應用了避免死鎖的策略。這裡需要注意的是，兩個函數還是對`A`和`B`互斥量進行操作，並且順序相反：

   ```c++
   static void sane_func_1()
   {
   	scoped_lock l {mut_a, mut_b};
   	
       cout << "sane f1 got both mutexes." << endl;
   }
   
   static void sane_func_2()
   {
   	scoped_lock l {mut_b, mut_a};
   	
       cout << "sane f2 got both mutexes." << endl;
   }
   ```

6. 主函數中觀察這兩種情況。首先，我們使用不會死鎖的函數：

   ```c++
   int main()
   {
       {
           thread t1 {sane_func_1};
           thread t2 {sane_func_2};
           
           t1.join();
           t2.join();
       }
   ```

7. 然後，調用製造死鎖的函數：

   ```c++
       {
           thread t1 {deadlock_func_1};
           thread t2 {deadlock_func_2};
           
           t1.join();
           t2.join();
       }
   }
   ```

8. 編譯並運行程序，就能得到如下的輸出。前兩行為無死鎖情況下，兩個函數的打印結果。接下來的兩個函數則產生死鎖。因為我們能看到f1函數始終是在等待互斥量B，而f2則在等待互斥量A。兩個函數都沒做成功的對兩個互斥量上鎖。我們可以讓這個程序持續運行，不管時間是多久，結果都不會變化。程序只能從外部進行殺死，這裡我們使用`Ctrl + C`的組合鍵，將程序終止：

   ```c++
   $ ./avoid_deadlock
   sane f1 got both mutexes
   sane f2 got both mutexes
   bad f2 acquiring mutex B...
   bad f1 acquiring mutex A...
   bad f1 acquiring mutex B...
   bad f2 acquiring mutex A...
   ```

## How it works...

例子中，我們故意製造了死鎖，我們也瞭解了這樣一種情況發生的有多快。在一個很大的項目中，多線程開發者在編寫代碼的時候，都會共享一些互斥量用於保護資源，所有開發者都需要遵循同一種加鎖和解鎖的順序。這種策略或規則是很容易遵守的，不過也是很容易遺忘的。另一個問題則是*鎖序倒置*。

`scoped_lock`對於這種情況很有幫助。其實在C++17中添加，其工作原理與`lock_guard`和`unique_lock`一樣：其構造函數會進行上鎖操作，並且析構函數會對互斥量進行解鎖操作。`scoped_lock`特別之處是，可以指定多個互斥量。

`scoped_lock`使用`std::lock`函數，其會調用一個特殊的算法對所提供的互斥量調用`try_lock`函數，這是為了避免死鎖。因此，在加鎖與解鎖的順序相同的情況下，使用`scoped_lock`或對同一組鎖調用`std::lock`都是非常安全的。