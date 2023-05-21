# 在字符串中定位模式並選擇最佳實現——std::search

在一個字符串中查找另一個字符串，與在一個範圍內查找一個對象有些不同。首先，字符串是可迭代的對象。另一方面，從一個字符串中查詢另一個字符串，就意味著就是在一個範圍內查詢另一個範圍。所以在查找過程中，有多次的比較，所以我們需要其他算法參與。

`std::string`就包含`find`函數，其能實現我們想要的；不過，本節我們將使用`std::search`來完成這個任務。雖然，`std::search`在字符串中會大量的用到，不過很多種容器都能使用這個算法來完成查找任務。C++17之後，`std::search`添加了更多有趣的特性，並且其本身可使用簡單地交換搜索算法。這些算法都優化過，並且免費提供給開發者使用。另外，我們可以實現自己的搜索算法，並且可以將我們實現的算法插入`std::search`中。

## How to do it...

我們將對字符串使用新`std::search`函數，並且嘗試使用其不同的查找對象進行應用：

1. 首先，包含必要的頭文件，和聲明所要使用的命名空間。

   ```c++
   #include <iostream>
   #include <string>
   #include <algorithm>
   #include <iterator>
   #include <functional>

   using namespace std;
   ```

2. 我們將實現一個輔助函數，用於打印查找算法所範圍的位置，從而輸出子字符串。

   ```c++
   template <typename Itr>
   static void print(Itr it, size_t chars)
   {
       copy_n(it, chars, ostream_iterator<char>{cout});
       cout << '\n';
   }
   ```

3. 我們例子輸入的一個勒龐風格的字符串，其中包含我們要查找的字符串。本例中，這個需要查找的字符串為"elitr":

   ```c++
   int main()
   {
       const string long_string {
           "Lorem ipsum dolor sit amet, consetetur"
           " sadipscing elitr, sed diam nonumy eirmod"};
       const string needle {"elitr"};
   ```

4. 舊`std::search`接口接受一組`begin`和`end`迭代器，用於確定子字符串的查找範圍。這個接口會返回一個迭代器指向所查找到的子字符串。如果接口沒有找到對應的字符串，其將返回該範圍的`end`迭代器：

   ```c++
       {
           auto match (search(begin(long_string), end(long_string),
           				 begin(needle), end(needle)));
           print(match, 5);
       }
   ```

5. C++17版本的`std::search`將會使用一組`begin/end`迭代器和一個所要查找的對象。`std::default_searcher`能接受一組子字符串的`begin`和`end`迭代器，再在一個更大的字符串中，查找這個字符串：

   ```c++
       {
           auto match (search(begin(long_string), end(long_string),
           	default_searcher(begin(needle), end(needle))));
           print(match, 5);
       }
   ```

6. 這種改變就很容易切換搜索算法。`std::boyer_moore_searcher`使用Boyer-Moore查找算法進行快速的查找：

   ```c++
       {
           auto match (search(begin(long_string), end(long_string),
               boyer_moore_searcher(begin(needle), end(needle))));
           print(match, 5);
       }	
   ```

7. C++17標準中，有三種不同的搜索器對象實現。其中還有一種是Boyer-Moore-Horspool查找算法實現：

   ```c++
       {
           auto match (search(begin(long_string), end(long_string),
               boyer_moore_horspool_searcher(begin(needle),
               end(needle))));
           print(match, 5);
       }
   }
   ```

8. 我們編譯並運行這個程序。我們可以看到相同的字符串輸出：

   ```c++
   $ ./pattern_search_string
   elitr
   elitr
   elitr
   elitr
   ```

## How it works...

我們在`std::search`中使用了4種查找方式，得到了相同的結果。這幾種方式適用於哪種情況呢？

讓我們假設大字符串為`s`，要查找的部分為`p`。然後，調用`std::search(begin(s), end(s), begin(p), end(p));`和`std::search(begin(s), end(s), default_searcher(begin(p), end(p));`做相同的事情。

其他搜索方式將會以更復雜的方式實現：

- `std::default_searcher`：其會重定向到`std::search`的實現。
- `std::boyer_moore_searcher`：使用Boyer-Moore查找算法。
- `std::boyer_moore_horspool_searcher`：使用Boyer-Moore-Horspool查找算法。

為什麼會有這些特殊的算法呢？Boyer-Moore算法起源於一個特殊想法——查找部分與原始字符串進行比較，其始於查找字符串的尾部，並且從右到左查找。如果查找的字符多個位置不匹配，並且對應部分沒有出現，那麼就需要在整個字符串進行平移，然後在進行查找。下圖可能會看的更加明白一些。先來看一下第一步發生了什麼：因為算法已知所要匹配字符串的長度，所以需要對相應位置上的字符進行比較，然後在平移到下一個長度點進行比較。在圖中，這發生在第二步。這樣Boyer-Moore算法就能避免對不必要的字符進行比較。

![](../../images/chapter5/5-7-1.png)

當然，在我們沒有提供新的比較查找算法時，Boyer-Moore為默認的查找算法。其要比原先默認的算法快很多，不過其需要快速查找的數據結果進行支持，以判斷搜索字符是否存在於查找塊中，以及以多少為偏移進行定位。編譯器將選擇不同複雜度的算法實現，這取決於其所使用到的數據類型(對複雜類型的哈希映射和類型的原始查找表進行更改)。最後，默認的查找算法在查詢不是很長的字符串也是非常的快。如果需要查找算法提高性能，那麼Boyer-Moore將會是個不錯的選擇。

Boyer-Moore-Horspool為簡化版的Boyer-Moore算法。其丟棄了“壞字符”規則，當對應字符串沒有找到時，將會對整個查找塊進行偏移。需要權衡的是，這個算法要比Boyer-Moore算法慢，但是其不需要對那麼多特殊的數據結構進行操作。

> Note：
>
> 不要試圖嘗試比較哪種算法在哪種情況下更快。你可以使用自己實際的例子進行測試，並且基於你得到的結果進行討論。

