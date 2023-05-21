# 實現個人待辦事項列表——std::priority_queue

`std::priority_queue`是另一種適配容器(類似於`std::stack`)。其實為另一種數據結構的包裝器(默認的數據結構為`std::vector`)，並且提供類似隊列的接口。同樣也遵循隊列的特性，先進先出。這與我們之前使用的`std::stack`完全不同。

這裡僅僅是對`std::queue`的行為進行描述，本節將展示`std::priority_queue`是如何工作的。這個適配器比較特殊，其不僅有FIFO的特性，還混合著優先級。這就意味著，FIFO的原則會在某些條件下被打破，根據優先級的順序形成子FIFO隊列。

## How to do it...

本節中，我們將創建一個待辦事項的結構。為了程序的簡明性就不從用戶輸入解析輸入了。這次專注於`std::priority_queue`的使用。所以我們使用一些待辦事項和優先級填充一個優先級序列，然後以FIFO的順序讀出這些元素(這些元素是通過優先級進行過分組)。

1. 包含必要的頭文件。`std::priority_queue`在`<queue>`中聲明。

   ```c++
   #include <iostream>
   #include <queue>
   #include <tuple>
   #include <string>
   ```

2. 我們怎麼將待辦事項存在優先級隊列中呢？我們不能添加項目時，附加優先級。優先級隊列將使用自然序對待隊列中的所有元素。現在我們實現一個自定義的結構體`struct todo_item`，並賦予其優先級係數，和一個字符串描述待辦事件，並且為了讓該結構體具有可排序性，這裡會實現比較操作符`<`。另外，我們將會使用`std::pair`，其能幫助我們聚合兩個類型為一個類型，並且能完成自動比較。

   ```c++
   int main()
   {
   	using item_type = std::pair<int, std::string>;
   ```

3. 那麼現在我們有了一個新類型`item_type`，其由一個優先級數字和一個描述字符串構成。所以，我們可以使用這種類型實例化一個優先級隊列。

   ```c++
   	std::priority_queue<item_type> q;
   ```

4. 我們現在來填充優先級隊列。其目的就是為了提供一個非結構化列表，之後優先級隊列將告訴我們以何種順序做什麼事。比如，你有漫畫要看的同時，也有作業需要去做，那麼你必須先去寫作業。不過，`std::priority_queue`沒有構造函數，其支持初始化列表，通過列表我們能夠填充優先級隊列(使用`vector`或`list`都可以對優先級隊列進行初始化)。所以我們這裡定義了一個列表，用於下一步的初始化。

   ```c++
       std::initializer_list<item_type> il {
           {1, "dishes"},
           {0, "watch tv"},
           {2, "do homework"},
           {0, "read comics"},
       };
   ```

5. 現在我們可以很方便的遍歷列表中的所有元素，然後通過`push`成員函數將元素插入優先級列表中。

   ```c++
       for (const auto &p : il) {
       	q.push(p);
       }
   ```

6. 這樣所有的元素就都隱式的進行了排序，並且我們可以瀏覽列表中優先級最高的事件。

   ```c++
       while(!q.empty()) {
           std::cout << q.top().first << ": " << q.top().second << '\n';
           q.pop();
       }
       std::cout << '\n';
   }
   ```

7. 編譯運行程序。結果如我們所料，作業是最優先的，看電視和看漫畫排在最後。

   ```c++
   $ ./main
   2: do homework
   1: dishes
   0: watch tv
   0: read comics
   ```

## How it works...

`std::priority_queue`使用起來很簡單。我們只是用了其三個成員函數。

1. `q.push(item)`將元素推入隊列中。
2. `q.top()`返回隊首元素的引用。
3. `q.pop()`移除隊首元素。

不過，如何做到排序的呢？我們將優先級數字和描述字符串放入一個`std::pair`中，然後就自然得到排序後的結果。這裡有一個` std::pair<int, std::string>`的實例`p`，我們可通過`p.first`訪問優先級整型數，使用`p.second`訪問字符串。我們在循環中就是這樣打印所有待辦事件的。

如何讓優先級隊列意識到` {2, "do homework"}`要比`{0, "watch tv"}`重要呢？

比較操作符`<`在這裡處理了不同的元素。我們假設現在有`left < right`，兩個變量的類型都是pair。

1. ` left.first != right.first`，然後返回`left.first < right.first`。
2. ` left.first == right.first`，然後返回`left.second < right.second`。

以這種方式就能滿足我們的要求。最重要的就是`pair`中第一個成員，然後是第二個成員。否則，`std::priority_queue`將會字母序將元素進行排序，而非使用數字優先級的順序(這樣的話，看電視將會成為首先要做的事情，而完成作業則是最後一件事。對於懶人來說，無疑是個完美的順序)。

