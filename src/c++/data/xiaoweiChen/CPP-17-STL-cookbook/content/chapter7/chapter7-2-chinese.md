# 消除字符串開始和結束處的空格

應用從用戶端獲取到的輸入，經常會有很多不必要的空格存在。之前的章節中，將單詞間多餘的空格進行移除。

現在讓我們來看看，被空格包圍的字符串應該怎麼去移除多餘的空格。`std::string`具有很多不錯的輔助函數能完成這項工作。

> Note：
>
> 這節看完後，下節也別錯過。將會在下節看到我們如何使用`std::string_view`類來避免不必要的拷貝或數據修改。

## How to do it...

本節，我們將完成一個輔助函數的實現，其將判斷是否有多餘的空格在字符串開頭和結尾，並複製返回去掉這些空格的字符串，並進行簡單的測試：

1. 包含必要的頭文件，並聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <string>
   #include <algorithm>
   #include <cctype>
   
   using namespace std;
   ```

2. 函數將對一個常量字符串進行首尾空格的去除，並返回首尾沒有空格的新字符串：

   ```c++
   string trim_whitespace_surrounding(const string &s)
   { 
   ```

3. `std::string`能夠提供兩個函數，這兩個函數對我們很有幫助。第一個就是`string::find_first_not_of`，其能幫助我們找到我們想要跳過的字符。本節中毫無疑問就是空格，其包括空格，製表符和換行符。函數能返回第一個非空格字符的位置。如果字符串裡面只有空格，那麼會返回`string::npos`。這意味著沒有找到除了空格的其他字符。如果這樣，我們就會返回一個空的字符串：

   ```c++
   	const char whitespace[] {" \t\n"};
   	const size_t first (s.find_first_not_of(whitespace));
   	if (string::npos == first) { return {}; }
   ```

4. 現在我們知道新字符串從哪裡開始，但是再哪裡結尾呢？因此，需要使用另一個函數`string::find_last_not_of`，其能找到最後一個非空格字符的位置：

   ```c++
   	const size_t last (s.find_last_not_of(whitespace));
   ```

5. 使用`string::substr`就能返回子字符串，返回的字符串沒有空格。這個函數需要兩個參數——一個是字符串的起始位置，另一個是字符串的長度：

   ```c++
   	return s.substr(first, (last - first + 1));
   }
   ```

6. 這就完成了。現在讓我們來編寫主函數，創建字符串，讓字符串的前後充滿空格，以便我們進行移除：

   ```c++
   int main()
   {
       string s {" \t\n string surrounded by ugly"
       		 " whitespace \t\n "};
   ```

7. 我們將打印去除前和去除後的字符串。將字符串放入大括號中，這樣就很容易辨別哪裡有空格了：

   ```c++
       cout << "{" << s << "}\n";
       cout << "{"
       	 << trim_whitespace_surrounding(s)
       	 << "}\n";
   }
   ```

8. 編譯運行程序，就會得到如下的結果：

   ```c++
   $ ./trim_whitespace
   {
   string surrounded by ugly whitespace
   }
   {string surrounded by ugly whitespace}
   ```

## How it works...

本節，我們使用了`string::find_first_not_of`和`string::find_last_not_of`函數。這兩個函數也能接受C風格的字符串，會將其當做字符鏈表進行搜索。當有一個字符串`foo bar`時，當調用`find_first_not_of("bfo ")`時返回5，因為'a'字符是第一個不屬於`bfo`的字符。參數中字符的順序，在這裡並不重要。

倒裝的函數也是同樣的原理，當然還有兩個沒有使用到的函數：`string::find_first_of`和`string::find_last_of`。

同樣也是基於迭代器的函數，需要檢查函數是否返回了合理的位置，當沒有找到時，函數會返回一個特殊的位置——`string::npos`。

我們可以從輔助函數中找出字符所在的位置，並且使用`string::substr`來構造前後沒有空格的字符串。這個函數接受一個首字符相對位置和字符串長度，然後就會構造一個子字符串進行返回。舉個栗子，`string{"abcdef"}.substr(2, 2)`將返回`cd`。