# 實現詞頻計數器——std::map

`std::map`在收集和統計數據方面非常有用，通過建立鍵值關係，將可修改的對象映射到對應鍵上，可以很容易的實現一個詞頻計數器。

## How to do it...

本節中，我們將從標準輸入中獲取用戶的輸入，或是從記錄一部小說的文本文件。我們會去標記輸入單詞，並統計一共有多少個單詞。

1. 包含必要的頭文件。

   ```c++
   #include <iostream>
   #include <map>
   #include <vector>
   #include <algorithm>
   #include <iomanip>
   ```

2. 聲明所使用的命名空間。

   ```c++
   using namespace std;
   ```

3. 我們將使用一個輔助函數，對輸入中的符號進行處理。

   ```c++
   string filter_punctuation(const string &s)
   {
       const char *forbidden {".,:; "};
       const auto idx_start (s.find_first_not_of(forbidden));
       const auto idx_end (s.find_last_not_of(forbidden));
       return s.substr(idx_start, idx_end - idx_start + 1);
   }
   ```

4. 現在，我們來實現真正要工作的部分。使用`map`表對輸入的每個單詞進行統計。另外，使用一個變量來保存目前為止看到的最長單詞的長度。程序的最後，我們將打印這個`map`表。

   ```c++
   int main()
   {
       map<string, size_t> words;
       int max_word_len {0};
   ```

5. 將標準輸入導入`std::string`變量中，標準輸入由空格隔開。通過如下方法獲取輸入單詞。

   ```c++
       string s;
       while (cin >> s) {
   ```

6. 我們獲得的單詞可能包含標點符號，因為這些符號可能緊跟在單詞後面。使用輔助函數將標點符號去除。

   ```c++
   		auto filtered (filter_punctuation(s));
   ```

7. 如果當前處理的單詞是目前處理最長的單詞，我們會更新`max_word_len`變量。

   ```c++
   		max_word_len = max<int>(max_word_len, filtered.length());
   ```

8. 然後，我們將增加該詞在`words map`中的頻率。如果是首次處理該單詞，那麼將會隱式創建一個鍵值對，然後插入`map`，之後再進行自加操作。

   ```c++
       	++words[filtered];
       }	
   ```

9. 當循環結束時，`words map`會保存所有輸入單詞的頻率。`map`中單詞作為鍵，並且鍵以字母序排列。我們想要以頻率多少進行排序，詞頻最高的排第一位。為了達到這樣的效果，首先實現一個`vector`，將所有鍵值對放入這個`vector`中。

   ```c++
       vector<pair<string, size_t>> word_counts;
       word_counts.reserve(words.size());
       move(begin(words), end(words), back_inserter(word_counts));
   ```

10. 然後，`vector`中將將具有`words map`中的所有元素。然後，我們來進行排序，把詞頻最高的單詞排在最開始，最低的放在最後。

   ```c++
       sort(begin(word_counts), end(word_counts),
           [](const auto &a, const auto &b) {
           return a.second > b.second;
           });
   ```

11. 現在所有元素如我們想要的順序排列，之後將這些數據打印在用戶的終端上。使用`std::setw`流控制器，可以格式化輸出相應的內容。

    ```c++
        cout << "# " << setw(max_word_len) << "<WORD>" << " #<COUNT>\n";
        for (const auto & [word, count] : word_counts) {
            cout << setw(max_word_len + 2) << word << " #"
            	 << count << '\n';
        }
    }
    ```

12. 編譯後運行，我們就會得到一個詞頻表：

    ```c++
    $ cat lorem_ipsum.txt | ./word_frequency_counter
    # <WORD> #<COUNT>
    et #574
    dolor #302
    sed #273
    diam #273
    sit #259
    ipsum #259
    ...
    ```

## How it works...

本節中，我們使用`std::map`實例進行單詞統計，然後將`map`中的所有元素放入`vector`中，然後進行排序，再打印輸出。為什麼要這麼做？

先看一個例子。當我們要從`a a b c b b b d c c`字符串中統計詞頻時，我們的`map`內容如下：

```
a -> 2
b -> 4
c -> 3
d -> 1
```

不過，這是未排序的，這不是我們想要給用戶展示的排序。我們的程序要首先輸出b的頻率，因為b的頻率最高。然後是c，a，d。不幸的是，我們無法要求`map`使用鍵所對應的值進行排序。

這就需要`vector`幫忙了，將`map`中的鍵值對放入`vector`中。這個方法明確的將這些元素從`map`中刪除了。

```c++
vector<pair<string, size_t>> word_counts;
```

然後，我們使用`std::move`函數將詞-頻對應關係填充整個`vector`。這樣的好處是讓單詞不會重複，不過這樣會將元素從`map`中完全刪除。使用`move`方法，減少了很多不必要的拷貝。

```c++
move(begin(words), end(words), back_inserter(word_counts));
```

> Note
>
> 一些STL的實現使用短字符優化——當所要處理的字符串過長，這種方法將無需再在堆上分配內存，並且可以將字符串直接進行存儲。在這個例子中，移動雖然不是最快的方式，但也不會慢多少。

接下來比較有趣的就是排序操作，其使用了一個Lambda表達式作為自定義比較謂詞：

```c++
sort(begin(word_counts), end(word_counts),
	[](const auto &a, const auto &b) { return a.second > b.second; });
```

排序算法將會成對的處理元素，比較兩個元素。通過提供的Lambda函數，`sort`方法將不會再使用默認比較謂詞，其會將`a.second`和`b.second`進行比較。這裡的鍵值對中，第二個值為詞頻數，所以可以使用`.second`得到對應詞頻數。通過這種方式，將移動所有高頻率的詞到`vector`的開始，並且將低頻率詞放在末尾。

