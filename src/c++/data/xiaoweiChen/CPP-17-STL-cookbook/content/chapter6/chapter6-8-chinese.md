# 刪除詞組間連續的空格

我們會經常從輸入中讀取字符串，這些字符串會包含一些原生格式，需要進行清洗。其中一個例子就是字符串中包含了太多的空格。

本節，我們將實現一個聰明的空格濾波算法，其會刪除多於的空格，會給單詞間留下一個空格。我們可以將這個算法稱為`remove_multi_whitespace`，並且接口與STL很像。

## How to do it...

本節，我們將實現過濾空格的算法，並瞭解其是如何進行工作的：

1. 包含必要的頭文件和聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <string>
   #include <algorithm>
   
   using namespace std;
   ```

2. `remove_multi_whitespace`看起來與STL的風格非常類似。這個算法會移除多餘的空格，只保留一個空格。當字符串為`a b`，算法是不會進行任何操作的；當字符串為`a   b`時，算法會返回`a b`。為了完成這個算法，我們使用`std::unqiue`通過對一段區域的迭代，用來查找一對連續的元素。然後，通過謂詞函數進行判斷，確定兩個元素是否相等。如果相等，那麼`std::unique`會將其中一個移除。這樣，子範圍中就不會存在相等的元素了。謂詞函數會通過讀取到的內容來判斷二者是否相等。我們需要給`std::unique`怎麼樣一個謂詞函數呢？其需要判斷兩個元素是否是連續的空格；如果是，就要移除一個空格。與`std::unique`類似，也需要傳入一對`begin/end`迭代器，然後返回的迭代器將返回新範圍的末尾迭代器：

   ```c++
   template <typename It>
   It remove_multi_whitespace(It it, It end_it)
   {
       return unique(it, end_it, [](const auto &a, const auto &b) {
       	return isspace(a) && isspace(b);
       });
   }
   ```

3. 萬事俱備，就來進行測試，嘗試使用算法將不必要的空格進行刪除：

   ```c++
   int main()
   {
       string s {"fooo bar \t baz"};
       
       cout << s << '\n';
   ```

4. 對字符串使用過濾算法，去掉多餘的空格：

   ```c++
       s.erase(remove_multi_whitespace(begin(s), end(s)), end(s));
       
   	cout << s << '\n';
   }
   ```

5. 編譯並運行程序，就會得到如下的輸出：

   ```c++
   $ ./remove_consecutive_whitespace
   fooo bar       baz
   fooo bar baz
   ```

## How it works...

整個問題的解決中，我們沒有使用循環或者元素間的互相比較。我們只使用謂詞函數來完成判斷兩個給定字符是否是空格的任務。然後，將謂詞函數與`std::unique`相結合，所有多餘的空格就都消失了。本章中有些算法可能會有些爭議，不過這個算法的確算的上短小精悍的典範了。

我們如何在將算法進行組合的呢？我們來看一下`std::unique`可能的實現代碼：

```c++
template<typename It, typename P>
It unique(It it, It end, P p)
{
	if (it == end) { return end; }

    It result {it};
	while (++it != end) {
		if (!p(*result, *it) && ++result != it) {
			*result = std::move(*it);
		}
	}
	return ++result;
}
```

其中循環會迭代到範圍的最後，當元素滿足謂詞條件，就會從原始位置上移除一個元素。這個版本的`std::unique`不接受多餘的謂詞函數，來判斷兩個相鄰的元素是否相等。這樣的話，只能將重複的字符去除，比如會將`abbbbbbbbc`變換成`abc`。

那麼，我們應該怎麼做才能不去除除了空格之外的重複的元素呢？這樣，謂詞函數不能告訴程序“兩個輸入字符是相同的”，而是要說“兩個輸入字符都是空格”。

最後需要注意的是，無論是`std::unique`還是`remove_multi_whitespace`都會從字符串中移除字母元素。根據字符串的語義來移動字符串，並表明新的結尾在哪裡。新的尾部到舊的尾部的元素依舊存在，所以我們必須將它們刪除：

```c++
s.erase(remove_multi_whitespace(begin(s), end(s)), end(s));
```

和`vector`和`list`一樣，`erase`成員函數其會對元素進行擦除和刪除。

