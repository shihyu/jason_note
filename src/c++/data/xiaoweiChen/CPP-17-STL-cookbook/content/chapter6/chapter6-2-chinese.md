# 使用樹實現搜索輸入建議生成器

上網時，在搜索引擎中輸入要查找的東西時，對應下拉選項中會嘗試猜測你想要查找什麼。這種猜測是基於之前相關主題被查找的數量。有時搜索引擎十分有趣，其會顯示一些奇怪的主題。

![](../../images/chapter6/6-2-1.png)

本章，我們將使用樹類實現一個簡單的搜索建議引擎。

## How to do it...

本節，我們將實現一個終端應用，其能接受輸入，並且能對所要查找的內容進行猜測，當然猜測的依據是我們用文本完成的“數據庫”。

1. 包含必要的頭文件和聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <optional>
   #include <algorithm>
   #include <functional>
   #include <iterator>
   #include <map>
   #include <list>
   #include <string>
   #include <sstream>
   #include <fstream>
   
   using namespace std;
   ```

2. 我們將使用上一節實現的trie類：

   ```c++
   template <typename T>
   class trie
   {
   	map<T, trie> tries;
   public:
   	template <typename It>
   	void insert(It it, It end_it) {
   		if (it == end_it) { return; }
   		tries[*it].insert(next(it), end_it);
   	}
   
       template <typename C>
   	void insert(const C &container) {
   		insert(begin(container), end(container));
   	}
       
   	void insert(const initializer_list<T> &il) {
   		insert(begin(il), end(il));
   	}
       
   	void print(list<T> &l) const {
   		if (tries.empty()) {
   			copy(begin(l), end(l),
   				ostream_iterator<T>{cout, " "});
   			cout << '\n';
   		}
   		for (const auto &p : tries) {
   			l.push_back(p.first);
   			p.second.print(l);
   			l.pop_back();
   		}
   	}
      	 
   	void print() const {
   		list<T> l;
   		print(l);
   	}
       
   	template <typename It>
   	optional<reference_wrapper<const trie>>
   	subtrie(It it, It end_it) const {
   		if (it == end_it) { return ref(*this); }
   		auto found (tries.find(*it));
   		if (found == end(tries)) { return {}; }
   
           return found->second.subtrie(next(it), end_it);
   	}
       
   	template <typename C>
   	auto subtrie(const C &c) const {
   		return subtrie(begin(c), end(c));
   	}
   };
   ```

3. 實現一個簡單的輔助函數，這個函數將用於提示用戶輸入他們想要查找的東西：

   ```c++
   static void prompt()
   {
   	cout << "Next input please:\n > ";
   } 
   ```

4. 主函數中，我們打開一個文本文件，其作為我們的基礎數據庫。我們逐行讀取文本文件的內容，並且將數據放入trie中解析：

   ```c++
   int main()
   {
       trie<string> t;
       fstream infile {"db.txt"};
       for (string line; getline(infile, line);) {
           istringstream iss {line};
           t.insert(istream_iterator<string>{iss}, {});
       }
   ```

5. 現在可以使用構建好的trie類，並且需要實現接收用戶查詢輸入的接口。會提示用戶進行輸入，並且將用戶的輸入整行讀取：

   ```c++
       prompt();
       for (string line; getline(cin, line);) {
       	istringstream iss {line};
   ```

6. 通過文本輸入，可以使用trie對其子trie進行查詢。如果在數據庫中已經有相應的語句，那麼會對輸入進行建議，否則會告訴用戶沒有建議給他們：

   ```c++
       if (auto st (t.subtrie(istream_iterator<string>{iss}, {}));
       	st) {
       	cout << "Suggestions:\n";
       	st->get().print();
       } else {
       	cout << "No suggestions found.\n";
       }
   ```

7. 之後，將打印一段分割符，並且再次等待用戶的輸入：

   ```c++
           cout << "----------------\n";
           prompt();
       }
   }
   ```

8. 運行程序之前，我們需要將db.txt文件進行設置。查找的輸入可以是任何字符，並且其不確保是已經排過序的。進入trie類的所有語句：

   ```c++
   do ghosts exist
   do goldfish sleep
   do guinea pigs bite
   how wrong can you be
   how could trump become president
   how could this happen to me
   how did bruce lee die
   how did you learn c++
   what would aliens look like
   what would macgiver do
   what would bjarne stroustrup do
   ...
   ```

9. 創建完db.txt之後，我們就可以運行程序了。其內容如下所示：

   ```c++
   hi how are you
   hi i am great thanks
   do ghosts exist
   do goldfish sleep
   do guinea pigs bite
   how wrong can you be
   how could trump become president
   how could this happen to me
   how did bruce lee die
   how did you learn c++
   what would aliens look like
   what would macgiver do
   what would bjarne stroustrup do
   what would chuck norris do
   why do cats like boxes
   why does it rain
   why is the sky blue
   why do cats hate water
   why do cats hate dogs
   why is c++ so hard
   ```

10. 編譯並運行程序，然後進行輸入查找：

    ```c++
    $ ./word_suggestion
    Next input please:
    > what would
    Suggestions:
    aliens look like
    bjarne stroustrup do
    chuck norris do
    macgiver do
    ----------------
    Next input please:
    > why do
    Suggestions:
    cats hate dogs
    cats hate water
    cats like boxes
    ----------------
    Next input please:
    >
    ```
## How it works...

trie是如何工作的，已經在上一節中介紹過了，不過本節我們對其進行填充和查找的過程看起來有些奇怪。讓我們來仔細觀察一下代碼片段，其使用文本數據庫文件對空trie類進行填充：

```c++
fstream infile {"db.txt"};
for (string line; getline(infile, line);) {
    istringstream iss {line};
    t.insert(istream_iterator<string>{iss}, {});
}
```

這段代碼會逐行的將文本文件中的內容讀取出來。然後，我們將字符串拷貝到一個`istringstream`對象中。我們可以根據輸入流對象，創建一個`istring_iterator`迭代器，其能幫助我們查找子trie。這樣，我們就不需要將字符串放入`vector`或`list`中了。上述代碼中，有一段不必要的內存分配，可以使用移動方式，將`line`中的內容移動到iss中，避免不必要的內存分配。不過，`std::istringstream`沒有提供構造函數，所以只能將`std::string`中的內容移動到流中。不過，這裡會對輸入字符串進行復制。

當在trie中查詢用戶的輸入時，使用了相同的策略，但不使用輸入文件流。我們使用`std::cin`作為替代，因為`trie::subtrie`對迭代器的操作，和`trie::insert`如出一轍。

## There's more...

這裡有必要對每個trie節點添加統計變量，這樣我們就能知道各種前綴被查詢的頻率。因此，我們就可以將程序的建議進行排序，當前的搜索引擎就是這樣做的。智能手機觸摸屏文本輸入的建議，也可以通過這種方式實現。

這個修改就留給讀者當作業了。 ：）