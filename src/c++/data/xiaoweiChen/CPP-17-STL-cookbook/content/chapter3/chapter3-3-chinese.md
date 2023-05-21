# 使用迭代適配器填充通用數據結構

大多數情況下，我們想要用數據來填充任何容器，不過數據源和容器卻沒有通用的接口。這種情況下，我們就需要人工的去編寫算法，將相應的數據推入容器中。不過，這會分散我們解決問題的注意力。

不同數據結構間的數據傳遞現在可以只通過一行代碼就完成，這要感謝STL中的**迭代適配器**。本節會展示如何使用迭代適配器。

## How to do it...

本節中，我們使用一些迭代器包裝器，展示如何使用包裝器，並瞭解其如何在編程任務中給予我們幫助。

1. 包含必要的頭文件。

   ```c++
   #include <iostream>
   #include <string>
   #include <iterator>
   #include <sstream>
   #include <deque>
   ```

2. 聲明使用的命名空間。

   ```c++
   using namespace std;
   ```

3. 開始使用`std::istream_iterator`。這裡我們特化為`int`類型。這樣，迭代器就能將標準輸入解析成整數。例如，當我們遍歷這個迭代器，其就和`std::vector<int>`一樣了。`end`迭代器的類型沒有變化，但不需要構造參數:

   ```c++ 
   int main()
   {
       istream_iterator<int> it_cin {cin};
       istream_iterator<int> end_cin;
   ```

4. 接下來，我們實例化一個`std::deque<int>`，並且將標準輸入中的所有數字拷貝到隊列中。隊列本身不是一個迭代器，所以我們使用`std::back_inserter`輔助函數將隊列包裝入`std::back_insert_iterator`中。這樣指定的迭代器就能執行`v.pack_back(item)`，將標準輸入中的每個元素放入容器中。這樣就能讓隊列自動增長。

   ```c++
       deque<int> v;
       copy(it_cin, end_cin, back_inserter(v));	
   ```

5. 接下來，我們使用`std::istringstream`將元素拷貝到隊列中部。先使用字符串，來定義一個字符流的實例：

   ```c++
   	istringstream sstr {"123 456 789"};
   ```

6. 我們需要選擇列表的插入點。這個點必須在中間，我們使用隊列的起始指針，然後使用`std::next`函數將其指向中間位置。函數第二個參數的意思就是讓指針前進多少，這裡選擇`v.size() / 2`步，也就是隊列的正中間位置(這裡我們將`v.size()`強轉為`int`類型，因為`std::next`第二個參數類型為`difference_type`，是和第一個迭代器參數間的距離。因此，該類型是個有符號類型。根據編譯選項，如果我們不進行顯式強制轉化，編譯器可能會報出警告)。

   ```c++
       auto deque_middle (next(begin(v),
       	 static_cast<int>(v.size()) / 2));
   ```

7. 現在，我們可以從輸入流中一步步的拷貝整數到隊列當中。另外，流的`end`包裝迭代器為空的` std::istream_iterator<int> `。這個隊列已經被包裝到一個插入包裝器中，也就是成為`std::insert_iterator`的一個實例，其指向隊列中間位置的迭代器，我們用`deque_middle`表示:

   ```c++
   	copy(istream_iterator<int>{sstr}, {}, inserter(v, deque_middle));
   ```

8. 現在，讓我們使用`std::front_insert_iterator`插入一些元素到隊列中部：

   ```c++
       initializer_list<int> il2 {-1, -2, -3};
       copy(begin(il2), end(il2), front_inserter(v));
   ```

9. 最後一步將隊列中的全部內容打印出來。`std::ostream_iterator`作為輸出迭代器，在我們的例子中其就是從`std::cout`拷貝打印出的信息，並將各個元素使用逗號隔開：

   ```c++
       copy(begin(v), end(v), ostream_iterator<int>{cout, ", "});
       cout << '\n';
   }
   ```

10. 編譯並運行，即有如下的輸出。你能找到那些數字是由哪行的代碼插入的嗎？

    ```c++
    $ echo "1 2 3 4 5" | ./main
    -3, -2, -1, 1, 2, 123, 456, 789, 3, 4, 5,
    ```

## How it works...

本節我們使用了很多不同類型的迭代適配器。他們有一點是共同的，會將一個對象包裝成迭代器。

**std::back_insert_iterator**

`back_insert_iterator`可以包裝`std::vector`、`std::deque`、`std::list`等容器。其會調用容器的`push_back`方法在容器最後插入相應的元素。如果容器實例不夠長，那麼容器的容量會自動增長。

**std::front_insert_iterator**

`front_insert_iterator`和`back_insert_iterator`一樣，不過`front_insert_iterator`調用的是容器的`push_front`函數，也就是在所有元素前插入元素。這裡需要注意的是，當對類似於`std::vector`的容器進行插入時，其已經存在的所有元素都要後移，從而空出位置來放插入元素，這會對性能造成一定程度的影響。

**std::insert_iterator**

這個適配器與其他插入適配器類似，不過能在容器的中間位置插入新元素。使用`std::inserter`包裝輔助函數需要兩個參數。第一個參數是容器的實例，第二個參數是迭代器指向的位置，就是新元素插入的位置。

**std::istream_iterator**

`istream_iterator`是另一種十分方便的適配器。其能對任何`std::istream`使用(文件流或標準輸入流)，並且可以根據實例的具體特化類型，對流進行分析。本節中，我們使用了`std::istram_iterator<int>(std::cin)`，其會將整數從標準輸入中拉出來。

通常，對於流來說，其長度我們是不知道的。這就存在一個問題，也就是`end`迭代器指向的位置在哪裡？對於流迭代器來說，它就知道相應的`end`迭代器的位置。這樣就使得迭代器的比較更加高效，不需要通過遍歷來完成。這樣就是為什麼`end`流迭代器不需要傳入任何參數的原因。

**std::ostream_iterator**

`ostream_iterator`和`istream_iterator`類似，不過是用來進行輸出的流迭代器。與`istream_iterator`不同在於，構造時需要傳入兩個參數，且第二個參數必須要是一個字符串，這個字符串將會在各個元素之後，推入輸出流中。這樣我們就能很容易的在元素中間插入逗號或者換行的符號，以便用戶進行觀察。