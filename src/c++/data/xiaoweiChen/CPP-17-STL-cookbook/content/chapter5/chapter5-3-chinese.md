# 從容器中刪除指定元素

複製、轉換和過濾是對一段數據常做的操作。本節，我們將重點放在過濾元素上。

將過濾出的元素從數據結構中移除，或是簡單的移除其中一個，但對於不同數據結構來說，操作上就完全不一樣了。在鏈表中(比如`std::list`)，只要將對應節點的指針進行變動就好。不過，對於連續存儲的結構體來說(比如`std::vector`，`std::array`，還有部分`std::deque`)，刪除相應的元素時，將會有其他元素來替代刪除元素的位置。當一個元素槽空出來後，那麼後面所有的元素都要進行移動，來將這個空槽填滿。這個聽起來都很麻煩，不過本節中我們只是想要從字符串中移除空格，這個功能沒有太多的工作量。

當我們定義了一個結構體時，我們是不會考慮如何將其元素進行刪除的。當需要做這件事的時候，我們才會注意到。STL中的`std::remove`和`std::remove_if`函數可以給我們提供幫助。

## How to do it...

我們將通過不同的方式將`vector`中的元素進行刪除：

1. 包含必要的頭文件，並聲明所使用的命名空間。

   ``` c++
   #include <iostream>
   #include <vector>
   #include <algorithm>
   #include <iterator>

   using namespace std;
   ```

2. 一個簡單的打印輔助函數，用來打印`vector`中的內容：

   ```c++
   void print(const vector<int> &v)
   {
       copy(begin(v), end(v), ostream_iterator<int>{cout, ", "});
       cout << '\n';
   }
   ```

3. 我們將使用簡單的整數對`vector`進行實例化。然後，對`vector`進行打印，這樣就能和後面的結果進行對比：

   ```c++
   int main()
   {
       vector<int> v {1, 2, 3, 4, 5, 6};
       print(v);
   ```

4. 現在，我們移除`vector`中所有的2。`std::remove`將2值移動到其他位置，這樣這個值相當於消失了。因為`vector`長度在移除元素後變短了，`std::remove`將會返回一個迭代器，這個迭代器指向新的末尾處。舊的`end`迭代器所指向的地方，實際上就沒有什麼意義了，所以我們可以告訴`vector`將這個位置進行擦除。我們使用兩行代碼來完成這個任務：

   ```c++
       {
           const auto new_end (remove(begin(v), end(v), 2));
           v.erase(new_end, end(v));
       }
       print(v);
   ```

5. 現在，我們來移除奇數。為了完成移除，我們需要實現一個謂詞函數，這個函數用來告訴程序哪些值是奇數，然後結合`std::remove_if`來使用。

   ```c++
       {
           auto odd_number ([](int i) { return i % 2 != 0; });
           const auto new_end (
           	remove_if(begin(v), end(v), odd_number));
           v.erase(new_end, end(v));
       }
       print(v);
   ```

6. 下一個嘗試的算法是`std::replace`。我們使用這個函數將所有4替換成123。與`std::replace`函數對應，`std::replace_if`也存在於STL中，同樣可以接受謂詞函數：

   ```c++
       replace(begin(v), end(v), 4, 123);
       print(v);
   ```

7. 讓我們重新初始化`vector`，併為接下來的實驗創建兩個空的`vector`：

   ```c++
       v = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
       
   	vector<int> v2;
       vector<int> v3;
   ```

8. 然後，我們實現兩個判讀奇偶數的謂詞函數：

   ```c++
   	auto odd_number ([](int i) { return i % 2 != 0; });
   	auto even_number ([](int i) { return i % 2 == 0; });
   ```

9. 接下來的兩行做的事情完全相同。其將偶數拷貝到v2和v3中。第一行使用`std::remove_copy_if`函數，當相應數值不滿足謂詞條件時，函數會從源容器中拷貝到另一個容器中。第二行`std::copy_if`則是拷貝滿足謂詞條件的元素。

   ```c++
       remove_copy_if(begin(v), end(v),
       	back_inserter(v2), odd_number);
       copy_if(begin(v), end(v),
       	back_inserter(v3), even_number); 
   ```

10. 然後，打印這兩個`vector`，其內容應該是完全相同的。

    ```c++
        print(v2);
        print(v3);
    }
    ```

11. 編譯運行程序。第一行輸出的是`vector`初始化的值。第二行是移除2之後的內容。接下來一行是移除所有奇數後的結果。第4行是將4替換為123的結果。最後兩行則是v2和v3中的內容：

    ```c++
    $ ./removing_items_from_containers
    1, 2, 3, 4, 5, 6,
    1, 3, 4, 5, 6,
    4, 6,
    123, 6,
    2, 4, 6, 8, 10,
    2, 4, 6, 8, 10,
    ```

## How it works...

這裡我們使用了很多與排序算法相關的函數：

| 算法函數                                                     | 作用                                                         |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| [std::remove](https://zh.cppreference.com/w/cpp/algorithm/remove) | 接受一個容器範圍和一個具體的值作為參數，並且移除對應的值。返回一個新的end迭代器，用於修改容器的範圍。 |
| [std::replace](https://zh.cppreference.com/w/cpp/algorithm/replace) | 接受一個容器範圍和兩個值作為參數，將使用第二個數值替換所有與第一個數值相同的值。 |
| [std::remove_copy](https://zh.cppreference.com/w/cpp/algorithm/remove_copy) | 接受一個容器範圍，一個輸出迭代器和一個值作為參數。並且將所有不滿足條件的元素拷貝到輸出迭代器的容器中。 |
| [std::replace_copy](https://zh.cppreference.com/w/cpp/algorithm/replace_copy) | 與`std::replace`功能類似，但與`std::remove_copy`更類似些。源容器的範圍並沒有變化。 |
| [std::copy_if](https://zh.cppreference.com/w/cpp/algorithm/copy) | 與`std::copy`功能相同，可以多接受一個謂詞函數作為是否進行拷貝的依據。 |

> Note:
>
> 表中沒有if的算法函數，都有一個*_if版本存在，其能接受謂詞函數，通過謂詞函數判斷的結果來進行相應的操作。

