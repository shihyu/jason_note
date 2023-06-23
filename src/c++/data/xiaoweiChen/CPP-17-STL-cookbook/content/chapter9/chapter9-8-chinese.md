# 將執行的程序推到後臺——std::async

當我們想要將一些可以執行的代碼放在後臺，可以用線程將這段程序運行起來。然後，我們就等待運行的結果就好：

```c++
std::thread t {my_function, arg1, arg2, ...};
// do something else
t.join(); // wait for thread to finish
```

這裡`t.join()`並不會給我們`my_function`函數的返回值。為了獲取返回值，需要先實現`my_function`函數，然後將其返回值存儲到主線程能訪問到的地方。如果這樣的情況經常發生，我們就要重複的寫很多代碼。

C++11之後，`std::async`能幫我們完成這項任務。我們將寫一個簡單的程序，並使用異步函數，讓線程在同一時間內做很多事情。`std::async`其實很強大，讓我們先來瞭解其一方面。

## How to do it...

我們將在一個程序中併發進行多個不同事情，不顯式創建線程，這次使用`std::async`和`std::future`：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <map>
   #include <string>
   #include <algorithm>
   #include <iterator>
   #include <future>
   
   using namespace std;
   ```

2. 實現了三個函數，算是完成些很有趣的任務。第一個函數能夠接收一個字符串，並且創建一個對於字符串中的字符進行統計的直方圖：

   ```c++
   static map<char, size_t> histogram(const string &s)
   {
       map<char, size_t> m;
       
       for (char c : s) { m[c] += 1; }
       
       return m;
   }
   ```

3. 第二個函數也能接收一個字符串，並返回一個排序後的副本：

   ```c++
   static string sorted(string s)
   {
       sort(begin(s), end(s));
       return s;
   }
   ```

4. 第三個函數會對傳入的字符串中元音字母進行計數：

   ```c++
   static bool is_vowel(char c)
   {
       char vowels[] {"aeiou"};
       return end(vowels) !=
       		find(begin(vowels), end(vowels), c);
   }
   
   static size_t vowels(const string &s)
   {
   	return count_if(begin(s), end(s), is_vowel);
   }
   ```

5. 主函數中，我們從標準輸入中獲取字符串。為了不讓輸入字符串分段，我們禁用了`ios::skipws`。這樣就能得到一個很長的字符串，並且不管這個字符串中有多少個空格。我們會對結果字符串使用`pop_back`，因為這種方式會讓一個字符串中包含太多的終止符：

   ```c++
   int main()
   {
       cin.unsetf(ios::skipws);
       string input {istream_iterator<char>{cin}, {}};
       input.pop_back();
   ```

6. 為了獲取函數的返回值，並加快對輸入字符串的處理速度，我們使用了異步的方式。`std::async`函數能夠接收一個策略和一個函數，以及函數對應的參數。我們對於這個三個函數均使用`launch::async`策略。並且，三個函數的輸入參數是完全相同的：

   ```c++
   	auto hist (async(launch::async,
       				histogram, input));
       auto sorted_str (async(launch::async,
       				sorted, input));
       auto vowel_count (async(launch::async,
       				vowels, input));
   ```

7. `async`的調用會立即返回，因為其並沒有執行我們的函數。另外，準備好同步的結構體，用來獲取函數所返回的結果。目前的結果使用不同的線程併發的進行計算。此時，我們可以做其他事情，之後再來獲取函數的返回值。`hist`，`sorted_str`和`vowel_count`分別為函數`histogram`，`sorted` 和`vowels`的返回值，不過其會通過`std::async`包裝入`future`類型中。這個對象表示在未來某個時間點上，對象將會獲取返回值。通過對`future`對象使用`.get()`，我們將會阻塞主函數，直到相應的值返回，然後再進行打印：

   ```c++
       for (const auto &[c, count] : hist.get()) {
       	cout << c << ": " << count << '\n';
       }
   
       cout << "Sorted string: "
           << quoted(sorted_str.get()) << '\n'
           << "Total vowels: "
           << vowel_count.get() << '\n';
   }
   ```

8. 編譯並運行代碼，就能得到如下的輸出。我們使用一個簡短的字符串的例子時，代碼並不是真正的在並行，但這個例子中，我們能確保代碼是併發的。另外，程序的結構與串行版本相比，並沒有改變多少：

    ```c++
    $ echo "foo bar baz foobazinga" | ./async
     : 3
    a: 4
    b: 3
    f: 2
    g: 1
    i: 1
    n: 1
    o: 4
    r: 1
    z: 2
    Sorted string: "   aaaabbbffginoooorzz"
    Total vowels: 9
    ```

## How it works...

如果你沒有使用過`std::async`，那麼代碼可以簡單的寫成串行代碼：

```c++
auto hist (histogram(input));
auto sorted_str (sorted( input));
auto vowel_count (vowels( input));

for (const auto &[c, count] : hist) {
  cout << c << ": " << count << '\n';
}
cout << "Sorted string: " << quoted(sorted_str) << '\n';
cout << "Total vowels: " << vowel_count << '\n';
```

下面的代碼，則是並行的版本。我們將三個函數使用`async(launch::async, ...)`進行包裝。這樣三個函數都不會由主函數來完成。此外，`async`會啟動新線程，並讓線程併發的完成這幾個函數。這樣我們只需要啟動一個線程的開銷，就能將對應的工作放在後臺進行，而後可以繼續執行其他代碼：

```c++
auto hist (async(launch::async, histogram, input));
auto sorted_str (async(launch::async, sorted, input));
auto vowel_count (async(launch::async, vowels, input));

for (const auto &[c, count] : hist.get()) {
	cout << c << ": " << count << '\n';
}

cout << "Sorted string: "
    << quoted(sorted_str.get()) << '\n'
    << "Total vowels: "
    << vowel_count.get() << '\n';
```

例如`histogram`函數則會返回一個`map`實例，`async(..., histogram, ...)`將返回給我們的`map`實例包裝進之前就準備好的`future`對象中。`future`對象時一種空的佔位符，直到線程執行完函數返回時，才有具體的值。結果`map`將會返回到`future`對象中，所以我們可以對對象進行訪問。`get`函數能讓我們得到被包裝起來的結果。

讓我們來看一個更加簡單的例子。看一下下面的代碼：

```c++
auto x (f(1, 2, 3));
cout << x;
```

與之前的代碼相比，我們也可以以下面的方式完成代碼：

```c++
auto x (async(launch::async, f, 1, 2, 3));
cout << x.get();
```

這都是最基本的。後臺執行的方式可能要比標準C++出現還要早。當然，還有一個問題要解決：`launch::async`是什麼東西？` launch::async`是一個用來定義執行策略的標識。其有兩種獨立方式和一種組合方式：

| 策略選擇                                                     | 意義                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [launch::async](http://zh.cppreference.com/w/cpp/thread/launch) | 運行新線程，以異步執行任務                                   |
| [launch::deferred](http://zh.cppreference.com/w/cpp/thread/launch) | 在調用線程上執行任務(惰性求值)。在對`future`調用`get`和`wait`的時候，才進行執行。如果什麼都沒有發生，那麼執行函數就沒有運行。 |
| launch::async \| launch::deferred                            | 具有兩種策略共同的特性，STL的`async`實現可以的選擇策略。當沒有提供策略時，這種策略就作為默認的選擇。 |

> Note：
>
> 不使用策略參數調用`async(f, 1, 2, 3)`，我們將會選擇都是用的策略。`async`的實現可以自由的選擇策略。這也就意味著，我們不能確定任務會執行在一個新的線程上，還是執行在當前線程上。

## There's more...

還有件事情我們必須要知道，假設我們寫瞭如下的代碼：

```c++
async(launch::async, f);
async(launch::async, g);
```

這就會讓`f`和`g`函數併發執行(這個例子中，我們並不關心其返回值)。運行這段代碼時，代碼會阻塞在這兩個調用上，這並不是我們想看到的情況。

所以，為什麼會阻塞呢？`async`不是非阻塞式、異步的調用嗎？沒錯，不過這裡有點特殊：當對一個`async`使用`launch::async`策略時，獲取一個`future`對象，之後其析構函數將會以阻塞式等待方式運行。

這也就意味著，這兩次調用阻塞的原因就是，`future`生命週期只有一行的時間！我們可以以獲取其返回值的方式，來避免這個問題，從而讓`future`對象的生命週期更長。