# 使用STL算法實現單詞查找樹類

所謂的trie數據類型，能夠對感興趣的數據進行存儲，並且易於查找。將文本語句分割成多個單詞，放置在列表中，我們能發現其開頭一些單詞的共性。

讓我們看下下圖，這裡有兩個句子“hi how are you”和“hi how do you do”，存儲在一個類似於樹的結構體中。其都以“hi how”開頭，句子後面不同的部分，劃分為樹結構：

![](../../images/chapter6/6-1-1.png)

因為trie數據結構結合了相同的前綴，其也稱為前綴樹，很容易使用STL的數據結構實現。本章我們將關注如何實現我們自己的trie類。

## How to do it...

本節，我們將使用STL數據結構和算法實現前綴樹結構。

1. 包含必要的頭文件和聲明所使用的命名空間

   ```c++
   #include <iostream>
   #include <optional>
   #include <algorithm>
   #include <functional>
   #include <iterator>
   #include <map>
   #include <vector>
   #include <string>

   using namespace std;
   ```

2. 我們首先實現一個類。我們的實現中，trie為`map`的遞歸映射。每個trie節點夠包含一個`map`，節點的有效值`T`映射了下一個節點：

   ```c++
   template <typename T>
   class trie
   {
   	map<T, trie> tries;
   ```

3. 將新節點插入隊列的代碼很簡單。使用者需要提供一個`begin/end`迭代器對，並且會通過循環進行遞歸。當用戶輸入的序列為{1, 2, 3}時，我們可以將1作為一個子trie，2為下一個子trie，以此類推。如果這些子trie在之前不存在，其將會通過`std::map`的`[]`操作符進行添加：

   ```c++
   public:
       template <typename It>
       void insert(It it, It end_it) {
           if (it == end_it) { return; }
           tries[*it].insert(next(it), end_it);
       }
   ```

4. 我們這裡也會定義一個輔助函數，用戶只需要提供一個容器，之後輔助函數就會通過迭代器自動進行查詢：

   ```c++
   	template <typename C>
       void insert(const C &container) {
       	insert(begin(container), end(container));
       } 
   ```

5. 調用我們的類時，可以寫成這樣`my_trie.insert({"a", "b","c"}); `，必須幫助編譯器正確的判斷出這段代碼中的所有類型，因此我們又添加了一個函數，這個函數用於重載的插入接口：

   ```c++
   	void insert(const initializer_list<T> &il) {
   		insert(begin(il), end(il));
   	}
   ```

6. 我們也想了解，trie中有什麼，所以我們需要一個打印函數。為了打印，我們可以對tire進行深度遍歷。這樣根節點下面的是第一個葉子節點，我們會記錄我們所看到的元素的負載。當我們達到葉子節點，那麼就可以進行打印了。我們會看到，當到達葉子的時候`tries.empty()`為true。遞歸調用print後，我們將再次彈出最後添加的負載元素：

   ```c++
       void print(vector<T> &v) const {
           if (tries.empty()) {
               copy(begin(v), end(v),
               	ostream_iterator<T>{cout, " "});
               cout << '\n';
           }
           for (const auto &p : tries) {
               v.push_back(p.first);
               p.second.print(v);
               v.pop_back();
           }
       }
   ```

7. 打印函數需要傳入一個可打印負載元素的列表，不過用戶不需要傳入任何參數就能調用它。這樣，我們就定義了一個無參數的打印函數，其構造了輔助列表對象：

   ```c++
   	void print() const {
           vector<T> v;
           print(v);
       } 
   ```

8. 現在，我們就可以創建和打印trie了，我們將先搜索子trie。當trie包含的序列為`{a, b, c}`和`{a, b, d, e}`，並且我們給定的序列為`{a, b}`，對於查詢來說，返回的子序列為包含`{c}`和`{d, e}`的部分。當我們找到子trie，將返回一個`const`的引用。在搜索中，也會出現沒有要搜索序列的情況。即便如此，我們還是要返回些什麼。`std::optional`是一個非常好的幫手，因為當沒有找到匹配的序列，我們可以返回一個空的`optional`對象：

   ```c++
       template <typename It>
       optional<reference_wrapper<const trie>>
       subtrie(It it, It end_it) const {
           if (it == end_it) { return ref(*this); }
           auto found (tries.find(*it));
           if (found == end(tries)) { return {}; }
           
           return found->second.subtrie(next(it), end_it);
       }
   ```

9. 與`insert`方法類似，我們將提供一個只需要一個參數的`subtrie`方法，其能自動的從輸入容器中獲取迭代器：

   ```c++
       template <typename C>
       auto subtrie(const C &c) {
       	return subtrie(begin(c), end(c));
       }
   };
   ```

10. 這樣就實現完了。我們在主函數中使用我們trie類，使用`std::string`類型對類進行特化，並實例化對象：

    ```c++
    int main()
    {
        trie<string> t;
        t.insert({"hi", "how", "are", "you"});
        t.insert({"hi", "i", "am", "great", "thanks"});
        t.insert({"what", "are", "you", "doing"});
        t.insert({"i", "am", "watching", "a", "movie"});
    ```

11. 打印整個trie：

    ```c++
    	cout << "recorded sentences:\n";
    	t.print();
    ```

12. 而後，我們將獲取輸入語句的子trie，其以“hi”開頭：

    ```c++
        cout << "\npossible suggestions after \"hi\":\n";

        if (auto st (t.subtrie(initializer_list<string>{"hi"}));
            st) {
            st->get().print();
        }
    }
    ```

13. 編譯並運行程序，其會返回兩個句子的以“hi”開頭的子trie：

    ```c++
    $ ./trie
    recorded sentences:
    hi how are you
    hi i am great thanks
    i am watching a movie
    what are you doing

    possible suggestions after "hi":
    how are you
    i am great thanks
    ```

## How it works...

有趣的是，單詞序列的插入代碼要比在子trie查找給定字母序列的代碼簡單許多。所以，我們首先來看一下插入代碼：

```c++
template <typename It>
void trie::insert(It it, It end_it) {
    if (it == end_it) { return; }
    tries[*it].insert(next(it), end_it);
}
```

迭代器對`it`和`end_it`，表示要插入的字符序列。`tries[*it]`代表在子trie中要搜索的第一個字母，然後調用`.insert(next(it), end_it);`對更低級的子trie序列使用插入函數，使用迭代器一個詞一個詞的推進。` if (it == end_it) { return; }`行會終止遞歸。返回語句不會做任何事情，這到有點奇怪了。所有插入操作都在`tries[*it]`語句上進行，`std::map`的中括號操作將返回鍵所對應的值或是創建該鍵，相關的值(本節中映射類型是一個trie)由默認構造函數構造。這樣，當我們查找不理解的單詞時，就能隱式的創建一個新的trie分支。

查找子trie看起來十分複雜，因為我們沒有必要隱藏那麼多的代碼：

```c++
template <typename It>
optional<reference_wrapper<const trie>>
subtrie(It it, It end_it) const {
    if (it == end_it) { return ref(*this); }
    auto found (tries.find(*it));
    if (found == end(tries)) { return {}; }

    return found->second.subtrie(next(it), end_it);
}
```

這段代碼的主要部分在於`auto found (tries.find(*it));`。我們使用find來替代中括號操作符。當我們使用中括號操作符進行查找時，trie將會為我們創建丟失的元素(順帶一提，當我們嘗試這樣做，類的函數為`const`，所以這樣做事不可能的。這樣的修飾能幫助我們減少bug的發生)。

另一個細節是返回值`optional<reference_wrapper<const trie>>`。我們選擇`std::optional`作為包裝器，因為其可能沒有我們所要找打tire。當我們僅插入“hello my friend”，那麼就不會找到“goodbye my friend”。這樣，我們僅返回`{}`就可以了，其代表返回一個空`optional`對象給調用者。不過這還是沒有解釋，我們為什麼使用`reference_wrapper`代替`optional<const trie &>`。`optional`的實例，其為`trie&`類型，是不可賦值的，因此不會被編譯。使用`reference_warpper`實現一個引用，就是用來對對象進行賦值的。