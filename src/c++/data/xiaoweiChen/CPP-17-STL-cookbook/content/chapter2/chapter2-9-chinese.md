# 過濾用戶的重複輸入，並以字母序將重複信息打印出——std::set

`std::set`是一個奇怪的容器：工作原理和`std::map`很像，不過`std::set`將鍵作為值，沒有鍵值對。所以沒做辦法與其他類型的數據進行映射。表面上看，`std::set`因為沒有太多的例子，導致很多開發者幾乎不知道有這樣的容器。想要使用類似`std::set`的功能時，只有自己去實現一遍。

本節展示如何使用`std::set`收集很多不同的元素，過濾這些元素，最後只輸出一個元素。

## How to do it...

從標準輸入流中讀取單詞，所有不重複的單詞將放到一個`std::set`實例中。之後，枚舉出所有輸入流中不重複的單詞。

1. 包含必要的頭文件。

   ```c++
   #include <iostream>
   #include <set>
   #include <string>
   #include <iterator>
   ```

2. 為了分析我們的輸入，會使用到`std`命名空間：

   ```c++
   using namespace std;
   ```

3. 現在來實現主函數，先來實例化一個`std::set`。

   ```c++
   int main()
   {
   	set<string> s;
   ```

4. 下一件事情就是獲取用戶的輸入。我們只從標準輸入中讀取，這樣我們就要用到`istream_iterator`。

   ```c++
       istream_iterator<string> it {cin};
       istream_iterator<string> end;
   ```

5. 這樣就得到了一對`begin`和`end`迭代器，可以用來表示用戶的輸入，我們可以使用`std::inserter`來填滿`set`實例。

   ```c++
   	copy(it, end, inserter(s, s.end()));
   ```

6. 這樣就完成了填充。為了看到從標準輸入獲得的不重複單詞，我們可以打印當前的`set`實例。

   ```c++
   	for (const auto word : s) {
       	cout << word << ", ";
       }
       cout << '\n';
   }
   ```

7. 最後，讓我們編譯並運行這個程序。從之前的輸入中，重複的單詞都會去除，獲得不重複的單詞，然後以字母序排序輸出。

   ```
   $ echo "a a a b c foo bar foobar foo bar bar" | ./program
   a, b, bar, c, foo, foobar,
   ```

## How it works...

程序中有兩個有趣的部分。第一個是使用了`std::istream_iterator`來訪問用戶輸入，另一個是將`std::set`實例使用`std::inserter`用包裝後，在使用`std::copy`填充。這看起來像是變魔術一樣，只需要一行代碼，我們就能完成使用輸入流填充實例，去除重複的單詞和以字母序進行排序。

**std::istream_iterator**

這個例子的有趣之處在於一次性可以處理流中大量相同類型的數據：我們對整個輸入進行逐字的分析，並以`std::string`實例的方式插入`set`。

`std::istream_iterator`只傳入了一個模板參數。也就我們輸入數據的類型。我們選擇`std::string`是因為我們假設是文本輸入，不過這裡也可以是`float`型的輸入。基本上任何類型都可以使用`cin >> var;`完成。構造函數接受一個`istream`實例。標準輸入使用全局輸入流`std::cin`表示，例子中其為`istream`的參數。

```c++
istream_iterator<string> it {cin};
```

輸入流迭代器`it`就已經實例化完畢了，其可以做兩件事情：當對其解引用(`*it`)時，會得到當前輸入的符號。我們通過輸入迭代器構造`std::string`實例，每個字符串容器中都包含一個單詞；當進行自加`++it`時，其會跳轉到下一個單詞，然後再解引用訪問下一個單詞。

不過，每次自加後的解引用時都須謹慎。當標準輸入為空，迭代器就不能再解引用。另外，我們需要終止使用解引用獲取單詞的循環。終止的條件就是通過和`end`迭代器進行比較，知道何時迭代器無法解引用。如果`it==end`成立，那麼說明輸入流已經讀取完畢。

我們在創建`it`的同時，也創建了一個`std::istream_iterator`的`end`迭代器。其目的是於`it`進行比較，在每次迭代中作為中止條件。

當`std::cin`結束時，`it`迭代器將會與`end`進行比較，並返回true。

**std::inserter**

調用`std::copy`時，我們使用`it`和`end`作為輸入迭代器。第三個參數必須是一個輸出迭代器。因此，不能使用`s.begin()`或`s.end()`。一個空的`set`中，這二者是一致的，所以不能對`set`的迭代器進行解引用(無論是讀取或賦值)。

這就使`std::inserter`有了用武之地。其為一個函數，返回一個`std::insert_iterator`，返回值的行為類似一個迭代器，不過會完成普通迭代器無法完成的事。當對其使用加法時，其不會做任何事。當我們對其解引用，並賦值給它時，它會連接相關容器，並且將賦值作為一個新元素插入容器中。

當通過`std::inserter`實例化`std::insert_iterator`時，我們需要兩個參數：

```c++
auto insert_it = inserter(s, s.end());
```

其中s是我們的`set`，`s.end()`是指向新元素插入點的迭代器。對於一個空`set`來說，從哪裡開始和從哪裡結束一樣重要。當使用其他數據結構時，比如`vector`和`list`，第二個參數對於定義插入新項的位置來說至關重要。

**將二者結合**

最後，所有的工作都在`std::copy`的調用中完成：

```c++
copy(input_iterator_begin, input_iterator_end, insert_iterator);
```

這個調用從`std::cin`中獲取輸入迭代器，並將其推入`std::set`中。之後，其會讓迭代器自增，並且確定輸入迭代器是否達到末尾。如果不是，那麼可以繼續從標準輸入中獲取單詞。

重複的單詞會自動去除。當`set`已經擁有了一個單詞，再重複將這個單詞添加入`set`時，不會產生任何效果。與`std::multiset`的表現不同，`std::multiset`會接受重複項。