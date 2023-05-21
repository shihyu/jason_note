# 在有序和無序的vector中查找元素

通常，需要確定某種元素在某個容器範圍內是否存在。如果存在，我們會對這個值進行修改，或者訪問與其相關的值。

查找元素的目的是不同的。當想要讓在一段已排序的元素中進行查找，可以使用二分查找法，這種方法要比線性查找快的多。如果沒有排序，那麼就只能進行線性遍歷來查找對應的值。

傳統的STL查找算法我們都可以使用，所以瞭解一下這些算法。本節將會使用兩個不同的算法，線性查找算法`std::find`，二分查找算法`std::equal_range`。

## How to do it...

本節，我們將對一個比較小的數據集進行線性和二分查找：

1. 包含必要的頭文件，以及聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <vector>
   #include <list>
   #include <algorithm>
   #include <string>
   
   using namespace std;
   ```

2. 數據集會包含`city`結構體，只是存儲的城市的名字和人口數量：

   ```c++
   struct city {
       string name;
       unsigned population;
   };	
   ```

3. 搜索算法需要將元素與目標對象進行對比，所以我們需要重載`city`結構體的`==`操作符：

   ```c++
   bool operator==(const city &a, const city &b) {
   	return a.name == b.name && a.population == b.population;
   }
   ```

4. 我們也需要將`city`實例進行打印，所以我們對其輸出操作符`<<`也進行了重載：

   ```c++
   ostream& operator<<(ostream &os, const city &city) {
       return os << "{" << city.name << ", "
       	<< city.population << "}";
   }
   ```

5. 查找函數通常會返回迭代器。當函數找到相應的元素時，會返回指向其的迭代器，否則就會返回容器的`end`迭代器。第二種情況下，我們就不能對該迭代器進行訪問。因為要打印輸出結果，所以需要實現一個函數，這個函數會返回另一個函數對象，並會將數據結構的`end`迭代器進行包裝。當要對結果進行打印時，會與容器的`end`迭代器相比較，如果不是`end`，那麼打印出查找到的值；如果是`end`，則僅打印`<end>`：

   ```c++
   template <typename C>
   static auto opt_print (const C &container)
   {
       return [end_it (end(container))] (const auto &item) {
           if (item != end_it) {
           	cout << *item << '\n';
           } else {
           	cout << "<end>\n";
           }
       };
   }
   ```

6. 我們使用德國的一些城市對`vector`進行實例化：

   ```c++
   int main()
   {
       const vector<city> c {
           {"Aachen", 246000},
           {"Berlin", 3502000},
           {"Braunschweig", 251000},
           {"Cologne", 1060000}
       };
   ```

7. 使用這個輔助函數構造一個城市打印函數，其會獲取到城市`vector`容器的`end`迭代器`c`：

   ```c++
   	auto print_city (opt_print(c));
   ```

8. 使用`std::find`在`vector`中找到相應的元素——科隆(Cologne)。因為可以直接獲得這個元素，所以這個搜索看起來毫無意義。不過，在查找之前並不知道這個元素在`vector`中的位置，而`find`函數告訴我們這個元素的具體位置。我們也可以寫一個循環，僅對城市名進行比較，而無需比較人口數量。不過，這是個不是很好的設計。下一步，我們將做另外一個實驗：

   ```c++
       {
           auto found_cologne (find(begin(c), end(c),
           	city{"Cologne", 1060000}));
           print_city(found_cologne);
       }
   ```

9. 當不需要知道對應城市的人口數量時，就不需要使用`==`操作符，只需要比較城市名稱就好。`std::find_if`函數可以接受一個函數對象作為謂詞函數。這樣，就能只使用城市名來查找“科隆”了：

   ```c++
       {
           auto found_cologne (find_if(begin(c), end(c),
           	[] (const auto &item) {
           	return item.name == "Cologne";
           	}));
           print_city(found_cologne);
       }
   ```

10. 為了讓搜索更加優雅，可以實現謂詞構建器。`population_higher_than`函數對象能接受一個人口數量，並且返回人口數量比這個數量多的城市。在這個小數據集中找一下多於2百萬人口的城市。例子中，只有柏林(Berlin)符合條件：

   ```c++
   {
       auto population_more_than ([](unsigned i) {
           return [=] (const city &item) {
           	return item.population > i;
           };
       });
       auto found_large (find_if(begin(c), end(c),
       	population_more_than(2000000)));
       print_city(found_large);
   }
   ```

11. 使用的查找函數，線性的遍歷容器，查找的時間複雜度為O(n)。STL也有二分查找函數，其時間複雜度為O(log(n))。讓我們生成一個新的數據集，其包含了一些整數，並構建了另一個`print`函數:

    ```c++
        const vector<int> v {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
        
        auto print_int (opt_print(v));
    ```

12. `std::binary_search`函數會返回一個布爾值，這個布爾值會告訴你函數是否找到了相應的元素，但是不會將指向元素的迭代器返回。二分查找需要查找的列表是已排序的，否則二分查找將出錯：

    ```c++
    	bool contains_7 {binary_search(begin(v), end(v), 7)};
    	cout << contains_7 << '\n';
    ```

13. 如果需要獲得查找的元素，就需要使用其他STL函數。其中之一就是`std::equal_range`。其不會返回對應元素的迭代器給我們，不過會返回一組迭代器。第一個迭代器是指向第一個不小於給定值的元素。第二個迭代器指向第一個大於給定值的元素。我們的範圍為數字1到10，那麼第一個迭代器將指向7，因為其是第一個不小於7的元素。第二個迭代器指向8，因為其實第一個大於7的元素：

    ```c++
    	auto [lower_it, upper_it] (
    		equal_range(begin(v), end(v), 7));
    	print_int(lower_it);
    	print_int(upper_it); 
    ```

14. 當需要其中一個迭代器，可以使用`std::lower_bound`或`std::upper_bound`。`lower_bound`函數只會返回第一個迭代器，而`upper_bound`則會返回第二個迭代器：

    ```c++
    	print_int(lower_bound(begin(v), end(v), 7));
    	print_int(upper_bound(begin(v), end(v), 7));
    }
    ```

15. 編譯並運行這個程序，我們看到如下輸出：

    ```c++
    $ ./finding_items
    {Cologne, 1060000}
    {Cologne, 1060000}
    {Berlin, 3502000}
    1
    7
    8
    7
    8
    ```

## How it works...

本節使用的STL查找算法：

| 算法函數                                                     | 作用                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [std::find](https://zh.cppreference.com/w/cpp/algorithm/find) | 可將一個搜索範圍和一個值作為參數。函數將返回找到的第一個值的迭代器。線性查找。 |
| [std::find_if](https://zh.cppreference.com/w/cpp/algorithm/find) | 與`std::find`原理類似，不過其使用謂詞函數替換比較值。        |
| [std::binary_search](https://zh.cppreference.com/w/cpp/algorithm/binary_search) | 可將一個搜索範圍和一個值作為參數。執行二分查找，當找到對應元素時，返回true；否則，返回false。 |
| [std::lower_bound](https://zh.cppreference.com/w/cpp/algorithm/lower_bound) | 可將一個查找返回和一個值作為參數，並且執行二分查找，返回第一個不小於給定值元素的迭代器。 |
| [std::upper_bound](https://zh.cppreference.com/w/cpp/algorithm/upper_bound) | 與`std::lower_bound`類似，不過會返回第一個大於給定值元素的迭代器。 |
| [std::equal_range](https://zh.cppreference.com/w/cpp/algorithm/equal_range) | 可將一個搜索範圍和一個值作為參數，並且返回一對迭代器。其第一個迭代器和`std::lower_bound`返回結果一樣，第二個迭代器和`std::upper_bound`返回結果一樣。 |

所有這些函數，都能接受一個自定義的比較函數作為可選參數傳入。這樣就可以自定義的進行查找，就如我們在本章做的那樣。

來看一下`std::equal_range`是如何工作的。假設我們有一個`vector`，` v = {0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 8}`，並且調用`equal_range(begin(v), end(v), 7);`，為了執行對7的二分查找。如`equal_range`要返回一對上下限迭代器那樣，這個結果將返回一段區域`{7, 7, 7}`，因為原始`vector`中有很多7，所以這個子隊列中也有很多7。下圖能說明其運行的原理：

![](../../images/chapter5/5-5-1.png)

首先，`equal_range`會使用典型的二分查找，直到其找到那個不小於查找值的那個元素。而後，另一個迭代器也是用同樣的方式找到。如同分開調用`lower_bound`和`upper_bound`一樣。

為了獲得一個二分查找函數，並返回其第一個適配條件的元素。我們可以按照如下的方式實現：

```c++
template <typename Iterator, typename T>
Iterator standard_binary_search(Iterator it, Iterator end_it, T value)
{
    const auto potential_match (lower_bound(it, end_it, value));
    if (potential_match != end_it && value == *potential_match) {
    	return potential_match;
    }
    return end_it;
}
```

這個函數使用`std::lower_bound`，為的就是找到第一個不大於`value`的元素。返回結果`potential_match`，有三種情況：

- 沒有值不小於`value`。這樣，返回值和`end_it`(`end`迭代器)一樣。
- 遇到的第一個不小於`value`的元素，同時也大於`value`。因此需要返回`end_it`，表示沒有找到相應的值。
- `potential_match`指向的元素與`value`相同。這個匹配沒毛病。因此就返回相應的迭代器。

當類型T沒有`==`操作符時，需要為二分查找提供一個`<`操作實現。然後，可以將比較重寫為`!(value < *potential_match) && !(*potential_match < value)`。如果它們不小於，也不大於，那麼必定等於。

STL中因為缺少對多次命中的“定義”，所以並沒有提供相應的函數來適配多次命中。

> Note：
>
> 需要留意`std::map`和`std::set`等數據結構，它們有自己的`find`函數。它們攜帶的`find`函數要比通用的算法快很多，因為他們的實現與數據結構強耦合。