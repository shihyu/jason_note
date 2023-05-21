# 壓縮和解壓縮字符串

壓縮問題在編程面試中出現的相對較多。就是使用一個函數將`aaaaabbbbbbbccc`字符串轉換成一個短字符串`a5b7c3`。`a5`表示原始字符串中有5個a，`b7`表示原始字符串中有7個b。這就一個相對簡單的壓縮算法。對於普通的文本，並不需要使用這個算法，因為文本中重複的東西很少，不需要進行壓縮。不過，這套算法就算沒有計算機，我們也能很容易的對其進行實現。如果代碼在一開始沒有進行很好的設計，那麼就很容易出現bug。雖然，處理字符串並不是一件很困難的事情，但是代碼中大量使用C風格的字符串時，很有可能遇到緩衝區溢出的bug。

本節讓我們使用STL來對字符壓縮和解壓進行實現。

## How to do it...

本節，我們將對字符串實現簡單的`compress`和`decompress`函數：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <string>
   #include <algorithm>
   #include <sstream>
   #include <tuple>
   
   using namespace std;
   ```

2. 對於我們的壓縮算法，我們會嘗試去找到文本中連續相同的字符，並且對他們進行單獨的進行壓縮處理。當我們拿到一個字符串，我們需要知道與第一個字符不同的字符在哪裡。這裡使用`std::find`來尋找與第一個位置上的元素不同的元素位置。先將起始位置的字符賦予`c`。經過查找後就會返回一個迭代器，其指向第一個不同的元素。兩個不同字符間的距離，會放到元組中返回：

   ```c++
   template <typename It>
   tuple<It, char, size_t> occurrences(It it, It end_it)
   {
       if (it == end_it) { return {it, '?', 0}; }
       
       const char c {*it};
       const auto diff (find_if(it, end_it,
       			    [c](char x) { return c != x; }));
       
       return {diff, c, distance(it, diff)};
   }
   ```

3. `compress`會連續的對`occurrences`函數進行調用。這樣，就能從同一個字符組，跳轉到另一個。`r << c << n`行表示將字符`c`推入到輸出流中，並且將`occurrences`函數的調用次數作為結果字符串的一部分。最後會返回一個字符串對象，就包含了壓縮過的字符串：

   ```c++
   string compress(const string &s)
   {
       const auto end_it (end(s));
       stringstream r;
       
       for (auto it (begin(s)); it != end_it;) {
       	const auto [next_diff, c, n] (occurrences(it, end_it));
       	r << c << n;
       	it = next_diff;
       }
       
       return r.str();
   }
   ```

4. `decompress`的原理也不復雜，但會更簡短。其會持續的從輸入流中獲取字符，字符串包括字符和數字。對於這兩種值，函數會構造一個字符串用於解壓所獲取到的字符串。最後，會再次返回一個字符串。順帶一提，這裡的`decompress`函數是不安全的。其很容易被破解。我們會在後面來看下這個問題：

   ```c++
   string decompress(const string &s)
   {
       stringstream ss{s};
       stringstream r;
       
       char c;
       size_t n;
       
       while (ss >> c >> n) { r << string(n, c); }
       return r.str();
   }
   ```

5. 主函數中會構造一個簡單的字符串，裡面有很多重複的字符。打印壓縮過後，和解壓過後的字符串。最後，我們應該會得到原始的字符串：

   ```c++
   int main()
   {
       string s {"aaaaaaaaabbbbbbbbbccccccccccc"};
       cout << compress(s) << '\n';
       cout << decompress(compress(s)) << '\n';
   }
   ```

6. 編譯並運行程序，我們就會得到如下的輸出：

   ```c++
   $ ./compress
   a9b9c11
   aaaaaaaaabbbbbbbbbccccccccccc
   ```

## How it works...

這裡我們使用兩個函數`compress`和`decompress`來解決這個問題。

解壓函數這裡實現的十分簡單，因為其就包含一些變量的聲明，其主要工作的代碼其實只有一行：

```c++
while (ss >> c >> n) { r << string(n, c); }
```

其能持續將字符讀取到`c`當中，並且將數字變量讀取到`n`中，然後輸出到`r`中。`stringstream`類在這裡會隱藏對字符串解析的細節。當成功進行解壓後，解壓的字符串將輸入到字符流中，這也就是`decompress`最後的結果。如果`c = 'a'`並且`n = 5`，那麼`string(n, c)`的字符串為`aaaaa`。

壓縮函數比較複雜，我們為其編寫了一個小的輔助函數。這個輔助函數就是`occurences`。那麼我們就先來看一下`occurences`函數。下面的圖展示了`occurences`函數工作的方式：

![](../../images/chapter6/6-9-1.png)

`occurences`函數能夠接受兩個參數：指向字符序列起始點的迭代器和末尾點的迭代器。使用`find_if`能找到第一個與起始點字符不同的字符的位置，也就是圖中的`diff`迭代器的位置。起始位置與`diff`位置之間元素就與起始字符相同，圖中相同的字符有6個。在我們計算出這些信息後，`diff`迭代就可以在下次查詢時，進行重複利用。因此，我們將`diff`、子序列範圍和子序列範圍的長度包裝在一個元組中進行返回。

根據這些信息，我們就能在子序列之間切換，並且將結果推入到目標字符串中：

```c++
for (auto it (begin(s)); it != end_it;) {
    const auto [next_diff, c, n] (occurrences(it, end_it));
    r << c << n;
    it = next_diff;
}
```

## There's more...

還記得在第4步的時候，我們說過`decompress`不安全嗎？這個函數確實容易被利用。

試想我們傳入一個字符串：`a00000`。壓縮的第一個結果為`a1`因為其只包含了一個字母`a`。然後，對後面5個0進行處理，結果為`05`。然後將兩個結果合併，那麼結果就為`a105`。不幸的是，外部對這個字符串的解讀是“a連續出現了105次”。我們的輸入字符串並沒有什麼錯。這裡最糟糕的情況就是，我們將這個字符串進行了壓縮，然後我們通過輸入的六個字符得到了一個長度為105的字符串。試想當用戶得到了這樣的結果會不會感到憤怒？因為我們的算法並沒有準備好應對這樣的輸入。

為了避免這樣的事情發生，我們只能在`compress`函數中禁止數字的輸入，或者將數字使用其他的方式進行處理。之後，`decompress`算法需要加入一個條件，就是需要固定輸出字符串的最大長度。這個就當做作業，交由讀者自行完成。