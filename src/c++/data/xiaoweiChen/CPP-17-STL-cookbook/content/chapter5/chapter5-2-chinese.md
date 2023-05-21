# 容器元素排序

排序是一項很常見的任務，並且可以通過各種各樣的方式進行。每個計算機科學專業的學生，都學過很多排序算法(包括這些算法的性能和穩定性)。

因為這是個已解決的問題，所以開發者沒必要浪費時間再次來解決排序問題，除非是出於學習的目的。

## How to do it...

本節中，我們將展示如何使用`std::sort`和`std::partial_sort`。

1. 首先，包含必要的頭文件和聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <algorithm>
   #include <vector>
   #include <iterator>
   #include <random>

   using namespace std;
   ```

2. 我們將打印整數在`vector`出現的次數，為了縮短任務代碼的長度，我們在這裡寫一個輔助函數：

   ```c++
   static void print(const vector<int> &v)
   {
       copy(begin(v), end(v), ostream_iterator<int>{cout, ", "});
       cout << '\n';
   }
   ```

3. 我們開始實例化一個`vector`：

   ```c++
   int main()
   {
   	vector<int> v {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
   ```

4. 因為我們將使用不同的排序函數將`vector`多次打亂，所以我們需要一個隨機數生成器：

   ```c++
   	random_device rd;
   	mt19937 g {rd()};
   ```

5. `std::is_sorted`函數會告訴我們，容器內部的值是否已經經過排序。所以這行將打印到屏幕上：

   ```c++
   	cout << is_sorted(begin(v), end(v)) << '\n';
   ```

6. `std::shuffle`將打亂`vector`中的內容，之後我們會再次對`vector`進行排序。前兩個參數是容器的首尾迭代器，第三個參數是一個隨機數生成器：

   ```c++
   	shuffle(begin(v), end(v), g);
   ```

7. 現在`is_sorted`函數將返回false，所以0將打印在屏幕上，`vector`的元素總量和具體數值都沒有變，不過順序發生了變化。我們會將函數的返回值再次打印在屏幕上：

   ```c++
   	cout << is_sorted(begin(v), end(v)) << '\n';
   	print(v);
   ```

8. 現在，在通過`std::sort`對`vector`進行排序。然後打印是否排序的結果：

   ```c++
   	sort(begin(v), end(v));
       
   	cout << is_sorted(begin(v), end(v)) << '\n';
       print(v);
   ```

9. 另一個比較有趣的函數是`std::partition`。有時候，並不需要對列表完全進行排序，只需要比它前面的某些值小就可以。所以，讓使用`partition`將數值小於5的元素排到前面，並打印它們：

   ```c++
       shuffle(begin(v), end(v), g);
       
   	partition(begin(v), end(v), [] (int i) { return i < 5; });
       
   	print(v); 
   ```

10. 下一個與排序相關的函數是`std::partial_sort`。我們可以使用這個函數對容器的內容進行排序，不過只是在某種程度上的排序。其會將`vector`中最小的N個數，放在容器的前半部分。其餘的留在`vector`的後半部分，不進行排序：

    ```c++
        shuffle(begin(v), end(v), g);
        auto middle (next(begin(v), int(v.size()) / 2));
        partial_sort(begin(v), middle, end(v));
        
    	print(v);
    ```

11. 當我們要對沒做比較操作符的結構體進行比較，該怎麼辦呢？讓我們來定義一個結構體，然後用這個結構體來實例化一個`vector`：

    ```c++
        struct mystruct {
        int a;
        int b;
        };

        vector<mystruct> mv { {5, 100}, {1, 50}, {-123, 1000},
        				   {3, 70}, {-10, 20} };
    ```

12. `std::sort`函數可以將比較函數作為第三個參數進行傳入。讓我們來使用它，並且傳遞一個比較函數。為了展示其實如何工作的，我們會對其第二個成員b進行比較。這樣，我們將按`mystruct::b`的順序進行排序，而非`mystruct::a`的順序：

    ```c++
        sort(begin(mv), end(mv),
        [] (const mystruct &lhs, const mystruct &rhs) {
            return lhs.b < rhs.b;
        });
    ```

13. 最後一步則是打印已經排序的`vector`：

    ```c++
        for (const auto &[a, b] : mv) {
        	cout << "{" << a << ", " << b << "} ";
        }
        cout << '\n';
    }
    ```

14. 編譯運行程序。第一個1是由`std::is_sorted`所返回的。之後將`vector`進行打亂後，`is_sorted`就返回0。第三行是打亂後的`vector`。下一個1是使用sort之後進行打印的。然後，`vector`會被再次打亂，並且使用`std::partition`對部分元素進行排序。我們可以看到所有比5小的元素都在左邊，比5大的都在右邊。我們暫且將現在的順序認為是亂序。倒數第二行展示了`std::partial_sort`的結果。前半部分的內容進行了嚴格的排序，而後半部分則沒有。最後一樣，我們將打印`mystruct`實例的結果。其結果是嚴格根據第二個成員變量的值進行排序的：

    ```c++
    $ ./sorting_containers
    1
    0
    7, 1, 4, 6, 8, 9, 5, 2, 3, 10,
    1
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    1, 2, 4, 3, 5, 7, 8, 10, 9, 6,
    1, 2, 3, 4, 5, 9, 8, 10, 7, 6,
    {-10, 20} {1, 50} {3, 70} {5, 100} {-123, 1000}
    ```

## How it works...

這裡我們使用了很多與排序算法相關的函數：

| 算法函數                                                     | 作用                                                         |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| [std::sort](https://zh.cppreference.com/w/cpp/algorithm/sort) | 接受一定範圍的元素，並對元素進行排序。                       |
| [std::is_sorted](https://zh.cppreference.com/w/cpp/algorithm/is_sorted) | 接受一定範圍的元素，並判斷該範圍的元素是否經過排序。         |
| [std::shuffle](https://zh.cppreference.com/w/cpp/algorithm/random_shuffle) | 類似於反排序函數；其接受一定範圍的元素，並打亂這些元素。     |
| [std::partial_sort](https://zh.cppreference.com/w/cpp/algorithm/partial_sort) | 接受一定範圍的元素和另一個迭代器，前兩個參數決定排序的範圍，後兩個參數決定不排序的範圍。 |
| [std::partition](https://zh.cppreference.com/w/cpp/algorithm/partition) | 能夠接受謂詞函數。所有元素都會在謂詞函數返回true時，被移動到範圍的前端。剩下的將放在範圍的後方。 |

對於沒有實現比較操作符的對象來說，想要排序就需要提供一個自定義的比較函數。其簽名為`bool function_name(const T &lhs, const T &rhs)`，並且在執行過程中無副作用。

當然排序還有其他類似`std::stable_sort`的函數，其能保證排序後元素的原始順序，`std::stable_partition`也有類似的功能。

> Note:
>
> `std::sort`對於排序有不同的實現。根據所提供的迭代器參數，其實現分為選擇排序、插入排序、合併排序，對於元素數量較少的容器可以完全進行優化。在使用者的角度，我們通常都不需要了解這些。