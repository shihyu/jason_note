# std::unordered_map中使用自定義類型

當我們使用`std::unordered_map`代替`std::map`時，對於鍵的選擇要從另一個角度出發。`std::map`要求鍵的類型可以排序。因此，元素可以進行排序。不過，當我們使用數學中的向量作為鍵呢？這樣一來就沒有判斷哪個向量大於另一個向量，比如向量(0, 1)和(1, 0)無法相比較，因為它們指向的方向不同。在`std::unordered_map`中這都不是問題，因為不需要對鍵的哈希值進行排序。對於我們來說只要為類型實現一個哈希函數和等同`==`操作符的實現，等同操作符的是實現是為了判斷兩個對象是否完全相同。本節中，我們就來實驗一下這個例子。

## How to do it...

本節中，我們要定義一個簡單的`coord`數據結構，其沒有默認哈希函數，所以我們必須要自行定義一個。然後我們會使用`coord`對象來對應一些值。

1. 包含使用`std::unordered_map`所必須的頭文件

   ```c++
   #include <iostream>
   #include <unordered_map> 
   ```

2. 自定義數據結構，這是一個簡單的數據結構，還不具備對應的哈希函數：

   ```c++
   struct coord {
   	int x;
   	int y;
   };
   ```

3. 實現哈希函數是為了能讓類型作為鍵存在，這裡先實現比較操作函數：

   ```c++
   bool operator==(const coord &l, const coord &r)
   {
   	return l.x == r.x && l.y == r.y;
   }
   ```

4. 為了使用STL哈希的能力，我們打開了std命名空間，並且創建了一個特化的`std::hash`模板。其使用`using`將特化類型進行別名。

   ```c++
   namespace std
   {
   template <>
   struct hash<coord>
   {
       using argument_type = coord;
       using result_type = size_t;
   ```

5. 下面要重載該類型的括號表達式。我們只是為`coord`結構體添加數字，這是一個不太理想的哈希方式，不過這裡只是展示如何去實現這個函數。一個好的散列函數會盡可能的將值均勻的分佈在整個取值範圍內，以減少哈希碰撞。

   ```c++
       result_type operator()(const argument_type &c) const
       {
           return static_cast<result_type>(c.x)
          		   + static_cast<result_type>(c.y);
       }
   };
   }
   ```

6. 我們現在可以創建一個新的`std::unordered_map`實例，其能結構`coord`結構體作為鍵，並且對應任意值。例子中對`std::unordered_map`使用自定義的類型來說，已經很不錯了。讓我們基於哈希進行實例化，並填充自定義類型的`map`表，並打印這個`map`表：

   ```c++
   int main()
   {
       std::unordered_map<coord, int> m { 
           { {0, 0}, 1}, 
           { {0, 1}, 2},
           { {2, 1}, 3}
       };
       for (const auto & [key, value] : m) {
           std::cout << "{(" << key.x << ", " << key.y
       			 << "): " << value << "} ";
       }
       std::cout << '\n';
   }
   ```

7. 編譯運行這個例子，就能看到如下的打印信息：

   ```
   $ ./custom_type_unordered_map
   {(2, 1): 3} {(0, 1): 2} {(0, 0): 1}
   ```

## How it works...

通常實例化一個基於哈希的map表(比如: `std::unordered_map`)時，我們會這樣寫：

```c++
std::unordered_map<key_type, value_type> my_unordered_map;
```

編譯器為我們創建特化的`std::unordered_map`時，這句話背後隱藏了大量的操作。所以，讓我們來看一下其完整的模板類型聲明：

```c++
template<
    class Key,
    class T,
    class Hash = std::hash<Key>,
    class KeyEqual = std::equal_to<Key>,
    class Allocator = std::allocator< std::pair<const Key, T> >
> class unordered_map;
```

這裡第一個和第二個模板類型，我麼填寫的是`coord`和`int`。另外的三個模板類型是選填的，其會使用已有的標準模板類。這裡前兩個參數需要我們給定對應的類型。

對於這個例子，`class Hash`模板參數是最有趣的一個：當我們不顯式定義任何東西時，其就指向`std::hash<key_type>`。STL已經具有`std::hash`的多種特化類型，比如`std::hash<std::string>`、`std::hash<int>`、`std::hash<unique_ptr>`等等。這些類型中可以選擇最優的一種類型類解決對應的問題。

不過，STL不知道如何計算我們自定義類型`coord`的哈希值。所以我們要使用我們定義的類型對哈希模板進行特化。編譯器會從`std::hash`特化列表中，找到我們所實現的類型，也就是將自定義類型作為鍵的類型。

如果新特化一個`std::hash<coord>`類型，並且將其命名成my_hash_type，我們可以使用下面的語句來實例化這個類型：

```c++
std::unordered_map<coord, value_type, my_hash_type> my_unordered_map;
```

這樣命名就很直觀，可讀性好，而且編譯器也能從哈希實現列表中找到與之對應的正確的類型。