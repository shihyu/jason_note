# 高效的修改std::map元素的鍵值

在`std::map`數據結構中，鍵-值通常都對應存在，而且鍵通常是唯一併排序過的，而且鍵值一旦設定那麼就不允許用戶再進行修改。為了阻止用戶修改鍵，鍵的類型聲明使用了`const`。

這種限制是非常明智的，其可以保證用戶很難在使用`std::map`的時候出錯。不過，如果我們真的需要修改`map`的鍵值該怎麼辦呢？

C++17之前，因為對應的鍵已經存在，我們不得不將整個鍵-值對從樹中移除，然後再插入。這種方法的確定很明顯，其需要分配出一些不必要的內存，感覺上也會對性能有一定的影響。

從C++17起，我們無需重新分配內存，就可以刪除和重新插入map鍵值對。下面的內容中將會展示如何操作。

## How to do it...

我們使用`std::map`類型一個實現應用，用於確定車手在虛擬比賽中的排位。當車手在比賽中完成超越，那麼我們將使用C++17的新方法改變其鍵值。

1. 包含必要的頭文件和聲明使用的命名空間。

   ```c++
   #include <iostream>
   #include <map>
   
   using namespace std;
   ```

2. 我們會在修改map的時候打印之前和之後結果，所以這裡先實現了一個輔助函數。

   ```c++
   template <typename M>
   void print(const M &m)
   {
       cout << "Race placement:\n";
       for (const auto &[placement, driver] : m) {
      		cout << placement << ": " << driver << '\n';
       }
   }
   ```

3. 主函數中，我們實例化並初始化一個`map`，其鍵為整型，表示是當前的排位；值為字符型，表示駕駛員的姓名。我們在這裡先打印一下這個`map`，因為我們會在下一步對其進行修改。

   ```c++
   int main()
   {
       map<int, string> race_placement {
           {1, "Mario"}, {2, "Luigi"}, {3, "Bowser"},
           {4, "Peach"}, {5, "Yoshi"}, {6, "Koopa"},
           {7, "Toad"}, {8, "Donkey Kong Jr."}
       };
       print(race_placement);
   ```

4. 讓我來看下排位賽的某一圈的情況，Bowser因為賽車事故排在最後，Donkey Kong Jr. 從最後一名超到第三位。例子中首先要從`map`中提取節點，因為這是唯一能修改鍵值的方法。`extract`函數是C++17新加的特性。其可以從`map`中刪除元素，並沒有內存重分配的副作用。看下這裡是怎麼用的吧。

   ```c++
   {
       auto a(race_placement.extract(3));
       auto b(race_placement.extract(8)); 
   ```

5. 現在我們要交換Bowser和Donkey Kong Jr.的鍵。鍵通常都是無法修改的，不過我們可以通過`extract`方法來修改元素的鍵。

   ```c++
   	swap(a.key(), b.key());
   ```

6. `std::map`的`insert`函數在C++17中有一個新的重載版本，其接受已經提取出來的節點，就是為了在插入他們時，不會分配不必要的內存。

   ```c++
       race_placement.insert(move(a));
       race_placement.insert(move(b));
   }
   ```

7. 最後，我們打印一下目前的排位。

   ```c++
   	print(race_placement);
   }
   ```

8. 編譯並運行可以得到如下輸出。我們可以看到初始的排位和最後的排位。

   ```c++
   $ ./mapnode_key_modification
   Race placement:
   1: Mario
   2: Luigi
   3: Bowser
   4: Peach
   5: Yoshi
   6: Koopa
   7: Toad
   8: Donkey Kong Jr.
   Race placement:
   1: Mario
   2: Luigi
   3: Donkey Kong Jr.
   4: Peach
   5: Yoshi
   6: Koopa
   7: Toad
   8: Bowser
   ```

## How it works...

在C++17中，`std::map`有一個新成員函數`extract`。其有兩種形式：

```c++
node_type extract(const_iterator position);
node_type extract(const key_type& x)
```

在例子中，我們使用了第二個，能接受一個鍵值，然後找到這個鍵值，並提取對應的`map`節點。第一個函數接受一個迭代器，提取的速度會更快，應為給定了迭代器就不需要在查找。

當使用第二種方式去提取一個不存在的節點時，會返回一個空`node_type`實例。`empty()`成員函數會返回一個布爾值，用來表明`node_type`實例是否為空。以任何方式訪問一個空的實例都會產生未定義行為。

提取節點之後，我們要使用`key()`函數獲取要修改的鍵，這個函數會返回一個非常量的鍵。

需要注意的是，要將節點重新插會到`map`時，我們需要在`insert`中移動他們。因為`extract`可避免不必要的拷貝和內存分配。還有一點就是，移動一個`node_type`時，其不會讓容器的任何值發生移動。

## There's more...

使用`extract`方法提取的`map`節點實際上非常通用。我們可以從一個`map`實例中提取出來節點，然後插入到另一個`map`中，甚至可以插入到`multimap`實例中。這種方式在`unordered_map`和`unordered_multimap`實例中也適用。同樣在`set/multiset`和`unordered_set/unordered_multiset`也適用。

為了在不同`map`或`set`結構中移動元素，鍵、值和分配器的類型都必須相同。需要注意的是，不能將`map`中的節點移動到`unordered_map`中，或是將`set`中的元素移動到`unordered_set`中。

