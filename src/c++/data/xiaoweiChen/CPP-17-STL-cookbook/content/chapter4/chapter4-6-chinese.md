# 使用std::accumulate和Lambda函數實現transform_if

大多數用過`std::copy_if`和`std::transform`的開發者可能曾經疑惑過，為什麼標準庫裡面沒有`std::transform_if`。`std::copy_if`會將源範圍內符合謂詞判斷的元素挑出來，不符合條件的元素忽略。而`std::transform`會無條件的將源範圍內所有元素進行變換，然後放到目標範圍內。這裡的變換謂詞是由用戶提供的一個函數，這個函數不會太複雜，比如乘以多個數或將元素完全變換成另一種類型。

這兩個函數很早就存在了，不過到現在還是沒有`std::transform_if`函數。本節就來實現這個函數。看起來實現這個函數並不難，可以通過謂詞將對應的元素選擇出來，然後將這些挑選出來的元素進行變換。不過，我們會利用這個機會更加深入的瞭解Lambda表達式。

## How to do it...

我們將來實現我們的`transform_if`函數，其將會和`std::accumulate`一起工作。

1. 包含必要的頭文件。

   ```c++
   #include <iostream>
   #include <iterator>
   #include <numeric>
   ```

2. 首先，我們來實現一個`map`函數。其能接受一個轉換函數作為參數，然後返回一個函數對象，這個函數對象將會和`std::accumulate`一起工作。

   ```c++
   template <typename T>
   auto map(T fn)
   {
   ```

3. 當傳入一個遞減函數時，我們會返回一個函數對象，當這個函數對象調用遞減函數時，其會返回另一個函數對象，這個函數對象可以接受一個累加器和一個輸入參數。遞減函數會在累加器中進行調用，並且`fn`將會對輸入變量進行變換。如果這裡看起來比較複雜的話，我們將在後面進行詳細的解析：

   ```c++
       return [=] (auto reduce_fn) {
           return [=] (auto accum, auto input) {
           	return reduce_fn(accum, fn(input));
           };
       };
   }
   ```

4. 現在，讓我們來實現一個`filter`函數。其和`map`的工作原理一樣，不過其不會對輸入進行修改(`map`中會對輸入進行變換)。另外，我們接受一個謂詞函數，並且在不接受謂詞函數的情況下，跳過輸入變量，而非減少輸入變量：

   ```c++
   template <typename T>
   auto filter(T predicate)
   {
   ```

5. 兩個Lambda表達式與`map`函數具有相同的函數簽名。其不同點在於`input`參數是否進行過操作。謂詞函數用來區分我們是否對輸入調用`reduce_fn`函數，或者直接調用累加器而不進行任何修改：

   ```c++
       return [=] (auto reduce_fn) {
           return [=] (auto accum, auto input) {
               if (predicate(input)) {
               	return reduce_fn(accum, input);
               } else {
               	return accum;
               }
           };
       };
   }
   ```

6. 現在讓我們使用這些輔助函數。我們實例化迭代器，我們會從標準輸入中獲取整數值：

   ```c++
   int main()
   {
       std::istream_iterator<int> it {std::cin};
       std::istream_iterator<int> end_it;
   ```

7. 然後，我們會調用謂詞函數`even`，當傳入一個偶數時，這個函數會返回true。變換函數`twice`會對輸入整數做乘2處理：

   ```c++
       auto even ([](int i) { return i % 2 == 0; });
       auto twice ([](int i) { return i * 2; });
   ```

8. `std::accumulate`函數會將所對應範圍內的數值進行累加。累加默認就是通過`+`操作符將範圍內的值進行相加。我們想要提供自己的累加函數，也就是我們不想只對值進行累加。我們會將迭代器`it`進行解引用，獲得其對應的值，之後對再對其進行處理：

   ```c++
       auto copy_and_advance ([](auto it, auto input) {
           *it = input;
           return ++it;
       });
   ```

9. 我們現在將之前零零散散的實現拼組在一起。我們對標準輸入進行迭代，通過輸出迭代器`ostream_iterator`將對應的值輸出在終端上。 `copy_and_advance`函數對象將會接收用戶輸入的整型值，之後使用輸出迭代器進行輸出。將值賦值給輸出迭代器，將會使打印變得高效。不過，我們只會將偶數挑出來，然後對其進行乘法操作。為了達到這個目的，我們將`copy_and_advance`函數包裝入`even`過濾器中，再包裝入`twice`引射器中：

   ```c++
       std::accumulate(it, end_it,
           std::ostream_iterator<int>{std::cout, ", "},
           filter(even)(
               map(twice)(
               	copy_and_advance
               )
           ));
       std::cout << '\n';
   }
   ```

10. 編譯並運行程序，我們將得到如下的輸出。奇數都被拋棄了，只有偶數做了乘2運算：

    ```c++
    $ echo "1 2 3 4 5 6" | ./transform_if
    4, 8, 12,
    ```

## How it works...

本節看起來還是很複雜的，因為我們使用了很多嵌套Lambda表達式。為了跟清晰的瞭解它們是如何工作的，我們先了解一下`std::accumulate`的內部工作原理。下面的實現類似一個標準函數的實現：

```c++
template <typename T, typename F>
T accumulate(InputIterator first, InputIterator last, T init, F f)
{
    for (; first != last; ++first) {
    	init = f(init, *first);
    }
    return init;
}
```

函數參數f在這起到主要作用，所有值都會累加到用戶提供的`init`變量上。通常情況下，迭代器範圍將會傳入一組數字，類似`0, 1, 2, 3, 4 `，並且`init`的值為0。函數`f`只是一個二元函數，其會計算兩個數的加和。

例子中循環將會將所有值累加到`init`上，也就類似於`init += (((0 + 1) + 2) + 3) + 4 `。這樣看起來`std::accumulate`就是一個通用的摺疊函數。摺疊範圍意味著，將二值操作應用於累加器變量和迭代範圍內的每一個值(累加完一個數，再累加下一個數)。這個函數很通用，可以用它做很多事情，就比如實現`std::transform_if`函數！`f`函數也會遞減函數中進行調用。

`transform_if`的一種很直接的實現，類似如下代碼：

```c++
template <typename InputIterator, typename OutputIterator, typename P, typename Transform>
OutputIterator transform_if(InputIterator first, InputIterator last,OutputIterator out,P predicate, Transform trans)
{
    for (; first != last; ++first) {
        if (predicate(*first)) {
            *out = trans(*first);
            ++out;
        }
    }
    return out;
}
```

這個實現看起來和`std::accumulate`的實現很類似，這裡的`out`參數可以看作為`init`變量，並且使用函數`f`替換`if`。

我們確實做到了。我們構建了`if`代碼塊，並且將二元函數對象作為一個參數提供給了`std::accumulate`：

```c++
auto copy_and_advance ([](auto it, auto input) {
    *it = input;
    return ++it;
});
```

`std::accumulate`會將`init`值作為二元函數`it`的參數傳入，第二個參數則是當前迭代器所指向的數據。我們提供了一個輸出迭代器作為`init`參數。這樣`std::accumulate`就不會做累加，而是將其迭代的內容轉發到另一個範圍內。這就意味著，我們只需要重新實現`std::copy`就可以了。

通過`copy_and_advance`函數對象，使用我們提供的謂詞，將過濾後的結果傳入另一個使用謂詞的函數對象：

```c++
template <typename T>
auto filter(T predicate)
{
    return [=] (auto reduce_fn) {
        return [=] (auto accum, auto input) {
            if (predicate(input)) {
            	return reduce_fn(accum, input);
            } else {
            	return accum;
            }
        };
    };
}
```

構建過程看上去沒那麼簡單，不過先來看一下`if`代碼塊。當`predicate`函數返回true時，其將返回`reduce_fn`函數處理後的結果，也就是`accum`變量。這個實現省略了使用過濾器的操作。`if`代碼塊位於Lambda表達式的內部，其具有和`copy_and_advance`一樣的函數簽名，這使它成為一個合適的替代品。

現在我們就要進行過濾，但不進行變換。這個操作有`map`輔助函數完成：

```c++
template <typename T>
auto map(T fn)
{
    return [=] (auto reduce_fn) {
        return [=] (auto accum, auto input) {
        	return reduce_fn(accum, fn(input));
        };
    };
}
```

這段代碼看起來就簡單多了。其內部有一個還有一個Lambda表達式，該表達式的函數簽名與`copy_and_advance`，所以可以替代`copy_and_advance`。這個實現僅轉發輸入變量，不過會通過二元函數對`fn`的調用，對參數進行量化。

之後，當我們使用這些輔助函數時，我們可以寫成如下的表達式：

```c++
filter(even)(
    map(twice)(
    	copy_and_advance
    )
)
```

`filter(even)`將會捕獲`even`謂詞，並且返回給我們一個函數，其為一個包裝了另一個二元函數的二元函數，被包裝的那個二元函數則是進行過濾的函數。`map(twice)`函數做了相同的事情，`twice`變換函數，將`copy_and_advance`包裝入另一個二元函數中，那另一個二元函數則是對參數進行變換的函數。

雖然沒有任何的優化，但我們的代碼還是非常的複雜。為了讓函數之間能一起工作，我們對函數進行了多層嵌套。不過，這對於編譯器來說不是一件很難的事情，並且能對所有代碼進行優化。程序最後的結果要比實現`transform_if`簡單很多。這裡我們沒有多花一分錢，就獲得了非常好的函數模組。這裡我們就像堆樂高積木一樣，可將`even`謂詞和`twice`轉換函數相結合在一起。

