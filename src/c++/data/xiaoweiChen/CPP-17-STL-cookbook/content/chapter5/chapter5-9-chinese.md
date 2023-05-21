# 生成輸入序列的序列

當測試代碼需要處理參數順序不重要的輸入序列時，有必要測試它是否對所有可能的輸入產生相同的輸出。當你自己實現了一個排序算法時，就要寫這樣的測試代碼來確定自己的實現是否正確。

`std::next_permutation`在任何時候都能幫我們將序列進行打亂。我們在可修改的範圍中可以調用它，其會將以字典序進行置換。

## How to do it...

本節，我們將從標準輸入中讀取多個字符串，然後使用`std::next_permutation`生成已排序的序列，並且打印這個序列：

1. 首先，包含必要的頭文件，並聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <vector>
   #include <string>
   #include <iterator>
   #include <algorithm>
   
   using namespace std; 
   ```

2. 使用標準數組對`vector`進行初始化，接下來對`vector`進行排序：

   ```c++
   int main()
   {
       vector<string> v {istream_iterator<string>{cin}, {}};
       sort(begin(v), end(v));
   ```

3. 現在來打印`vector`中的內容。隨後，調用`std::next_permutation`，其會打亂已經排序的`vector`，再對其進行打印。直到`next_permutation`返回false時，代表`next_permutation`完成了其操作，循環結束：

   ```c++
       do {
           copy(begin(v), end(v),
           	ostream_iterator<string>{cout, ", "});
           cout << '\n';
       } while (next_permutation(begin(v), end(v)));
   }
   ```

4. 編譯運行這個程序，會有如下的打印：

   ```c++
   $ echo "a b c" | ./input_permutations
   a, b, c,
   a, c, b,
   b, a, c,
   b, c, a,
   c, a, b,
   c, b, a,
   ```

## How it works...

`std::next_permutation`算法使用起來有點奇怪。因為這個函數接受一組開始/結束迭代器，當其找到下一個置換時返回true；否則，返回false。不過“下一個置換”又是什麼意思呢？

當`std::next_permutation`算法找到元素中的下一個字典序時，其會以如下方式工作：

1. 通過`v[i - 1] < v[i]`的方式找到最大索引i。如果這個最大索引不存在，那麼返回false。
2. 再找到最大所以j，這裡j需要大於等於i，並且`v[j] > v[i - 1]`。
3. 將位於索引位置j和i - 1上的值進行交換。
4. 將從i到範圍末尾的元素進行反向。
5. 返回true。

每次單獨的置換順序，都會在同一個序列中呈現。為了看到所有置換的可能，我們先對數組進行了排序。如果我們輸入“c b a”到算法中，算法會立即終止，因為每個元素都以反字典序排列。



