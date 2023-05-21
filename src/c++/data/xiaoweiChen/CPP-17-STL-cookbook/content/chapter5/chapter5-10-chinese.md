# 實現字典合併工具

假設我們有一個已經排序的列表，有人有另一個已排序的列表，我們想要將這兩個列表進行共享。那麼最好的方式就是將這兩個列表合併起來。我們需要合併後的列表也是有序的，這樣我們查找元素就會十分方便。

為了將兩個已排序列表中的元素進行合併，我們本能的會想需要創建一個新的列表來放置這兩個列表中的元素。對於要加入的元素，我們需要將隊列中的元素進行對比，然後找到最小的那個元素將其放到列表的最前面。不過，這樣輸出隊列的順序會被打亂。下面的圖就能很好的說明這個問題：

![](../../images/chapter5/5-10-1.png)

`std::merge`算法就可以直接來幫助我們做這個事情，這樣我們就無需過多的參與。本節我們將展示如何使用這個算法。

## How to do it...

我們將創建一個簡單的字典，其為英語單詞和德語單詞一對一的翻譯，之後將其存儲在`std::deque`數據結構中。程序將標註輸入中獲取這個字典，並且打印合並之後的字典。

1. 包含必要的頭文件，並聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <algorithm>
   #include <iterator>
   #include <deque>
   #include <tuple>
   #include <string>
   #include <fstream>
   
   using namespace std; 
   ```

2. 字典是一對字符串，兩兩對應：

   ```c++
   using dict_entry = pair<string, string>;
   ```

3. 我們將在屏幕上打印這個組對，並且要從用戶輸入中讀取這個組對，所以我們必須要重載`>>`和`<<`操作符：

   ```c++
   namespace std {
   ostream& operator<<(ostream &os, const dict_entry p)
   {
   	return os << p.first << " " << p.second;
   }
   istream& operator>>(istream &is, dict_entry &p)
   {
   	return is >> p.first >> p.second;
   }
   }
   ```

4. 這裡需要創建一個輔助函數，其能接受任何流對象作為輸入，幫助我們構建字典。其會構建一個`std::deque`來存放一對一的字符串對，並且其會讀取標準輸入中的所有字符。並在返回字典前，對字典進行排序：

   ```c++
   template <typename IS>
   deque<dict_entry> from_instream(IS &&is)
   {
       deque<dict_entry> d {istream_iterator<dict_entry>{is}, {}};
       sort(begin(d), end(d));
       return d;
   }
   ```

5. 這裡使用不同的輸入流，創建兩個不同的字典。其中一個是從`dict.txt`文件中讀取出的字符，我們先假設這個文件存在。其每一行為一個組對，另一個流就是標準輸入：

   ```c++
   int main()
   {
       const auto dict1 (from_instream(ifstream{"dict.txt"}));
       const auto dict2 (from_instream(cin));
   ```

6. 作為輔助函數`from_instream`將返回給我們一個已經排過序的字典，這樣我們就可以將兩個字典直接放入`std::merge`算法中。其能通過給定兩個的`begin`和`end`迭代器組確定輸入的範圍，並在最後給定輸出。這裡的輸出將會打印在用戶的屏幕上：

   ```c++
       merge(begin(dict1), end(dict1),
           begin(dict2), end(dict2),
           ostream_iterator<dict_entry>{cout, "\n"});
   }
   ```

7. 可以編譯這個程序，不過在運行之前，我們需要創建`dict.txt`文件，並且寫入如下內容：

   ```c++
   car auto
   cellphone handy
   house haus
   ```

8. 現在我們運行程序了，輸入一些英文單詞，將其翻譯為德文。這時的輸出仍舊是一個排序後的字典，其可以將輸入的所有單詞進行翻譯。

   ```c++
   $ echo "table tisch fish fisch dog hund" | ./dictionary_merge
   car auto
   cellphone handy
   dog hund
   fish fisch
   house haus
   table tisch
   ```

## How it works...

`std::meger`算法接受兩對`begin/end`迭代器，這兩對迭代器確定了輸入範圍。這兩對迭代器所提供的輸入範圍也必須是已排序的。第五個參數就是輸出容器的迭代器，其接受兩段範圍合併的元素。

其有一個變體`std::inplace_merge`。兩個算法幾乎一樣，不過這個變體只需要一對迭代器，並且沒有輸出，和其名字一樣，其會直接在輸入範圍上進行操作。比如對`{A, C, B, D}`這個序列來說，可以將第一個子序列定義為`{A, C}`，第二個子序列定義為`{B, D}`。使用`std::inplace_merge`算法將兩個序列進行合併，其結果為`{A, B, C, D}`。

