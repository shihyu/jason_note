# 通過邏輯連接創建複雜謂詞

當使用通用代碼過濾數據時，我們通常會定義一些謂詞，這些謂詞就是告訴計算機，哪些數據是我們想要樣，哪些數據時我們不想要的。通常謂詞都是組合起來使用。

例如，當我們在過濾字符串時，我們需要實現一個謂詞，當其發現輸入的字符串以`foo`開頭就返回true，其他情況都返回false。另一個謂詞，當其發現輸入的字符串以“bar”結尾時，返回true，否則返回false。

我們也不總是自己去定義謂詞，有時候可以複用已經存在的謂詞，並將它們結合起來使用。比如，如果我們既想要檢查輸入字符串的開頭是否是`foo`，又想檢查結尾是否為“bar”時，就可以將之前提到的兩個謂詞組合起來使用。本節我們使用Lambda表達式，用一種更加舒服的方式來完成這件事。

## How to do it...

我們將來實現一個非常簡單的字符串過濾謂詞，並且將其和輔助函數結合讓其變得更加通用。

1. 包含必要的頭文件

   ```c++
   #include <iostream>
   #include <functional>
   #include <string>
   #include <iterator>
   #include <algorithm> 
   ```

2. 這裡實現兩個簡單的謂詞函數，後面會用到它們。第一個謂詞會告訴我們字符串的首字母是否是`a`，第二個謂詞則會告訴我們字符串的結尾字母是否為`b`：

   ```c++
   static bool begins_with_a (const std::string &s)
   {
   	return s.find("a") == 0;
   }
   static bool ends_with_b (const std::string &s)
   {
   	return s.rfind("b") == s.length() - 1;
   }
   ```

3. 現在，讓我們來實現輔助函數，我們稱其為`combine`。其需要一個二元函數作為其第一個參數，可以是邏輯'與'或邏輯'或'操作。之後的兩個參數為需要結合在一起的謂詞函數：

   ```c++
   template <typename A, typename B, typename F>
   auto combine(F binary_func, A a, B b)
   {
   ```

4. 之後，我們會返回一個Lambda表達式，這個表達式可以獲取到兩個合併後的謂詞。這個表達式需要一個參數，這個參數會傳入兩個謂詞中，然後表達式將返回這個兩個謂詞結合後的結果：

   ```c++
       return [=](auto param) {
       	return binary_func(a(param), b(param));
       };
   }
   ```

5. 在實現主函數之前，先聲明所使用命名空間：

   ```c++
   using namespace std;
   ```

6. 現在，讓將兩個謂詞函數合併在一起，形成另一個全新的謂詞函數，其會告訴我們輸入的字符串是否以'a'開頭，並且以'b'結尾，比如"ab"或"axxxb"就會返回true。二元函數我們選擇`std::logical_and`。這是個模板類，需要進行實例化，所以這裡我們使用大括號對創建其實例。需要注意的是，因為該類的默認類型為void，所以這裡我們並沒有提供模板參數。特化類的參數類型，都由編譯器推導得到：

   ```c++
   int main()
   {
       auto a_xxx_b (combine(
           logical_and<>{},
           begins_with_a, ends_with_b));
   ```

7. 我們現在可以對標準輸入進行遍歷，然後打印出滿足全新謂詞的詞組：

   ```c++
       copy_if(istream_iterator<string>{cin}, {},
               ostream_iterator<string>{cout, ", "},
               a_xxx_b);
       cout << '\n';
   } 
   ```

8. 編譯邊運行程序，就會得到如下輸出。我們輸入了四個單詞，但是隻有兩個滿足我們的謂詞條件：

   ```c++
   $ echo "ac cb ab axxxb" | ./combine
   ab, axxxb,
   ```

##There's more...

STL已經提供了一些非常有用的函數對象，例如`std::logical_and`，`std::logical_or`等等。所以我們沒有必要所有東西都自己去實現。可以去看一下C++的參考手冊，瞭解一下都有哪些函數對象已經實現：

- 英文：http://en.cppreference.com/w/cpp/utility/functional
- 中文：http://zh.cppreference.com/w/cpp/utility/functional

