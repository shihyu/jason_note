# 容器間相互複製元素

大多數STL數據結構都支持迭代器。這就意味著大多數數據結構能夠通過成員函數`begin()`和`end()`成員函數得到相應的迭代器，並能對數據進行迭代。迭代的過程看起來是相同的，無論是什麼樣的數據結構都是一樣的。

我們可以對`vector`，`list`，`deque`，`map`等等數據結構進行迭代。我們甚至可以使用迭代器作為文件/標準輸入輸出的出入口。此外，如之前章節介紹，我們能將迭代器接口放入算法中。這樣的話，我們可以使用迭代器訪問任何元素，並且可以將迭代器作為STL算法的參數傳入，對特定範圍內的數據進行處理。

`std::copy`算法可以很好的展示迭代器是如何將不同的數據結構進行抽象，而後將一個容器的數據拷貝到另一個容器。類似這樣的算法就與數據結構的類型完全沒有關係了。為了證明這點，我們會把玩一下`std::copy`。

## How to do it...

本節中，我們將對不同的變量使用`std::copy`。

1. 首先，包含必要的頭文件，並聲明所用到的命名空間。

   ```c++
   #include <iostream>
   #include <vector>
   #include <map>
   #include <string>
   #include <tuple>
   #include <iterator>
   #include <algorithm>
   
   using namespace std;
   ```

2. 我們將使用整型和字符串值進行組對。為了能很好的將其進行打印，我們將會重載`<<`流操作：

   ```c++
   namespace std {
   ostream& operator<<(ostream &os, const pair<int, string> &p)
   {
   	return os << "(" << p.first << ", " << p.second << ")";
   }
   }
   ```

3. 主函數中，我們將使用整型-字符串對填充一個`vector`。並且我們聲明一個`map`變量，其用來關聯整型值和字符串值：

   ```c++
   int main()
   {
       vector<pair<int, string>> v {
           {1, "one"}, {2, "two"}, {3, "three"},
           {4, "four"}, {5, "five"}};
       
       map<int, string> m;
   ```

4. 現在將`vector`中的前幾個整型字符串對使用`std::copy_n`拷貝到`map`中。因為`vector`和`map`是兩種完全不同的結構體，我們需要對`vector`中的數據進行變換，這裡就要使用到`insert_iterator`適配器。`std::inserter`函數為我們提供了一個適配器。在算法中使用類似`std::copy_n`的算法時，需要與插入迭代器相結合，這是一種更加通用拷貝/插入元素的方式(從一種數據結構到另一種數據結構)，但這種方式不是最快的。使用指定數據結構的成員函數插入元素無疑是更加高效的方式：

   ```c++
   	copy_n(begin(v), 3, inserter(m, begin(m)));
   ```

5. 讓我們打印一下`map`中的內容。縱觀本書，我們會經常使用`std::copy`函數來打印容器的內容。`std::ostream_iterator`在這裡很有用，因為其可以將用戶的標準輸出作為另一個容器，而後將要輸出的內容拷貝過去：

   ```c++
       auto shell_it (ostream_iterator<pair<int, string>>{cout,
       ", "});
       
   	copy(begin(m), end(m), shell_it);
       cout << '\n';
   ```

6. 對`map`進行清理，然後進行下一步的實驗。這次，我們會將`vector`的元素*移動*到`map`中，並且是所有元素：

   ```c++
       m.clear();
       
   	move(begin(v), end(v), inserter(m, begin(m)));
   ```

7. 我們將再次打印`map`中的內容。此外，`std::move`是一種改變數據源的算法，這次我們也會打印`vector`。這樣，我們就會看到算法時如何對數據源進行的移動：

   ```c++
       copy(begin(m), end(m), shell_it);
       cout << '\n';
       
   	copy(begin(v), end(v), shell_it);
       cout << '\n';
   }
   ```

8. 編譯運行這個程序，看看會發生什麼。第一二行非常簡單，其反應的就是`copy_n`和`move`算法執行過後的結果。第三行比較有趣，因為移動算法將其源搬移到`map`中，所以這時的`vector`是空的。在重新分配空間前，我們通常不應該訪問成為移動源的項。但是為了這個實驗，我們忽略它：

   ```c++
   $ ./copying_items
   (1, one), (2, two), (3, three),
   (1, one), (2, two), (3, three), (4, four), (5, five),
   (1, ), (2, ), (3, ), (4, ), (5, ),
   ```

## How it works...

`std::copy`是STL中最簡單的算法之一，其實現也非常短。我們可以看一下等價實現：

```c++
template <typename InputIterator, typename OutputIterator>
OutputIterator copy(InputIterator it, InputIterator end_it,
OutputIterator out_it)
{
    for (; it != end_it; ++it, ++out_it) {
    	*out_it = *it;
    }
    return out_it;
}
```

這段代碼很樸素，使用`for`循環將一個容器中的元素一個個的拷貝到另一個容器中。此時，有人就可能會發問："使用`for`循環的實現非常簡單，並且還不用返回值。為什麼要在標準庫實現這樣的算法？"，這是個不錯的問題。

`std::copy`並非能讓代碼大幅度減少的一個實現，很多其他的算法實現其實非常複雜。這種實現其實在代碼層面並不明顯，但STL算法更多的在於做了很多底層優化，編譯器會選擇最優的方式執行算法，這些底層的東西目前還不需要去了解。

STL算法也讓能避免讓開發者在代碼的可讀性和優化性上做權衡。

> Note：
>
> 如果類型只有一個或多個(使用`class`或`struct`包裝)的矢量類型或是類，那麼其拷貝賦值通常是輕量的，所以可以使用`memcopy`或`memmove`進行賦值操作，而不要使用自定義的賦值操作符進行操作。

這裡，我們也使用了`std::move`。其和`std::copy`一樣優秀，不過`std::move(*it)`會將循環中的源迭代器，從局部值(左值)轉換為引用值(右值)。這個函數就會告訴編譯器，直接進行移動賦值操作來代替拷貝賦值操作。對於大多數複雜的對象，這會讓程序的性能更好，但會破壞原始對象。

