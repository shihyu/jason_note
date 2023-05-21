# 向std::map實例中高效並有條件的插入元素

我們需要用鍵值對填充一個`map`實例時，會碰到兩種不同的情況：

1. 鍵不存在。創建一個全新的鍵值對。
2. 鍵已存在。修改鍵所對應的值。

我通常會使用`insert`或`emplace`函數對`map`插入新元素，如果插入不成功，那麼就是第二種情況，就需要去修改現有的元素。`insert`和`emplace`都會創建一個新元素嘗試插入到`map`實例中，不過在第二種情況下，這個新生成的元素會被扔掉。兩種情況下，我們都會多餘調用一次構造函數。

C++17中，添加了`try_emplace`函數，其只有在滿足條件的情況下，才能插入新元素。讓我們實現一個程序，建立一張表，列出各國億萬富翁的數量。我們例子中不會使用很大開銷進行元素創建，不過我們的例子來源於生活，其能讓你明白如何使用`try_emplace`。

## How to do it...

本節中，我們將實現一個應用，其能創建一張百萬富翁的列表。這個列表中按國家區分，裡面記錄了各國富人的數量。

1. 包含頭文件和聲明命名空間。

   ```c++
   #include <iostream>
   #include <functional>
   #include <list>
   #include <map>

   using namespace std;
   ```

2. 定義一個結構器，代表對應的富翁。

   ```c++
   struct billionaire {
       string name;
       double dollars;
       string country;
   };
   ```

3. 主函數中，我們定義了一個百萬富翁的列表。世界上有很多百萬富翁，所以我們創建一個有限列表來存儲這些富翁的信息。這個列表是已排序的。2017年福布斯富豪名單，世界百萬富翁排行榜可以在  https://www.forbes.com/billionaires/list 查到。

   ```c++
   int main()
   {
       list<billionaire> billionaires {
           {"Bill Gates", 86.0, "USA"},
           {"Warren Buffet", 75.6, "USA"},
           {"Jeff Bezos", 72.8, "USA"},
           {"Amancio Ortega", 71.3, "Spain"},
           {"Mark Zuckerberg", 56.0, "USA"},
           {"Carlos Slim", 54.5, "Mexico"},
           // ...
           {"Bernard Arnault", 41.5, "France"},
           // ...
           {"Liliane Bettencourt", 39.5, "France"},
           // ...
           {"Wang Jianlin", 31.3, "China"},
           {"Li Ka-shing", 31.2, "Hong Kong"}
           // ...
       };
   ```

4. 現在讓我們定義一個表。這個表由表示國家名的字符串和一個組對構成。組對中會具有上面列表的一個(const)副本。這也就是每個國家最富有的人。組對中另一個變量是一個計數器，其會統計某國的富豪人數。

   ```c++
   	map<string, pair<const billionaire, size_t>> m;	
   ```

5. 現在，讓我們將列表中的數據嘗試插入到組對中。每個組對中都包含了對應國家的百萬富翁，並將計數器的值置成1。

   ```c++
   	for (const auto &b : billionaires) {
   		auto [iterator, success] = m.try_emplace(b.country, b, 1);
   ```

6. 如果這一步成功，那就不用再做其他事了。我們使用b和1創建的組對已經插入到表中。如果因為鍵已存在而插入失敗，那麼組對就不會構建。當我們百萬富翁結構體非常大時，我們需要將運行時拷貝的時間節省下來。不過，在不成功的情況下，我們還是要對計數器進行增加1的操作。

   ```c++
       if (!success) {
           iterator->second.second += 1;
           }
       }
   ```

7. 現在，我們來打印一下每個國家百萬富翁的數量，以及各個國家中最富有的人。

   ```c++
       for (const auto & [key, value] : m) {
           const auto &[b, count] = value;
           cout << b.country << " : " << count
          	     << " billionaires. Richest is "
                << b.name << " with " << b.dollars
                << " B$\n";
       }
   }
   ```

8. 編譯並運行程序，就會得到下面的輸出(這裡的輸出是不完整的，因為列表比較長)。

   ```
   $ ./efficient_insert_or_modify
   China : 1 billionaires. Richest is Wang Jianlin with 31.3 B$
   France : 2 billionaires. Richest is Bernard Arnault with 41.5 B$
   Hong Kong : 1 billionaires. Richest is Li Ka-shing with 31.2 B$
   Mexico : 1 billionaires. Richest is Carlos Slim with 54.5 B$
   Spain : 1 billionaires. Richest is Amancio Ortega with 71.3 B$
   USA : 4 billionaires. Richest is Bill Gates with 86 B$
   ```

## How it works...

本節圍繞著`std::map`中的`try_emplace`函數展開，這個函數是C++17添加的。下面是其函數聲明之一：

```c++
std::pair<iterator, bool> try_emplace(const key_type& k, Args&&... args);
```

其函數第一個參數`k`是插入的鍵，`args`表示這個鍵對應的值。如果我們成功的插入了元素，那麼函數就會返回一個迭代器，其指向新節點在表中的位置，組對中布爾變量的值被置為true。當插入不成功，組對中的布爾變量值會置為false，並且迭代器指向與新元素衝突的位置。

這個特性在我們的例子中非常有用——可以完美處理第一次訪問到，和之後訪問到的情況。

> Note：
>
> `std::map`中`insert`和`emplace`方法完全相同。`try_emplace`與它們不同的地方在於，在遇到已經存在的鍵時，不會去構造組對。當相應對象的類型需要很大開銷進行構造時，這對於程序性能是幫助的。

## There's more...

如果我們將表的類型從`std::map`換成`std::unordered_map`，程序照樣能工作。這樣的話，當不同類型的表具有較好的性能特性時，我們就可以快速的進行切換。例子中，唯一可觀察到的區別是，億萬富翁表不再按字母順序打印，因為哈希表和搜索樹不同，其不會對對象進行排序。