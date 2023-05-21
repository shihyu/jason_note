# 轉換不同的時間單位——std::ratio

C++11之後，STL具有了很多用來測量和顯示時間的新類型和函數。STL這部分內容放在`std::chrono`命名空間中。

本節我們將關注測量時間，以及如何對兩種不同的時間單位進行轉換，比如：秒到毫秒和微秒的轉換。STL已經提供了現成的工具，我們可以自定義時間單位，並且可以無縫的在不同的時間單位間進行轉換。

## How to do it...

本節，我們寫一個小遊戲，會讓用戶輸入一個單詞，然後記錄用戶打字的速度，並以不同的時間單位顯示所用時間：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <chrono>
   #include <ratio>
   #include <cmath>
   #include <iomanip>
   #include <optional>
   
   using namespace std; 
   ```

2. `chrono::duration`經常用來表示所用時間的長度，其為秒的倍數或小數，所有STL的程序都由整型類型進行特化。本節中，將使用`double`進行特化。本節之後，我們更多的會關注已經存在於STL的時間單位：

   ```c++
   using seconds = chrono::duration<double>;
   ```

3. 1毫秒為1/1000秒，可以用這個單位來定義秒。`ratio_multiply`模板參數可以使用STL預定義的`milli`用來表示`seconds::period`，其會給我們相應的小數。`ratio_multiply`為基本時間的倍數：

   ```c++
   using milliseconds = chrono::duration<
   	double, ratio_multiply<seconds::period, milli>>;
   ```

4. 對於微秒來說也是一樣的。可以使用`micro`表示：

   ```c++
   using microseconds = chrono::duration<
   	double, ratio_multiply<seconds::period, micro>>;
   ```

5. 現在我們實現一個函數，會用來從用戶的輸入中讀取一個字符串，並且統計用戶輸入所用的時間。這個函數沒有參數，在返回用戶輸入的同時，返回所用的時間，我們用一個組對(pair)將這兩個數進行返回：

   ```c++
   static pair<string, seconds> get_input()
   {
   	string s;
   ```

6. 我們需要從用戶開始輸入時計時，記錄一個時間點的方式可以寫成如下方式：

   ```c++
   	const auto tic (chrono::steady_clock::now());
   ```

7. 現在可以來獲取用戶的輸入了。當我們沒有獲取成功，將會返回一個默認的元組對象。這個元組對象中的元素都是空：

   ```c++
       if (!(cin >> s)) {
       	return { {}, {} };
       }
   ```

8. 成功獲取輸入後，我們會打上下一個時間戳。然後，返回用戶的輸入和輸入所用的時間。注意這裡獲取的都是絕對的時間戳，通過計算這兩個時間戳的差，我們得到了打印所用的時間：

   ```c++
       const auto toc (chrono::steady_clock::now());
       
   	return {s, toc - tic};
   } 
   ```

9. 現在讓我們來實現主函數，使用一個循環獲取用戶的輸入，直到用戶輸入正確的字符串為止。在每次循環中，我們都會讓用戶輸入"C++17"，然後調用`get_input`函數：

   ```c++
   int main()
   {
       while (true) {
       	cout << "Please type the word \"C++17\" as"
       			" fast as you can.\n> ";
           
       	const auto [user_input, diff] = get_input();
   ```

10. 然後對輸入進行檢查。當輸入為空，程序會終止：

   ```c++
   		if (user_input == "") { break; }
   ```

11. 當用戶正確的輸入"C++17"，我們將會對用戶表示祝賀，然後返回其輸入所用時間。`diff.count()`函數會以浮點數的方式返回輸入所用的時間。當我們使用STL原始的`seconds`時間類型時，將會得到一個已舍入的整數，而不是一個小數。通過使用以毫秒和微秒為單位的計時，我們將獲得對應單位的計數，然後通過相應的轉換方式進行時間單位轉換：

    ```c++
            if (user_input == "C++17") {
                cout << "Bravo. You did it in:\n"
                    << fixed << setprecision(2)
                    << setw(12) << diff.count()
                    << " seconds.\n"
                    << setw(12) << milliseconds(diff).count()
                    << " milliseconds.\n"
                    << setw(12) << microseconds(diff).count()
                    << " microseconds.\n";
                break;
    ```

12. 如果用戶輸入有誤時，我們會提示用戶繼續輸入：

    ```c++
            } else {
                cout << "Sorry, your input does not match."
               			" You may try again.\n";
            }
        }
    }
    ```

13. 編譯並運行程序，就會得到如下的輸出。第一次輸入時，會有一個錯誤，程序會讓我們重新進行輸入。在正確輸入之後，我們就會得到輸入所花費的時間：

    ```c++
    $ ./ratio_conversion
    Please type the word "C++17" as fast as you can.
    > c+17
    Sorry, your input does not match. You may try again.
    Please type the word "C++17" as fast as you can.
    > C++17
    Bravo. You did it in: 
            2.82 seconds.
         2817.95 milliseconds.
      2817948.40 microseconds.
    ```

## How it works...

本節中對不同時間單位進行轉換是，我們需要先選擇三個可用的時鐘對象的一個。其分別為`system_clock`，`steady_clock`和`high_resolution_clock`，這三個時鐘對象都在`std::chrono`命名空間中。他們有什麼區別呢？讓我們來看一下：

| 時鐘類型                                                     | 特性                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [system_clock](https://zh.cppreference.com/w/cpp/chrono/system_clock) | 表示系統級別的實時掛鐘。想要獲取本地時間的話，這是個正確的選擇。 |
| [steady_clock](https://zh.cppreference.com/w/cpp/chrono/steady_clock) | 表示單調型的時間。這個時間是不可能倒退的，而時間倒退可能會在其他時鐘上發生，比如：其最小精度不同，或是在冬令時和夏令時交替時。 |
| [high_resolution_clock](https://zh.cppreference.com/w/cpp/chrono/high_resolution_clock) | STL中可統計最細粒度時鐘週期的時鐘。                          |

當我們要衡量時間的“距離”，或者計算兩個時間點的絕對間隔。即便時鐘是112年，5小時，10分鐘，1秒(或其他)之後或之前的時間，這都不影響兩個時間點間的相對距離。這裡我們唯一關注的就是打的兩個時間點`toc`和`tic`，時鐘需要是微秒級別的(許多系統都使用這樣的時鐘)，因為不同的時鐘對於我們的測量有一定的影響。對於這樣的需求，`steady_clock`無疑是最佳的選擇。其能根據處理器的時間戳計數器進行實現，只要該時鐘開始計數(系統開始運行)就不會停止。

OK，現在來對合適的時間對象進行選擇，可以通過`chrono::steady_clock::now()`對時間點進行保存。`now`函數會返回一個`chrono::time_point<chrono::steady_clock>`類的值。兩個點之間的差就是所用時間間隔，或`chrono::duration`類型的時間長度。這個類型是本節的核心類型，其看起來有點複雜。讓我們來看一下`duration`模板類的簽名：

```c++
template<
    class Rep,
    class Period = std::ratio<1>
> class duration;
```

我們需要改變的參數類為`Rep`和`Period`。`Rep`很容易解釋：其只是一個數值類型用來保存時間點的值。對於已經存在的STL時間單位，都為`long long int`型。本節中，我們選擇了`double`。因為我們的選擇，保存的時間描述也可以轉換為毫秒或微秒。當`chrono::seconds`類型記錄的時間為1.2345秒時，其會舍入成一個整數秒數。這樣，我們就能使用`chrono::microseconds`來保存`tic`和`toc`之間的時間，並且將其轉化為粒度更加大的時間。正因為選擇`double`作為`Rep`傳入，可以對計時的精度在丟失較少精度的情況下，進行向上或向下的調整。

對於我們的計時單位，我們採取了`Rep = double`方式，所以會在`Period`上有不同的選擇：

```c++
using seconds = chrono::duration<double>;
using milliseconds = chrono::duration<double,
	ratio_multiply<seconds::period, milli>>;
using microseconds = chrono::duration<double,
	ratio_multiply<seconds::period, micro>>;
```

`seconds`是最簡單的時間單位，其為`Period = ratio<1>`，其他的時間單位就只能進行轉換。1毫秒是千分之一秒，所以我們將使用`milli`特化的`seconds::period`轉化為秒時，就要使用`std::ratio<1, 1000>`類型(`std::ratio<a, b>`表示分數值a/b)。`ratio_multiply`類型是一個編譯時函數，其表示對應類型的結果是多個`ratio`值累加。

可能這看起來非常複雜，那就讓我們來看一個例子吧：`ratio_multiply<ratio<2, 3>, ratio<4, 5>>`的結果為`ratio<8, 15>`，因為`(2/3) * (4/5) = 8/15`。

我們結果類型定義等價情況如下：

```c++
using seconds = chrono::duration<double, ratio<1, 1>>;
using milliseconds = chrono::duration<double, ratio<1, 1000>>;
using microseconds = chrono::duration<double, ratio<1, 1000000>>;
```

上面列出的類型，很容易的就能進行轉換。當我們具有一個時間間隔`d`，其類型為`seconds`，我們就能將其轉換成`milliseconds`。轉換隻需要通過構造函數就能完成——`milliseconds(d)`。

## There's more...

其他教程和書籍中，你可以會看到使用`duration_cast`的方式對時間進行轉換。當我們具有一個時間間隔類`chrono::milliseconds`和要轉換成的類型`chrono::hours`時，就需要轉換為`duration_cast<chrono::hours>(milliseconds_value)`，因為這些時間單位都是整型。從一個細粒度的時間單位，轉換成一個粗粒度的時間單位，將會帶來時間精度的損失，這也是為什麼我們使用`duration_cast`的原因。基於`double`和`float`的時間間隔類型不需要進行強制轉換。