# 保持對std::vector實例的排序

`array`和`vector`不會對他們所承載的對象進行排序。有時我們去需要排序，但這不代表著我們總是要去切換數據結構，需要排序能夠自動完成。在我們的例子有如有一個`std::vector`實例，將添加元素後的實例依舊保持排序，會是一項十分有用的功能。

## How to do it...

本節中我們使用隨機單詞對`std::vector`進行填充，然後對它進行排序。並在插入更多的單詞的同時，保證`vector`實例中單詞的整體排序。

1. 先包含必要的頭文件。

   ```c++
   #include <iostream>
   #include <vector>
   #include <string>
   #include <algorithm>
   #include <iterator>
   #include <cassert>
   ```

2. 聲明所要使用的命名空間。

   ```c++
   using namespace std;
   ```

3. 完成主函數，使用一些隨機單詞填充`vector`實例。

   ```c++
   int main()
   {
       vector<string> v {"some", "random", "words",
                         "without", "order", "aaa",
                         "yyy"};
   ```

4. 對vector實例進行排序。我們使用一些斷言語句和STL中自帶的`is_sorted`函數對是否排序進行檢查。

   ```c++
       assert(false == is_sorted(begin(v), end(v)));
       sort(begin(v), end(v));
       assert(true == is_sorted(begin(v), end(v)));
   ```

5. 這裡我們使用`insert_sorted`函數添加隨機單詞到已排序的`vector`中，這個函數我們會在後面實現。這些新插入的單詞應該在正確的位置上，並且`vector`實例需要保持已排序的狀態。

   ```c++
       insert_sorted(v, "foobar");
       insert_sorted(v, "zzz");
   ```

6. 現在，我們來實現`insert_sorted`函數。

   ```c++
   void insert_sorted(vector<string> &v, const string &word)
   {
       const auto insert_pos (lower_bound(begin(v), end(v), word));
       v.insert(insert_pos, word);
   }
   ```

7. 回到主函數中，我們將`vector`實例中的元素進行打印。

   ```c++
       for (const auto &w : v) {
       	cout << w << " ";
       }
       cout << '\n';
   }	
   ```

8. 編譯並運行後，我們得到如下已排序的輸出。

   ```c++
   aaa foobar order random some without words yyy zzz
   ```

## How it works...

程序整個過程都是圍繞`insert_sorted`展開，這也就是本節所要說明的：對於任意的新字符串，通過計算其所在位置，然後進行插入，從而保證`vector`整體的排序性。不過，這裡我們假設的情況是，在插入之前，`vector`已經排序。否則，這種方法無法工作。

這裡我們使用STL中的`lower_bound`對新單詞進行定位，其可接收三個參數。頭兩個參數是容器開始和結尾的迭代器。這確定了我們單詞`vector`的範圍。第三個參數是一個單詞，也就是要被插入的那個。函數將會找到大於或等於第三個參數的首個位置，然後返回指向這個位置的迭代器。

獲取了正確的位置，那就使用`vector`的成員函數`insert`將對應的單詞插入到正確的位置上。

## There's more...

`insert_sorted`函數很通用。如果需要其適應不同類型的參數，這樣改函數就能處理其他容器所承載的類型，甚至是容器的類似，比如`std::set`、`std::deque`、`std::list`等等。(這裡需要注意的是成員函數`lower_bound`與 `std::lower_bound`等價，不過成員函數的方式會更加高效，因為其只用於對應的數據集合)

```c++
template <typename C, typename T>
void insert_sorted(C &v, const T &item)
{
    const auto insert_pos (lower_bound(begin(v), end(v), item));
    v.insert(insert_pos, item);
}
```

當我們要將`std::vector`類型轉換為其他類型時，需要注意的是並不是所有容器都支持`std::sort`。該函數所對應的算法需要容器為可隨機訪問容器，例如`std::list`就無法進行排序。